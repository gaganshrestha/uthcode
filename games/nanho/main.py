import sys
import random
import os
import math
import pygame
import pymunk

from pygame.locals import *
from pygame.color import *
from pymunk import Vec2d

__version__ = 0.5

def to_pygame(point):
    """Hack to convert pymunk to pygame coordinates"""
    return int(point.x), int(-point.y+500)

def background_image(file_name, colorkey=None):
    full_path = os.path.join('assets', file_name)
    try:
        image = pygame.image.load(full_path)
    except pygame.error, message:
        print 'Cannot load image', full_path
        raise SystemExit, message

    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    # Returns a converted image and Rect obj
    return image, image.get_rect()

def load_image(file_name, colorkey=None):
    full_path = os.path.join('assets', file_name)
    try:
        image = pygame.image.load(full_path)
    except pygame.error, message:
        print 'Cannot load image', full_path
        raise SystemExit, message

    return image, image.get_rect()

class GameSprite(pygame.sprite.Sprite):

    def __init__(self, file_name, colorkey=None):
        self.image, self.rect = load_image(file_name)

def create_bananas(space):
    mass = 10
    size = 50
    points = [(-size, -size), (-size, size), (size, size), (size, -size)]
    moment = pymunk.moment_for_poly(mass, points, (0, 0))
    body = pymunk.Body(mass, moment)
    x = random.randint(0, 500)
    body.position = Vec2d(x, x)
    banana = pymunk.Poly(body, points, (0, 0))
    banana.elasticity = 0.95
    space.add(body, banana)
    return banana

def create_primate(space):
    mass = 1
    radius = 25
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
    body = pymunk.Body(mass, inertia)
    body.position = 10, 10
    primate = pymunk.Circle(body, radius, (0, 0))
    primate.elasticity = 0.95
    primate.friction = 25
    space.add(body, primate)
    return primate

def draw_border_walls(space):
    static_body = pymunk.Body()
    # x1,y1, x2,y2
    static_lines = [pymunk.Segment(static_body, (0.0, 0.0), (0.0, 500.0), 5.0),
                    pymunk.Segment(static_body, (0.0, 500.0), (800.0, 500.0), 5.0),
                    pymunk.Segment(static_body, (800.0, 500.0), (800.0, 0.0), 5.0),
                    pymunk.Segment(static_body, (800.0, 0.0), (0.0, 0.0), 5.0)
                   ]
    for line in static_lines:
        line.elasticity = 0.7
        line.group = 1
    space.add(static_lines)
    return static_lines

def draw_logs(space):
    static_body = pymunk.Body()
    static_logs = [pymunk.Segment(static_body, (200, 300), (350, 300), 5)]
    for logs in static_logs:
        logs.elasticity = 1
        logs.group = 1
    space.add(static_logs)
    return static_logs

def draw_flippers(space):
    # Add Flippers
    fp = [(20, -20), (-120, 0), (20, 20)]
    mass = 100
    moment = pymunk.moment_for_poly(mass, fp)

    # right flipper
    r_flipper_body = pymunk.Body(mass, moment)
    r_flipper_body.position = 750, 10
    r_flipper_shape = pymunk.Poly(r_flipper_body, fp)
    space.add(r_flipper_body, r_flipper_shape)

    r_flipper_joint_body = pymunk.Body()
    r_flipper_joint_body.position = r_flipper_body.position
    j = pymunk.PinJoint(r_flipper_body, r_flipper_joint_body, (0, 0), (0, 0))
    s = pymunk.DampedRotarySpring(r_flipper_body, r_flipper_joint_body, 0.15, 20000000, 900000)
    space.add(j, s)

    # left flipper
    l_flipper_body = pymunk.Body(mass, moment)
    l_flipper_body.position = 10, 10
    l_flipper_shape = pymunk.Poly(l_flipper_body, [(-x, y) for x, y in fp])
    space.add(l_flipper_body, l_flipper_shape)

    l_flipper_joint_body = pymunk.Body()
    l_flipper_joint_body.position = l_flipper_body.position
    j = pymunk.PinJoint(l_flipper_body, l_flipper_joint_body, (0, 0), (0, 0))
    s = pymunk.DampedRotarySpring(l_flipper_body, l_flipper_joint_body, -0.15, 20000000, 900000)
    space.add(j, s)


    r_flipper_shape.group = l_flipper_shape.group = 1
    r_flipper_shape.elasticity = l_flipper_shape.elasticity = 0.4

    return r_flipper_body, r_flipper_shape, l_flipper_body, l_flipper_shape

def add_text(txt):
    if pygame.font:
        FONTCOLOR = (255, 255, 0)
        fontfile = os.path.join('assets', 'arcade.ttf')
        font = pygame.font.Font(fontfile, 36)
        text = font.render(txt, 0, FONTCOLOR)
        textpos = text.get_rect()
        return text, textpos

def load_music(music_file):
    if pygame.mixer:
        pygame.mixer.init()
        music = os.path.join('assets', music_file)
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

def main():
    # Primatians - woo
    num_bananas = 0
    trained = False
    play_bg = True
    load_music('bg.mp3')

    pygame.init()
    screen = pygame.display.set_mode((800, 500), pygame.RESIZABLE)
    pygame.display.set_caption("Primatians  - A Nanho Games Production")

    bg, bg_rect = background_image('rainforest.png')

    screen.blit(bg, (0, 0))

    clock = pygame.time.Clock()
    running = True

    # Physics stuff
    space = pymunk.Space(50)
    space.gravity = (90, -90.0)

    # Balls
    bananas = []
    for n in range(1):
        b = create_bananas(space)
        bananas.append(b)

    # Primates
    primates = []
    p = create_primate(space)
    primates.append(p)

    static_lines = draw_border_walls(space)

    static_logs = draw_logs(space)

    r_flipper_body, r_flipper_shape, l_flipper_body, l_flipper_shape = draw_flippers(space)

    # sprites
    banana_sprite = GameSprite('banana-small.png')
    primate1_sprite = GameSprite('primate3.png')
    log_sprite = GameSprite("log2.png")

    # Game Ahoy!

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif (event.type == KEYDOWN and event.key == K_z) or (event.type == KEYDOWN and event.key == K_LEFT):
                l_flipper_body.apply_impulse(Vec2d.unit() * -40000, (-100, 0))
            elif (event.type == KEYDOWN and event.key == K_x) or (event.type == KEYDOWN and event.key == K_RIGHT):
                r_flipper_body.apply_impulse(Vec2d.unit() * 40000, (-100, 0))

        screen.blit(bg, (0, 0))

        # Draw lines

        for line in static_lines:
            body = line.body
            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            p1 = to_pygame(pv1)
            p2 = to_pygame(pv2)
            pygame.draw.lines(screen, THECOLORS["black"], False, [p1, p2])

        # Draw logs

        for log in static_logs:
            body = log.body
            point = body.position + log.b.rotated(body.angle)
            p = to_pygame(point)
            screen.blit(log_sprite.image, p)

        for banana in bananas:
            p = to_pygame(banana.body.position)
            angle_degrees = math.degrees(banana.body.angle) + 180
            rotated_img = pygame.transform.rotate(banana_sprite.image, angle_degrees)
            screen.blit(rotated_img, p)
            # Assigning to rect.center moves the Rect object.
            # Useful for collision detection
            banana_sprite.rect.center = p

        for primate in primates:
            p = to_pygame(primate.body.position)
            screen.blit(primate1_sprite.image, p)
            primate1_sprite.rect.center = p


        r_flipper_body.position = 790, 10
        l_flipper_body.position = 10, 10

        r_flipper_body.velocity = l_flipper_body.velocity = 0, 0

        for f in [r_flipper_shape, l_flipper_shape]:
            ps = f.get_points()
            ps.append(ps[0])
            ps = map(to_pygame, ps)
            color = THECOLORS["burlywood4"]
            pygame.draw.polygon(screen, color, ps, 0)

        if pygame.sprite.collide_rect(primate1_sprite, banana_sprite):
            num_bananas += 1
            txt = "Yummy Bananas %d" % num_bananas
            text, textpos = add_text(txt)
            screen.blit(text, (750, 450))
            if num_bananas == 5:
                trained = True
                play_bg = False
            # Reset Sprites location
            x = random.randint(0, 500)
            banana.body.position = Vec2d(x, x)
            banana.body.reset_forces()
            banana.body.velocity = Vec2d(10, 10)

        txt = "Yummy Bananas %d" % num_bananas
        text, textpos = add_text(txt)
        screen.blit(text, (400, 50))

        if trained:
            txt = "You've trained me. Yay!"
            text, textpos = add_text(txt)
            screen.blit(text, (400, 100))
            banana.body.velocity = Vec2d(0, 0)
            primate.body.velocity = Vec2d(0, 0)
            banana.body.rotation = Vec2d(0, 0)
            if not play_bg:
                pygame.mixer.quit()
                load_music('final.wav')
                play_bg = True

        # Update physics
        dt = 1.0/60.0/5

        for x in range(5):
            space.step(dt)

        pygame.display.flip()
        clock.tick(50)

if __name__ == '__main__':
    sys.exit(main())
