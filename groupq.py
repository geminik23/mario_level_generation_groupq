import os
import sys
from random import Random, choices
import numpy as np
import configparser
from rtinspector import RealtimeInspector, RTIResult
from mario_constant import *


############################################################################
# Dependency Matrix Converter
############################################################################
class DMatConverter():
    """
    numpy array to string converter for key storing in hashtable
    """
    def Decode(sequence, bsize):
        res = np.array([ord(c) for c in sequence], dtype=int)
        return res.reshape(bsize)

    def Encode(mat):
        res = ''.join([chr(ele) for ele in mat.flatten().tolist()])
        return res


class DMat_11:
    """ Dependency Matrix [1 1] """
    def PrevState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,0:unit])

    def NextState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,unit:unit*2])

    @classmethod
    def Parse(cls, matrix, unit):
        return (cls.PrevState(matrix, unit), cls.NextState(matrix, unit))


class DMat_1101:
    """ Dependency Matrix [1 1; 0 1] """
    def PrevState(matrix, unit):
        return DMatConverter.Encode( np.concatenate((matrix[0:unit, 0:unit], matrix[unit:unit*2, unit:unit*2]),axis=1) )

    def NextState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,unit:unit*2])

    @classmethod
    def Parse(cls, matrix, unit):
        return (cls.PrevState(matrix, unit), cls.NextState(matrix, unit))


class DMat_1111:
    """ Dependency Matrix [1 1; 1 1] """
    def PrevState(matrix, unit):
        return DMatConverter.Encode( np.concatenate((matrix[0:unit, 0:unit], matrix[unit:unit*2, 0:unit], matrix[unit:unit*2, unit:unit*2]),axis=1))

    def NextState(matrix, unit):
        return DMatConverter.Encode(matrix[0:unit,unit:unit*2])

    @classmethod
    def Parse(cls, matrix, unit):
        return (cls.PrevState(matrix, unit), cls.NextState(matrix, unit))




############################################################################
# Mario Level Object
############################################################################
class MarioLevel:
    """
    Load level from file and convert into numpy array.
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

        f.close()

    def get_data(self):
        return self.data

    def EncodeLevel(data):
        lines = data.tolist()
        out = []
        for line in lines:
            out.append(''.join([chr(c) for c in line]))
        return '\n'.join(out)



############################################################################
# Dependency Table
############################################################################
class DependencyTable:
    """
    Stores the markov states(t), states(t+1) and frequency
    """
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



############################################################################
# Mario Core Markov Chains training and generator
############################################################################
# * use decode, encode only in this class
class MarioCoreMC:
    """
    Mario Core Markov Chain object
    """
    def __init__(self, unitsize):
        self._unit = BLOCK_UNIT if not unitsize else unitsize
        
        # dependency tables
        self._dt_wall = DependencyTable()
        self._dt_bottom = DependencyTable() # same with dt_11

        self._dt_11 = DependencyTable()
        self._dt_1101 = DependencyTable()
        self._dt_1111 = DependencyTable()
        pass


    def train(self, level):
        ldata = level.get_data()
        nrows = ldata.shape[0]/self._unit

        ######
        # 1. save the wallet information
        self._dt_wall.train((DEFAULT_STATE, DMatConverter.Encode( ldata[:, 0:self._unit])))

        ######
        # 2. train the bottom lines
        n = int((nrows-1)*self._unit)
        bottoms = ldata[n:n+self._unit, :]

        length = bottoms.shape[1]
        if length % self._unit is not 0: length -= (length % self._unit)

        for xoff in range(self._unit,length,self._unit):
            nstate = bottoms[:,xoff:xoff+self._unit]
            mat = bottoms[:,xoff-self._unit:xoff+self._unit]
            self._dt_bottom.train(DMat_11.Parse(mat, self._unit))

        ######
        # 3. train from bottom to top and left to right : to 3 dependency table
        for xoff in range(self._unit, length, self._unit):
            for yoff in range(ldata.shape[0] - 2*self._unit, -1, -self._unit):
                # train to D1101 D1111
                mat = ldata[yoff:yoff+self._unit*2, xoff-self._unit:xoff+self._unit]
                self._dt_1101.train(DMat_1101.Parse(mat, self._unit))
                self._dt_1111.train(DMat_1111.Parse(mat, self._unit))

                # train to D11
                self._dt_11.train(DMat_11.Parse(ldata[yoff:yoff+self._unit, xoff-self._unit:xoff+self._unit], self._unit))
        pass


    def generate(self, output, rti):
        (h, w) = output.shape
        rti.reset(output, self._unit)

        ######
        # 1. generate the left wall
        wall = self._dt_wall.generate_state(DEFAULT_STATE)
        wall = DMatConverter.Decode(wall, (h, self._unit))
        output[:, 0:self._unit] = wall[:,:]

        ######
        # 2. generate the bottom
        #output[h-self._unit:h, 0:self._unit] = self._start_block[:,:]
        retry = True
        if w%self._unit != 0:
            w -= w%self._unit
        while retry:
            cur = output[h-self._unit:h, 0:self._unit]
            for xoff in range(self._unit, w, self._unit):
                generated = self._dt_bottom.generate_state(DMatConverter.Encode(cur))
                if not generated: break
                cur = DMatConverter.Decode(generated, (self._unit, self._unit))
                output[h-self._unit:h, xoff:xoff+self._unit] = cur[:,:]

            retry = not rti.check_bottom()

        #####
        # 3. generate whole tiles
        for xoff in range(self._unit, w, self._unit):
            for yoff in range(h - 2*self._unit, -1, -self._unit):
                res = rti.inspect((xoff, yoff)) ## inspect whenever changed new column

                # check current position
                generated = None

                # dependency matrix methods
                while res is not RTIResult.TRUE:
                    #
                    if res is RTIResult.DMAT_1111:
                        cur = output[yoff:yoff+self._unit*2, xoff-self._unit:xoff+self._unit]
                        generated = self._dt_1111.generate_state(DMat_1111.PrevState(cur, self._unit))
                    #
                    elif res is RTIResult.DMAT_1101:
                        cur = output[yoff:yoff+self._unit*2, xoff-self._unit:xoff+self._unit]
                        generated = self._dt_1101.generate_state(DMat_1101.PrevState(cur, self._unit))
                    #
                    elif res is RTIResult.DMAT_11:
                        cur = output[yoff:yoff+self._unit, xoff-self._unit:xoff+self._unit]
                        generated = self._dt_11.generate_state(DMat_11.PrevState(cur, self._unit))
                    #
                    elif res is RTIResult.ERROR:
                        print("retry.... this happens when blocksize is too big or training data is not enouch.")
                        break
                        # sys.exit(1)

                    res = rti.check_block(generated)
                    if res is RTIResult.TRUE:
                        output[yoff:yoff+self._unit, xoff:xoff+self._unit] = DMatConverter.Decode(generated, (self._unit, self._unit))[:,:]
                ######################## end while
        


        # placing MARIO_START MARIO_EXIT
        startpos = rti.mario_start_pos()
        exitpos = rti.mario_exit_pos()

        if startpos:
            output[startpos[1], startpos[0]] = MarioSprite.MARIO_START.value
        output[exitpos[1], exitpos[0]] = MarioSprite.MARIO_EXIT.value

        # TODO self._rt_inspector.place enemy / coin / items
        pass #generate()

        





############################################################################
# Group Generator
############################################################################
class GroupQLevelGenerator:
    """
    Mario Level Generator of GroupQ
    """

    def __init__(self, config_path):
        self._config = None
        self.load_config(config_path)

        # load config
        self._unitsize = self._config[CONFIG_PARAMS].get('block_unit_size')
        if not self._unitsize: self._unitsize = DEFAULT_BLOCK_UNIT
        else: self._unitsize = int(self._unitsize)

        self._rt_inspector = RealtimeInspector(self._config)
        self._markovchain = MarioCoreMC(self._unitsize)
        # generating output
        self._output = np.zeros(DEST_SIZE, dtype=int)


    def load_config(self, config_path):
        # load config
        arg_load = config_path
        self._config = configparser.ConfigParser()
        self._config.read(arg_load)


    def train_levels(self):
        """ training the  mario levels from input paths in config file """
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
        te = TimeEstimate().start()

        # reset output and call genrate method of markov chain object
        self._output.fill(MarioSprite.EMPTY.value)
        self._markovchain.generate(self._output, self._rt_inspector)

        return te.stop()


    def save_file(self, idx):
        """ save the generated file to lvl_{idx}.txt """
        # ready for save
        filename = os.path.join(self._config[CONFIG_OUTPUTPATH]["path"], "lvl-{}.txt".format(idx))
        f = open(filename, 'w')
        f.write(MarioLevel.EncodeLevel(self._output))
        f.close()
        return filename


    def generate_levels(self):
        """ generate the levels and save to path"""
        nlevels = self._config[CONFIG_PARAMS].get('num_levels')
        nlevels = int(nlevels) if nlevels else DEFAULT_NUM_OF_LEVELS

        for i in range(nlevels):
            t = self.generate_level()
            fn = self.save_file(i+1)
            print("level generating time : {:.3f} secs, saved to : '{}'".format(t, fn))
        
