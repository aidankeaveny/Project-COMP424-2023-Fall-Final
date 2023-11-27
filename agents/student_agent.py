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
                    if (time.time() - start_time) > 1.95:
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
                    return float('inf')
                elif endgame[1] < endgame[2]:
                    return float('-inf')
                else:
                    return 0
            my_moves = get_possible_moves(my_pos,board,adv_pos)
            return len(my_moves)
        time_reached = False


        def maxValue(my_pos,adv_pos,board,current_depth,alpha,beta,max_depth):
            nonlocal time_reached
            if current_depth == max_depth or check_endgame(board,my_pos,adv_pos)[0]:
                    return None, heuristic(my_pos,adv_pos,board)
            possible_moves = get_possible_moves(my_pos,board,adv_pos)
            best_move = possible_moves[0]
            # move looks like (pos, dir)
            for move in possible_moves:
                if (time.time() - start_time) > 1.99:
                        time_reached = True
                        return best_move,alpha
                fake_board = deepcopy(board)
                fake_board = set_barrier(fake_board,move[0][0],move[0][1],move[1])
                adv_turn = minValue(move[0],adv_pos,fake_board,current_depth+1,alpha,beta,max_depth)
                if adv_turn[1]>alpha:
                    alpha = adv_turn[1]
                    best_move = move
                if alpha >= beta:
                    return best_move,beta
            return best_move, alpha
        

        def minValue(my_pos,adv_pos,board,current_depth,alpha,beta,max_depth):
            nonlocal time_reached
            if current_depth == max_depth or check_endgame(board,my_pos,adv_pos)[0]:
                    return None, heuristic(my_pos,adv_pos,board)
            possible_moves = get_possible_moves(adv_pos,board,my_pos)
            best_move = possible_moves[0]
            # move looks like (pos, dir)
            for move in possible_moves:
                if (time.time() - start_time) > 1.99:
                        time_reached = True
                        return best_move,beta
                fake_board = deepcopy(board)
                fake_board = set_barrier(fake_board,move[0][0],move[0][1],move[1])
                adv_turn = maxValue(my_pos,move[0],fake_board,current_depth+1,alpha,beta,max_depth)
                if adv_turn[1]<beta:
                    beta = adv_turn[1]
                    best_move = move
                if alpha >= beta:
                    return best_move,alpha
            return best_move, beta
        
        depth = 2
        if max_step >= 5:
            depth = 1
        
        best_move = maxValue(my_pos,adv_pos,chess_board,0,float('-inf'),float('inf'),depth)
        i = 0
        while((time.time() - start_time) < 1.9):
            depth += i
            move = maxValue(my_pos,adv_pos,chess_board,0,float('-inf'),float('inf'),depth)
            if not time_reached:
                best_move = move
            
        return best_move[0][0], best_move[0][1]

