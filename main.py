import os
from modules.pathfinding import run_pathfinding

# 批量處理多個布局
layouts_dir = 'layouts'
for folder in os.listdir(layouts_dir):
    folder_path = os.path.join(layouts_dir, folder)
    if os.path.isdir(folder_path) and folder != 'latest':
        print(f"\nProcessing {folder}...")
        results = run_pathfinding(folder_path, num_people=8, show_plot=False)
        if results:
            print(f"Success rate: {results['success_rate']:.1f}%")
