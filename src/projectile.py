from settings import *
import pygame
from time import sleep

class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos, groups, facing, hit_sprites, magic_power, radius=FIREBALL_RADIUS) -> None:
        super().__init__(groups)
        self.sprite_sheet = pygame.image.load("img/spells/fireball.png").convert_alpha()
        self.image = self.get_sprite(self.sprite_sheet, 0, 0, 48, 48)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-25,-25)
        self.start_x = self.hitbox.x
        self.start_y = self.hitbox.y

        self.radius = radius
        self.facing = facing
        self.direction = None
        self.collide = False
        self.magic_power = magic_power

        self.shoot_animation = [self.get_sprite(self.sprite_sheet, i, 0, 48, 48) for i in range(4)]
        self.explode_animation = [self.get_sprite(self.sprite_sheet, i, 0, 48, 48, 5*48) for i in range(6)]

        self.image_index = 0
        self.animation_speed = 0.1  # Szybkość animacji pocisku
        self.explosion_speed = 0.1
        self.animation_timer = 0

        self.hit_sprites = hit_sprites

        # efekty głosowe
        self.fireball_channel = pygame.mixer.Channel(2)

        self.fireball_sound = pygame.mixer.Sound("sounds/effects/fireball.mp3")
        self.fireball_sound.set_volume(0.3)
        self.fireball_channel.play(self.fireball_sound)

        self.explosion_sound = pygame.mixer.Sound("sounds/effects/explosion.wav")
        self.explosion_sound.set_volume(0.3)
        self.explosion_sound.fadeout(2)

        # tutaj zmieniamy rotację obrazu fireball w zależności od kierunku w którym został wystrzelony
        # oraz przesuwamy go tak, żeby był spójny wraz z animacją gracza
        if self.facing == "up":
            self.hitbox.move_ip(-15,-15)
            self.direction = "vertical"
            self.vel = FIREBALL_SPEED * -1
            self.image = pygame.transform.rotate(self.image, 90)
            self.shoot_animation = [pygame.transform.rotate(i, 90) for i in self.shoot_animation]
            self.explode_animation = [pygame.transform.rotate(i, 90) for i in self.explode_animation]
        elif self.facing == "down":
            self.hitbox.move_ip(-15,-10)
            self.direction = "vertical"
            self.vel = FIREBALL_SPEED * 1
            self.image = pygame.transform.rotate(self.image, -90)
            self.shoot_animation = [pygame.transform.rotate(i, -90) for i in self.shoot_animation]
            self.explode_animation = [pygame.transform.rotate(i, -90) for i in self.explode_animation]
        elif self.facing == "left":
            self.hitbox.move_ip(-40,-20)
            self.direction = "horizontal"
            self.vel = FIREBALL_SPEED * -1
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
            self.shoot_animation = [pygame.transform.flip(i, flip_x=True, flip_y=False) for i in self.shoot_animation]
            self.explode_animation = [pygame.transform.flip(i, flip_x=True, flip_y=False) for i in self.explode_animation]
        elif self.facing == "right":
            self.hitbox.move_ip(-10,-20)
            self.direction = "horizontal"
            self.vel = FIREBALL_SPEED * 1

    # wycinamy jeden obraz z sprite
    def get_sprite(self, sheet, x, y, width, height, offset = 0):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (x * width + offset, y * height, width, height))
        return image
    
    # wykrywamy kolizję, i jeżeli przeszkoda ma moduł take_damage() to zabieramy mu życie
    def collision(self):
        for sprite in self.hit_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                self.collide = True
                self.image_index = 0
                self.animation_timer = 0
                
                self.fireball_channel.stop()
                self.fireball_channel.play(self.explosion_sound)

                if hasattr(sprite, 'take_damage'):
                    sprite.take_damage(spell_data['fireball']['damage']*self.magic_power)

    # efekt głosowy
    def play_sound(self, sound):
        sound.play()

    def update(self):
        self.current_x = self.hitbox.x
        self.current_y = self.hitbox.y

        if not self.collide:
            if self.direction == "vertical":
                self.hitbox.y += self.vel
                if self.vel > 0:
                    self.rect.centerx = self.hitbox.centerx+5
                    self.rect.centery = self.hitbox.centery
                else:
                    self.rect.centerx = self.hitbox.centerx-5
                    self.rect.centery = self.hitbox.centery

            elif self.direction == "horizontal":
                self.hitbox.x += self.vel
                self.rect.centerx = self.hitbox.centerx
                self.rect.centery = self.hitbox.centery-5

            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.image_index = (self.image_index + 1) % len(self.shoot_animation)
                self.image = self.shoot_animation[self.image_index]

            self.collision()
        else:
            self.animation_timer += self.explosion_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.image_index += 1
                self.image = self.explode_animation[self.image_index]
                
            if self.image_index >= len(self.explode_animation) - 1:
                self.kill()

        # nisczymy pocisk jeżeli osiągnał swój radius
        if abs(self.start_x - self.current_x) > self.radius or abs(self.start_y - self.current_y) > self.radius:
            self.kill()


class Laserbeam(pygame.sprite.Sprite):
    def __init__(self, pos, groups, facing, hit_sprites, magic_power) -> None:
        super().__init__(groups)

        self.sprite_sheet = pygame.image.load("img/spells/laserbeam.png").convert_alpha()
        self.image = self.get_sprite(self.sprite_sheet, 0, 0, 256, 64)
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.move_ip(10, -15)
        self.hitbox = self.rect.inflate(-10,-40)
        self.magic_power = magic_power

        self.facing = facing
        self.hit_sprites = hit_sprites

        self.image_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0

        self.animation = [self.get_sprite(self.sprite_sheet, 0, i, 256, 64) for i in range(7)]

        self.laserbeam_channel = pygame.mixer.Channel(3)
        self.laserbeam_sound = pygame.mixer.Sound("sounds/effects/laserbeam.mp3")
        self.laserbeam_sound.set_volume(0.3)
        
        self.laserbeam_channel.play(self.laserbeam_sound)

        # zmieniamy rotację obrazu Laserbeam, w zależności od tego w którą
        # stronę został wystrzelony
        if self.facing == "up":
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect(topleft=pos)
            self.animation = [pygame.transform.rotate(i, 90) for i in self.animation]
            self.rect.move_ip(-20, -250)
            self.hitbox = self.rect.inflate(-40,-10)
        elif self.facing == "down":
            self.image = pygame.transform.rotate(self.image, -90)
            self.rect = self.image.get_rect(topleft=pos)
            self.animation = [pygame.transform.rotate(i, -90) for i in self.animation]
            self.rect.move_ip(-30, 5)
            self.hitbox = self.rect.inflate(-40,-10)
        elif self.facing == "left":
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
            self.rect = self.image.get_rect(topleft=pos)
            self.animation = [pygame.transform.flip(i, flip_x=True, flip_y=False) for i in self.animation]
            self.rect.move_ip(-260, -20)
            self.hitbox = self.rect.inflate(-10,-40)

    def get_sprite(self, sheet, x, y, width, height, offset = 0):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (x * width, y * height, width, height))
        return image
    
    # wykrywamy kolizję i zabieramy życie jeżeli trafiliśmy przeciwnika
    def collision(self):
        for sprite in self.hit_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                self.collide = True
                print("Laser beam hits target!")

                if hasattr(sprite, 'take_damage'):
                    sprite.take_damage(spell_data['laserbeam']['damage']*self.magic_power)

    def update(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.image_index += 1
            self.image = self.animation[self.image_index]
        
        self.collision()
                
        if self.image_index >= len(self.animation) - 1:
            self.kill()