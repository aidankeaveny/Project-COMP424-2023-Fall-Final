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
        def get_allowed_dirs(r,c):
            return [ d                                
            for d in range(0,4)                           # 4 moves possible
            if not chess_board[r,c,d] and                 # chess_board True means wall
            not adv_pos == (r+moves[d][0],c+moves[d][1])] # cannot move through Adversary
        def get_possible_moves(pos):
            possible_moves = [pos]
            my_allowed_dirs = get_allowed_dirs(r,c)
            queue = [(r,c,my_allowed_dirs,0)]
            while queue:
                info = queue[0]
                if info[3] >= max_step:
                    break
                queue = queue[1:]
                for j in range(len(info[2])):
                    m_r, m_c = moves[info[2][j]]
                    new_pos = (info[0] + m_r, info[1] + m_c)
                    if new_pos not in possible_moves:
                        new_dirs = get_allowed_dirs(new_pos[0], new_pos[1])
                        queue.append((new_pos[0],new_pos[1],new_dirs,info[3]+1))
                        possible_moves.append(new_pos)
            return possible_moves
        possible_moves = get_possible_moves(my_pos)
        adv_dirs = get_allowed_dirs(adv_pos[0],adv_pos[1])
        if len(adv_dirs) == 1: # if can trap adversary
            m_r, m_c = moves[adv_dirs[0]]
            next_to_adv = (adv_pos[0]+m_r,adv_pos[1]+m_c)
            wall = 0
            if next_to_adv in possible_moves:
                return next_to_adv, (adv_dirs[0]+2)%4
        best_move = my_pos
        best_len_dirs = len(get_allowed_dirs(my_pos[0],my_pos[1]))
        for move in possible_moves:
            allowed_dirs = get_allowed_dirs(move[0],move[1])
            if len(allowed_dirs) > best_len_dirs:
                best_move = move
                best_len_dirs = len(allowed_dirs)

        r, c = best_move
        my_allowed_dirs = get_allowed_dirs(r,c)

        if len(my_allowed_dirs) >= 1:
            wall = my_allowed_dirs[0]
        else:
            wall = 0
            
            
        time_taken = time.time() - start_time
        # print("My AI's turn took ", time_taken, "seconds.")

        # dummy return
        return best_move, wall
