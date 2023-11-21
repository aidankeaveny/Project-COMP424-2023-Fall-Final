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
        def get_allowed_dirs_place(r,c,board):
            allowed_dirs = [ d                                
                for d in range(0,4)
                if not board[r,c,d]]
            return allowed_dirs
        # Build a list of the moves we can make
        def get_possible_moves(pos, board, adv_pos):
            possible_moves = [pos]
            r,c = pos
            my_allowed_dirs = get_allowed_dirs_move(r,c, board, adv_pos)
            queue = [(r,c,my_allowed_dirs,0)]
            while queue:
                info = queue[0]
                if info[3] > max_step:
                    break
                queue = queue[1:]
                for j in range(len(info[2])):
                    m_r, m_c = moves[info[2][j]]
                    new_pos = (info[0] + m_r, info[1] + m_c)
                    if new_pos not in possible_moves and (info[3]+1)<=max_step:
                        new_dirs = get_allowed_dirs_move(new_pos[0], new_pos[1], board, adv_pos)
                        queue.append((new_pos[0],new_pos[1],new_dirs,info[3]+1))
                        possible_moves.append(new_pos)
            return possible_moves
        possible_moves = get_possible_moves(my_pos, chess_board,adv_pos)
        adv_dirs = get_allowed_dirs_move(adv_pos[0],adv_pos[1], chess_board, my_pos)
        if len(adv_dirs) == 1: # if can trap adversary
            m_r, m_c = moves[adv_dirs[0]]
            next_to_adv = (adv_pos[0]+m_r,adv_pos[1]+m_c)
            wall = 0
            if next_to_adv in possible_moves:
                return next_to_adv, (adv_dirs[0]+2)%4
            

        
        # best_move = my_pos
        # best_len_dirs = len(get_allowed_dirs(my_pos[0],my_pos[1]))
        # for move in possible_moves:
        #     allowed_dirs = get_allowed_dirs(move[0],move[1])
        #     if len(allowed_dirs) > best_len_dirs:
        #         best_move = move
        #         best_len_dirs = len(allowed_dirs)
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
        

        depth = 4
        # build the tree (my position, adv postition, board, parent, depth, (is_endgame,protagonist winner))
        # were 1 means protagonist won, 0 means tie, -1 lost
        tree = [(my_pos,adv_pos,chess_board,-1,0,(False,0))]
        for i in range(depth):
            stack = []
            for j in range(len(tree)):
                if tree[j][4] == i: # append all at depth i
                    # append the index as well as the original info
                    stack.append((tree[j],j))
                if tree[j][4] > i: # if we past desired depth
                    break
            while(stack):
                info = stack.pop()
                # check if the game is over
                if not info[0][5][0]:
                    if i%2==0: #moves protagonist
                        cur_moves = get_possible_moves(info[0][0],info[0][2],info[0][1])
                        for move in cur_moves:
                            cur_dirs = get_allowed_dirs_place(move[0],move[1],info[0][2])
                            for k in range(len(cur_dirs)):
                                fake_board = info[0][2].copy()
                                fake_board = set_barrier(fake_board,move[0],move[1],cur_dirs[k])
                                is_endgame = check_endgame(fake_board,move,info[0][1])
                                #check if winner
                                if is_endgame[0]:
                                    #check who won
                                    if is_endgame[1] > is_endgame[2]:
                                        tree.append((move,info[0][1],fake_board,info[1],i+1,(True,1)))
                                    elif is_endgame[1] < is_endgame[2]:
                                        tree.append((move,info[0][1],fake_board,info[1],i+1,(True,-1)))
                                    else:
                                        tree.append((move,info[0][1],fake_board,info[1],i+1,(True,0)))
                                else: #if no winner yet
                                    tree.append((move,info[0][1],fake_board,info[1],i+1,(False,0)))
                    else: #moves opponent
                        cur_moves = get_possible_moves(info[0][1],info[0][2],info[0][0])
                        for move in cur_moves:
                            cur_dirs = get_allowed_dirs_place(move[0],move[1],info[0][2])
                            for k in range(len(cur_dirs)):
                                fake_board = info[0][2].copy()
                                fake_board = set_barrier(fake_board,move[0],move[1],cur_dirs[k])
                                is_endgame = check_endgame(fake_board,info[0][0],move)
                                #check if winner
                                if is_endgame[0]:
                                    #check who won
                                    if is_endgame[1] > is_endgame[2]:
                                        tree.append((info[0][0],move,fake_board,info[1],i+1,(True,1)))
                                    elif is_endgame[1] < is_endgame[2]:
                                        tree.append((info[0][0],move,fake_board,info[1],i+1,(True,-1)))
                                    else:
                                        tree.append((info[0][0],move,fake_board,info[1],i+1,(True,0)))
                                else: #if no winner yet
                                    tree.append((info[0][0],move,fake_board,info[1],i+1,(False,0)))
        print('here')




        # this will store position,heuristic,depth
        # where the heuristic is number of possible locations to move to
        
        stack = [(my_pos,len(get_possible_moves(my_pos, chess_board)),0)]
        # position,wall,parent,heuristic,depth
        tree = []
        # for i in range(1,4): # this will append the first 4 branches, move 0 steps and wall
        #     fake_board = chess_board
        #     chess_board[my_pos[0],my_pos[1],4-i] = True
        #     stack.append((my_pos[0],my_pos[1],4-i,len(get_possible_moves(my_pos, fake_board)),0,1))
        def add_set_of_moves(board):
            info = stack.pop()
            possible_moves = get_possible_moves(info[0],board)
            for move in possible_moves:
                for i in range(1,4): # this will append the wall branches; go to (move) and wall
                    fake_board = chess_board
                    chess_board[move[0],move[1],4-i] = True
                    tree.append((move,4-i,len(get_possible_moves(move, fake_board)),info[4]+1))



        r, c = best_move
        my_allowed_dirs = get_allowed_dirs_move(r,c)

        if len(my_allowed_dirs) >= 1:
            wall = my_allowed_dirs[0]
        else:
            wall = 0
            
            
        time_taken = time.time() - start_time
        # print("My AI's turn took ", time_taken, "seconds.")

        # dummy return
        return best_move, wall
