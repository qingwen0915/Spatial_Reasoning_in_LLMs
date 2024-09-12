import json

def parse_description(description):
    parts = description.split()
    grid_size = (int(parts[2]), int(parts[4]))
    obstacles = []
    if parts[-3] != "at:":
        obstacles_str = " ".join(parts[parts.index("at:") + 1:parts.index("Go")])
        obstacles = [tuple(map(int, obs.strip("()").split(","))) for obs in obstacles_str.split()]
    start_goal_str = " ".join(parts[parts.index("Go") + 2:])
    start = tuple(map(int, start_goal_str.split(")")[0].strip("(").split(",")))
    goal = tuple(map(int, start_goal_str.split(")")[1].strip("(").split(",")))
    return grid_size, start, goal, obstacles

def parse_response(response):
    actions = response.strip().split()
    return actions

def is_valid_path(grid_size, start, goal, obstacles, path_commands):
    directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
    x, y = start

    for command in path_commands:
        if command in directions:
            dx, dy = directions[command]
            x += dx
            y += dy
            if not (0 <= x < grid_size[0] and 0 <= y < grid_size[1]) or (x, y) in obstacles:
                return False, None

    is_goal_reached = (x, y) == goal
    return is_goal_reached, len(path_commands)

def evaluate_results(results_file, ground_truth_file):
    with open(results_file, "r") as f:
        results = json.load(f)

    with open(ground_truth_file, "r") as f:
        ground_truth = json.load(f)

    total_cases = len(results)
    valid_paths = 0
    optimal_paths = 0
    path_lengths = []

    for result, truth in zip(results, ground_truth):
        grid_size, start, goal, obstacles = parse_description(result["english"])
        ground_truth_actions = parse_response(truth["agent_as_a_point"])
        predicted_actions = parse_response(result["predicted"])

        is_valid, path_length = is_valid_path(grid_size, start, goal, obstacles, predicted_actions)
        if is_valid:
            valid_paths += 1
            if path_length == len(ground_truth_actions):
                optimal_paths += 1
            path_lengths.append(path_length)

    valid_percentage = (valid_paths / total_cases) * 100
    optimal_percentage = (optimal_paths / total_cases) * 100

    return {
        "valid_percentage": valid_percentage,
        "optimal_percentage": optimal_percentage,
        "path_lengths": path_lengths,
    }

# Example usage
results_file = "results_3x.json"
ground_truth_file = "../worlds/2D_world_3x.json"
evaluation = evaluate_results(results_file, ground_truth_file)
print(f"Valid Percentage: {evaluation['valid_percentage']:.2f}%")
print(f"Optimal Percentage: {evaluation['optimal_percentage']:.2f}%")
print(f"Path Lengths: {evaluation['path_lengths']}")