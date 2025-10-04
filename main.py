import pygame
import sys
import random
from variables import *

pygame.init()

W, H = 800, 600
win = pygame.display.set_mode((W, H))

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

class Game:
    def __init__(self):
        self.player = pygame.Rect(100, 500, 40, 40)
        self.vel_y = 0
        self.on_ground = False
        self.stamina = 10  # starting stamina
        self.score = 0
        self.camera_x = 0
        self.last_checkpoint_x = 0
        self.platforms = []
        self.checkpoints = []
        self.generate_initial_level()

    def generate_initial_level(self):
        # Generate initial platforms
        self.platforms = []
        for i in range(5):
            x = 200 + i * 300
            y = random.randint(400, 500)
            self.platforms.append(pygame.Rect(x, y, 200, 20))
            
            # Add checkpoint every 3 platforms
            if i > 0 and i % 3 == 0:
                self.checkpoints.append(pygame.Rect(x + 100, y - 100, 40, 40))

    def generate_new_section(self):
        last_platform = self.platforms[-1]
        x = last_platform.x + random.randint(250, 350)
        y = random.randint(400, 500)
        self.platforms.append(pygame.Rect(x, y, 200, 20))
        
        # Add new checkpoint every 3rd platform
        if len(self.platforms) % 3 == 0:
            self.checkpoints.append(pygame.Rect(x + 100, y - 100, 40, 40))

game = Game()

def draw(game):
    win.fill((20, 20, 30))
    
    # Draw player (adjusted for camera)
    player_screen_pos = pygame.Rect(
        game.player.x - game.camera_x,
        game.player.y,
        game.player.width,
        game.player.height
    )
    pygame.draw.rect(win, (0, 255, 0), player_screen_pos)
    
    # Draw platforms (adjusted for camera)
    for p in game.platforms:
        platform_screen_pos = pygame.Rect(
            p.x - game.camera_x,
            p.y,
            p.width,
            p.height
        )
        pygame.draw.rect(win, (180, 180, 180), platform_screen_pos)
    
    # Draw checkpoints (adjusted for camera)
    for cp in game.checkpoints:
        cp_screen_pos = pygame.Rect(
            cp.x - game.camera_x,
            cp.y,
            cp.width,
            cp.height
        )
        pygame.draw.rect(win, (255, 215, 0), cp_screen_pos)  # Gold color for checkpoints
    
    # Draw HUD
    text = font.render(f"Stamina: {game.stamina} | Score: {game.score}", True, (255,255,255))
    win.blit(text, (20, 20))
    pygame.display.flip()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Move player
    if keys[pygame.K_LEFT]: 
        game.player.x -= 5
    if keys[pygame.K_RIGHT]: 
        game.player.x += 5
    
    # Jump with stamina check
    if keys[pygame.K_SPACE] and game.on_ground and game.stamina > 0:
        game.vel_y = -15
        game.on_ground = False
        game.stamina -= 1

    # Apply gravity
    game.vel_y += 1
    game.player.y += game.vel_y

    # Camera follows player
    target_camera_x = game.player.x - W // 3
    game.camera_x += (target_camera_x - game.camera_x) * 0.1

    # Platform collisions
    game.on_ground = False
    for p in game.platforms:
        if game.player.colliderect(p) and game.vel_y > 0:
            game.player.bottom = p.top
            game.vel_y = 0
            game.on_ground = True

    # Ground collision
    if game.player.bottom >= H:
        game.player.bottom = H
        game.vel_y = 0
        game.on_ground = True

    # Checkpoint collision
    for cp in game.checkpoints[:]:
        if game.player.colliderect(cp):
            game.stamina = min(game.stamina + 5, 10)  # Increase stamina, cap at 10
            game.last_checkpoint_x = cp.x
            game.score += 100
            game.checkpoints.remove(cp)  # Remove collected checkpoint

    # Generate new sections as player moves forward
    if game.player.x > game.platforms[-1].x - W:
        game.generate_new_section()

    # Game over conditions
    if game.stamina <= 0 and not game.on_ground:
        print(f"Game Over! Final Score: {game.score}")
        running = False

    draw(game)
    clock.tick(60)

pygame.quit()
sys.exit()
 