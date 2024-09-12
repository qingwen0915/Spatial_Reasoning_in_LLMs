import numpy as np 
import json
import os 
import sys 
import heapq
import gurobipy as gp
from gurobipy import GRB

# THIS IS THE LAST FILE TO USE, after place_agent_goals.py (generate_envs.py before place_agent_goals)

# This is the natural language generation piece
# Takes in an x by y world, an initial location as a list [x coord, y coord], a list of goals [goal index][x coord][y coord].
# They seem to ignore contraints here.
# Just simple string concatenation to generate. Straightforward.
def generate_nl(x, y, obstacles, goals, initial_loc, constraint='None'):

    '''
        Possible Constraints:
            arithm even
            arithm odd
            arithm prime
            arithm divs {x}
            {x} before {y}
    '''

    english = f'You are in a {x} by {y} world. There are obstacles that you have to avoid at: '

    # First provide the obstacles.
    for i in range(len(obstacles)):
        obstacle = obstacles[i]
        english += f'({obstacle[0]},{obstacle[1]})'
        if(i < len(obstacles) - 2):
                english += ', '
        elif (i == len(obstacles) - 2): 
                english += ' and '
    
    # Then provide the goals
    english += '. '
    if(len(goals) == 1):
        english += f'Go from ({initial_loc[0]},{initial_loc[1]}) to ({goals[0][0]},{goals[0][1]})' 
    
    # If multiple goals
    else:
        english += f'You are at ({initial_loc[0]},{initial_loc[1]}).'

        english += ' You have to visit ' 
        for i in range(len(goals)):
            english += f'p{i}'
            if(i < len(goals) - 2):
                english += ', '
            elif (i == len(goals) - 2): 
                english += ' and '
        
        english += '. '

    # this is where the multiple goals are
        for i in range(len(goals)):
            english += f'p{i} is located at ({goals[i][0]}, {goals[i][1]})'
            if(i < len(goals) - 2):
                english += ', '
            elif (i == len(goals) - 2): 
                english += ' and '
        
        # If we want a strict ordering
        english += '. '
        if('arithm' in constraint):
            plan = constraint.split(' ')

            if(len(plan) == 2):
                english += 'Visit ' + plan[1] + ' numbered locations first.'

            elif(len(plan) == 3):
                english += 'Visit divisors of ' + plan[2] + ' first.' 
    
    return english

# This will check
def a_star(grid, start, goal):
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def heuristic(position):
        return abs(position[0] - goal[0]) + abs(position[1] - goal[1])

    visited = set()
    heap = []
    heapq.heappush(heap, (0, start, []))
    while heap:
        cost, current, path = heapq.heappop(heap)

        if current == goal:
            return path + [current]

        if current in visited:
            continue

        visited.add(current)

        for action in actions:
            neighbor = (current[0] + action[0], current[1] + action[1])

            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if grid[neighbor] != 1:
                    new_cost = cost + 1
                    new_path = path + [current]
                    heapq.heappush(heap, (new_cost + heuristic(neighbor), neighbor, new_path))

    return 'Goal not reachable'

def a_star_value(grid, start, goal):
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def heuristic(position):
            return abs(position[0] - goal[0]) + abs(position[1] - goal[1])

        visited = set()
        heap = []
        heapq.heappush(heap, (0, start, []))

        while heap:
            cost, current, path = heapq.heappop(heap)

            current = tuple(current)
            if current == goal:
                return len(path + [current])

            if current in visited:
                continue

            visited.add(current)

            for action in actions:
                neighbor = (current[0] + action[0], current[1] + action[1])

                if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                    if grid[neighbor] != 1:
                        new_cost = cost + 1
                        new_path = path + [current]
                        heapq.heappush(heap, (new_cost + heuristic(neighbor), neighbor, new_path))

        return 100000

def solution_point(path):

    if(path == 'Goal not reachable'):
        return path

    directions = ''
    
    for i in range(len(path) - 1):
        curr = path[i]
        nxt = path[i + 1]

        if(curr[0] + 1 == nxt[0]):
            directions += 'down '
        elif (curr[0] - 1 == nxt[0]):
            directions += 'up '
        elif (curr[1] + 1 == nxt[1]):
            directions += 'right '
        elif (curr[1] - 1 == nxt[1]):
            directions += 'left '

    return directions

def solution_direction(path):

    if(path == 'Goal not reachable'):
        return path

    path = path.split(' ')

    directions = ''

    orientation = 'south'
    
    for i in range(len(path)):

        if(path[i] == 'right'):
            if(orientation == 'south'):
                directions += 'turn left move forward '
                orientation = 'east'
            elif (orientation == 'north'):
                directions += 'turn right move forward '
                orientation = 'east'
            elif (orientation == 'east'):
                directions += 'move forward '
            elif (orientation == 'west'):
                directions += 'turn right turn right move forward '
                orientation = 'east'
        elif (path[i] == 'left'):
            if(orientation == 'south'):
                directions += 'turn right move forward '
                orientation = 'west'
            elif (orientation == 'north'):
                directions += 'turn left move forward '
                orientation = 'west'
            elif (orientation == 'east'):
                directions += 'turn left turn left move forward '
                orientation = 'west'
            elif (orientation == 'west'):
                directions += 'move forward '
        elif (path[i] == 'down'):
            if(orientation == 'south'):
                directions += 'move forward '
                orientation = 'south'
            elif (orientation == 'north'):
                directions += 'turn left turn left move forward '
                orientation = 'south'
            elif (orientation == 'east'):
                directions += 'turn right move forward '
                orientation = 'south'
            elif (orientation == 'west'):
                directions += 'turn left move forward '
                orientation = 'south'
        elif (path[i] == 'up'):
            if(orientation == 'south'):
                directions += 'turn right turn right move forward '
                orientation = 'north'
            elif (orientation == 'north'):
                directions += 'move forward '
                orientation = 'north'
            elif (orientation == 'east'):
                directions += 'turn left move forward '
                orientation = 'north'
            elif (orientation == 'west'):
                directions += 'turn right move forward '
                orientation = 'south'

    return directions


def solution_plan(plan):

    path = ''
    for i in range(len(plan)):
        curr = plan[i][0]
        nxt = plan[i][1]

        sub_path = solution_point(plan[i][2])
        path += sub_path + 'inspect '

    return path



def main():
    '''
    CLA:
        directory/setting
    '''


    samples = []
    # Place in your
    with open(str(sys.argv[1])) as f:
        data = json.load(f)

        # For each environment you created
        for world in data:

            # Extract the necessary components to get the natural language
            grid = world['world']
            obstacles = world['obstacles']
            start = world['start']
            goals = world['goals']
            
            # Generate the natural language description.
            nl = generate_nl(len(grid), len(grid[0]), obstacles, goals, start)

            if(len(goals) == 1):
                # This puts in our grid, starting position, and goal position
                coordinates = a_star(np.array(grid), (start[0], start[1]), (goals[0][0], goals[0][1]))
                # Generate the solution and its direction
                # Uses the a_star algorithm to check if a goal is reachable, and attributes values to
                # Get our text to arrive there somehow
                sol_point = solution_point(coordinates)

                # this is simple. But it takes into account the agent's orientation to provide directions.
                sol_direct = solution_direction(sol_point)

                sample = {
                    'world': grid,
                    'nl_description': nl,
                    'solution_coordinates': coordinates,
                    'agent_as_a_point': sol_point,
                    'agent_has_direction': sol_direct 
                }


            samples.append(sample)

        with open(str(sys.argv[1]).replace('.json', '') + '_samples.json', 'w') as fo:
                json_object = json.dumps(samples, indent = 4)
                fo.write(json_object)
                fo.write('\n')

    
if __name__ == "__main__":
    main()

# This will generate the samples. 1_train_set_samples.json

    