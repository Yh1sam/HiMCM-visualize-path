# pathfinding.py - A* Pathfinding Algorithm (Each Person Heads to Nearest Exit)
import numpy as np
import matplotlib.pyplot as plt
import heapq
import math
import random

class Node:
    """A node class for A* pathfinding"""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __repr__(self):
        return f"{self.position} - g: {self.g:.2f} h: {self.h:.2f} f: {self.f:.2f}"

def generate_32_directions():
    """Generate 32 directions for pathfinding."""
    directions = []
    for i in range(32):
        angle = 2 * math.pi * i / 32
        dx = round(math.cos(angle))
        dy = round(math.sin(angle))
        # 避免(0,0)與重複方向
        if (dx, dy) != (0, 0) and (dx, dy) not in directions:
            directions.append((dx, dy))
    return directions

DIRECTIONS_32 = generate_32_directions()



def is_diagonal_move_valid(grid, current, neighbor):
    """Check if diagonal movement passes through a wall"""
    x1, y1 = current
    x2, y2 = neighbor
    
    # Diagonal move
    if abs(x2 - x1) == 1 and abs(y2 - y1) == 1:
        # Check both adjacent orthogonal moves are walkable
        if grid[x2][y1] != 0 or grid[x1][y2] != 0:
            return False
    return True

def a_star_search(grid, start, end):
    """Returns a path as a list of tuples from start to end on the given grid."""
    if grid[start[0]][start[1]] != 0:
        print(f"Warning: Start point {start} is not walkable")
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                nx, ny = start[0] + dx, start[1] + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
                    start = (nx, ny)
                    break
            else:
                continue
            break
    
    if grid[end[0]][end[1]] != 0:
        print(f"Warning: End point {end} is not walkable")
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                nx, ny = end[0] + dx, end[1] + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
                    end = (nx, ny)
                    break
            else:
                continue
            break
    
    start_node = Node(None, start)
    end_node = Node(None, end)

    open_list = []
    heapq.heappush(open_list, start_node)
    closed_list = set()
    g_costs = {start: 0}

    while open_list:
        current_node = heapq.heappop(open_list)

        if current_node.position in closed_list:
            continue
        closed_list.add(current_node.position)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        (x, y) = current_node.position

        for dx, dy in DIRECTIONS_32:
            nx, ny = x + dx, y + dy

            if nx < 0 or ny < 0 or nx >= len(grid) or ny >= len(grid[0]):
                continue
            if grid[nx][ny] != 0:
                continue
            if not is_diagonal_move_valid(grid, (x, y), (nx, ny)):
                continue

            move_cost = math.sqrt(dx*dx + dy*dy)
            new_g_cost = g_costs.get(current_node.position, float('inf')) + move_cost

            if (nx, ny) not in g_costs or new_g_cost < g_costs[(nx, ny)]:
                g_costs[(nx, ny)] = new_g_cost
                h_cost = math.dist((nx, ny), end_node.position)
                f_cost = new_g_cost + h_cost

                neighbor = Node(current_node, (nx, ny))
                neighbor.g = new_g_cost
                neighbor.h = h_cost
                neighbor.f = f_cost

                heapq.heappush(open_list, neighbor)

    return None

def find_nearest_exit(person_pos, exits):
    """Find the nearest exit from a given position"""
    min_dist = float('inf')
    nearest_exit = None
    for exit_pos in exits:
        dist = math.dist(person_pos, exit_pos)
        if dist < min_dist:
            min_dist = dist
            nearest_exit = exit_pos
    return tuple(nearest_exit) if nearest_exit is not None else None

def find_random_walkable_positions(grid, num_people):
    """Find multiple random walkable positions in the grid"""
    walkable_positions = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 0:
                walkable_positions.append((i, j))
    if len(walkable_positions) < num_people:
        print(f"Warning: Not enough walkable positions, only {len(walkable_positions)} people can be placed")
        return walkable_positions
    return random.sample(walkable_positions, num_people)

# ===== MAIN PROGRAM =====
if __name__ == "__main__":
    print("Loading walkability map and config...")
    try:
        walkability_grid = np.load('walkability_map.npy')
        config = np.load('layout_config.npy', allow_pickle=True).item()
        exits = np.load('exit_positions.npy')
    except FileNotFoundError:
        print("Error: Map files not found! Please run room_generator.py first.")
        exit()
    
    WIDTH = config['width']
    HEIGHT = config['height']
    RESOLUTION = config['resolution']
    NUM_PEOPLE = 8  # Number of people to spawn
    
    print(f"Map size: {WIDTH}m × {HEIGHT}m")
    print(f"Grid size: {walkability_grid.shape}")
    print(f"Resolution: {RESOLUTION} px/meter")
    print(f"Number of exits: {len(exits)}")
    print(f"Exit positions: {exits}")
    
    print(f"\nGenerating {NUM_PEOPLE} random people positions...")
    people_positions = find_random_walkable_positions(walkability_grid, NUM_PEOPLE)
    
    # Find paths—each person heads to their nearest exit
    paths = []
    target_exits = []
    
    print("\nPathfinding (each person chooses their nearest exit)...")
    for i, start_pos in enumerate(people_positions):
        nearest_exit = find_nearest_exit(start_pos, exits)
        target_exits.append(nearest_exit)
        
        print(f"Person {i+1}/{NUM_PEOPLE}: start {start_pos} → target exit {nearest_exit}")
        
        path = a_star_search(walkability_grid, start_pos, nearest_exit)
        if path:
            paths.append(path)
            print(f"  ✓ Path found, length: {len(path)} steps")
        else:
            paths.append(None)
            print(f"  ✗ No path found")
    
    # Exit usage stats
    exit_usage = {}
    for exit_pos in exits:
        exit_key = tuple(exit_pos)
        exit_usage[exit_key] = target_exits.count(exit_key)
    
    print("\nExit usage statistics:")
    for i, exit_pos in enumerate(exits):
        exit_key = tuple(exit_pos)
        print(f"  Exit {i+1} {exit_pos}: {exit_usage[exit_key]} people")
    
    # Visualization
    print("\nRendering paths ...")
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Create visualization in (height, width, 3) format
    height_px = walkability_grid.shape[1]
    width_px = walkability_grid.shape[0]
    walkmap_visual = np.zeros((height_px, width_px, 3), dtype=np.uint8)
    
    # Fill colors (be careful with axis mapping)
    for i in range(width_px):
        for j in range(height_px):
            if walkability_grid[i][j] == 0:
                walkmap_visual[j][i] = [255, 255, 255]  # White = walkable
            else:
                walkmap_visual[j][i] = [0, 0, 0]        # Black = wall

    ax.imshow(walkmap_visual, origin='lower', extent=[0, WIDTH, 0, HEIGHT])
    
    # Draw people and paths
    colors = ['#FF4444', '#4444FF', '#FF44FF', '#44FF44', '#FFAA44', '#44AAFF', '#AA44FF', '#AAFF44']
    for i, (person_pos, path) in enumerate(zip(people_positions, paths)):
        color = colors[i % len(colors)]
        ax.scatter(person_pos[0] / RESOLUTION, person_pos[1] / RESOLUTION, 
                   marker='o', color='blue', s=200, zorder=10, edgecolors='white', linewidths=2)
        if path:
            path_x = [p[0] / RESOLUTION for p in path]
            path_y = [p[1] / RESOLUTION for p in path]
            ax.plot(path_x, path_y, color=color, linewidth=2.5, alpha=0.9, zorder=5)

    # Draw all exits (different markers if needed)
    exit_markers = ['*', 'P']
    for i, exit_p in enumerate(exits):
        marker = exit_markers[i % len(exit_markers)]
        ax.scatter(exit_p[0] / RESOLUTION, exit_p[1] / RESOLUTION,
                   marker=marker, color='green', s=600, zorder=15, 
                   edgecolors='darkgreen', linewidths=3,
                   label=f'Exit {i+1} ({exit_usage[tuple(exit_p)]} people)')

    ax.scatter([], [], marker='o', color='blue', s=100, label='Person', edgecolors='white', linewidths=2)
    
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (m)', fontsize=12, weight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, weight='bold')
    ax.set_title(f'A* Pathfinding - {NUM_PEOPLE} Persons Evacuation Paths (8 directions, smart exit choice)', fontsize=16, weight='bold')
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    
    plt.tight_layout()
    plt.savefig('pathfinding_result.png', dpi=150, bbox_inches='tight')
    print("\nResult plot saved as pathfinding_result.png")
    plt.show()
    
    successful_paths = sum(1 for p in paths if p is not None)
    print(f"\n{'='*60}")
    print(f"Pathfinding complete!")
    print(f"Paths found: {successful_paths}/{NUM_PEOPLE}")
    if successful_paths < NUM_PEOPLE:
        print(f"Failed: {NUM_PEOPLE - successful_paths} people")
    print(f"{'='*60}")
