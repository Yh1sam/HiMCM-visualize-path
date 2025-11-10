# 2D室內空間生成器 - 完整版（最小連通 + 通行圖）
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = random.choice(['客廳', '臥室', '廚房', '浴室', '書房', '餐廳', '儲藏室'])
        self.color = random.choice(['#FFE5B4', '#B4D7FF', '#FFB4D7', '#B4FFD7', 
                                   '#FFD7B4', '#D7B4FF', '#FFFFB4'])
        self.doors = []  # 存儲門的位置
        self.connected_to = set()  # 記錄已連接的房間
    
    def get_area(self):
        return self.width * self.height
    
    def is_adjacent(self, other):
        """檢查兩個房間是否相鄰"""
        epsilon = 0.01
        
        # 檢查水平相鄰（共享垂直邊）
        if abs(self.x + self.width - other.x) < epsilon or \
           abs(other.x + other.width - self.x) < epsilon:
            return not (self.y + self.height <= other.y or other.y + other.height <= self.y)
        
        # 檢查垂直相鄰（共享水平邊）
        if abs(self.y + self.height - other.y) < epsilon or \
           abs(other.y + other.height - self.y) < epsilon:
            return not (self.x + self.width <= other.x or other.x + other.width <= self.x)
        
        return False
    
    def create_door_to(self, other):
        """在兩個相鄰房間之間創建門"""
        door_width = 1  # 門寬1米
        door = None

        # 右側相鄰
        if abs(self.x + self.width - other.x) < 0.01:
            overlap_start = max(self.y, other.y)
            overlap_end = min(self.y + self.height, other.y + other.height)
            overlap_mid = (overlap_start + overlap_end) / 2
            wall_thickness = int(0.1 * RESOLUTION)
            door = {
                'x': self.x + self.width - wall_thickness / RESOLUTION,
                'y': overlap_mid - door_width / 2,
                'width': 0.2,
                'height': door_width,
                'is_exit': False
            }
        # 左側相鄰
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
        # 下側相鄰
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
        # 上側相鄰
        elif abs(other.y + other.height - self.y) < 0.01:
            overlap_start = max(self.x, other.x)
            overlap_end = min(self.x + self.width, other.x + other.width)
            overlap_mid = (overlap_start + overlap_end) / 2
            
            door = {
                'x': overlap_mid - door_width / 2,
                'y': self.y - 0.1,
                'width': door_width,
                'height': 1,
                'is_exit': False
            }

        if door:
            self.doors.append(door)
            self.connected_to.add(id(other))
    
    def create_exit(self, width_total, height_total):
        """創建外部出口"""
        door_width = 1
        walls = []
        
        # 檢查哪些牆是外牆
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
        
        # 隨機選擇一面外牆
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

def find_connected_component(room, visited):
    """使用DFS找到與給定房間連通的所有房間"""
    visited.add(id(room))
    component = [room]
    
    for other_id in room.connected_to:
        if other_id not in visited:
            for r in rooms:
                if id(r) == other_id:
                    component.extend(find_connected_component(r, visited))
                    break
    
    return component

def ensure_connectivity():
    """確保所有房間連通（使用最小生成樹思想）"""
    if len(rooms) <= 1:
        return
    
    # 構建相鄰關係圖
    adjacency = {}
    for i, room in enumerate(rooms):
        adjacency[i] = []
        for j, other in enumerate(rooms):
            if i != j and room.is_adjacent(other):
                adjacency[i].append(j)
    
    # 使用Prim算法構建最小生成樹
    connected = {0}  # 從第一個房間開始
    edges_added = 0
    
    while len(connected) < len(rooms) and edges_added < len(rooms) * 2:
        # 找到一條邊：一端在connected中，另一端不在
        found = False
        for i in connected:
            for j in adjacency[i]:
                if j not in connected:
                    # 創建門連接
                    rooms[i].create_door_to(rooms[j])
                    rooms[j].connected_to.add(id(rooms[i]))
                    connected.add(j)
                    edges_added += 1
                    found = True
                    break
            if found:
                break
        
        if not found:
            # 如果找不到邊，嘗試隨機連接（處理非相鄰情況）
            break

# ===== 參數設置 =====
WIDTH = 20        # 總寬度 (米)
HEIGHT = 15       # 總高度 (米)
MIN_SIZE = 3      # 最小房間尺寸 (米)
SPLITS = 4        # 分割次數
RESOLUTION = 50   # 通行圖解析度（每米的像素數）

# 生成布局
split_space(0, 0, WIDTH, HEIGHT, 0, SPLITS, MIN_SIZE)

# 使用最小生成樹確保連通性
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

# ===== 生成通行圖 (Walkability Map) =====
def create_walkability_map():
    """創建通行圖：白色=可行走，黑色=牆壁，綠色=出口"""
    width_px = int(WIDTH * RESOLUTION)
    height_px = int(HEIGHT * RESOLUTION)
    
    # 創建RGB圖像（初始為黑色 - 全是牆壁）
    walkmap = np.zeros((height_px, width_px, 3), dtype=np.uint8)
    
    wall_thickness = int(0.1 * RESOLUTION)  # 牆厚度約0.1米
    
    # 繪製每個房間的可行走區域（白色）
    for room in rooms:
        x1 = int(room.x * RESOLUTION) + wall_thickness
        y1 = int(room.y * RESOLUTION) + wall_thickness
        x2 = int((room.x + room.width) * RESOLUTION) - wall_thickness
        y2 = int((room.y + room.height) * RESOLUTION) - wall_thickness
        
        # 填充白色（可行走）
        walkmap[y1:y2, x1:x2] = [255, 255, 255]
    
    # 繪製門口（內部門和出口）
    for room in rooms:
        for door in room.doors:
            # 計算像素坐標，並確保不超出邊界
            x1 = max(0, int(door['x'] * RESOLUTION))
            y1 = max(0, int(door['y'] * RESOLUTION))
            x2 = min(width_px, int((door['x'] + door['width']) * RESOLUTION))
            y2 = min(height_px, int((door['y'] + door['height']) * RESOLUTION))
            
            # 確保坐標有效
            if x2 > x1 and y2 > y1:
                if door['is_exit']:
                    # 出口（純綠色）
                    walkmap[y1:y2, x1:x2] = [0, 255, 0]
                else:
                    # 內部門（白色 - 可行走）
                    walkmap[y1:y2, x1:x2] = [255, 255, 255]
    
    return walkmap

walkability_map = create_walkability_map()

# ===== 可視化（2張圖） =====
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# 左圖：彩色房間布局
for room in rooms:
    # 繪製房間
    rect = patches.Rectangle((room.x, room.y), room.width, room.height,
                             linewidth=2, edgecolor='black', facecolor=room.color, alpha=0.7)
    ax1.add_patch(rect)
    
    # 繪製所有門（內部門和出口）
    for door in room.doors:
        if door['is_exit']:
            # 外部出口（綠色）
            door_rect = patches.Rectangle((door['x'], door['y']), door['width'], door['height'],
                                         linewidth=3, edgecolor='#2E7D32', facecolor='#4CAF50')
        else:
            # 內部門（白色）
            door_rect = patches.Rectangle((door['x'], door['y']), door['width'], door['height'],
                                         linewidth=2, edgecolor='#666', facecolor='white')
        ax1.add_patch(door_rect)
    
    # 添加房間標籤
    center_x = room.x + room.width / 2
    center_y = room.y + room.height / 2
    ax1.text(center_x, center_y, f'{room.type}\n{room.width:.1f}m × {room.height:.1f}m',
           ha='center', va='center', fontsize=9, weight='bold',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))

ax1.set_xlim(0, WIDTH)
ax1.set_ylim(0, HEIGHT)
ax1.set_aspect('equal')
ax1.set_xlabel('寬度 (m)', fontsize=12)
ax1.set_ylabel('高度 (m)', fontsize=12)
ax1.set_title('彩色房間布局圖（最小連通）', fontsize=14, weight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')

# 右圖：通行圖（黑白綠）
ax2.imshow(walkability_map, origin='lower', extent=[0, WIDTH, 0, HEIGHT])
ax2.set_xlim(0, WIDTH)
ax2.set_ylim(0, HEIGHT)
ax2.set_aspect('equal')
ax2.set_xlabel('寬度 (m)', fontsize=12)
ax2.set_ylabel('高度 (m)', fontsize=12)
ax2.set_title('通行圖（白色=可行走，黑色=牆壁，綠色=出口）', fontsize=14, weight='bold')
ax2.grid(True, alpha=0.3, linestyle='--', color='gray')

plt.tight_layout()
plt.show()

# 可選：保存通行圖為圖片
from PIL import Image
walkmap_img = Image.fromarray(walkability_map)
walkmap_img.save('walkability_map.png')
print("通行圖已保存為 walkability_map.png")

# ===== 輸出房間信息 =====
print(f"\n{'='*60}")
print(f"生成了 {len(rooms)} 個房間:")
print(f"{'='*60}")

total_area = 0
total_exits = 0
total_doors = 0

for i, room in enumerate(rooms, 1):
    area = room.get_area()
    total_area += area
    internal_doors = len([d for d in room.doors if not d['is_exit']])
    exit_doors = len([d for d in room.doors if d['is_exit']])
    total_exits += exit_doors
    total_doors += internal_doors
    
    exit_mark = ' 🚪 [外部出口]' if exit_doors > 0 else ''
    print(f"{i:2d}. {room.type:6s}: {room.width:5.1f}m × {room.height:5.1f}m = {area:6.1f}m² | 內部門:{internal_doors}{exit_mark}")

print(f"{'='*60}")
print(f"總面積: {total_area:.1f}m² | 內部門總數: {total_doors} | 外部出口: {total_exits}")
print(f"{'='*60}")
