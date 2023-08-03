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
    # enumerate all length 1 step
    for coord in remain_zeros:
        x , y = coord[0] , coord[1]
        move = [(x,y), 1 , 1] # assume only move 1 step , so dir is given a random number 1
        moves.append(move)

    for coord in remain_zeros:
        for len in [2 , 3]:
            for dir in [1 , 2 , 3 , 4 , 5 ,6]:
                x , y = coord[0] , coord[1]
                move = [(x,y), len , dir]
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

# # Scoring metrics
def DoomWinorLose(after_mapStat):
    num_zeros = np.count_nonzero(after_mapStat == 0)
    if num_zeros == 1: 
        return -10000
    elif num_zeros == 0:
        return 10000
    else:
        return 0

def ScatteredNode(after_mapStat):
    after_zero_coords = checkRemainMove(after_mapStat)
    lonely_node_count = 0
    pair_node_count = 0
    for coord in after_zero_coords:
        x , y = coord[0] , coord[1]
        neighbor = 0
        for dir in [1 , 2 , 3 , 4 , 5 , 6]:
            neigh_x , neigh_y = Next_Node(x , y , dir)
            if neigh_x < 0 or neigh_x > 11 or neigh_y < 0 or neigh_y > 11:
                continue
            if after_mapStat[neigh_x][neigh_y] == 0:
                neighbor += 1
                if neighbor > 1 :
                    break

        if neighbor == 0 : lonely_node_count += 1
        if neighbor == 1 : pair_node_count += 1
        

    if len(after_zero_coords) != (lonely_node_count + pair_node_count) : 
        # assert board contains only OO or O like segments
        return 0

    assert (pair_node_count%2) == 0

    if pair_node_count == 0 : # which means only lonely nodes are on the board
        if (lonely_node_count%2) == 1:
            return -9000
        else:
            return 9000
    elif lonely_node_count == 0 : # which means only OO are on the board
        if (pair_node_count/2) == 2:
            return -9000
    else :
        pass
    
    return 0

def Total_Score(after_mapStat):
    return DoomWinorLose(after_mapStat) + \
    ScatteredNode(after_mapStat)

# # Minmax with alpha beta pruning
class Minmax():
    def __init__(self , queryState , max_depth = 5):
        self.queryStat = queryState
        self.max_depth = max_depth
    
    def virtual_move(self , turn , state , action): 
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
    
    def best_action(self , is_max_player , cur_mapStat , alpha , beta , depth):
        abs_score = Total_Score(cur_mapStat)
        if (depth == self.max_depth) or abs(abs_score) >= 10000 :
            signed_score = abs_score if is_max_player == 1 else -abs_score
            return None , signed_score

        remain_moves = enumerate_all_moves(cur_mapStat)
        if is_max_player == 1:
            best_value = float('-inf')
            best_action = None
            for move in remain_moves:
                new_mapStat = self.virtual_move(1 , cur_mapStat , move)
                _ , value = self.best_action(2 , new_mapStat , alpha , beta , depth + 1)
                if value > best_value:
                    best_value = value
                    best_action = move
            
                alpha = max(alpha, value)
                if value >= beta:
                    break
            # print(f"Player {1} , In depth {depth} , node{id_} , best score is {best_value} , choose best action {best_action}")
            return best_action , best_value
        
        else :
            best_value = float('inf')
            best_action = None
            for move in remain_moves:
                new_mapStat = self.virtual_move(2 , cur_mapStat , move)
                _ , value = self.best_action(1 , new_mapStat , alpha , beta , depth + 1)
                if value < best_value:
                    best_value = value
                    best_action = move

                beta = min(beta , value)
                if value <= alpha:
                    break
            # print(f"Player {2} , In depth {depth} , node{id_} , best score is {best_value} , choose best action {best_action}")
            return best_action , best_value

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
    # # Minmax Algorithm
    num_zeros = 144 - np.count_nonzero(mapStat)
    if num_zeros <= 11:
        selector = Minmax(mapStat , max_depth = 5)
        step , _ = selector.best_action(1 , mapStat , float('-inf') , float('inf') , 0)
    else :
        moves = enumerate_all_moves(mapStat)
        step = moves[np.random.randint(0 , len(moves))]
    if step == None:
        for x , row in enumerate(mapStat):
            for y , col in enumerate(row):
                if col == 0:
                    step = [(x,y), 1 , 1]
                    return step

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
