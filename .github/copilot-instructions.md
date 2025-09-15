# Proper Duel - Pixel Art Samurai Fighting Game

A Python/Pygame 2D fighting game featuring player vs intelligent AI samurai combat with pixel art aesthetics and retro presentation.

## Architecture Overview

### Core Game Loop (`game/engine.py`)
- **Scene Management**: Three distinct scenes - SplashScene, MainMenuScene, FightScene
- **State Machine**: Scene transitions managed by `scene_type` ("splash" → "menu" → "fight")
- **Event Pipeline**: Events flow through engine → input_handler → character/scene systems
- **60 FPS Target**: Fixed timestep with `pygame.time.Clock()` and delta time (`dt`) propagation

### Character System (`game/character.py`)
- **Base Character Class**: Core physics, health, animation state management
- **Combat State Machine**: `is_attacking`, `is_blocking`, `is_dead`, `is_hit` with timing controllers
- **Specialized Fighters**: `Samurai1` (player, blue) and `Samurai2` (AI, red) with unique sprites
- **Animation Integration**: Uses `SpriteAnimator` for frame-based animation sequences
- **Physics**: Gravity-based movement with ground collision at `ground_y = 335.0`

### AI System (`game/input_handler.py`)
- **Distance-Based Behavior**: Close-range blocking, medium-range attacking, long-range approach
- **Reaction Timing**: `reaction_time = 0.3s`, `decision_interval = 0.2s` for realistic responses
- **Aggression Parameter**: `aggression = 0.7` controls risk/reward balance
- **Special Attack Logic**: Uses 10-second cooldowns with strategic timing

### Resource Management (`game/resource_utils.py`)
**Critical for PyInstaller builds**: Handles both development and bundled executable asset loading
```python
# Use these functions for ALL asset loading:
sprite_path("Idle.png")      # → assets/sprites/Idle.png
audio_path("menu.mp3")       # → assets/audio/menu.mp3
asset_path("subfolder/file") # → assets/subfolder/file
```

## Development Workflow

### Running the Game
```powershell
python main.py                    # Development mode
python build_exe.py               # Build standalone executable
.\build_game.bat                  # Windows batch build script
pyinstaller ProperDuel.spec       # Direct PyInstaller build
```

### Adding New Characters
1. Inherit from `Character` base class in `character.py`
2. Override `load_sprites()` to define animation sequences
3. Set unique `self.color` fallback and sprite paths
4. Add to scene initialization in `scenes.py`

### Animation System (`game/sprite_system.py`)
- **SpriteSheet**: Loads PNG files and extracts frames by grid coordinates
- **Animation**: Frame sequences with configurable timing (`frame_duration`)
- **SpriteAnimator**: Manages multiple named animations per character
- **Frame Format**: Horizontal sprite strips (6 frames @ 32x48 pixels typical)

### Asset Path Requirements
**NEVER use hardcoded paths** - always use resource utilities:
```python
# ❌ Wrong - breaks in PyInstaller builds
pygame.image.load("assets/sprites/Idle.png")

# ✅ Correct - works in both development and builds
pygame.image.load(sprite_path("Idle.png"))
```

## Build & Distribution

### PyInstaller Configuration (`ProperDuel.spec`)
- **Single File Build**: `--onefile` creates portable ~155MB executable
- **Asset Bundling**: Automatic inclusion of `assets/` and `game/` directories
- **Path Resolution**: `sys._MEIPASS` handling via `resource_utils.py`
- **Hidden Imports**: Explicit PyGame module inclusion for proper bundling

### Critical Build Files
- `ProperDuel.spec` - PyInstaller configuration with asset handling
- `build_exe.py` - Cross-platform build script with error handling
- `build_game.bat` - Windows-specific build automation
- `BUILD_NOTES.md` - Detailed build troubleshooting and optimization notes

## Combat Mechanics

### Attack System
- **Attack Duration**: `0.48s` (6 frames × 0.08s per frame)
- **Hit Frame**: Frame 4 (0-indexed) triggers damage calculation
- **Cooldown**: `0.5s` prevents attack spam
- **Special Attacks**: `0.72s` duration with `10s` cooldown

### Collision Detection
- **Range Check**: Distance-based hit detection (`abs(char1.x - char2.x) < 60`)
- **Facing Validation**: Attacks only hit targets in front of attacker
- **Attack ID System**: Prevents multiple hits from single attack sequence

## Scene Architecture (`game/scenes.py`)

### State Management Pattern
Each scene implements:
- `handle_input(keys, events)` → Returns action strings
- `update(dt)` → Updates animations and timers  
- `render(screen)` → Draws scene elements
- Action-based transitions (e.g., "start_game", "quit", "skip")

### Round System
- **Match Format**: First to 3 round wins
- **Round Timer**: 99 seconds with automatic progression
- **Health Persistence**: Damage carries between rounds
- **Victory Conditions**: Health depletion or timeout

## Testing & Debugging

### Common Issues
- **Asset Loading Errors**: Always test builds on systems without Python installed
- **Animation Timing**: Verify `dt` values are reasonable (typically 0.016s @ 60fps)
- **Input Lag**: Check event processing order in `handle_events()`
- **AI Behavior**: Monitor distance calculations and decision timing

### Performance Monitoring
- Target 60 FPS consistently on moderate hardware
- Monitor sprite loading times during scene transitions
- Check memory usage with large sprite sheets