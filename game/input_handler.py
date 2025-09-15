"""
Input management for the fighting game.
Manages keyboard input for player 1 and AI logic for player 2.
"""

import pygame
import random
import math
from typing import Dict, Any


class PlayerInput:
    """Represents the current input state for a player."""
    
    def __init__(self):
        print("DEBUG: PlayerInput.__init__ called")
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.attack = False
        self.block = False
        self.special = False
        self.is_parrying = False  # True during parry window (quick tap)
        self.parry_window_time = 0.0  # Time remaining in parry window
        print(f"DEBUG: PlayerInput.__init__ finished, has is_parrying: {hasattr(self, 'is_parrying')}")
    
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.attack = False
        self.block = False
        self.special = False


class AIController:
    """AI controller for the second player."""
    
    def __init__(self):
        """Initialize AI controller."""
        self.input = PlayerInput()
        self.reaction_time = 0.3  # seconds
        self.aggression = 0.7  # 0.0 = defensive, 1.0 = aggressive
        self.last_decision_time = 0.0
        self.decision_interval = 0.2  # seconds between decisions
        self.current_action = "idle"
        self.action_timer = 0.0
        
        # AI state tracking
        self.last_player_distance = 0.0
        self.attack_cooldown = 0.0
        self.block_duration = 0.0
        self.special_attack_cooldown = 0.0
        
    def update(self, dt: float, ai_character, player_character):
        """Update AI logic and generate input."""
        # Reset input state
        self._reset_input()
        
        # Update timers
        self.last_decision_time += dt
        self.action_timer += dt
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.block_duration = max(0, self.block_duration - dt)
        self.special_attack_cooldown = max(0, self.special_attack_cooldown - dt)
        
        # Calculate distance to player
        distance = abs(ai_character.x - player_character.x)
        
        # Make decisions at intervals
        if self.last_decision_time >= self.decision_interval:
            self._make_decision(ai_character, player_character, distance)
            self.last_decision_time = 0.0
        
        # Execute current action
        self._execute_action(ai_character, player_character, distance)
        
        return self.input
    
    def _reset_input(self):
        """Reset all input states."""
        self.input.left = False
        self.input.right = False
        self.input.up = False
        self.input.down = False
        self.input.attack = False
        self.input.block = False
        self.input.special = False
    
    def _make_decision(self, ai_character, player_character, distance):
        """Make AI decision based on game state."""
        # Don't make decisions if stunned - AI should wait it out
        if ai_character.is_stunned:
            self.current_action = "stunned"
            return
            
        # Check if player is attacking
        player_attacking = player_character.is_attacking
        
        # Check AI's stamina status for blocking decisions
        can_block = ai_character.stamina > ai_character.stamina_per_block  # Only block if we have enough stamina for at least one block
        
        # Special attack opportunity - use when player is vulnerable or at medium range
        if (self.special_attack_cooldown <= 0 and not ai_character.is_stunned and
            ((distance < 100 and player_character.is_attacking) or  # Counter-attack with special
             (distance < 120 and not player_character.is_blocking and random.random() < 0.3) or  # Surprise special attack
             (player_character.health < 30 and distance < 150 and random.random() < 0.5))):  # Finishing move
            self.current_action = "special_attack"
            self.action_timer = 0.0
            self.special_attack_cooldown = 10.0  # Set cooldown to match character cooldown
            return
        
        # Distance-based decisions
        if distance < 60:  # Close range
            # Only block if we have stamina and aren't already low
            if player_attacking and can_block and random.random() < 0.8:
                # Be more conservative with blocking if stamina is low
                block_chance = 0.8 if ai_character.stamina > 60 else 0.4
                if random.random() < block_chance:
                    self.current_action = "block"
                    self.action_timer = 0.0
                    self.block_duration = 0.3  # Shorter block duration to conserve stamina
                else:
                    # If can't or won't block, try to retreat or attack
                    if self.attack_cooldown <= 0 and random.random() < 0.5:
                        self.current_action = "attack"
                        self.action_timer = 0.0
                        self.attack_cooldown = 1.0
                    else:
                        self.current_action = "retreat"
                        self.action_timer = 0.0
            elif self.attack_cooldown <= 0 and random.random() < self.aggression:
                self.current_action = "attack"
                self.action_timer = 0.0
                self.attack_cooldown = 1.0
            elif random.random() < 0.3:
                self.current_action = "retreat"
                self.action_timer = 0.0
        elif distance < 150:  # Medium range
            if random.random() < self.aggression * 0.8:
                self.current_action = "approach"
                self.action_timer = 0.0
            elif random.random() < 0.2 and ai_character.stamina >= ai_character.jump_stamina_cost:
                # Only jump attack if we have enough stamina
                self.current_action = "jump_attack"
                self.action_timer = 0.0
        else:  # Long range
            self.current_action = "approach"
            self.action_timer = 0.0
    
    def _execute_action(self, ai_character, player_character, distance):
        """Execute the current AI action."""
        if self.current_action == "approach":
            # Move towards player
            if ai_character.x > player_character.x:
                self.input.left = True
            else:
                self.input.right = True
                
        elif self.current_action == "retreat":
            # Move away from player
            if ai_character.x > player_character.x:
                self.input.right = True
            else:
                self.input.left = True
                
        elif self.current_action == "attack":
            self.input.attack = True
            
        elif self.current_action == "special_attack":
            self.input.special = True
            
        elif self.current_action == "block":
            if self.block_duration > 0:
                self.input.block = True
            else:
                self.current_action = "idle"
                
        elif self.current_action == "stunned":
            # Do nothing - AI is stunned and cannot act
            # Character system will handle the stun duration
            pass
                
        elif self.current_action == "jump_attack":
            if self.action_timer < 0.2:
                self.input.up = True
            elif self.action_timer < 0.5:
                # Move towards player while jumping
                if ai_character.x > player_character.x:
                    self.input.left = True
                else:
                    self.input.right = True
                self.input.attack = True
            else:
                self.current_action = "idle"
        
        # Add some randomness to movement
        if random.random() < 0.1:  # 10% chance
            if random.random() < 0.5:
                self.input.left = not self.input.left
            else:
                self.input.right = not self.input.right


class InputHandler:
    """Handles input for player 1 and AI for player 2."""
    
    def __init__(self):
        """Initialize input handler with key mappings and AI."""
        # Player 1 controls (WASD + Space/Shift)
        self.player1_keys = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'up': pygame.K_w,
            'down': pygame.K_s,
            'attack': pygame.K_SPACE,
            'block': pygame.K_LSHIFT,
            'special': pygame.K_q
        }
        
        # Input states
        self.player1_input = PlayerInput()
        
        # Ensure parry attributes exist (defensive programming against import cache issues)
        if not hasattr(self.player1_input, 'is_parrying'):
            self.player1_input.is_parrying = False
        if not hasattr(self.player1_input, 'parry_window_time'):
            self.player1_input.parry_window_time = 0.0
            
        print(f"DEBUG: Created PlayerInput with attributes: {dir(self.player1_input)}")
        print(f"DEBUG: is_parrying attribute exists: {hasattr(self.player1_input, 'is_parrying')}")
        
        # AI controller for player 2
        self.ai_controller = AIController()
        
        # Key states for event handling
        self.keys_pressed = set()
        
        # Parry timing tracking
        self.shift_press_time = 0.0  # How long SHIFT has been held
        self.shift_was_pressed = False  # Previous frame SHIFT state
        self.parry_window_duration = 0.3  # 0.3 second parry window
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
    
    def update(self, dt: float = 0.0, ai_character=None, player_character=None):
        """Update input states based on currently pressed keys and AI logic."""
        # Get current key states
        keys = pygame.key.get_pressed()
        
        # Handle SHIFT key timing for parry vs block detection
        shift_currently_pressed = keys[self.player1_keys['block']]
        
        if shift_currently_pressed:
            if not self.shift_was_pressed:
                # SHIFT just pressed - start timing
                self.shift_press_time = 0.0
            else:
                # SHIFT still held - accumulate time
                self.shift_press_time += dt
        else:
            if self.shift_was_pressed:
                # SHIFT just released - check if it was a quick tap (parry)
                if self.shift_press_time <= self.parry_window_duration:
                    # Quick tap detected - trigger parry window
                    self.player1_input.is_parrying = True
                    self.player1_input.parry_window_time = self.parry_window_duration
            self.shift_press_time = 0.0
        
        # Update parry window countdown
        if self.player1_input.is_parrying:
            self.player1_input.parry_window_time -= dt
            if self.player1_input.parry_window_time <= 0.0:
                self.player1_input.is_parrying = False
                self.player1_input.parry_window_time = 0.0
        
        # Update Player 1 input
        self.player1_input.left = keys[self.player1_keys['left']]
        self.player1_input.right = keys[self.player1_keys['right']]
        self.player1_input.up = keys[self.player1_keys['up']]
        self.player1_input.down = keys[self.player1_keys['down']]
        self.player1_input.attack = keys[self.player1_keys['attack']]
        
        # Block state: True if SHIFT held AND not in parry window
        self.player1_input.block = shift_currently_pressed and not self.player1_input.is_parrying
        
        self.player1_input.special = keys[self.player1_keys['special']]
        
        # Store previous frame state
        self.shift_was_pressed = shift_currently_pressed
    
    def get_player1_input(self) -> PlayerInput:
        """Get Player 1 input state."""
        return self.player1_input
    
    def get_player2_input(self, dt: float, ai_character, player_character) -> PlayerInput:
        """Get AI input for Player 2."""
        return self.ai_controller.update(dt, ai_character, player_character)