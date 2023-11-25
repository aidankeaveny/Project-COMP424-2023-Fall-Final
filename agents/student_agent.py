# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
import numpy as np
from copy import deepcopy
import time


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        
        # Some simple code to help you with timing. Consider checking 
        # time_taken during your search and breaking with the best answer
        # so far when it nears 2 seconds.
        start_time = time.time()
        r, c = my_pos
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        opposites = {0: 2, 1: 3, 2: 0, 3: 1}
        # this gets possible directions for moving
        def get_allowed_dirs_move(r,c, board, opp_pos):
            allowed_dirs = [ d                                
                for d in range(0,4)                           # 4 moves possible
                if not board[r,c,d] and                 # chess_board True means wall
                not opp_pos == (r+moves[d][0],c+moves[d][1])] # cannot move through Adversary
            return allowed_dirs
        #this gets possible directions for placing a wall
        def get_allowed_dirs_place(r,c,board):
            allowed_dirs = [ d                                
                for d in range(0,4)
                if not board[r,c,d]]
            return allowed_dirs
        # Build a list of the moves we can make
        # list of (pos, dir)
        def get_possible_moves(pos, board, adv_pos):
            allowed_dirs=get_allowed_dirs_place(pos[0],pos[1],board)
            possible_moves = []
            for i in range(len(allowed_dirs)):
                possible_moves.append((pos,allowed_dirs[i]))
            r,c = pos
            my_allowed_dirs = get_allowed_dirs_move(r,c, board, adv_pos)
            queue = [(r,c,my_allowed_dirs,0)]
            while queue:
                info = queue.pop(0)
                if info[3] > max_step:
                    break
                for j in range(len(info[2])):
                    if (time.time() - start_time) > 1.9:
                        return possible_moves
                    m_r, m_c = moves[info[2][j]]
                    new_pos = (info[0] + m_r, info[1] + m_c)
                    if new_pos not in (tup[0] for tup in possible_moves) and (info[3]+1)<=max_step:
                        new_dirs = get_allowed_dirs_move(new_pos[0], new_pos[1], board, adv_pos)
                        queue.append((new_pos[0],new_pos[1],new_dirs,info[3]+1))
                        new_dirs_place = get_allowed_dirs_place(new_pos[0],new_pos[1],board)
                        for dir in new_dirs_place:
                            possible_moves.append((new_pos,dir))
                return possible_moves
        
        # possible_moves = get_possible_moves(my_pos, chess_board,adv_pos)
        # adv_dirs = get_allowed_dirs_move(adv_pos[0],adv_pos[1], chess_board, my_pos)
        # if len(adv_dirs) == 1: # if can trap adversary
        #     m_r, m_c = moves[adv_dirs[0]]
        #     next_to_adv = (adv_pos[0]+m_r,adv_pos[1]+m_c)
        #     wall = 0
        #     if next_to_adv in possible_moves:
        #         return next_to_adv, (adv_dirs[0]+2)%4
            

        def set_barrier(board, r, c, dir):
            # Set the barrier to True
            board[r, c, dir] = True
            # Set the opposite barrier to True
            move = moves[dir]
            board[r + move[0], c + move[1], opposites[dir]] = True
            return board
        

        def check_endgame(board, pos1, pos2):
            board_size = board.shape[1]
            # Union-Find
            father = dict()
            for r in range(board_size):
                for c in range(board_size):
                    father[(r, c)] = (r, c)

            def find(pos):
                if father[pos] != pos:
                    father[pos] = find(father[pos])
                return father[pos]

            def union(pos1, pos2):
                father[pos1] = pos2

            for r in range(board_size):
                for c in range(board_size):
                    for dir, move in enumerate(
                        moves[1:3]
                    ):  # Only check down and right
                        if board[r, c, dir + 1]:
                            continue
                        pos_a = find((r, c))
                        pos_b = find((r + move[0], c + move[1]))
                        if pos_a != pos_b:
                            union(pos_a, pos_b)

            for r in range(board_size):
                for c in range(board_size):
                    find((r, c))
            p0_r = find(pos1)
            p1_r = find(pos2)
            p0_score = list(father.values()).count(p0_r)
            p1_score = list(father.values()).count(p1_r)
            if p0_r == p1_r:
                return False, p0_score, p1_score
            return True, p0_score, p1_score
        
        #make the heuristic number of my possible moves - opponenet
        def heuristic(my_pos,adv_pos,board):
            # endgame returns (done, p1_score, p2_score)
            endgame = check_endgame(board,my_pos,adv_pos)
            if endgame[0]:
                if endgame[1] > endgame[2]:
                    return 10000
                elif endgame[1] < endgame[2]:
                    return -10000
                else:
                    return 0
            my_moves = get_possible_moves(my_pos,board,adv_pos)
            # adv_moves = get_possible_moves(adv_pos,board,my_pos)
            return len(my_moves)
        

        #Whats a good way to determine the depth?
        depth = 2


        def maxValue(my_pos,adv_pos,board,current_depth):
            if current_depth == depth or check_endgame(board,my_pos,adv_pos)[0]:
                return None, heuristic(my_pos,adv_pos,board)
            possible_moves = get_possible_moves(my_pos,board,adv_pos)
            maximum = float('-inf')
            best_move = possible_moves[0]
            # move looks like (pos, dir)
            for move in possible_moves:
                # TODO: add time contingency
                if (time.time() - start_time) > 1.95:
                        return best_move,maximum
                fake_board = board.copy()
                fake_board = set_barrier(fake_board,move[0][0],move[0][1],move[1])
                h = minValue(move[0],adv_pos,fake_board,current_depth+1)[1]
                if h > maximum:
                    best_move = move
                    maximum = h
            return best_move, maximum
        

        def minValue(my_pos,adv_pos,board,current_depth):
            if current_depth == depth or check_endgame(board,my_pos,adv_pos)[0]:
                return None, heuristic(my_pos,adv_pos,board)
            possible_moves = get_possible_moves(adv_pos,board,my_pos)
            minimum = float('inf')
            best_move = possible_moves[0]
            # move looks like (pos, dir)
            for move in possible_moves:
                # TODO: add time contingency
                if (time.time() - start_time) > 1.95:
                        return best_move,minimum
                fake_board = board.copy()
                fake_board = set_barrier(fake_board,move[0][0],move[0][1],move[1])
                h = maxValue(my_pos,move[0],fake_board,current_depth+1)[1]
                if h < minimum:
                    best_move = move
                    minimum = h
            return best_move, minimum
        
        move = maxValue(my_pos,adv_pos,chess_board,0)
        return move[0][0], move[0][1]


                

        

        # depth = 3
        # # build the tree (my position, adv postition, board, parent, depth, (is_endgame,protagonist winner))
        # # were 1 means protagonist won, 0 means tie, -1 lost
        # tree = [(my_pos,adv_pos,chess_board,-1,0,(False,0))]
        # for i in range(depth):
        #     stack = []
        #     for j in range(len(tree)):
        #         if tree[j][4] == i: # append all at depth i
        #             # append the index as well as the original info
        #             stack.append((tree[j],j))
        #         if tree[j][4] > i: # if we past desired depth
        #             break
        #     while(stack):
        #         info = stack.pop()
        #         # check if the game is over
        #         if not info[0][5][0]:
        #             if i%2==0: #moves protagonist
        #                 cur_moves = get_possible_moves(info[0][0],info[0][2],info[0][1])
        #                 for move in cur_moves:
        #                     cur_dirs = get_allowed_dirs_place(move[0],move[1],info[0][2])
        #                     for k in range(len(cur_dirs)):
        #                         fake_board = info[0][2].copy()
        #                         fake_board = set_barrier(fake_board,move[0],move[1],cur_dirs[k])
        #                         is_endgame = check_endgame(fake_board,move,info[0][1])
        #                         #check if winner
        #                         if is_endgame[0]:
        #                             #check who won
        #                             if is_endgame[1] > is_endgame[2]:
        #                                 tree.append((move,info[0][1],fake_board,info[1],i+1,(True,1)))
        #                             elif is_endgame[1] < is_endgame[2]:
        #                                 tree.append((move,info[0][1],fake_board,info[1],i+1,(True,-1)))
        #                             else:
        #                                 tree.append((move,info[0][1],fake_board,info[1],i+1,(True,0)))
        #                         else: #if no winner yet
        #                             tree.append((move,info[0][1],fake_board,info[1],i+1,(False,0)))
        #             else: #moves opponent
        #                 cur_moves = get_possible_moves(info[0][1],info[0][2],info[0][0])
        #                 for move in cur_moves:
        #                     cur_dirs = get_allowed_dirs_place(move[0],move[1],info[0][2])
        #                     for k in range(len(cur_dirs)):
        #                         fake_board = info[0][2].copy()
        #                         fake_board = set_barrier(fake_board,move[0],move[1],cur_dirs[k])
        #                         is_endgame = check_endgame(fake_board,info[0][0],move)
        #                         #check if winner
        #                         if is_endgame[0]:
        #                             #check who won
        #                             if is_endgame[1] > is_endgame[2]:
        #                                 tree.append((info[0][0],move,fake_board,info[1],i+1,(True,1)))
        #                             elif is_endgame[1] < is_endgame[2]:
        #                                 tree.append((info[0][0],move,fake_board,info[1],i+1,(True,-1)))
        #                             else:
        #                                 tree.append((info[0][0],move,fake_board,info[1],i+1,(True,0)))
        #                         else: #if no winner yet
        #                             tree.append((info[0][0],move,fake_board,info[1],i+1,(False,0)))


        # # make a heuristic tree that has all of the information but if
        # # its endgame or depth of tree (leaf) evaluate heuristic
        # heuristic_tree = []
        # for i in range(len(tree)):
        #     info = tree[i]
        #     is_leaf = info[5][0]
        #     heuristic = 0
        #     if is_leaf and info[5][1] == 1: #wins
        #         heuristic = 10000
        #     elif is_leaf and info[5][1] == -1: #loses
        #         heuristic = -10000
        #     elif not is_leaf: #makes h number of possible moves from position
        #         if info[4] == depth: # max depth means leaf
        #             is_leaf = True 
        #             heuristic = len(get_possible_moves(info[0],info[2],info[1]))
        #     heuristic_tree.append((info,(is_leaf,heuristic)))

        # def maxValue(node,alpha1,beta1):
        #     if node[1][0]:
        #         return node[1][1], None
        #     # get successors
        #     successors = []
        #     for i in range(1,len(tree)): #0 will give parent -1
        #         #tree[i][3] gives index of parent of tree[i]
        #         #this checks if parent of tree[i] is node
        #         if tree[tree[i][3]][0] == node[0][0] and\
        #             tree[tree[i][3]][1] == node[0][1] and\
        #                 tree[tree[i][3]][2].all() == node[0][2].all() and\
        #                     tree[tree[i][3]][3] == node[0][3]:
        #             successors.append(heuristic_tree[i])
        #         # if depth greater than current depth+1 break
        #         if tree[i][4] > node[0][4]+1:
        #             break
        #     best_value = float('-inf')
        #     best_move = None
        #     for successor in successors:
        #         value, _ = minValue(successor,alpha1,beta1)
        #         if value > best_value:
        #             best_value = value
        #             best_move = successor[0]
        #         alpha1 = max(alpha1,value)
        #         if alpha1 >= beta1:
        #             break
        #     return best_value,best_move
        
        # def minValue(node,alpha2,beta2):
        #     if node[1][0]: #if cuttoff return evaluation
        #         return node[1][1], None
        #     # get successors
        #     successors = []
        #     for i in range(1,len(tree)): #0 will give parent -1
        #         #tree[i][3] gives index of parent of tree[i]
        #         if tree[tree[i][3]][0] == node[0][0] and\
        #             tree[tree[i][3]][1] == node[0][1] and\
        #                 tree[tree[i][3]][2].all() == node[0][2].all() and\
        #                     tree[tree[i][3]][3] == node[0][3]:
        #             successors.append(heuristic_tree[i])
        #         # if depth greater than current depth+1 break
        #         if tree[i][4] > node[0][4]+1:
        #             break
        #     best_value = float('inf')
        #     best_move = None
        #     for successor in successors:
        #         value, _ = maxValue(successor,alpha2,beta2)
        #         if value < best_value:
        #             best_value = value
        #             best_move = successor[0]
        #         beta2 = min(beta2,value)
        #         if alpha2 >= beta2:
        #             break
        #     return best_value, best_move

        # try simple minimax search
        # def maxValue(node):
        #     if node[1][0]: #if cuttoff return evaluation
        #         return node[1][1], None
        #     # get successors
        #     successors = []
        #     for i in range(1,len(tree)): #0 will give parent -1
        #         #tree[i][3] gives index of parent of tree[i]
        #         if tree[tree[i][3]][0] == node[0][0] and\
        #             tree[tree[i][3]][1] == node[0][1] and\
        #                 tree[tree[i][3]][2].all() == node[0][2].all() and\
        #                     tree[tree[i][3]][3] == node[0][3]:
        #             successors.append(heuristic_tree[i])
        #         # if depth greater than current depth+1 break
        #         if tree[i][4] > node[0][4]+1:
        #             break
        #     best_value = float('-inf')
        #     best_move = None
        #     for successor in successors:
        #         value, _ = minValue(successor)
        #         if value > best_value:
        #             best_value = value
        #             best_move = successor[0]
        #     return best_value, best_move
        # def minValue(node):
        #     if node[1][0]: #if cuttoff return evaluation
        #         return node[1][1], None
        #     # get successors
        #     successors = []
        #     for i in range(1,len(tree)): #0 will give parent -1
        #         #tree[i][3] gives index of parent of tree[i]
        #         if tree[tree[i][3]][0] == node[0][0] and\
        #             tree[tree[i][3]][1] == node[0][1] and\
        #                 tree[tree[i][3]][2].all() == node[0][2].all() and\
        #                     tree[tree[i][3]][3] == node[0][3]:
        #             successors.append(heuristic_tree[i])
        #         # if depth greater than current depth+1 break
        #         if tree[i][4] > node[0][4]+1:
        #             break
        #     best_value = float('inf')
        #     best_move = None
        #     for successor in successors:
        #         value, _ = maxValue(successor)
        #         if value < best_value:
        #             best_value = value
        #             best_move = successor[0]
        #     return best_value, best_move




        # best_move = minValue(heuristic_tree[0])
        # # my_allowed_dirs = get_allowed_dirs_move(r,c)
        # # print(best_move)
        # move_to = best_move[1][0]
        # fake_board = best_move[1][2]
        # #find where the wall was put
        # real_places = get_allowed_dirs_place(move_to[0],move_to[1],chess_board)
        # fake_places = get_allowed_dirs_place(move_to[0],move_to[1],fake_board)
        # wall = 0
        # for i in range(len(real_places)):
        #     if real_places[i] not in fake_places:
        #         wall = i
        #         break


            
            
        # time_taken = time.time() - start_time
        # print("My AI's turn took ", time_taken, "seconds.")
        # return move_to, wall
