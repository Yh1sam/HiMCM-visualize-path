import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_simple_office(data_file='simple_office.json'):
    """
    Generates and saves a visualization of the simple office layout.
    """
    with open(data_file, 'r') as f:
        layout = json.load(f)

    floor_width, floor_height = layout['floor_dimensions']

    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_title(layout['name'])
    ax.set_xlabel("X-coordinate (m)")
    ax.set_ylabel("Y-coordinate (m)")
    ax.set_xlim(-2, floor_width + 2)
    ax.set_ylim(-2, floor_height + 2)
    ax.set_aspect('equal', adjustable='box')

    # Define colors and markers
    room_colors = {'office': 'lightblue', 'corridor': 'lightgrey'}
    exit_marker = 'X'
    safety_equipment_markers = {
        'fire_alarm': 'v',
        'extinguisher': 'o',
        'smoke_detector': 's',
        'emergency_light': '*'
    }
    safety_equipment_colors = {
        'fire_alarm': 'red',
        'extinguisher': 'darkred',
        'smoke_detector': 'orange',
        'emergency_light': 'yellow'
    }

    # Draw rooms
    for room in layout['rooms']:
        x, y = room['position']
        w, h = room['size']
        color = room_colors.get(room['type'], 'lightcyan')
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='black', facecolor=color, label=room['type'])
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, room['name'], ha='center', va='center', fontsize=9, wrap=True)

    # Draw exits
    for exit_obj in layout['exits']:
        x, y = exit_obj['position']
        w = exit_obj['width']
        # Draw exit as a rectangle
        rect = patches.Rectangle((x,y), w, w, linewidth=2, edgecolor='green', facecolor='green', label='exit')
        ax.add_patch(rect)

    # Draw doors
    if 'doors' in layout:
        for door in layout['doors']:
            x, y = door['position']
            w, h = door['size']
            rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='saddlebrown', facecolor='saddlebrown', label='door', zorder=4)
            ax.add_patch(rect)

    # Draw safety equipment
    for equip in layout['safety_equipment']:
        x, y = equip['position']
        marker = safety_equipment_markers.get(equip['type'], 'P')
        color = safety_equipment_colors.get(equip['type'], 'purple')
        ax.scatter(x, y, marker=marker, color=color, s=100, label=equip['type'], zorder=5)

    # Create a legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', bbox_to_anchor=(1.2, 1))

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig('simple_office_layout.png', bbox_inches='tight')
    plt.close(fig)
    print("Saved visualization to simple_office_layout.png")

if __name__ == "__main__":
    visualize_simple_office()
