"""
Character Classes
Samurai fighter characters with combat mechanics and sprite animations.
"""

import pygame
import os
import random
from typing import Tuple, Optional
from game.input_handler import PlayerInput
from game.sprite_system import SpriteSheet, Animation, SpriteAnimator
from game.resource_utils import sprite_path


class Character:
    """Base character class for samurai fighters."""
    
    def __init__(self, x: float, y: float, facing_right: bool = True, attack_sound=None, block_sound=None, pain_sound=None):
        """Initialize character."""
        # Position and movement
        self.x = x
        self.y = y
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.facing_right = facing_right
        
        # Character stats
        self.health = 100
        self.max_health = 100
        self.speed = 200.0  # pixels per second
        self.jump_power = 650.0  # Increased from 400.0 for higher, faster jumps
        self.jump_stamina_cost = 20  # Stamina cost for jumping
        
        # Audio
        self.attack_sound = attack_sound
        self.block_sound = block_sound
        self.pain_sound = pain_sound
        
        # Combat state
        self.is_attacking = False
        self.is_blocking = False
        self.is_dead = False
        self.is_hit = False  # Track when character is taking a hit
        self.hit_duration = 0.0
        self.hit_animation_time = 0.4  # How long hit animation should play (in seconds)
        self.attack_cooldown = 0.0
        self.attack_duration = 0.48  # 6 frames × 0.08 seconds = 0.48 seconds
        self.attack_cooldown_time = 0.5  # seconds
        self.current_attack_id = 0  # Track unique attacks
        self.attack_hit_frame = 4  # Hit occurs on frame 5 (0-indexed frame 4) out of 6
        self.can_hit = False  # Whether this attack can deal damage
        
        # Special attack state
        self.is_special_attacking = False
        self.special_attack_cooldown = 0.0
        self.special_attack_duration = 0.72  # 6 frames × 0.12 seconds = 0.72 seconds (slower)
        self.special_attack_cooldown_time = 10.0  # 10 seconds cooldown
        self.current_special_attack_id = 0  # Track unique special attacks
        self.special_attack_hit_frame = 4  # Hit occurs on frame 5 (0-indexed frame 4) out of 6
        self.can_special_hit = False  # Whether this special attack can deal damage
        
        # Stamina system
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_per_block = 50  # 2 blocks = 100 stamina = empty
        self.stamina_regen_rate = 25.0  # stamina per second when not blocking
        
        # Cheat system for debugging
        self.god_mode = False  # One-shot attack power
        self.cheat_input = ""  # Track typed characters for cheat
        self.cheat_timer = 0.0  # Reset cheat input after timeout
        self.is_stunned = False
        self.stun_duration = 0.0
        self.stun_time = 2.5  # seconds
        self.last_block_time = 0.0  # Track when last block occurred
        
        # Physics
        self.gravity = 800.0  # pixels per second squared
        self.ground_y = 335.0  # ground level (updated to match spawn position)
        self.on_ground = True
        
        # Sprite properties
        self.width = 32
        self.height = 48
        self.color = (100, 100, 200)  # Fallback color
        
        # Animation system
        self.animator = SpriteAnimator()
        self.last_attack_id = -1  # Track last animation played
        self.last_special_attack_id = -1  # Track last special attack animation played
        self.load_sprites()
    
    def load_sprites(self):
        """Load character sprites - to be overridden by subclasses."""
        # Create fallback animation
        fallback_surface = pygame.Surface((32, 48), pygame.SRCALPHA)
        fallback_surface.fill(self.color)
        fallback_animation = Animation([fallback_surface], 0.2)
        self.animator.add_animation("idle", fallback_animation)
    
    def update(self, dt: float, player_input: PlayerInput):
        """Update character state."""
        # Don't process input or physics if dead
        if self.is_dead:
            # Only update animations for death sequence
            self.animator.update(dt)
            return
            
        # Handle input
        self._handle_input(player_input, dt)
        
        # Update physics
        self._update_physics(dt)
        
        # Update combat timers
        self._update_combat(dt)
        
        # Update animations
        self._update_animations(dt)

    # Added simple attack API used by AI opponents
    def attack(self):
        """Start a normal attack sequence if not cooling down."""
        if self.is_dead or self.is_attacking or self.attack_cooldown > 0:
            return
        self.is_attacking = True
        self.attack_duration = 0.48  # sync with animation timing
        self.current_attack_id += 1
        self.can_hit = False
        # Start animation now; base _update_animations will manage hit frame
        self.animator.play_animation("attack", True)
        if self.attack_sound:
            self.attack_sound.play()

    def special_attack(self):
        """Start a special attack if not cooling down."""
        if self.is_dead or self.is_special_attacking or self.special_attack_cooldown > 0:
            return
        self.is_special_attacking = True
        self.special_attack_duration = 0.72
        self.current_special_attack_id += 1
        self.can_special_hit = False
        # Use same animation name if not separate
        if "special_attack" in self.animator.animations:
            self.animator.play_animation("special_attack", True)
        else:
            self.animator.play_animation("attack", True)
        if self.attack_sound:
            self.attack_sound.play()
    
    def _update_animations(self, dt: float):
        """Update character animations based on state."""
        # Update animator
        self.animator.update(dt)
        
        # If dead, only play death animation
        if self.is_dead:
            if self.animator.current_animation_name != "dead":
                self.animator.play_animation("dead", True)
            return
        
        # Check if attack animation has reached the hit frame
        if self.is_attacking and self.animator.current_animation_name == "attack":
            current_frame = self.animator.current_animation.current_frame
            if current_frame >= self.attack_hit_frame and not self.can_hit:
                self.can_hit = True  # Enable hit detection
        
        # Check if special attack animation has reached the hit frame
        if self.is_special_attacking and self.animator.current_animation_name == "special_attack":
            current_frame = self.animator.current_animation.current_frame
            if current_frame >= self.special_attack_hit_frame and not self.can_special_hit:
                self.can_special_hit = True  # Enable hit detection
        
        # Choose animation based on character state
        if self.is_special_attacking:
            # Start new special attack animation if this is a new special attack
            if self.current_special_attack_id != self.last_special_attack_id:
                self.animator.play_animation("special_attack", True)
                self.last_special_attack_id = self.current_special_attack_id
                self.can_special_hit = False  # Reset hit capability for new special attack
                
                # Play attack sound effect (same sound for special attack)
                if self.attack_sound:
                    self.attack_sound.play()
        elif self.is_attacking:
            # Start new attack animation if this is a new attack
            if self.current_attack_id != self.last_attack_id:
                self.animator.play_animation("attack", True)
                self.last_attack_id = self.current_attack_id
                self.can_hit = False  # Reset hit capability for new attack
                
                # Play attack sound effect
                if self.attack_sound:
                    self.attack_sound.play()
        elif self.is_hit:
            # Hit animation takes priority over most other states
            self.animator.play_animation("hit", False)
        elif self.is_stunned:
            # Stun animation (white silhouette)
            self.animator.play_animation("stun", False)
        elif self.is_blocking:
            self.animator.play_animation("block", False)
        elif abs(self.velocity_x) > 10:  # Moving
            self.animator.play_animation("walk", False)
        elif not self.on_ground:  # Jumping/falling
            self.animator.play_animation("jump", False)
        else:  # Standing still
            self.animator.play_animation("idle", False)
    
    def _handle_input(self, input_state: PlayerInput, dt: float):
        """Handle player input."""
        # Don't process input if stunned
        if self.is_stunned:
            self.is_blocking = False
            self.velocity_x = 0
            return
            
        # Block first (affects other actions) - only if we have stamina
        was_blocking = self.is_blocking
        can_block = self.stamina > 0 and not self.is_attacking
        self.is_blocking = input_state.block and can_block
        
        # Consume stamina when starting to block
        if self.is_blocking and not was_blocking:
            self.stamina = max(0, self.stamina - self.stamina_per_block)
            self.last_block_time = 0.0  # Reset block timer
            
            # Check if stamina depleted - trigger stun
            if self.stamina <= 0:
                self.is_stunned = True
                self.stun_duration = self.stun_time
                self.is_blocking = False
        
        # Movement (disabled while blocking or stunned)
        if not self.is_blocking and not self.is_stunned:
            if input_state.left:
                self.velocity_x = -self.speed
                self.facing_right = False
            elif input_state.right:
                self.velocity_x = self.speed
                self.facing_right = True
            else:
                self.velocity_x = 0
        else:
            # Can't move while blocking or stunned
            self.velocity_x = 0
        
        # Jump (disabled while blocking or stunned, requires stamina)
        if (input_state.up and self.on_ground and not self.is_blocking and not self.is_stunned and 
            self.stamina >= self.jump_stamina_cost):
            self.velocity_y = -self.jump_power
            self.on_ground = False
            # Consume stamina for jumping
            self.stamina = max(0, self.stamina - self.jump_stamina_cost)
            
            # Check if stamina depleted - trigger stun
            if self.stamina <= 0:
                self.is_stunned = True
                self.stun_duration = self.stun_time
                self.is_blocking = False
        
        # Attack (disabled while stunned)
        if input_state.attack and not self.is_attacking and not self.is_special_attacking and self.attack_cooldown <= 0 and not self.is_stunned:
            self.start_attack()
        
        # Special Attack (disabled while stunned)
        if input_state.special and not self.is_attacking and not self.is_special_attacking and not self.is_stunned:
            self.start_special_attack()
    
    def _update_physics(self, dt: float):
        """Update physics simulation."""
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity * dt
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Ground collision
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.velocity_y = 0
            self.on_ground = True
        
        # Screen boundaries (extended arena - 100 pixels on each side)
        arena_left = -100
        arena_right = 900
        if self.x < arena_left:
            self.x = arena_left
        elif self.x > arena_right - self.width:
            self.x = arena_right - self.width
    
    def _update_combat(self, dt: float):
        """Update combat state."""
        # Stun duration
        if self.is_stunned:
            self.stun_duration -= dt
            if self.stun_duration <= 0:
                self.is_stunned = False
                self.is_blocking = False
        
        # Attack duration
        if self.is_attacking:
            self.attack_duration -= dt
            if self.attack_duration <= 0:
                self.is_attacking = False
                self.attack_cooldown = self.attack_cooldown_time
        
        # Hit duration
        if self.is_hit:
            self.hit_duration -= dt
            if self.hit_duration <= 0:
                self.is_hit = False
        
        # Special attack duration
        if self.is_special_attacking:
            self.special_attack_duration -= dt
            if self.special_attack_duration <= 0:
                self.is_special_attacking = False
                # Start cooldown when special attack finishes
                self.special_attack_cooldown = self.special_attack_cooldown_time

        # Cooldowns tick down
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        if self.special_attack_cooldown > 0:
            self.special_attack_cooldown = max(0.0, self.special_attack_cooldown - dt)

        # Stamina regeneration and block timer
        if not self.is_blocking and not self.is_stunned and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * dt)
        if not self.is_blocking:
            self.last_block_time += dt

    # Exposed helper for scenes/AI: enter stun state
    def start_stun(self, duration: Optional[float] = None):
        """Put character into stunned state for a duration."""
        if self.is_dead:
            return
        self.is_stunned = True
        self.is_blocking = False
        self.stun_duration = duration if duration is not None else self.stun_time
        # Prefer 'stun' animation if present; otherwise 'hit'
        if "stun" in self.animator.animations:
            self.animator.play_animation("stun", True)
        elif "hit" in self.animator.animations:
            self.animator.play_animation("hit", True)
    
    def start_attack(self):
        """Start an attack."""
        self.is_attacking = True
        self.attack_duration = 0.48  # Match 6-frame animation duration
        self.is_blocking = False
        self.current_attack_id += 1  # Increment for new attack
        self.can_hit = False  # Reset hit capability
    
    def start_special_attack(self):
        """Start a special attack."""
        if self.special_attack_cooldown <= 0:  # Only if cooldown is ready
            self.is_special_attacking = True
            self.special_attack_duration = 0.72  # Match 6-frame slower animation duration
            self.is_blocking = False
            self.current_special_attack_id += 1  # Increment for new special attack
            self.can_special_hit = False  # Reset hit capability
            return True
        return False
    
    def process_cheat_input(self, character: str, dt: float):
        """Process cheat code input."""
        # Reset timer on new input
        if character:
            self.cheat_timer = 0.0
            self.cheat_input += character.lower()
            
            # Keep only last 6 characters (length of "kojima")
            if len(self.cheat_input) > 6:
                self.cheat_input = self.cheat_input[-6:]
                
            # Check for kojima cheat
            if "kojima" in self.cheat_input:
                self.god_mode = not self.god_mode  # Toggle god mode
                print(f"Kojima cheat {'ACTIVATED' if self.god_mode else 'DEACTIVATED'}! One-shot attacks: {'ON' if self.god_mode else 'OFF'}")
                self.cheat_input = ""  # Reset after activation
        
        # Update timer and reset input after timeout
        self.cheat_timer += dt
        if self.cheat_timer > 2.0:  # 2 second timeout
            self.cheat_input = ""
            self.cheat_timer = 0.0
    
    def take_damage(self, damage: int, attacker_x: float):
        """Take damage if not blocking properly."""
        # Check if blocking is effective (must face the attacker)
        is_effective_block = False
        if self.is_blocking and not self.is_dead:
            # Check if player is facing the attacker
            if self.facing_right and attacker_x > self.x:
                is_effective_block = True  # Facing right, attacker is to the right
            elif not self.facing_right and attacker_x < self.x:
                is_effective_block = True  # Facing left, attacker is to the left

        if is_effective_block:
            # Attack was blocked - play block sound
            if self.block_sound:
                # Stop any currently playing block sound to prevent overlap
                self.block_sound.stop()
                self.block_sound.play()
            return False
        elif not self.is_dead:
            # Attack hit - take damage and play pain sound
            self.health = max(0, self.health - damage)
            
            # Play pain sound for any damage taken
            if self.pain_sound:
                self.pain_sound.play()
            
            if self.health <= 0:
                self.is_dead = True
                # Start death animation
                self.animator.play_animation("dead", True)
            else:
                # Character takes damage but doesn't die - play hit animation
                self.is_hit = True
                self.hit_duration = self.hit_animation_time
                self.animator.play_animation("hit", True)
            return True
        return False
    
    def is_death_animation_finished(self) -> bool:
        """Check if death animation has finished playing."""
        if not self.is_dead:
            return False
        return (self.animator.current_animation_name == "dead" and 
                self.animator.current_animation.is_finished())
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get attack hitbox if attacking and can hit."""
        if not self.is_attacking or not self.can_hit:
            return None
        
        # Shortened attack range for better positioning gameplay
        attack_width = 25  # Reduced from 40 to 25
        attack_height = 15  # Reduced from 20 to 15
        
        if self.facing_right:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        
        attack_y = self.y + self.height // 2 - attack_height // 2
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_special_attack_rect(self) -> Optional[pygame.Rect]:
        """Get special attack hitbox if special attacking and can hit."""
        if not self.is_special_attacking or not self.can_special_hit:
            return None
        
        # Longer range for special attack
        attack_width = 40  # Longer range than normal attack
        attack_height = 25  # Taller hitbox than normal attack
        
        if self.facing_right:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - attack_width
        
        attack_y = self.y + self.height // 2 - attack_height // 2
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def get_rect(self) -> pygame.Rect:
        """Get character collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, surface: pygame.Surface):
        """Render the character."""
        # Get current sprite frame
        current_frame = self.animator.get_current_frame()
        
        # Apply horizontal flip if character is facing left
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        # Calculate render position (center the sprite on character position)
        render_x = self.x - (current_frame.get_width() - self.width) // 2
        render_y = self.y - (current_frame.get_height() - self.height) // 2
        
        # Render sprite
        surface.blit(current_frame, (render_x, render_y))


class Samurai1(Character):
    """First samurai character (blue) - Player character with sprites."""
    
    def __init__(self, x: float, y: float, attack_sound=None, block_sound=None, pain_sound=None):
        super().__init__(x, y, facing_right=True, attack_sound=attack_sound, block_sound=block_sound, pain_sound=pain_sound)
        self.color = (100, 100, 255)  # Blue fallback
        self.speed = 250.0  # Player is faster than base speed (was 200.0)
    
    def load_sprites(self):
        """Load samurai sprites."""
        # Path to sprites
        idle_path = sprite_path("Idle.png")
        attack_path = sprite_path("Attack1.png")
        run_path = sprite_path("Run.png")
        
        # Character scale factor (2x bigger)
        scale_factor = 2
        
        try:
            # Load idle sprite sheet
            idle_sheet = SpriteSheet(idle_path)
            
            # Extract 8 frames from the idle sprite sheet
            # Assuming each frame is 32 pixels wide and the sheet height is the frame height
            frame_width = idle_sheet.width // 8  # 8 frames horizontally
            frame_height = idle_sheet.height
            
            idle_frames_raw = idle_sheet.get_frames(frame_width, frame_height, 8, 0)
            # Scale frames to 2x size
            idle_frames = [pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor)) for frame in idle_frames_raw]
            idle_animation = Animation(idle_frames, 0.15)  # 0.15 seconds per frame
            
            self.animator.add_animation("idle", idle_animation)
            
            # Update character dimensions based on scaled sprite
            if idle_frames:
                self.width = frame_width * scale_factor
                self.height = frame_height * scale_factor
            
            print(f"Loaded idle animation with {len(idle_frames)} frames ({self.width}x{self.height})")
            
            # Load attack sprite sheet
            attack_sheet = SpriteSheet(attack_path)
            
            # Attack1.png has 6 frames
            attack_frame_count = 6
            attack_frame_width = attack_sheet.width // attack_frame_count
            attack_frame_height = attack_sheet.height
            
            attack_frames_raw = attack_sheet.get_frames(attack_frame_width, attack_frame_height, attack_frame_count, 0)
            # Scale attack frames to 2x size
            attack_frames = [pygame.transform.scale(frame, (attack_frame_width * scale_factor, attack_frame_height * scale_factor)) for frame in attack_frames_raw]
            # Attack animation should be faster and not loop
            attack_animation = Animation(attack_frames, 0.08)  # 0.08 seconds per frame
            attack_animation.loop = False  # Don't loop attack animation
            
            self.animator.add_animation("attack", attack_animation)
            
            print(f"Loaded attack animation with {len(attack_frames)} frames ({attack_frame_width * scale_factor}x{attack_frame_height * scale_factor})")
            
            # Load special attack sprite sheet (Attack2.png)
            special_attack_path = sprite_path("Attack2.png")
            special_attack_sheet = SpriteSheet(special_attack_path)
            
            # Attack2.png has 6 frames
            special_attack_frame_count = 6
            special_attack_frame_width = special_attack_sheet.width // special_attack_frame_count
            special_attack_frame_height = special_attack_sheet.height
            
            special_attack_frames_raw = special_attack_sheet.get_frames(special_attack_frame_width, special_attack_frame_height, special_attack_frame_count, 0)
            # Scale special attack frames to 2x size
            special_attack_frames = [pygame.transform.scale(frame, (special_attack_frame_width * scale_factor, special_attack_frame_height * scale_factor)) for frame in special_attack_frames_raw]
            # Special attack animation should be slower and not loop
            special_attack_animation = Animation(special_attack_frames, 0.12)  # 0.12 seconds per frame (slower than regular attack)
            special_attack_animation.loop = False  # Don't loop special attack animation
            
            self.animator.add_animation("special_attack", special_attack_animation)
            
            print(f"Loaded special attack animation with {len(special_attack_frames)} frames ({special_attack_frame_width * scale_factor}x{special_attack_frame_height * scale_factor})")
            
            # Load run sprite sheet
            run_sheet = SpriteSheet(run_path)
            
            # Run.png has 8 frames
            run_frame_count = 8
            run_frame_width = run_sheet.width // run_frame_count
            run_frame_height = run_sheet.height
            
            run_frames_raw = run_sheet.get_frames(run_frame_width, run_frame_height, run_frame_count, 0)
            # Scale run frames to 2x size
            run_frames = [pygame.transform.scale(frame, (run_frame_width * scale_factor, run_frame_height * scale_factor)) for frame in run_frames_raw]
            run_animation = Animation(run_frames, 0.1)  # 0.1 seconds per frame for smooth running
            
            self.animator.add_animation("walk", run_animation)
            
            print(f"Loaded run animation with {len(run_frames)} frames ({run_frame_width * scale_factor}x{run_frame_height * scale_factor})")
            
            # Load death sprite sheet
            death_path = sprite_path("Death.png")
            death_sheet = SpriteSheet(death_path)
            
            # Death.png has 6 frames
            death_frame_count = 6
            death_frame_width = death_sheet.width // death_frame_count
            death_frame_height = death_sheet.height
            
            death_frames_raw = death_sheet.get_frames(death_frame_width, death_frame_height, death_frame_count, 0)
            # Scale death frames to 2x size
            death_frames = [pygame.transform.scale(frame, (death_frame_width * scale_factor, death_frame_height * scale_factor)) for frame in death_frames_raw]
            death_animation = Animation(death_frames, 0.15)  # 0.15 seconds per frame
            death_animation.loop = False  # Don't loop death animation
            
            self.animator.add_animation("dead", death_animation)
            
            print(f"Loaded death animation with {len(death_frames)} frames ({death_frame_width * scale_factor}x{death_frame_height * scale_factor})")
            
            # Load hit sprite sheet
            hit_path = sprite_path("Take Hit.png")
            hit_sheet = SpriteSheet(hit_path)
            
            # Take Hit.png - need to determine frame count (checking common counts)
            # Most sprite sheets have 4-6 frames for hit animations
            hit_frame_count = 4  # Starting with 4, will adjust if needed
            if hit_sheet.width % 4 == 0:
                hit_frame_count = 4
            elif hit_sheet.width % 3 == 0:
                hit_frame_count = 3
            elif hit_sheet.width % 5 == 0:
                hit_frame_count = 5
            elif hit_sheet.width % 6 == 0:
                hit_frame_count = 6
                
            hit_frame_width = hit_sheet.width // hit_frame_count
            hit_frame_height = hit_sheet.height
            
            hit_frames_raw = hit_sheet.get_frames(hit_frame_width, hit_frame_height, hit_frame_count, 0)
            # Scale hit frames to 2x size
            hit_frames = [pygame.transform.scale(frame, (hit_frame_width * scale_factor, hit_frame_height * scale_factor)) for frame in hit_frames_raw]
            hit_animation = Animation(hit_frames, 0.1)  # 0.1 seconds per frame for quick hit reaction
            hit_animation.loop = False  # Don't loop hit animation
            
            self.animator.add_animation("hit", hit_animation)
            
            print(f"Loaded hit animation with {len(hit_frames)} frames ({hit_frame_width * scale_factor}x{hit_frame_height * scale_factor})")
            
            # Load stun sprite sheet (white silhouette)
            stun_path = sprite_path("Take Hit - white silhouette.png")
            stun_sheet = SpriteSheet(stun_path)
            
            # Take Hit - white silhouette.png has 4 frames
            stun_frame_count = 4
            stun_frame_width = stun_sheet.width // stun_frame_count
            stun_frame_height = stun_sheet.height
            
            stun_frames_raw = stun_sheet.get_frames(stun_frame_width, stun_frame_height, stun_frame_count, 0)
            # Scale stun frames to 2x size
            stun_frames = [pygame.transform.scale(frame, (stun_frame_width * scale_factor, stun_frame_height * scale_factor)) for frame in stun_frames_raw]
            stun_animation = Animation(stun_frames, 0.2)  # 0.2 seconds per frame for stun effect
            stun_animation.loop = True  # Loop stun animation while stunned
            
            self.animator.add_animation("stun", stun_animation)
            
            print(f"Loaded stun animation with {len(stun_frames)} frames ({stun_frame_width * scale_factor}x{stun_frame_height * scale_factor})")
            
            # Load jump sprite sheet
            jump_path = sprite_path("Jump.png")
            jump_sheet = SpriteSheet(jump_path)
            
            # Jump.png has 2 frames (400x200 = 2 frames of 200x200 each)
            jump_frame_count = 2
            jump_frame_width = jump_sheet.width // jump_frame_count
            jump_frame_height = jump_sheet.height
            
            jump_frames_raw = jump_sheet.get_frames(jump_frame_width, jump_frame_height, jump_frame_count, 0)
            # Scale jump frames to 2x size
            jump_frames = [pygame.transform.scale(frame, (jump_frame_width * scale_factor, jump_frame_height * scale_factor)) for frame in jump_frames_raw]
            jump_animation = Animation(jump_frames, 0.15)  # 0.15 seconds per frame for smooth jumping
            jump_animation.loop = False  # Don't loop jump animation
            
            self.animator.add_animation("jump", jump_animation)
            
            print(f"Loaded jump animation with {len(jump_frames)} frames ({jump_frame_width * scale_factor}x{jump_frame_height * scale_factor})")
            
        except Exception as e:
            print(f"Could not load sprites: {e}")
            # Use fallback animation
            super().load_sprites()
        
        # Use idle animation for other states that don't have dedicated sprites yet
        if "idle" in self.animator.animations:
            idle_anim = self.animator.animations["idle"]
            self.animator.add_animation("block", idle_anim)


class Samurai2(Character):
    """Second samurai character (red) - AI opponent."""
    
    def __init__(self, x: float, y: float, attack_sound=None, block_sound=None, pain_sound=None):
        super().__init__(x, y, facing_right=False, attack_sound=attack_sound, block_sound=block_sound, pain_sound=pain_sound)
        self.color = (255, 100, 100)  # Red fallback
        self.speed = 180.0  # AI is slower than base speed (was 200.0)
    
    def load_sprites(self):
        """Load samurai sprites (same as player for now)."""
        # Path to sprites
        idle_path = sprite_path("Idle.png")
        attack_path = sprite_path("Attack1.png")
        run_path = sprite_path("Run.png")
        
        # Character scale factor (2x bigger)
        scale_factor = 2
        
        try:
            # Load idle sprite sheet
            idle_sheet = SpriteSheet(idle_path)
            
            # Extract 8 frames from the idle sprite sheet
            frame_width = idle_sheet.width // 8  # 8 frames horizontally
            frame_height = idle_sheet.height
            
            idle_frames_raw = idle_sheet.get_frames(frame_width, frame_height, 8, 0)
            
            # Apply red tint and scale to make AI character different
            tinted_idle_frames = []
            for frame in idle_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))  # Light red with transparency
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_idle_frames.append(scaled_frame)
            
            idle_animation = Animation(tinted_idle_frames, 0.15)
            self.animator.add_animation("idle", idle_animation)
            
            # Update character dimensions based on scaled sprite
            if tinted_idle_frames:
                self.width = frame_width * scale_factor
                self.height = frame_height * scale_factor
            
            print(f"Loaded AI idle animation with {len(tinted_idle_frames)} frames ({self.width}x{self.height})")
            
            # Load attack sprite sheet
            attack_sheet = SpriteSheet(attack_path)
            
            # Attack1.png has 6 frames
            attack_frame_count = 6
            attack_frame_width = attack_sheet.width // attack_frame_count
            attack_frame_height = attack_sheet.height
            
            attack_frames_raw = attack_sheet.get_frames(attack_frame_width, attack_frame_height, attack_frame_count, 0)
            
            # Apply red tint and scale to attack frames
            tinted_attack_frames = []
            for frame in attack_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (attack_frame_width * scale_factor, attack_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_attack_frames.append(scaled_frame)
            
            attack_animation = Animation(tinted_attack_frames, 0.08)
            attack_animation.loop = False
            self.animator.add_animation("attack", attack_animation)
            
            print(f"Loaded AI attack animation with {len(tinted_attack_frames)} frames ({attack_frame_width * scale_factor}x{attack_frame_height * scale_factor})")
            
            # Load special attack sprite sheet (Attack2.png)
            special_attack_path = sprite_path("Attack2.png")
            special_attack_sheet = SpriteSheet(special_attack_path)
            
            # Attack2.png has 6 frames
            special_attack_frame_count = 6
            special_attack_frame_width = special_attack_sheet.width // special_attack_frame_count
            special_attack_frame_height = special_attack_sheet.height
            
            special_attack_frames_raw = special_attack_sheet.get_frames(special_attack_frame_width, special_attack_frame_height, special_attack_frame_count, 0)
            
            # Apply red tint and scale to special attack frames
            tinted_special_attack_frames = []
            for frame in special_attack_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (special_attack_frame_width * scale_factor, special_attack_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_special_attack_frames.append(scaled_frame)
            
            special_attack_animation = Animation(tinted_special_attack_frames, 0.12)  # 0.12 seconds per frame (slower)
            special_attack_animation.loop = False
            self.animator.add_animation("special_attack", special_attack_animation)
            
            print(f"Loaded AI special attack animation with {len(tinted_special_attack_frames)} frames ({special_attack_frame_width * scale_factor}x{special_attack_frame_height * scale_factor})")
            
            # Load run sprite sheet
            run_sheet = SpriteSheet(run_path)
            
            # Run.png has 8 frames
            run_frame_count = 8
            run_frame_width = run_sheet.width // run_frame_count
            run_frame_height = run_sheet.height
            
            run_frames_raw = run_sheet.get_frames(run_frame_width, run_frame_height, run_frame_count, 0)
            
            # Apply red tint and scale to run frames
            tinted_run_frames = []
            for frame in run_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (run_frame_width * scale_factor, run_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_run_frames.append(scaled_frame)
            
            run_animation = Animation(tinted_run_frames, 0.1)
            self.animator.add_animation("walk", run_animation)
            
            print(f"Loaded AI run animation with {len(tinted_run_frames)} frames ({run_frame_width * scale_factor}x{run_frame_height * scale_factor})")
            
            # Load death sprite sheet
            death_path = sprite_path("Death.png")
            death_sheet = SpriteSheet(death_path)
            
            # Death.png has 6 frames
            death_frame_count = 6
            death_frame_width = death_sheet.width // death_frame_count
            death_frame_height = death_sheet.height
            
            death_frames_raw = death_sheet.get_frames(death_frame_width, death_frame_height, death_frame_count, 0)
            
            # Apply red tint and scale to death frames
            tinted_death_frames = []
            for frame in death_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (death_frame_width * scale_factor, death_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_death_frames.append(scaled_frame)
            
            death_animation = Animation(tinted_death_frames, 0.15)
            death_animation.loop = False
            self.animator.add_animation("dead", death_animation)
            
            print(f"Loaded AI death animation with {len(tinted_death_frames)} frames ({death_frame_width * scale_factor}x{death_frame_height * scale_factor})")
            
            # Load hit sprite sheet
            hit_path = sprite_path("Take Hit.png")
            hit_sheet = SpriteSheet(hit_path)
            
            # Take Hit.png - determine frame count
            hit_frame_count = 4  # Starting with 4, will adjust if needed
            if hit_sheet.width % 4 == 0:
                hit_frame_count = 4
            elif hit_sheet.width % 3 == 0:
                hit_frame_count = 3
            elif hit_sheet.width % 5 == 0:
                hit_frame_count = 5
            elif hit_sheet.width % 6 == 0:
                hit_frame_count = 6
                
            hit_frame_width = hit_sheet.width // hit_frame_count
            hit_frame_height = hit_sheet.height
            
            hit_frames_raw = hit_sheet.get_frames(hit_frame_width, hit_frame_height, hit_frame_count, 0)
            
            # Apply red tint and scale to hit frames
            tinted_hit_frames = []
            for frame in hit_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (hit_frame_width * scale_factor, hit_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_hit_frames.append(scaled_frame)
            
            hit_animation = Animation(tinted_hit_frames, 0.1)
            hit_animation.loop = False
            self.animator.add_animation("hit", hit_animation)
            
            print(f"Loaded AI hit animation with {len(tinted_hit_frames)} frames ({hit_frame_width * scale_factor}x{hit_frame_height * scale_factor})")
            
            # Load stun sprite sheet (white silhouette)
            stun_path = sprite_path("Take Hit - white silhouette.png")
            stun_sheet = SpriteSheet(stun_path)
            
            # Take Hit - white silhouette.png has 4 frames
            stun_frame_count = 4
            stun_frame_width = stun_sheet.width // stun_frame_count
            stun_frame_height = stun_sheet.height
            
            stun_frames_raw = stun_sheet.get_frames(stun_frame_width, stun_frame_height, stun_frame_count, 0)
            
            # Apply red tint and scale to stun frames (to differentiate AI)
            tinted_stun_frames = []
            for frame in stun_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (stun_frame_width * scale_factor, stun_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_stun_frames.append(scaled_frame)
            
            stun_animation = Animation(tinted_stun_frames, 0.2)  # 0.2 seconds per frame for stun effect
            stun_animation.loop = True  # Loop stun animation while stunned
            self.animator.add_animation("stun", stun_animation)
            
            print(f"Loaded AI stun animation with {len(tinted_stun_frames)} frames ({stun_frame_width * scale_factor}x{stun_frame_height * scale_factor})")
            
            # Load jump sprite sheet
            jump_path = sprite_path("Jump.png")
            jump_sheet = SpriteSheet(jump_path)
            
            # Jump.png has 2 frames (400x200 = 2 frames of 200x200 each)
            jump_frame_count = 2
            jump_frame_width = jump_sheet.width // jump_frame_count
            jump_frame_height = jump_sheet.height
            
            jump_frames_raw = jump_sheet.get_frames(jump_frame_width, jump_frame_height, jump_frame_count, 0)
            
            # Apply red tint and scale to jump frames
            tinted_jump_frames = []
            for frame in jump_frames_raw:
                # Scale frame to 2x size first
                scaled_frame = pygame.transform.scale(frame, (jump_frame_width * scale_factor, jump_frame_height * scale_factor))
                # Apply red overlay
                red_overlay = pygame.Surface(scaled_frame.get_size(), pygame.SRCALPHA)
                red_overlay.fill((255, 100, 100, 50))
                scaled_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                tinted_jump_frames.append(scaled_frame)
            
            jump_animation = Animation(tinted_jump_frames, 0.15)
            jump_animation.loop = False
            self.animator.add_animation("jump", jump_animation)
            
            print(f"Loaded AI jump animation with {len(tinted_jump_frames)} frames ({jump_frame_width * scale_factor}x{jump_frame_height * scale_factor})")
            
        except Exception as e:
            print(f"Could not load AI sprites: {e}")
            # Use fallback animation
            super().load_sprites()
        
        # Use idle animation for other states
        if "idle" in self.animator.animations:
            idle_anim = self.animator.animations["idle"]
            self.animator.add_animation("block", idle_anim)


class YellowNinja(Character):
    """Yellow Ninja enemy with sprite animations and AI behavior."""
    
    def __init__(self, x: float, y: float, attack_sound=None, block_sound=None, pain_sound=None):
        """Initialize Yellow Ninja enemy."""
        super().__init__(x, y, facing_right=False, attack_sound=attack_sound, block_sound=block_sound, pain_sound=pain_sound)
        
        # Yellow Ninja appearance
        self.color = (255, 255, 0)  # Yellow fallback
        self.enemy_name = "Yellow Ninja"
        self.sprite_scale = 2.25  # Slightly larger than player
        
        # AI behavior variables (Level 2 - slightly harder than Level 1)
        self.ai_timer = 0.0
        self.ai_decision_interval = 0.15  # Slightly faster decisions than Level 1
        self.ai_reaction_time = 0.25  # Slightly faster reactions
        self.ai_aggression = 0.75  # More aggressive than Level 1
        self.ai_last_player_action = None
        self.ai_reaction_timer = 0.0
        self.ai_current_action = "idle"
        
        # Special attacks
        self.special_attack_cooldown = 0.0
        self.special_attack_cooldown_time = 8.0  # Faster special attack cooldown
        
        # Additional render offset to align feet to ground
        self.sprite_y_offset = 0

        # Load Yellow Ninja sprites
        self.load_sprites()
    
    def load_sprites(self):
        """Load Yellow Ninja sprite animations."""
        try:
            # Initialize sprite animator
            self.animator = SpriteAnimator()
            
            # Load sprite sheets for Yellow Ninja
            idle_sheet = SpriteSheet(sprite_path("YellowNinja/yellowNinja - idle.png"))
            walk_sheet = SpriteSheet(sprite_path("YellowNinja/yellowNinja - walk.png"))
            attack_sheet = SpriteSheet(sprite_path("YellowNinja/yellowNinja - attack.png"))
            hit_sheet = SpriteSheet(sprite_path("YellowNinja/yellowNinja - hit.png"))
            death_sheet = SpriteSheet(sprite_path("YellowNinja/yellowNinja - Death.png"))
            
            # Use the correct frame counts provided by user
            idle_frames = 8
            walk_frames = 10
            attack_frames = 20
            hit_frames = 4
            death_frames = 14
            
            print(f"Yellow Ninja loading sprites with frame counts: idle={idle_frames}, walk={walk_frames}, attack={attack_frames}, hit={hit_frames}, death={death_frames}")
            
            # Match the player's dynamic slicing approach
            # Determine per-frame dimensions from sheet sizes
            idle_w = idle_sheet.width // idle_frames
            idle_h = idle_sheet.height
            walk_w = walk_sheet.width // walk_frames
            walk_h = walk_sheet.height
            attack_w = attack_sheet.width // attack_frames
            attack_h = attack_sheet.height
            hit_w = hit_sheet.width // hit_frames
            hit_h = hit_sheet.height
            death_w = death_sheet.width // death_frames
            death_h = death_sheet.height
            
            idle_frames_list_raw = idle_sheet.get_frames(idle_w, idle_h, idle_frames, 0)
            walk_frames_list_raw = walk_sheet.get_frames(walk_w, walk_h, walk_frames, 0)
            attack_frames_list_raw = attack_sheet.get_frames(attack_w, attack_h, attack_frames, 0)
            hit_frames_list_raw = hit_sheet.get_frames(hit_w, hit_h, hit_frames, 0)
            death_frames_list_raw = death_sheet.get_frames(death_w, death_h, death_frames, 0)
            
            # Scale factor: slightly larger than player
            scale_factor = self.sprite_scale
            def scale(frames, fw, fh):
                return [
                    pygame.transform.scale(frame, (int(fw * scale_factor), int(fh * scale_factor)))
                    for frame in frames
                ]
            
            idle_frames_list = scale(idle_frames_list_raw, idle_w, idle_h)
            walk_frames_list = scale(walk_frames_list_raw, walk_w, walk_h)
            attack_frames_list = scale(attack_frames_list_raw, attack_w, attack_h)
            hit_frames_list = scale(hit_frames_list_raw, hit_w, hit_h)
            death_frames_list = scale(death_frames_list_raw, death_w, death_h)
            
            # Update YellowNinja collision box to match scaled idle sprite
            if idle_frames_list:
                self.width = int(idle_w * scale_factor)
                self.height = int(idle_h * scale_factor)
                # Compute baseline offset so visible feet (bbox.bottom) align to collision bottom
                test_frame = idle_frames_list[0]
                try:
                    bbox = test_frame.get_bounding_rect(min_alpha=1)
                    frame_h = test_frame.get_height()
                    bottom_padding = frame_h - bbox.bottom  # transparent pixels below the visible feet
                    # Base anchor puts sprite bottom (frame_h) below collision bottom by (frame_h - self.height)/2.
                    # We add an offset so bbox.bottom sits on collision bottom:
                    # offset = bottom_padding - (frame_h - self.height)/2
                    self.sprite_y_offset = int(bottom_padding - (frame_h - self.height) / 2)
                except Exception:
                    self.sprite_y_offset = 0
            
            # Animation timing aligned with Character timers
            # - Attack duration in Character is 0.48s → 20 frames => 0.024s/frame
            # - Hit duration is 0.4s → 4 frames => 0.1s/frame
            idle_anim = Animation(idle_frames_list, 0.15)
            walk_anim = Animation(walk_frames_list, 0.10)
            attack_anim = Animation(attack_frames_list, 0.024); attack_anim.loop = False
            hit_anim = Animation(hit_frames_list, 0.10); hit_anim.loop = False
            death_anim = Animation(death_frames_list, 0.12); death_anim.loop = False
            
            # Add animations to animator
            self.animator.add_animation("idle", idle_anim)
            self.animator.add_animation("walk", walk_anim)
            self.animator.add_animation("run", walk_anim)  # Use walk for run
            self.animator.add_animation("attack", attack_anim)
            self.animator.add_animation("block", idle_anim)  # Use idle for block
            # Use idle as jump placeholder (requested)
            self.animator.add_animation("jump", idle_anim)
            self.animator.add_animation("hit", hit_anim)
            self.animator.add_animation("dead", death_anim)
            
            # Start with idle animation
            self.animator.play_animation("idle", True)
            
            print("Yellow Ninja sprites loaded successfully")
            
        except Exception as e:
            print(f"Could not load Yellow Ninja sprites: {e}")
            import traceback
            traceback.print_exc()
            # Use fallback animation
            super().load_sprites()
        
        # Use idle animation for other states
        if self.animator and "idle" in self.animator.animations:
            idle_anim = self.animator.animations["idle"]
            self.animator.add_animation("block", idle_anim)
    
    def update(self, dt: float, gravity: float, ground_y: float, opponent: 'Character', arena_left: float = -100, arena_right: float = 900):
        """Update Yellow Ninja with AI behavior.""" 
        # Update combat timers manually
        self._update_combat(dt)
        # Update blink timer if active
        if hasattr(self, "_blink_timer") and self._blink_timer > 0:
            self._blink_timer = max(0.0, self._blink_timer - dt)
        
        # Apply physics manually to avoid base class interference
        if not self.is_dead:
            # Apply gravity
            if not self.on_ground:
                self.velocity_y += gravity * dt
            
            # Apply movement
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
            # Ground collision
            if self.y >= ground_y:
                self.y = ground_y
                self.velocity_y = 0
                self.on_ground = True
            else:
                self.on_ground = False
        
        # AI behavior
        self._update_ai(dt, opponent)
        
        # Enforce arena boundaries
        if self.x < arena_left:
            self.x = arena_left
        elif self.x > arena_right:
            self.x = arena_right
            
        # Update animation manually for stability
        self._update_animation_state()
        
        # Update animator
        if self.animator:
            self.animator.update(dt)
    
    def _update_animation_state(self):
        """Update animation state based on character state without frequent resets."""
        if not self.animator:
            return
        
        desired = "idle"
        if self.is_dead:
            desired = "dead"
        elif self.is_hit and self.hit_duration > 0:
            desired = "hit"
        elif self.is_attacking:
            desired = "attack"
        elif self.is_blocking:
            desired = "block"
        elif abs(self.velocity_x) > 10:
            desired = "walk"
        
        if self.animator.current_animation_name != desired:
            # Do not reset frames when switching between idle/walk to avoid popping
            reset = desired in ("attack", "hit", "dead")
            self.animator.play_animation(desired, reset)
    
    def _update_ai(self, dt: float, player: 'Character'):
        """Enhanced AI behavior for Yellow Ninja."""
        if self.is_dead:
            return
        
        self.ai_timer += dt
        
        # Make decisions periodically
        if self.ai_timer >= self.ai_decision_interval:
            self.ai_timer = 0.0
            self._make_ai_decision(player)
        
        # Execute current action
        self._execute_ai_action(dt, player)
    
    def _make_ai_decision(self, player: 'Character'):
        """Enhanced AI decision making for Yellow Ninja."""
        distance = abs(self.x - player.x)
        
        # Check if player is attacking
        if player.is_attacking and distance < 100:
            if self.stamina >= 50:  # Can afford to block
                self.ai_current_action = "block"
            else:
                self.ai_current_action = "retreat"
        elif distance < 70:  # Close range - slightly more aggressive
            if self.stamina >= 50 and random.random() < self.ai_aggression:
                # Try special attack if available
                if self.special_attack_cooldown <= 0:
                    self.ai_current_action = "special_attack"
                else:
                    self.ai_current_action = "attack"
            else:
                self.ai_current_action = "block"
        elif distance < 180:  # Medium range - more active
            if random.random() < self.ai_aggression:
                self.ai_current_action = "approach"
            else:
                self.ai_current_action = "idle"
        else:  # Long range
            self.ai_current_action = "approach"
    
    def _execute_ai_action(self, dt: float, player: 'Character'):
        """Execute the current AI action."""
        # Determine desired facing based on relative position, but apply a deadzone to avoid flicker
        desired_facing_right = self.facing_right
        if abs(self.x - player.x) > 8:  # deadzone of 8px to prevent oscillation
            desired_facing_right = self.x < player.x

        if self.ai_current_action == "approach":
            # Move towards player
            if desired_facing_right:
                self.velocity_x = self.speed * 1.1  # Slightly faster than player
            else:
                self.velocity_x = -self.speed * 1.1
            self.facing_right = desired_facing_right
        elif self.ai_current_action == "retreat":
            # Move away from player
            if desired_facing_right:
                self.velocity_x = -self.speed
            else:
                self.velocity_x = self.speed
            self.facing_right = desired_facing_right
        elif self.ai_current_action == "attack":
            self.velocity_x = 0
            if not self.is_attacking and self.attack_cooldown <= 0:
                self.attack()
        elif self.ai_current_action == "special_attack":
            self.velocity_x = 0
            if not self.is_attacking and self.special_attack_cooldown <= 0 and not self.is_special_attacking:
                # Teleport behind player with blink effect
                self.is_special_attacking = True
                self.special_attack_duration = 0.3  # quick teleport pre-attack window
                # Blink: briefly hide by setting a flag on animator (simulate by skipping render frames)
                self._blink_timer = 0.2
                # Reposition behind the player
                offset = 30
                if player.facing_right:
                    # Appear behind player's back (to their left)
                    self.x = player.x - self.width - offset
                    self.facing_right = True  # face player
                else:
                    # Player faces left; appear on their right
                    self.x = player.x + player.width + offset
                    self.facing_right = False  # face player
                # Align to ground
                self.y = player.y
                self.on_ground = True
                # Immediately perform an attack from behind
                self.current_attack_id += 1
                self.is_attacking = True
                self.attack_duration = 0.48
                self.can_hit = False
                if "attack" in self.animator.animations:
                    self.animator.play_animation("attack", True)
                # Start special cooldown
                self.special_attack_cooldown = self.special_attack_cooldown_time
        elif self.ai_current_action == "block":
            self.velocity_x = 0
            self.is_blocking = True
        else:  # idle
            self.velocity_x = 0
            self.is_blocking = False
    
    def render(self, surface: pygame.Surface):
        """Render YellowNinja with baseline adjustment so feet align with ground."""
        # Blink effect: skip rendering on alternating frames while timer active
        if hasattr(self, "_blink_timer") and self._blink_timer > 0:
            # 50ms cadence blink
            if (int(pygame.time.get_ticks() / 50) % 2) == 0:
                return
        # Get current sprite frame
        current_frame = self.animator.get_current_frame()
        if not current_frame:
            return
        
        # Apply horizontal flip if character is facing left
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        # Match base render anchor and apply vertical offset computed from idle frame padding
        render_x = self.x - (current_frame.get_width() - self.width) // 2
        render_y = self.y - (current_frame.get_height() - self.height) // 2
        render_y += int(self.sprite_y_offset)
        
        surface.blit(current_frame, (render_x, render_y))


# FUTURE: Scalable Enemy System for 10 Levels
# For future levels, create enemy classes like:
# - GreenNinja (Level 3) - More defensive, higher health
# - RedNinja (Level 4) - Very aggressive, fast attacks  
# - BlueMage (Level 5) - Ranged attacks, teleport ability
# - BlackAssassin (Level 6) - Stealth, critical hits
# - WhiteMonk (Level 7) - Counter-attacks, healing
# - PurpleWarrior (Level 8) - Heavy armor, slow but strong
# - OrangeBerserker (Level 9) - Rage mode, increasing damage
# - RainbowBoss (Level 10) - All abilities combined
#
# Each enemy class should inherit from Character and have:
# - Unique sprite folder in assets/sprites/
# - Progressive AI difficulty (faster decisions, higher aggression)
# - Special abilities unique to that enemy type
# - Balanced stats for progression curve