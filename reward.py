class Reward:
    def __init__(self):
        self.position = (0, 0)
        self.active = False
        self.timer = 0
        self.duration = 100  # How long the reward stays on screen (in frames)
        self.points = 0
        self.type = 0
        self.color = GOLD
    
    def activate(self):
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
        self.randomize_position()
    
    def randomize_position(self):
        """Randomize the reward position"""
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )
    
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
