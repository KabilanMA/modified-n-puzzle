import random
import copy
import sys

start_file_name = str(sys.argv[1].strip())
goal_file_name = str(sys.argv[2].strip())

print(start_file_name, goal_file_name)

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

            
class Node:
    
    def __init__(self, data, parent, level):
        self.data = data
        self.parent = parent
        self.level = level # level = g
    
    def findEmpty(self, struct=[], x='-'):
        if not struct:
            struct = self.data
        output = []
        for i in range(0, len(self.data)):
            for j in range(0, len(self.data)):
                if struct[i][j] == x:
                    output.append((i,j))
        return output
            
    def getChildren(self):
        empty_slots = self.findEmpty(self.data)
        children = []
        
        for empty_slot in empty_slots:
            x,y = empty_slot
                # LEFT      RIGHT    DOWN    UP
            moves = [[x, y+1],[x, y-1],[x-1, y],[x+1, y]]
            for i, move in enumerate(moves):
                # print(move)
                child = self.move(self.data, x, y, move)

                if child:
                    child_node = Node(child, self, self.level+1)
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
        
    def _evalH(self, goal, heu='manhattan', empty='-'):
        
        def evalH1(goal, empty):
            #misplaced tiles
            # move only to the adjacent slot with only no diagonal movement
            h = 0
            for i in range(len(self.data)):
                for j in range(len(self.data)):
                    if self.data[i][j] != goal[i][j] and self.data[i][j] != empty:
                        h+=1
            return h

        def evalH2(goal, empty):
            # Total Manhattan distance
            h = 0
            for i in range(len(self.data)):
                for j in range(len(self.data)):
                    start_val = self.data[i][j]
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
            self.h =  evalH2(goal, empty)
        else:
            self.h = evalH1(goal, empty)
    
    def evalF(self, goal, heu, empty='-'):
        self._evalH(goal, heu, empty='-')
        self.f = self.level + self.h
        return True
    
def belongs(checkNode, nodeArray):
    for inState in nodeArray:
        if inState.data == checkNode.data:
            return True, inState
    
    return False, None

 
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
    
    def rearrange(array2d, iteration=0):
        iteration = random.randint(10,20)
        print("Number re-arrangements: {}".format(2*iteration))
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
                    
    def getOutput(start, goal, heu):
        OPEN = []
        CLOSED = []
        rootNode = Node(start, None, 0)
        rootNode.evalF(goal, heu)
        OPEN.append(rootNode)
        count = 0
        while OPEN:
            count +=1
            OPEN.sort(key=lambda x:x.f, reverse=False)
            current_state = OPEN.pop(0)
            
            if current_state.data == goal:
                print("Success after {} expand - {}".format(count-1, heu))
                return count -1

            CLOSED.append(current_state)
            
            for nextState in current_state.getChildren():
                if belongs(nextState, CLOSED)[0]:
                    continue
                
                if not (belongs(nextState, OPEN)[0]):
                    nextState.evalF(goal, heu)
                    OPEN.append(nextState)
                else:
                    openNode = belongs(nextState, OPEN)[1]
                    if nextState.level < openNode.level:
                        openNode.level = openNode.level
                        openNode.parent = nextState.parent
        else:
            return 0
        
        
    output = []
    for i in range(iteration):
        
        n = random.randint(5,20)
        start = getRandom(n)
        # goal = getRandom(n)
        goal = copy.deepcopy(start)
        rearrange(start)
        
        node_expanded_misplaced = getOutput(start, goal, 'misplaced')
        
        if node_expanded_misplaced != 0:
          node_expanded_manhattan = getOutput(start, goal, 'manhattan')
          print((str(node_expanded_misplaced) + '\t' + str(node_expanded_manhattan)))
          output.append(("   "+str(node_expanded_misplaced) + '     -  ' + str(node_expanded_manhattan)))

    writeDoc = '\n'.join(output)
    writeDoc = 'misplaced\tmanhattan\n' + writeDoc
    
    with open('random.txt','w') as f:
        f.write(writeDoc)

def userFileInputProcess(start=None, goal = None, heu='manhattan'):
    
    if (start==None or goal==None):
        start = accept(input("Enter the Start Configuration File Name(with .txt extension): "))
        goal = accept(input("Enter the Goal Configuration File Name(with .txt extension): "))
    else:
        start = accept(start)
        goal = accept(goal)
    
    output_file_name = 'Sample_Output.txt'
    
    
    def getMove(fromState, toState, empty='-'):
        n = len(fromState.data)
        temp = ''
        for i in range(n):
            for j in range(n):
                if fromState.data[i][j] != toState.data[i][j] and fromState.data[i][j] != empty:
                    
                    if i-1>=0 and fromState.data[i][j] == toState.data[i-1][j]:
                        temp = '({}, {})'.format(int(fromState.data[i][j]), "up")
                    elif i+1 <= n-1 and fromState.data[i][j] == toState.data[i+1][j]:
                        temp = "({}, {})".format(int(fromState.data[i][j]), "down")
                    elif j-1>=0 and fromState.data[i][j] == toState.data[i][j-1]:
                        temp = "({}, {})".format(int(fromState.data[i][j]), "left")
                    elif j+1 <= n-1 and fromState.data[i][j] == toState.data[i][j+1]:
                        temp = "({}, {})".format(int(fromState.data[i][j]), "right")
                    break
        return str(temp)
                        
                    
    def backTrack(node):
        path = []
        while node.parent:
            path.append(getMove(node.parent, node))
            node = node.parent
        path.reverse()
        return path 
    
    
    def getOutput():       
        OPEN = []
        CLOSED = []
        rootNode = Node(start, None, 0)
        rootNode.evalF(goal, heu)
        OPEN.append(rootNode)
        count = 0
        while OPEN:
            count +=1
            OPEN.sort(key=lambda x:x.f, reverse=False)
            current_state = OPEN.pop(0)
            
            if current_state.data == goal:
                print("Success after {} expand - {}".format(count-1, heu))
                return backTrack(current_state)

            CLOSED.append(current_state)
            
            for nextState in current_state.getChildren():
                if belongs(nextState, CLOSED)[0]:
                    continue
                
                if not (belongs(nextState, OPEN)[0]):
                    nextState.evalF(goal, heu)
                    OPEN.append(nextState)
                else:
                    openNode = belongs(nextState, OPEN)[1]
                    if nextState.level < openNode.level:
                        openNode.level = openNode.level
                        openNode.parent = nextState.parent
        else:
            return []
        
    result = getOutput()
    if len(result)!=0:
        s = ', '.join(result)
        print(s)
        with open(output_file_name, 'w') as f:
            f.write(s)
    else:
        s = "Failed"
        with open(output_file_name, 'w') as f:
            f.write(s)
       
           
# while True:
#     selection = input("\nSelect the option of operation using the integer value.\n1.Solve the n-puzzle problem in from the file.\n2.Solve the n-puzzle problem for random generator.\nAny other key to exit the program.\n\t: ")
#     if(selection == '1'):
#         userFileInputProcess()
#     elif selection == '2':
#         try:
#             randomEvaluatorProcess(int(input("Enter the number of problems to solve(Enter only integer). Result will be saved in random.txt file: ")))
#         except Exception as e:
#             print("Only enter integer number")
#     else:
#         break

userFileInputProcess(start = start_file_name, goal = goal_file_name)