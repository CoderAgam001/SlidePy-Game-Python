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
        self.game_started = False
        self.player = pygame.Rect(100, 500, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.move_speed = 5
        self.max_vel_y = 15  # Maximum falling speed
        self.jump_strength = 13  # Jump velocity
        self.gravity = 0.5  # Gravity strength
        self.score = 0  # Track score
        self.yellow_sprites = []  # Good collectibles
        self.red_sprites = []  # Bad collectibles
        
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
        self.yellow_sprites = []
        self.red_sprites = []
        
        for i in range(5):
            x = 200 + i * 300
            y = random.randint(400, 500)
            
            # Create platform with extended data
            platform_left = x
            platform_right = x + self.current_platform_width
            platform_center = (platform_left + platform_right) // 2
            
            # Create platform dictionary with all data
            platform = {
                'rect': pygame.Rect(x, y, self.current_platform_width, self.current_platform_height),
                'left': platform_left,
                'right': platform_right,
                'center': platform_center
            }
            self.platforms.append(platform)
            
            # Define sprite zones
            yellow_zone = (platform_left, platform_center - 20)  # -20 to account for sprite width
            red_zone = (platform_center, platform_right - 40)    # -40 to account for sprite width
            
            sprite_type = random.choices(['none', 'yellow', 'red', 'both'], 
                                      weights=[30, 35, 20, 15])[0]
            
            if sprite_type in ['yellow', 'both']:
                sprite_x = random.randint(yellow_zone[0], yellow_zone[1])
                sprite_y = y - random.randint(60, 120)  # Keep sprites in visible range
                self.yellow_sprites.append(pygame.Rect(sprite_x, sprite_y, 40, 40))
            
            if sprite_type in ['red', 'both']:
                sprite_x = random.randint(red_zone[0], red_zone[1])
                sprite_y = y - random.randint(60, 120)
                self.red_sprites.append(pygame.Rect(sprite_x, sprite_y, 40, 40))

    def generate_new_section(self):
        last_platform = self.platforms[-1]
        x = last_platform['rect'].x + random.randint(250, 350)
        y = random.randint(400, 500)
        
        # Create new platform with extended data
        platform_left = x
        platform_right = x + self.current_platform_width
        platform_center = (platform_left + platform_right) // 2
        
        # Create platform dictionary with all data
        platform = {
            'rect': pygame.Rect(x, y, self.current_platform_width, self.current_platform_height),
            'left': platform_left,
            'right': platform_right,
            'center': platform_center
        }
        self.platforms.append(platform)
        
        # Add collectibles with random but separated placement
        platform_left = x
        platform_right = x + self.current_platform_width
        
        # Randomly decide which type of sprite to spawn (if any)
        sprite_type = random.choices(['none', 'yellow', 'red', 'both'], weights=[30, 35, 20, 15])[0]
        
        if sprite_type in ['yellow', 'both']:
            # Yellow sprite placement with variable height
            sprite_x = platform_left + random.randint(0, (self.current_platform_width // 2) - 40)
            sprite_y = y - random.randint(40, 160)  # More height variation
            self.yellow_sprites.append(pygame.Rect(sprite_x, sprite_y, 40, 40))
        
        if sprite_type in ['red', 'both']:
            # Red sprite placement with variable height
            sprite_x = platform_left + (self.current_platform_width // 2) + random.randint(0, (self.current_platform_width // 2) - 40)
            sprite_y = y - random.randint(40, 160)  # More height variation
            self.red_sprites.append(pygame.Rect(sprite_x, sprite_y, 40, 40))

game = Game()

def draw(game):
    win.fill((20, 20, 30))
    
    if not game.game_started:
        start_text = font.render("Press Space to Begin", True, WHITE)
        text_rect = start_text.get_rect(center=(W//2, H//2.5))
        win.blit(start_text, text_rect)
        pygame.display.flip()
        
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
            p['rect'].x - game.camera_x,
            p['rect'].y,
            p['rect'].width,
            p['rect'].height
        )
        pygame.draw.rect(win, (180, 180, 180), platform_screen_pos)
    
    # Draw yellow sprites
    for sprite in game.yellow_sprites:
        sprite_screen_pos = pygame.Rect(
            sprite.x - game.camera_x,
            sprite.y,
            sprite.width,
            sprite.height
        )
        pygame.draw.rect(win, YELLOW, sprite_screen_pos)
    
    # Draw red sprites
    for sprite in game.red_sprites:
        sprite_screen_pos = pygame.Rect(
            sprite.x - game.camera_x,
            sprite.y,
            sprite.width,
            sprite.height
        )
        pygame.draw.rect(win, RED, sprite_screen_pos)
    
    # Create a floating overlay surface with alpha channel
    overlay = pygame.Surface((W, 80), pygame.SRCALPHA)
    
    # Create a semi-transparent background for better text visibility
    pygame.draw.rect(overlay, (0, 0, 0, 128), overlay.get_rect(), border_radius=10)
    
    # Render text with glow effect
    jumps_text = font.render(f"Jumps: {game.jumps}", True, WHITE)
    score_text = font.render(f"Score: {game.score}", True, WHITE)
    speed_text = font.render(f"Speed: {round(game.move_speed, 1)}", True, WHITE)
    
    # Position text with some padding and spacing
    padding = 20
    overlay.blit(jumps_text, (padding, (80 - jumps_text.get_height()) // 2))
    overlay.blit(score_text, (W//3, (80 - score_text.get_height()) // 2))
    overlay.blit(speed_text, (2*W//3, (80 - speed_text.get_height()) // 2))
    
    # Add the overlay to the main window
    win.blit(overlay, (0, 20))
    pygame.display.flip()


# Game Loop
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Handle game start
    if not game.game_started:
        if keys[pygame.K_SPACE]:
            game.game_started = True
        draw(game)
        clock.tick(60)
        continue
    
    # Set base game dynamics
    game.current_platform_width = game.base_platform_width
    game.current_platform_height = game.base_platform_height

    # Set movement speed
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
    
    game.player.y = new_y

    target_camera_x = game.player.x - W // 3
    game.camera_x += (target_camera_x - game.camera_x) * 0.1

    game.on_ground = False
    for p in game.platforms:
        platform = p['rect']
        if game.player.colliderect(platform):
            at_left_edge = abs(game.player.right - p['left']) < 10
            at_right_edge = abs(game.player.left - p['right']) < 10
            
            if at_left_edge or at_right_edge:

                if at_left_edge:
                    game.player.right = p['left']

                else:
                    game.player.left = p['right']
                
                game.vel_x = 0
            
            else:
                
                if game.player.centery < platform.centery:
                    game.player.bottom = platform.top
                    game.vel_y = 0
                    game.on_ground = True
                
                else:
                    game.player.top = platform.bottom
                    game.vel_y = 0

    # Ground collision
    if game.player.bottom >= H:
        game.player.bottom = H
        game.vel_y = 0
        game.on_ground = True

    # Sprite collisions
    
    # Yellow sprites (positive effects)
    for sprite in game.yellow_sprites[:]:
        if game.player.colliderect(sprite):
            game.jumps = min(game.jumps + 3, 10)
            game.move_speed = min(game.move_speed + 0.5, 20)
            game.score += 2
            game.yellow_sprites.remove(sprite)
    
    # Red sprites (negative effects)
    for sprite in game.red_sprites[:]:
        if game.player.colliderect(sprite):
            game.jumps = max(game.jumps - 1, 0)
            game.move_speed = max(game.move_speed - 0.5, 5)
            game.score = max(game.score - 1, 0)
            game.red_sprites.remove(sprite)
    
    # Generate new sections as player moves forward
    if game.player.x > game.platforms[-1]['rect'].x - W:
        game.generate_new_section()

    # Game Over conditions
    if game.jumps <= 0 and not game.on_ground:
        game.last_position = (game.player.x, game.player.y)
        
        # End Screen
        waiting_for_input = True
        while waiting_for_input:
            win.fill((20, 20, 20))

            game_over_text = font.render("Game Over!", True, TOMATO)
            text_rect = game_over_text.get_rect(center=(W//2, H//2 - 40))
            win.blit(game_over_text, text_rect)
            
            restart_text = font.render("Press R to Restart or ESC to Exit", True, (0, 255, 0))
            restart_rect = restart_text.get_rect(center=(W//2, H//2 + 80))
            win.blit(restart_text, restart_rect)
            
            pygame.display.flip()
            
            # End Screen Event Handler
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