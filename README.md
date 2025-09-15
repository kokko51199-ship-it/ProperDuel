# Proper Duel - Pixel Art Samurai Fighting Game

A Python/Pygame 2D fighting game featuring player vs intelligent AI samurai combat with pixel art aesthetics and retro presentation.

## Quick start
- Install dependencies: `pip install -r requirements.txt`
- Run the game: `python main.py`

---

## Features

- **Player vs AI combat** - Fight against an intelligent AI opponent
- **First to 3 wins match** - Multi-round tournament format
- **Smart AI behavior** - AI adapts to distance, attacks strategically, and blocks incoming attacks
- **Simple combat system** - Attack, block, and movement mechanics
- **Health system** - Track damage across multiple rounds
- **Round system** - 99-second rounds with automatic progression
- **Basic physics** - Gravity, jumping, and ground collision
- **Retro pixel art style** - Ready for custom sprite integration

## Game Mode

**First to 3 Wins Match**: Battle the AI across multiple rounds. The first fighter to win 3 rounds wins the entire match!

## Controls

### Player (Left Samurai - Blue)
- **Movement**: W/A/S/D keys
- **Attack**: Spacebar
- **Block**: Left Shift
- **Special**: Q key (reserved for future features)

### AI Opponent (Right Samurai - Red)
- **Automatically controlled** with intelligent behavior:
  - Approaches when at long range
  - Attacks when close
  - Blocks incoming attacks
  - Retreats when overwhelmed
  - Uses jump attacks strategically

## Installation

1. **Clone or download** this repository
2. **Install Python 3.7+** if not already installed
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python main.py
```

## Project Structure

```
Proper Duel/
├── main.py                 # Game entry point
├── requirements.txt        # Python dependencies
├── game/                   # Core game modules
│   ├── engine.py          # Game engine and main loop
│   ├── character.py       # Character classes and combat
│   ├── input_handler.py   # Input system for both players
│   └── scenes.py          # Scene management
├── assets/                 # Game assets (sprites, audio)
│   ├── sprites/           # Character and environment art
│   └── audio/             # Sound effects and music
└── .github/
    └── copilot-instructions.md  # Development guidelines
```

## Game Mechanics

### Match System
- **First to 3 Wins**: Complete match requires winning 3 rounds
- **Round Duration**: 99 seconds per round
- **Victory Conditions**: Defeat opponent or have more health when time expires
- **Round Transitions**: 3-second break between rounds with score display

### Combat System
- **Attacks**: Deal 10 damage, have cooldown period
- **Blocking**: Prevents damage when timed correctly
- **Health**: Each character starts with 100 HP per round
- **Rounds Reset**: Health and positions reset each round

### AI Behavior
- **Distance-based tactics**: Different strategies for close, medium, and long range
- **Reaction time**: Realistic response delays to player actions
- **Blocking intelligence**: AI blocks incoming attacks with high accuracy
- **Aggressive/Defensive balance**: Mix of offensive and defensive strategies

### Movement
- **Walking**: Left/right movement at 200 pixels/second
- **Jumping**: Vertical movement with gravity physics
- **Ground Collision**: Characters stay on the ground plane

## Development

### Adding Sprites
1. Create 32x48 pixel PNG images
2. Place in `assets/sprites/` directory
3. Modify character classes to load and display sprites
4. Update animation system for walking, attacking, blocking

### Adding Sound Effects
1. Add WAV/OGG files to `assets/audio/` directory
2. Load sounds in the appropriate game modules
3. Trigger sounds during combat events

### Extending Characters
- Modify `Character` class in `game/character.py`
- Add new moves, combos, or special abilities
- Customize stats (speed, health, attack power)

## Technical Details

- **Engine**: Pygame 2.5.0+
- **Frame Rate**: 60 FPS
- **Resolution**: 800x600 pixels
- **Physics**: Basic gravity and collision detection
- **Input**: Real-time keyboard input handling

## Future Enhancements

- [ ] Sprite animations and pixel art graphics
- [ ] Sound effects and background music
- [ ] Special moves and combos
- [ ] Multiple fighting stages
- [ ] Character selection screen
- [ ] Tournament mode
- [ ] AI opponents

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify for your own projects.

---

**Ready to duel?** Run `python main.py` and start fighting!