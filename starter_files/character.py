import pygame
import constants
import weapon
import math

class Character():
    # pass in animations
    def __init__(self,x,y, health, mob_animations, char_type, boss, size):
        self.char_type = char_type

        self.boss = boss

        self.flip = False
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0
        self.action = 0  # 0:idle, 1:run
        self.update_time = pygame.time.get_ticks() # measure frames to change
        self.running = False
        self.image = self.animation_list[self.action][self.frame_index] # first image is the idle animation
        self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
        self.rect.center = (x, y)

        self.health = health
        self.alive = True

        self.score = 0

        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.stunned = False
        self.last_attack = pygame.time.get_ticks()


    def draw(self, screen):
        flipImage = pygame.transform.flip(self.image, self.flip, False) # true flip vertically, false horizontally

        # check if original character (elf)
        if self.char_type == 0:
            screen.blit(flipImage, (self.rect.x, self.rect.y - constants.SCALE * constants.OFFSET)) # use modified to put relative to player
        else:
            screen.blit(flipImage, self.rect)

        # pygame.draw.rect(screen, constants.RED, self.rect, 1)?

    def move(self, dx, dy, obstacles, exit_tile = None):
        level_complete = False
        self.running = False

        screen_scroll = [0,0]

        # check if moving (to change animations)
        if dx != 0 or dy != 0:
            self.running = True

        # check if flip
        if dx < 0:
            self.flip = True


        if dx > 0:
            self.flip = False

        # control diagonal speed since hypotenuse
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/2)
            dy = dy * (math.sqrt(2)/2)

        # check for collision with map in x direction
        self.rect.x += dx
        for obstacle in obstacles:
            if obstacle[1].colliderect(self.rect): # check for collision with Rect
                # check which side collision is from
                if dx > 0:
                    self.rect.right = obstacle[1].left # player moving right: set to left side of wall
                if dx < 0:
                    self.rect.left = obstacle[1].right # player moving left: set to right side of wall

        # check for collision in y direction
        self.rect.y += dy
        for obstacle in obstacles:
            if obstacle[1].colliderect(self.rect): # check for collision with Rect
                # check which side collision is from
                if dy > 0:
                    self.rect.bottom = obstacle[1].top # player moving down: set to top side of wall
                if dy < 0:
                    self.rect.top = obstacle[1].bottom # player moving up: set to bottom side of wall

        # check if player out of boundaries
        if self.char_type == 0:
            # check collision with exit tile
            if exit_tile[1].colliderect(self.rect):
                # center only
                exit_distance = math.sqrt((self.rect.centerx - exit_tile[1].centerx)**2 + (self.rect.centery - exit_tile[1].centery)**2)
                if exit_distance < 20:
                    level_complete = True

            # update scroll based on player position
            # horizontal
            if self.rect.right > (constants.WIDTH - constants.SCROLL_THRESH): # x axis
                screen_scroll[0] = (constants.WIDTH - constants.SCROLL_THRESH) - self.rect.right # make player look stationary
                self.rect.right = constants.WIDTH - constants.SCROLL_THRESH
            if self.rect.left < constants.SCROLL_THRESH:
                screen_scroll[0] = constants.SCROLL_THRESH - self.rect.left
                self.rect.left = constants.SCROLL_THRESH

            # vertical
            if self.rect.bottom > (constants.HEIGHT - constants.SCROLL_THRESH):
                screen_scroll[1] = (constants.HEIGHT - constants.SCROLL_THRESH) - self.rect.bottom  # make player look stationary
                self.rect.bottom = constants.HEIGHT - constants.SCROLL_THRESH
            if self.rect.top < constants.SCROLL_THRESH:
                screen_scroll[1] = constants.SCROLL_THRESH - self.rect.top
                self.rect.top = constants.SCROLL_THRESH

        return screen_scroll, level_complete

    # update animation based on moving or idle
    def update_animation(self, new_action):
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frameindex = 0
            self.updatetime = pygame.time.get_ticks()

    def ai(self, player, screen_scroll, obstacles, fire_image):
        fireball = None
        dx = 0
        dy = 0
        clipped = ()
        stun_cooldown = 100

        # reposition mobs based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # create line of sight from enemy to player
        line = ((self.rect.centerx, self.rect.centery) , (player.rect.centerx, player.rect.centery)) # 2 coordinates as start/end
        # check if line of sight passes through obstacle tile
        for obstacle in obstacles:
            if obstacle[1].clipline(line):
                clipped = obstacle[1].clipline(line)

        # check enemy distance to player
        dist = math.sqrt((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)

        # if no intersection (wall) then can move to player
        if not clipped and dist > constants.RANGE: # stop when close to player
            # calculate movement towards the player
            if self.rect.centerx > player.rect.centerx: # move enemy left
                dx = -constants.ENEMY_SPEED
            if self.rect.centerx < player.rect.centerx: # move enemy right
                dx = constants.ENEMY_SPEED
            if self.rect.centery > player.rect.centery: # move enemy up
                dy = -constants.ENEMY_SPEED
            if self.rect.centery < player.rect.centery: # move enemy down
                dy = constants.ENEMY_SPEED

        # if character alive, then use attack, hit, stun
        if self.alive:
            if not self.stunned:
                self.move(dx, dy, obstacles)
                # attack player
                if dist < constants.ATTACK_RANGE and player.hit == False:
                    player.health -= 10
                    player.hit = True
                    player.last_hit = pygame.time.get_ticks()

                # boss shoots fireballs
                fireball_cooldown = 700
                if self.boss:
                    if dist < 500:
                        if pygame.time.get_ticks() - self.last_attack >= fireball_cooldown:
                            fireball = weapon.Fireball(fire_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                            self.last_attack = pygame.time.get_ticks()



            # check if hit
            if self.hit == True:
                self.hit = False
                self.last_hit = pygame.time.get_ticks()
                self.stunned = True
                self.running = False
                self.update_animation(0)

            if (pygame.time.get_ticks() - self.last_hit) > stun_cooldown:
                self.stunned = False

        return fireball

    def update(self):
        cooldown = 70

        # check if character died
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # reset enemy taking a hit
        hit_cooldown = 1000
        if self.char_type == 0:
            if self.hit == True and ((pygame.time.get_ticks() - self.last_hit) >= hit_cooldown):
                self.hit = False

        # check what action player is performing
        if self.running:
            self.update_animation(1)
        else:
            self.update_animation(0)

        # handle animation, update image for idle
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time passed
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if animation finished
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

