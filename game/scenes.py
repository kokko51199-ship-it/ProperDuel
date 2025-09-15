"""
Game Scenes
Fight scene and scene management.
"""

import pygame
import os
import math
import random
from typing import Optional
from game.character import Samurai1, Samurai2, YellowNinja
from game.input_handler import PlayerInput
from game.resource_utils import sprite_path


class SplashScene:
    """Splash screen scene with Vic Vega branding."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the splash scene."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Splash state
        self.splash_timer = 0.0
        self.splash_duration = 7.0  # Show splash for 7 seconds total
        self.fade_start_time = 4.0  # Start fading after 4 seconds
        self.fade_duration = 3.0    # Fade for 3 seconds (4s show + 3s fade = 7s total)
        self.finished = False
        
        # Background
        self.bg_color = (10, 10, 20)  # Very dark blue background
        
        # Fonts
        self.mega_font = None
        self.large_font = None
        self._init_fonts()
        
        # Animation effects
        self.glow_timer = 0.0
        self.glow_speed = 2.0  # Glow pulsing speed
        
    def _init_fonts(self):
        """Initialize fonts for splash screen."""
        self.mega_font = pygame.font.Font(None, 72)     # Extra large for splash
        self.large_font = pygame.font.Font(None, 48)    # Large for underline
        
    def _render_pixel_text(self, text: str, font: pygame.font.Font, color: tuple, scale: int = 2):
        """Render text with pixelated, retro look by scaling up small text."""
        # Render text at small size first
        small_surface = font.render(text, False, color)  # False = no anti-aliasing for pixel look
        
        # Scale up using nearest neighbor to maintain pixel edges
        original_size = small_surface.get_size()
        new_size = (original_size[0] * scale, original_size[1] * scale)
        scaled_surface = pygame.transform.scale(small_surface, new_size)
        
        return scaled_surface
    
    def handle_input(self, keys_pressed: dict, events: list) -> str:
        """Handle splash input - can skip with any key."""
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.finished = True
                return "skip"
        return "continue"
    
    def update(self, dt: float):
        """Update splash animations and timing."""
        self.splash_timer += dt
        self.glow_timer += dt
        
        if self.splash_timer >= self.splash_duration:
            self.finished = True
    
    def is_finished(self) -> bool:
        """Check if splash screen is finished."""
        return self.finished
    
    def render(self, screen: pygame.Surface):
        """Render the splash screen."""
        # Clear with dark background
        screen.fill(self.bg_color)
        
        # Calculate fade effect
        fade_alpha = 255  # Default full opacity
        if self.splash_timer > self.fade_start_time:
            # Calculate fade progress (0.0 = full opacity, 1.0 = fully transparent)
            fade_progress = (self.splash_timer - self.fade_start_time) / self.fade_duration
            fade_progress = min(fade_progress, 1.0)  # Clamp to 1.0
            fade_alpha = int(255 * (1.0 - fade_progress))  # 255 -> 0
        
        # Calculate glow effect intensity
        glow_intensity = abs(math.cos(self.glow_timer * self.glow_speed))
        
        # Create multiple glow layers for flashy effect
        base_pink = (255, 20, 147)  # Hot pink base
        bright_pink = (255, 105, 180)  # Brighter pink for glow
        
        # Mix colors based on glow intensity
        glow_color = (
            int(base_pink[0] + (bright_pink[0] - base_pink[0]) * glow_intensity),
            int(base_pink[1] + (bright_pink[1] - base_pink[1]) * glow_intensity),
            int(base_pink[2] + (bright_pink[2] - base_pink[2]) * glow_intensity)
        )
        
        # Create a surface for the entire splash content to apply fade
        splash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        splash_surface.fill((0, 0, 0, 0))  # Transparent background
        
        # ASCII Art above VIC VEGA text - Simple character silhouette
        ascii_art = [
            "################################################################",
            "################################################################",
            "################################################################",
            "################################################################",
            "################################################################",
            "################################@@##############################",
            "##############################@@@@@@############################",
            "############################@@@@@@@@@@##########################",
            "##########################@@@@@@@@@@@@@@########################",
            "########################@@@@@@@@@@@@@@@@@@######################",
            "######################@@@@@@@@@@@@@@@@@@@@@@####################",
            "####################@@@@@@@@@@@@@@@@@@@@@@@@@@##################",
            "##################@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@################",
            "################@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##############",
            "##############@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@############",
            "############@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##########",
            "##########@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@########",
            "########@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@######",
            "######@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@####",
            "####@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##",
            "##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
            "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
        ]
        
        # Render ASCII art with neon pink glow
        try:
            ascii_font = pygame.font.Font(None, 12)  # Smaller font for better fitting
            ascii_start_y = 20  # Start position for ASCII art
            
            for i, line in enumerate(ascii_art):
                # Create the ASCII art line with glow effect
                ascii_surface = ascii_font.render(line, False, glow_color)
                ascii_rect = ascii_surface.get_rect()
                ascii_rect.centerx = self.screen_width // 2
                ascii_rect.y = ascii_start_y + i * 10  # Tighter line spacing
                
                # Add shadow effect for the ASCII art
                shadow_surface = ascii_font.render(line, False, (80, 5, 40))
                shadow_rect = shadow_surface.get_rect()
                shadow_rect.centerx = self.screen_width // 2 + 1
                shadow_rect.y = ascii_start_y + i * 10 + 1
                
                splash_surface.blit(shadow_surface, shadow_rect)
                splash_surface.blit(ascii_surface, ascii_rect)
        except Exception as e:
            print(f"ASCII art rendering error: {e}")
        
        # Render main text "VIC VEGA" with multiple shadow layers for depth
        main_text = "VIC VEGA"
        
        # Adjust position to be below ASCII art
        main_text_y = self.screen_height // 2 + 80  # Move down more to make room for ASCII art
        
        # Create multiple shadow layers (outer to inner)
        shadow_offsets = [(6, 6), (4, 4), (2, 2)]
        shadow_colors = [(80, 5, 40), (120, 10, 60), (160, 15, 80)]
        
        for offset, shadow_color in zip(shadow_offsets, shadow_colors):
            shadow_text = self._render_pixel_text(main_text, self.mega_font, shadow_color, 2)
            shadow_rect = shadow_text.get_rect()
            shadow_rect.centerx = self.screen_width // 2 + offset[0]
            shadow_rect.centery = main_text_y + offset[1]
            splash_surface.blit(shadow_text, shadow_rect)
        
        # Main text with glow effect
        main_surface = self._render_pixel_text(main_text, self.mega_font, glow_color, 2)
        main_rect = main_surface.get_rect()
        main_rect.centerx = self.screen_width // 2
        main_rect.centery = main_text_y
        splash_surface.blit(main_surface, main_rect)
        
        # Create underline effect with same glow
        underline_y = main_rect.bottom + 10
        underline_thickness = 8
        
        # Multiple underline layers for glow effect
        for i in range(3):
            thickness = underline_thickness + (2 - i) * 2
            alpha_color = (
                glow_color[0],
                glow_color[1], 
                glow_color[2]
            )
            
            # Create surface for underline with alpha
            underline_surf = pygame.Surface((main_rect.width + 20, thickness))
            underline_surf.fill(alpha_color)
            if i > 0:
                underline_surf.set_alpha(100 - i * 30)  # Fade outer layers
            
            underline_rect = underline_surf.get_rect()
            underline_rect.centerx = self.screen_width // 2
            underline_rect.y = underline_y + i * 2
            splash_surface.blit(underline_surf, underline_rect)
        
        # Add some sparkle effects directly to splash surface
        for _ in range(8):
            if random.random() < 0.3:  # 30% chance each frame
                spark_x = random.randint(main_rect.left - 50, main_rect.right + 50)
                spark_y = random.randint(main_rect.top - 30, main_rect.bottom + 50)
                spark_size = random.randint(2, 6)
                pygame.draw.circle(splash_surface, (255, 255, 255), (spark_x, spark_y), spark_size)
        
        # Skip instruction at bottom
        skip_surface = self._render_pixel_text("PRESS ANY KEY TO CONTINUE", self.large_font, (150, 150, 150), 1)
        skip_rect = skip_surface.get_rect()
        skip_rect.centerx = self.screen_width // 2
        skip_rect.y = self.screen_height - 60
        splash_surface.blit(skip_surface, skip_rect)
        
        # Apply fade effect to the entire splash surface
        if fade_alpha < 255:
            splash_surface.set_alpha(fade_alpha)
        
        # Blit the faded splash surface to the main screen
        screen.blit(splash_surface, (0, 0))


class MainMenuScene:
    """Main menu scene with retro aesthetics."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the main menu scene."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Menu state
        self.selected_option = 0
        self.menu_options = ["START GAME", "QUIT"]
        
        # Background
        self.bg_color = (20, 30, 40)  # Dark blue background
        self.background_image = None
        self._load_background()
        
        # Fonts
        self.font = None
        self.large_font = None
        self.mega_font = None
        self._init_fonts()
        
        # Animation
        self.menu_blink_timer = 0.0
        self.menu_blink_speed = 1.0  # Blinks per second
        
    def _init_fonts(self):
        """Initialize pixelated retro fonts."""
        self.font = pygame.font.Font(None, 24)          # Medium pixelated text  
        self.large_font = pygame.font.Font(None, 32)    # Large pixelated text
        self.mega_font = pygame.font.Font(None, 48)     # Mega pixelated text
    
    def _render_pixel_text(self, text: str, font: pygame.font.Font, color: tuple, scale: int = 2):
        """Render text with pixelated, retro look by scaling up small text."""
        # Render text at small size first
        small_surface = font.render(text, False, color)  # False = no anti-aliasing for pixel look
        
        # Scale up using nearest neighbor to maintain pixel edges
        original_size = small_surface.get_size()
        new_size = (original_size[0] * scale, original_size[1] * scale)
        scaled_surface = pygame.transform.scale(small_surface, new_size)
        
        return scaled_surface
    
    def _load_background(self):
        """Load background image if available."""
        bg_path = sprite_path("background.png")
        if os.path.exists(bg_path):
            try:
                self.background_image = pygame.image.load(bg_path)
                # Scale to screen size
                self.background_image = pygame.transform.scale(
                    self.background_image, 
                    (self.screen_width, self.screen_height)
                )
            except pygame.error:
                self.background_image = None
    
    def handle_input(self, keys_pressed: dict, events: list) -> str:
        """Handle menu input and return action."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 0:  # START GAME
                        return "start_game"
                    elif self.selected_option == 1:  # QUIT
                        return "quit"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
        
        return "continue"
    
    def update(self, dt: float):
        """Update menu animations."""
        self.menu_blink_timer += dt
    
    def render(self, screen: pygame.Surface):
        """Render the main menu."""
        # Draw background
        if self.background_image:
            # Darken the background for menu
            darkened_bg = self.background_image.copy()
            darkened_bg.fill((0, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(darkened_bg, (0, 0))
        else:
            screen.fill(self.bg_color)
        
        # Title with neon effect (pink shadow + blue text)
        # First render the shadow in neon pink, offset by a few pixels
        title_shadow = self._render_pixel_text("PROPER DUEL", self.large_font, (255, 20, 147), 3)  # Hot pink shadow
        shadow_rect = title_shadow.get_rect()
        shadow_rect.centerx = self.screen_width // 2 + 3  # Offset shadow 3 pixels right
        shadow_rect.y = 80 + 3  # Offset shadow 3 pixels down
        screen.blit(title_shadow, shadow_rect)
        
        # Then render the main title in neon blue on top
        title_text = self._render_pixel_text("PROPER DUEL", self.large_font, (0, 255, 255), 3)  # Cyan/neon blue
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen_width // 2
        title_rect.y = 80
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self._render_pixel_text("PIXEL FIGHTING CHAMPIONSHIP", self.font, (200, 200, 200), 2)
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.centerx = self.screen_width // 2
        subtitle_rect.y = title_rect.bottom + 15  # Closer to the title
        screen.blit(subtitle_text, subtitle_rect)
        
        # Menu options
        menu_start_y = self.screen_height // 2 + 50
        option_spacing = 60
        
        for i, option in enumerate(self.menu_options):
            # Determine color and scale based on selection
            if i == self.selected_option:
                # Neon effect for selected option (same as title)
                blink_phase = int(self.menu_blink_timer * self.menu_blink_speed * 2) % 2
                if blink_phase == 0:
                    color = (0, 255, 255)      # Bright neon blue (same as title)
                    shadow_color = (255, 20, 147)  # Hot pink shadow
                else:
                    color = (0, 200, 200)      # Slightly darker blue
                    shadow_color = (200, 15, 120)  # Slightly darker pink
                scale = 3
                prefix = "> "
                
                # Render shadow first (offset)
                shadow_text = self._render_pixel_text(f"{prefix}{option}", self.large_font, shadow_color, scale)
                shadow_rect = shadow_text.get_rect()
                shadow_rect.centerx = self.screen_width // 2 + 2  # Offset shadow 2 pixels right
                shadow_rect.y = menu_start_y + i * option_spacing + 2  # Offset shadow 2 pixels down
                screen.blit(shadow_text, shadow_rect)
            else:
                color = (180, 180, 180)  # Gray for unselected
                scale = 2
                prefix = "  "
            
            # Render main text
            option_text = self._render_pixel_text(f"{prefix}{option}", self.large_font, color, scale)
            option_rect = option_text.get_rect()
            option_rect.centerx = self.screen_width // 2
            option_rect.y = menu_start_y + i * option_spacing
            screen.blit(option_text, option_rect)
        
        # Instructions
        instructions = [
            "USE ARROW KEYS TO NAVIGATE",
            "PRESS ENTER TO SELECT",
            "ESC TO QUIT"
        ]
        
        inst_start_y = self.screen_height - 120
        for i, instruction in enumerate(instructions):
            inst_text = self._render_pixel_text(instruction, self.font, (120, 120, 120), 1)
            inst_rect = inst_text.get_rect()
            inst_rect.centerx = self.screen_width // 2
            inst_rect.y = inst_start_y + i * 25
            screen.blit(inst_text, inst_rect)


class FightScene:
    """Main fighting scene with player vs AI - First to 3 wins."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the fight scene."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Audio (will be set by the game engine)
        self.attack_sound = None
        self.block_sound = None
        self.pain_sound = None
        
        # Create characters (attack_sound will be updated when available)
        self.player1 = Samurai1(150, 335)  # Human player (left side)
        self.player2 = Samurai2(600, 335)  # AI opponent (right side)
        
        # Match state (first to 3 wins)
        self.player_wins = 0
        self.ai_wins = 0
        self.wins_needed = 3
        self.current_round = 1
        
        # Round state
        self.round_time = 99.0  # seconds
        self.round_over = False
        self.round_winner: Optional[str] = None
        self.match_over = False
        self.match_winner: Optional[str] = None
        
        # Round transition
        self.round_end_timer = 0.0
        self.round_end_duration = 2.5  # seconds to show death animation and round result
        
        # Pause state
        self.is_paused = False
        self.pause_blink_timer = 0.0
        self.pause_blink_speed = 2.0  # Blinks per second
        
        # Dialogue state
        self.showing_dialogue = False
        self.dialogue_phase = "threat"  # "threat", "choices", "outcome"
        self.dialogue_timer = 0.0
        self.selected_choice = 0  # 0 = Spare, 1 = Finish
        self.player_choice = None  # "spare" or "finish"
        self.dialogue_complete = False
        
        # Background
        self.bg_color = (50, 80, 50)  # Dark green fallback
        self.background_image = None
        self._load_background()
        
        # Font for UI (will be initialized when needed)
        self.font = None
        self.small_font = None
        self.large_font = None
        self.mega_font = None
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize pixelated retro fonts."""
        # Create pixelated fonts by using small sizes and no anti-aliasing
        self.small_font = pygame.font.Font(None, 16)    # Small pixelated text
        self.font = pygame.font.Font(None, 24)          # Medium pixelated text  
        self.large_font = pygame.font.Font(None, 32)    # Large pixelated text
        self.mega_font = pygame.font.Font(None, 48)     # Mega pixelated text
    
    def _render_pixel_text(self, text: str, font: pygame.font.Font, color: tuple, scale: int = 2):
        """Render text with pixelated, retro look by scaling up small text."""
        # Render text at small size first
        small_surface = font.render(text, False, color)  # False = no anti-aliasing for pixel look
        
        # Scale up using nearest neighbor to maintain pixel edges
        original_size = small_surface.get_size()
        new_size = (original_size[0] * scale, original_size[1] * scale)
        scaled_surface = pygame.transform.scale(small_surface, new_size)
        
        return scaled_surface
    
    def set_sounds(self, attack_sound, block_sound, pain_sound):
        """Set attack, block, and pain sounds for both characters."""
        self.attack_sound = attack_sound
        self.block_sound = block_sound
        self.pain_sound = pain_sound
        self.player1.attack_sound = attack_sound
        self.player1.block_sound = block_sound
        self.player1.pain_sound = pain_sound
        self.player2.attack_sound = attack_sound
        self.player2.block_sound = block_sound
        self.player2.pain_sound = pain_sound
    
    def update_pause(self, dt: float, paused: bool):
        """Update pause state and blinking animation."""
        self.is_paused = paused
        if self.is_paused:
            self.pause_blink_timer += dt
    
    def handle_dialogue_input(self, events: list):
        """Handle input during dialogue sequences."""
        if not self.showing_dialogue:
            return
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.dialogue_phase == "choices":
                    # Handle choice selection
                    if event.key == pygame.K_1:
                        self.selected_choice = 0
                    elif event.key == pygame.K_2:
                        self.selected_choice = 1
                    elif event.key == pygame.K_UP:
                        self.selected_choice = 0
                    elif event.key == pygame.K_DOWN:
                        self.selected_choice = 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Confirm choice
                        self.player_choice = "spare" if self.selected_choice == 0 else "finish"
                        self.dialogue_phase = "outcome"
                        self.dialogue_timer = 0.0
                        print(f"Player chose: {self.player_choice}")
                        
                elif self.dialogue_phase == "outcome":
                    # Handle continue after outcome
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.dialogue_complete = True
                        print("Dialogue complete - transitioning to next scene")
    
    def update_dialogue(self, dt: float):
        """Update dialogue progression and timers."""
        if not self.showing_dialogue:
            return
            
        self.dialogue_timer += dt
        
        # Auto-progress from threat to choices after 3 seconds
        if self.dialogue_phase == "threat" and self.dialogue_timer >= 3.0:
            self.dialogue_phase = "choices"
            self.dialogue_timer = 0.0
            
        # Check if dialogue is complete to end the match
        if self.dialogue_complete:
            self.match_over = True
            self.match_winner = "Player"
            self.showing_dialogue = False
            print(f"MATCH OVER! Player wins with choice: {self.player_choice}")
    
    def update(self, dt: float, player1_input: PlayerInput, player2_input: PlayerInput):
        """Update the fight scene."""
        if self.match_over:
            return
        
        # Handle round transition
        if self.round_over:
            self.round_end_timer += dt
            # Continue updating characters so death animation can play
            self.player1.update(dt, player1_input)
            self.player2.update(dt, player2_input)
            if self.round_end_timer >= self.round_end_duration:
                self._start_new_round()
            return
        
        # Update characters
        self.player1.update(dt, player1_input)
        self.player2.update(dt, player2_input)
        
        # Check for collisions and combat
        self._handle_combat()
        
        # Update timer
        self.round_time -= dt
        if self.round_time <= 0:
            self.round_time = 0
            self._end_round("time")
        
        # Check for knockout
        if self.player1.health <= 0 and not self.player1.is_dead:
            # Player just died, trigger death animation
            pass
        elif self.player2.health <= 0 and not self.player2.is_dead:
            # AI just died, trigger death animation
            pass
        elif self.player1.is_dead and self.player1.is_death_animation_finished():
            self._end_round("ai_win")
        elif self.player2.is_dead and self.player2.is_death_animation_finished():
            self._end_round("player_win")
    
    def _handle_combat(self):
        """Handle combat between player and AI."""
        # Check if player hits AI with regular attack
        p1_attack = self.player1.get_attack_rect()
        if p1_attack and p1_attack.colliderect(self.player2.get_rect()):
            # Use god mode damage if active, otherwise normal damage
            damage = 100 if self.player1.god_mode else 3
            if self.player2.take_damage(damage, self.player1.x):  # Pass attacker's position
                print("Player hits Evil Twin!")
                self.player1.can_hit = False  # Prevent multiple hits from same attack
        
        # Check if player hits AI with special attack
        p1_special_attack = self.player1.get_special_attack_rect()
        if p1_special_attack and p1_special_attack.colliderect(self.player2.get_rect()):
            # Use god mode damage if active, otherwise normal special damage
            damage = 100 if self.player1.god_mode else 8
            if self.player2.take_damage(damage, self.player1.x):  # Higher damage for special attack
                print("Player special hits Evil Twin!")
                self.player1.can_special_hit = False  # Prevent multiple hits from same special attack
        
        # Check if AI hits player with regular attack
        p2_attack = self.player2.get_attack_rect()
        if p2_attack and p2_attack.colliderect(self.player1.get_rect()):
            if self.player1.take_damage(3, self.player2.x):  # Pass attacker's position
                print("Evil Twin hits Player!")
                self.player2.can_hit = False  # Prevent multiple hits from same attack
        
        # Check if AI hits player with special attack
        p2_special_attack = self.player2.get_special_attack_rect()
        if p2_special_attack and p2_special_attack.colliderect(self.player1.get_rect()):
            if self.player1.take_damage(8, self.player2.x):  # Higher damage for special attack
                print("Evil Twin special hits Player!")
                self.player2.can_special_hit = False  # Prevent multiple hits from same special attack
    
    def _end_round(self, result: str):
        """End the current round and determine winner."""
        self.round_over = True
        self.round_end_timer = 0.0
        
        if result == "player_win":
            self.round_winner = "Player"
            self.player_wins += 1
        elif result == "ai_win":
            self.round_winner = "Evil Twin"
            self.ai_wins += 1
        elif result == "time":
            # Determine winner by health
            if self.player1.health > self.player2.health:
                self.round_winner = "Player"
                self.player_wins += 1
            elif self.player2.health > self.player1.health:
                self.round_winner = "Evil Twin"
                self.ai_wins += 1
            else:
                self.round_winner = "Draw"
        
        print(f"Round {self.current_round} Over! Winner: {self.round_winner}")
        print(f"Score - Player: {self.player_wins}, Evil Twin: {self.ai_wins}")
        
        # Check if match is over (first to 3 wins)
        if self.player_wins >= self.wins_needed:
            # Player wins - trigger dialogue instead of immediate match end
            self.showing_dialogue = True
            self.dialogue_phase = "threat"
            self.dialogue_timer = 0.0
            print(f"PLAYER VICTORY! Starting dialogue sequence...")
        elif self.ai_wins >= self.wins_needed:
            self.match_over = True
            self.match_winner = "Evil Twin"
            print(f"MATCH OVER! Evil Twin wins the match {self.ai_wins}-{self.player_wins}!")
    
    def _start_new_round(self):
        """Start a new round."""
        if self.match_over:
            return
            
        self.current_round += 1
        self.round_over = False
        self.round_winner = None
        self.round_time = 99.0
        
        # Reset character positions and health
        self.player1.x = 0
        self.player1.y = 335
        self.player1.health = self.player1.max_health
        self.player1.velocity_x = 0
        self.player1.velocity_y = 0
        self.player1.is_attacking = False
        self.player1.is_blocking = False
        self.player1.attack_cooldown = 0
        self.player1.on_ground = True
        self.player1.is_dead = False  # Reset death state
        
        self.player2.x = 600
        self.player2.y = 335
        self.player2.health = self.player2.max_health
        self.player2.velocity_x = 0
        self.player2.velocity_y = 0
        self.player2.is_attacking = False
        self.player2.is_blocking = False
        self.player2.attack_cooldown = 0
        self.player2.on_ground = True
        self.player2.is_dead = False  # Reset death state
        
        print(f"Round {self.current_round} begins!")
    
    def _load_background(self):
        """Load and scale the background image."""
        try:
            bg_path = sprite_path("background.png")
            original_bg = pygame.image.load(bg_path).convert()
            
            # Get original dimensions
            orig_width, orig_height = original_bg.get_size()
            print(f"Original background size: {orig_width}x{orig_height}")
            
            # Scale to fill the screen (800x600) - force exact dimensions
            self.background_image = pygame.transform.scale(original_bg, (800, 600))
            print(f"Scaled background to: 800x600")
            print(f"Loaded background image: {bg_path}")
        except Exception as e:
            print(f"Could not load background image: {e}")
            self.background_image = None
    
    def render(self, surface: pygame.Surface):
        """Render the fight scene."""
        # Background
        if self.background_image:
            # Render background image scaled to fill screen
            surface.blit(self.background_image, (0, 0))
        else:
            # Fallback to solid color
            surface.fill(self.bg_color)
        
        # Render characters
        self.player1.render(surface)
        self.player2.render(surface)
        
        # Render UI
        self._render_ui(surface)
        
        # Render dialogue box if showing
        if self.showing_dialogue:
            self._render_dialogue_box(surface)
        
        # Render pause screen if paused (pause takes priority over dialogue)
        if self.is_paused:
            self._render_pause_screen(surface)
    
    def _render_ui(self, surface: pygame.Surface):
        """Render the user interface with pixelated retro style."""
        # Timer (large, prominent)
        timer_text = self._render_pixel_text(f"{int(self.round_time):02d}", self.large_font, (255, 255, 255), 3)
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 40))
        surface.blit(timer_text, timer_rect)
        
        # Round counter (small, centered)
        round_text = self._render_pixel_text(f"ROUND {self.current_round}", self.small_font, (200, 200, 200), 2)
        round_rect = round_text.get_rect(center=(self.screen_width // 2, 70))
        surface.blit(round_text, round_rect)
        
        # Player wins counter (left side, blue)
        p1_text = self._render_pixel_text(f"PLAYER: {self.player_wins}", self.small_font, (100, 150, 255), 2)
        surface.blit(p1_text, (20, 20))
        
        # AI wins counter (right side, red)
        p2_text = self._render_pixel_text(f"EVIL TWIN: {self.ai_wins}", self.small_font, (255, 100, 100), 2)
        p2_rect = p2_text.get_rect(topright=(self.screen_width - 20, 20))
        surface.blit(p2_text, p2_rect)
        
        # Health bars
        self._render_health_bar(surface, 20, 90, self.player1.health, self.player1.max_health, (100, 100, 255))
        self._render_health_bar(surface, self.screen_width - 220, 90, self.player2.health, self.player2.max_health, (255, 100, 100))
        
        # Stamina bars (below health bars)
        self._render_stamina_bar(surface, 20, 120, self.player1.stamina, self.player1.max_stamina, (100, 255, 255), self.player1.is_stunned)
        self._render_stamina_bar(surface, self.screen_width - 220, 120, self.player2.stamina, self.player2.max_stamina, (255, 255, 100), self.player2.is_stunned)
        
        # Round result screen
        if self.round_over and not self.match_over:
            self._render_round_result(surface)
        
        # Match over screen
        if self.match_over:
            self._render_match_over(surface)
    
    def _render_health_bar(self, surface: pygame.Surface, x: int, y: int, health: int, max_health: int, color: tuple):
        """Render a pixelated retro health bar."""
        bar_width = 200
        bar_height = 16  # Reduced for more retro feel
        pixel_size = 4   # Size of each "pixel" block
        
        # Calculate health segments (each segment is pixel_size wide)
        total_segments = bar_width // pixel_size
        health_segments = int((health / max_health) * total_segments)
        
        # Draw pixelated background border (retro style)
        border_thickness = 2
        border_rect = pygame.Rect(x - border_thickness, y - border_thickness, 
                                bar_width + border_thickness * 2, bar_height + border_thickness * 2)
        pygame.draw.rect(surface, (255, 255, 255), border_rect)  # White border
        
        # Draw dark background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (32, 32, 32), bg_rect)  # Dark retro background
        
        # Draw pixelated health segments
        for i in range(health_segments):
            segment_x = x + (i * pixel_size)
            segment_rect = pygame.Rect(segment_x, y, pixel_size - 1, bar_height)  # -1 for pixel separation
            
            # Color gradient based on health percentage
            health_percentage = health / max_health
            if health_percentage > 0.6:
                # Green when healthy
                pixel_color = (50, 255, 50)
            elif health_percentage > 0.3:
                # Yellow when medium health
                pixel_color = (255, 255, 50)
            else:
                # Red when low health
                pixel_color = (255, 50, 50)
            
            pygame.draw.rect(surface, pixel_color, segment_rect)
    
    def _render_stamina_bar(self, surface: pygame.Surface, x: int, y: int, stamina: int, max_stamina: int, color: tuple, is_stunned: bool):
        """Render a pixelated retro stamina bar."""
        bar_width = 200
        bar_height = 12  # Smaller than health bar
        pixel_size = 4   # Size of each "pixel" block
        
        # Calculate stamina segments (each segment is pixel_size wide)
        total_segments = bar_width // pixel_size
        stamina_segments = int((stamina / max_stamina) * total_segments)
        
        # Draw pixelated background border (retro style)
        border_thickness = 1  # Thinner border for stamina
        border_color = (255, 255, 255) if not is_stunned else (255, 0, 0)  # Red border when stunned
        border_rect = pygame.Rect(x - border_thickness, y - border_thickness, 
                                bar_width + border_thickness * 2, bar_height + border_thickness * 2)
        pygame.draw.rect(surface, border_color, border_rect)
        
        # Draw dark background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        bg_color = (16, 16, 16) if not is_stunned else (64, 16, 16)  # Darker red background when stunned
        pygame.draw.rect(surface, bg_color, bg_rect)
        
        # Draw pixelated stamina segments (unless stunned)
        if not is_stunned:
            for i in range(stamina_segments):
                segment_x = x + (i * pixel_size)
                segment_rect = pygame.Rect(segment_x, y, pixel_size - 1, bar_height)  # -1 for pixel separation
                
                # Color gradient based on stamina percentage
                stamina_percentage = stamina / max_stamina
                if stamina_percentage > 0.6:
                    # Bright cyan when full stamina
                    pixel_color = color
                elif stamina_percentage > 0.3:
                    # Dim the color for medium stamina
                    pixel_color = (color[0] // 2, color[1] // 2, color[2])
                else:
                    # Very dim for low stamina
                    pixel_color = (color[0] // 4, color[1] // 4, color[2] // 2)
                
                pygame.draw.rect(surface, pixel_color, segment_rect)
        else:
            # Show "STUNNED" text when stamina is depleted
            stun_text = self._render_pixel_text("STUNNED", self.small_font, (255, 50, 50), 1)
            stun_rect = stun_text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
            surface.blit(stun_text, stun_rect)
    
    def _render_round_result(self, surface: pygame.Surface):
        """Render round result screen with pixelated retro style."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Round winner text (large pixelated)
        if self.round_winner:
            if self.round_winner == "Draw":
                winner_text = self._render_pixel_text("ROUND DRAW!", self.mega_font, (255, 255, 0), 3)
            else:
                winner_text = self._render_pixel_text(f"{self.round_winner.upper()} WINS!", self.mega_font, (255, 255, 255), 3)
            winner_rect = winner_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 60))
            surface.blit(winner_text, winner_rect)
        
        # Score display (medium pixelated)
        score_text = self._render_pixel_text(f"PLAYER {self.player_wins} - {self.ai_wins} EVIL TWIN", self.large_font, (200, 200, 200), 2)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        surface.blit(score_text, score_rect)
        
        # Next round timer (small pixelated)
        time_remaining = self.round_end_duration - self.round_end_timer
        if time_remaining > 0:
            timer_text = self._render_pixel_text(f"NEXT ROUND IN {int(time_remaining) + 1}...", self.font, (150, 150, 150), 2)
            timer_rect = timer_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
            surface.blit(timer_text, timer_rect)
    
    def _render_match_over(self, surface: pygame.Surface):
        """Render match over screen with pixelated retro style."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Match winner text (mega pixelated with gold color)
        if self.match_winner:
            winner_text = self._render_pixel_text(f"{self.match_winner.upper()} WINS!", self.mega_font, (255, 215, 0), 4)
            winner_rect = winner_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
            surface.blit(winner_text, winner_rect)
        
        # Final score (large pixelated)
        final_score = self._render_pixel_text(f"FINAL: {self.player_wins} - {self.ai_wins}", self.large_font, (255, 255, 255), 3)
        score_rect = final_score.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(final_score, score_rect)
        
        # Match type (medium pixelated)
        match_text = self._render_pixel_text("FIRST TO 3 WINS", self.font, (200, 200, 200), 2)
        match_rect = match_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
        surface.blit(match_text, match_rect)
        
        # Instructions (small pixelated)
        inst_text = self._render_pixel_text("PRESS ESC TO EXIT", self.small_font, (150, 150, 150), 2)
        inst_rect = inst_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 120))
        surface.blit(inst_text, inst_rect)
    
    def _render_pause_screen(self, surface: pygame.Surface):
        """Render pause screen with retro neon blinking effect."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Calculate blink effect (on/off cycle)
        blink_cycle = math.sin(self.pause_blink_timer * self.pause_blink_speed * math.pi)
        is_visible = blink_cycle > 0
        
        if is_visible:
            # Create neon-style "PAUSE" text with multiple glow layers
            pause_text = "PAUSE"
            
            # Multiple shadow/glow layers for neon effect
            glow_colors = [
                (255, 0, 255, 30),   # Magenta glow (outermost)
                (255, 50, 255, 60),  # Lighter magenta 
                (255, 100, 255, 90), # Even lighter
                (255, 150, 255, 120), # Almost white magenta
                (255, 255, 255, 255)  # Pure white center
            ]
            
            glow_offsets = [
                [(x, y) for x in range(-3, 4) for y in range(-3, 4)],  # Large glow
                [(x, y) for x in range(-2, 3) for y in range(-2, 3)],  # Medium glow
                [(x, y) for x in range(-1, 2) for y in range(-1, 2)],  # Small glow
                [(0, 0)],  # Inner glow
                [(0, 0)]   # Center text
            ]
            
            # Center position
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2
            
            # Render each glow layer
            for i, (color, offsets) in enumerate(zip(glow_colors, glow_offsets)):
                # Create the text surface
                text_surface = self._render_pixel_text(pause_text, self.mega_font, color[:3], 4)
                
                # Apply alpha if specified
                if len(color) == 4:
                    text_surface.set_alpha(color[3])
                
                # Render at each offset position for glow effect
                for offset_x, offset_y in offsets:
                    text_rect = text_surface.get_rect()
                    text_rect.centerx = center_x + offset_x
                    text_rect.centery = center_y + offset_y
                    surface.blit(text_surface, text_rect)
            
            # Instructions below pause text
            inst_text = self._render_pixel_text("PRESS ESC TO RESUME", self.font, (200, 200, 255), 2)
            inst_rect = inst_text.get_rect(center=(center_x, center_y + 80))
            surface.blit(inst_text, inst_rect)
    
    def _render_dialogue_box(self, surface: pygame.Surface):
        """Render retro dialogue box with Evil Twin's final words and player choices."""
        # Create dialogue box background
        box_width = 600
        box_height = 200
        box_x = (self.screen_width - box_width) // 2
        box_y = self.screen_height - box_height - 50
        
        # Dark background with retro border
        border_thickness = 4
        
        # Outer border (bright)
        outer_rect = pygame.Rect(box_x - border_thickness, box_y - border_thickness, 
                               box_width + border_thickness * 2, box_height + border_thickness * 2)
        pygame.draw.rect(surface, (255, 255, 255), outer_rect)
        
        # Inner border (dark)
        inner_border = pygame.Rect(box_x - border_thickness + 2, box_y - border_thickness + 2,
                                 box_width + (border_thickness - 2) * 2, box_height + (border_thickness - 2) * 2)
        pygame.draw.rect(surface, (100, 100, 100), inner_border)
        
        # Main background
        main_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, (20, 20, 40), main_rect)
        
        # Character portrait area (Evil Twin)
        portrait_size = 80
        portrait_x = box_x + 20
        portrait_y = box_y + 20
        portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_size, portrait_size)
        
        # Draw background for portrait
        pygame.draw.rect(surface, (20, 20, 40), portrait_rect)
        
        # Load and display Evil Twin portrait
        try:
            # Load the dedicated portrait image
            portrait_path = sprite_path("portrait.png")
            portrait_image = pygame.image.load(portrait_path).convert_alpha()
            
            # Scale portrait to fit the box (with some padding)
            portrait_inner_size = portrait_size - 6  # Leave 3px border on each side
            scaled_portrait = pygame.transform.scale(portrait_image, (portrait_inner_size, portrait_inner_size))
            
            # Center the portrait in the box
            portrait_x_pos = portrait_x + (portrait_size - portrait_inner_size) // 2
            portrait_y_pos = portrait_y + (portrait_size - portrait_inner_size) // 2
            surface.blit(scaled_portrait, (portrait_x_pos, portrait_y_pos))
            
        except Exception as e:
            # Fallback to colored rectangle with "?" if portrait loading fails
            print(f"Could not load Evil Twin portrait: {e}")
            pygame.draw.rect(surface, (80, 40, 40), portrait_rect)
            
            # Draw a simple "?" as placeholder
            question_text = self._render_pixel_text("?", self.large_font, (255, 200, 200), 3)
            question_rect = question_text.get_rect(center=(portrait_x + portrait_size//2, portrait_y + portrait_size//2))
            surface.blit(question_text, question_rect)
        
        # Portrait border
        pygame.draw.rect(surface, (200, 200, 200), portrait_rect, 2)
        
        # Evil Twin name
        name_text = self._render_pixel_text("EVIL TWIN", self.font, (255, 100, 100), 2)
        name_x = portrait_x + portrait_size + 20
        name_y = portrait_y
        surface.blit(name_text, (name_x, name_y))
        
        # Dialogue text area
        text_x = name_x
        text_y = name_y + 30
        text_width = box_width - (text_x - box_x) - 20
        
        if self.dialogue_phase == "threat":
            # Evil Twin's threat
            threat_text = "You will never get to her alive..."
            dialogue_surface = self._render_pixel_text(threat_text, self.font, (255, 255, 255), 2)
            surface.blit(dialogue_surface, (text_x, text_y))
            
        elif self.dialogue_phase == "choices":
            # Player choice prompt
            prompt_text = "What do you do?"
            prompt_surface = self._render_pixel_text(prompt_text, self.font, (255, 255, 255), 2)
            surface.blit(prompt_surface, (text_x, text_y))
            
            # Choice options
            choice_y = text_y + 40
            
            # Option 1: Spare
            spare_color = (255, 255, 100) if self.selected_choice == 0 else (200, 200, 200)
            spare_prefix = "> " if self.selected_choice == 0 else "  "
            spare_text = self._render_pixel_text(f"{spare_prefix}1. Spare him", self.font, spare_color, 2)
            surface.blit(spare_text, (text_x, choice_y))
            
            # Option 2: Finish
            finish_color = (255, 255, 100) if self.selected_choice == 1 else (200, 200, 200)
            finish_prefix = "> " if self.selected_choice == 1 else "  "
            finish_text = self._render_pixel_text(f"{finish_prefix}2. Finish him", self.font, finish_color, 2)
            surface.blit(finish_text, (text_x, choice_y + 25))
            
            # Instructions
            inst_text = self._render_pixel_text("Use 1/2 or UP/DOWN to choose, ENTER to confirm", self.small_font, (150, 150, 150), 1)
            surface.blit(inst_text, (text_x, choice_y + 60))
            
        elif self.dialogue_phase == "outcome":
            # Show outcome based on player choice
            if self.player_choice == "spare":
                outcome_text = "You show mercy... The Evil Twin retreats into the shadows."
                outcome_color = (100, 255, 100)  # Green
            else:
                outcome_text = "You finish what was started... The Evil Twin is no more."
                outcome_color = (255, 100, 100)  # Red
                
            outcome_surface = self._render_pixel_text(outcome_text, self.font, outcome_color, 2)
            surface.blit(outcome_surface, (text_x, text_y))
            
            # Continue instruction
            continue_text = self._render_pixel_text("Press SPACE to continue...", self.small_font, (150, 150, 150), 1)
            surface.blit(continue_text, (text_x, text_y + 40))


class Level2Scene:
    """Level 2 scene - fight against block enemy with same mechanics as Level 1."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize Level 2 fight scene."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Audio (will be set by the game engine)
        self.attack_sound = None
        self.block_sound = None
        self.pain_sound = None
        
        # Create characters
        self.player1 = Samurai1(0, 335)  # Human player (left side)
        self.player2 = YellowNinja(600, 335)  # Yellow Ninja enemy (right side)
        
        # Match state (first to 3 wins)
        self.player_wins = 0
        self.ai_wins = 0
        self.wins_needed = 3
        self.current_round = 1
        
        # Round state
        self.round_time = 99.0  # seconds
        self.round_over = False
        self.round_winner = None
        self.match_over = False
        self.match_winner = None
        
        # Round transition
        self.round_end_timer = 0.0
        self.round_end_duration = 2.5  # seconds to show death animation and round result
        
        # Pause state
        self.is_paused = False
        self.pause_blink_timer = 0.0
        self.pause_blink_speed = 2.0  # Blinks per second
        
        # Dialogue state (for post-match victory)
        self.showing_dialogue = False
        self.dialogue_phase = "victory"
        self.dialogue_timer = 0.0
        self.dialogue_complete = False
        
        # Intro state (for Level 2 intro)
        self.showing_intro = False  # No intro needed for Level 2
        
        # Background
        self.bg_color = (50, 80, 50)  # Dark green fallback
        self.background_image = None
        # Manual vertical spawn offsets (visual calibration)
        self.spawn_offset_player = 300  # move player down by 300px
        self.spawn_offset_enemy = 265   # move enemy down by 265px
        
        # Ground layer assets
        self.ground_image = None
        self.ground_top_y = 0.0  # will be set when ground.png loads
        
        # Arena boundaries (same as Level 1)
        self.arena_left = -100
        self.arena_right = 900
        
        # Initialize fonts and load background
        self._init_fonts()
        self._load_background()
        
    def _init_fonts(self):
        """Initialize fonts."""
        try:
            self.small_font = pygame.font.Font(None, 16)
            self.font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 32)
            self.mega_font = pygame.font.Font(None, 48)
        except:
            # Use default fonts if loading fails
            self.small_font = pygame.font.Font(None, 16)
            self.font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 32)
            self.mega_font = pygame.font.Font(None, 48)
        
    def _load_background(self):
        """Load the background image."""
        try:
            background_path = sprite_path("background.png")
            if os.path.exists(background_path):
                self.background_image = pygame.image.load(background_path)
                self.background_image = pygame.transform.scale(
                    self.background_image,
                    (self.screen_width, self.screen_height)
                )
                print(f"Loaded Level 2 background: {background_path}")
            # Load ground image (assets/sprites/ground.png)
            ground_path = sprite_path("ground.png")
            if os.path.exists(ground_path):
                ground_img = pygame.image.load(ground_path).convert_alpha()
                # Scale horizontally to screen width, keep original height
                g_height = ground_img.get_height()
                if ground_img.get_width() != self.screen_width:
                    ground_img = pygame.transform.scale(ground_img, (self.screen_width, g_height))
                self.ground_image = ground_img
                # Compute top Y coordinate of the ground (top edge of ground graphic)
                self.ground_top_y = float(self.screen_height - self.ground_image.get_height())
                # Place fighters using manual offsets so their bottoms sit lower on the screen
                # Player uses physics ground_y; enemy receives ground via update()
                new_p1_ground = (self.ground_top_y + self.spawn_offset_player) - self.player1.height
                self.player1.ground_y = new_p1_ground
                self.player1.y = new_p1_ground
                self.player1.on_ground = True
                # Initialize enemy y similarly (its update() will keep it on the provided ground)
                self.player2.y = (self.ground_top_y + self.spawn_offset_enemy) - self.player2.height
                self.player2.on_ground = True
                print(f"Loaded Level 2 ground: {ground_path} at y={self.ground_top_y}")
        except pygame.error:
            self.background_image = None
            
    def _render_pixel_text(self, text: str, font: pygame.font.Font, color: tuple, scale: int = 2):
        """Render text with pixelated, retro look by scaling up small text."""
        small_surface = font.render(text, False, color)
        original_size = small_surface.get_size()
        new_size = (original_size[0] * scale, original_size[1] * scale)
        scaled_surface = pygame.transform.scale(small_surface, new_size)
        return scaled_surface
        
    def set_sounds(self, attack_sound, block_sound, pain_sound):
        """Set sounds for characters."""
        self.attack_sound = attack_sound
        self.block_sound = block_sound
        self.pain_sound = pain_sound
        
        # Set sounds for characters
        self.player1.attack_sound = attack_sound
        self.player1.block_sound = block_sound
        self.player1.pain_sound = pain_sound
        
        self.player2.attack_sound = attack_sound
        self.player2.block_sound = block_sound
        self.player2.pain_sound = pain_sound
        
    def handle_input(self, keys_pressed: dict, events: list) -> str:
        """Handle input for Level 2."""
        # Handle dialogue first
        if self.showing_dialogue:
            return self._handle_dialogue_input(events)
        
        # Handle pause
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.match_over:
                        self.is_paused = not self.is_paused
                    else:
                        return "menu"
                        
                # Process cheat input for player 1
                if event.unicode.isalpha():
                    self.player1.process_cheat_input(event.unicode, self.round_time)
        
        return "continue"
    
    def _handle_dialogue_input(self, events: list) -> str:
        """Handle input during victory dialogue."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.dialogue_complete = True
                    return "level3"  # Progress to next level
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
        return "continue"
        
    def update(self, dt: float, player1_input=None, player2_input=None):
        """Update Level 2 scene."""
        # Handle dialogue
        if self.showing_dialogue:
            self.dialogue_timer += dt
            return
        
        # Handle pause
        if self.is_paused:
            self.pause_blink_timer += dt
            return
        
        # Handle match over state
        if self.match_over:
            return
        
        # Handle round end
        if self.round_over:
            self.round_end_timer += dt
            if self.round_end_timer >= self.round_end_duration:
                self._start_next_round()
            return
        
        # Update round timer
        self.round_time -= dt
        if self.round_time <= 0:
            self.round_time = 0
            self._end_round("timeout")
            return
        
        # Update characters
        if player1_input:
            self.player1.update(dt, player1_input)
        else:
            from game.input_handler import PlayerInput
            empty_input = PlayerInput()
            self.player1.update(dt, empty_input)
        
        # Update AI enemy using ground plane with manual offset applied
        if self.ground_image is not None:
            enemy_ground_y = (self.ground_top_y + self.spawn_offset_enemy) - self.player2.height
        else:
            # Fallback: keep original baseline (335) and apply enemy offset relative to feet baseline
            enemy_ground_y = 335 + self.spawn_offset_enemy
        self.player2.update(dt, 2000.0, enemy_ground_y, self.player1, self.arena_left, self.arena_right)
        
        # Collision detection
        self._check_collisions()
        
        # Check for round end conditions
        if self.player1.is_dead and not self.round_over:
            self._end_round("ai_wins")
        elif self.player2.is_dead and not self.round_over:
            self._end_round("player_wins")
    
    def _check_collisions(self):
        """Check for combat collisions between characters."""
        distance = abs(self.player1.x - self.player2.x)
        
        # Check player 1 attacking player 2
        if (self.player1.is_attacking and self.player1.can_hit and 
            distance < 60 and self._is_facing_target(self.player1, self.player2)):
            
            if self.player2.is_blocking:
                # Block
                self.player1.can_hit = False
                if self.block_sound:
                    self.block_sound.play()
                # Reduce blocker's stamina
                self.player2.stamina = max(0, self.player2.stamina - 50)
                if self.player2.stamina <= 0:
                    self.player2.start_stun()
            else:
                # Hit
                damage = 25 if not self.player1.god_mode else 100
                self._deal_damage(self.player2, damage)
                self.player1.can_hit = False
                if self.pain_sound:
                    self.pain_sound.play()
        
        # Check player 2 attacking player 1
        if (self.player2.is_attacking and self.player2.can_hit and 
            distance < 60 and self._is_facing_target(self.player2, self.player1)):
            
            if self.player1.is_blocking:
                # Block
                self.player2.can_hit = False
                if self.block_sound:
                    self.block_sound.play()
                # Reduce blocker's stamina
                self.player1.stamina = max(0, self.player1.stamina - 50)
                if self.player1.stamina <= 0:
                    self.player1.start_stun()
            else:
                # Hit
                damage = 25
                self._deal_damage(self.player1, damage)
                self.player2.can_hit = False
                if self.pain_sound:
                    self.pain_sound.play()
    
    def _is_facing_target(self, attacker, target) -> bool:
        """Check if attacker is facing the target."""
        if attacker.facing_right and target.x > attacker.x:
            return True
        elif not attacker.facing_right and target.x < attacker.x:
            return True
        return False
    
    def _deal_damage(self, target, damage: int):
        """Deal damage to a character."""
        target.health = max(0, target.health - damage)
        target.is_hit = True
        target.hit_duration = target.hit_animation_time
        
        if target.health <= 0:
            target.is_dead = True
    
    def _end_round(self, reason: str):
        """End the current round."""
        self.round_over = True
        self.round_end_timer = 0.0
        
        if reason == "player_wins":
            self.round_winner = "Player"
            self.player_wins += 1
        elif reason == "ai_wins":
            self.round_winner = "Yellow Ninja"
            self.ai_wins += 1
        else:  # timeout
            # Determine winner by health
            if self.player1.health > self.player2.health:
                self.round_winner = "Player"
                self.player_wins += 1
            elif self.player2.health > self.player1.health:
                self.round_winner = "Block Enemy"
                self.ai_wins += 1
            else:
                self.round_winner = "Draw"
        
        # Check for match end
        if self.player_wins >= self.wins_needed:
            self.match_over = True
            self.match_winner = "Player"
            # Show victory dialogue after a delay
            self.dialogue_timer = 0.0
            self.showing_dialogue = True
        elif self.ai_wins >= self.wins_needed:
            self.match_over = True
            self.match_winner = "Yellow Ninja"
    
    def _start_next_round(self):
        """Start the next round."""
        self.current_round += 1
        self.round_over = False
        self.round_winner = None
        self.round_time = 99.0
        
        # Reset character positions and health
        self.player1.x = 0
        if self.ground_image is not None:
            self.player1.ground_y = (self.ground_top_y + self.spawn_offset_player) - self.player1.height
            self.player1.y = self.player1.ground_y
        else:
            # Fallback to original baseline + offset (feet baseline)
            self.player1.ground_y = 335 + self.spawn_offset_player
            self.player1.y = self.player1.ground_y
        self.player1.health = self.player1.max_health
        self.player1.velocity_x = 0
        self.player1.velocity_y = 0
        self.player1.is_attacking = False
        self.player1.is_blocking = False
        self.player1.attack_cooldown = 0
        self.player1.on_ground = True
        self.player1.is_dead = False
        self.player1.is_hit = False
        self.player1.stamina = self.player1.max_stamina
        self.player1.is_stunned = False
        self.player1.stun_timer = 0.0
        
        self.player2.x = 600
        if self.ground_image is not None:
            self.player2.y = (self.ground_top_y + self.spawn_offset_enemy) - self.player2.height
        else:
            self.player2.y = 335 + self.spawn_offset_enemy
        self.player2.health = self.player2.max_health
        self.player2.velocity_x = 0
        self.player2.velocity_y = 0
        self.player2.is_attacking = False
        self.player2.is_blocking = False
        self.player2.attack_cooldown = 0
        self.player2.on_ground = True
        self.player2.is_dead = False
        self.player2.is_hit = False
        self.player2.stamina = self.player2.max_stamina
        self.player2.is_stunned = False
        self.player2.stun_timer = 0.0
        
    def render(self, screen: pygame.Surface):
        """Render Level 2 scene."""
        # Draw background
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.bg_color)
        
        # Draw ground layer
        if self.ground_image:
            screen.blit(self.ground_image, (0, int(self.screen_height - self.ground_image.get_height())))
        
        # Handle dialogue rendering
        if self.showing_dialogue:
            self._render_victory_dialogue(screen)
            return
        
        # Render characters
        self.player1.render(screen)
        self.player2.render(screen)
        
        # Draw UI - identical to Level 1
        self._render_health_bar(screen, 20, 90, self.player1.health, self.player1.max_health, (100, 100, 255))
        self._render_health_bar(screen, self.screen_width - 220, 90, self.player2.health, self.player2.max_health, (255, 100, 100))
        
        # Draw stamina bars
        self._render_stamina_bar(screen, 20, 120, self.player1.stamina, self.player1.max_stamina, (100, 255, 255), self.player1.is_stunned)
        self._render_stamina_bar(screen, self.screen_width - 220, 120, self.player2.stamina, self.player2.max_stamina, (255, 255, 100), self.player2.is_stunned)
        
        # Draw round info
        self._render_round_info(screen)
        
        # Draw pause overlay
        if self.is_paused:
            self._render_pause_overlay(screen)
        
        # Draw round end overlay
        if self.round_over and not self.match_over:
            self._render_round_end_overlay(screen)
        elif self.match_over and not self.showing_dialogue:
            self._render_match_end_overlay(screen)
    
    def _render_victory_dialogue(self, screen: pygame.Surface):
        """Render victory dialogue for Level 2."""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Victory message
        victory_text = self._render_pixel_text("LEVEL 2 COMPLETE!", self.large_font, (255, 255, 0), 3)
        victory_rect = victory_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(victory_text, victory_rect)
        
        # Subtitle
        subtitle_text = self._render_pixel_text("You defeated the Yellow Ninja!", self.font, (255, 255, 255), 2)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 280))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Continue prompt
        continue_text = self._render_pixel_text("Press SPACE to continue", self.font, (200, 200, 200), 2)
        continue_rect = continue_text.get_rect(center=(self.screen_width // 2, 400))
        screen.blit(continue_text, continue_rect)
    
    def _render_round_info(self, surface: pygame.Surface):
        """Render round and score information."""
        # Round number
        round_text = self._render_pixel_text(f"ROUND {self.current_round}", self.font, (255, 255, 255), 2)
        round_rect = round_text.get_rect(center=(self.screen_width // 2, 30))
        surface.blit(round_text, round_rect)
        
        # Timer
        timer_text = self._render_pixel_text(f"{int(self.round_time)}", self.large_font, (255, 255, 0), 2)
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 60))
        surface.blit(timer_text, timer_rect)
        
        # Show god mode indicator
        if self.player1.god_mode:
            god_text = self._render_pixel_text("KOJIMA MODE: ON", self.font, (255, 255, 0), 2)
            surface.blit(god_text, (self.screen_width - 250, 10))
    
    def _render_pause_overlay(self, surface: pygame.Surface):
        """Render pause overlay."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Blinking PAUSE text
        if int(self.pause_blink_timer * self.pause_blink_speed) % 2:
            pause_text = self._render_pixel_text("PAUSED", self.large_font, (255, 255, 255), 3)
            pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(pause_text, pause_rect)
    
    def _render_round_end_overlay(self, surface: pygame.Surface):
        """Render round end overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Round result
        if self.round_winner:
            if self.round_winner == "Draw":
                result_text = self._render_pixel_text("DRAW!", self.large_font, (255, 255, 0), 3)
            else:
                result_text = self._render_pixel_text(f"{self.round_winner.upper()} WINS ROUND!", self.large_font, (255, 255, 0), 3)
            result_rect = result_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(result_text, result_rect)
    
    def _render_match_end_overlay(self, surface: pygame.Surface):
        """Render match end overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Match result
        if self.match_winner:
            if self.match_winner == "Player":
                result_text = self._render_pixel_text("VICTORY!", self.large_font, (0, 255, 0), 3)
            else:
                result_text = self._render_pixel_text("DEFEAT!", self.large_font, (255, 0, 0), 3)
            result_rect = result_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            surface.blit(result_text, result_rect)
    
    def _render_health_bar(self, surface: pygame.Surface, x: int, y: int, health: int, max_health: int, color: tuple):
        """Render a pixelated retro health bar."""
        bar_width = 200
        bar_height = 16  # Reduced for more retro feel
        pixel_size = 4   # Size of each "pixel" block
        
        # Calculate health segments (each segment is pixel_size wide)
        total_segments = bar_width // pixel_size
        health_segments = int((health / max_health) * total_segments)
        
        # Draw pixelated background border (retro style)
        border_thickness = 2
        border_rect = pygame.Rect(x - border_thickness, y - border_thickness, 
                                bar_width + border_thickness * 2, bar_height + border_thickness * 2)
        pygame.draw.rect(surface, (255, 255, 255), border_rect)  # White border
        
        # Draw dark background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (32, 32, 32), bg_rect)  # Dark retro background
        
        # Draw pixelated health segments
        for i in range(health_segments):
            segment_x = x + (i * pixel_size)
            segment_rect = pygame.Rect(segment_x, y, pixel_size - 1, bar_height)  # -1 for pixel separation
            
            # Color gradient based on health percentage
            health_percentage = health / max_health
            if health_percentage > 0.6:
                # Green when healthy
                pixel_color = (50, 255, 50)
            elif health_percentage > 0.3:
                # Yellow when medium health
                pixel_color = (255, 255, 50)
            else:
                # Red when low health
                pixel_color = (255, 50, 50)
            
            pygame.draw.rect(surface, pixel_color, segment_rect)
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Health text
        health_text = self._render_pixel_text(f"HEALTH: {health}/{max_health}", self.small_font, (255, 255, 255), 1)
        surface.blit(health_text, (x + bar_width + 10, y + 2))
    
    def _render_stamina_bar(self, surface: pygame.Surface, x: int, y: int, stamina: int, max_stamina: int, color: tuple, is_stunned: bool):
        """Render a pixelated retro stamina bar."""
        bar_width = 200
        bar_height = 12  # Smaller than health bar
        pixel_size = 4   # Size of each "pixel" block
        
        # Check if player is stunned (stamina is 0)
        is_stunned = stamina <= 0
        
        # Calculate stamina segments (each segment is pixel_size wide)
        total_segments = bar_width // pixel_size
        stamina_segments = int((stamina / max_stamina) * total_segments)
        
        # Draw pixelated background border (retro style)
        border_thickness = 1  # Thinner border for stamina
        border_color = (255, 255, 255) if not is_stunned else (255, 0, 0)  # Red border when stunned
        border_rect = pygame.Rect(x - border_thickness, y - border_thickness, 
                                bar_width + border_thickness * 2, bar_height + border_thickness * 2)
        pygame.draw.rect(surface, border_color, border_rect)
        
        # Draw dark background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        bg_color = (16, 16, 16) if not is_stunned else (64, 16, 16)  # Darker red background when stunned
        pygame.draw.rect(surface, bg_color, bg_rect)
        
        # Draw pixelated stamina segments (unless stunned)
        if not is_stunned:
            for i in range(stamina_segments):
                segment_x = x + (i * pixel_size)
                segment_rect = pygame.Rect(segment_x, y, pixel_size - 1, bar_height)  # -1 for pixel separation
                
                # Color gradient based on stamina percentage
                stamina_percentage = stamina / max_stamina
                if stamina_percentage > 0.6:
                    # Bright cyan when full stamina
                    pixel_color = (100, 255, 255)
                elif stamina_percentage > 0.3:
                    # Dim the color for medium stamina
                    pixel_color = (50, 127, 255)
                else:
                    # Very dim for low stamina
                    pixel_color = (25, 63, 127)
                
                pygame.draw.rect(surface, pixel_color, segment_rect)
        else:
            # Show red flash effect when stunned
            if int(pygame.time.get_ticks() / 200) % 2:  # Flash every 200ms
                flash_rect = pygame.Rect(x, y, bar_width, bar_height)
                pygame.draw.rect(surface, (128, 0, 0), flash_rect)