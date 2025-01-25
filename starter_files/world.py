import constants
from items import Item
from character import Character

class World():
    def __init__(self):
        self.tiles = []
        self.obstacles = []
        self.exit = None
        self.items = []
        self.player = None
        self.enemies = []

    def process_data(self, data, tile_list, item_images, mob_animations):
        self.level_length = len(data)

        # for each value in level data file
        for y, row in enumerate(data):
            for x, col in enumerate(row):
                image = tile_list[col]
                image_rect = image.get_rect()
                image_x = x * constants.TILE_SIZE
                image_y = y * constants.TILE_SIZE
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]

                # check if wall tile (7), put in obstacles
                if col == 7:
                    self.obstacles.append(tile_data)
                elif col == 8: # exit tile
                    self.exit = tile_data
                elif col == 9: # coin
                    coin = Item(image_x, image_y, 0, item_images[0])
                    self.items.append(coin)
                    # overwrite image coin to floor
                    tile_data[0] = tile_list[0]
                elif col == 10: # potion
                    potion = Item(image_x, image_y, 1, [item_images[1]])
                    self.items.append(potion)
                    # overwrite image coin to floor
                    tile_data[0] = tile_list[0]
                elif col == 11: # player
                    player = Character(image_x, image_y, 100, mob_animations, 0, False, 1)
                    self.player = player
                    # overwrite image coin to floor
                    tile_data[0] = tile_list[0]
                elif col >= 12 and col <= 16: # enemy
                    enemy = Character(image_x, image_y, 100, mob_animations, col - 11, False, 1)
                    self.enemies.append(enemy)
                    # overwrite image coin to floor
                    tile_data[0] = tile_list[0]
                elif col == 17: # boss
                    enemy = Character(image_x, image_y, 100, mob_animations, 6, True, 2)
                    self.enemies.append(enemy)
                    # overwrite image coin to floor
                    tile_data[0] = tile_list[0]

                # add image data to main tiles list
                # if not -1, is not blank space, so append
                if col >= 0:
                    self.tiles.append(tile_data)

    def draw(self, surface):
        for tile in self.tiles:
            surface.blit(tile[0], tile[1]) # image and where

    # update so player camera is centered
    def update(self, screen_scroll):
        for tile in self.tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])

