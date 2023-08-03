import STcpClient_1 as STcpClient
import numpy as np
import random
from copy import deepcopy
from collections import defaultdict

'''
    input position (x,y) and direction
    output next node position on this direction
'''
# # Utility function
def Next_Node(pos_x,pos_y,direction):
    if pos_y%2==1:
        if direction==1:
            return pos_x,pos_y-1
        elif direction==2:
            return pos_x+1,pos_y-1
        elif direction==3:
            return pos_x-1,pos_y
        elif direction==4:
            return pos_x+1,pos_y
        elif direction==5:
            return pos_x,pos_y+1
        elif direction==6:
            return pos_x+1,pos_y+1
    else:
        if direction==1:
            return pos_x-1,pos_y-1
        elif direction==2:
            return pos_x,pos_y-1
        elif direction==3:
            return pos_x-1,pos_y
        elif direction==4:
            return pos_x+1,pos_y
        elif direction==5:
            return pos_x-1,pos_y+1
        elif direction==6:
            return pos_x,pos_y+1

def checkRemainMove(mapStat):
    free_region = (mapStat == 0)
    temp = []
    for i in range(len(free_region)):
        for j in range(len(free_region[0])):
            if(free_region[i][j] == True):
                temp.append([i,j])
    return temp

def checkMoveValidation(mapStat, move):
    # move =[move position, move # of step, move direction]
    [pos_x, pos_y] = move[0]  # expected [x,y]
    # if mapStat[pos_x][pos_y] != 0:
    #     return False
    next_x, next_y=pos_x,pos_y
    for i in range(move[1] - 1): 
        [next_x, next_y]=Next_Node(next_x,next_y,move[2])
        if(next_x < 0 or next_x > 11 or next_y < 0 or next_y > 11 or mapStat[next_x][next_y]!=0):
            return False
    return True

def enumerate_all_moves(mapStat):
    remain_zeros = checkRemainMove(mapStat)
    # print(remain_zeros)
    moves = []
    # enumerate all length 1 step(only step on )
    for coord in remain_zeros:
        x , y = coord[0] , coord[1]
        move = [(x,y), 1 , 1] # assume only move 1 step , so dir is given a random number 1
        moves.append(move)

    for coord in remain_zeros:
        for len in [2 , 3]:
            for dir in [1 , 2 , 3 , 4 , 5 ,6]:
                x , y = coord[0] , coord[1]
                move = [(x,y), len , dir] # assume only move 1 step , so dir is given a random number 1
                if checkMoveValidation(mapStat, move) == True:
                    moves.append(move)
    return moves

def virtual_move(state , turn , action): # get the state when rollout occurs , because it is in rollout so "turn" needs to be passed in 
    new_state = deepcopy(state)
    [move_pos_x, move_pos_y] = action[0]  # expected [x,y]
    steps = action[1]  # how many step
    move_dir = action[2]  # 1~6
    next_x = move_pos_x
    next_y = move_pos_y
    new_state[next_x][next_y] = turn
    for i in range(steps - 1): 
        [next_x, next_y] = Next_Node(next_x,next_y,move_dir)
        new_state[next_x][next_y] = turn
    return new_state

# # Node Class , representing a state in the middle of the Game
class Node():
    def __init__(self, state , turn , parent , parent_action):
        self.state = state
        self.turn = turn
        self.enemy_turn = 2 if self.turn == 1 else 1
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.number_of_visits = 0
        self.win = 0
        # global id_
        # self.id_ = id_
        # id_ += 1

    def UCB(self , c_param): # calculate the UCB value of "self"
        if self.number_of_visits == 0:
            return 1000000
        w = None
        n = self.number_of_visits
        if self.turn == 1: # if "self" is the turn of player1 , since we only store win time of player1
            w = self.win
        else : # n - self.win == player2 win time
            w = n - self.win
            
        parent_simulation = self.parent.number_of_visits
        return w / n + c_param * np.sqrt(np.log(parent_simulation) / n)
        
    def best_child(self, c_param): # Think of "self" as parent node , to choose the best child node using their UCB values
        choices_weights = [child.UCB(c_param) for child in self.children]
        return self.children[np.argmax(choices_weights)]
    
    def expand(self): # expand "self" , to append all the children (corresponds to all the move "self" can do) in self.children
        all_possible_moves = enumerate_all_moves(self.state)
        for action in all_possible_moves:
            new_state = self.expand_move(action)
            # print('create child ' , new_state)
            child_node = Node(
                new_state , self.enemy_turn , parent=self , parent_action=action) # new state is for next turn , for the enemy
            self.children.append(child_node)
        

    def expand_move(self , action): # get the state when "self" pick a move
        new_state = deepcopy(self.state)
        [move_pos_x, move_pos_y] = action[0]  # expected [x,y]
        steps = action[1]  # how many step
        move_dir = action[2]  # 1~6
        next_x = move_pos_x
        next_y = move_pos_y
        new_state[next_x][next_y] = self.turn    # because it is "self" takes a move and leads to a new state
        for i in range(steps - 1): 
            [next_x, next_y]=Next_Node(next_x,next_y,move_dir)
            new_state[next_x][next_y] = self.turn  # because it is "self" takes a move and leads to a new state
        return new_state
        

    def virtual_move(self , state , turn , action): # get the state when rollout occurs , because it is in rollout so "turn" needs to be passed in 
        new_state = deepcopy(state)
        [move_pos_x, move_pos_y] = action[0]  # expected [x,y]
        steps = action[1]  # how many step
        move_dir = action[2]  # 1~6
        next_x = move_pos_x
        next_y = move_pos_y
        new_state[next_x][next_y] = turn
        for i in range(steps - 1): 
            [next_x, next_y]=Next_Node(next_x,next_y,move_dir)
            new_state[next_x][next_y] = turn
        return new_state
    
    def is_terminated(self , state): # check if the Board Game is finished
        return not (state==0).any()
    
    def is_leaf(self): # check if "self" is leaf node , i.e. no children moves
        return (len(self.children) == 0)
    
    def not_visited(self): # check if "self" has been visited before
        return (self.number_of_visits == 0)
    
    def backpropagate(self , result): # from "self" , backpropagate till the root node , and root node's parent is None
        self.number_of_visits += 1
        if result == 1: # store player1 's wining time , nomatter what turn of this node
            self.win += 1
        # print(len_ , self.id_ , self.win , self.number_of_visits)
        if self.parent != None:
            self.parent.backpropagate(result)

    def rollout(self): # from "self" , do "rollout" until the Board Game ends
        current_rollout_state = deepcopy(self.state)
        current_turn = self.turn
        # print(current_rollout_state)
        while not self.is_terminated(current_rollout_state):
            possible_moves = enumerate_all_moves(current_rollout_state)
            action = self.rollout_policy(possible_moves)
            current_rollout_state = self.virtual_move(current_rollout_state , current_turn , action)
            current_turn = 2 if current_turn == 1 else 1 # go to next state , which is for the opponent of the current turn

        # return who makes the last 2nd move , i.e. who is the game final winner
        if current_turn == 1 :
            # if current turn == 1 , that means last move is 2(since update player ==> identify Game terminated) , so the winner is 1
            return 1
        else :
            # if current turn == 2 , that means last move is 1(since update player ==> identify Game terminated) , so the winner is 2
            return 2
        
    def rollout_policy(self , possible_moves): # how to pick a move in "rollout" stage , default is random chosen
        # print(np.random.randint(len(possible_moves)))
        return possible_moves[np.random.randint(0 , len(possible_moves))]
    
# # MCTS with random rollout move    
class MCTS():
    def __init__(self , turn , iterLimit , queryState , c_param = 1.4):
        self.turn = turn
        self.iterLimit = iterLimit
        self.queryState = queryState
        self.c_param = c_param
        self.root = Node(self.queryState , self.turn , parent=None , parent_action=None)
    
    def tree_policy(self):
        current_node = self.root
        while True:
            next_layer_node = current_node.best_child(self.c_param)
            # print(next_layer_node.is_leaf() , next_layer_node.not_visited())
            if next_layer_node.is_leaf():
                if next_layer_node.not_visited():
                    return next_layer_node
                else:
                    if not next_layer_node.is_terminated(next_layer_node.state):
                        next_layer_node.expand()
                        target_node = next_layer_node.children[np.random.randint(0 , len(next_layer_node.children))]
                        return target_node
                    else:
                        return None
            current_node = next_layer_node
    
    def best_action(self):
        for i in range(self.iterLimit):
            if i == 0: # if in initial state , just expand since rollout using state of root is meaningless
                self.root.expand()
            best_unvisited_leaf = self.tree_policy()
            if best_unvisited_leaf == None:
                break
            result = best_unvisited_leaf.rollout()
            best_unvisited_leaf.backpropagate(result)

        # Get the children of root of highest win rate , i.e. the one with best action  
        win_rate = [ child.win / child.number_of_visits if child.number_of_visits!=0 else 0 for child in self.root.children]
        return self.root.children[np.argmax(win_rate)].parent_action

'''
    輪到此程式移動棋子
    mapStat : 棋盤狀態(list of list), 為 12*12矩陣, 0=可移動區域, -1=障礙, 1~2為玩家1~2佔領區域
    gameStat : 棋盤歷史順序
    return Step
    Step : 3 elements, [(x,y), l, dir]
            x, y 表示要畫線起始座標
            l = 線條長度(1~3)
            dir = 方向(1~6),對應方向如下圖所示
              1  2
            3  x  4
              5  6
'''

def Getstep(mapStat, gameStat):
    step = None
    # # MCTS Algorithm
    selector = MCTS(1 , iterLimit = 550 , queryState = mapStat , c_param = 1.4)
    step = selector.best_action()
    return step

# start game
print('start game')
while (True):

    (end_program, id_package, mapStat, gameStat) = STcpClient.GetBoard()
    if end_program:
        STcpClient._StopConnect()
        break
    
    decision_step = Getstep(mapStat, gameStat)
    
    STcpClient.SendStep(id_package, decision_step)
