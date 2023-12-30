import sys
import os

import pygame

import config
import constants

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, player_group)
        self.jump_height = -250
        self.image = load_image('circle.png')
        self.player_width = self.image.get_rect().width
        self.player_height = self.image.get_rect().height
        self.rect = self.image.get_rect()
        self.dx = 100 / constants.FPS
        self.moves_right = False
        self.moves_left = False
        self.jumps = False
        self.falls = False
        self.dy = 0

    def move(self, key_down):
        if key_down[config.key_right] and self.rect.x + self.dx + self.player_width < constants.WIDTH:
            self.rect.x += self.dx
        if key_down[config.key_left] and self.rect.x - self.dx > 0:
            self.rect.x += -self.dx

    def update(self):
        if self.dy > 0:
            self.falls = True
        if (
                not pygame.sprite.spritecollideany(self,
                                                   tile_group)) or self.rect.y + self.player_height < constants.HEIGHT:
            self.dy += constants.GRAVITY
        if self.rect.y + self.player_height >= constants.HEIGHT:
            self.dy = 0
        if pygame.sprite.spritecollideany(self, tile_group):
            collide_sprites = pygame.sprite.spritecollide(self, tile_group, False)
            for sprite in collide_sprites:
                if pygame.sprite.collide_rect(self, sprite) and self.moves_right and abs(
                        self.rect.y - sprite.rect.y) < constants.SPRITE_WIDTH:
                    self.moves_right = False
                    self.rect.x = sprite.rect.x - self.rect.width
                if pygame.sprite.collide_rect(self, sprite) and self.moves_left and abs(
                        self.rect.y - sprite.rect.y) < constants.SPRITE_WIDTH:
                    self.moves_left = False
                    self.rect.x = sprite.rect.x + sprite.rect.width
                if pygame.sprite.collide_rect(self, sprite) and self.jumps and abs(
                        self.rect.x - sprite.rect.x) < constants.SPRITE_HEIGHT:
                    self.jumps = False
                    self.rect.y = sprite.rect.y + sprite.rect.height
                if pygame.sprite.collide_rect(self, sprite) and self.falls and abs(
                    self.rect.x - sprite.rect.x) < constants.SPRITE_HEIGHT:
                    self.falls = False
                    self.rect.y = sprite.rect.y + self.rect.width
        if self.rect.y + self.player_height > constants.HEIGHT:
            self.rect.y = constants.HEIGHT - self.player_height
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x + self.player_width > constants.WIDTH:
            self.rect.x = constants.WIDTH - self.player_width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y + (self.dy / constants.FPS) >= 0:
            self.rect.y += self.dy / constants.FPS

    def player_jump(self):
        if self.dy == 0 and (pygame.sprite.spritecollideany(self,
                                                            tile_group) or self.rect.y + self.player_height == constants.HEIGHT):
            self.dy = self.jump_height
            self.rect.y += self.dy / 100


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y):
        groups = [all_sprites, tile_group]
        super().__init__(*groups)
        if tile_type == 'grass':
            self.image = load_image('grass.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с низображением {fullname} не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


grass_image = load_image('grass.png')


def load_level(filename):
    for i in tile_group.sprites():
        all_sprites.remove(i)
    tile_group.empty()
    with open(filename, 'r') as level:
        level_information = level.read().split('\n')
        for i in range(len(level_information)):
            for j in range(len(level_information[i])):
                if level_information[i][j] == constants.GRASS_SYMBOL:
                    Tile('grass', j * constants.SPRITE_WIDTH, i * constants.SPRITE_HEIGHT)


def main():
    pygame.init()
    running = True
    pygame.display.set_caption('Платформер')
    player = Player()
    key_down = {config.key_left: False, config.key_right: False, config.key_up: False}
    load_level('level_1.txt')
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == config.key_right:
                    key_down[config.key_right] = True
                    player.moves_right = True
                if event.key == config.key_left:
                    key_down[config.key_left] = True
                    player.moves_left = True
                if event.key == config.key_up:
                    key_down[config.key_up] = True
                    player.jumps = True
            if event.type == pygame.KEYUP:
                key_down[event.key] = False
                if event.type == config.key_right:
                    player.moves_right = False
                if event.type == config.key_left:
                    player.moves_left = False
        if any(key_down.items()):
            player.move(key_down)
            if key_down[config.key_up]:
                player.player_jump()
        screen.fill(pygame.Color((0, 0, 0)))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(constants.FPS)


if __name__ == '__main__':
    sys.exit(main())
