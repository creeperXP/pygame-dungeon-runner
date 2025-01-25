# constants used

# game window width/height
WIDTH = 800
HEIGHT = 600
# top panel
PANEL = (50,50,50)

# colors
RED = (255,0,0)
BG = (40,25,25)
MENU_BG = (130, 0, 0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PINK = (235, 65, 54)

# used to determine frame rate
# speed of objects, other scale
# offset of objects collision
FRAME_RATE = 60
SPEED = 5
SCALE = 3
OFFSET = 12

# item/weapon scales
WEAPON_SCALE = 1.5
FIREBALL_SCALE = 1
FIREBALL_SPEED = 4
ARROW_SPEED = 10
ITEM_SCALE = 3
POTION_SCALE = 2

# used in loading the level data
TILE_SIZE = 16 * SCALE # since all is scaled by 3, and each image is 16 px
TILE_TYPES = 18
ROW = 150
COL = 150

# player camera moves centered to this
SCROLL_THRESH = 200

# enemy speed
# how attack works
ENEMY_SPEED = 4
RANGE = 50
ATTACK_RANGE = 60

# button size scale
BUTTON_SCALE = 1
