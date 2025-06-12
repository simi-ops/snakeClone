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
    return score > min(entry["score"] for entry in scoreboard["high_scores"])

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
