
import enum
from mario_constant import *
import numpy as np

############################################################################
# Real-time Inspector
############################################################################
class RTIResult(enum.Enum):
    TRUE = 1
    DMAT_1111 = 2
    DMAT_1101 = 3
    DMAT_11 = 4
    ERROR = 5
    
class RealtimeInspector:
    def __init__(self, config):
        ##::::load params from config
        params = config[CONFIG_PARAMS]

        ##::::realtime vars
        self._data = None
        self._cur_method = RTIResult.DMAT_1111
        self._unit = None
        self._start_point = None
        # mario start and exit position 
        self._m_start = None
        self._m_exit = None
        self._t_start_sel_pos = MARIO_START_POSITION 
        pass

    def reset(self, data, unitsize):
        """reset the variables. this should be called before starting generating"""
        # initialize the member vars
        self._data = data
        self._placed_start = False
        self._unit = unitsize
        self._m_start = None
        self._m_exit = None
        self._t_start_sel_pos = MARIO_START_POSITION
        pass

    def inspect(self, pos):
        """
        This was supposed to track the player's path, to avoid the unplayable factors, and to find the place to put the enemies and coins.
        For future work, this method will be used for MCTS (Monte Carlo Tree Search)
        """
        if self._data is None: raise TypeError("data is not assigned")

        # initialize
        (h, w) = np.shape(self._data)
        self._expecting_blocks = []

        self._last_ncol = pos[1]

        # search start position
        if not self._m_start:
            self._search_startpos(pos[1])

        ## TODO "FUTURE WORK"


        self._cur_method = RTIResult.DMAT_1111
        return self._cur_method


    def check_bottom(self):
        """check gap is jumpable"""
        bline = self._data[-1,:]
        n = 0
        for t in bline:
            if t == MarioSprite.EMPTY.value: n+=1
            else: n = 0
            if n>5: return False
        return True


    def check_block(self, block):
        """check whether the block is suitable or not"""
        if block is None:
            # if there is no block, return next dependency matrix
            self._cur_method = RTIResult(self._cur_method.value+1)
            return self._cur_method

        # TODO Check block is suitable

        return RTIResult.TRUE


    def mario_start_pos(self):
        return self._m_start

    def mario_exit_pos(self):
        """search exit position when calling"""
        self._search_exitpos()
        return self._m_exit


    ##########PRIVATE METHODS############
    def _search_startpos(self, xoff):
        (h, w) = self._data.shape
        while not self._m_start and xoff > self._t_start_sel_pos:
            if not self._data[h-1, self._t_start_sel_pos] == MarioSprite.EMPTY.value:
                for y in range(h-2, -1, -1):
                    if self._data[y, self._t_start_sel_pos] == MarioSprite.EMPTY.value:
                        # set mario start position 
                        self._m_start = (self._t_start_sel_pos, y)
                        # copy to tracking position 
                        self._tracking_pos = [p for p in self._m_start]
                        break
            self._t_start_sel_pos += 1
        

    def _search_exitpos(self):
        if self._m_exit: return
        (h, w) = self._data.shape
        mario_exit = w-1-MARIO_EXIT_POSITION
        while not self._m_exit:
            if not self._data[h-1, mario_exit] == MarioSprite.EMPTY.value:
                for y in range(h-2, -1, -1):
                    if self._data[y, mario_exit] == MarioSprite.EMPTY.value:
                        self._m_exit = (mario_exit, y)
                        break
                pass
            mario_exit -= 1
            pass

