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
        self.high_score = 0  # Keep high score persistent
        self.reset_game()

    def reset_game(self):
        # Reset player position and physics
        self.player = pygame.Rect(100, 500, 40, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = 5  # Original base speed
        self.move_speed = 5  # Current movement speed
        self.max_vel_y = 15  # Maximum falling speed
        self.jump_strength = 13  # Jump velocity
        self.gravity = 0.5  # Gravity strength
        self.coin_pattern_counter = 0  # Track coin placement pattern (0-3)
        
        # Speed boost tracking
        self.boost_coins_remaining = 0  # Coins remaining before boost ends
        self.current_boost_level = 0  # Current speed boost percentage
        
        # Platform and coin generation settings
        self.base_platform_width = 200
        self.base_platform_height = 20
        self.current_platform_width = 200
        self.current_platform_height = 20
        self.coin_frequency = 4  # One coin every 4 platforms initially
        self.platform_count = 0  # Track total platforms for coin spawning
        
        # Reset game state
        self.on_ground = False
        self.jumps = 10  # starting jumps
        self.auto_move = False
        self.above_platform = False
        self.coins = 0  # Spendable coins
        self.total_coins_collected = 0  # Total coins for speed boost
        self.score = 0
        
        # Reset position tracking
        self.last_position = None
        self.camera_x = 0
        self.last_checkpoint_x = 0
        self.starting_point_x = 50
        
        # Clear and regenerate level
        self.platforms = []
        self.checkpoints = []
        self.generate_initial_level()

    def generate_initial_level(self):
        # Generate initial platforms
        self.platforms = []
        self.platform_count = 0
        for i in range(5):
            x = 200 + i * 300
            y = random.randint(400, 500)
            self.platforms.append(pygame.Rect(x, y, self.current_platform_width, self.current_platform_height))
            self.platform_count += 1
            
            # Add coins based on frequency
            if self.platform_count % self.coin_frequency == 0:
                coin_x = x + self.current_platform_width // 2 - 20  # Center on platform
                
                # Place coin above platform
                coin_y = max(60, y - 80)  # Keep at least 60px from top
                
                self.checkpoints.append(pygame.Rect(coin_x, coin_y, 40, 40))

    def generate_new_section(self):
        last_platform = self.platforms[-1]
        x = last_platform.x + random.randint(250, 350)
        y = random.randint(400, 500)
        self.platforms.append(pygame.Rect(x, y, self.current_platform_width, self.current_platform_height))
        self.platform_count += 1
        
        # Add coins based on frequency
        if self.platform_count % self.coin_frequency == 0:
            coin_x = x + self.current_platform_width // 2 - 20  # Center on platform
            
            # Place coin above platform
            coin_y = max(60, y - 80)  # Keep at least 60px from top
            
            self.checkpoints.append(pygame.Rect(coin_x, coin_y, 40, 40))

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
    
    # Draw checkpoints (adjusted for camera)
    for cp in game.checkpoints:
        cp_screen_pos = pygame.Rect(
            cp.x - game.camera_x,
            cp.y,
            cp.width,
            cp.height
        )
        pygame.draw.rect(win, GOLD, cp_screen_pos)
    
    # Draw HUD
    jumps_text = font.render(f"jumps: {game.jumps}", True, WHITE)
    coins_text = font.render(f"Coins: {game.coins}", True, GOLD)
    total_text = font.render(f"Total: {game.total_coins_collected}", True, GOLD)
    
    # Show speed boost if active
    speed_color = WHITE
    speed_text = "Speed: Normal"
    if 5 <= game.total_coins_collected < 10:
        speed_text = "Speed: +25%!"
        speed_color = YELLOW
   
    elif 10 <= game.total_coins_collected < 15:
        speed_text = "Speed: +50%!"
        speed_color = ORANGE
    
    elif 15 <= game.total_coins_collected < 20:
        speed_text = "Speed: +75%!"
        speed_color = TOMATO

    elif game.total_coins_collected >= 20:
        speed_text = "Speed: +100%!"
        speed_color = RED
        
    speed_boost_text = font.render(speed_text, True, speed_color)
    
    win.blit(jumps_text, (20, 20))
    win.blit(coins_text, (200, 20))
    win.blit(total_text, (400, 20))
    win.blit(speed_boost_text, (600, 20))
    pygame.display.flip()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Update game dynamics based on total coins collected
    
    # 100% speed increase
    if game.total_coins_collected >= 20:
        game.move_speed = game.base_speed * 2.0
        game.current_platform_width = int(game.base_platform_width * 0.50)
        game.coin_frequency = 5
    
    # 75% speed increase
    elif 15 <= game.total_coins_collected < 20:
        game.move_speed = game.base_speed * 1.75
        game.current_platform_width = int(game.base_platform_width * 0.60)
        game.coin_frequency = 5
        
    # 50% speed increase
    elif 10 <= game.total_coins_collected < 15:
        game.move_speed = game.base_speed * 1.5
        game.current_platform_width = int(game.base_platform_width * 0.70)
        game.coin_frequency = 4
        
    # 25% speed increase
    elif game.total_coins_collected >= 5:
        game.move_speed = game.base_speed * 1.25
        game.current_platform_width = int(game.base_platform_width * 0.80)
        game.coin_frequency = 4
    
    else:
        game.move_speed = game.base_speed
        game.current_platform_width = game.base_platform_width
        game.current_platform_height = game.base_platform_height
        game.coin_frequency = 4

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

    # Coin collision
    for cp in game.checkpoints[:]:
        if game.player.colliderect(cp):
            game.jumps = min(game.jumps + 3, 10)  # Increase jumps, cap at 10
            game.last_checkpoint_x = cp.x
            game.coins += 1  # Increment spendable coins
            game.total_coins_collected += 1  # Track total coins
            game.score += 100  # Hidden score increment
            
            # Update boost duration
            if game.boost_coins_remaining > 0:
                game.boost_coins_remaining -= 1
                if game.boost_coins_remaining == 0:
                    # Reset speed boost when duration ends
                    game.current_boost_level = 0
                    game.move_speed = game.base_speed
            
            # Activate new speed boost if not already boosted
            if game.boost_coins_remaining == 0:
                if game.total_coins_collected >= 15:
                    game.current_boost_level = 100  # 100% boost
                elif game.total_coins_collected >= 10:
                    game.current_boost_level = 75   # 75% boost
                elif game.total_coins_collected >= 5:
                    game.current_boost_level = 50   # 50% boost
                
                if game.current_boost_level > 0:
                    game.boost_coins_remaining = 3  # Set duration to 3 coins
            
            game.checkpoints.remove(cp)  # Remove collected coin

    # Generate new sections as player moves forward
    if game.player.x > game.platforms[-1].x - W:
        game.generate_new_section()

    # Game over conditions
    if game.jumps <= 0 and not game.on_ground:
        # Update high score if current score is higher
        game.high_score = max(game.high_score, game.score)
        
        # Store current position for continue feature
        game.last_position = (game.player.x, game.player.y)
        
        waiting_for_input = True
        while waiting_for_input:
            # Create game over screen
            win.fill((20, 20, 30))  # Clear screen with background color
            
            # Draw "Game Over" text
            game_over_text = font.render("Game Over!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(W//2, H//2 - 80))
            win.blit(game_over_text, text_rect)
            
            # Draw High Score (based on hidden score)
            if game.score > game.high_score:
                new_high_score_text = font.render("New High Score!", True, (255, 215, 0))
                new_high_rect = new_high_score_text.get_rect(center=(W//2, H//2 - 40))
                win.blit(new_high_score_text, new_high_rect)
            
            # Draw Coins
            coins_text = font.render(f"Coins: {game.coins}", True, (255, 215, 0))
            coins_rect = coins_text.get_rect(center=(W//2, H//2))
            win.blit(coins_text, coins_rect)
            
            # Draw continue option if player has enough coins
            if game.coins >= 2:  # Need at least 2 coins to spend half
                cost = game.coins // 2  # Calculate cost with integer division (rounds down)
                continue_text = font.render(f"Press C to Continue (Cost: {cost} coins)", True, (0, 255, 255))
                continue_rect = continue_text.get_rect(center=(W//2, H//2 + 40))
                win.blit(continue_text, continue_rect)
            
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
                        # Reset game state but keep high score
                        current_high_score = game.high_score
                        game.reset_game()
                        game.high_score = current_high_score
                        waiting_for_input = False
                    elif event.key == pygame.K_c and game.coins >= 2:
                        spent_coins = game.coins // 2
                        game.coins -= spent_coins
                        game.jumps = 7
                        if game.last_position:
                            game.player.x, game.player.y = game.last_position
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