import sys
import operator
import heapq

def BFS_alg(s0, transitions, goal_states):
    open_nodes = [[(s0,0)]]
    visited = set()
    visited.add(s0)
    cost = 0
    while len(open_nodes)>0:
        path = open_nodes.pop(0)
        n = path[-1]
        if n[0] not in visited:
            visited.add(n[0])
        if n[0] in goal_states:
            print('[FOUND_SOLUTION]: yes')
            print(f'[STATES_VISITED]: {len(visited)}')
            print(f'[PATH_LENGTH]: {len(path)}')
            print(('[TOTAL_COST]: {:.1f}').format(n[1]))
            path_out = '[PATH]: ' + str(s0)
            for i in range(1,len(path)):
                path_out+= " => " + str(path[i][0])
            for p in path:
                cost+=p[1]
            print(path_out)
            return True, n[1]
        tmp = []
        for state in transitions[n[0]]:
            if state[0] not in visited:
                tmp.append((state[0],n[1]+state[1]))        
        tmp = sorted(tmp, key = lambda x: x[0]) 
        for state in tmp:
            open_nodes.append(path + [state])    
    return False, 0

def UCS_alg(s0, transitions, goal_states, check):
    open_nodes = [(0, s0)]    
    heapq.heapify(open_nodes)
    paths = {}
    visited = set()
    visited.add(s0)
    paths[(0, s0)]=[]
    while len(open_nodes)>0:
        n = heapq.heappop(open_nodes)
        if n[1] not in visited:
            visited.add(n[1])
        if n[1] in goal_states:
            if check:
                return True, n[0]
            print('[FOUND_SOLUTION]: yes')
            print(f'[STATES_VISITED]: {len(visited)}')
            print(f'[PATH_LENGTH]: {len(paths[n])+1}')
            print(('[TOTAL_COST]: {:.1f}').format(n[0]))
            path_out = '[PATH]: ' + str(s0)
            for i in range(1,len(paths[n])):
                path_out+= " => " + str(paths[n][i][1])
            path_out+= " => " + n[1]
            print(path_out)
            return True, n[0]
        for state in transitions[n[1]]:
            if state[0] not in visited:
                paths[(n[0]+state[1],state[0])] = paths[n] + [n]
                heapq.heappush(open_nodes, (n[0]+state[1],state[0]))    
    return False, 0

def a_Star(s0, transitions, goal_states, heuristic_values):
    open_nodes = [(0, 0, s0)]
    visited = set()
    visited.add(s0)
    heapq.heapify(open_nodes)
    paths = {}
    paths[(0, 0, s0)]=[]
    costs = {}
    while len(open_nodes)>0:
        n = heapq.heappop(open_nodes)
        if n[2] not in visited:
            visited.add(n[2])
        if n[2] in goal_states:
            print('[FOUND_SOLUTION]: yes')
            print(f'[STATES_VISITED]: {len(visited)}')
            print(f'[PATH_LENGTH]: {len(paths[n])+1}')
            print(('[TOTAL_COST]: {:.1f}').format(n[1]))
            path_out = '[PATH]: ' + str(s0)
            for i in range(1,len(paths[n])):
                path_out+= " => " + str(paths[n][i][2])
            path_out+= " => " + n[2]
            print(path_out)
            return True
        for state in transitions[n[2]]:
            if state[0] not in visited:
                if (costs.get(state[0]) is not None) and (costs.get(state[0]) < (n[1]+state[1])):
                    continue 
                costs[state[0]] = n[1]+state[1]
                heapq.heappush(open_nodes, (heuristic_values[state[0]]+ n[1]+state[1], n[1]+state[1], state[0]))
                paths[(heuristic_values[state[0]]+ n[1]+state[1], n[1]+state[1], state[0])] = paths[n] + [n]
                
    return False


def optimistic_heuristic(transitions, heuristic_values, goal_states):
    results = set()
    
    for k,v in sorted(heuristic_values.items()):
        check = 'ERR'
        _, h_calc = UCS_alg(k, transitions, goal_states, True)
        if v <= h_calc:
            check = 'OK'
        results.add(check)
        print(f'[CONDITION]: [{check}] h({k}) <= h*: {round(v,1)} <= {float(h_calc):.1f}')

    conclusion = 'Heuristic is optimistic.'
    if 'ERR' in results:
        conclusion = 'Heuristic is not optimistic.'
    print(f'[CONCLUSION]: {conclusion}')
    return

def consistent_heuristic(transitions, heuristic_values):
    results = set()
    for k,v in sorted(heuristic_values.items()):
        for t in transitions[k]:
            check = 'ERR'
            if v <= (heuristic_values[t[0]] + t[1]):
                check = 'OK'
            results.add(check)
            print(f'[CONDITION]: [{check}] h({k}) <= h({t[0]}) + c: {round(v,1)} <= {round(heuristic_values[t[0]],1)} + {round(t[1],1)}')

    conclusion = 'Heuristic is consistent.'
    if 'ERR' in results:
        conclusion = 'Heuristic is not consistent.'
    print(f'[CONCLUSION]: {conclusion}')

    return

def parse_file(name, initial_state):
    temp_dict = {}
    with open(name, encoding="utf-8") as f:
        for line in f:
            line = line[:-1]
            if line[0] == '#':
                continue
            if ':' not in line:
                if initial_state != '':
                    goal_states = line.split(' ')
                else:
                    initial_state = line
            else:
                temp = line.split(' ')
                key = temp[0][:-1]
                if key not in temp_dict.keys():
                    temp_dict[key]=[]
                temp = temp[1:]
                for t in temp:
                    if ',' in t:
                        t = t.split(',')
                        temp_dict[key].append((t[0],float(t[1])))
                    else:
                        temp_dict[key] = float(t)
    
    if name == heuristic_f:
        return temp_dict
    else:
        return goal_states, initial_state, temp_dict
    


if __name__ == "__main__":
    arguments = len(sys.argv) - 1
    algorithm = ''
    state_space_f = ''
    heuristic_f = ''
    check_optimistic = 0
    check_consistent = 0

    position = 1
    while (arguments >= position):
        if sys.argv[position] == '--alg':
            position = position + 1
            algorithm = sys.argv[position]
        elif sys.argv[position] == '--ss':
            position = position + 1
            state_space_f = sys.argv[position]
        elif sys.argv[position] == '--h':
            position = position + 1
            heuristic_f = sys.argv[position]
        elif sys.argv[position] == '--check-optimistic':
            check_optimistic = 1    
        elif sys.argv[position] == '--check-consistent':
            check_consistent = 1
        
        position = position + 1
    
    initial_state=''
    goal_states = []
    transitions = {}
    heuristic_values = {}

    if state_space_f != '':
        goal_states, initial_state, transitions = parse_file(state_space_f, initial_state)
    if heuristic_f != '':
        heuristic_values = parse_file(heuristic_f, initial_state)
    
    if(algorithm=='ucs'):
        print(f'# {algorithm.upper()}')
        found, _ = UCS_alg(initial_state,transitions, goal_states, False)
        if not found:
            print('[FOUND_SOLUTION]: no')

    if(algorithm=='bfs'):
        print(f'# {algorithm.upper()}')
        found, _ = BFS_alg(initial_state,transitions, goal_states)
        if not found:
            print('[FOUND_SOLUTION]: no')
    if(algorithm=="astar"):
        print(f'# A-STAR {heuristic_f}')
        found = a_Star(initial_state,transitions, goal_states, heuristic_values)
        if not found:
            print('[FOUND_SOLUTION]: no')

    if check_optimistic:
        print(f'# HEURISTIC-OPTIMISTIC {heuristic_f}')
        optimistic_heuristic(transitions, heuristic_values, goal_states)

    if check_consistent:
        print(f'# HEURISTIC-CONSISTENT {heuristic_f}')
        consistent_heuristic(transitions, heuristic_values)

