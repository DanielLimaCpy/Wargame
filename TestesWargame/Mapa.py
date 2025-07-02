import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
import time


class Hex:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def __repr__(self):
        return f"({self.q}, {self.r})"

    def get_neighbors(self):
        directions = [
            (1, 0), (-1, 0),
            (0, -1), (1, -1),
            (0, 1), (-1, 1),
        ]
        return [Hex(self.q + dq, self.r + dr) for dq, dr in directions]

def gerar_mapa_hex(raio):
    mapa = set()
    for q in range(-raio, raio + 1):
        r_min = max(-raio, -q - raio)
        r_max = min(raio, -q + raio)
        for r in range(r_min, r_max + 1):
            mapa.add(Hex(q, r))
    return mapa

def get_valid_actions(current_hex, hex_map):
    directions = [
        (1, 0), (-1, 0),
        (0, -1), (1, -1),
        (0, 1), (-1, 1),
    ]
    actions = []
    for i, (dq, dr) in enumerate(directions):
        neighbor = Hex(current_hex.q + dq, current_hex.r + dr)
        if neighbor in hex_map:
            actions.append((i, neighbor))
    return actions

def escolher_acao(Q, estado_idx, valid_actions, epsilon):
    if random.uniform(0, 1) < epsilon:
        return random.choice(valid_actions)
    else:
        melhor = max(valid_actions, key=lambda a: Q[estado_idx][a[0]])
        return melhor

def atualizar_q(Q, s_idx, a_idx, r, s_prox_idx, alpha, gamma):
    melhor_prox = np.max(Q[s_prox_idx])
    Q[s_idx][a_idx] += alpha * (r + gamma * melhor_prox - Q[s_idx][a_idx])

def desenhar_hex(ax, center_x, center_y, size, color):
    angles = np.linspace(0, 2*np.pi, 7)
    x = center_x + size * np.cos(angles)
    y = center_y + size * np.sin(angles)
    hex_patch = patches.Polygon(xy=list(zip(x, y)), closed=True, edgecolor='gray', facecolor=color)
    ax.add_patch(hex_patch)

def axial_para_pixel(hex, size):
    x = size * (3**0.5) * (hex.q + hex.r / 2)
    y = size * 1.5 * hex.r
    return x, y

def desenhar_mapa(mapa, agente=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    size = 1.0  # raio visual do hexágono

    for hex in mapa:
        x, y = axial_para_pixel(hex, size)
        cor = 'white'
        if hex == agente:
            cor = 'red'
        desenhar_hex(ax, x, y, size, cor)
    
    ax.set_aspect('equal')
    ax.axis('off')
    plt.pause(0.3)
    plt.clf()

# Criar mapa
raio = 4
hex_map = gerar_mapa_hex(raio)
hex_list = list(hex_map)
hex_index = {hex: i for i, hex in enumerate(hex_list)}
n_states = len(hex_list)
n_actions = 6
Q = np.zeros((n_states, n_actions))

# Parâmetros do Q-learning
epsilon = 0.1
alpha = 0.5
gamma = 0.9

# Estado inicial
estado = random.choice(list(hex_map))
estado_idx = hex_index[estado]

# Iniciar visualização
plt.ion()

# Loop de aprendizado + visualização
for passo in range(100):
    desenhar_mapa(hex_map, agente=estado)

    acoes_validas = get_valid_actions(estado, hex_map)
    a_idx, prox_estado = escolher_acao(Q, estado_idx, acoes_validas, epsilon)
    prox_estado_idx = hex_index[prox_estado]

    recompensa = -1
    atualizar_q(Q, estado_idx, a_idx, recompensa, prox_estado_idx, alpha, gamma)

    estado = prox_estado
    estado_idx = prox_estado_idx

# Encerrar visualização
plt.ioff()
plt.show()
