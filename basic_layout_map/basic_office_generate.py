# office_layout_generator.py - Fixed door depth and folder organization
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os
from datetime import datetime

class Room:
    def __init__(self, x, y, width, height, room_type='office'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = room_type
        self.color = '#E8F4F8' if room_type == 'office' else '#D3D3D3'
        self.doors = []
    
    def add_door(self, door):
        """Add a door to this room"""
        self.doors.append(door)

def create_office_layout():
    """Create office layout matching the reference image"""
    rooms = []
    doors = []
    exits = []
    
    # Floor dimensions (in meters)
    FLOOR_WIDTH = 30
    FLOOR_HEIGHT = 20
    
    # Hallway configuration
    HALLWAY_HEIGHT = 5
    HALLWAY_Y = 7.5  # Positioned vertically centered
    
    # Office configuration
    OFFICE_HEIGHT_TOP = 7.5
    OFFICE_HEIGHT_BOTTOM = 7.5
    NUM_OFFICES_PER_ROW = 3
    OFFICE_WIDTH = FLOOR_WIDTH / NUM_OFFICES_PER_ROW  # Each office: 10m wide
    
    # === Create Top Row Offices (3 offices, directly connected) ===
    for i in range(NUM_OFFICES_PER_ROW):
        x = i * OFFICE_WIDTH
        y = HALLWAY_Y - OFFICE_HEIGHT_TOP
        
        room = Room(x, y, OFFICE_WIDTH, OFFICE_HEIGHT_TOP, 'office')
        rooms.append(room)
        
        # Add door connecting to hallway (bottom of office)
        # INCREASED DEPTH: door height now 0.4m to fully penetrate wall
        door_x = x + OFFICE_WIDTH / 2 - 0.5
        door_y = y + OFFICE_HEIGHT_TOP - 0.2  # Start deeper into wall
        doors.append({
            'x': door_x,
            'y': door_y,
            'width': 1,
            'height': 0.4,  # INCREASED from 0.2 to 0.4
            'is_exit': False
        })
    
    # === Create Hallway (full width) ===
    hallway = Room(0, HALLWAY_Y, FLOOR_WIDTH, HALLWAY_HEIGHT, 'hallway')
    rooms.append(hallway)
    
    # === Create Bottom Row Offices (3 offices, directly connected) ===
    for i in range(NUM_OFFICES_PER_ROW):
        x = i * OFFICE_WIDTH
        y = HALLWAY_Y + HALLWAY_HEIGHT
        
        room = Room(x, y, OFFICE_WIDTH, OFFICE_HEIGHT_BOTTOM, 'office')
        rooms.append(room)
        
        # Add door connecting to hallway (top of office)
        # INCREASED DEPTH
        door_x = x + OFFICE_WIDTH / 2 - 0.5
        door_y = y - 0.2  # Start deeper into wall
        doors.append({
            'x': door_x,
            'y': door_y,
            'width': 1,
            'height': 0.4,  # INCREASED from 0.2 to 0.4
            'is_exit': False
        })
    
    # === Create Two Exits (left and right of hallway) ===
    # INCREASED EXIT WIDTH for better visibility
    exit_y = HALLWAY_Y + HALLWAY_HEIGHT / 2
    
    # Left Exit - EXTENDED to fully penetrate wall
    exits.append({
        'x': -0.2,  # Start outside the wall
        'y': exit_y - 0.5,
        'width': 0.4,  # INCREASED from 0.3 to 0.4
        'height': 1,
        'is_exit': True
    })
    
    # Right Exit - EXTENDED to fully penetrate wall
    exits.append({
        'x': FLOOR_WIDTH - 0.2,  # Extend outside
        'y': exit_y - 0.5,
        'width': 0.4,  # INCREASED from 0.3 to 0.4
        'height': 1,
        'is_exit': True
    })
    
    return rooms, doors, exits, FLOOR_WIDTH, FLOOR_HEIGHT

def create_walkability_map(rooms, doors, exits, width, height, resolution=50):
    """Create walkability map: 0=walkable, 1=wall"""
    width_px = int(width * resolution)
    height_px = int(height * resolution)
    
    # Initialize as all walls
    grid = np.ones((width_px, height_px), dtype=np.uint8)
    
    wall_thickness = int(0.15 * resolution)
    
    # Draw walkable areas for each room
    for room in rooms:
        x1 = int(room.x * resolution) + wall_thickness
        y1 = int(room.y * resolution) + wall_thickness
        x2 = int((room.x + room.width) * resolution) - wall_thickness
        y2 = int((room.y + room.height) * resolution) - wall_thickness
        
        # Ensure boundaries don't exceed grid
        x1 = max(0, min(x1, width_px - 1))
        y1 = max(0, min(y1, height_px - 1))
        x2 = max(0, min(x2, width_px))
        y2 = max(0, min(y2, height_px))
        
        grid[x1:x2, y1:y2] = 0
    
    # Draw doors (walkable) with FULL PENETRATION
    for door in doors:
        x1 = max(0, int(door['x'] * resolution))
        y1 = max(0, int(door['y'] * resolution))
        x2 = min(width_px, int((door['x'] + door['width']) * resolution))
        y2 = min(height_px, int((door['y'] + door['height']) * resolution))
        
        grid[x1:x2, y1:y2] = 0
    
    # Draw exits (walkable) with FULL PENETRATION
    for exit_door in exits:
        x1 = max(0, int(exit_door['x'] * resolution))
        y1 = max(0, int(exit_door['y'] * resolution))
        x2 = min(width_px, int((exit_door['x'] + exit_door['width']) * resolution))
        y2 = min(height_px, int((exit_door['y'] + exit_door['height']) * resolution))
        
        grid[x1:x2, y1:y2] = 0
    
    return grid

def visualize_layout(rooms, doors, exits, width, height, output_dir):
    """Visualize the office layout"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Draw rooms
    for room in rooms:
        color = '#D3D3D3' if room.type == 'hallway' else '#E8F4F8'
        rect = patches.Rectangle((room.x, room.y), room.width, room.height,
                                 linewidth=2, edgecolor='black', facecolor=color, alpha=0.7)
        ax.add_patch(rect)
        
        # Add label
        center_x = room.x + room.width / 2
        center_y = room.y + room.height / 2
        label = 'HALLWAY' if room.type == 'hallway' else 'OFFICE'
        ax.text(center_x, center_y, label,
               ha='center', va='center', fontsize=14, weight='bold')
    
    # Draw doors (white rectangles with border) - NOW DEEPER
    for door in doors:
        rect = patches.Rectangle((door['x'], door['y']), door['width'], door['height'],
                                 linewidth=2, edgecolor='#666', facecolor='white')
        ax.add_patch(rect)
    
    # Draw exits (green) - NOW WIDER
    for exit_d in exits:
        rect = patches.Rectangle((exit_d['x'], exit_d['y']), exit_d['width'], exit_d['height'],
                                 linewidth=3, edgecolor='darkgreen', facecolor='green')
        ax.add_patch(rect)
        
        # Add EXIT label
        label_x = exit_d['x'] + exit_d['width'] / 2
        label_y = exit_d['y'] + exit_d['height'] / 2
        offset_x = -2 if exit_d['x'] < 1 else 2
        
        ax.text(label_x + offset_x, label_y, 'EXIT',
               ha='right' if exit_d['x'] < 1 else 'left', va='center', 
               fontsize=12, weight='bold', color='green')
    
    ax.set_xlim(-2, width + 2)
    ax.set_ylim(-2, height + 2)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (m)', fontsize=12, weight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, weight='bold')
    ax.set_title('Office Building Layout (Doors with Full Wall Penetration)', fontsize=16, weight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'office_layout.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Office layout saved to {output_path}")
    plt.show()

def save_exit_positions(exits, resolution, output_dir):
    """Save exit positions for pathfinding - CENTER of each exit"""
    exit_positions = []
    for exit_d in exits:
        # Calculate center of exit in pixel coordinates
        center_x = int((exit_d['x'] + exit_d['width'] / 2) * resolution)
        center_y = int((exit_d['y'] + exit_d['height'] / 2) * resolution)
        exit_positions.append([center_x, center_y])
    
    output_path = os.path.join(output_dir, 'exit_positions.npy')
    np.save(output_path, np.array(exit_positions))
    print(f"Exit positions saved to {output_path}: {exit_positions}")
    return exit_positions

# ===== MAIN PROGRAM =====
if __name__ == "__main__":
    # Create output directory
    output_dir = 'basic_office_layouts'
    os.makedirs(output_dir, exist_ok=True)
    
    # Add timestamp subdirectory for version control
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_dir = os.path.join(output_dir, timestamp)
    os.makedirs(session_dir, exist_ok=True)
    
    print(f"Creating office layout in: {session_dir}")
    print("="*60)
    
    rooms, doors, exits, WIDTH, HEIGHT = create_office_layout()
    
    RESOLUTION = 50
    
    office_count = len([r for r in rooms if r.type == 'office'])
    print(f"Generated {office_count} offices + 1 hallway")
    print(f"Floor dimensions: {WIDTH}m × {HEIGHT}m")
    print(f"Number of exits: {len(exits)}")
    print(f"Door dimensions: 1m × 0.4m (INCREASED for full wall penetration)")
    print(f"Exit dimensions: 0.4m × 1m (INCREASED for better visibility)")
    
    # Generate walkability map
    print("\nGenerating walkability map...")
    walkability_grid = create_walkability_map(rooms, doors, exits, WIDTH, HEIGHT, RESOLUTION)
    
    # Save walkability map
    walkmap_path = os.path.join(session_dir, 'walkability_map.npy')
    np.save(walkmap_path, walkability_grid)
    print(f"Walkability map saved to {walkmap_path}")
    print(f"Grid shape: {walkability_grid.shape}")
    
    # Save exit positions
    save_exit_positions(exits, RESOLUTION, session_dir)
    
    # Save configuration
    config = {
        'width': WIDTH,
        'height': HEIGHT,
        'resolution': RESOLUTION,
        'num_rooms': office_count,
        'num_exits': len(exits),
        'door_size': '1m × 0.4m',
        'exit_size': '0.4m × 1m'
    }
    config_path = os.path.join(session_dir, 'layout_config.npy')
    np.save(config_path, config)
    print(f"Configuration saved to {config_path}")
    
    # Visualize layout
    print("\nVisualizing layout...")
    visualize_layout(rooms, doors, exits, WIDTH, HEIGHT, session_dir)
    
    # Create and save walkability visualization WITH EXITS
    print("\nCreating walkability map visualization...")
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create RGB visualization
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
    
    # Overlay exits in GREEN on walkability map
    for exit_d in exits:
        x1 = max(0, int(exit_d['x'] * RESOLUTION))
        y1 = max(0, int(exit_d['y'] * RESOLUTION))
        x2 = min(width_px, int((exit_d['x'] + exit_d['width']) * RESOLUTION))
        y2 = min(height_px, int((exit_d['y'] + exit_d['height']) * RESOLUTION))
        
        for i in range(x1, x2):
            for j in range(y1, y2):
                if j < height_px and i < width_px:
                    walkmap_visual[j][i] = [0, 255, 0]  # Green = exit
    
    ax.imshow(walkmap_visual, origin='lower', extent=[0, WIDTH, 0, HEIGHT])
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (m)', fontsize=12, weight='bold')
    ax.set_ylabel('Height (m)', fontsize=12, weight='bold')
    ax.set_title('Walkability Map (White=Walkable, Black=Wall, Green=Exit)', fontsize=16, weight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', color='gray')
    
    plt.tight_layout()
    walkmap_visual_path = os.path.join(session_dir, 'walkability_map.png')
    plt.savefig(walkmap_visual_path, dpi=150, bbox_inches='tight')
    print(f"Walkability map visualization saved to {walkmap_visual_path}")
    plt.show()
    
    # Create a symlink to latest for easy access
    latest_link = os.path.join(output_dir, 'latest')
    if os.path.exists(latest_link):
        os.remove(latest_link)
    try:
        os.symlink(timestamp, latest_link, target_is_directory=True)
    except OSError:
        # On Windows, just copy the path to a text file
        with open(os.path.join(output_dir, 'latest.txt'), 'w') as f:
            f.write(timestamp)
    
    print(f"\n{'='*60}")
    print("Generation complete!")
    print(f"Layout configuration:")
    print(f"  - 3 offices (top row, each 10m × 7.5m)")
    print(f"  - 1 hallway (center, 30m × 5m)")
    print(f"  - 3 offices (bottom row, each 10m × 7.5m)")
    print(f"  - 6 doors (1m × 0.4m each, FULL wall penetration)")
    print(f"  - 2 exits (0.4m × 1m each, left & right)")
    print(f"\nAll files saved to: {session_dir}")
    print(f"Files created:")
    print(f"  - office_layout.png")
    print(f"  - walkability_map.png")
    print(f"  - walkability_map.npy")
    print(f"  - exit_positions.npy")
    print(f"  - layout_config.npy")
    print(f"{'='*60}")
    print(f"\nTo use with pathfinding, copy these files from {session_dir}")
    print("Or update pathfinding.py to read from this directory!")
