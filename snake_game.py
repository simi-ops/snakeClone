import pygame
import random
import sys
import time
import os
import math
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 30  # Increased from 20 to 30 for bigger blocks
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 8  # Slightly reduced speed to compensate for larger blocks

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)

# Direction constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Snake Game")
clock = pygame.time.Clock()

# Sound settings
sound_enabled = True

# Load sounds
try:
    eat_sound = mixer.Sound('sounds/eat.wav')
    game_over_sound = mixer.Sound('sounds/game_over.wav')
    reward_sound = mixer.Sound('sounds/reward.wav')  # New sound for special rewards
    sound_files_exist = True
except:
    # Create a directory for sounds if it doesn't exist
    if not os.path.exists('sounds'):
        os.makedirs('sounds')
    
    # Create placeholder sounds
    eat_sound = mixer.Sound(buffer=bytearray(100))
    game_over_sound = mixer.Sound(buffer=bytearray(100))
    reward_sound = mixer.Sound(buffer=bytearray(100))
    sound_files_exist = False
    print("Sound files not found. Using placeholder sounds.")

# Font setup
font = pygame.font.SysFont('arial', 25)
small_font = pygame.font.SysFont('arial', 20)
large_font = pygame.font.SysFont('arial', 50)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Start with 3 segments in the middle of the screen
        self.length = 3
        self.positions = [
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
        ]
        self.direction = RIGHT
        self.color = GREEN
        self.score = 0
        self.speed = FPS
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        # Get current head position
        current = self.get_head_position()
        x, y = self.direction
        
        # Calculate new head position
        new_x = (current[0] + x)
        new_y = (current[1] + y)
        new_position = (new_x, new_y)
        
        # Check for wall collision
        if (new_x < 0 or new_x >= GRID_WIDTH or 
            new_y < 0 or new_y >= GRID_HEIGHT):
            return False  # Game over
        
        # Check for self collision
        if new_position in self.positions[1:]:
            return False  # Game over
        
        # Move snake
        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.positions.pop()
        
        return True  # Game continues
    
    def render(self, surface):
        for i, p in enumerate(self.positions):
            # Draw each segment
            color = DARK_GREEN if i == 0 else self.color  # Head is darker
            
            # Create slightly smaller rectangle for better visual separation
            margin = 2  # Small margin for visual separation between segments
            rect = pygame.Rect(
                p[0] * GRID_SIZE + margin, 
                p[1] * GRID_SIZE + margin, 
                GRID_SIZE - (margin * 2), 
                GRID_SIZE - (margin * 2)
            )
            
            # Draw rounded rectangle for snake segments
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 1, border_radius=8)  # Border
    
    def change_direction(self, direction):
        # Prevent reversing direction
        if (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        self.direction = direction

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
    
    def render(self, surface):
        # Draw food as a circle for visual distinction from snake
        center_x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2  # Slightly smaller than grid cell
        
        # Draw food with a glow effect
        pygame.draw.circle(surface, (255, 150, 150), (center_x, center_y), radius + 3)  # Outer glow
        pygame.draw.circle(surface, self.color, (center_x, center_y), radius)  # Main food

class Reward:
    def __init__(self):
        self.position = (0, 0)
        self.active = False
        self.timer = 0
        self.duration = 100  # How long the reward stays on screen (in frames)
        self.points = 0
        self.type = 0
        self.color = GOLD
    
    def activate(self, snake_positions):
        """Activate a new random reward"""
        self.active = True
        self.timer = self.duration
        
        # Randomize reward type (0-2)
        self.type = random.randint(0, 2)
        
        # Set reward properties based on type
        if self.type == 0:  # Gold reward (30 points)
            self.points = 30
            self.color = GOLD
        elif self.type == 1:  # Purple reward (50 points)
            self.points = 50
            self.color = PURPLE
        else:  # Cyan reward (100 points)
            self.points = 100
            self.color = CYAN
        
        # Randomize position (not on snake)
        self.randomize_position(snake_positions)
    
    def randomize_position(self, snake_positions):
        """Randomize the reward position (not on snake)"""
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            if self.position not in snake_positions:
                break
    
    def update(self):
        """Update reward timer"""
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
    
    def render(self, surface):
        """Render the reward if active"""
        if not self.active:
            return
            
        # Calculate center position
        center_x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        
        # Make the reward pulsate for visual effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5
        radius = (GRID_SIZE // 2 - 4) + pulse
        
        # Draw reward with a star-like shape
        points = []
        for i in range(10):
            angle = 2 * math.pi * i / 10
            r = radius if i % 2 == 0 else radius * 0.5
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points.append((x, y))
        
        # Draw the star shape
        pygame.draw.polygon(surface, self.color, points)
        
        # Draw a pulsating glow
        glow_radius = radius + 5 + pulse
        pygame.draw.circle(surface, self.color, (center_x, center_y), glow_radius, 2)
        
        # Draw points value
        value_text = small_font.render(f"+{self.points}", True, WHITE)
        surface.blit(value_text, (center_x - value_text.get_width()//2, center_y - value_text.get_height()//2))

def play_sound(sound):
    """Play sound if sounds are enabled"""
    if sound_enabled:
        sound.play()

def draw_score(surface, score):
    """Draw score and sound status"""
    score_text = font.render(f'Score: {score}', True, WHITE)
    surface.blit(score_text, (10, 10))
    
    # Draw sound status
    sound_status = "Sound: ON" if sound_enabled else "Sound: OFF"
    sound_color = GREEN if sound_enabled else RED
    sound_text = small_font.render(sound_status, True, sound_color)
    surface.blit(sound_text, (WIDTH - sound_text.get_width() - 10, 10))
    
    # Draw sound toggle instruction
    toggle_text = small_font.render("Press 'M' to toggle sound", True, WHITE)
    surface.blit(toggle_text, (WIDTH - toggle_text.get_width() - 10, 35))

def draw_game_over(surface, score):
    game_over_text = large_font.render('GAME OVER', True, WHITE)
    score_text = font.render(f'Final Score: {score}', True, WHITE)
    restart_text = font.render('Press R to Restart or Q to Quit', True, WHITE)
    
    surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

def show_reward_notification(surface, points):
    """Show a temporary notification when a reward is collected"""
    notification_text = font.render(f"BONUS! +{points} points!", True, GOLD)
    surface.blit(notification_text, (WIDTH//2 - notification_text.get_width()//2, 50))

def main():
    global sound_enabled
    
    snake = Snake()
    food = Food()
    reward = Reward()
    
    running = True
    game_over = False
    paused = False
    
    # Variables for reward spawning
    reward_chance = 0.005  # 0.5% chance per frame to spawn a reward
    reward_notification_timer = 0
    reward_points = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # Restart game
                        snake.reset()
                        food.randomize_position()
                        reward.active = False
                        game_over = False
                        reward_notification_timer = 0
                    elif event.key == pygame.K_q:
                        running = False
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_m:
                        # Toggle sound
                        sound_enabled = not sound_enabled
        
        # Clear screen
        screen.fill(BLACK)
        
        if not game_over and not paused:
            # Update snake position
            if not snake.update():
                game_over = True
                play_sound(game_over_sound)
            
            # Check if snake ate food
            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 10
                play_sound(eat_sound)
                
                # Increase speed every 50 points
                if snake.score % 50 == 0:
                    snake.speed += 1
                
                # Spawn new food (ensure it's not on the snake)
                while True:
                    food.randomize_position()
                    if food.position not in snake.positions:
                        break
            
            # Check if snake ate a reward
            if reward.active and snake.get_head_position() == reward.position:
                snake.score += reward.points
                reward_points = reward.points
                reward_notification_timer = 60  # Show notification for 60 frames
                play_sound(reward_sound)
                reward.active = False
            
            # Update reward
            reward.update()
            
            # Random chance to spawn a reward if none is active
            if not reward.active and random.random() < reward_chance:
                reward.activate(snake.positions)
            
            # Update reward notification timer
            if reward_notification_timer > 0:
                reward_notification_timer -= 1
        
        # Draw everything
        snake.render(screen)
        food.render(screen)
        if reward.active:
            reward.render(screen)
        draw_score(screen, snake.score)
        
        # Show reward notification if timer is active
        if reward_notification_timer > 0:
            show_reward_notification(screen, reward_points)
        
        if game_over:
            draw_game_over(screen, snake.score)
        
        if paused:
            pause_text = large_font.render('PAUSED', True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))
        
        # Update display
        pygame.display.flip()
        
        # Control game speed
        clock.tick(snake.speed)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
