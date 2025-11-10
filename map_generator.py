# room_generator.py - 生成房間布局和通行圖
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = random.choice(['客廳', '臥室', '廚房', '浴室', '書房', '餐廳', '儲藏室'])
        self.color = random.choice(['#FFE5B4', '#B4D7FF', '#FFB4D7', '#B4FFD7', 
                                   '#FFD7B4', '#D7B4FF', '#FFFFB4'])
        self.doors = []
        self.connected_to = set()
    
    def get_area(self):
        return self.width * self.height
    
    def is_adjacent(self, other):
        """檢查兩個房間是否相鄰"""
        epsilon = 0.01
        
        if abs(self.x + self.width - other.x) < epsilon or \
           abs(other.x + other.width - self.x) < epsilon:
            return not (self.y + self.height <= other.y or other.y + other.height <= self.y)
        
        if abs(self.y + self.height - other.y) < epsilon or \
           abs(other.y + other.height - self.y) < epsilon:
            return not (self.x + self.width <= other.x or other.x + other.width <= self.x)
        
        return False
    
    def create_door_to(self, other):
        """在兩個相鄰房間之間創建門"""
        door_width = 1
        door = None

        if abs(self.x + self.width - other.x) < 0.01:
            overlap_start = max(self.y, other.y)
            overlap_end = min(self.y + self.height, other.y + other.height)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': self.x + self.width - 0.1,
                'y': overlap_mid - door_width / 2,
                'width': 0.2,
                'height': door_width,
                'is_exit': False
            }
        elif abs(other.x + other.width - self.x) < 0.01:
            overlap_start = max(self.y, other.y)
            overlap_end = min(self.y + self.height, other.y + other.height)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': self.x - 0.1,
                'y': overlap_mid - door_width / 2,
                'width': 0.2,
                'height': door_width,
                'is_exit': False
            }
        elif abs(self.y + self.height - other.y) < 0.01:
            overlap_start = max(self.x, other.x)
            overlap_end = min(self.x + self.width, other.x + other.width)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': overlap_mid - door_width / 2,
                'y': self.y + self.height - 0.1,
                'width': door_width,
                'height': 0.2,
                'is_exit': False
            }
        elif abs(other.y + other.height - self.y) < 0.01:
            overlap_start = max(self.x, other.x)
            overlap_end = min(self.x + self.width, other.x + other.width)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': overlap_mid - door_width / 2,
                'y': self.y - 0.1,
                'width': door_width,
                'height': 0.2,
                'is_exit': False
            }

        if door:
            self.doors.append(door)
            self.connected_to.add(id(other))
    
    def create_exit(self, width_total, height_total):
        """創建外部出口"""
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
                'y': self.y - 0.1,
                'width': door_width,
                'height': 0.2,
                'is_exit': True
            }
        elif wall == 'right':
            exit_door = {
                'x': self.x + self.width - 0.1,
                'y': self.y + (self.height - door_width) / 2,
                'width': 0.2,
                'height': door_width,
                'is_exit': True
            }
        elif wall == 'bottom':
            exit_door = {
                'x': self.x + (self.width - door_width) / 2,
                'y': self.y + self.height - 0.1,
                'width': door_width,
                'height': 0.2,
                'is_exit': True
            }
        elif wall == 'left':
            exit_door = {
                'x': self.x - 0.1,
                'y': self.y + (self.height - door_width) / 2,
                'width': 0.2,
                'height': door_width,
                'is_exit': True
            }

        if exit_door:
            self.doors.append(exit_door)
            return True
        return False

rooms = []

def split_space(x, y, width, height, depth, max_depth, min_size):
    """使用BSP算法遞迴分割空間"""
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
    """確保所有房間連通（使用最小生成樹思想）"""
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
    """創建通行圖：0=可行走，1=牆壁"""
    width_px = int(width * resolution)
    height_px = int(height * resolution)
    
    # 創建網格（初始為1 - 全是牆壁）
    grid = np.ones((width_px, height_px), dtype=np.uint8)
    
    wall_thickness = int(0.1 * resolution)
    
    # 繪製每個房間的可行走區域（0）
    for room in rooms:
        x1 = int(room.x * resolution) + wall_thickness
        y1 = int(room.y * resolution) + wall_thickness
        x2 = int((room.x + room.width) * resolution) - wall_thickness
        y2 = int((room.y + room.height) * resolution) - wall_thickness
        
        grid[x1:x2, y1:y2] = 0
    
    # 繪製門口（0 - 可行走）
    for room in rooms:
        for door in room.doors:
            x1 = max(0, int(door['x'] * resolution))
            y1 = max(0, int(door['y'] * resolution))
            x2 = min(width_px, int((door['x'] + door['width']) * resolution))
            y2 = min(height_px, int((door['y'] + door['height']) * resolution))
            
            grid[x1:x2, y1:y2] = 0
    
    return grid

def save_exit_positions(width, height, resolution, filename='exit_positions.npy'):
    """保存所有出口位置"""
    exits = []
    for room in rooms:
        for door in room.doors:
            if door.get('is_exit', False):
                center_x = int((door['x'] + door['width'] / 2) * resolution)
                center_y = int((door['y'] + door['height'] / 2) * resolution)
                exits.append([center_x, center_y])
    
    if exits:
        np.save(filename, np.array(exits))
        print(f"出口位置已保存到 {filename}")
    return exits

# ===== 主程序 =====
if __name__ == "__main__":
    # 參數設置
    WIDTH = 20
    HEIGHT = 15
    MIN_SIZE = 3
    SPLITS = 4
    RESOLUTION = 50

    print("生成房間布局...")
    split_space(0, 0, WIDTH, HEIGHT, 0, SPLITS, MIN_SIZE)
    ensure_connectivity()

    # 創建1-2個外部出口
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

    print(f"生成了 {len(rooms)} 個房間，{exits_created} 個出口")

    # 生成並保存通行圖
    print("生成通行圖...")
    walkability_grid = create_walkability_map(WIDTH, HEIGHT, RESOLUTION)
    
    # 保存為numpy數組
    np.save('walkability_map.npy', walkability_grid)
    print("通行圖已保存為 walkability_map.npy")
    
    # 保存出口位置
    exits = save_exit_positions(WIDTH, HEIGHT, RESOLUTION)
    
    # 保存配置參數
    config = {
        'width': WIDTH,
        'height': HEIGHT,
        'resolution': RESOLUTION,
        'num_rooms': len(rooms),
        'num_exits': exits_created
    }
    np.save('layout_config.npy', config)
    print("配置已保存為 layout_config.npy")

    # 可視化彩色房間布局
    print("繪製布局圖...")
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
    ax.set_xlabel('寬度 (m)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('2D室內空間布局圖（最小連通）', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('room_layout.png', dpi=150, bbox_inches='tight')
    print("布局圖已保存為 room_layout.png")
    plt.show()

    print("\n完成！可以運行 pathfinding.py 進行尋路演算")
