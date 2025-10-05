import pygame
import sys
import random

pygame.init()

W, H = 800, 600
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("SlidePy Runner")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255,215,0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
TOMATO = (255, 99, 71)

class Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player = pygame.Rect(100, 500, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = 5  # Original base speed
        self.move_speed = 5  # Current movement speed
        self.max_vel_y = 15  # Maximum falling speed
        self.jump_strength = 13  # Jump velocity
        self.gravity = 0.5  # Gravity strength
        
        # Platform settings
        self.base_platform_width = 200
        self.base_platform_height = 20
        self.current_platform_width = 200
        self.current_platform_height = 20
        
        # Reset game state
        self.on_ground = False
        self.jumps = 10  # starting jumps
        self.auto_move = False
        self.above_platform = False
        
        # Reset position tracking
        self.last_position = None
        self.camera_x = 0
        self.starting_point_x = 50
        
        # Clear and regenerate level
        self.platforms = []
        self.generate_initial_level()

    def generate_initial_level(self):
        # Generate initial platforms
        self.platforms = []
        for i in range(5):
            x = 200 + i * 300
            y = random.randint(400, 500)
            self.platforms.append(pygame.Rect(x, y, self.current_platform_width, self.current_platform_height))

    def generate_new_section(self):
        last_platform = self.platforms[-1]
        x = last_platform.x + random.randint(250, 350)
        y = random.randint(400, 500)
        self.platforms.append(pygame.Rect(x, y, self.current_platform_width, self.current_platform_height))

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
    
    pygame.draw.rect(win, GREEN, player_screen_pos)
    
    # Draw platforms (adjusted for camera)
    for p in game.platforms:
        platform_screen_pos = pygame.Rect(
            p.x - game.camera_x,
            p.y,
            p.width,
            p.height
        )
        
        pygame.draw.rect(win, (180, 180, 180), platform_screen_pos)
    
    jumps_text = font.render(f"jumps: {game.jumps}", True, WHITE)
    win.blit(jumps_text, (20, 20))
    pygame.display.flip()


# Game Loop
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Set base game dynamics
    game.move_speed = game.base_speed
    game.current_platform_width = game.base_platform_width
    game.current_platform_height = game.base_platform_height

    game.vel_x = game.move_speed
    
    if keys[pygame.K_LEFT] and game.player.x > game.starting_point_x:
        game.vel_x = -game.move_speed

    game.player.x += game.vel_x
    
    # Jump with jumps check
    if keys[pygame.K_SPACE] and game.on_ground and game.jumps > 0:
        game.vel_y = -game.jump_strength
        game.on_ground = False
        game.jumps -= 1

    # Apply gravity with terminal velocity and safety checks
    if not game.on_ground:
        game.vel_y = min(game.vel_y + game.gravity, game.max_vel_y)
    
    # Apply vertical movement with safety bounds
    new_y = game.player.y + game.vel_y
    
    # Prevent moving outside screen bounds
    if new_y < 0:
        new_y = 0
        game.vel_y = 0
    elif new_y > H - game.player.height:
        new_y = H - game.player.height
        game.vel_y = 0
        game.on_ground = True
    
    # Apply the safe position
    game.player.y = new_y

    # Camera follows player
    target_camera_x = game.player.x - W // 3
    game.camera_x += (target_camera_x - game.camera_x) * 0.1

    # Platform collisions with improved detection
    game.on_ground = False
    for p in game.platforms:
        if game.player.colliderect(p):
            # Calculate collision overlap
            dx = min(game.player.right - p.left, p.right - game.player.left)
            dy = min(game.player.bottom - p.top, p.bottom - game.player.top)
            
            # Determine if collision is more horizontal or vertical
            if dx < dy:
                # Horizontal collision
                if game.player.centerx < p.centerx:  # Coming from left
                    if game.vel_x > 0:  # Only adjust if moving right
                        game.player.right = p.left
                        game.vel_x = 0
                else:  # Coming from right
                    if game.vel_x < 0:  # Only adjust if moving left
                        game.player.left = p.right
                        game.vel_x = 0
            else:
                # Vertical collision
                if game.player.centery < p.centery:  # Coming from above
                    game.player.bottom = p.top
                    game.vel_y = 0
                    game.on_ground = True
                else:  # Coming from below
                    game.player.top = p.bottom
                    game.vel_y = 0

    # Ground collision
    if game.player.bottom >= H:
        game.player.bottom = H
        game.vel_y = 0
        game.on_ground = True

    # Platform generation check

    # Generate new sections as player moves forward
    if game.player.x > game.platforms[-1].x - W:
        game.generate_new_section()

    # Game over conditions
    if game.jumps <= 0 and not game.on_ground:
        # Store current position
        game.last_position = (game.player.x, game.player.y)
        
        waiting_for_input = True
        while waiting_for_input:
            # Create game over screen
            win.fill((20, 20, 30))  # Clear screen with background color
            
            # Draw "Game Over" text
            game_over_text = font.render("Game Over!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(W//2, H//2 - 40))
            win.blit(game_over_text, text_rect)
            
            # Draw restart instructions
            restart_text = font.render("Press R to Restart or ESC to Exit", True, (0, 255, 0))
            restart_rect = restart_text.get_rect(center=(W//2, H//2 + 80))
            win.blit(restart_text, restart_rect)
            
            pygame.display.flip()
            
            # Handle restart or quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset_game()
                        waiting_for_input = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            clock.tick(60)
        
        continue

    draw(game)
    clock.tick(60)

pygame.quit()
sys.exit()