import pygame
import random
import sys
import time
import os
import math
import json
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

# Scoreboard file
SCOREBOARD_FILE = "scoreboard.json"

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
        self.duration = 150  # Increased duration (150 frames instead of 100)
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
        if self.type == 0:  # Gold reward (50 points - increased from 30)
            self.points = 50
            self.color = GOLD
        elif self.type == 1:  # Purple reward (100 points - increased from 50)
            self.points = 100
            self.color = PURPLE
        else:  # Cyan reward (200 points - increased from 100)
            self.points = 200
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

# Scoreboard functions
def load_scoreboard():
    """Load the scoreboard from file"""
    try:
        with open(SCOREBOARD_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default scoreboard if file doesn't exist or is invalid
        return {"high_scores": []}

def save_scoreboard(scoreboard):
    """Save the scoreboard to file"""
    with open(SCOREBOARD_FILE, 'w') as f:
        json.dump(scoreboard, f)

def add_score_to_scoreboard(name, score):
    """Add a new score to the scoreboard"""
    scoreboard = load_scoreboard()
    
    # Add new score
    scoreboard["high_scores"].append({"name": name, "score": score})
    
    # Sort by score (highest first) and keep only top 10
    scoreboard["high_scores"] = sorted(
        scoreboard["high_scores"], 
        key=lambda x: x["score"], 
        reverse=True
    )[:10]
    
    # Save updated scoreboard
    save_scoreboard(scoreboard)
    
    # Return position in scoreboard (0-based)
    for i, entry in enumerate(scoreboard["high_scores"]):
        if entry["name"] == name and entry["score"] == score:
            return i
    
    return -1  # Not in top 10

def is_high_score(score):
    """Check if score qualifies for the high score board"""
    scoreboard = load_scoreboard()
    
    # If we have fewer than 10 scores, any score qualifies
    if len(scoreboard["high_scores"]) < 10:
        return True
    
    # Otherwise, check if score is higher than the lowest score
    return score > min(entry["score"] for entry in scoreboard["high_scores"]) if scoreboard["high_scores"] else True

def draw_scoreboard(surface):
    """Draw the scoreboard on the screen"""
    scoreboard = load_scoreboard()
    
    # Draw title
    title_text = large_font.render("HIGH SCORES", True, GOLD)
    surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
    
    # Draw scores
    y_pos = 170
    for i, entry in enumerate(scoreboard["high_scores"]):
        # Determine color (gold for top 3, white for others)
        color = GOLD if i < 3 else WHITE
        
        # Format the entry
        rank_text = font.render(f"{i+1}.", True, color)
        name_text = font.render(f"{entry['name']}", True, color)
        score_text = font.render(f"{entry['score']}", True, color)
        
        # Position and draw
        surface.blit(rank_text, (WIDTH//2 - 150, y_pos))
        surface.blit(name_text, (WIDTH//2 - 100, y_pos))
        surface.blit(score_text, (WIDTH//2 + 100, y_pos))
        
        y_pos += 30
    
    # Draw instruction to return
    back_text = font.render("Press SPACE to return", True, WHITE)
    surface.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))

def get_player_name(surface, score):
    """Get player name for high score entry"""
    name = ""
    entering_name = True
    
    while entering_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    entering_name = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() and len(name) < 10:
                    name += event.unicode
        
        # Clear screen
        surface.fill(BLACK)
        
        # Draw title
        title_text = large_font.render("NEW HIGH SCORE!", True, GOLD)
        score_text = font.render(f"Your score: {score}", True, WHITE)
        prompt_text = font.render("Enter your name:", True, WHITE)
        name_text = font.render(name + "_", True, WHITE)
        enter_text = font.render("Press ENTER when done", True, WHITE)
        
        surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 150))
        surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 220))
        surface.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, 270))
        surface.blit(name_text, (WIDTH//2 - name_text.get_width()//2, 320))
        surface.blit(enter_text, (WIDTH//2 - enter_text.get_width()//2, 370))
        
        pygame.display.flip()
        clock.tick(30)
    
    return name if name else "Player"

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
    
    # Check if this is a high score
    if is_high_score(score):
        instructions = font.render('Press H to save high score', True, GOLD)
    else:
        instructions = font.render('Press R to Restart or Q to Quit', True, WHITE)
    
    surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 70))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 10))
    surface.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT//2 + 50))
    
    # Always show restart/quit options
    if is_high_score(score):
        restart_text = font.render('R: Restart | Q: Quit | S: View Scoreboard', True, WHITE)
        surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 90))

def show_reward_notification(surface, points):
    """Show a temporary notification when a reward is collected"""
    notification_text = font.render(f"RARE BONUS! +{points} points!", True, GOLD)
    surface.blit(notification_text, (WIDTH//2 - notification_text.get_width()//2, 50))
    
    # Add a second line for the growth bonus
    growth_text = small_font.render("Snake grew longer!", True, GREEN)
    surface.blit(growth_text, (WIDTH//2 - growth_text.get_width()//2, 80))

def main():
    global sound_enabled
    
    snake = Snake()
    food = Food()
    reward = Reward()
    
    running = True
    game_over = False
    paused = False
    viewing_scoreboard = False
    
    # Variables for reward spawning
    reward_chance = 0.0005  # 0.05% chance per frame to spawn a reward (10x more rare)
    reward_notification_timer = 0
    reward_points = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if viewing_scoreboard:
                    if event.key == pygame.K_SPACE:
                        viewing_scoreboard = False
                elif game_over:
                    if event.key == pygame.K_r:
                        # Restart game
                        snake.reset()
                        food.randomize_position()
                        reward.active = False
                        game_over = False
                        reward_notification_timer = 0
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_h and is_high_score(snake.score):
                        # Enter high score
                        player_name = get_player_name(screen, snake.score)
                        add_score_to_scoreboard(player_name, snake.score)
                        viewing_scoreboard = True
                    elif event.key == pygame.K_s:
                        # View scoreboard
                        viewing_scoreboard = True
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
                    elif event.key == pygame.K_s:
                        # View scoreboard during gameplay
                        paused = True
                        viewing_scoreboard = True
        
        # Clear screen
        screen.fill(BLACK)
        
        if viewing_scoreboard:
            draw_scoreboard(screen)
        else:
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
                    reward_notification_timer = 90  # Show notification for 90 frames (increased from 60)
                    play_sound(reward_sound)
                    reward.active = False
                    
                    # Bonus: Add a segment to the snake when collecting a reward
                    snake.length += 1
                
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
            
            if paused and not viewing_scoreboard:
                pause_text = large_font.render('PAUSED', True, WHITE)
                screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))
                
                # Show scoreboard option during pause
                view_scores_text = font.render("Press S to view high scores", True, WHITE)
                screen.blit(view_scores_text, (WIDTH//2 - view_scores_text.get_width()//2, HEIGHT//2 + 60))
        
        # Update display
        pygame.display.flip()
        
        # Control game speed
        clock.tick(snake.speed if not (game_over or paused or viewing_scoreboard) else 30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
