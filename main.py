# main.py - Batch process layouts and generate pathfinding results
import os
from modules.pathfinding import run_pathfinding

# Batch process multiple layout folders
results = run_pathfinding(
    layout_dir='basic_office_map',
    num_people=8,
    save_output=True,  # 保存PNG和TXT
    show_plot=True     # 顯示圖表
)
