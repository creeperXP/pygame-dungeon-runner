import pygame

# import class within a file
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World
import csv
from button import Button

from pygame import mixer

# initialize the pygame modules used
pygame.init()

# define game variables (for CSV)
level = 1
screen_scroll = [0, 0] # x and y screen scrolling
start_intro = False
start = False
pause = False

# maintain frame rate overall
clock = pygame.time.Clock()

# create screen
screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
# create tab name
pygame.display.set_caption("Dungeon")


# define the movement of the player
moveleft = False
moveright = False
moveup = False
movedown = False

# helper function to scale image
def scale_image(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h* scale))

# load music and sounds
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000) # loops -1 = infinite, start at 0.0 seconds, fade in over 5000ms (5 sec)

# sound effects
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

# load button images
restart_img = scale_image(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constants.BUTTON_SCALE)
start_img = scale_image(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_image(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_image(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)

# load weapon images
bow_img = scale_image(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_img = scale_image(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_img = scale_image(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

# player health image
health_empty = scale_image(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
health_half = scale_image(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
health_full = scale_image(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

# coin images
coin_images = []
for x in range(4):
    img = scale_image(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(), constants.ITEM_SCALE)
    coin_images.append(img)

# potion image
potion_image = scale_image(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)
item_images = []
item_images.append(coin_images)
item_images.append(potion_image)

# tilemap images
tiles = []
for x in range(constants.TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
    tile_image2 = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tiles.append(tile_image2)


# animations
animation_types = ["idle", "run"]
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]
mob_animations = []

for mob in mob_types:
    animations = []

    for animation in animation_types:
        # create temp list to store both types
        temp = []

        for i in range (4): # frames of animation
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            # optimize image format
            img = pygame.transform.scale(img, ((img.get_width() * constants.SCALE), (img.get_height() * constants.SCALE)))
            temp.append(img)

        #append each list to total animations
        animations.append(temp)
    # add mob animations to animation list
    mob_animations.append(animations)

# font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

# function displaying draw text
def text_display(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# function to display game info
def display_info():
    # panel
    pygame.draw.rect(screen, (constants.PANEL), (0, 0, constants.WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0,50), (constants.WIDTH, 50))
    half_heart = False # only 1 half heart allowed

    # draw lives
    for i in range(5):
        if player.health >= ((i+1) * 20): # need at least 20 health to have full heart
            screen.blit(health_full, (10 + i * 50,0))
        elif player.health %20 > 0 and half_heart == False:
            screen.blit(health_half, (10 + i * 50,0))
            half_heart = True
        else:
            screen.blit(health_empty, (10 + i * 50,0))
    # show level
    text_display("LEVEL: " + str(level), font, constants.WHITE, constants.WIDTH/2, 15)

    # show score
    text_display(f"{player.score}", font, constants.WHITE, constants.WIDTH - 150, 15)

# function to reset level
def reset():
    arrow_group.empty()
    item_group.empty()
    fireball_group.empty()
    # dmg text
    damage_txt_group.empty()

    #empty tile list
    # empty tile list
    data = []
    for row in range(constants.ROW):
        r = [-1] * constants.COL
        data.append(r)
    return data

# grid implementation to see each hitbox
# def draw_grid():
    # for x in range(30):
        # pygame.draw.line(screen, constants.WHITE, (x*constants.TILE_SIZE, 0), (x*constants.TILE_SIZE, constants.HEIGHT)) # x axis
        # pygame.draw.line(screen, constants.WHITE, (0, x*constants.TILE_SIZE), (constants.WIDTH, x*constants.TILE_SIZE)) # y axis

# class for damage text
class DamageTXT(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect() # rectangle from image
        self.rect.center = (x,y)
        self.counter = 0 #remove text after certain seconds

    def update(self):
        # reposition based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        #move damage text up
        self.rect.y -= 1

        # delete text after few sedons
        self.counter+=1
        if self.counter > 30:
            self.kill()

# class for screen fade in/out on entry and death
class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        # complete black: opens from middle out
        if self.direction == 1:
            # center to left
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter,0, constants.WIDTH // 2, constants.HEIGHT))
            # center to right
            pygame.draw.rect(screen, self.color, (constants.WIDTH//2 + self.fade_counter,0, constants.WIDTH // 2, constants.HEIGHT))
            # center to top
            pygame.draw.rect(screen, self.color, (0,0 - self.fade_counter, constants.WIDTH, constants.HEIGHT//2))
            # center to bottom
            pygame.draw.rect(screen, self.color, (0, constants.HEIGHT//2 + self.fade_counter, constants.WIDTH, constants.HEIGHT))
        elif self.direction == 2: # vertical screen fade down
            pygame.draw.rect(screen, self.color, (0,0, constants.WIDTH, 0 + self.fade_counter))

        if self.fade_counter >= constants.WIDTH:
            fade_complete = True
        return fade_complete

# empty tile list
world_data = []
for row in range(constants.ROW):
    r = [-1] * constants.COL
    world_data.append(r)

# load in csv level data
with open(f"levels/level{level}_data.csv", newline="") as csvfile: # no new lines, csvfile = object to be read
    reader = csv.reader(csvfile, delimiter = ",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile) # all string initially

# create the game with the world class
world = World()
world.process_data(world_data, tiles, item_images, mob_animations)

# create character and weapon
player = world.player
bow = Weapon(bow_img, arrow_img)

# create enemies
enemy_list = world.enemies

# create sprite groups
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()
#dmg text
damage_txt_group = pygame.sprite.Group()

# score coin
score_coin = Item(constants.WIDTH - 175, 23, 0, coin_images)

# add items from level data
for item in world.items:
    item_group.add(item)

# create screen fade
intro_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.PINK, 4)

# create button
restart_button = Button(constants.WIDTH // 2 - 175, constants.HEIGHT //2 - 50, restart_img)
start_button = Button(constants.WIDTH // 2 - 145, constants.HEIGHT //2 - 150, start_img)
exit_button = Button(constants.WIDTH // 2 - 110, constants.HEIGHT //2 + 50, exit_img)
resume_button = Button(constants.WIDTH // 2 - 175, constants.HEIGHT //2 - 150, resume_img)

# keep screen (game) running
running = True
while running:

    # control frame rate
    clock.tick(constants.FRAME_RATE)

    # show start button on entry
    # also if exit button is on screen then the game is not running
    if start == False:
        screen.fill(constants.MENU_BG)
        if start_button.draw(screen):
            start = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # display pause button
        if pause == True:
            screen.fill(constants.MENU_BG)
            if resume_button.draw(screen):
                pause = False
            if exit_button.draw(screen):
                run = False
        else:
            # need this to avoid player trail behind
            screen.fill(constants.BG)

            # check if player alive
            if player.alive:

                # draw_grid()

                # calculate x and y movement
                dx = 0
                dy = 0  # dy is vertical, dx is left rihgt
                if moveright:
                    dx = constants.SPEED
                if moveleft:
                    dx = -constants.SPEED
                if moveup:
                    dy = -constants.SPEED
                if movedown:
                    dy = constants.SPEED

                # player moves
                # check for colliison
                screen_scroll, level_complete = player.move(dx, dy, world.obstacles, world.exit)

                # update player and arrow movement
                world.update(screen_scroll)
                player.update()
                arrow = bow.update(player)

                # update enemy/no move
                for enemy in enemy_list:
                    # boss enemy fireball shooting
                    fireball = enemy.ai(player, screen_scroll, world.obstacles, fireball_img)
                    if fireball:
                        fireball_group.add(fireball)
                    # check if enemy alive to continue animation
                    if enemy.alive:
                        enemy.update()

                # check if arrow
                if arrow:
                    arrow_group.add(arrow)
                    shot_fx.play()
                for arrow in arrow_group:
                    # update position of arrow
                    damage, damage_pos = arrow.update(screen_scroll, enemy_list, world.obstacles)
                    # if arrow hit enemy, update the damage
                    if damage:
                        damage_text = DamageTXT(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
                        damage_txt_group.add(damage_text)
                        hit_fx.play()
                damage_txt_group.update()

                # show items
                item_group.update(screen_scroll, player, coin_fx, heal_fx)

                # update boss fireballs based on player movement
                fireball_group.update(screen_scroll, player)

            # draw tiles
            world.draw(screen)

            # can say due to sprite, but need to modify arrow_group.draw(screen)

            # draw player on screen
            for enemy in enemy_list:
                enemy.draw(screen)
            player.draw(screen)
            bow.draw(screen)
            # draw arrows
            for arrow in arrow_group:
                arrow.draw(screen)
            for fireball in fireball_group:
                fireball.draw(screen)
            damage_txt_group.draw(screen)

            item_group.draw(screen)

            # draw health
            display_info()

            # draw score coin since panel overlaps
            score_coin.draw(screen)

            # check level complete
            # if so, load in next level data
            if level_complete == True:
                start_intro = True
                level+=1
                world_data = reset()
                # load in csv level data
                with open(f"levels/level{level}_data.csv", newline="") as csvfile:  # no new lines, csvfile = object to be read
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)  # all string initially

                world = World()
                world.process_data(world_data, tiles, item_images, mob_animations)

                # store previous lvl data
                temp_hp = player.health
                temp_score = player.score

                player = world.player
                # put hp and score
                player.health = temp_hp
                player.score = temp_score

                enemy_list = world.enemies
                score_coin = Item(constants.WIDTH - 115, 23, 0, coin_images)

                for item in world.items:
                    item_group.add(item)

            # show intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            # show death screen
            if player.alive == False:
                if death_fade.fade():
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_intro = True # reset level

                        world_data = reset()
                        # load in csv level data
                        with open(f"levels/level{level}_data.csv",
                                  newline="") as csvfile:  # no new lines, csvfile = object to be read
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)  # all string initially

                        world = World()
                        world.process_data(world_data, tiles, item_images, mob_animations)

                        temp_score = player.score

                        player = world.player

                        player.score = temp_score

                        enemy_list = world.enemies
                        score_coin = Item(constants.WIDTH - 115, 23, 0, coin_images)

                        for item in world.items:
                            item_group.add(item)

    # event handler (key press)
    # quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # take diff keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moveleft = True
            if event.key == pygame.K_w:
                moveup = True
            if event.key == pygame.K_s:
                movedown = True
            if event.key == pygame.K_d:
                moveright = True
            if event.key == pygame.K_ESCAPE: # pause
                pause = True

        # take diff keyboard releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moveleft = False
            if event.key == pygame.K_w:
                moveup = False
            if event.key == pygame.K_s:
                movedown = False
            if event.key == pygame.K_d:
                moveright = False


    pygame.display.update()



pygame.quit()