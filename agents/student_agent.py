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
                info = queue[0]
                if info[3] > max_step:
                    break
                queue = queue[1:]
                for j in range(len(info[2])):
                    m_r, m_c = moves[info[2][j]]
                    new_pos = (info[0] + m_r, info[1] + m_c)
                    if new_pos not in (tup[0] for tup in possible_moves) and (info[3]+1)<=max_step:
                        new_dirs = get_allowed_dirs_move(new_pos[0], new_pos[1], board, adv_pos)
                        queue.append((new_pos[0],new_pos[1],new_dirs,info[3]+1))
                        new_dirs_place = get_allowed_dirs_place(new_pos[0],new_pos[1],board)
                        for dir in new_dirs_place:
                            possible_moves.append((new_pos,dir))
            return possible_moves
        possible_moves = get_possible_moves(my_pos,chess_board,adv_pos)
        adv_dirs = get_allowed_dirs_move(adv_pos[0],adv_pos[1],chess_board,my_pos)
        if len(adv_dirs) == 1: # if can trap adversary
            m_r, m_c = moves[adv_dirs[0]]
            next_to_adv = (adv_pos[0]+m_r,adv_pos[1]+m_c)
            if next_to_adv in (tup[0] for tup in possible_moves):
                return next_to_adv, (adv_dirs[0]+2)%4
            
        # we want to move to place with most possible moves
        # start with current location and first available wall
        my_dirs = get_allowed_dirs_place(my_pos[0],my_pos[1],chess_board)
        best_move = (my_pos,my_dirs[0])
        best_len_possible_moves = len(get_possible_moves(my_pos,chess_board,adv_pos))
        for move in possible_moves:
            allowed_moves = get_possible_moves(move[0],chess_board,adv_pos)
            if len(allowed_moves) > best_len_possible_moves:
                best_move = move
                best_len_possible_moves = len(allowed_moves)
            
            
        time_taken = time.time() - start_time
        # print("My AI's turn took ", time_taken, "seconds.")

        # dummy return
        return best_move[0], best_move[1]
