import matplotlib.pyplot as plt
import hexalattice.hexalattice as hex

# Cria e plota uma grade hexagonal 5x5
nx ,ny= 11,11

hex_centers, _ = hex.create_hex_grid(
    nx=nx,
    ny=nx,
    do_plot=True
)
matriz_hex = {}
index = 0
for i in range(nx):       # colunas
    for j in range(ny):   # linhas
        centro = hex_centers[index]
        matriz_hex[(j, i)] = centro 
        index += 1
        
        
fig, ax = plt.subplots()
for (j, i), (x, y) in matriz_hex.items():
    hex.add_single_hexagon(ax, center=(x, y), face_color='lightgray', edge_color='black')
    ax.text(x, y, f"{j},{i}", ha='center', va='center', fontsize=8)

ax.set_aspect('equal')
plt.axis('off')
plt.show()

# Aguarda o usuário pressionar Enter para encerrar o script
input("Pressione Enter para sair...")

