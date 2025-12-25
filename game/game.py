#!/usr/bin/env python3
"""
Anachron - Main Game Module

A time-travel survival game where you carry three modern items through
random historical eras, building toward happiness until you choose to stay.

Architecture:
- config.py: All tunable parameters
- time_machine.py: Window mechanics, device state
- fulfillment.py: Hidden anchor tracking (Belonging, Legacy, Freedom)
- items.py: Modern item inventory
- game_state.py: Central state coordination
- prompts.py: AI narrative integration
- eras.py: Historical era definitions
- game.py: Main game loop and UI (this file)
"""

import random
import time
import os
import re
import textwrap
import threading
import sys
import logging
from typing import List
from datetime import datetime
from pathlib import Path

# Set up logging to file for debugging disconnection issues
logging.basicConfig(
    filename='/tmp/anachron_game.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Note: anthropic package not installed. Running in demo mode.")

# Local imports
from config import TEXT_SPEED, SHOW_DEVICE_STATUS, MODES, EUROPEAN_ERA_IDS
from game_state import GameState, GameMode, GamePhase, RegionPreference
from time_machine import TimeMachine, select_random_era, IndicatorState
from fulfillment import parse_anchor_adjustments, strip_anchor_tags
from items import Inventory, parse_item_usage
from eras import ERAS
from prompts import (
    get_system_prompt, get_arrival_prompt, get_turn_prompt,
    get_window_prompt, get_staying_ending_prompt, get_leaving_prompt
)
from scoring import Score, Leaderboard, calculate_score, GameHistory


# =============================================================================
# TERMINAL UI HELPERS
# =============================================================================

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


class Spinner:
    """Loading spinner"""
    
    def __init__(self, message="Thinking"):
        self.message = message
        self.spinning = False
        self.thread = None
        self.frames = ['—', '\\', '|', '/']
        
    def _spin(self):
        idx = 0
        while self.spinning:
            frame = self.frames[idx % len(self.frames)]
            print(f"\r{Colors.DIM}{self.message}... {frame}{Colors.END}", end='', flush=True)
            idx += 1
            time.sleep(0.1)
        print(f"\r{' ' * (len(self.message) + 10)}\r", end='', flush=True)
        
    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        
    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_box(lines, color=Colors.CYAN, width=70):
    """Print text in a box"""
    content_width = width - 2
    print(f"{color}╔{'═' * width}╗{Colors.END}")
    for line in lines:
        for subline in str(line).split('\n'):
            if len(subline.strip()) == 0:
                print(f"{color}║{Colors.END} {' ' * content_width} {color}║{Colors.END}")
            else:
                wrapped = textwrap.wrap(subline, width=content_width) or ['']
                for wrapped_line in wrapped:
                    padded = wrapped_line.ljust(content_width)
                    print(f"{color}║{Colors.END} {padded} {color}║{Colors.END}")
    print(f"{color}╚{'═' * width}╝{Colors.END}")


def print_header(text, color=Colors.HEADER):
    """Print a section header"""
    print(f"\n{color}{Colors.BOLD}{'═' * 70}")
    print(f"  {text}")
    print(f"{'═' * 70}{Colors.END}\n")


def slow_print(text, delay=TEXT_SPEED):
    """Typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def get_input(prompt, valid_options=None):
    """Get validated input"""
    logger.debug(f"get_input called with prompt='{prompt}', valid_options={valid_options}")
    while True:
        try:
            response = input(f"{Colors.YELLOW}{prompt}{Colors.END} ").strip().upper()
            logger.debug(f"get_input received response='{response}'")
            if valid_options is None or response in valid_options:
                return response
            print(f"{Colors.RED}Please enter one of: {', '.join(valid_options)}{Colors.END}")
        except EOFError as e:
            logger.error(f"EOFError in get_input: {e}")
            raise
        except KeyboardInterrupt as e:
            logger.error(f"KeyboardInterrupt in get_input: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected exception in get_input: {type(e).__name__}: {e}")
            raise


def roll_dice(sides=20, show=True):
    """Roll a die with optional animation"""
    if show:
        print(f"{Colors.DIM}Rolling...{Colors.END}", end=' ')
        for _ in range(5):
            print(f"{random.randint(1, sides)}", end=' ', flush=True)
            time.sleep(0.1)
        print()
    return random.randint(1, sides)


# =============================================================================
# AI INTEGRATION
# =============================================================================

class NarrativeEngine:
    """Handles AI-generated narrative"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.messages = []
        self.system_prompt = ""
        
        if ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic()
        else:
            self.client = None
    
    def set_era(self, era: dict):
        """Set up system prompt for current era"""
        self.system_prompt = get_system_prompt(self.game_state, era)
        self.messages = []  # Fresh conversation for new era
    
    def generate(self, user_prompt: str, stream: bool = True) -> str:
        """Generate narrative response"""
        self.messages.append({"role": "user", "content": user_prompt})
        
        if not self.client:
            response = self._demo_response(user_prompt)
            if stream:
                for char in response:
                    print(char, end='', flush=True)
                    time.sleep(0.008)
                print()
        else:
            response = self._api_call(stream)
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def _api_call(self, stream: bool) -> str:
        """Make API call with streaming"""
        spinner = Spinner("Generating")
        spinner.start()
        
        response = ""
        first_token = True
        buffer = ""  # Buffer to detect and hide anchor tags
        in_anchor_tag = False
        
        try:
            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=self.system_prompt,
                messages=self.messages
            ) as api_stream:
                for text in api_stream.text_stream:
                    if first_token:
                        spinner.stop()
                        first_token = False
                    response += text
                    
                    if stream:
                        buffer += text
                        
                        # Check for anchor tag start
                        if '<anchors>' in buffer:
                            # Print everything before the tag
                            before_tag = buffer.split('<anchors>')[0]
                            print(before_tag, end='', flush=True)
                            buffer = '<anchors>' + buffer.split('<anchors>', 1)[1]
                            in_anchor_tag = True
                        
                        # Check for anchor tag end
                        if in_anchor_tag and '</anchors>' in buffer:
                            # Discard the tag, keep anything after
                            after_tag = buffer.split('</anchors>', 1)[1] if '</anchors>' in buffer else ''
                            buffer = after_tag
                            in_anchor_tag = False
                        
                        # If not in tag and no partial tag detected, print buffer
                        if not in_anchor_tag and '<' not in buffer:
                            print(buffer, end='', flush=True)
                            buffer = ""
                        elif not in_anchor_tag and '<' in buffer and '>' in buffer:
                            # Complete non-anchor tag, just print it
                            if '<anchors>' not in buffer:
                                print(buffer, end='', flush=True)
                                buffer = ""
            
            # Print any remaining buffer (excluding anchor content)
            if stream and buffer and not in_anchor_tag:
                clean_buffer = re.sub(r'<anchors>.*?</anchors>', '', buffer, flags=re.DOTALL)
                print(clean_buffer, end='', flush=True)
            
            if stream:
                print()
            if first_token:
                spinner.stop()
                
        except Exception as e:
            spinner.stop()
            print(f"{Colors.RED}AI Error: {e}{Colors.END}")
            response = self._demo_response("")
            
        return response
    
    def _demo_response(self, prompt: str) -> str:
        """Demo response when API unavailable"""
        if "arrival" in prompt.lower() or len(self.messages) <= 2:
            return """You stumble forward, catching yourself against rough stone. The air hits you first—woodsmoke, animal dung, something cooking. Your ears ring from the transition.

When your vision clears, you see a narrow street of packed earth. Wooden buildings lean against each other, their upper floors jutting out. People in rough wool and leather stop to stare at your strange clothing.

A woman carrying a basket of bread crosses herself and hurries past. A dog barks. Somewhere nearby, a hammer rings against metal.

You are Thomas the Stranger now—that's what they'll call you. Your device hangs cool against your chest, dormant. Your three items are hidden beneath your coat. You need shelter before dark, and you need to figure out when and where you are.

A tavern sign creaks in the wind ahead. To your left, a church bell tower rises above the rooftops. To your right, a blacksmith's forge glows orange through an open door.

[A] Head to the tavern - travelers gather there, and you need information
[B] Make for the church - sanctuary and perhaps a sympathetic ear
[C] Approach the blacksmith - honest work might earn trust faster than questions

<anchors>belonging[0] legacy[0] freedom[0]</anchors>"""
        else:
            return """Your choice sets events in motion. The day unfolds with unexpected consequences.

People are beginning to know your face now. Some nod in recognition. Others still eye you with suspicion. This place is becoming familiar, for better or worse.

[A] Press forward with your current path
[B] Seek out someone you've met before
[C] Take time to observe and plan

<anchors>belonging[+3] legacy[+1] freedom[+2]</anchors>"""


# =============================================================================
# MAIN GAME CLASS
# =============================================================================

class Game:
    """Main game controller"""
    
    def __init__(self):
        self.state = GameState()
        self.narrator = None
        self.current_era = None
        self._selected_region = RegionPreference.WORLDWIDE  # Default
        
        # History tracking
        self.history = GameHistory()
        self.current_game = None
    
    def run(self):
        """Main game loop"""
        clear_screen()
        self._show_title()
        
        # Setup
        self._get_player_info()
        self._select_region()
        self._select_mode()
        self._show_items()
        
        # Start first era
        self._enter_random_era()
        
        # Main loop
        while self.state.phase != GamePhase.ENDED:
            self._play_turn()
    
    def _show_title(self):
        """Display title screen"""
        input(f"{Colors.DIM}Press Enter to begin...{Colors.END}")
    
    def _get_player_info(self):
        """Get player name"""
        clear_screen()
        print_header("WHO ARE YOU?")
        name = input(f"{Colors.YELLOW}Enter your name: {Colors.END}").strip()
        self.state.player_name = name if name else "Traveler"
    
    def _select_region(self):
        """Select historical region focus"""
        clear_screen()
        print_header("WHERE IN HISTORY?")
        
        print(f"  {Colors.CYAN}[1]{Colors.END} European Focus")
        print(f"      Ancient Greece, Vikings, Medieval Europe, Colonial America,")
        print(f"      Industrial Britain, World Wars")
        print()
        print(f"  {Colors.CYAN}[2]{Colors.END} World Explorer")
        print(f"      All eras: Egypt, China, Aztec Empire, Mughal India,")
        print(f"      plus European eras")
        print()
        
        choice = get_input("Your choice:", ['1', '2'])
        self._selected_region = RegionPreference.EUROPEAN if choice == '1' else RegionPreference.WORLDWIDE
    
    def _select_mode(self):
        """Set game mode (currently defaulting to mature)"""
        # Default to mature mode for all players
        mode = GameMode.MATURE
        
        self.state.start_game(self.state.player_name, mode, self._selected_region)
        self.narrator = NarrativeEngine(self.state)
        
        # Start history record
        self.current_game = self.history.start_new_game(self.state.player_name)
    
    def _show_items(self):
        """Show starting items and backstory"""
        clear_screen()
        print_header("READY OR NOT, YOUR JOURNEY BEGINS")
        
        slow_print("Twenty-four. Stanford. Six figures. A life that looks perfect")
        slow_print("and feels like nothing.")
        time.sleep(0.5)
        slow_print("\nSo when the lab needed a volunteer for the time machine's first")
        slow_print("human trial, you stepped up without thinking.")
        slow_print("Thirty seconds into the past. What could go wrong?")
        time.sleep(0.5)
        slow_print("\nEverything, it turns out.")
        time.sleep(0.3)
        slow_print("\nThe machine is broken. You can't go home.")
        slow_print("All you have is what was in your pockets:")
        print()
        
        for item in self.state.inventory.modern_items:
            print(f"  {Colors.GREEN}• {item.name}{Colors.END}")
            print(f"    {Colors.DIM}{item.description}{Colors.END}")
            print()
        
        input(f"\n{Colors.DIM}Press Enter to learn about the device...{Colors.END}")
        
        # Explain time machine mechanics
        self._explain_device()
    
    def _explain_device(self):
        """Explain how the time machine works"""
        clear_screen()
        print_header("THE DEVICE")
        
        slow_print("The time machine is small—about the size of a chunky wristwatch.")
        slow_print("You wear it on your wrist, hidden under your sleeve.")
        time.sleep(0.5)
        
        print(f"\n{Colors.CYAN}HOW IT WORKS:{Colors.END}\n")
        print(f"  {Colors.YELLOW}•{Colors.END} The window won't open immediately when you arrive somewhere new")
        print(f"  {Colors.YELLOW}•{Colors.END} You'll have time to settle in first—typically most of a year")
        print(f"  {Colors.YELLOW}•{Colors.END} When the window opens, you have a short time to decide")
        print(f"  {Colors.YELLOW}•{Colors.END} Choose to activate it, or let the window close and stay")
        print()
        
        print(f"{Colors.CYAN}THE CATCH:{Colors.END}\n")
        print(f"  {Colors.YELLOW}•{Colors.END} You can't choose where or when you go—it's random")
        print(f"  {Colors.YELLOW}•{Colors.END} Your three items always come with you")
        print(f"  {Colors.YELLOW}•{Colors.END} Your relationships do NOT come with you")
        print(f"  {Colors.YELLOW}•{Colors.END} Each jump means starting over")
        print()
        
        print(f"{Colors.CYAN}THE GOAL:{Colors.END}\n")
        slow_print("  Find a time and place where you want to stay.")
        slow_print("  Build something worth staying for—people, purpose, freedom.")
        slow_print("  When the window opens and you choose not to leave...")
        slow_print("  that's when you've found happiness.")
        
        input(f"\n{Colors.DIM}Press Enter to see where you've landed...{Colors.END}")
    
    def _enter_random_era(self):
        """Enter a random era"""
        visited_ids = self.state.time_machine.eras_visited
        
        # Filter eras based on region preference
        if self.state.region_preference == RegionPreference.EUROPEAN:
            available_eras = [e for e in ERAS if e['id'] in EUROPEAN_ERA_IDS]
        else:
            available_eras = ERAS  # Worldwide = all eras
        
        self.current_era = select_random_era(available_eras, visited_ids)
        
        self.state.enter_era(self.current_era)
        
        # Update time machine display with current era info
        self.state.time_machine.update_display(
            year=self.current_era['year'],
            location=self.current_era['location'],
            era_name=self.current_era['name']
        )
        
        # Reset inventory for new era (clears revealed status)
        self.state.inventory.reset_for_new_era()
        
        self.narrator.set_era(self.current_era)
        
        # Record era in history
        if self.current_game:
            self.history.start_era(
                self.current_game,
                self.current_era['name'],
                self.current_era['year'],
                self.current_era['location']
            )
        
        # Show era arrival
        clear_screen()
        print_header(f"ARRIVAL: {self.current_era['name']}")
        
        # Show device display
        display_text = self.state.time_machine.display.get_display_text()
        print(f"{Colors.DIM}Device display: {display_text}{Colors.END}\n")
        
        # Show era summary (5 key themes)
        self._show_era_summary()
        
        # Generate arrival narrative
        prompt = get_arrival_prompt(self.state, self.current_era)
        response = self.narrator.generate(prompt)
        
        # Record narrative in history
        if self.current_game:
            self.history.add_narrative(self.current_game, response)
        
        # Process response
        self._process_response(response)
        
        self.state.phase = GamePhase.LIVING
    
    def _show_era_summary(self):
        """Show a brief summary of the era's main themes"""
        era = self.current_era
        
        print(f"{Colors.CYAN}━━━ About This Era ━━━{Colors.END}")
        print()
        
        # Location and time context
        year = era.get('year', 0)
        if year < 0:
            year_str = f"{abs(year)} BCE"
        else:
            year_str = f"{year} CE"
        print(f"  {Colors.DIM}You are in {era.get('location', 'an unknown place')}, {year_str}.{Colors.END}")
        print()
        
        # Get key events as summary points (up to 5)
        key_events = era.get('key_events', [])[:5]
        
        if key_events:
            print(f"  {Colors.YELLOW}What defines this time:{Colors.END}")
            for event in key_events:
                # Truncate long events
                if len(event) > 75:
                    event = event[:72] + "..."
                print(f"    • {event}")
            print()
        
        print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
        print()
    
    def _play_turn(self):
        """Play a single turn"""
        # Show device status if enabled
        if SHOW_DEVICE_STATUS:
            self._show_device_status()
        
        # Determine valid choices - Q is available except when "stay forever" is an option
        show_quit = not (self.state.phase == GamePhase.WINDOW_OPEN and self.state.can_stay_meaningfully)
        valid_choices = ['A', 'B', 'C', 'Q'] if show_quit else ['A', 'B', 'C']
        
        # Show quit option if available
        if show_quit:
            print(f"\n{Colors.DIM}[Q] Quit game{Colors.END}")
        
        # Get player choice
        choice = get_input("Your choice:", valid_choices)
        
        # Handle quit
        if choice == 'Q':
            self._handle_quit()
            return
        
        # Check for special window choices
        if self.state.phase == GamePhase.WINDOW_OPEN:
            # B = leave this era
            if self._is_leaving_choice(choice):
                self._handle_leaving()
                return
            # C = stay forever (only when can_stay_meaningfully)
            if choice == 'C' and self.state.can_stay_meaningfully:
                self._handle_stay_forever()
                return
        
        # Normal turn
        roll = roll_dice()
        
        clear_screen()
        if self.state.current_era:
            print(f"{Colors.DIM}{self.current_era['name']} | {self.state.current_era.time_in_era_description}{Colors.END}\n")
        
        # Generate response
        prompt = get_turn_prompt(self.state, choice, roll)
        response = self.narrator.generate(prompt)
        
        # Record narrative in history
        if self.current_game:
            self.history.add_narrative(self.current_game, response)
        
        # Process response
        self._process_response(response)
        
        # Advance turn and check for window
        events = self.state.advance_turn()
        
        if events["window_opened"]:
            self._handle_window_open()
        elif events["window_closing"]:
            print(f"\n{Colors.YELLOW}The device pulses urgently. The window is closing...{Colors.END}")
        elif events["window_closed"]:
            print(f"\n{Colors.DIM}The device falls silent. The moment has passed.{Colors.END}")
            self.state.phase = GamePhase.LIVING
    
    def _show_device_status(self):
        """Show time machine indicator status"""
        indicator = self.state.time_machine.indicator
        
        if indicator == IndicatorState.DARK:
            status = f"{Colors.DIM}[Device: silent]{Colors.END}"
        elif indicator == IndicatorState.FAINT_PULSE:
            status = f"{Colors.DIM}[Device: faint pulse]{Colors.END}"
        elif indicator == IndicatorState.STEADY_GLOW:
            status = f"{Colors.YELLOW}[Device: glowing steadily]{Colors.END}"
        elif indicator == IndicatorState.BRIGHT_PULSE:
            status = f"{Colors.GREEN}[Device: WINDOW OPEN]{Colors.END}"
        
        print(f"\n{status}")
    
    def _handle_window_open(self):
        """Handle when travel window opens - generate new choices including leave option"""
        # Clear screen to make it clear we're in a new moment
        clear_screen()
        
        if self.current_era:
            print(f"{Colors.DIM}{self.current_era['name']} | {self.state.current_era.time_in_era_description}{Colors.END}\n")
        
        print(f"{Colors.GREEN}{'═' * 50}{Colors.END}")
        print(f"{Colors.GREEN}  THE WINDOW IS OPEN{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 50}{Colors.END}")
        print()
        
        if self.state.can_stay_meaningfully:
            print(f"{Colors.YELLOW}You've built something here. You could stay forever...{Colors.END}\n")
        
        # Update phase
        self.state.phase = GamePhase.WINDOW_OPEN
        
        # Generate new narrative with window-aware choices (including leave option)
        prompt = get_window_prompt(self.state)
        response = self.narrator.generate(prompt)
        
        # Record narrative in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[The time machine window opens]\n" + response)
        
        # Process response
        self._process_response(response)
    
    def _is_leaving_choice(self, choice: str) -> bool:
        """Check if choice is the time machine activation (always B when window is open)"""
        # When window is open, B is always the "activate time machine" choice per prompts
        return choice == 'B' and self.state.time_machine.window_active
    
    def _handle_leaving(self):
        """Handle player choosing to leave"""
        self.state.choose_to_travel()
        
        clear_screen()
        print_header("DEPARTURE")
        
        prompt = get_leaving_prompt(self.state)
        response = self.narrator.generate(prompt)
        
        # Record departure in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[You activate the time machine]\n" + response)
        
        input(f"\n{Colors.DIM}Press Enter to see where you land...{Colors.END}")
        
        # Enter new era
        self._enter_random_era()
    
    def _handle_stay_forever(self):
        """Handle player choosing to stay forever - end game"""
        clear_screen()
        print_header("A NEW HOME")
        
        print(f"{Colors.CYAN}You reach for the device on your wrist...{Colors.END}")
        time.sleep(1)
        print(f"{Colors.CYAN}And then you stop.{Colors.END}")
        time.sleep(1)
        print()
        print(f"{Colors.GREEN}This is your home now.{Colors.END}")
        print()
        time.sleep(1)
        
        # Generate ending narrative
        prompt = get_staying_ending_prompt(self.state, self.current_era)
        response = self.narrator.generate(prompt)
        
        # Record ending narrative in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[You choose to stay forever]\n" + response)
        
        # End the game
        self.state.choose_to_stay(is_final=True)
        self.state.end_game()
        
        # Calculate and display score
        self._show_final_score()
    
    def _show_final_score(self, ending_type_override: str = None):
        """Display final score"""
        # Calculate score
        score = calculate_score(self.state, ending_type_override=ending_type_override)
        
        # Save to game history
        if self.current_game:
            self.history.end_game(self.current_game, score)
        
        # Add to leaderboard (silently)
        leaderboard = Leaderboard()
        leaderboard.add_score(score)
        
        input(f"\n{Colors.DIM}Press Enter to see your journey's score...{Colors.END}")
        
        clear_screen()
        print_header("YOUR JOURNEY")
        
        # Show score breakdown
        print(score.get_breakdown_display())
        
        print(f"\n{Colors.DIM}Thank you for playing Anachron.{Colors.END}")
    
    def _handle_quit(self):
        """Handle player choosing to quit the game"""
        clear_screen()
        print_header("YOUR JOURNEY ENDS")
        
        print(f"{Colors.CYAN}You set down the device.{Colors.END}")
        time.sleep(0.5)
        print(f"{Colors.CYAN}Some journeys end before the destination is found.{Colors.END}")
        print()
        time.sleep(0.5)
        
        # Record quit in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[Journey abandoned]")
        
        # End the game
        self.state.end_game()
        
        # Calculate and display score with "abandoned" ending type
        self._show_final_score(ending_type_override="abandoned")
    
    def _handle_staying(self, final: bool = False):
        """Handle player choosing to stay"""
        if final:
            # Final stay - end game
            self.state.choose_to_stay(is_final=True)
            
            clear_screen()
            print_header("YOU CHOOSE TO STAY")
            
            prompt = get_staying_ending_prompt(self.state, self.current_era)
            response = self.narrator.generate(prompt)
            
            self.state.end_game()
        else:
            # Just letting window close
            self.state.choose_to_stay()
            print(f"\n{Colors.DIM}You let the moment pass. The device falls silent.{Colors.END}")
    
    def _process_response(self, response: str):
        """Process AI response - extract data and update state."""
        # Parse anchor adjustments
        adjustments = parse_anchor_adjustments(response)
        for anchor, delta in adjustments.items():
            if delta != 0:
                self.state.fulfillment.adjust(anchor, delta, "choice")
        
        # Parse item usage
        used_items = parse_item_usage(response, self.state.inventory)
        for item_id in used_items:
            self.state.inventory.use_item(item_id)
        
        # Extract choices for validation
        choices = self._parse_choices(response)
        
        # Store in era state
        if self.state.current_era and choices:
            self.state.current_era.events.append(f"Turn {self.state.current_era.turns_in_era}")
    
    def _parse_choices(self, response: str) -> list:
        """Extract choices from response"""
        # Strip anchor tags first
        clean_response = strip_anchor_tags(response)
        
        choices = []
        for line in clean_response.split('\n'):
            line = line.strip()
            match = re.match(r'^\[([A-C])\]\s*(.+)$', line, re.IGNORECASE)
            if match:
                choice_text = match.group(2).strip()
                # Remove any trailing score tags or other artifacts
                choice_text = re.sub(r'\s*<[^>]+>.*$', '', choice_text)
                choice_text = re.sub(r'\s*SCORES:.*$', '', choice_text, flags=re.IGNORECASE)
                if choice_text and len(choice_text) > 3:
                    choices.append({'id': match.group(1).upper(), 'text': choice_text})
        return choices[:3]


def main():
    logger.info("=== Game starting ===")
    try:
        game = Game()
        game.run()
        logger.info("=== Game ended normally ===")
    except EOFError as e:
        logger.error(f"Game crashed with EOFError: {e}")
        print(f"\n{Colors.RED}Connection lost. Please refresh to restart.{Colors.END}")
    except KeyboardInterrupt:
        logger.info("Game interrupted by user (Ctrl+C)")
        print(f"\n{Colors.YELLOW}Game interrupted.{Colors.END}")
    except Exception as e:
        logger.error(f"Game crashed with unexpected exception: {type(e).__name__}: {e}", exc_info=True)
        print(f"\n{Colors.RED}An error occurred: {e}{Colors.END}")
    finally:
        logger.info("=== Game process exiting ===")


if __name__ == "__main__":
    main()
