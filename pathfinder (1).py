"""
AI Pathfinder Visualizer - ALL 6 ALGORITHMS
============================================
Complete pathfinding visualizer with:
1. Breadth-First Search (BFS)
2. Depth-First Search (DFS)
3. Uniform-Cost Search (UCS)
4. Depth-Limited Search (DLS)
5. Iterative Deepening DFS (IDDFS)
6. Bidirectional Search

Installation:
    pip install pygame

Controls:
    Algorithm Selection: Click algorithm buttons
    Mouse: Click/drag to draw walls
    S + Click: Set Start
    T + Click: Set Target
    SPACE: Run selected algorithm
    C: Clear search
    R: Reset grid
"""

import pygame
import sys
from collections import deque
import heapq
from enum import Enum
import random


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    TARGET = 3


class CellState(Enum):
    NONE = 0
    FRONTIER = 1
    EXPLORED = 2
    PATH = 3
    FRONTIER2 = 4  # For bidirectional search (second frontier)
    EXPLORED2 = 5  # For bidirectional search (second explored)


class Colors:
    """Color palette"""
    EMPTY = (255, 255, 255)
    WALL = (44, 62, 80)
    START = (39, 174, 96)
    TARGET = (231, 76, 60)
    FRONTIER = (243, 156, 18)
    EXPLORED = (52, 152, 219)
    PATH = (155, 89, 182)
    FRONTIER2 = (230, 126, 34)      # Orange for second frontier
    EXPLORED2 = (26, 188, 156)      # Teal for second explored
    GRID_LINE = (189, 195, 199)
    BG = (236, 240, 241)
    UI_BG = (52, 73, 94)
    UI_TEXT = (236, 240, 241)
    BUTTON = (46, 204, 113)
    BUTTON_HOVER = (39, 174, 96)
    BUTTON_SELECTED = (241, 196, 15)
    WARNING = (230, 126, 34)
    SUCCESS = (46, 204, 113)
    ERROR = (231, 76, 60)


class AllAlgorithmsPathfinder:
    """Complete pathfinder with all 6 algorithms"""
    
    def __init__(self, rows=30, cols=50, cell_size=16):
        pygame.init()
        
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        
        self.grid_width = cols * cell_size
        self.grid_height = rows * cell_size
        self.ui_height = 220
        self.window_width = self.grid_width
        self.window_height = self.grid_height + self.ui_height
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("🎮 AI Pathfinder - All 6 Algorithms")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 18)
        self.info_font = pygame.font.Font(None, 16)
        self.stats_font = pygame.font.Font(None, 15)
        
        # Grid
        self.grid = [[CellType.EMPTY for _ in range(cols)] for _ in range(rows)]
        self.cell_states = [[CellState.NONE for _ in range(cols)] for _ in range(rows)]
        
        # State
        self.start = None
        self.target = None
        self.mode = 'wall'
        self.dragging = False
        self.drag_erase = False
        
        # Algorithm selection
        self.selected_algorithm = 'BFS'
        self.algorithms = ['BFS', 'DFS', 'UCS', 'DLS', 'IDDFS', 'Bidirectional']
        
        # Search state
        self.frontier = None
        self.explored = set()
        self.came_from = {}
        self.final_path = []
        self.search_complete = False
        self.searching = False
        self.step_count = 0
        
        # Algorithm-specific state
        self.depth_limit = 20  # For DLS
        self.current_depth_limit = 0  # For IDDFS
        self.cost_so_far = {}  # For UCS
        
        # Bidirectional specific
        self.frontier_forward = None
        self.frontier_backward = None
        self.explored_forward = set()
        self.explored_backward = set()
        self.came_from_forward = {}
        self.came_from_backward = {}
        self.meeting_point = None
        
        # Animation
        self.animation_delay = 20
        self.last_step_time = 0
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self.status_message = "Select an algorithm and create a maze!"
        self.status_color = Colors.UI_TEXT
        
        self.setup_buttons()
    
    def setup_buttons(self):
        """Setup all UI buttons"""
        bw, bh = 75, 28
        spacing = 6
        start_x = 10
        
        # Row 1: Algorithm selection
        y1 = 12
        self.algo_buttons = []
        for i, algo in enumerate(self.algorithms):
            btn = self.create_button(
                start_x + (bw + spacing) * i, y1, bw, bh,
                algo, lambda a=algo: self.select_algorithm(a),
                Colors.BUTTON_SELECTED if algo == self.selected_algorithm else Colors.BUTTON
            )
            self.algo_buttons.append(btn)
        
        # Row 2: Main controls
        y2 = 50
        self.control_buttons = [
            self.create_button(start_x, y2, bw, bh, "Start (S)", self.set_start_mode),
            self.create_button(start_x + (bw + spacing) * 1, y2, bw, bh, "Target (T)", self.set_target_mode),
            self.create_button(start_x + (bw + spacing) * 2, y2, bw, bh, "▶ Run", self.start_search, Colors.SUCCESS),
            self.create_button(start_x + (bw + spacing) * 3, y2, bw, bh, "Clear", self.clear_search_visual, Colors.WARNING),
            self.create_button(start_x + (bw + spacing) * 4, y2, bw, bh, "Reset", self.reset_grid, Colors.ERROR),
        ]
        
        # Row 3: Presets
        y3 = 88
        self.preset_buttons = [
            self.create_button(start_x, y3, bw, bh, "Simple", lambda: self.load_preset('simple')),
            self.create_button(start_x + (bw + spacing) * 1, y3, bw, bh, "Maze", lambda: self.load_preset('maze')),
            self.create_button(start_x + (bw + spacing) * 2, y3, bw, bh, "Spiral", lambda: self.load_preset('spiral')),
            self.create_button(start_x + (bw + spacing) * 3, y3, bw, bh, "Random", lambda: self.load_preset('random')),
        ]
        
        # Speed and depth controls
        speed_x = self.window_width - 160
        self.misc_buttons = [
            self.create_button(speed_x, y1, 35, bh, "➖", self.decrease_speed),
            self.create_button(speed_x + 40, y1, 35, bh, "➕", self.increase_speed),
            self.create_button(speed_x, y2, 35, bh, "D-", self.decrease_depth),
            self.create_button(speed_x + 40, y2, 35, bh, "D+", self.increase_depth),
        ]
        
        self.all_buttons = self.algo_buttons + self.control_buttons + self.preset_buttons + self.misc_buttons
    
    def create_button(self, x, y, w, h, text, callback, color=Colors.BUTTON):
        return {
            'rect': pygame.Rect(x, y, w, h),
            'text': text,
            'color': color,
            'callback': callback,
            'enabled': True,
            'base_color': color
        }
    
    def select_algorithm(self, algo):
        """Select which algorithm to use"""
        if not self.searching:
            self.selected_algorithm = algo
            # Update button colors
            for btn in self.algo_buttons:
                if btn['text'] == algo:
                    btn['color'] = Colors.BUTTON_SELECTED
                else:
                    btn['color'] = btn['base_color']
            self.update_status(f"{algo} selected! Press ▶ Run or SPACE to start", Colors.SUCCESS)
    
    def set_start_mode(self):
        if not self.searching:
            self.mode = 'start'
            self.update_status("Click anywhere to place START point", Colors.SUCCESS)
    
    def set_target_mode(self):
        if not self.searching:
            self.mode = 'target'
            self.update_status("Click anywhere to place TARGET point", Colors.ERROR)
    
    def increase_speed(self):
        self.animation_delay = max(1, self.animation_delay - 10)
        self.update_status(f"Speed: {self.animation_delay}ms delay", Colors.UI_TEXT)
    
    def decrease_speed(self):
        self.animation_delay = min(200, self.animation_delay + 10)
        self.update_status(f"Speed: {self.animation_delay}ms delay", Colors.UI_TEXT)
    
    def increase_depth(self):
        self.depth_limit = min(100, self.depth_limit + 5)
        self.update_status(f"DLS Depth Limit: {self.depth_limit}", Colors.UI_TEXT)
    
    def decrease_depth(self):
        self.depth_limit = max(5, self.depth_limit - 5)
        self.update_status(f"DLS Depth Limit: {self.depth_limit}", Colors.UI_TEXT)
    
    def update_status(self, message, color=None):
        self.status_message = message
        if color:
            self.status_color = color
    
    def reset_grid(self):
        if not self.searching:
            self.grid = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
            self.cell_states = [[CellState.NONE for _ in range(self.cols)] for _ in range(self.rows)]
            self.start = None
            self.target = None
            self.clear_search()
            self.mode = 'wall'
            self.update_status("Grid reset!", Colors.UI_TEXT)
    
    def clear_search_visual(self):
        if not self.searching:
            self.clear_search()
            self.cell_states = [[CellState.NONE for _ in range(self.cols)] for _ in range(self.rows)]
            self.update_status("Search cleared!", Colors.WARNING)
    
    def clear_search(self):
        self.frontier = None
        self.explored = set()
        self.came_from = {}
        self.final_path = []
        self.search_complete = False
        self.searching = False
        self.step_count = 0
        self.cost_so_far = {}
        self.current_depth_limit = 0
        
        # Bidirectional
        self.frontier_forward = None
        self.frontier_backward = None
        self.explored_forward = set()
        self.explored_backward = set()
        self.came_from_forward = {}
        self.came_from_backward = {}
        self.meeting_point = None
    
    def load_preset(self, preset_name):
        """Load preset maze"""
        if self.searching:
            return
        
        self.reset_grid()
        
        if preset_name == 'simple':
            self.start = (5, 5)
            self.target = (self.rows - 6, self.cols - 6)
        
        elif preset_name == 'maze':
            self.start = (2, 2)
            self.target = (self.rows - 3, self.cols - 3)
            for i in range(5, self.rows - 5, 8):
                for j in range(5, self.cols - 5):
                    self.grid[i][j] = CellType.WALL
                for j in range(10, self.cols - 5):
                    if i + 4 < self.rows:
                        self.grid[i + 4][j] = CellType.WALL
                self.grid[i][self.cols - 10] = CellType.EMPTY
                if i + 4 < self.rows:
                    self.grid[i + 4][10] = CellType.EMPTY
        
        elif preset_name == 'spiral':
            self.start = (self.rows // 2, self.cols // 2)
            self.target = (2, 2)
            for layer in range(1, min(self.rows, self.cols) // 4):
                offset = layer * 3
                for j in range(offset, self.cols - offset):
                    if offset < self.rows:
                        self.grid[offset][j] = CellType.WALL
                for i in range(offset, self.rows - offset):
                    if self.cols - offset - 1 >= 0:
                        self.grid[i][self.cols - offset - 1] = CellType.WALL
                for j in range(offset, self.cols - offset):
                    if self.rows - offset - 1 >= 0:
                        self.grid[self.rows - offset - 1][j] = CellType.WALL
                for i in range(offset + 1, self.rows - offset):
                    if offset >= 0:
                        self.grid[i][offset] = CellType.WALL
                if offset + 3 < self.cols:
                    self.grid[offset][offset + 3] = CellType.EMPTY
        
        elif preset_name == 'random':
            self.start = (5, 5)
            self.target = (self.rows - 6, self.cols - 6)
            for i in range(self.rows):
                for j in range(self.cols):
                    if (i, j) != self.start and (i, j) != self.target:
                        if random.random() < 0.25:
                            self.grid[i][j] = CellType.WALL
        
        if self.start:
            self.grid[self.start[0]][self.start[1]] = CellType.START
        if self.target:
            self.grid[self.target[0]][self.target[1]] = CellType.TARGET
        
        self.update_status(f"{preset_name.capitalize()} maze loaded!", Colors.SUCCESS)
    
    def get_grid_pos(self, mouse_pos):
        x, y = mouse_pos
        y -= self.ui_height
        if y < 0 or y >= self.grid_height:
            return None
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            for button in self.all_buttons:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button['rect'].collidepoint(event.pos) and button['enabled']:
                        button['callback']()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_s:
                    self.set_start_mode()
                elif event.key == pygame.K_t:
                    self.set_target_mode()
                elif event.key == pygame.K_SPACE:
                    self.start_search()
                elif event.key == pygame.K_c:
                    self.clear_search_visual()
                elif event.key == pygame.K_r:
                    self.reset_grid()
                elif event.key == pygame.K_1:
                    self.select_algorithm('BFS')
                elif event.key == pygame.K_2:
                    self.select_algorithm('DFS')
                elif event.key == pygame.K_3:
                    self.select_algorithm('UCS')
                elif event.key == pygame.K_4:
                    self.select_algorithm('DLS')
                elif event.key == pygame.K_5:
                    self.select_algorithm('IDDFS')
                elif event.key == pygame.K_6:
                    self.select_algorithm('Bidirectional')
            
            if event.type == pygame.MOUSEBUTTONDOWN and not self.searching:
                grid_pos = self.get_grid_pos(event.pos)
                if grid_pos:
                    row, col = grid_pos
                    if event.button == 1:
                        self.dragging = True
                        self.handle_grid_click(row, col)
                    elif event.button == 3:
                        if self.grid[row][col] == CellType.WALL:
                            self.grid[row][col] = CellType.EMPTY
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION and self.dragging and not self.searching:
                grid_pos = self.get_grid_pos(event.pos)
                if grid_pos and self.mode == 'wall':
                    row, col = grid_pos
                    if (row, col) != self.start and (row, col) != self.target:
                        if self.drag_erase:
                            self.grid[row][col] = CellType.EMPTY
                        else:
                            self.grid[row][col] = CellType.WALL
        
        return True
    
    def handle_grid_click(self, row, col):
        if self.mode == 'wall':
            if (row, col) != self.start and (row, col) != self.target:
                if self.grid[row][col] == CellType.WALL:
                    self.grid[row][col] = CellType.EMPTY
                    self.drag_erase = True
                else:
                    self.grid[row][col] = CellType.WALL
                    self.drag_erase = False
        
        elif self.mode == 'start':
            if self.start:
                old_row, old_col = self.start
                self.grid[old_row][old_col] = CellType.EMPTY
            self.start = (row, col)
            self.grid[row][col] = CellType.START
            self.mode = 'wall'
            self.update_status("Start set! Now set Target (T)", Colors.SUCCESS)
        
        elif self.mode == 'target':
            if self.target:
                old_row, old_col = self.target
                self.grid[old_row][old_col] = CellType.EMPTY
            self.target = (row, col)
            self.grid[row][col] = CellType.TARGET
            self.mode = 'wall'
            self.update_status("Target set! Press ▶ Run", Colors.SUCCESS)
    
    def start_search(self):
        """Initialize search based on selected algorithm"""
        if self.searching:
            return
        if not self.start or not self.target:
            self.update_status("ERROR: Set Start and Target first!", Colors.ERROR)
            return
        
        self.clear_search()
        self.cell_states = [[CellState.NONE for _ in range(self.cols)] for _ in range(self.rows)]
        self.searching = True
        
        algo = self.selected_algorithm
        
        if algo == 'BFS':
            self.frontier = deque([self.start])
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
        
        elif algo == 'DFS':
            self.frontier = [self.start]  # Stack
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
        
        elif algo == 'UCS':
            self.frontier = [(0, self.start)]  # Priority queue: (cost, node)
            heapq.heapify(self.frontier)
            self.came_from = {self.start: None}
            self.cost_so_far = {self.start: 0}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
        
        elif algo == 'DLS':
            self.frontier = [(self.start, 0)]  # Stack with depth: (node, depth)
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
        
        elif algo == 'IDDFS':
            self.current_depth_limit = 0
            self.frontier = [(self.start, 0)]
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
        
        elif algo == 'Bidirectional':
            self.frontier_forward = deque([self.start])
            self.frontier_backward = deque([self.target])
            self.came_from_forward = {self.start: None}
            self.came_from_backward = {self.target: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
            self.cell_states[self.target[0]][self.target[1]] = CellState.FRONTIER2
        
        self.update_status(f"🔍 {algo} searching...", Colors.WARNING)
    
    def get_neighbors(self, node):
        """Get neighbors in clockwise order"""
        row, col = node
        neighbors = []
        movements = [(-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1)]
        
        for dr, dc in movements:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                if self.grid[new_row][new_col] != CellType.WALL:
                    neighbors.append((new_row, new_col))
        return neighbors
    
    def get_move_cost(self, from_node, to_node):
        """Calculate cost of move (diagonal = 1.414, straight = 1.0)"""
        r1, c1 = from_node
        r2, c2 = to_node
        if abs(r1 - r2) + abs(c1 - c2) == 2:  # Diagonal
            return 1.414
        return 1.0
    
    def algorithm_step(self):
        """Execute one step of the selected algorithm"""
        algo = self.selected_algorithm
        
        if algo == 'BFS':
            return self.bfs_step()
        elif algo == 'DFS':
            return self.dfs_step()
        elif algo == 'UCS':
            return self.ucs_step()
        elif algo == 'DLS':
            return self.dls_step()
        elif algo == 'IDDFS':
            return self.iddfs_step()
        elif algo == 'Bidirectional':
            return self.bidirectional_step()
    
    def bfs_step(self):
        """BFS step"""
        if not self.frontier:
            self.finish_search(False)
            return
        
        current = self.frontier.popleft()
        self.explored.add(current)
        if current != self.start and current != self.target:
            self.cell_states[current[0]][current[1]] = CellState.EXPLORED
        
        if current == self.target:
            self.reconstruct_path()
            self.finish_search(True)
            return
        
        for neighbor in self.get_neighbors(current):
            if neighbor not in self.explored and neighbor not in self.frontier:
                self.frontier.append(neighbor)
                self.came_from[neighbor] = current
                if neighbor != self.target:
                    self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER
        
        self.step_count += 1
    
    def dfs_step(self):
        """DFS step"""
        if not self.frontier:
            self.finish_search(False)
            return
        
        current = self.frontier.pop()  # LIFO - Stack
        
        if current in self.explored:
            return
        
        self.explored.add(current)
        if current != self.start and current != self.target:
            self.cell_states[current[0]][current[1]] = CellState.EXPLORED
        
        if current == self.target:
            self.reconstruct_path()
            self.finish_search(True)
            return
        
        for neighbor in reversed(self.get_neighbors(current)):  # Reverse to maintain clockwise
            if neighbor not in self.explored:
                if neighbor not in [n for n in self.frontier]:
                    self.frontier.append(neighbor)
                    if neighbor not in self.came_from:
                        self.came_from[neighbor] = current
                    if neighbor != self.target:
                        self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER
        
        self.step_count += 1
    
    def ucs_step(self):
        """UCS step"""
        if not self.frontier:
            self.finish_search(False)
            return
        
        cost, current = heapq.heappop(self.frontier)
        
        if current in self.explored:
            return
        
        self.explored.add(current)
        if current != self.start and current != self.target:
            self.cell_states[current[0]][current[1]] = CellState.EXPLORED
        
        if current == self.target:
            self.reconstruct_path()
            self.finish_search(True)
            return
        
        for neighbor in self.get_neighbors(current):
            if neighbor not in self.explored:
                new_cost = self.cost_so_far[current] + self.get_move_cost(current, neighbor)
                
                if neighbor not in self.cost_so_far or new_cost < self.cost_so_far[neighbor]:
                    self.cost_so_far[neighbor] = new_cost
                    heapq.heappush(self.frontier, (new_cost, neighbor))
                    self.came_from[neighbor] = current
                    if neighbor != self.target:
                        self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER
        
        self.step_count += 1
    
    def dls_step(self):
        """DLS step"""
        if not self.frontier:
            self.finish_search(False)
            return
        
        current, depth = self.frontier.pop()
        
        if current in self.explored:
            return
        
        self.explored.add(current)
        if current != self.start and current != self.target:
            self.cell_states[current[0]][current[1]] = CellState.EXPLORED
        
        if current == self.target:
            self.reconstruct_path()
            self.finish_search(True)
            return
        
        if depth < self.depth_limit:
            for neighbor in reversed(self.get_neighbors(current)):
                if neighbor not in self.explored:
                    self.frontier.append((neighbor, depth + 1))
                    if neighbor not in self.came_from:
                        self.came_from[neighbor] = current
                    if neighbor != self.target:
                        self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER
        
        self.step_count += 1
    
    def iddfs_step(self):
        """IDDFS step - iterative deepening"""
        if not self.frontier:
            # Increase depth limit and restart
            self.current_depth_limit += 1
            if self.current_depth_limit > 50:  # Max depth limit
                self.finish_search(False)
                return
            
            # Restart search with new depth limit
            self.explored = set()
            self.frontier = [(self.start, 0)]
            self.came_from = {self.start: None}
            self.cell_states = [[CellState.NONE for _ in range(self.cols)] for _ in range(self.rows)]
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
            return
        
        current, depth = self.frontier.pop()
        
        if current in self.explored:
            return
        
        self.explored.add(current)
        if current != self.start and current != self.target:
            self.cell_states[current[0]][current[1]] = CellState.EXPLORED
        
        if current == self.target:
            self.reconstruct_path()
            self.finish_search(True)
            return
        
        if depth < self.current_depth_limit:
            for neighbor in reversed(self.get_neighbors(current)):
                if neighbor not in self.explored:
                    self.frontier.append((neighbor, depth + 1))
                    if neighbor not in self.came_from:
                        self.came_from[neighbor] = current
                    if neighbor != self.target:
                        self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER
        
        self.step_count += 1
    
    def bidirectional_step(self):
        """Bidirectional search step"""
        if not self.frontier_forward and not self.frontier_backward:
            self.finish_search(False)
            return
        
        # Alternate between forward and backward
        if self.step_count % 2 == 0 and self.frontier_forward:
            # Forward search
            current = self.frontier_forward.popleft()
            self.explored_forward.add(current)
            if current != self.start:
                self.cell_states[current[0]][current[1]] = CellState.EXPLORED
            
            # Check if paths meet
            if current in self.explored_backward:
                self.meeting_point = current
                self.reconstruct_bidirectional_path()
                self.finish_search(True)
                return
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in self.explored_forward and neighbor not in self.frontier_forward:
                    self.frontier_forward.append(neighbor)
                    self.came_from_forward[neighbor] = current
                    if neighbor != self.target:
                        self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER
        
        elif self.frontier_backward:
            # Backward search
            current = self.frontier_backward.popleft()
            self.explored_backward.add(current)
            if current != self.target:
                self.cell_states[current[0]][current[1]] = CellState.EXPLORED2
            
            # Check if paths meet
            if current in self.explored_forward:
                self.meeting_point = current
                self.reconstruct_bidirectional_path()
                self.finish_search(True)
                return
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in self.explored_backward and neighbor not in self.frontier_backward:
                    self.frontier_backward.append(neighbor)
                    self.came_from_backward[neighbor] = current
                    if neighbor != self.start:
                        self.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER2
        
        self.step_count += 1
    
    def reconstruct_path(self):
        """Reconstruct path from start to target"""
        self.final_path = []
        current = self.target
        while current in self.came_from:
            self.final_path.append(current)
            current = self.came_from[current]
        self.final_path.append(self.start)
        self.final_path.reverse()
        self.mark_path()
    
    def reconstruct_bidirectional_path(self):
        """Reconstruct path for bidirectional search"""
        self.final_path = []
        
        # Forward path
        current = self.meeting_point
        forward_path = []
        while current in self.came_from_forward:
            forward_path.append(current)
            current = self.came_from_forward[current]
        forward_path.append(self.start)
        forward_path.reverse()
        
        # Backward path
        current = self.meeting_point
        backward_path = []
        if current in self.came_from_backward and self.came_from_backward[current]:
            current = self.came_from_backward[current]
            while current in self.came_from_backward:
                backward_path.append(current)
                current = self.came_from_backward[current]
            backward_path.append(self.target)
        
        self.final_path = forward_path + backward_path
        self.mark_path()
    
    def mark_path(self):
        """Mark the final path"""
        for node in self.final_path:
            if node != self.start and node != self.target:
                self.cell_states[node[0]][node[1]] = CellState.PATH
    
    def finish_search(self, found):
        """Complete the search"""
        self.search_complete = True
        self.searching = False
        
        if found:
            msg = f"✓ PATH FOUND! | {self.selected_algorithm} | "
            msg += f"Steps: {self.step_count} | "
            
            if self.selected_algorithm == 'Bidirectional':
                explored = len(self.explored_forward) + len(self.explored_backward)
            else:
                explored = len(self.explored)
            
            msg += f"Explored: {explored} | Path: {len(self.final_path)}"
            
            if self.selected_algorithm == 'IDDFS':
                msg += f" | Depth: {self.current_depth_limit}"
            
            self.update_status(msg, Colors.SUCCESS)
        else:
            msg = f"❌ NO PATH | {self.selected_algorithm} | Steps: {self.step_count}"
            if self.selected_algorithm == 'DLS':
                msg += f" | Depth limit: {self.depth_limit}"
            elif self.selected_algorithm == 'IDDFS':
                msg += f" | Max depth reached: {self.current_depth_limit}"
            self.update_status(msg, Colors.ERROR)
    
    def get_cell_color(self, row, col):
        """Get cell color based on type and state"""
        cell_type = self.grid[row][col]
        cell_state = self.cell_states[row][col]
        
        if cell_type == CellType.START:
            return Colors.START
        elif cell_type == CellType.TARGET:
            return Colors.TARGET
        elif cell_state == CellState.PATH:
            return Colors.PATH
        elif cell_state == CellState.FRONTIER:
            return Colors.FRONTIER
        elif cell_state == CellState.FRONTIER2:
            return Colors.FRONTIER2
        elif cell_state == CellState.EXPLORED:
            return Colors.EXPLORED
        elif cell_state == CellState.EXPLORED2:
            return Colors.EXPLORED2
        elif cell_type == CellType.WALL:
            return Colors.WALL
        return Colors.EMPTY
    
    def draw_button(self, button):
        """Draw a button"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button['rect'].collidepoint(mouse_pos) and button['enabled']
        color = Colors.BUTTON_HOVER if is_hovered else button['color']
        
        pygame.draw.rect(self.screen, color, button['rect'], border_radius=4)
        pygame.draw.rect(self.screen, Colors.UI_BG, button['rect'], 2, border_radius=4)
        
        text_surface = self.button_font.render(button['text'], True, Colors.UI_TEXT)
        text_rect = text_surface.get_rect(center=button['rect'].center)
        self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(Colors.BG)
        
        # UI panel
        ui_rect = pygame.Rect(0, 0, self.window_width, self.ui_height)
        pygame.draw.rect(self.screen, Colors.UI_BG, ui_rect)
        
        # Draw buttons
        for button in self.all_buttons:
            self.draw_button(button)
        
        # Labels
        label1 = self.info_font.render("Select Algorithm (or press 1-6):", True, Colors.UI_TEXT)
        self.screen.blit(label1, (10, 0))
        
        label2 = self.info_font.render("Controls:", True, Colors.UI_TEXT)
        self.screen.blit(label2, (10, 38))
        
        label3 = self.info_font.render("Presets:", True, Colors.UI_TEXT)
        self.screen.blit(label3, (10, 76))
        
        speed_label = self.info_font.render("Speed:", True, Colors.UI_TEXT)
        self.screen.blit(speed_label, (self.window_width - 160, 0))
        
        depth_label = self.info_font.render(f"DLS={self.depth_limit}:", True, Colors.UI_TEXT)
        self.screen.blit(depth_label, (self.window_width - 160, 38))
        
        # Status
        status_surface = self.info_font.render(self.status_message, True, self.status_color)
        self.screen.blit(status_surface, (10, 125))
        
        # Stats
        if self.selected_algorithm == 'Bidirectional':
            explored = len(self.explored_forward) + len(self.explored_backward)
            frontier = len(self.frontier_forward) if self.frontier_forward else 0
            frontier += len(self.frontier_backward) if self.frontier_backward else 0
        else:
            explored = len(self.explored)
            frontier = len(self.frontier) if self.frontier else 0
        
        stats = f"Algorithm: {self.selected_algorithm} | Steps: {self.step_count} | "
        stats += f"Frontier: {frontier} | Explored: {explored} | Path: {len(self.final_path)}"
        
        if self.selected_algorithm == 'IDDFS':
            stats += f" | Current Depth: {self.current_depth_limit}"
        
        stats_surface = self.stats_font.render(stats, True, Colors.WARNING)
        self.screen.blit(stats_surface, (10, 145))
        
        # Instructions
        instructions = "S=Start | T=Target | SPACE=Run | C=Clear | R=Reset | Drag=Walls | ESC=Exit"
        inst_surface = self.stats_font.render(instructions, True, Colors.UI_TEXT)
        self.screen.blit(inst_surface, (10, 165))
        
        # Algorithm info
        algo_info = {
            'BFS': "BFS: Queue (FIFO) - Guarantees shortest path",
            'DFS': "DFS: Stack (LIFO) - Goes deep first",
            'UCS': "UCS: Priority Queue - Considers edge costs",
            'DLS': "DLS: Depth-Limited DFS - Stops at depth limit",
            'IDDFS': "IDDFS: Iterative Deepening - Increases depth gradually",
            'Bidirectional': "Bidirectional: Searches from both ends"
        }
        info_text = algo_info[self.selected_algorithm]
        info_surface = self.stats_font.render(info_text, True, Colors.UI_TEXT)
        self.screen.blit(info_surface, (10, 185))
        
        algo_delay = f"Delay: {self.animation_delay}ms"
        delay_surface = self.stats_font.render(algo_delay, True, Colors.UI_TEXT)
        self.screen.blit(delay_surface, (10, 203))
        
        # Grid
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size + self.ui_height
                color = self.get_cell_color(row, col)
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, cell_rect)
                pygame.draw.rect(self.screen, Colors.GRID_LINE, cell_rect, 1)
        
        # Labels
        label_font = pygame.font.Font(None, int(self.cell_size * 1.3))
        if self.start:
            s_text = label_font.render('S', True, (255, 255, 255))
            s_rect = s_text.get_rect(center=(
                self.start[1] * self.cell_size + self.cell_size // 2,
                self.start[0] * self.cell_size + self.cell_size // 2 + self.ui_height
            ))
            self.screen.blit(s_text, s_rect)
        
        if self.target:
            t_text = label_font.render('T', True, (255, 255, 255))
            t_rect = t_text.get_rect(center=(
                self.target[1] * self.cell_size + self.cell_size // 2,
                self.target[0] * self.cell_size + self.cell_size // 2 + self.ui_height
            ))
            self.screen.blit(t_text, t_rect)
        
        pygame.display.flip()
    
    def update(self):
        """Update game state"""
        if self.searching:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.animation_delay:
                self.algorithm_step()
                self.last_step_time = current_time
    
    def run(self):
        """Main game loop"""
        print("\n" + "="*70)
        print("🎮 AI PATHFINDER - ALL 6 ALGORITHMS")
        print("="*70)
        print("\nAlgorithms Available:")
        print("  1. BFS - Breadth-First Search")
        print("  2. DFS - Depth-First Search")
        print("  3. UCS - Uniform-Cost Search")
        print("  4. DLS - Depth-Limited Search")
        print("  5. IDDFS - Iterative Deepening DFS")
        print("  6. Bidirectional Search")
        print("\nPress 1-6 to select algorithm or click buttons!")
        print("="*70)
        print("\nGame window opened! Compare different search strategies!\n")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


def main():
    game = AllAlgorithmsPathfinder(rows=30, cols=50, cell_size=16)
    game.run()


if __name__ == "__main__":
    main()
