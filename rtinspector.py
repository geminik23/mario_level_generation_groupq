import enum
from mario_constant import *

############################################################################
# Real-time Inspector
############################################################################

START_POSITION = 4
EXIT_POSITION = 3

class RTResult(enum.Enum):
    TRUE = 1
    DMAT_1111 = 2
    DMAT_1101 = 3
    DMAT_11 = 4
    ERROR = 5
    
class RealtimeInspector:
    def __init__(self, config):
        # load params from config
        params = config[CONFIG_PARAMS]
        # maximum trials
        # 
    


        self._placed_start = False
        self._data = None
        self._cur_method = RTResult.DMAT_1111


        pass

    def reset(self, data, unitsize):
        self._data = data
        self._placed_start = False
        pass

    def inspect(self, position):
        """check the current blocks whether it is playable"""
        if self._data is None: raise TypeError("data is not assigned")

        if not self._placed_start and position[0]>=START_POSITION:
            # TODO place the start
            self._placed_start = True

        # current state
        self._cur_method = RTResult.DMAT_1111

        
        return self._cur_method

    def check_block(self, block):
        if block is None:
            self._cur_method = RTResult(self._cur_method.value+1)
            return self._cur_method


        return RTResult.TRUE

        


        

    



