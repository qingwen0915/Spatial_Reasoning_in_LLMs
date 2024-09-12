import json
import csv
import heapq
import re
import os
import pandas as pd

def parse_description(description):
    grid_size_match = re.search(r'(\d+) by (\d+) by (\d+) world', description)
    grid_size = (int(grid_size_match.group(1)), int(grid_size_match.group(2)), int(grid_size_match.group(3)))
    obstacles_match = re.findall(r'\((\d+),(\d+),(\d+)\)', description.split('avoid at:')[1].split('.')[0])
    obstacles = {(int(x), int(y), int(z)) for x, y, z in obstacles_match}
    start_goal_match = re.findall(r'\((\d+),(\d+),(\d+)\)', description.split('Go from')[1])
    start = (int(start_goal_match[0][0]), int(start_goal_match[0][1]), int(start_goal_match[0][2]))
    goal = (int(start_goal_match[1][0]), int(start_goal_match[1][1]), int(start_goal_match[1][2]))
    return grid_size, start, goal, obstacles

def parse_response(response):
    pattern = r'Action:\s*([^\n#]*)'
    matches = re.findall(pattern, response)
    actions = matches[-1].strip() if matches else None
    return actions
    
def a_star(grid_size, start, goal, obstacles):
    def heuristic(position):
        return abs(position[0] - goal[0]) + abs(position[1] - goal[1]) + abs(position[2] - goal[2])

    grid = [[[0 if (i, j, k) not in obstacles else 1 for k in range(grid_size[2])] for j in range(grid_size[1])] for i in range(grid_size[0])]
    heap = []
    heapq.heappush(heap, (0 + heuristic(start), start, []))
    visited = set()

    while heap:
        cost, current, path = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return len(path)

        for dx, dy, dz in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]:
            nx, ny, nz = current[0] + dx, current[1] + dy, current[2] + dz
            if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1] and 0 <= nz < grid_size[2] and grid[nx][ny][nz] != 1:
                heapq.heappush(heap, (cost + 1 + heuristic((nx, ny, nz)), (nx, ny, nz), path + [current]))

    return float('inf')

def is_valid_path(grid_size, start, goal, obstacles, path_commands):
    directions = {'up': (-1, 0, 0), 'down': (1, 0, 0), 'left': (0, -1, 0), 'right': (0, 1, 0), 'forward': (0, 0, 1), 'backward': (0, 0, -1)}
    x, y, z = start

    for command in path_commands.split():
        if command in directions:
            dx, dy, dz = directions[command]
            x += dx
            y += dy
            z += dz
            if not (0 <= x < grid_size[0] and 0 <= y < grid_size[1] and 0 <= z < grid_size[2]) or (x, y, z) in obstacles:
                return {
                    'valid': False,
                    'reason': "Invalid path: Out of bounds or hit an obstacle",
                    'is_optimal': False,
                    'actual_path_length': None,
                    'optimal_path_length': None
                }

    is_goal_reached = (x, y, z) == goal
    optimal_path_length = a_star(grid_size, start, goal, obstacles)
    actual_path_length = len(path_commands.split())

    return {
        'valid': is_goal_reached,
        'reason': "Reached the goal" if is_goal_reached else "Did not reach the goal",
        'is_optimal': (actual_path_length == optimal_path_length) if is_goal_reached else False,
        'actual_path_length': actual_path_length,
        'optimal_path_length': optimal_path_length
    }

def calculate_percentages(data):
    valid_count = sum(1 for item in data if item['valid'])
    optimal_count = sum(1 for item in data if item['is_optimal'])
    total_count = len(data)

    valid_percentage = (valid_count / total_count) * 100
    optimal_percentage = (optimal_count / total_count) * 100

    return valid_percentage, optimal_percentage, total_count

directory_path = 'results/'
outputs = []
results_list = []

for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    data = json.load(open(file_path)) 

    for task in data:
        grid_size, start, goal, obstacles = parse_description(task['english'])
        path_commands = parse_response(task['predicted'])
        result = is_valid_path(grid_size, start, goal, obstacles, path_commands)
        outputs.append(result)

    json_path = 'valid-path/'
    model_name = filename.split('.')[0].replace('results_', '')
    with open(json_path+model_name+'_valid_path.json', 'w') as f:
        json.dump(outputs, f, indent=4)

    valid_percentage, optimal_percentage, total_count = calculate_percentages(outputs)

    results_list.append({
            'Model Name': filename.replace('results_', '').replace('.json', ''),
            'Valid Percentage': valid_percentage,
            'Optimal Percentage': optimal_percentage,
            'Total Count': total_count
        })

results_df = pd.DataFrame(results_list)
results_df.to_csv('model_accuracy_results.csv', index=False)