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
        def allowed_dirs(r,c):
            return [ d                                
            for d in range(0,4)                           # 4 moves possible
            if not chess_board[r,c,d] and                 # chess_board True means wall
            not adv_pos == (r+moves[d][0],c+moves[d][1])] # cannot move through Adversary
        #TODO: make possible locations array
        my_allowed_dirs = allowed_dirs(r,c)
        best_r = my_pos[0]
        best_c = my_pos[1]
        best_number_of_dirs = len(my_allowed_dirs)
        queue = [(r,c,my_allowed_dirs,0)]
        while queue: # find square with least amount of walls
            if best_number_of_dirs == 4:
                    break
            info = queue[len(queue)-1]
            if info[3] > max_step:
                break
            queue = queue[:len(queue)-1]
            for j in range(len(info[2])): # move to square with least amount of walls
                m_r, m_c = moves[info[2][j]]
                new_pos = (info[0] + m_r, info[1] + m_c)
                new_dirs = allowed_dirs(new_pos[0], new_pos[1])
                if len(new_dirs) > best_number_of_dirs:
                    best_number_of_dirs = len(new_dirs)
                    best_r = new_pos[0]
                    best_c = new_pos[1]
                if best_number_of_dirs == 4:
                    break
                queue.append((new_pos[0],new_pos[1],new_dirs,info[3]+1))
                
        my_pos = (best_r,best_c)
        r, c = my_pos
        my_allowed_dirs = allowed_dirs(r,c)
        wall = my_allowed_dirs[0]
            
            
        time_taken = time.time() - start_time
        print("My AI's turn took ", time_taken, "seconds.")

        # dummy return
        return my_pos, wall
