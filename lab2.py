import sys

def resolution_alg(clauses, goal):
    SoS = {}
    number = len(clauses.keys())+1
    used_clauses = clauses.copy()
    new = {}
    parent = {}
    all_clauses = clauses.copy()
    if not bool(clauses):
        print(f'1. {goal}')
        print(f'2. ~{goal}')
        print(f'NIL (1, 2)')
        return True 

    i = max(clauses.values())+1
    #convert goal
    if ' v ' in goal:
        goal = goal.split(' v ')
        for g in goal:
            SoS['~' + g.strip()] = i
            i+=1
    else:
        SoS['~' + goal]=i
        i+=1

    used_clauses, SoS = deletion_strategy(used_clauses,SoS)
    used_clauses.update(SoS)

    while True:
        for c1 in used_clauses:
            for c2 in SoS:
                #paziti da nema ponavljanja
                if (used_clauses[c1], SoS[c2]) in parent.values():
                    continue
                if c1==c2:
                    continue
                resolvents = resolve(c1, c2)

                if 'NIL' in resolvents:
                    parent[i] = (used_clauses[c1], SoS[c2])
                    x = [i]
                    print_set = set()
                    print_set.add(i)
                    print_set.add(used_clauses[c1])
                    print_set.add(SoS[c2])
                    while len(x):
                        if x[0] in parent.keys():
                            print_set.add(parent[x[0]][0])
                            print_set.add(parent[x[0]][1])
                            if x[0] in parent.keys():
                                x.append(parent[x[0]][0])
                                x.append(parent[x[0]][1])
                        x.pop(0)

                    for x,y in all_clauses.items():
                        if y in print_set:
                            if y in parent.keys():
                                print(f'{y}. {x} {parent[y]}')
                            else:
                                print(f'{y}. {x}')
                            if(y==number):
                                print('==================')
                    print('==================')
                    print(f'NIL ({used_clauses[c1]}, {SoS[c2]})')

                    return True

                if len(resolvents)==1:
                    new[resolvents[0]] = i
                    parent[i] = (used_clauses[c1], SoS[c2])
                    i+=1

        if used_clauses.keys() <= new.keys() or not bool(new):
            return False

        all_clauses.update(used_clauses)
        all_clauses.update(new)
        used_clauses, new = deletion_strategy(used_clauses,new)
        SoS = new.copy()
        new = {}
        used_clauses.update(SoS)
    
    return False

def resolve(c1, c2):
    c1 = c1.split(' v ')
    c2 = c2.split(' v ')
    c1 = [i.strip() for i in c1]
    c2 = [i.strip() for i in c2]
    resolvents = []
    for i in c1:
        for j in c2:
            if (i.strip() ==  ('~' + j.strip())) or (j.strip() ==  ('~' + i.strip())):
                if(len(c2) == 1 and len(c1)==1):
                    return ['NIL']
                tmp = c1.copy() + c2
                tmp.remove(i)
                tmp.remove(j)
                if len(tmp) > 1:
                    tmp = ' v '.join(tmp)
                    resolvents.append(tmp)
                else:
                    resolvents.extend(tmp)
    return resolvents

def deletion_strategy(d1, d2):
    remove = set()
    l1 = [(' ' + k + ' ') for k in d1.keys()]
    l2 = [(' ' + k + ' ') for k in d2.keys()]
    for k1 in l1:
        for k2 in l2:
            if ((k2) in k1) and ('~'+k2) not in k1:
                remove.add(k1.strip())
            if (k1) in k2 and ('~'+k1) not in k2:
                remove.add(k2.strip())
    for k in remove:
        if k in d1.keys():
            del d1[k]
        else:
            del d2[k]

    return d1, d2

def parse_file(name, g):
    clauses = {}
    commands = []
    goal = ''
    with open(name, encoding="utf-8") as f:
        for i,line in enumerate(f):
            line = line[:-1]
            if line[0] == '#':
                continue
            if g:
                clauses[line.lower()] = i+1 
            else:
                commands.append((line[0:-2],line[-1:]))                
        if g:
            goal = max(clauses, key=lambda k: clauses[k])
            del clauses[goal]
            return clauses, goal
        
        return commands, goal
        

if __name__ == "__main__":
    clauses = {}
    commands = []
    goal = ''

    if sys.argv[1] == 'resolution':
        clauses, goal = parse_file(sys.argv[2], True)
        res = resolution_alg(clauses, goal)
        if res:
            print(f'[CONCLUSION]: {goal} is true')
        else:
            print(f'[CONCLUSION]: {goal} is unknown')

    if sys.argv[1] == 'cooking':
        clauses, goal = parse_file(sys.argv[2], True)
        clauses[goal] = max(clauses.values())+1 
        commands, _ = parse_file(sys.argv[3], False)
        print('Constructed with knowledge:')
        for k in clauses.keys():
            print(k)

        for c in commands:
            print(f'\nUser\'s command: {c[0]} {c[1]}')
            if c[1] == '?':
                res = resolution_alg(clauses, c[0].lower())
                if res:
                    print(f'[CONCLUSION]: {c[0].lower()} is true')
                else:
                    print(f'[CONCLUSION]: {c[0].lower()} is unknown')
            elif c[1] == '+':
                i = max(clauses.values())+1
                clauses[c[0].lower()] = i
                print(f'added {c[0]}')
            elif c[1] == '-':
                del clauses[c[0].lower()]
                print(f'removed {c[0]}')
