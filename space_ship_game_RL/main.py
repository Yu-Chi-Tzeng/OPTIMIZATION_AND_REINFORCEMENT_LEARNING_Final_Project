import argparse
import pygame
import sys
from setting import *
from game import Game

pygame.init()
pygame.font.init()

# Add argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pygame for RL")

clock = pygame.time.Clock()

# Pass debug flag to Game
game = Game(debug=args.debug)

running = True

count = 0
reward = 0
while running:
    # Checking for events
    for event in pygame.event.get():
        # Highest score=10000
        if event.type == pygame.QUIT or game.score >= 10000:
            pygame.quit()
            sys.exit()

    # Update
    if game.running:
        game.update(action=3)

    # Drawing
    if game.running:
        game.draw(screen)

    pygame.display.update()
    clock.tick(FPS)


    if game.is_collided:
        reward -= 100
    
    if count % FPS == 0:
        print(reward+game.score)
    
    count += 1

print("game score", game.score)
pygame.quit()


