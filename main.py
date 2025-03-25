import heapq
import pygame
import math
from collections import deque

# Globais
WIDTH = 840
HEIGHT = 900
SQUARE_SIZE = 20
COLORS = {
    '-': (120, 0, 0),      # Fios soltos
    '*': (0, 0, 120),      # Piso molhado
    ' ': (200, 200, 200),  # Piso seco
    '|': (139, 69, 19),    # Porta
    '!': (139, 69, 19),    # Porta Saida
    '#': (50, 50, 50),     # Parede
    'E': (0, 255, 0),      # Eleven (verde)
    'D': (255, 255, 0),    # Dustin (amarelo)
    'M': (255, 165, 0),    # Mike (laranja)
    'L': (128, 0, 128),    # Lucas (roxo)
    'W': (0, 255, 255),    # Will (ciano)
    'V': (100, 100, 100)   # Visitado
}

terrains = {
    '-': 6,  # Fios soltos
    '*': 3,  # Piso molhado
    ' ': 1,  # Piso seco
    '|': 4,  # Porta
    '!': 4,  # Saida (porta)
    '#': float('inf')  # Parede (infinito)
}

def read_map(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    return [list(line.strip()) for line in lines]

def draw_map(screen, map_matrix, custo, caminho, custo_atual):
    for y, line in enumerate(map_matrix):
        for x, cell in enumerate(line):
            color = COLORS.get(cell, (0, 0, 0))
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            )

    font = pygame.font.Font(None, 36)

    if custo == -1:
        text_surface = font.render("Encontrando custo total...", True, (255, 255, 255))
    else:
        text_surface = font.render(f"Custo total: {custo}", True, (255, 255, 255))

    if caminho is None:
        lines = [
            "Caminho não encontrado",
            "Não é possível salvar todos os amigos"
        ]
        # Renderiza cada linha separadamente
        text_surfaces = [font.render(line, True, (255, 0, 0)) for line in lines]
    else:
        text_surfaces = [font.render("", True, (255, 0, 0))]

    if custo_atual != -1:
        text_surface2 = font.render(f"Custo atual: {custo_atual}", True, (255, 255, 255))
    else:
        text_surface2 = font.render("", True, (255, 0, 0))

    screen.blit(text_surface, (10, 850))

    y_offset = 380
    for text_surface in text_surfaces:
        screen.blit(text_surface, (200, y_offset))
        y_offset += 40
    screen.blit(text_surface2, (350, 850))

def find_position(map_matrix, target):
    for y, line in enumerate(map_matrix):
        for x, cell in enumerate(line):
            if cell == target:
                return (y, x)
    return None

def gen_cost_matrix(map):
    cost_matrix = []
    for line in map:
        new_line = []
        for cell in line:
            if cell in terrains:
                new_line.append(terrains[cell])
            else:
                new_line.append(cell)
        cost_matrix.append(new_line)
    return cost_matrix

def update_map(map_matrix, current_pos, new_pos):
    y, x = current_pos
    ny, nx = new_pos

    map_matrix[y][x] = 'V'
    map_matrix[ny][nx] = 'E'

def initialize_game_window(width, height):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mapa do Laboratório")
    return screen

def heuristica_manhattan_simples(cost_matrix, end):
    rows, cols = len(cost_matrix), len(cost_matrix[0])
    heuristic = [[0 for _ in range(cols)] for _ in range(rows)]

    ey, ex = end

    for y in range(rows):
        for x in range(cols):
            heuristic[y][x] = abs(ey - y) + abs(ex - x)

    return heuristic

def heuristica_manhattan(cost_matrix, end):
    rows, cols = len(cost_matrix), len(cost_matrix[0])
    heuristic = [[float('inf') for _ in range(cols)] for _ in range(rows)]
    queue = deque([end])  # Começa do destino
    heuristic[end[0]][end[1]] = 0  # Distância para si mesmo é 0

    while queue:
        y, x = queue.popleft()
        current_cost = heuristic[y][x]

        neighbors = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
        for ny, nx in neighbors:
            if 0 <= ny < rows and 0 <= nx < cols:
                if cost_matrix[ny][nx] != float('inf') and heuristic[ny][nx] == float('inf'):
                    # Atualiza a distância se a célula for acessível
                    heuristic[ny][nx] = current_cost + 1
                    queue.append((ny, nx))

    return heuristic

# A* baseado no algoritmo de busca custo uniforme do livro de Inteligência Artificial Russell Norvig
def a_star(cost_matrix, start, end):
    start_y, start_x = start
    end_y, end_x = end

    if cost_matrix[start_y][start_x] == math.inf or cost_matrix[end_y][end_x] == math.inf:
        return None, math.inf

    # Calcula a matriz de heurísticas
    heuristic = heuristica_manhattan(cost_matrix, end)

    if heuristic[start_y][start_x] == math.inf or heuristic[end_y][end_x] == math.inf:
        return None, math.inf

    # Fronteira
    frontier = []
    heapq.heappush(frontier, (0, start_y, start_x))

    # Custo do caminho até cada célula
    cost_so_far = {(start_y, start_x): 0}

    # Caminho percorrido
    came_from = {(start_y, start_x): None}

    while frontier:
        _, current_y, current_x = heapq.heappop(frontier)

        # Objetivo
        if (current_y, current_x) == (end_y, end_x):
            break

        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_y, next_x = current_y + dy, current_x + dx

            # Verifica se está dentro dos limites da matriz
            if 0 <= next_y < len(cost_matrix) and 0 <= next_x < len(cost_matrix[0]):
                if cost_matrix[next_y][next_x] == math.inf:
                    continue

                # Custo até o próximo nó
                new_cost = cost_so_far[(current_y, current_x)] + (1 if isinstance(cost_matrix[next_y][next_x], str) else cost_matrix[next_y][next_x])

                # Se o próximo nó não foi visitado ou se encontrou um caminho mais barato
                if (next_y, next_x) not in cost_so_far or new_cost < cost_so_far[(next_y, next_x)]:
                    cost_so_far[(next_y, next_x)] = new_cost
                    priority = new_cost + heuristic[next_y][next_x]
                    heapq.heappush(frontier, (priority, next_y, next_x))
                    came_from[(next_y, next_x)] = (current_y, current_x)

    # Reconstruir o caminho
    path = []
    current = (end_y, end_x)
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()

    return path, cost_so_far.get((end_y, end_x), math.inf)

def main():
    map_file = "laboratorio/laboratorio.txt"
    lab_map = read_map(map_file)

    custo_total = 0

    screen = initialize_game_window(WIDTH, HEIGHT)

    cost_matrix = gen_cost_matrix(lab_map)

    current_pos = find_position(lab_map, 'E')
    print(f"Posição inicial da Eleven: {current_pos}")

    objetivos = [
        find_position(lab_map, 'D'),
        find_position(lab_map, 'L'),
        find_position(lab_map, 'M'),
        find_position(lab_map, 'W'),
        find_position(lab_map, '!')  # Saída
    ]

    custo_atual = 0
    for objetivo in objetivos:
        print(f"Buscando para o objetivo: {objetivo}")

        caminho, custo = a_star(cost_matrix, current_pos, objetivo)

        if caminho is None:
            print(f"Não foi possível encontrar caminho para o objetivo: {objetivo}")
            break

        print(f"Caminho encontrado: {caminho}, Custo: {custo}")
        custo_total = custo_total + custo
        for pos in caminho[1:]:
            update_map(lab_map, current_pos, pos)
            current_pos = pos

            x, y = pos

            custo_atual = custo_atual + (1 if isinstance(cost_matrix[x][y], str) else cost_matrix[x][y])

            screen.fill((0, 0, 0))
            draw_map(screen, lab_map, -1, caminho, custo_atual)
            pygame.display.flip()
            pygame.time.wait(100)

    print(f"Custo Total: {custo_total}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        draw_map(screen, lab_map, custo_total, caminho, -1)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
