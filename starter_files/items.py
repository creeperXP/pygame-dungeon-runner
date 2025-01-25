# collectibles: coins and potions
import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, animation_list):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type # 0 = coin, 1 = health potion
        self.animation_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self, screen_scroll, player, coin_fx, heal_fx):
        # reposition based on screen scrolling
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # check if item collected by player
        if self.rect.colliderect(player.rect):
            # coin collection
            if self.item_type == 0:
                player.score += 1
                coin_fx.play()
            elif self.item_type == 1:
                player.health += 10
                heal_fx.play()
                if player.health > 100:
                    player.health = 100


            self.kill()

        cooldown = 150

        # handle animation, update image for idle
        self.image = self.animation_list[self.frame_index]

        # check if enough time passed
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if animation finished
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
