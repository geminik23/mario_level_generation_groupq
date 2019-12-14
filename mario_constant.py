import enum
from datetime import datetime

DEFAULT_BLOCK_UNIT = 2
DEFAULT_NUM_OF_LEVELS = 1
DEFAULT_STATE = 0

CONFIG_INPUTPATH = "InputPath"
CONFIG_OUTPUTPATH = "OutputPath"
CONFIG_PARAMS = "Params"
DEST_WIDTH= 150
DEST_HEIGHT = 16
DEST_SIZE = (DEST_HEIGHT, DEST_WIDTH)

MARIO_START_POSITION = 4
MARIO_EXIT_POSITION = 2

JUMP_MAXIMUM_H = 4
JUMP_MAXIMUM_W = 4


# for time estimation
class TimeEstimate:
    """
    Estimate the time
    """
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


# 
# ALL_TILES = [EMPTY, GROUND, PYRAMID_BLOCK, NORMAL_BRICK, COIN_BRICK, LIFE_BRICK, SPECIAL_BRICK, SPECIAL_QUESTION_BLOCK, COIN_QUESTION_BLOCK, COIN_HIDDEN_BLOCK, LIFE_HIDDEN_BLOCK, USED_BLOCK, COIN, PIPE, PIPE_FLOWER, BULLET_BILL, PLATFORM_BACKGROUND, PLATFORM, GOOMBA, GOOMBA_WINGED, RED_KOOPA, RED_KOOPA_WINGED, GREEN_KOOPA, GREEN_KOOPA_WINGED, SPIKY, SPIKY_WINGED] 

ALL_ENEMY = [MarioSprite.GOOMBA.value, 
        MarioSprite.GOOMBA_WINGED.value, 
        MarioSprite.RED_KOOPA.value,
        MarioSprite.RED_KOOPA_WINGED.value,
        MarioSprite.GREEN_KOOPA.value,
        MarioSprite.GREEN_KOOPA_WINGED.value,
        MarioSprite.SPIKY.value,
        MarioSprite.SPIKY_WINGED.value]

ALL_SPRITES_TO_BE_REMOVED = [MarioSprite.MARIO_START.value,
        MarioSprite.MARIO_EXIT.value,
        MarioSprite.COIN.value,
        MarioSprite.PLATFORM_BACKGROUND.value ] # + ALL_ENEMY


