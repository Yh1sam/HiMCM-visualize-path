# pathfinding.py - Modular A* Pathfinding Algorithm
import numpy as np
import matplotlib.pyplot as plt
import heapq
import math
import random
import os


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
        # Avoid (0,0) and duplicate directions
        if (dx, dy) != (0, 0) and (dx, dy) not in directions:
            directions.append((dx, dy))
    return directions


DIRECTIONS_32 = generate_32_directions()

def path_distance_meters(path, resolution):
    """Sum of segment distances (in meters) along a pixel path."""
    if not path or len(path) < 2:
        return 0.0
    dist_px = 0.0
    for i in range(1, len(path)):
        a = path[i - 1]
        b = path[i]
        dist_px += math.dist(a, b)
    return dist_px / resolution  # px -> meters

def scaled_step_count(path, resolution, step_unit_m=0.7):
    """Scaled steps: how many 'step_unit_m' units the path covers."""
    dist_m = path_distance_meters(path, resolution)
    return int(round(dist_m / step_unit_m))



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
    # Clamp start and end positions to valid grid boundaries
    start = (
        max(0, min(start[0], len(grid) - 1)),
        max(0, min(start[1], len(grid[0]) - 1))
    )
    end = (
        max(0, min(end[0], len(grid) - 1)),
        max(0, min(end[1], len(grid[0]) - 1))
    )
    
    if grid[start[0]][start[1]] != 0:
        print(f"Warning: Start point {start} is not walkable, adjusting...")
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
        print(f"Warning: End point {end} is not walkable, adjusting...")
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
        # Ensure exit_pos is a tuple of standard Python integers
        exit_tuple = (int(exit_pos[0]), int(exit_pos[1]))
        dist = math.dist(person_pos, exit_tuple)
        if dist < min_dist:
            min_dist = dist
            nearest_exit = exit_tuple
    return nearest_exit


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


def load_map_data(layout_dir):
    """Load map data from the specified directory"""
    walkmap_path = os.path.join(layout_dir, 'walkability_map.npy')
    config_path = os.path.join(layout_dir, 'layout_config.npy')
    exits_path = os.path.join(layout_dir, 'exit_positions.npy')
    
    if not os.path.exists(walkmap_path):
        raise FileNotFoundError(f"Walkability map not found: {walkmap_path}")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if not os.path.exists(exits_path):
        raise FileNotFoundError(f"Exit positions not found: {exits_path}")
    
    walkability_grid = np.load(walkmap_path)
    config = np.load(config_path, allow_pickle=True).item()
    exits = np.load(exits_path)
    
    return walkability_grid, config, exits


def save_pathfinding_report(layout_dir, results):
    """Save pathfinding results to a text report"""
    report_path = os.path.join(layout_dir, 'pathfinding_report.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("A* PATHFINDING SIMULATION REPORT\n")
        f.write("="*70 + "\n\n")
        
        # Layout configuration
        f.write("LAYOUT CONFIGURATION:\n")
        f.write("-"*70 + "\n")
        config = results['config']
        f.write(f"Map Size: {config['width']}m x {config['height']}m\n")
        f.write(f"Resolution: {config['resolution']} px/meter\n")
        f.write(f"Walking Speed: {results.get('speed_mps', 1.2)} m/s\n")
        f.write(f"Number of Rooms: {config['num_rooms']}\n")
        f.write(f"Number of Exits: {config['num_exits']}\n\n")
        
        # Pathfinding results
        f.write("PATHFINDING RESULTS:\n")
        f.write("-"*70 + "\n")
        f.write(f"Total People: {results['num_people']}\n")
        f.write(f"Successful Paths: {sum(1 for p in results['paths'] if p is not None)}\n")
        f.write(f"Failed Paths: {sum(1 for p in results['paths'] if p is None)}\n")
        f.write(f"Success Rate: {results['success_rate']:.1f}%\n\n")
        if 'total_evac_time_s' in results:
            f.write(f"Total Evacuation Time (max): {results['total_evac_time_s']:.2f} s\n\n")
        else:
            f.write("\n")
        
        # Exit usage statistics
        f.write("EXIT USAGE STATISTICS:\n")
        f.write("-"*70 + "\n")
        for exit_pos, count in results['exit_usage'].items():
            f.write(f"Exit at {exit_pos}: {count} people\n")
        f.write("\n")
        
        # Detailed path information
        f.write("DETAILED PATH INFORMATION:\n")
        f.write("-"*70 + "\n")
        for i, (start_pos, target_exit, path) in enumerate(zip(
            results['people_positions'], 
            results['target_exits'], 
            results['paths']
        )):
            f.write(f"\nPerson {i+1}:\n")
            f.write(f"  Start Position: {start_pos}\n")
            f.write(f"  Target Exit: {target_exit}\n")
            if path:
                f.write(f"  Path Length: {len(path)} steps\n")
                dist_m = results.get('distances_m', [None]*len(results['paths']))[i]
                time_s = results.get('times_s', [None]*len(results['paths']))[i]
                human_steps = results.get('scaled_steps', [None]*len(results['paths']))[i]
                if dist_m is not None:
                    f.write(f"  Path Length (m): ~{dist_m:.2f} m\n")
                if human_steps is not None:
                    f.write(f"  Human Steps (~0.7 m): {human_steps}\n")
                if time_s is not None:
                    f.write(f"  Est. Time: {time_s:.2f} s @ {results.get('speed_mps', 1.2):.2f} m/s\n")
                f.write(f"  Path Status: OK SUCCESS\n")
            else:
                f.write(f"  Path Status: X FAILED\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"Report saved to {report_path}")
    return report_path


def run_pathfinding(layout_dir, num_people=8, save_output=True, show_plot=False, speed_mps=1.2, step_unit_m=0.7):
    """
    Run A* pathfinding simulation on a given layout
    
    Parameters:
    -----------
    layout_dir : str
        Path to directory containing map data
    num_people : int, optional
        Number of people to simulate (default: 8)
    save_output : bool, optional
        Whether to save result plot and report (default: True)
    show_plot : bool, optional
        Whether to display plot (default: True)
    
    Returns:
    --------
    dict : Dictionary containing simulation results
    """
    
    print(f"Loading map data from: {layout_dir}")
    print("="*60)
    
    try:
        walkability_grid, config, exits = load_map_data(layout_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    
    WIDTH = config['width']
    HEIGHT = config['height']
    RESOLUTION = config['resolution']
    
    print(f"Map size: {WIDTH}m x {HEIGHT}m")
    print(f"Grid size: {walkability_grid.shape}")
    print(f"Resolution: {RESOLUTION} px/meter")
    print(f"Number of exits: {len(exits)}")
    print(f"Exit positions: {exits}")
    
    print(f"\nGenerating {num_people} random people positions...")
    people_positions = find_random_walkable_positions(walkability_grid, num_people)
    
    # Find paths?ach person heads to their nearest exit
    paths = []
    target_exits = []
    distances_m = []
    times_s = []
    scaled_steps_list = []
    
    print("\nPathfinding (each person chooses their nearest exit)...")
    for i, start_pos in enumerate(people_positions):
        nearest_exit = find_nearest_exit(start_pos, exits)
        target_exits.append(nearest_exit)
        
        print(f"Person {i+1}/{num_people}: start {start_pos} -> target exit {nearest_exit}")
        
        path = a_star_search(walkability_grid, start_pos, nearest_exit)
        if path:
            paths.append(path)
            dist_m = path_distance_meters(path, RESOLUTION)
            human_steps = scaled_step_count(path, RESOLUTION, step_unit_m)
            time_s = dist_m / speed_mps if speed_mps > 0 else float('inf')
            distances_m.append(dist_m)
            times_s.append(time_s)
            scaled_steps_list.append(human_steps)
            print(f"  Path found: ~{dist_m:.1f} m, ~{human_steps} human-steps (0.7 m), est time: {time_s:.1f} s")
        else:
            paths.append(None)
            distances_m.append(None)
            times_s.append(None)
            scaled_steps_list.append(None)
            print(f"  X No path found")
    
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
    print("\nRendering paths...")
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Create visualization in (height, width, 3) format
    height_px = walkability_grid.shape[1]
    width_px = walkability_grid.shape[0]
    walkmap_visual = np.zeros((height_px, width_px, 3), dtype=np.uint8)
    
    # Fill colors
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

    # Draw all exits
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
    ax.set_title(f'A* Pathfinding - {num_people} Persons Evacuation Paths (32 directions)', 
                fontsize=16, weight='bold')
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    
    plt.tight_layout()
    
    if save_output:
        output_path = os.path.join(layout_dir, 'pathfinding_result.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\nResult plot saved to {output_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    # Calculate success rate
    successful_paths = sum(1 for p in paths if p is not None)
    success_rate = (successful_paths / num_people) * 100 if num_people > 0 else 0
    valid_times = [t for t in times_s if t is not None]
    total_evac_time_s = max(valid_times) if valid_times else 0.0
    
    if len(valid_times) > 0:
        print("\nEvacuation time summary:")

        print(f"  Avg time: {sum(valid_times)/len(valid_times):.1f} s")
        print(f"  Max (total) time: {total_evac_time_s:.1f} s")
    print(f"\n{'='*60}")
    print(f"Pathfinding complete!")
    print(f"Paths found: {successful_paths}/{num_people} ({success_rate:.1f}%)")
    if successful_paths < num_people:
        print(f"Failed: {num_people - successful_paths} people")
    print(f"{'='*60}")
    
    # Return results
    results = {
        'paths': paths,
        'people_positions': people_positions,
        'target_exits': target_exits,
        'exit_usage': exit_usage,
        'success_rate': success_rate,
        'num_people': num_people,
        'config': config,
        'speed_mps': speed_mps,
        'distances_m': distances_m,
        'times_s': times_s,
        'scaled_steps': scaled_steps_list,
        'total_evac_time_s': total_evac_time_s
    }
    
    # Save report if requested
    if save_output:
        save_pathfinding_report(layout_dir, results)
    
    return results

# ===== MAIN PROGRAM (for standalone execution) =====
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run A* pathfinding simulation on a layout')
    parser.add_argument('layout_dir', nargs='?', default='layouts/latest', 
                       help='Path to layout directory (default: layouts/latest)')
    parser.add_argument('-n', '--num-people', type=int, default=8,
                       help='Number of people to simulate (default: 8)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save output plot')
    parser.add_argument('--no-show', action='store_true',
                       help='Do not display plot window')
    
    args = parser.parse_args()
    
    # Check if 'latest' directory exists, if not try reading latest.txt
    layout_dir = args.layout_dir
    if layout_dir == 'layouts/latest':
        latest_file = 'layouts/latest.txt'
        if os.path.exists(latest_file):
            with open(latest_file, 'r') as f:
                timestamp = f.read().strip()
            layout_dir = os.path.join('layouts', timestamp)
            print(f"Using latest layout: {layout_dir}")
    
    # Run pathfinding
    results = run_pathfinding(
        layout_dir=layout_dir,
        num_people=args.num_people,
        save_output=not args.no_save,
        show_plot=not args.no_show
    )
    
    if results:
        print("\nSimulation completed successfully!")

