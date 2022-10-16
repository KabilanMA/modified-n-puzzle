import copy
import random

def printPretty(array2D):
    for i in range(len(array2D)):
        for j in range(len(array2D[i])):
            print(str(array2D[i][j]), end="\t")
        print()
    print()

def accept(filename):
    with open(filename, 'r') as f:
        output = []
        for row in f:
            output.append(str(row.strip()).split())
    return output

            
def save(output, sol_found, output_file_name):
    if sol_found:
        temp = []
        for move in output:
            temp.append(str((int(move[0]), str(move[1]))))
        s = ", ".join(temp)
        print(s)
        with open(output_file_name, 'w') as f:
            f.write(s)
    else:
        with open(output_file_name, 'w') as f:
            f.write(output)

def evalH(start, goal, heu='manhattan', empty='-'):
    def evalH1(start, goal, empty):
        #misplaced tiles
        # move only to the adjacent slot with only no diagonal movement
        h = 0
        for i in range(len(start)):
            for j in range(len(start)):
                if start[i][j] != goal[i][j] and start[i][j] != empty:
                    h+=1
        return h
    
    def evalH2(start, goal, empty):
        # Total Manhattan distance
        h = 0
        for i in range(len(start)):
            for j in range(len(start)):
                start_val = start[i][j]
                if start_val != empty:
                    got = False
                    for gi in range(len(goal)):
                        for gj in range(len(goal)):
                            if start_val == goal[gi][gj]:
                                h += abs(gi - i) + abs(gj - j)
                                got = True
                                break 
                        if got:
                            break
        return h
    
    if heu == 'manhattan':
        return evalH2(start,goal, empty)
    else:
        return evalH1(start, goal, empty)
    

def evalF(start_node, goal, heu='manhattan'):
    """f = h + g
    
    Keyword arguments:
    start_node -- start_node is a Node object
    goal -- goal is a List
    """
    
    f = evalH(start_node.data, goal, heu) + start_node.level
    return f

# @jit(target_backend='cuda') 
def belongs(node, list_of_node, heu='misplaced'):
    for single_node in list_of_node:
        if evalH(node.data, single_node.data, heu) == 0:
            return True
    return False


class Node:

    def __init__(self, data, level, f, parent=None, movement=None):
        #level=g, f = g+h
        self.parent = parent
        self.data = data
        self.level = level
        self.f = f
        self.movement = movement

    def getChildren(self):
        empty_slots = self.findEmpty(self.data)
        children = []
        # print(empty_slots)
        for empty_slot in empty_slots:
            x,y = empty_slot
                # LEFT      RIGHT    DOWN    UP
            moves = [[x, y+1],[x, y-1],[x-1, y],[x+1, y]]
            for i, move in enumerate(moves):
                # print(move)
                child = self.move(self.data, x, y, move)
                movement = ['','-']
                if i == 0:
                    movement[0] = "Left"
                if i == 1:
                    movement[0] = "Right"
                if i == 2:
                    movement[0] = "Down"
                if i == 3:
                    movement[0] = "Up"
                if child:
                    val = self.data[move[0]][move[1]]
                    movement[1] = val
                    child_node = Node(child, self.level+1, 0, self, movement)
                    children.append(child_node)
        
        # print(children)
        return children

    def move(self, struct, x1, y1, next_move):
        try:
            if ((next_move[0] >=0 and next_move[0] < len(self.data)) and (next_move[1]>=0 and next_move[1]<len(self.data))):
                temp_struct = copy.deepcopy(struct)
                storage = temp_struct[next_move[0]][next_move[1]]
                temp_struct[next_move[0]][next_move[1]] = temp_struct[x1][y1]
                temp_struct[x1][y1] = storage
                # print(temp_struct)
                # print(storage)
                return temp_struct
            else:
                # print("Cannot move to the new location")
                return None
        except IndexError:
            return None
        
    def findEmpty(self, struct=[], x='-'):
        if not struct:
            struct = self.data
        output = []
        for i in range(0, len(self.data)):
            for j in range(0, len(self.data)):
                if struct[i][j] == x:
                    output.append((i,j))
        return output

def userFileInputProcess(heu='manhattan'):
    start = accept(input("Enter the Start Configuration File Name(with .txt extension): "))
    goal = accept(input("Enter the Goal Configuration File Name(with .txt extension): "))
    output_file_name = input('Enter output File Name: ')
           
    opened = []
    closed = []
    start_node = Node(start, 0, 0)
    start_node.f = evalF(start_node, goal, heu)
    opened.append(start_node)
    output_data = []
    count = 0
    sol_found = False
    goal_node = start_node
    while opened:
        count += 1
        if heu=='manhattan' and count>1500:
            return []
        if heu=='misplaced' and count>2500:
            return []
             
        opened.sort(key=lambda x:x.f, reverse=True)
        current_node = opened.pop()
        closed.append(current_node)
        if(evalH(current_node.data, goal, heu) == 0):
            print("Success after {} expand".format(count))
            goal_node = current_node
            sol_found = True
            break
        
        best_child = None
        IN=False
        
        for child in current_node.getChildren():
            
            isChildBelongsTo = belongs(child, (opened+closed))
            child.f = evalF(child, goal, heu)
            if not isChildBelongsTo:
                opened.append(child)
            
            if not best_child:
                IN = not(isChildBelongsTo)
                best_child = child
                
            elif child.f < best_child.f and belongs(child, closed):
                IN = not (isChildBelongsTo)
                best_child = child

        if not IN:
            opened.append(best_child)
    else:
        print("Faild to find the solution")

    
    if sol_found:
        val = goal_node.movement
        while val:
            output_data.append((val[1], val[0]))
            
            goal_node = goal_node.parent
            val = goal_node.movement
        output_data.reverse() 
        s = copy.deepcopy(output_data)
    else:
        s = "Failed to find the solution"

    save(s, sol_found, output_file_name)


def randomEvaluatorProcess(iteration=100):
    
    def getRandom(n):        
        puzzle = [['-' for j in range(n)] for a in range(n)]
        
        values = [str(x) for x in range(1, n**2 - 1)]

        positions = []
        for q in range(n):
            for w in range(n):
                positions.append((q,w))
        m = len(values)
        for j in range(m):
            pop_val = values.pop(random.randrange(len(values)))
            pos = positions.pop(random.randrange(len(positions)))
            puzzle[pos[0]][pos[1]] = pop_val
        
        return puzzle
    
    def getOutput(start, goal, heu):
        opened = []
        closed = []
        start_node = Node(start, 0, 0)
        start_node.f = evalF(start_node, goal, heu)
        opened.append(start_node)
        output_data = []
        count = 0
        sol_found = False
        goal_node = start_node
        while opened:
            count += 1 
            if heu=='manhattan' and count>1500:
                return []
            if heu=='misplaced' and count>2500:
                return []
            
            opened.sort(key=lambda x:x.f, reverse=True)
            current_node = opened.pop()
            closed.append(current_node)

            if(evalH(current_node.data, goal, heu) == 0):
                print("Success after {} expand".format(count))
                goal_node = current_node
                sol_found = True
                break
            
            best_child = None
            IN=False
            
            for child in current_node.getChildren():
                
                isChildBelongsTo = belongs(child, (opened+closed))
                child.f = evalF(child, goal, heu)
                if not isChildBelongsTo:
                    opened.append(child)
                    
                if not best_child:
                    IN = not(isChildBelongsTo)
                    best_child = child
                    
                elif child.f < best_child.f and belongs(child, closed):
                    IN = not (isChildBelongsTo)
                    best_child = child
            
            if not IN:
                opened.append(best_child)
        else:
            print("Faild to find the solution")
    
        
        if sol_found:
            val = goal_node.movement
            while val:
                output_data.append((val[1], val[0]))
                goal_node = goal_node.parent
                val = goal_node.movement
            output_data.reverse()
            return output_data
        else:
            return []
    
    def rearranch(array2d, iteration=random.randrange(20,30)):
        for _ in range(iteration):
            
            empty_slots = []
            for temp_i in range(len(array2d)):
                for temp_j in range(len(array2d)):
                    if array2d[temp_i][temp_j] == '-':
                        empty_slots.append((temp_i,temp_j))
                        
            for empty_slot in empty_slots:
                x,y = empty_slot
                # LEFT      RIGHT    DOWN    UP
                moves = [[x, y+1],[x, y-1],[x-1, y],[x+1, y]]
                positions = []
                for move in moves:
                    if ((move[0] >=0 and move[0] < len(array2d)) and (move[1]>=0 and move[1]<len(array2d))):
                        positions.append(move)
        
                movei = positions[random.randrange(len(positions))]
                array2d[x][y] = array2d[movei[0]][movei[1]]
                array2d[movei[0]][movei[1]] = '-'
                
                   
    output = []
    for i in range(iteration):
        
        n = random.randint(5,20)
        # n = 25
        start = getRandom(n)
        # goal = getRandom(n)
        goal = copy.deepcopy(start)
        rearranch(start)
        
        output_manhattan = getOutput(start, goal, 'manhattan')
        manhattan = 'inf' if len(output_manhattan) == 0 else str(len(output_manhattan))
        
        if manhattan !='inf':
          output_misplaced = getOutput(start, goal, 'misplaced')
          misplaced = 'inf' if len(output_misplaced) == 0 else str(len(output_misplaced))
          print((str(misplaced) + '\t' + str(manhattan)))
          output.append((str(misplaced) + '     -     ' + str(manhattan)))

    writeDoc = '\n'.join(output)
    writeDoc = 'misplaced   manhattan\n' + writeDoc
    
    with open('random.txt','w') as f:
        f.write(writeDoc)
        
        
# userFileInputProcess()       
# randomEvaluatorProcess(iteration=1)            
while True:
    selection = input("\nSelect the option of operation using the integer value.\n1.Solve the n-puzzle problem in from the file.\n2.Solve the n-puzzle problem for random generator.\nAny other key to exit the program.\n\t: ")
    if(selection == '1'):
        userFileInputProcess()
    elif selection == '2':
        try:
            randomEvaluatorProcess(int(input("Enter the number of problems to solve(Enter only integer). Result will be saved in random.txt file: ")))
        except Exception as e:
            print("Only enter integer number")
    else:
        break
