# ==============================================================================
# IMPORTAÇÕES E CONFIGURAÇÃO DE AMBIENTE
# ==============================================================================
# A linha 'matplotlib.use('TkAgg')' é uma tentativa de forçar o uso de um
# motor de renderização gráfica mais estável e compatível, o que pode resolver
# problemas de visualização em diferentes sistemas operacionais.
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import random
from hexalattice.hexalattice import create_hex_grid

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS DO JOGO
# ==============================================================================
TAMANHO_MAPA = 11
PONTOS_VITORIA = 10

# Dicionário com as propriedades de cada facção
FACTIONS = {
    'Vermelho': {'cor': 'firebrick', 'pos_inicial': [(1,1), (1,2), (2,1), (2,2), (3,1), (2,3)]},
    'Azul': {'cor': 'royalblue', 'pos_inicial': [(1,10), (1,11), (2,10), (2,11), (3,11), (2,9)]},
    'Verde': {'cor': 'forestgreen', 'pos_inicial': [(11,1), (11,2), (10,1), (10,2), (9,1), (10,3)]},
    'Amarelo': {'cor': 'goldenrod', 'pos_inicial': [(11,10), (11,11), (10,10), (10,11), (9,11), (10,9)]}
}

# Lista de unidades que cada facção recebe no início
INITIAL_UNITS = ['Infantaria', 'Infantaria', 'Cavalaria', 'Cavalaria', 'Arqueiro', 'Especial']

# Coordenadas dos Pontos de Controle (PCs) no formato (linha, coluna)
PONTOS_CONTROLE = {
    'PC1': (6,6), 'PC2': (3,3), 'PC3': (3,9), 'PC4': (9,3), 'PC5': (9,9)
}

# ==============================================================================
# CLASSE PARA REPRESENTAR CADA PEÇA (TAMPINHA)
# ==============================================================================
class Peca:
    """Representa uma única peça no tabuleiro."""
    def __init__(self, faccao, tipo, posicao):
        self.faccao = faccao
        self.tipo = tipo
        self.posicao = posicao
        self.cor = FACTIONS[faccao]['cor']
        self.id = f"{faccao[0]}-{tipo[0]}-{random.randint(100, 999)}"

    def get_bonus_ataque(self):
        """Calcula o bônus de ataque com base nas regras."""
        bonus = 0
        if self.tipo == 'Cavalaria': bonus += 1
        if self.faccao == 'Vermelho': bonus += 1
        # TODO: Implementar lógicas de unidades especiais
        return bonus

    def get_bonus_defesa(self, tabuleiro):
        """Calcula o bônus de defesa com base nas regras."""
        bonus = 0
        if self.tipo == 'Infantaria': bonus += 1
        if self.faccao == 'Amarelo':
            for vizinho_pos in tabuleiro.get_vizinhos(self.posicao):
                peca_vizinha = tabuleiro.get_peca_em(vizinho_pos)
                if peca_vizinha and peca_vizinha.faccao == self.faccao:
                    bonus += 1
                    break
        return bonus

    def __repr__(self):
        """Representação textual da peça para debug."""
        return f"Peca({self.id} @ {self.posicao})"

# ==============================================================================
# CLASSE PARA GERENCIAR O TABULEIRO
# ==============================================================================
class Tabuleiro:
    """Gerencia a grade, as posições das peças e a renderização do mapa."""
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.grid = {}  # Dicionário para guardar as peças: {(linha, col): objeto Peca}
        self.hex_centers, _ = create_hex_grid(nx=tamanho, ny=tamanho, do_plot=False)
        self.matriz_hex_coords = self._criar_mapeamento_coords()

    def _criar_mapeamento_coords(self):
        """Mapeia coordenadas (linha, col) para coordenadas de tela (x,y)."""
        matriz = {}
        index = 0
        for i in range(self.tamanho):  # Colunas na biblioteca
            for j in range(self.tamanho):  # Linhas na biblioteca
                matriz[(j + 1, i + 1)] = self.hex_centers[index]
                index += 1
        return matriz

    def get_vizinhos(self, posicao):
        """Retorna as coordenadas válidas vizinhas a uma dada posição."""
        l, c = posicao
        # Lógica para coordenadas vizinhas em grade hexagonal de "offset" (colunas pares/ímpares)
        if c % 2 == 1:  # Colunas ímpares
            candidatos = [(l - 1, c), (l + 1, c), (l, c - 1), (l, c + 1), (l - 1, c - 1), (l - 1, c + 1)]
        else:  # Colunas pares
            candidatos = [(l - 1, c), (l + 1, c), (l, c - 1), (l, c + 1), (l + 1, c - 1), (l + 1, c + 1)]
        
        # Filtra para retornar apenas posições que existem dentro do mapa
        vizinhos_validos = [pos for pos in candidatos if 1 <= pos[0] <= self.tamanho and 1 <= pos[1] <= self.tamanho]
        return vizinhos_validos

    def adicionar_peca(self, peca):
        self.grid[peca.posicao] = peca

    def mover_peca(self, pos_origem, pos_destino):
        peca = self.grid.pop(pos_origem, None)
        if peca:
            peca.posicao = pos_destino
            self.grid[pos_destino] = peca

    def remover_peca(self, posicao):
        return self.grid.pop(posicao, None)

    def get_peca_em(self, posicao):
        return self.grid.get(posicao)

    def desenhar_mapa(self, rodada, jogador_atual, pontuacoes):
        """Usa Matplotlib para desenhar o estado atual completo do tabuleiro."""
        print("\n--- Gerando visualização do mapa ---")
        
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_aspect('equal')
        plt.axis('off')

        # 1. Desenha todos os hexágonos da grade
        for pos, center_coords in self.matriz_hex_coords.items():
            cor_face = 'gainsboro'  # Cor padrão do hexágono
            if pos in PONTOS_CONTROLE.values():
                cor_face = 'gold'
            
            # O 0.95 cria um pequeno espaçamento visual entre os hexágonos
            hex_shape = plt.Polygon([
                (center_coords[0] + 0.5 * 0.95, center_coords[1] - 0.288 * 0.95),
                (center_coords[0], center_coords[1] - 0.577 * 0.95),
                (center_coords[0] - 0.5 * 0.95, center_coords[1] - 0.288 * 0.95),
                (center_coords[0] - 0.5 * 0.95, center_coords[1] + 0.288 * 0.95),
                (center_coords[0], center_coords[1] + 0.577 * 0.95),
                (center_coords[0] + 0.5 * 0.95, center_coords[1] + 0.288 * 0.95),
            ], facecolor=cor_face, edgecolor='black', linewidth=1.0)
            ax.add_patch(hex_shape)

        # 2. Desenha as peças (círculos) sobre os hexágonos
        for peca in self.grid.values():
            center_coords = self.matriz_hex_coords[peca.posicao]
            ax.add_patch(plt.Circle(center_coords, 0.4, color=peca.cor, zorder=3))
            ax.text(center_coords[0], center_coords[1], peca.tipo[0], 
                    ha='center', va='center', color='white', weight='bold', fontsize=10, zorder=4)

        # 3. Adiciona o título com informações da partida
        titulo = f"Rodada: {rodada} - Vez de: {jogador_atual}"
        placar_str = " | ".join([f"{faccao}: {pontos} pts" for faccao, pontos in pontuacoes.items()])
        plt.title(f"{titulo}\nPlacar: {placar_str}", fontsize=14)
        
        plt.show()

# ==============================================================================
# CLASSE PRINCIPAL DO JOGO (MOTOR DA SIMULAÇÃO)
# ==============================================================================
class Jogo:
    """Orquestra as regras, turnos, e o estado geral da partida."""
    def __init__(self, lista_faccoes):
        print("Inicializando um novo jogo...")
        self.tabuleiro = Tabuleiro(TAMANHO_MAPA)
        self.faccoes = lista_faccoes
        self.pontuacoes = {faccao: 0 for faccao in self.faccoes}
        self.rodada = 1
        self.jogador_atual_idx = 0
        self._setup_inicial()

    def _setup_inicial(self):
        """Cria e posiciona as peças iniciais para cada facção."""
        print("Posicionando peças iniciais...")
        for faccao in self.faccoes:
            for i, tipo_unidade in enumerate(INITIAL_UNITS):
                pos = FACTIONS[faccao]['pos_inicial'][i]
                nova_peca = Peca(faccao, tipo_unidade, pos)
                self.tabuleiro.adicionar_peca(nova_peca)
        print("Setup concluído.")

    def resolver_combate(self, atacante, defensor):
        """Executa a lógica de um combate com rolagem de dados."""
        bonus_ataque = atacante.get_bonus_ataque()
        bonus_defesa = defensor.get_bonus_defesa(self.tabuleiro)
        roll_ataque = random.randint(1, 6) + bonus_ataque
        roll_defesa = random.randint(1, 6) + bonus_defesa
        
        print(f"  COMBATE: {atacante.id} ataca {defensor.id}!")
        print(f"    - Ataque: {roll_ataque} (dado+{bonus_ataque}) | Defesa: {roll_defesa} (dado+{bonus_defesa})")

        if roll_ataque > roll_defesa:
            print(f"    - Vencedor: {atacante.id}! Peça {defensor.id} foi removida.")
            self.tabuleiro.remover_peca(defensor.posicao)
        else: # Empate ou vitória do defensor
            print(f"    - EMPATE! Ambas as peças foram removidas.")
            self.tabuleiro.remover_peca(atacante.posicao)
            self.tabuleiro.remover_peca(defensor.posicao)

    def jogar_turno_ia_simples(self, faccao):
        """Simula um turno com uma Inteligência Artificial básica."""
        print(f"\n--- TURNO DA FACÇÃO {faccao.upper()} (Rodada {self.rodada}) ---")
        pecas_do_jogador = [p for p in self.tabuleiro.grid.values() if p.faccao == faccao]
        random.shuffle(pecas_do_jogador)

        for peca in pecas_do_jogador:
            if peca.posicao not in self.tabuleiro.grid:
                continue

            vizinhos = self.tabuleiro.get_vizinhos(peca.posicao)
            alvos_possiveis = [v_peca for v_pos in vizinhos if (v_peca := self.tabuleiro.get_peca_em(v_pos)) and v_peca.faccao != faccao]
            movimentos_possiveis = [v_pos for v_pos in vizinhos if not self.tabuleiro.get_peca_em(v_pos)]
            
            if alvos_possiveis:
                alvo = random.choice(alvos_possiveis)
                self.resolver_combate(peca, alvo)
            elif movimentos_possiveis:
                movimentos_possiveis.sort(key=lambda p: (p[0]-6)**2 + (p[1]-6)**2)
                novo_pos = movimentos_possiveis[0]
                print(f"  AÇÃO: {peca.id} move-se de {peca.posicao} para {novo_pos}.")
                self.tabuleiro.mover_peca(peca.posicao, novo_pos)

    def atualizar_pontuacao(self):
        """No final da rodada, verifica os PCs e atribui pontos."""
        print("\n--- FIM DA RODADA: Atualizando Pontuação ---")
        for pos_pc in PONTOS_CONTROLE.values():
            peca = self.tabuleiro.get_peca_em(pos_pc)
            if peca:
                self.pontuacoes[peca.faccao] += 1
                print(f"Ponto para {peca.faccao} por controlar PC em {pos_pc}.")
        print(f"PLACAR ATUAL: {self.pontuacoes}")

    def verificar_vitoria(self):
        """Verifica se alguma condição de vitória foi atingida."""
        for faccao, pontos in self.pontuacoes.items():
            if pontos >= PONTOS_VITORIA:
                return faccao, "pontos"
        
        faccoes_ativas = set(p.faccao for p in self.tabuleiro.grid.values())
        if len(faccoes_ativas) <= 1:
            return list(faccoes_ativas)[0] if faccoes_ativas else "Ninguém", "eliminação"
        
        return None, None

    def iniciar_simulacao(self, max_rodadas=25):
        """Roda a simulação completa até um vencedor ou o limite de rodadas."""
        vencedor = None
        motivo_vitoria = ""

        self.tabuleiro.desenhar_mapa(rodada=0, jogador_atual="Setup Inicial", pontuacoes=self.pontuacoes)
        
        print("\n\n*** SIMULAÇÃO INICIADA ***")
        while not vencedor and self.rodada <= max_rodadas:
            jogador_atual = self.faccoes[self.jogador_atual_idx]
            self.jogar_turno_ia_simples(jogador_atual)
            
            self.jogador_atual_idx = (self.jogador_atual_idx + 1) % len(self.faccoes)
            
            if self.jogador_atual_idx == 0:
                self.atualizar_pontuacao()
                vencedor, motivo_vitoria = self.verificar_vitoria()
                self.rodada += 1
        
        print("\n\n*** SIMULAÇÃO FINALIZADA ***")
        if vencedor:
            print(f"A facção {vencedor.upper()} venceu por {motivo_vitoria} na rodada {self.rodada - 1}!")
        else:
            print(f"A simulação terminou após {max_rodadas} rodadas sem um vencedor claro.")
        
        self.tabuleiro.desenhar_mapa(rodada=self.rodada - 1, jogador_atual="Fim de Jogo", pontuacoes=self.pontuacoes)

# ==============================================================================
# PONTO DE ENTRADA DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    faccoes_em_jogo = ['Vermelho', 'Azul', 'Verde', 'Amarelo']
    partida = Jogo(faccoes_em_jogo)
    partida.iniciar_simulacao()