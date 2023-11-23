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
        # Build a list of the moves we can make
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
        def get_possible_moves(pos, board, adv_pos):
            allowed_dirs=get_allowed_dirs_place(pos[0],pos[1],board)
            possible_moves = [(pos,allowed_dirs[0])]
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
        
        possible_moves = get_possible_moves(my_pos,chess_board,adv_pos)
        adv_dirs = get_allowed_dirs_move(adv_pos[0],adv_pos[1],chess_board,my_pos)
        if len(adv_dirs) == 1: # if can trap adversary
            m_r, m_c = moves[adv_dirs[0]]
            next_to_adv = (adv_pos[0]+m_r,adv_pos[1]+m_c)
            if next_to_adv in (tup[0] for tup in possible_moves):
                return next_to_adv, (adv_dirs[0]+2)%4
            
        # we want to move to place with most possible moves
        # start with current location and first available wall
        # need to start with some move to improve on
        # this will obviously just initiate random walk
        best_move = ((0,0),0)
        best_len_possible_moves = 0        
        for move in possible_moves:
            if (time.time() - start_time) > 1.99:
                return best_move[0],best_move[1]
            fake_board = set_barrier(chess_board,move[0][0],move[0][1],move[1])
            #check if move is a winning move
            endgame = check_endgame(fake_board,move[0],adv_pos)
            # if new move wins
            if endgame[0] and endgame[1] > endgame[2]:
                return move[0],move[1]
            # if you lose at the new move
            elif endgame[0] and endgame[1] < endgame[2]:
                continue
            places_to_wall = get_allowed_dirs_place(move[0][0],move[0][1],fake_board)
            # if at this new move you block yourself in
            if (time.time() - start_time) > 1.99:
                return best_move[0],best_move[1]
            if len(places_to_wall) <= 1:
                if len(places_to_wall) == 0:
                    continue
                #if adv can block me in
                m_r, m_c = moves[places_to_wall[0]]
                next_to_me = (move[0][0]+m_r,move[0][1]+m_c)
                adv_moves = get_possible_moves(adv_pos,fake_board,my_pos)
                if next_to_me in (tup[0] for tup in adv_moves):
                    continue
            allowed_moves = get_possible_moves(move[0],fake_board,adv_pos)
            if len(allowed_moves) > best_len_possible_moves:
                best_move = move
                best_len_possible_moves = len(allowed_moves)
            
            
        time_taken = time.time() - start_time
        # print("My AI's turn took ", time_taken, "seconds.")

        # dummy return
        return best_move[0], best_move[1]
