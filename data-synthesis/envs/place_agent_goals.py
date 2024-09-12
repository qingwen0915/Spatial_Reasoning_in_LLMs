import random
import sys
import json
import os

# THIS FILE COMES AFTER generate_envs.py

# Let's construct the grid
def construct_grid(n, obstacles):
    '''
    0: empty cell
    1: obstacle
    2: start location
    3: goal
    '''
    grid = []

    # If there is an obstacle, print a 1, else a 0 - just extracting them here
    for i in range(n):
        row = []
        for j in range(n):
            if([i, j] in obstacles):
                row.append(1)
            else:
                row.append(0)
        grid.append(row)
    
    return grid

# Our input here is our obstacle locations, our grid size, the goals we want
def generate_worlds(obstacles, n, n_goals, trials=30):

    worlds = []
    # For each trial
    for _ in range(trials):
        # Give a grid with the obstacles
        grid = construct_grid(n, obstacles)
        while(True):
            # Put one agent in here that isn't already in an obstacle
            agent_x = random.randint(0, n-1)
            agent_y = random.randint(0, n-1)
            if([agent_x, agent_y] not in obstacles):
                break

        # print(agent_x, agent_y)

        # So we mark our obstacles as 1, our agent as 2, and open spaces as 0
        grid[agent_x][agent_y] = 2
    
        goals = []
        while(True):
            # Randomly generate the goals, don't overlap with others. Pick an open space
            goal_x = random.randint(0, n-1)
            goal_y = random.randint(0, n-1)
            if([goal_x, goal_y] not in obstacles 
                    and [goal_x, goal_y] != [agent_x, agent_y]
                    and [goal_x, goal_y] not in goals):
                goals.append([goal_x, goal_y])
                grid[goal_x][goal_y] = 3
            
            # Once we hit our goal limit, stop creating them
            if(len(goals) == n_goals):
                break

        # Get our information in an output
        # Open is 0, obstacle is 1, agent is 2, goal is 3
        '''
        Sample output:
        Grid:
        [[1, 2, 3], [0, 3, 3], [3, 1, 3]]
        Goal - these are coordinates
        [[1, 2], [2, 2], [1, 1], [2, 0], [0, 2]]
        Obstacle - these are coordinates
        [[2, 1], [0, 0]]
        '''
        print("Start")
        print([agent_x, agent_y])
        print(obstacles)
        print("Grid")
        print(grid)
        # Our
        worlds.append({
            'world': grid,
            'obstacles': obstacles,
            'start': [agent_x, agent_y], # Just one
            'goals': goals
        })

    return worlds


def main():
    '''
    CLA:
        directory/setting
        number of goals
    '''

    envs = os.listdir(str(sys.argv[1]))
    envs = [f for f in envs if "environments" in f]
    # This will extract this - just provide your folder with the JSON files
    '''
    ['generate_samples.py', 'generate_envs.py', 'place_agent_goals.py', 'environments2.json']
    This is wrong. Perhaps create a new folder for your .jsons separate from the python
    '''

    n_goals = int(sys.argv[2])
    
    worlds_train = []
    worlds_dev = []
    worlds_test = []

    # For each file
    for env in envs:
        # Read in the data from your folder
        with open(str(sys.argv[1]) + '/' + env) as f:
            
            # Data must be a json
            data = json.load(f)

            # Divide into train and test sets
            train = 0.8 * len(data)
            test = 0.2 * len(data)
    
            # Get 80% of the environments, loop through these
            for inst in data[:int(train)]:
                # For each environment, get the obstacles and the grid size
                obstacles = inst['obstacles']
                shape = inst['shape']

                '''
                Sample output
                [[2, 1], [0, 0]] <- for the obstacles
                Shape: the tuple, we just care about the size
                '''
                # Get the grid world setup
                combinations = generate_worlds(obstacles, shape[0], n_goals, trials=30)

                # Split train, test, dev
                tr = int(0.8 * len(combinations))
                dv = int(0.1 * len(combinations))
                # this is the unseen, holdout s
                ts = int(0.1 * len(combinations))

                for comb in combinations[:tr]:
                    worlds_train.append(comb)
                for comb in combinations[tr:tr+ts]:
                    worlds_dev.append(comb)
                for comb in combinations[tr+ts:]:
                    worlds_test.append(comb)

            # print(len(worlds_train), len(worlds_test), len(worlds_dev))

    # Write each to a json
    with open(str(n_goals)+'_train_set' + '.json', 'w') as fo:
        json_object = json.dumps(worlds_train, indent = 4)
        fo.write(json_object)
        fo.write('\n')
    with open(str(n_goals)+'dev_set' + '.json', 'w') as fo:
        json_object = json.dumps(worlds_dev, indent = 4)
        fo.write(json_object)
        fo.write('\n')
    with open(str(n_goals)+'_goals_test_seen' + '.json', 'w') as fo:
        json_object = json.dumps(worlds_test, indent = 4)
        fo.write(json_object)
        fo.write('\n')

    '''- generate unseen environments'''

    # this is just the exact same logic as above, repeated once more
    # This is weird, idk if we need this
    worlds_unseen = []
    for env in envs:
        with open(str(sys.argv[1]) + '/' + env) as f:
            data = json.load(f)

            train = 0.8 * len(data)
            test = 0.2 * len(data)

            for inst in data[int(train):]:
                obstacles = inst['obstacles']
                shape = inst['shape']

                print(obstacles)
                combinations = generate_worlds(obstacles, shape[0], n_goals, trials=30)

                tr = int(0.8 * len(combinations))
                dv = int(0.1 * len(combinations))
                ts = int(0.1 * len(combinations))
                
                print(tr, dv, ts)
                print(len(combinations))
                for comb in combinations:
                    worlds_unseen.append(comb)

            print(len(worlds_unseen))

    with open(str(n_goals)+'goals_unseen' + '.json', 'w') as fo:
        json_object = json.dumps(worlds_unseen, indent = 4)
        fo.write(json_object)
        fo.write('\n')

if __name__ == "__main__":
    main()