# Snake Clone

A classic Snake game implemented in Python using Pygame.

## Features

- 800x600 pixel game window with a black background
- Snake movement in four directions using arrow keys
- Food spawns at random positions
- Random special rewards that give bonus points
- Score tracking and display
- Game over when snake hits wall or itself
- Increasing difficulty (speed) as score gets higher
- Pause functionality (Spacebar)
- Sound effects for eating food, collecting rewards, and game over

## Controls

- Arrow keys: Control snake direction
- Spacebar: Pause/Resume game
- M: Toggle sound on/off
- R: Restart game after game over
- Q: Quit game after game over

## Requirements

- Python 3.x
- Pygame

## Installation

### Standard Installation
1. Make sure you have Python installed
2. Install Pygame:
   ```
   pip install pygame
   ```
3. Run the game:
   ```
   python snake_game.py
   ```

### Using Virtual Environment
1. Make sure you have Python installed
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install Pygame in the virtual environment:
   ```
   pip install pygame
   ```
5. Run the game:
   ```
   python snake_game.py
   ```
6. When finished, deactivate the virtual environment:
   ```
   deactivate
   ```

## Sound Files

The game looks for sound files in a `sounds` directory:
- `sounds/eat.wav` - Sound when snake eats food
- `sounds/game_over.wav` - Sound when game ends

If these files are not found, the game will use placeholder sounds.
