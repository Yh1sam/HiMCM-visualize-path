import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import heapq
import math
import time


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
    """Generates 32 evenly spaced direction offsets around a circle."""
    directions = []
    for i in range(32):
        angle = 2 * math.pi * i / 32
        dx = round(math.cos(angle))
        dy = round(math.sin(angle))
        if (dx, dy) != (0, 0) and (dx, dy) not in directions:
            directions.append((dx, dy))
    return directions


DIRECTIONS_32 = generate_32_directions()


def a_star_search(grid, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given grid."""

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


def create_grid_from_layout(layout, resolution=20):
    """Creates a grid representation of the layout for pathfinding."""
    width = int(layout['floor_dimensions'][0] * resolution)
    height = int(layout['floor_dimensions'][1] * resolution)
    grid = [[1 for _ in range(height)] for _ in range(width)]

    for room in layout['rooms']:
        if room['type'] == 'corridor':
            x, y = room['position']
            w, h = room['size']
            x, y, w, h = int(x*resolution), int(y*resolution), int(w*resolution), int(h*resolution)
            for i in range(w):
                for j in range(h):
                    if 0 <= x+i < width and 0 <= y+j < height:
                        grid[x+i][y+j] = 0

    for room in layout['rooms']:
        if room['type'] == 'office':
            x, y = room['position']
            w, h = room['size']
            x, y, w, h = int(x*resolution)+1, int(y*resolution)+1, int(w*resolution)-2, int(h*resolution)-2
            for i in range(w):
                for j in range(h):
                    if 0 <= x+i < width and 0 <= y+j < height:
                        grid[x+i][y+j] = 0

    if 'doors' in layout:
        for door in layout['doors']:
            x, y = door['position']
            w, h = door['size']
            x, y, w, h = int(x*resolution), int(y*resolution), int(w*resolution), int(h*resolution)
            for i in range(w):
                for j in range(h):
                    if 0 <= x+i < width and 0 <= y+j < height:
                        grid[x+i][y+j] = 0

    return grid


def visualize_paths(data_file='simple_office.json', resolution=5):
    """Visualizes the office layout with people and their shortest paths to an exit."""
    print("Starting visualization process...")
    start_time = time.time()

    with open(data_file, 'r') as f:
        layout = json.load(f)
    print(f"Loaded layout data in {time.time() - start_time:.2f} seconds.")

    print(f"Creating grid with resolution: {resolution}...")
    grid_start_time = time.time()
    grid = create_grid_from_layout(layout, resolution)
    print(f"Grid created in {time.time() - grid_start_time:.2f} seconds.")

    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_title(f"{layout['name']} - Evacuation Paths (32-direction A*)")
    ax.set_xlabel("X-coordinate (m)")
    ax.set_ylabel("Y-coordinate (m)")
    floor_width, floor_height = layout['floor_dimensions']
    ax.set_xlim(-2, floor_width + 2)
    ax.set_ylim(-2, floor_height + 2)
    ax.set_aspect('equal', adjustable='box')

    room_colors = {'office': 'lightblue', 'corridor': 'lightgrey'}

    for room in layout['rooms']:
        x, y = room['position']
        w, h = room['size']
        color = room_colors.get(room['type'], 'lightcyan')
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, room['name'], ha='center', va='center', fontsize=9, wrap=True)

    for exit_obj in layout['exits']:
        x, y = exit_obj['position']
        w = exit_obj['width']
        rect = patches.Rectangle((x, y), w, w, linewidth=2, edgecolor='green', facecolor='green')
        ax.add_patch(rect)

    if 'doors' in layout:
        for door in layout['doors']:
            x, y = door['position']
            w, h = door['size']
            rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='saddlebrown', facecolor='saddlebrown')
            ax.add_patch(rect)

    if 'people' in layout:
        for i, person in enumerate(layout['people']):
            print(f"Processing person {i+1}/{len(layout['people'])}...")
            path_start_time = time.time()

            start_pos = person['position']
            start_grid_pos = (int(start_pos[0] * resolution), int(start_pos[1] * resolution))
            ax.scatter(start_pos[0], start_pos[1], marker='o', color='red', s=100, zorder=10)

            nearest_exit = min(layout['exits'], key=lambda e: math.dist(start_pos, e['position']))
            exit_pos = nearest_exit['position']
            end_grid_pos = (int(exit_pos[0] * resolution), int(exit_pos[1] * resolution))

            path = a_star_search(grid, start_grid_pos, end_grid_pos)
            print(f"  Pathfinding complete in {time.time() - path_start_time:.2f} seconds.")

            if path:
                path_x = [p[0] / resolution for p in path]
                path_y = [p[1] / resolution for p in path]
                ax.plot(path_x, path_y, marker='.', color='red', zorder=5)
                print(f"  Path found with length {len(path)}")
            else:
                print("  No path found.")

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig('office_with_paths_32dir.png', bbox_inches='tight')
    plt.close(fig)
    print(f"Visualization saved. Total time: {time.time() - start_time:.2f} seconds.")


if __name__ == "__main__":
    visualize_paths()