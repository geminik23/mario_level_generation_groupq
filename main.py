import enum
import os
import sys
from random import Random, choices
import numpy as np
import configparser
from datetime import datetime


## CONSTANTS
BLOCK_UNIT = 2
CONFIG_INPUTPATH = "InputPath"
CONFIG_OUTPUTPATH = "OutputPath"
DEST_HEIGHT = 16
DEST_WIDTH = 150
DEST_SIZE = (DEST_HEIGHT, DEST_WIDTH)




# for time estimation
class TimeEstimate:
    def __init__(self):
        self._t = 0

    def start(self):
        self._t = datetime.now().timestamp()
        return self

    def stop(self):
        now = datetime.now().timestamp()
        p = now - self._t
        self._t = now
        return p


# Mario Sprite Enums
class MarioSprite(enum.Enum):
    # start and end of the level
    MARIO_START = ord('M')
    MARIO_EXIT = ord('F')
    EMPTY =ord('-')

    # game tiles symbols
    GROUND =ord('X')
    PYRAMID_BLOCK =ord('#')
    NORMAL_BRICK =ord('S')
    COIN_BRICK =ord('C')
    LIFE_BRICK =ord('L')
    SPECIAL_BRICK =ord('U')
    SPECIAL_QUESTION_BLOCK =ord('@')
    COIN_QUESTION_BLOCK =ord('!')
    COIN_HIDDEN_BLOCK =ord('2')
    LIFE_HIDDEN_BLOCK =ord('1')
    USED_BLOCK =ord('D')
    COIN =ord('o')
    PIPE =ord('t')
    PIPE_FLOWER =ord('T')
    BULLET_BILL =ord('*')
    PLATFORM_BACKGROUND =ord('|')
    PLATFORM =ord('%')

    # enemies that can be in the level
    GOOMBA =ord('g')
    GOOMBA_WINGED =ord('G')
    RED_KOOPA =ord('r')
    RED_KOOPA_WINGED =ord('R')
    GREEN_KOOPA =ord('k')
    GREEN_KOOPA_WINGED =ord('K')
    SPIKY =ord('y')
    SPIKY_WINGED =ord('Y')

    # only in ORIGINAL
    #CACTUS =ord('|')


# 
# ALL_TILES = [EMPTY, GROUND, PYRAMID_BLOCK, NORMAL_BRICK, COIN_BRICK, LIFE_BRICK, SPECIAL_BRICK, SPECIAL_QUESTION_BLOCK, COIN_QUESTION_BLOCK, COIN_HIDDEN_BLOCK, LIFE_HIDDEN_BLOCK, USED_BLOCK, COIN, PIPE, PIPE_FLOWER, BULLET_BILL, PLATFORM_BACKGROUND, PLATFORM, GOOMBA, GOOMBA_WINGED, RED_KOOPA, RED_KOOPA_WINGED, GREEN_KOOPA, GREEN_KOOPA_WINGED, SPIKY, SPIKY_WINGED] 

ALL_ENEMY = [MarioSprite.GOOMBA.value, 
        MarioSprite.GOOMBA_WINGED.value, 
        MarioSprite.RED_KOOPA.value,
        MarioSprite.RED_KOOPA_WINGED.value,
        MarioSprite.GREEN_KOOPA.value,
        MarioSprite.GREEN_KOOPA_WINGED.value,
        MarioSprite.SPIKY.value,
        MarioSprite.SPIKY_WINGED]
ALL_SPRITES_TO_BE_REMOVED = [MarioSprite.MARIO_START.value,
        MarioSprite.MARIO_EXIT.value,
        MarioSprite.COIN.value,
        MarioSprite.PLATFORM_BACKGROUND.value ] + ALL_ENEMY




class MarioLevel:
    """
    load level file and convert into numpy array.
    """
    def __init__(self, path):
        self.data = None
        self.load_level(path)
        pass

    def load_level(self, path):
        f = open(path, 'r')
        # load the each lines of level
        lines = []
        for line in f.readlines():
            lines.append(line.strip())
        
        h = len(lines)
        w = len(lines[0])
        self.data = np.zeros((h, w), dtype=int)
        self.data.fill(MarioSprite.EMPTY.value)

        i = 0
        for line in lines:
            # convert into np.array and remove the unnecessary sprites
            self.data[i,:] = np.array([MarioSprite.EMPTY.value if ord(c) in ALL_SPRITES_TO_BE_REMOVED else ord(c) for c in line.strip()][0:w])
            i += 1

        # remove the sprite unnecessary
        f.close()

    def get_data(self):
        return self.data

    def EncodeLevel(data):
        lines = data.tolist()
        out = []
        for line in lines:
            out.append(''.join([chr(c) for c in line]))
        return '\n'.join(out)



# 1. 2x2 ground
#

# 1. left boundary, right boundary bottom.... -> it needs?
# 2. left to right 1
# 3. top right 2
# 4. top right diagonal 3


class DependencyTable:
    
    def __init__(self):
        self._table= {}
        pass

    def train(self, states):
        # train
        prev_state = states[0]
        next_state = states[1]
        if not self._table.get(prev_state):
            self._table[prev_state] = {}
        count = self._table[prev_state].get(next_state)
        if count == None: self._table[prev_state][next_state] = 0
        self._table[prev_state][next_state] +=1
        pass

    def generate_state(self, state):
        # generate
        data = None
        table = self._table.get(state)
        if not table: return data
        data = choices([k for k in table.keys()], [v for v in table.values()])
        if type(data) == list: data = data[0]
        return data




class DMatConverter():
    """
    numpy array to string converter for key storing in hashtable
    """
    def Decode(sequence, bsize):
        res = np.array([ord(c) for c in sequence], dtype=int)
        return res.reshape((bsize, bsize))

    def Encode(mat):
        res = ''.join([chr(ele) for ele in mat.flatten().tolist()])
        return res


class DMat_11:
    def PrevState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,0:unit])

    def NextState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,unit:unit*2])

    @classmethod
    def Parse(cls, matrix, unit):
        return (cls.PrevState(matrix, unit), cls.NextState(matrix, unit))


class DMat_1101:
    def PrevState(matrix, unit):
        return DMatConverter.Encode( np.concatenate((matrix[0:unit, 0:unit], matrix[unit:unit*2, unit:unit*2]),axis=1) )

    def NextState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,unit:unit*2])

    @classmethod
    def Parse(cls, matrix, unit):
        return (cls.PrevState(matrix, unit), cls.NextState(matrix, unit))


class DMat_1111:
    def PrevState(matrix, unit):
        return DMatConverter.Encode( np.concatenate((matrix[0:unit, 0:unit], matrix[unit:unit*2, 0:unit], matrix[unit:unit*2, unit:unit*2]),axis=1))

    def NextState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,unit:unit*2])
    @classmethod
    def Parse(cls, matrix, unit):
        return (cls.PrevState(matrix, unit), cls.NextState(matrix, unit))



class MDMarkovChain:
    """
    """
    def __init__(self):
        ## key : {value: frequency}
        # bottom
        self._unit = BLOCK_UNIT
        self._start_block = np.zeros((self._unit, self._unit), dtype=int)
        self._start_block.fill(MarioSprite.GROUND.value)
        self._dt_bottom = DependencyTable()

        pass

    def train(self, level):
        ldata = level.get_data()
        nrows = ldata.shape[0]/self._unit

        # ready for training the bottom lines
        n = int((nrows-1)*self._unit)
        bottoms = ldata[n:n+self._unit, :]


        length = bottoms.shape[1]
        if length & self._unit is not 0: length -= (length & self._unit)

        for xoff in range(self._unit,length,self._unit):
            nstate = bottoms[:,xoff:xoff+self._unit]
            mat = bottoms[:,xoff-self._unit:xoff+self._unit]
            self._dt_bottom.train(DMat_11.Parse(mat, self._unit))
        pass

    def generate(self, output):
        # * decode, encode
        # generate the bottom first
        (h, w) = output.shape
        output[h-self._unit:h, 0:self._unit] = self._start_block[:,:]
        
        cur = output[h-self._unit:h, 0:self._unit]
        for xoff in range(self._unit, w, self._unit):
            generated = self._dt_bottom.generate_state(DMatConverter.Encode(cur))
            # FIXME check if generated?
            cur = DMatConverter.Decode(generated, self._unit)
            output[h-self._unit:h, xoff:xoff+self._unit] = cur[:,:]

        # TODO
        
        pass


class GroupQLevelGenerator:
    """
    Mario Level Generator of GroupQ
    """

    def __init__(self, config_path):
        self._config = None
        self._markovchain = MDMarkovChain()
        self.load_config(config_path)
        self._output = np.zeros(DEST_SIZE, dtype=int)


    def load_config(self, config_path):
        # load config
        arg_load = config_path
        self._config = configparser.ConfigParser()
        self._config.read(arg_load)

    def train_levels(self):
        """
        train mario levels from input paths in config file
        """
        te = TimeEstimate().start()
        
        # looping input paths
        for key in self._config[CONFIG_INPUTPATH]:
            base_path = self._config[CONFIG_INPUTPATH][key]
            # load levels
            flist = os.listdir(base_path)
            files = []
            [files.append(f) if f.endswith('txt') else None for f in flist]
            for filename in files:
                level = MarioLevel(os.path.join(base_path, filename))
                # train level
                self._markovchain.train( level )

        return te.stop()

    def generate_level(self):
        """generate the mario level"""
        # initialize the output
        te = TimeEstimate().start()
        self._output.fill(MarioSprite.EMPTY.value)
        self._markovchain.generate(self._output)
        # TODO

        return te.stop()

    def save_file(self, idx):
        # ready for save
        filename = os.path.join(self._config[CONFIG_OUTPUTPATH]["path"], "lvl-{}.txt".format(idx))
        f = open(filename, 'w')
        f.write(MarioLevel.EncodeLevel(self._output))
        f.close()
        



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("it need config file to run : python3 main.py config.ini")
        sys.exit(1)

    generator = GroupQLevelGenerator(sys.argv[1])
    print("training time : {:.3f} secs".format(generator.train_levels()))
    print("generating time : {:.3f} secs".format(generator.generate_level()))
    generator.save_file(0)
