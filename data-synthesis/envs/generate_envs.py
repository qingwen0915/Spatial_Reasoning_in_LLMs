import random
import sys
import json

# START WITH THIS FILE FOR THE DATA GENERATION PROCESS
def generate_environments(n, min_obstacles, max_obstacles):
    '''
    Takes in the shape (1st command argument)
    Takes in the number of obstacles, randomizes location (2nd command argument)
    '''

    obsts = []

    # Randomizing the location on the grid
    num_obstacles = random.randint(min_obstacles, max_obstacles)
    while(len(obsts) < num_obstacles):
        i = random.randint(0, n-1)
        j = random.randint(0, n-1)

        # If already in here, don't append, continue
        if((i, j) in obsts):
            continue
        
        # Append location to list
        obsts.append((i, j))
    
    # Return the grid shape (nxn grid), just one tuple, and the obstacle locations (list of tuples)
    # Example output
    '''
    User input: python generate_envs.py 3 2 4
    3x3, with 2 obstacles, 4 environments

    {'shape': (3, 3), 'obstacles': [(2, 0), (0, 2)]}
    {'shape': (3, 3), 'obstacles': [(2, 2), (0, 1)]}
    {'shape': (3, 3), 'obstacles': [(1, 2), (2, 1)]}
    {'shape': (3, 3), 'obstacles': [(2, 1), (1, 0)]}

    '''

    return {
        'shape': (n, n),
        'obstacles': obsts
    }

def main():
    '''
    CLA:
        shape of the grids - 1st arg
        number of obstacles - 2nd arg
        number of environments - 3rd arg
    '''
    # Extract from the terminal
    shape = int(sys.argv[1])
    nb_obstacles = int(sys.argv[2])
    target = int(sys.argv[3])

    # Get the envs
    envs = []

    while(True):
        # Generate from user input
        env = generate_environments(shape, nb_obstacles, nb_obstacles)

        # If there is a duplicate, ignore it - get distinct envs
        if(env in envs):
            continue

        envs.append(env)

        # If we have all our envs, we're done
        if(len(envs) == target):
            break


    # Write the environments to a JSON file - sample input
    '''
    [{'shape': (3, 3), 'obstacles': [(0, 1), (1, 2)]}, {'shape': (3, 3), 'obstacles': [(0, 1), (2, 2)]}, {'shape': (3, 3), 'obstacles': [(1, 2), (2, 1)]}, {'shape': (3, 3), 'obstacles': [(0, 2), (2, 2)]}]
    '''
    # title it environments4.json if you want 4 environments
    with open('environments' + str(nb_obstacles) + '.json', 'w') as fo:
        # This just converts our list into a JSON and write it out
        json_object = json.dumps(envs, indent = 4)
        fo.write(json_object)
        fo.write('\n')

if __name__ == "__main__":
    main()

    # THIS FILE OUTPUTS
    '''
        [{'shape': (3, 3), 'obstacles': [(0, 1), (1, 2)]}, {'shape': (3, 3), 'obstacles': [(0, 1), (2, 2)]}, {'shape': (3, 3), 'obstacles': [(1, 2), (2, 1)]}, {'shape': (3, 3), 'obstacles': [(0, 2), (2, 2)]}]
    '''