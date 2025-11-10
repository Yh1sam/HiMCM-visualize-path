import json
import math

def generate_simple_office_layout(
    floor_width=50.0,
    floor_height=30.0,
    corridor_width=3.0,
    num_offices_per_side=5,
    door_width = 0.9
):
    """
    Generates a simple, well-structured office layout from scratch.

    This function creates a highly organized single-floor office layout with a
    central corridor, offices arranged in a grid, and logically placed exits,
    doors, and safety equipment. The layout is represented as a dictionary of
    nodes (rooms, doors, exits, equipment) with coordinates.

    The generation logic is as follows:
    1.  A central horizontal corridor is created.
    2.  Offices are placed in a grid pattern on both sides of the corridor.
    3.  A door is added to each office, connecting it to the corridor.
    4.  Two exits are placed at each end of the central corridor.
    5.  Safety equipment is distributed logically.

    Returns:
        dict: A dictionary containing the building's name, floor dimensions,
              and lists of rooms, doors, exits, and safety equipment.
    """
    layout = {
        'name': 'Simple Office Floor',
        'floor_dimensions': (floor_width, floor_height),
        'rooms': [],
        'doors': [],
        'exits': [],
        'safety_equipment': []
    }

    # Add central corridor
    corridor_y = (floor_height - corridor_width) / 2
    layout['rooms'].append({
        'id': 'CORRIDOR_01',
        'name': 'Main Corridor',
        'type': 'corridor',
        'position': (0, corridor_y),
        'size': (floor_width, corridor_width)
    })

    # Add offices and doors
    office_h = corridor_y
    office_w = floor_width / num_offices_per_side
    room_id = 0
    for i in range(num_offices_per_side):
        # Top side office
        office_x = i * office_w
        office_y = floor_height - office_h
        office = {
            'id': f'OFFICE_{room_id}',
            'name': f'Office {room_id}',
            'type': 'office',
            'position': (office_x, office_y),
            'size': (office_w, office_h)
        }
        layout['rooms'].append(office)
        
        # Add door for top side office
        layout['doors'].append({
            'id': f'DOOR_OFFICE_{room_id}',
            'room_id': f'OFFICE_{room_id}',
            'position': (office_x + (office_w - door_width)/2, office_y),
            'size': (door_width, 0.2) # thin rectangle for door
        })
        room_id += 1

        # Bottom side office
        office_x = i * office_w
        office_y = 0
        office = {
            'id': f'OFFICE_{room_id}',
            'name': f'Office {room_id}',
            'type': 'office',
            'position': (office_x, office_y),
            'size': (office_w, office_h)
        }
        layout['rooms'].append(office)

        # Add door for bottom side office
        layout['doors'].append({
            'id': f'DOOR_OFFICE_{room_id}',
            'room_id': f'OFFICE_{room_id}',
            'position': (office_x + (office_w - door_width)/2, office_h - 0.2),
            'size': (door_width, 0.2) # thin rectangle for door
        })
        room_id += 1

    # Add exits
    exit_width = 1.2
    layout['exits'].append({
        'id': 'EXIT_01',
        'position': (0, corridor_y + (corridor_width - exit_width) / 2),
        'width': exit_width,
        'type': 'main_exit'
    })
    layout['exits'].append({
        'id': 'EXIT_02',
        'position': (floor_width - exit_width, corridor_y + (corridor_width - exit_width) / 2),
        'width': exit_width,
        'type': 'main_exit'
    })

    # Add safety equipment (logical placement)
    # Alarms and extinguishers near exits
    for exit_obj in layout['exits']:
        ex, ey = exit_obj['position']
        exit_width = exit_obj['width']
        layout['safety_equipment'].append({
            'id': f'ALARM_{exit_obj["id"]}',
            'type': 'fire_alarm',
            'position': (ex + exit_width + 1 if ex == 0 else ex - 1, ey)
        })
        layout['safety_equipment'].append({
            'id': f'EXTINGUISHER_{exit_obj["id"]}',
            'type': 'extinguisher',
            'position': (ex + exit_width + 1 if ex == 0 else ex - 1, ey + 1)
        })
        layout['safety_equipment'].append({
            'id': f'EMERG_LIGHT_{exit_obj["id"]}',
            'type': 'emergency_light',
            'position': (ex + exit_width/2, ey + exit_width)
        })


    # Smoke detectors in rooms and corridor
    for room in layout['rooms']:
        rx, ry = room['position']
        rw, rh = room['size']
        if room['type'] == 'office':
            layout['safety_equipment'].append({
                'id': f'SMOKE_{room["id"]}',
                'type': 'smoke_detector',
                'position': (rx + rw/2, ry + rh/2)
            })
        elif room['type'] == 'corridor':
            # Place detectors along the corridor
            for i in range(1, int(floor_width / 10)):
                 layout['safety_equipment'].append({
                    'id': f'SMOKE_CORRIDOR_{i}',
                    'type': 'smoke_detector',
                    'position': (i * 10, ry + rh/2)
                })


    return layout

if __name__ == "__main__":
    office_layout = generate_simple_office_layout()
    with open('simple_office.json', 'w') as f:
        json.dump(office_layout, f, indent=2)
    print("Generated simple_office.json")