import enum
import os
import sys
from random import Random, choices


# Mario Sprite Enums
class MarioSprite(enum.Enum):
    # start and end of the level
    MARIO_START = 'M'
    MARIO_EXIT = 'F'
    EMPTY = '-'

    # game tiles symbols
    GROUND = 'X'
    PYRAMID_BLOCK = '#'
    NORMAL_BRICK = 'S'
    COIN_BRICK = 'C'
    LIFE_BRICK = 'L'
    SPECIAL_BRICK = 'U'
    SPECIAL_QUESTION_BLOCK = '@'
    COIN_QUESTION_BLOCK = '!'
    COIN_HIDDEN_BLOCK = '2'
    LIFE_HIDDEN_BLOCK = '1'
    USED_BLOCK = 'D'
    COIN = 'o'
    PIPE = 't'
    PIPE_FLOWER = 'T'
    BULLET_BILL = '*'
    PLATFORM_BACKGROUND = '|'
    PLATFORM = '%'

    # enemies that can be in the level
    GOOMBA = 'g'
    GOOMBA_WINGED = 'G'
    RED_KOOPA = 'r'
    RED_KOOPA_WINGED = 'R'
    GREEN_KOOPA = 'k'
    GREEN_KOOPA_WINGED = 'K'
    SPIKY = 'y'
    SPIKY_WINGED = 'Y'
#ALL_TILES = [EMPTY, GROUND, PYRAMID_BLOCK, NORMAL_BRICK, COIN_BRICK, LIFE_BRICK, SPECIAL_BRICK, SPECIAL_QUESTION_BLOCK, COIN_QUESTION_BLOCK, COIN_HIDDEN_BLOCK, LIFE_HIDDEN_BLOCK, USED_BLOCK, COIN, PIPE, PIPE_FLOWER, BULLET_BILL, PLATFORM_BACKGROUND, PLATFORM, GOOMBA, GOOMBA_WINGED, RED_KOOPA, RED_KOOPA_WINGED, GREEN_KOOPA, GREEN_KOOPA_WINGED, SPIKY, SPIKY_WINGED] 

DEST_PATH = "/home/geminik23/workspace/__java__/ecs7002p-marioai/levels/groupq"
#DEST_PATH = "./"


# probablity
# how to ?

rand = Random()


ORDER = 1
UNIT = 3
START = [[],[],[],[]]
MAPLINE = [{},{},{},{}]


def load_levels(path):
    f = open(path, 'r')
    lines = []
    for line in f.readlines():
        lines.append(line.strip())

    
    print(lines)
    length = len(lines[0])
    for i in range(4): # divide 4 section in row
        a = {}
        # parsing 4 lines
        # 1. save to maps 
        maps = [lines[i*4],lines[i*4+1],lines[i*4+2],lines[i*4+3]]
        
        if length % UNIT != 0:
            length -= length % UNIT
        length -=1

        prev = None
        for l in range(0, length, UNIT):
            data = ''
            for insidel in range(4):
                for u in range(UNIT):
                    data += maps[insidel][l+u]
                    # data = maps[0][l] + maps[0][l+1]
                    # data += maps[1][l] + maps[1][l+1]
                    # data += maps[2][l] + maps[2][l+1]
                    # data += maps[3][l] + maps[3][l+1]


            if prev == None:
                START[i].append(data)
            else:
                if not MAPLINE[i].get(prev):
                    MAPLINE[i][prev] = {}
                count = MAPLINE[i][prev].get(data)
                if count == None: MAPLINE[i][prev][data] = 0
                MAPLINE[i][prev][data] += 1
            prev = data
        pass
    f.close()


def add_sprite(dst, chunk, start, unit):
    for i in range(4):
        l = ''
        for j in range(unit):
            l += chunk[i*unit+j]
        dst[i+start].append(l)
    pass
    
    

def generate():
    # randomly select first part from START
    dest = []
    for i in range(16): dest.append([])

    for i in range(4):
        sel = int(rand.random()* len(START[i]))
        prev = START[i][sel]
        add_sprite(dest, prev, i*4, UNIT)
        for l in range(UNIT, 150, UNIT):
            table = MAPLINE[i].get(prev)
            data = choices([k for k in table.keys()], [v for v in table.values()])
            if type(data) == list:
                data = data[0]
            
            add_sprite(dest, data, i*4, UNIT)
            prev = data
            
            #add_sprite(dest, sel, range(i, i+4), UNIT)
            pass
        
    f = open('{}/test.txt'.format(DEST_PATH), 'w')
    for line in dest:
        l = ''.join(line)
        f.write(l)
        f.write('\n')
    f.close()


    
    pass

if __name__ == '__main__':
    # check generate path
    

    #load all levels...
    levels_path = ['./levels/original']
    # load txt
    for path in levels_path:
        l = os.listdir(levels_path[0])
        datas = []
        [datas.append(d) if d.endswith('txt') else None for d in l]

        for level in datas:
            load_levels("{}/{}".format(levels_path[0], level))

    # generate
    generate()
    
    

