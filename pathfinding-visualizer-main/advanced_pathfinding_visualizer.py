import pygame
import math
import os
from queue import PriorityQueue, Queue, LifoQueue

# ========== INITIAL SETUP ==========
pygame.init()
pygame.font.init()

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

GRID_WIDTH = int(min(screen_width, screen_height) * 0.75)
UI_WIDTH = 500
WINDOW_HEIGHT = max(GRID_WIDTH, 600)
TOTAL_WIDTH = GRID_WIDTH + UI_WIDTH

# Create single window with grid on left, UI on right
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,28"
WIN = pygame.display.set_mode((TOTAL_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pathfinding Visualizer by lal singh 🧭")

# Create separate surfaces for grid and UI sections
GRID_SURFACE = pygame.Surface((GRID_WIDTH, GRID_WIDTH))
UI_SURFACE = pygame.Surface((UI_WIDTH, WINDOW_HEIGHT))


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (100, 149, 237)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (138, 43, 226)
ORANGE = (255, 165, 0)
GREY = (200, 200, 200)

# ========== NODE CLASS ==========
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): return self.row, self.col
    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == GREEN
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == PURPLE
    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = GREEN
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = PURPLE
    def make_path(self): self.color = YELLOW
    def draw(self, win): pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

# ========== UTILITIES ==========
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw, ui_surface, algo_name, win, grid_width):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
        draw_ui_window(ui_surface, algo_name)
        # Blit both surfaces to main window
        win.blit(GRID_SURFACE, (0, 0))
        win.blit(UI_SURFACE, (grid_width, 0))
        # Redraw divider line
        pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
        pygame.display.update()

# ========== ALGORITHMS ==========

def a_star(draw, grid, start, end, ui_surface, algo_name, win):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    f_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw, ui_surface, algo_name, win, GRID_WIDTH)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g = g_score[current] + 1
            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score[neighbor] = temp_g + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        draw_ui_window(ui_surface, algo_name)
        win.blit(GRID_SURFACE, (0, 0))
        win.blit(UI_SURFACE, (GRID_WIDTH, 0))
        pygame.draw.line(win, (180, 180, 180), (GRID_WIDTH, 0), (GRID_WIDTH, WINDOW_HEIGHT), 2)
        pygame.display.update()
        if current != start:
            current.make_closed()
    return False


def dijkstra(draw, grid, start, end, ui_surface, algo_name, win):
    pq = PriorityQueue()
    pq.put((0, start))
    dist = {node: float("inf") for row in grid for node in row}
    dist[start] = 0
    came_from = {}

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = pq.get()[1]

        if current == end:
            reconstruct_path(came_from, end, draw, ui_surface, algo_name, win, GRID_WIDTH)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp = dist[current] + 1
            if temp < dist[neighbor]:
                came_from[neighbor] = current
                dist[neighbor] = temp
                pq.put((temp, neighbor))
                neighbor.make_open()

        draw()
        draw_ui_window(ui_surface, algo_name)
        win.blit(GRID_SURFACE, (0, 0))
        win.blit(UI_SURFACE, (GRID_WIDTH, 0))
        pygame.draw.line(win, (180, 180, 180), (GRID_WIDTH, 0), (GRID_WIDTH, WINDOW_HEIGHT), 2)
        pygame.display.update()
        if current != start:
            current.make_closed()
    return False


def bfs(draw, grid, start, end, ui_surface, algo_name, win):
    queue = Queue()
    queue.put(start)
    came_from = {}
    visited = {start}

    while not queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = queue.get()

        if current == end:
            reconstruct_path(came_from, end, draw, ui_surface, algo_name, win, GRID_WIDTH)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.put(neighbor)
                neighbor.make_open()

        draw()
        draw_ui_window(ui_surface, algo_name)
        win.blit(GRID_SURFACE, (0, 0))
        win.blit(UI_SURFACE, (GRID_WIDTH, 0))
        pygame.draw.line(win, (180, 180, 180), (GRID_WIDTH, 0), (GRID_WIDTH, WINDOW_HEIGHT), 2)
        pygame.display.update()
        if current != start:
            current.make_closed()
    return False


def dfs(draw, grid, start, end, ui_surface, algo_name, win):
    stack = LifoQueue()
    stack.put(start)
    came_from = {}
    visited = {start}

    while not stack.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = stack.get()

        if current == end:
            reconstruct_path(came_from, end, draw, ui_surface, algo_name, win, GRID_WIDTH)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.put(neighbor)
                neighbor.make_open()

        draw()
        draw_ui_window(ui_surface, algo_name)
        win.blit(GRID_SURFACE, (0, 0))
        win.blit(UI_SURFACE, (GRID_WIDTH, 0))
        pygame.draw.line(win, (180, 180, 180), (GRID_WIDTH, 0), (GRID_WIDTH, WINDOW_HEIGHT), 2)
        pygame.display.update()
        if current != start:
            current.make_closed()
    return False

# ========== DRAWING FUNCTIONS ==========
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([Node(i, j, gap, rows) for j in range(rows)])
    return grid

def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw_grid_window(surface, grid, rows, width):
    """Draw only the grid visualization on the grid surface"""
    surface.fill((255, 215, 0) )

    for row in grid:
        for node in row:
            node.draw(surface)
    draw_grid_lines(surface, rows, width)

def draw_ui_window(ui_surface, algo_name="None"):
    """Draw controls and legends on the UI surface"""
    ui_surface.fill((240, 240, 240))

    # --- Title Bar ---
    title_font = pygame.font.SysFont("arial", 28, bold=True)
    title_text = title_font.render("Pathfinding Visualizer", True, (25, 25, 112))
    title_rect = title_text.get_rect(center=(UI_WIDTH // 2, 30))
    ui_surface.blit(title_text, title_rect)

    # --- Algorithm name display ---
    font = pygame.font.SysFont("arial", 22, bold=True)
    algo_color = (30, 144, 255) if algo_name != "None" else (100, 100, 100)
    text = font.render(f"Algorithm: {algo_name}", True, algo_color)
    text_rect = text.get_rect(center=(UI_WIDTH // 2, 70))
    ui_surface.blit(text, text_rect)

    # --- Exit button ---
    button_font = pygame.font.SysFont("arial", 18)
    exit_text = button_font.render("Exit ✖", True, (255, 255, 255))
    exit_rect = pygame.Rect(UI_WIDTH - 90, 15, 80, 30)
    pygame.draw.rect(ui_surface, (220, 20, 60), exit_rect, border_radius=6)
    ui_surface.blit(exit_text, (UI_WIDTH - 75, 20))

    # --- Legend box (Colors) ---
    legend_x = 30
    legend_y = 95
    legend_font = pygame.font.SysFont("times new roman", 14, bold=True)

    legend_items = [
        ("Start", (255, 165, 0)),    # Orange
        ("End", (128, 0, 128)),      # Purple
        ("Barrier", (0, 0, 0)),      # Black
        ("Open Set", (0, 0, 255)),   # Blue
        ("Closed Set", (255, 0, 0)), # Red
        ("Path", (255, 255, 0)),     # Yellow
        ("Empty", (255, 255, 255)),  # White
    ]

    box_width = UI_WIDTH - 60
    box_height = 220
    pygame.draw.rect(ui_surface, (255, 255, 255), (legend_x - 5, legend_y - 5, box_width, box_height), border_radius=8)
    pygame.draw.rect(ui_surface, (180, 180, 180), (legend_x - 5, legend_y - 5, box_width, box_height), 2, border_radius=8)
    title = legend_font.render("Color Legend:", True, (0, 0, 0))
    ui_surface.blit(title, (legend_x, legend_y - 25))

    for i, (label, color) in enumerate(legend_items):
        y_offset = legend_y + i * 28
        pygame.draw.rect(ui_surface, color, (legend_x, y_offset, 25, 25))
        pygame.draw.rect(ui_surface, (0, 0, 0), (legend_x, y_offset, 25, 25), 1)
        text = legend_font.render(label, True, (0, 0, 0))
        ui_surface.blit(text, (legend_x + 35, y_offset + 4))

    # --- Algorithm Legend Box ---
    algo_legend_x = 30
    algo_legend_y = 340
    algo_items = [
        ("1 → A* (Fastest)", (30, 144, 255)),
        ("2 → Dijkstra's", (50, 205, 50)),
        ("3 → BFS", (255, 140, 0)),
        ("4 → DFS", (138, 43, 226)),
        ("SPACE → Run", (0, 0, 0)),
        ("C → Clear Grid", (0, 0, 0)),
    ]

    algo_box_height = 200
    pygame.draw.rect(ui_surface, (255, 255, 255), (algo_legend_x - 5, algo_legend_y - 5, box_width, algo_box_height), border_radius=8)
    pygame.draw.rect(ui_surface, (180, 180, 180), (algo_legend_x - 5, algo_legend_y - 5, box_width, algo_box_height), 2, border_radius=8)
    title2 = legend_font.render("Controls:", True, (0, 0, 0))
    ui_surface.blit(title2, (algo_legend_x, algo_legend_y - 25))

    for i, (label, color) in enumerate(algo_items):
        y_offset = algo_legend_y + i * 28
        text = legend_font.render(label, True, color)
        ui_surface.blit(text, (algo_legend_x, y_offset + 4))

    # --- Instructions Box ---
    instructions_y = 560
    instructions_font = pygame.font.SysFont("times new roman", 16, bold=True)
    instructions = [
        "  RULES :",
        "• Left Click: Place Start/End/Barriers",
        "• Right Click: Remove Nodes",
        "• Select algorithm (1-4), then press SPACE"
    ]
    
    #pygame.draw.rect(ui_surface, (255, 255, 255), (algo_legend_x - 5, instructions_y - 30, box_width, 60), border_radius=8)
    #pygame.draw.rect(ui_surface, (180, 180, 180), (algo_legend_x - 5, instructions_y - 30, box_width, 60), 2, border_radius=8)
    
    for i, instruction in enumerate(instructions):
        text = instructions_font.render(instruction, True, (50, 50, 50))
        ui_surface.blit(text, (algo_legend_x, instructions_y + i * 18))

    return exit_rect

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

# ========== MAIN LOOP ==========
def main(win, grid_surface, ui_surface, grid_width):
    ROWS = 40
    grid = make_grid(ROWS, grid_width)

    start = None
    end = None
    run = True
    algo = "None"

    # Initialize surfaces
    exit_rect = draw_ui_window(ui_surface, algo)
    draw_grid_window(grid_surface, grid, ROWS, grid_width)
    
    # Draw divider line between grid and UI
    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
    
    # Initial blit
    win.blit(grid_surface, (0, 0))
    win.blit(ui_surface, (grid_width, 0))
    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
    pygame.display.update()

    while run:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mouse_x, mouse_y = mouse_pos
                
                # Check if click is in UI section
                if mouse_x >= grid_width:
                    # Click is in UI section - adjust coordinates for UI surface
                    ui_x = mouse_x - grid_width
                    ui_y = mouse_y
                    ui_mouse_pos = (ui_x, ui_y)
                    
                    # Check exit button
                    exit_rect_absolute = pygame.Rect(exit_rect.x + grid_width, exit_rect.y, exit_rect.width, exit_rect.height)
                    if exit_rect_absolute.collidepoint(mouse_pos):
                        run = False
                        break
                else:
                    # Click is in grid section
                    try:
                        row, col = get_clicked_pos(mouse_pos, ROWS, grid_width)
                        if 0 <= row < ROWS and 0 <= col < ROWS:
                            node = grid[row][col]
                            if not start and node != end:
                                start = node
                                start.make_start()
                            elif not end and node != start:
                                end = node
                                end.make_end()
                            elif node != end and node != start:
                                node.make_barrier()
                            draw_grid_window(grid_surface, grid, ROWS, grid_width)
                            win.blit(grid_surface, (0, 0))
                            pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                            pygame.display.update()
                    except (ValueError, IndexError):
                        pass

            elif pygame.mouse.get_pressed()[2]:
                # Right click
                mouse_pos = pygame.mouse.get_pos()
                mouse_x = mouse_pos[0]
                if mouse_x < grid_width:  # Only in grid section
                    try:
                        row, col = get_clicked_pos(mouse_pos, ROWS, grid_width)
                        if 0 <= row < ROWS and 0 <= col < ROWS:
                            node = grid[row][col]
                            node.reset()
                            if node == start:
                                start = None
                            elif node == end:
                                end = None
                            draw_grid_window(grid_surface, grid, ROWS, grid_width)
                            win.blit(grid_surface, (0, 0))
                            pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                            pygame.display.update()
                    except (ValueError, IndexError):
                        pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, grid_width)
                    draw_grid_window(grid_surface, grid, ROWS, grid_width)
                    win.blit(grid_surface, (0, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

                if event.key == pygame.K_1:
                    algo = "A*"
                    draw_ui_window(ui_surface, algo)
                    win.blit(ui_surface, (grid_width, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

                if event.key == pygame.K_2:
                    algo = "Dijkstra"
                    draw_ui_window(ui_surface, algo)
                    win.blit(ui_surface, (grid_width, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

                if event.key == pygame.K_3:
                    algo = "BFS"
                    draw_ui_window(ui_surface, algo)
                    win.blit(ui_surface, (grid_width, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

                if event.key == pygame.K_4:
                    algo = "DFS"
                    draw_ui_window(ui_surface, algo)
                    win.blit(ui_surface, (grid_width, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

                if event.key == pygame.K_SPACE and start and end:
                    # Reset grid colors except barriers
                    for row in grid:
                        for node in row:
                            if not node.is_barrier() and node != start and node != end:
                                node.reset()
                    
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    draw_grid_window(grid_surface, grid, ROWS, grid_width)
                    draw_ui_window(ui_surface, algo)
                    win.blit(grid_surface, (0, 0))
                    win.blit(ui_surface, (grid_width, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

                    grid_draw = lambda: draw_grid_window(grid_surface, grid, ROWS, grid_width)
                    
                    if algo == "A*":
                        a_star(grid_draw, grid, start, end, ui_surface, algo, win)
                    elif algo == "Dijkstra":
                        dijkstra(grid_draw, grid, start, end, ui_surface, algo, win)
                    elif algo == "BFS":
                        bfs(grid_draw, grid, start, end, ui_surface, algo, win)
                    elif algo == "DFS":
                        dfs(grid_draw, grid, start, end, ui_surface, algo, win)
                    
                    draw_grid_window(grid_surface, grid, ROWS, grid_width)
                    draw_ui_window(ui_surface, algo)
                    win.blit(grid_surface, (0, 0))
                    win.blit(ui_surface, (grid_width, 0))
                    pygame.draw.line(win, (180, 180, 180), (grid_width, 0), (grid_width, WINDOW_HEIGHT), 2)
                    pygame.display.update()

        # Small delay to prevent high CPU usage
        pygame.time.Clock().tick(6)

    pygame.quit()

main(WIN, GRID_SURFACE, UI_SURFACE, GRID_WIDTH)
