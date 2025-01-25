import pygame
import math
import constants
import random

class Weapon():
    def __init__(self, image, arr_image):
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.arr_image = arr_image
        self.fire = False
        self.nospam = pygame.time.get_ticks()

    def update(self, player):
        shot_cooldown = 300
        arrow = None

        self.rect.center = player.rect.center # follow player movement

        # rotation for the bow
        pos = pygame.mouse.get_pos()
        x_distance = pos[0] - self.rect.centerx # set to follow mouse movement
        y_distance = -(pos[1] - self.rect.centery) # negative since pygame coords increase as you go downward
        self.angle = math.degrees(math.atan2(y_distance, x_distance)) # angle between positive x axis and x,y

        # add shooting arrows whenever mouse click left button ONCE.
        if pygame.mouse.get_pressed()[0] and self.fire == False and (pygame.time.get_ticks() - self.nospam) >= shot_cooldown:
            # create arrow same angle as the bow
            arrow = Arrow(self.arr_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fire = True
            self.nospam = pygame.time.get_ticks()

        # reset mouseclick
        if pygame.mouse.get_pressed()[0] == False:
            self.fire = False

        return arrow


    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width()/2), self.rect.centery - int(self.image.get_height()/2)))
        # centering around the center of self.rect based on the width of the image itself
        # top left corner of the image
        # pygame rotates an image around top left corner by default

class Arrow(pygame.sprite.Sprite):
    def __init__(self, image, x,y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_img = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_img, self.angle-90) #account for arrow angle not matching bow
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        # calculate horizontal/vertical speeds based on angle
        self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)

    def update(self, screen_scroll, enemy_list, obstacles):
        # reset variables
        damage = 0
        damage_position = None

        # reposition based on speed and screen scroll
        # check for collision
        self.rect.x += screen_scroll[0] + self.dx
        for obstacle in obstacles:
            if obstacle[1].colliderect(self.rect):  # check for collision with Rect
                self.kill()

        self.rect.y += screen_scroll[1] + self.dy

        # check if arrow off screen
        if self.rect.right < 0 or self.rect.left > constants.WIDTH or self.rect.bottom < 0 or self.rect.top > constants.HEIGHT:
            self.kill() # remove arrow from sprite group



        # check collision of arrow and enemy
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5, 5)
                enemy.health -= damage
                damage_position = enemy.rect
                print(enemy.health)
                enemy.hit = True
                self.kill() # remove arrow if hit
                break

        return damage, damage_position

    # sprite no need
    def draw(self, surface):
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width()/2), self.rect.centery - int(self.image.get_height()/2)))

class Arrow(pygame.sprite.Sprite):
    def __init__(self, image, x,y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_img = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_img, self.angle-90) #account for arrow angle not matching bow
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        # calculate horizontal/vertical speeds based on angle
        self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)

    def update(self, screen_scroll, enemy_list, obstacles):
        # reset variables
        damage = 0
        damage_position = None

        # reposition based on speed and screen scroll
        # check for collision
        self.rect.x += screen_scroll[0] + self.dx
        for obstacle in obstacles:
            if obstacle[1].colliderect(self.rect):  # check for collision with Rect
                self.kill()

        self.rect.y += screen_scroll[1] + self.dy

        # check if arrow off screen
        if self.rect.right < 0 or self.rect.left > constants.WIDTH or self.rect.bottom < 0 or self.rect.top > constants.HEIGHT:
            self.kill() # remove arrow from sprite group



        # check collision of arrow and enemy
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + random.randint(-5, 5)
                enemy.health -= damage
                damage_position = enemy.rect
                print(enemy.health)
                enemy.hit = True
                self.kill() # remove arrow if hit
                break

        return damage, damage_position

    # sprite no need
    def draw(self, surface):
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width()/2), self.rect.centery - int(self.image.get_height()/2)))

class Fireball(pygame.sprite.Sprite):
    def __init__(self, image, x,y, target_x, target_y):
        pygame.sprite.Sprite.__init__(self)
        self.original_img = image
        x_distance = target_x - x
        y_distance = -(target_y - y)
        self.angle = math.degrees(math.atan2(y_distance, x_distance))
        self.image = pygame.transform.rotate(self.original_img, self.angle-90) #account for arrow angle not matching bow
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

        # calculate horizontal/vertical speeds based on angle
        self.dx = math.cos(math.radians(self.angle)) * constants.FIREBALL_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.FIREBALL_SPEED)

    def update(self, screen_scroll, player):
        # reposition based on speed
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        # check if fireball has gone off screen
        if self.rect.right < 0 or self.rect.left > constants.WIDTH or self.rect.bottom < 0 or self.rect.top > constants.WIDTH:
            self.kill()

        # check collision between self and player
        if player.rect.colliderect(self.rect) and player.hit == False:
            player.hit = True
            player.last_hit = pygame.time.get_ticks()
            player.health -= 10
            self.kill()


    # sprite no need
    def draw(self, surface):
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width()/2), self.rect.centery - int(self.image.get_height()/2)))