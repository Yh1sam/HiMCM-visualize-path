# room_generator.py - Generate room layout and walkability map with folder management
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import os
from datetime import datetime

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = random.choice(['Living Room', 'Bedroom', 'Kitchen', 'Bathroom', 'Study', 'Dining Room', 'Storage'])
        self.color = random.choice(['#FFE5B4', '#B4D7FF', '#FFB4D7', '#B4FFD7', 
                                   '#FFD7B4', '#D7B4FF', '#FFFFB4'])
        self.doors = []
        self.connected_to = set()
    
    def get_area(self):
        return self.width * self.height
    
    def is_adjacent(self, other):
        """Check if two rooms are adjacent"""
        epsilon = 0.01
        
        if abs(self.x + self.width - other.x) < epsilon or \
           abs(other.x + other.width - self.x) < epsilon:
            return not (self.y + self.height <= other.y or other.y + other.height <= self.y)
        
        if abs(self.y + self.height - other.y) < epsilon or \
           abs(other.y + other.height - self.y) < epsilon:
            return not (self.x + self.width <= other.x or other.x + other.width <= self.x)
        
        return False
    
    def create_door_to(self, other):
        """Create door between adjacent rooms"""
        door_width = 1
        door = None

        if abs(self.x + self.width - other.x) < 0.01:
            overlap_start = max(self.y, other.y)
            overlap_end = min(self.y + self.height, other.y + other.height)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': self.x + self.width - 0.2,
                'y': overlap_mid - door_width / 2,
                'width': 0.4,  # Increased door depth for wall penetration
                'height': door_width,
                'is_exit': False
            }
        elif abs(other.x + other.width - self.x) < 0.01:
            overlap_start = max(self.y, other.y)
            overlap_end = min(self.y + self.height, other.y + other.height)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': self.x - 0.2,
                'y': overlap_mid - door_width / 2,
                'width': 0.4,  # Increased door depth
                'height': door_width,
                'is_exit': False
            }
        elif abs(self.y + self.height - other.y) < 0.01:
            overlap_start = max(self.x, other.x)
            overlap_end = min(self.x + self.width, other.x + other.width)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': overlap_mid - door_width / 2,
                'y': self.y + self.height - 0.2,
                'width': door_width,
                'height': 0.4,  # Increased door depth
                'is_exit': False
            }
        elif abs(other.y + other.height - self.y) < 0.01:
            overlap_start = max(self.x, other.x)
            overlap_end = min(self.x + self.width, other.x + other.width)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': overlap_mid - door_width / 2,
                'y': self.y - 0.2,
                'width': door_width,
                'height': 0.4,  # Increased door depth
                'is_exit': False
            }

        if door:
            self.doors.append(door)
            self.connected_to.add(id(other))
    
    def create_exit(self, width_total, height_total):
        """Create external exit"""
        door_width = 1
        walls = []
        
        if self.x == 0:
            walls.append('left')
        if self.y == 0:
            walls.append('top')
        if abs(self.x + self.width - width_total) < 0.01:
            walls.append('right')
        if abs(self.y + self.height - height_total) < 0.01:
            walls.append('bottom')
        
        if not walls:
            return False
        
        wall = random.choice(walls)
        exit_door = None

        if wall == 'top':
            exit_door = {
                'x': self.x + (self.width - door_width) / 2,
                'y': self.y - 0.2,
                'width': door_width,
                'height': 0.4,  # Increased exit depth
                'is_exit': True
            }
        elif wall == 'right':
            exit_door = {
                'x': self.x + self.width - 0.2,
                'y': self.y + (self.height - door_width) / 2,
                'width': 0.4,  # Increased exit depth
                'height': door_width,
                'is_exit': True
            }
        elif wall == 'bottom':
            exit_door = {
                'x': self.x + (self.width - door_width) / 2,
                'y': self.y + self.height - 0.2,
                'width': door_width,
                'height': 0.4,  # Increased exit depth
                'is_exit': True
            }
        elif wall == 'left':
            exit_door = {
                'x': self.x - 0.2,
                'y': self.y + (self.height - door_width) / 2,
                'width': 0.4,  # Increased exit depth
                'height': door_width,
                'is_exit': True
            }

        if exit_door:
            self.doors.append(exit_door)
            return True
        return False

rooms = []

def split_space(x, y, width, height, depth, max_depth, min_size):
    """Recursively split space using Binary Space Partitioning algorithm"""
    if depth >= max_depth or width < min_size * 2 or height < min_size * 2:
        rooms.append(Room(x, y, width, height))
        return
    
    split_horizontal = random.random() > 0.5
    
    if split_horizontal and height >= min_size * 2:
        split_pos = min_size + random.random() * (height - min_size * 2)
        split_space(x, y, width, split_pos, depth + 1, max_depth, min_size)
        split_space(x, y + split_pos, width, height - split_pos, depth + 1, max_depth, min_size)
    elif not split_horizontal and width >= min_size * 2:
        split_pos = min_size + random.random() * (width - min_size * 2)
        split_space(x, y, split_pos, height, depth + 1, max_depth, min_size)
        split_space(x + split_pos, y, width - split_pos, height, depth + 1, max_depth, min_size)
    else:
        rooms.append(Room(x, y, width, height))

def ensure_connectivity():
    """Ensure all rooms are connected using minimum spanning tree concept"""
    if len(rooms) <= 1:
        return
    
    adjacency = {}
    for i, room in enumerate(rooms):
        adjacency[i] = []
        for j, other in enumerate(rooms):
            if i != j and room.is_adjacent(other):
                adjacency[i].append(j)
    
    connected = {0}
    edges_added = 0
    
    while len(connected) < len(rooms) and edges_added < len(rooms) * 2:
        found = False
        for i in connected:
            for j in adjacency[i]:
                if j not in connected:
                    rooms[i].create_door_to(rooms[j])
                    rooms[j].connected_to.add(id(rooms[i]))
                    connected.add(j)
                    edges_added += 1
                    found = True
                    break
            if found:
                break
        
        if not found:
            break

def create_walkability_map(width, height, resolution):
    """Create walkability map: 0=walkable, 1=wall"""
    width_px = int(width * resolution)
    height_px = int(height * resolution)
    
    # Initialize grid as all walls (1)
    grid = np.ones((width_px, height_px), dtype=np.uint8)
    
    wall_thickness = int(0.1 * resolution)
    
    # Draw walkable areas for each room (0)
    for room in rooms:
        x1 = int(room.x * resolution) + wall_thickness
        y1 = int(room.y * resolution) + wall_thickness
        x2 = int((room.x + room.width) * resolution) - wall_thickness
        y2 = int((room.y + room.height) * resolution) - wall_thickness
        
        grid[x1:x2, y1:y2] = 0
    
    # Draw doors (0 - walkable)
    for room in rooms:
        for door in room.doors:
            x1 = max(0, int(door['x'] * resolution))
            y1 = max(0, int(door['y'] * resolution))
            x2 = min(width_px, int((door['x'] + door['width']) * resolution))
            y2 = min(height_px, int((door['y'] + door['height']) * resolution))
            
            grid[x1:x2, y1:y2] = 0
    
    return grid

def save_exit_positions(width, height, resolution, output_dir):
    """Save all exit positions"""
    exits = []
    max_x = int(width * resolution) - 1  # Maximum valid x index
    max_y = int(height * resolution) - 1  # Maximum valid y index
    
    for room in rooms:
        for door in room.doors:
            if door.get('is_exit', False):
                center_x = int((door['x'] + door['width'] / 2) * resolution)
                center_y = int((door['y'] + door['height'] / 2) * resolution)
                
                # Clamp to valid grid boundaries
                center_x = max(0, min(center_x, max_x))
                center_y = max(0, min(center_y, max_y))
                
                exits.append([center_x, center_y])
    
    if exits:
        filepath = os.path.join(output_dir, 'exit_positions.npy')
        np.save(filepath, np.array(exits))
        print(f"Exit positions saved to {filepath}: {exits}")
    return exits

# ===== MAIN PROGRAM =====
if __name__ == "__main__":
    # Create layouts main directory
    layouts_dir = 'layouts'
    os.makedirs(layouts_dir, exist_ok=True)
    
    # Create timestamped subdirectory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(layouts_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating new layout directory: {output_dir}")
    print("="*60)
    
    # Parameter settings
    WIDTH = 20
    HEIGHT = 15
    MIN_SIZE = 3
    SPLITS = 4
    RESOLUTION = 50

    print("Generating room layout...")
    split_space(0, 0, WIDTH, HEIGHT, 0, SPLITS, MIN_SIZE)
    ensure_connectivity()

    # Create 1-2 external exits
    exit_count = 1 if random.random() < 0.5 else 2
    boundary_rooms = [r for r in rooms if 
                      r.x == 0 or r.y == 0 or 
                      abs(r.x + r.width - WIDTH) < 0.01 or 
                      abs(r.y + r.height - HEIGHT) < 0.01]

    random.shuffle(boundary_rooms)
    exits_created = 0
    for room in boundary_rooms:
        if exits_created >= exit_count:
            break
        if room.create_exit(WIDTH, HEIGHT):
            exits_created += 1

    print(f"Generated {len(rooms)} rooms with {exits_created} exits")

    # Generate and save walkability map
    print("Generating walkability map...")
    walkability_grid = create_walkability_map(WIDTH, HEIGHT, RESOLUTION)
    
    # Save as numpy array
    walkmap_path = os.path.join(output_dir, 'walkability_map.npy')
    np.save(walkmap_path, walkability_grid)
    print(f"Walkability map saved to {walkmap_path}")
    
    # Save exit positions
    exits = save_exit_positions(WIDTH, HEIGHT, RESOLUTION, output_dir)
    
    # Save configuration parameters
    config = {
        'width': WIDTH,
        'height': HEIGHT,
        'resolution': RESOLUTION,
        'num_rooms': len(rooms),
        'num_exits': exits_created,
        'door_depth': '0.4m (increased for wall penetration)',
        'timestamp': timestamp
    }
    config_path = os.path.join(output_dir, 'layout_config.npy')
    np.save(config_path, config)
    print(f"Configuration saved to {config_path}")

    # Visualize colored room layout
    print("Rendering layout diagram...")
    fig, ax = plt.subplots(figsize=(14, 10))

    for room in rooms:
        rect = patches.Rectangle((room.x, room.y), room.width, room.height,
                                 linewidth=2, edgecolor='black', facecolor=room.color, alpha=0.7)
        ax.add_patch(rect)
        
        for door in room.doors:
            if door.get('is_exit', False):
                door_rect = patches.Rectangle((door['x'], door['y']), door['width'], door['height'],
                                             linewidth=3, edgecolor='#2E7D32', facecolor='#4CAF50')
            else:
                door_rect = patches.Rectangle((door['x'], door['y']), door['width'], door['height'],
                                             linewidth=2, edgecolor='#666', facecolor='white')
            ax.add_patch(door_rect)
        
        center_x = room.x + room.width / 2
        center_y = room.y + room.height / 2
        ax.text(center_x, center_y, f'{room.type}\n{room.width:.1f}m × {room.height:.1f}m',
               ha='center', va='center', fontsize=9, weight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (m)', fontsize=12, weight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, weight='bold')
    ax.set_title(f'2D Indoor Space Layout - {timestamp}', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    layout_path = os.path.join(output_dir, 'room_layout.png')
    plt.savefig(layout_path, dpi=150, bbox_inches='tight')
    print(f"Layout diagram saved to {layout_path}")
    plt.show()
    
    # Create and save walkability map visualization (black/white + green exits)
    print("Generating walkability map visualization...")
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create RGB image
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
    
    # Mark exits as green
    for room in rooms:
        for door in room.doors:
            if door.get('is_exit', False):
                x1 = max(0, int(door['x'] * RESOLUTION))
                y1 = max(0, int(door['y'] * RESOLUTION))
                x2 = min(width_px, int((door['x'] + door['width']) * RESOLUTION))
                y2 = min(height_px, int((door['y'] + door['height']) * RESOLUTION))
                
                for i in range(x1, x2):
                    for j in range(y1, y2):
                        if i < width_px and j < height_px:
                            walkmap_visual[j][i] = [0, 255, 0]  # Green = exit
    
    ax.imshow(walkmap_visual, origin='lower', extent=[0, WIDTH, 0, HEIGHT])
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (m)', fontsize=12, weight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, weight='bold')
    ax.set_title(f'Walkability Map (White=Walkable, Black=Wall, Green=Exit) - {timestamp}', 
                fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    
    plt.tight_layout()
    walkmap_visual_path = os.path.join(output_dir, 'walkability_map.png')
    plt.savefig(walkmap_visual_path, dpi=150, bbox_inches='tight')
    print(f"Walkability map visualization saved to {walkmap_visual_path}")
    plt.show()

    # Create latest link (or text file)
    latest_file = os.path.join(layouts_dir, 'latest.txt')
    with open(latest_file, 'w') as f:
        f.write(timestamp)
    print(f"Latest layout record saved to {latest_file}")

    print(f"\n{'='*60}")
    print("Generation complete!")
    print(f"\nAll files saved to: {output_dir}")
    print(f"Files created:")
    print(f"  - room_layout.png (colored layout diagram)")
    print(f"  - walkability_map.png (black/white walkability map + green exits)")
    print(f"  - walkability_map.npy (grid data)")
    print(f"  - exit_positions.npy (exit coordinates)")
    print(f"  - layout_config.npy (configuration info)")
    print(f"{'='*60}")
    print(f"\nTo use this layout for pathfinding, copy files from")
    print(f"{output_dir}")
    print(f"to the main directory, or modify pathfinding.py to read from this directory!")
