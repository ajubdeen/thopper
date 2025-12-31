#!/usr/bin/env python3
"""
Anachron - Game API Module

JSON-based API for the game, designed for web/mobile frontends.
Separates game logic from presentation entirely.

All methods return structured JSON that frontends can render as they wish.
"""

import json
import random
import re
from typing import Optional, Generator, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Local imports
from config import EUROPEAN_ERA_IDS
from game_state import GameState, GameMode, GamePhase, RegionPreference
from time_machine import select_random_era, IndicatorState
from fulfillment import parse_anchor_adjustments, strip_anchor_tags
from items import parse_item_usage
from eras import ERAS
from prompts import (
    get_system_prompt, get_arrival_prompt, get_turn_prompt,
    get_window_prompt, get_staying_ending_prompt, get_leaving_prompt
)
from scoring import calculate_score, Leaderboard, GameHistory


# =============================================================================
# MESSAGE TYPES
# =============================================================================

class MessageType:
    """Types of messages the API can emit"""
    # Game flow
    GAME_START = "game_start"
    GAME_END = "game_end"
    
    # Screens/phases
    TITLE = "title"
    SETUP_NAME = "setup_name"
    SETUP_REGION = "setup_region"
    INTRO_STORY = "intro_story"
    INTRO_ITEMS = "intro_items"
    INTRO_DEVICE = "intro_device"
    
    # Gameplay
    ERA_ARRIVAL = "era_arrival"
    ERA_SUMMARY = "era_summary"
    NARRATIVE = "narrative"
    NARRATIVE_CHUNK = "narrative_chunk"  # For streaming
    CHOICES = "choices"
    DEVICE_STATUS = "device_status"
    WINDOW_OPEN = "window_open"
    WINDOW_CLOSING = "window_closing"
    WINDOW_CLOSED = "window_closed"
    
    # Endings
    DEPARTURE = "departure"
    STAYING_FOREVER = "staying_forever"
    ENDING_NARRATIVE = "ending_narrative"
    FINAL_SCORE = "final_score"
    
    # System
    WAITING_INPUT = "waiting_input"
    ERROR = "error"
    LOADING = "loading"


def emit(msg_type: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a standardized message"""
    return {
        "type": msg_type,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# NARRATIVE ENGINE (JSON-based)
# =============================================================================

class NarrativeEngine:
    """Handles AI-generated narrative with JSON output"""
    
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
        self.messages = []
    
    def generate_streaming(self, user_prompt: str) -> Generator[Dict, None, str]:
        """
        Generate narrative response with streaming.
        Yields message dicts, returns full response.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        
        if not self.client:
            response = self._demo_response(user_prompt)
            # Simulate streaming for demo mode
            words = response.split(' ')
            for i, word in enumerate(words):
                chunk = word + (' ' if i < len(words) - 1 else '')
                yield emit(MessageType.NARRATIVE_CHUNK, {"text": chunk})
        else:
            response = yield from self._api_call_streaming()
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def generate(self, user_prompt: str) -> str:
        """Generate narrative response (non-streaming)"""
        self.messages.append({"role": "user", "content": user_prompt})
        
        if not self.client:
            response = self._demo_response(user_prompt)
        else:
            response = self._api_call()
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def _api_call_streaming(self) -> Generator[Dict, None, str]:
        """Make streaming API call, yield chunks, return full response"""
        response = ""
        buffer = ""
        in_anchor_tag = False
        
        try:
            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=self.system_prompt,
                messages=self.messages
            ) as api_stream:
                for text in api_stream.text_stream:
                    response += text
                    buffer += text
                    
                    # Handle anchor tag hiding
                    if '<anchors>' in buffer:
                        before_tag = buffer.split('<anchors>')[0]
                        if before_tag:
                            yield emit(MessageType.NARRATIVE_CHUNK, {"text": before_tag})
                        buffer = '<anchors>' + buffer.split('<anchors>', 1)[1]
                        in_anchor_tag = True
                    
                    if in_anchor_tag and '</anchors>' in buffer:
                        after_tag = buffer.split('</anchors>', 1)[1] if '</anchors>' in buffer else ''
                        buffer = after_tag
                        in_anchor_tag = False
                    
                    # Emit non-tag content
                    if not in_anchor_tag and '<' not in buffer:
                        if buffer:
                            yield emit(MessageType.NARRATIVE_CHUNK, {"text": buffer})
                        buffer = ""
                    elif not in_anchor_tag and '<' in buffer and '>' in buffer:
                        if '<anchors>' not in buffer:
                            yield emit(MessageType.NARRATIVE_CHUNK, {"text": buffer})
                            buffer = ""
            
            # Emit remaining buffer
            if buffer and not in_anchor_tag:
                clean_buffer = re.sub(r'<anchors>.*?</anchors>', '', buffer, flags=re.DOTALL)
                if clean_buffer:
                    yield emit(MessageType.NARRATIVE_CHUNK, {"text": clean_buffer})
                    
        except Exception as e:
            yield emit(MessageType.ERROR, {"message": str(e)})
            response = self._demo_response("")
        
        return response
    
    def _api_call(self) -> str:
        """Make non-streaming API call"""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=self.system_prompt,
                messages=self.messages
            )
            return response.content[0].text
        except Exception as e:
            return self._demo_response("")
    
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
# GAME API CLASS
# =============================================================================

class GameAPI:
    """
    JSON-based game API for web/mobile frontends.
    
    All methods yield or return structured message dicts.
    The frontend renders these however it wants.
    """
    
    def __init__(self):
        self.state = GameState()
        self.narrator = None
        self.current_era = None
        self._selected_region = RegionPreference.WORLDWIDE
        
        # History tracking
        self.history = GameHistory()
        self.current_game = None
    
    # =========================================================================
    # GAME FLOW
    # =========================================================================
    
    def start_game(self) -> Generator[Dict, None, None]:
        """Initialize a new game, yield setup messages"""
        yield emit(MessageType.TITLE, {
            "title": "ANACHRON",
            "tagline": "How will you fare in another era?"
        })
        
        yield emit(MessageType.SETUP_NAME, {
            "prompt": "Enter your name:",
            "default": "Traveler"
        })
    
    def set_player_name(self, name: str) -> Generator[Dict, None, None]:
        """Set player name and move to region selection"""
        self.state.player_name = name if name.strip() else "Traveler"
        
        # TEMPORARY: Force European-only eras to avoid race/ethnicity immersion issues
        # Player is established as 24yo from Bay Area (implicitly white/Western)
        # Non-Western eras require proper handling of appearance/otherness
        # TODO: Re-enable region selection when player appearance system is implemented
        yield emit(MessageType.SETUP_REGION, {
            "prompt": "Where in history?",
            "auto_select": "european",  # Frontend should skip this screen and use this value
            "options": [
                {
                    "id": "european",
                    "name": "European Focus",
                    "description": "Ancient Greece, Vikings, Medieval Europe, Colonial America, Industrial Britain, World Wars"
                },
                {
                    "id": "worldwide",
                    "name": "World Explorer", 
                    "description": "All eras: Egypt, China, Aztec Empire, Mughal India, plus European eras"
                }
            ]
        })
    
    def set_region(self, region: str) -> Generator[Dict, None, None]:
        """Set region preference and show intro"""
        self._selected_region = RegionPreference.EUROPEAN if region == "european" else RegionPreference.WORLDWIDE
        
        # Initialize game state
        self.state.start_game(self.state.player_name, GameMode.MATURE, self._selected_region)
        self.narrator = NarrativeEngine(self.state)
        self.current_game = self.history.start_new_game(self.state.player_name)
        
        # Intro story
        yield emit(MessageType.INTRO_STORY, {
            "paragraphs": [
                "Twenty-four. Stanford. Six figures. A life that looks perfect and feels like nothing.",
                "So when the lab needed a volunteer for the time machine's first human trial, you stepped up without thinking. Thirty seconds into the past. What could go wrong?",
                "Everything, it turns out.",
                "The machine is broken. You can't go home. All you have is what was in your pockets:"
            ]
        })
        
        # Show items
        items = []
        for item in self.state.inventory.modern_items:
            items.append({
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "uses": item.uses,
                "utility": item.utility,
                "risk": item.risk
            })
        
        yield emit(MessageType.INTRO_ITEMS, {"items": items})
        
        # Device explanation
        yield emit(MessageType.INTRO_DEVICE, {
            "title": "THE DEVICE",
            "description": "The time machine is small—about the size of a chunky wristwatch. You wear it on your wrist, hidden under your sleeve.",
            "mechanics": [
                "The window to use it won't open immediately when you arrive",
                "You'll have time to settle in first—typically most of a year",
                "When the window opens, you have a short time to decide",
                "Choose to activate it, or let the window close and stay"
            ],
            "catch": [
                "You can't choose when you go—it's random",
                "Your three items always come with you",
                "Your relationships do NOT come with you",
                "Each jump means starting over"
            ],
            "goal": "Find a time and place where you want to stay. Build something worth staying for—people, purpose, freedom. When the window opens and you choose not to leave... that's when you've found happiness."
        })
        
        yield emit(MessageType.WAITING_INPUT, {"action": "continue_to_era"})
    
    def enter_first_era(self) -> Generator[Dict, None, None]:
        """Enter the first random era"""
        yield from self._enter_random_era()
    
    # =========================================================================
    # GAMEPLAY
    # =========================================================================
    
    def make_choice(self, choice: str) -> Generator[Dict, None, None]:
        """Process a player choice (A, B, C, or Q)"""
        choice = choice.upper()
        
        # Handle quit
        if choice == 'Q':
            yield from self._handle_quit()
            return
        
        # Check for special window choices (window was already open from previous turn)
        if self.state.phase == GamePhase.WINDOW_OPEN:
            if choice == 'A':  # Leave this era (new ordering)
                yield from self._handle_leaving()
                return
            if choice == 'B' and self.state.can_stay_meaningfully:  # Stay forever
                yield from self._handle_stay_forever()
                return
            # Otherwise B or C = continue (will generate next turn)
        
        # Roll dice for this turn
        roll = random.randint(1, 20)
        
        # IMPORTANT: Advance turn FIRST to check if window opens
        # This lets us decide which prompt to use BEFORE generating narrative
        events = self.state.advance_turn()
        
        # If window just opened, generate combined turn+window response
        if events["window_opened"]:
            yield emit(MessageType.WINDOW_OPEN, {
                "message": "THE WINDOW IS OPEN",
                "can_stay_meaningfully": self.state.can_stay_meaningfully,
                "stay_message": "You've built something here. You could stay forever..." if self.state.can_stay_meaningfully else None
            })
            
            yield emit(MessageType.LOADING, {"message": "A moment of decision..."})
            
            # Generate combined turn outcome + window choice narrative
            prompt = self._get_combined_turn_and_window_prompt(choice, roll)
            response = ""
            
            for msg in self.narrator.generate_streaming(prompt):
                yield msg
                if msg["type"] == MessageType.NARRATIVE_CHUNK:
                    response += msg["data"].get("text", "")
            
            if not response:
                response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
            
            # Record narrative
            if self.current_game:
                self.history.add_narrative(self.current_game, "[The time machine window opens]\n" + response)
            
            # Process response (anchors, items)
            self._process_response(response)
            
            # Parse and emit choices (with window-specific options)
            choices = self._parse_choices(response)
            yield emit(MessageType.CHOICES, {
                "choices": choices,
                "can_quit": not self.state.can_stay_meaningfully,
                "window_open": True,
                "can_stay_forever": self.state.can_stay_meaningfully
            })
        else:
            # Normal turn - generate standard response
            yield emit(MessageType.LOADING, {"message": "The story unfolds..."})
            
            prompt = get_turn_prompt(self.state, choice, roll)
            response = ""
            
            for msg in self.narrator.generate_streaming(prompt):
                yield msg
                if msg["type"] == MessageType.NARRATIVE_CHUNK:
                    response += msg["data"].get("text", "")
            
            if not response:
                response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
            
            # Record narrative
            if self.current_game:
                self.history.add_narrative(self.current_game, response)
            
            # Process response (anchors, items)
            self._process_response(response)
            
            # Parse and emit choices
            choices = self._parse_choices(response)
            yield emit(MessageType.CHOICES, {
                "choices": choices,
                "can_quit": True
            })
            
            # Handle window state notifications (but NOT window_opened since we handled it above)
            if events["window_closing"]:
                yield emit(MessageType.WINDOW_CLOSING, {
                    "message": "The device pulses urgently. The window is closing..."
                })
            elif events["window_closed"]:
                yield emit(MessageType.WINDOW_CLOSED, {
                    "message": "The device falls silent. The moment has passed."
                })
                self.state.phase = GamePhase.LIVING
        
        # Emit device status
        yield self._get_device_status()
    
    def get_current_state(self) -> Dict:
        """Get the current game state for frontend rendering"""
        return {
            "phase": self.state.phase.value,
            "player_name": self.state.player_name,
            "era": {
                "name": self.current_era["name"] if self.current_era else None,
                "year": self.current_era["year"] if self.current_era else None,
                "location": self.current_era["location"] if self.current_era else None,
                "time_in_era": self.state.current_era.time_in_era_description if self.state.current_era else None
            } if self.current_era else None,
            "device": {
                "indicator": self.state.time_machine.indicator.value,
                "window_active": self.state.time_machine.window_active,
                "window_turns_remaining": self.state.time_machine.window_turns_remaining
            },
            "can_stay_meaningfully": self.state.can_stay_meaningfully,
            "total_turns": self.state.total_turns,
            "eras_visited": len(self.state.time_machine.eras_visited)
        }
    
    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    def _enter_random_era(self) -> Generator[Dict, None, None]:
        """Enter a random era"""
        visited_ids = self.state.time_machine.eras_visited
        
        # Filter eras based on region preference
        if self.state.region_preference == RegionPreference.EUROPEAN:
            available_eras = [e for e in ERAS if e['id'] in EUROPEAN_ERA_IDS]
        else:
            available_eras = ERAS
        
        self.current_era = select_random_era(available_eras, visited_ids)
        self.state.enter_era(self.current_era)
        
        # Update time machine display
        self.state.time_machine.update_display(
            year=self.current_era['year'],
            location=self.current_era['location'],
            era_name=self.current_era['name']
        )
        
        # Reset inventory revealed status
        self.state.inventory.reset_for_new_era()
        
        # Set up narrator for this era
        self.narrator.set_era(self.current_era)
        
        # Record era in history
        if self.current_game:
            self.history.start_era(
                self.current_game,
                self.current_era['name'],
                self.current_era['year'],
                self.current_era['location']
            )
        
        # Emit era arrival
        year = self.current_era['year']
        year_str = f"{abs(year)} BCE" if year < 0 else f"{year} CE"
        
        yield emit(MessageType.ERA_ARRIVAL, {
            "era_name": self.current_era['name'],
            "year": year,
            "year_display": year_str,
            "location": self.current_era['location'],
            "device_display": self.state.time_machine.display.get_display_text()
        })
        
        # Era summary
        yield emit(MessageType.ERA_SUMMARY, {
            "location": self.current_era['location'],
            "year_display": year_str,
            "key_events": self.current_era.get('key_events', [])[:5]
        })
        
        yield emit(MessageType.LOADING, {"message": "Arriving..."})
        
        # Generate arrival narrative
        prompt = get_arrival_prompt(self.state, self.current_era)
        response = ""
        
        for msg in self.narrator.generate_streaming(prompt):
            yield msg
            if msg["type"] == MessageType.NARRATIVE_CHUNK:
                response += msg["data"].get("text", "")
        
        if not response:
            response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
        
        # Record narrative
        if self.current_game:
            self.history.add_narrative(self.current_game, response)
        
        # Process response
        self._process_response(response)
        
        # Parse and emit choices
        choices = self._parse_choices(response)
        yield emit(MessageType.CHOICES, {
            "choices": choices,
            "can_quit": True
        })
        
        # Set phase
        self.state.phase = GamePhase.LIVING
        
        # Emit device status
        yield self._get_device_status()
    
    def _get_combined_turn_and_window_prompt(self, choice: str, roll: int) -> str:
        """
        Generate a prompt that combines the turn outcome with window opening.
        This prevents the double-narrative issue where turn and window are separate.
        """
        # Luck interpretation
        if roll <= 5:
            luck = "UNLUCKY - complications arise, the approach hits obstacles"
        elif roll <= 8:
            luck = "SLIGHTLY UNLUCKY - minor setbacks or delays"
        elif roll <= 12:
            luck = "NEUTRAL - things go roughly as expected"
        elif roll <= 16:
            luck = "LUCKY - things go better than expected"
        else:
            luck = "VERY LUCKY - unexpected good fortune, doors open"
        
        can_stay = self.state.can_stay_meaningfully
        fulfillment = self.state.fulfillment.get_narrative_state()
        window_turns = self.state.time_machine.window_turns_remaining  # Will be 3 since window just opened
        
        # Build emotional weight description
        if can_stay:
            emotional_weight = """
The player has BUILT something here. They have:"""
            if fulfillment['belonging']['has_arrived']:
                emotional_weight += "\n- People who would miss them, a place in the community"
            if fulfillment['legacy']['has_arrived']:
                emotional_weight += "\n- Something lasting they've created or influenced"
            if fulfillment['freedom']['has_arrived']:
                emotional_weight += "\n- A life on their own terms, hard-won independence"
            emotional_weight += """

Leaving now means LOSING much of this. Make this cost FELT in the narrative."""
        else:
            emotional_weight = """
The player hasn't built deep roots here yet. Leaving is easier, less costly.
But they could stay and build more."""
        
        # Choice format - window just opened = turn 1 of 3
        if can_stay:
            choice_format = """
CHOICE ORDER (window turn 1 of 3 - player has time to decide):

[A] Activate the time machine and leave this era behind
[B] This is my home now. I choose to stay here forever. (ENDS THE GAME - player accepts this as permanent home)
[C] Continue with current situation - the window will remain open for a little while longer

Note: [A] leaves, [B] ends the game (permanent stay), [C] continues while window stays open."""
        else:
            choice_format = """
CHOICE ORDER (window turn 1 of 3 - player has time to decide):

[A] Activate the time machine and leave this era behind
[B] First continuation option with current relationships/situation - mention window will remain open a little longer
[C] Second continuation option - mention window will remain open a little longer

Both [B] and [C] continue the game while the window stays open."""
        
        return f"""The player chose: [{choice}]
Dice roll: {roll}/20 - {luck}

THE TIME MACHINE WINDOW OPENS during this turn's events.

{emotional_weight}

NARRATIVE STRUCTURE:
1. First, briefly resolve the outcome of their choice [{choice}] (1-2 paragraphs)
2. Time passes appropriately (weeks, as usual for a turn)
3. THEN the device pulses - the window opens
4. Describe the weight of the moment - what they've built, who would miss them
5. Present window-aware choices

The narrative should flow naturally from choice resolution into the window moment.
Do NOT present two separate sets of choices - only ONE set at the end.

CRITICAL: Keep the time machine choice CLEAN. The player must be able to simply 
activate the device. No combat, imprisonment, or obstacles to leaving.

{choice_format}

FORMAT:
- 3-4 paragraphs total, ending with the window moment
- Then present the choices as specified above

<anchors>belonging[+/-X] legacy[+/-X] freedom[+/-X]</anchors>

IMPORTANT: Put the <anchors> tag on its own line AFTER all three choices."""

    def _handle_window_open(self) -> Generator[Dict, None, None]:
        """Handle when travel window opens"""
        self.state.phase = GamePhase.WINDOW_OPEN
        
        yield emit(MessageType.WINDOW_OPEN, {
            "message": "THE WINDOW IS OPEN",
            "can_stay_meaningfully": self.state.can_stay_meaningfully,
            "stay_message": "You've built something here. You could stay forever..." if self.state.can_stay_meaningfully else None
        })
        
        yield emit(MessageType.LOADING, {"message": "A moment of decision..."})
        
        # Generate window narrative
        prompt = get_window_prompt(self.state)
        response = ""
        
        for msg in self.narrator.generate_streaming(prompt):
            yield msg
            if msg["type"] == MessageType.NARRATIVE_CHUNK:
                response += msg["data"].get("text", "")
        
        if not response:
            response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
        
        # Record narrative
        if self.current_game:
            self.history.add_narrative(self.current_game, "[The time machine window opens]\n" + response)
        
        # Process response
        self._process_response(response)
        
        # Parse and emit choices (with window-specific options)
        choices = self._parse_choices(response)
        yield emit(MessageType.CHOICES, {
            "choices": choices,
            "can_quit": not self.state.can_stay_meaningfully,  # No quit when "stay forever" is available
            "window_open": True,
            "can_stay_forever": self.state.can_stay_meaningfully
        })
    
    def _handle_leaving(self) -> Generator[Dict, None, None]:
        """Handle player choosing to leave"""
        self.state.choose_to_travel()
        
        yield emit(MessageType.DEPARTURE, {
            "title": "DEPARTURE",
            "message": "You activate the time machine..."
        })
        
        yield emit(MessageType.LOADING, {"message": "Reality shifts..."})
        
        # Generate departure narrative
        prompt = get_leaving_prompt(self.state)
        response = ""
        
        for msg in self.narrator.generate_streaming(prompt):
            yield msg
            if msg["type"] == MessageType.NARRATIVE_CHUNK:
                response += msg["data"].get("text", "")
        
        if not response:
            response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
        
        # Record departure
        if self.current_game:
            self.history.add_narrative(self.current_game, "[You activate the time machine]\n" + response)
        
        yield emit(MessageType.WAITING_INPUT, {"action": "continue_to_next_era"})
    
    def continue_to_next_era(self) -> Generator[Dict, None, None]:
        """Continue to the next era after departure"""
        yield from self._enter_random_era()
    
    def _handle_stay_forever(self) -> Generator[Dict, None, None]:
        """Handle player choosing to stay forever"""
        yield emit(MessageType.STAYING_FOREVER, {
            "title": "A NEW HOME",
            "messages": [
                "You reach for the device on your wrist...",
                "And then you stop.",
                "This is your home now."
            ]
        })
        
        yield emit(MessageType.LOADING, {"message": "Your story concludes..."})
        
        # Generate ending narrative
        prompt = get_staying_ending_prompt(self.state, self.current_era)
        response = ""
        
        for msg in self.narrator.generate_streaming(prompt):
            yield msg
            if msg["type"] == MessageType.NARRATIVE_CHUNK:
                response += msg["data"].get("text", "")
        
        if not response:
            response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
        
        # Record ending
        if self.current_game:
            self.history.add_narrative(self.current_game, "[You choose to stay forever]\n" + response)
        
        # End the game
        self.state.choose_to_stay(is_final=True)
        self.state.end_game()
        
        # Emit waiting for user to continue to score screen
        yield emit(MessageType.WAITING_INPUT, {"action": "continue_to_score"})
        
        # Store ending narrative for when score is emitted
        self._ending_narrative = response
    
    def _handle_quit(self) -> Generator[Dict, None, None]:
        """Handle player choosing to quit"""
        yield emit(MessageType.GAME_END, {
            "title": "YOUR JOURNEY ENDS",
            "messages": [
                "You set down the device.",
                "Some journeys end before the destination is found."
            ]
        })
        
        # Record quit
        if self.current_game:
            self.history.add_narrative(self.current_game, "[Journey abandoned]")
        
        # End the game
        self.state.end_game()
        
        # Calculate and emit score
        yield from self._emit_final_score(ending_type_override="abandoned")
    
    def continue_to_score(self) -> Generator[Dict, None, None]:
        """Show final score after player has read ending narrative"""
        ending_narrative = getattr(self, '_ending_narrative', None)
        yield from self._emit_final_score(ending_narrative=ending_narrative)
    
    def _emit_final_score(self, ending_type_override: str = None, ending_narrative: str = None) -> Generator[Dict, None, None]:
        """Calculate and emit final score"""
        score = calculate_score(self.state, ending_type_override=ending_type_override)
        
        # Save to history
        if self.current_game:
            self.history.end_game(self.current_game, score)
        
        # Add to leaderboard with ending narrative
        leaderboard = Leaderboard()
        rank = leaderboard.add_score(score, ending_narrative=ending_narrative)
        
        yield emit(MessageType.FINAL_SCORE, {
            "total": score.total,
            "rank": rank,
            "breakdown": {
                "survival": {
                    "turns": score.turns_survived,
                    "points": score.survival_points
                },
                "exploration": {
                    "eras": score.eras_visited,
                    "points": score.exploration_points
                },
                "fulfillment": {
                    "belonging": score.belonging_score,
                    "legacy": score.legacy_score,
                    "freedom": score.freedom_score,
                    "total": score.fulfillment_points
                },
                "ending": {
                    "type": score.ending_type,
                    "bonus": score.ending_bonus
                }
            },
            "ending_narrative": ending_narrative or score.get_narrative_summary(),
            "blurb": score.get_blurb(),
            "final_era": score.final_era
        })
    
    def _get_device_status(self) -> Dict:
        """Get device status message"""
        indicator = self.state.time_machine.indicator
        
        status_map = {
            IndicatorState.DARK: {"status": "silent", "description": "The device is silent and cold."},
            IndicatorState.FAINT_PULSE: {"status": "faint_pulse", "description": "A faint pulse stirs in the device."},
            IndicatorState.STEADY_GLOW: {"status": "steady_glow", "description": "The device glows steadily."},
            IndicatorState.BRIGHT_PULSE: {"status": "window_open", "description": "The device pulses urgently. The window is open."}
        }
        
        status_data = status_map.get(indicator, status_map[IndicatorState.DARK])
        status_data["window_active"] = self.state.time_machine.window_active
        status_data["window_turns_remaining"] = self.state.time_machine.window_turns_remaining
        
        return emit(MessageType.DEVICE_STATUS, status_data)
    
    def _process_response(self, response: str):
        """Process AI response - extract anchors and item usage"""
        # Parse anchor adjustments
        adjustments = parse_anchor_adjustments(response)
        for anchor, delta in adjustments.items():
            if delta != 0:
                self.state.fulfillment.adjust(anchor, delta, "choice")
        
        # Parse item usage
        used_items = parse_item_usage(response, self.state.inventory)
        for item_id in used_items:
            self.state.inventory.use_item(item_id)
        
        # Store event
        if self.state.current_era:
            self.state.current_era.events.append(f"Turn {self.state.current_era.turns_in_era}")
    
    def _parse_choices(self, response: str) -> List[Dict]:
        """Extract choices from response"""
        clean_response = strip_anchor_tags(response)
        
        choices = []
        for line in clean_response.split('\n'):
            line = line.strip()
            match = re.match(r'^\[([A-C])\]\s*(.+)$', line, re.IGNORECASE)
            if match:
                choice_text = match.group(2).strip()
                choice_text = re.sub(r'\s*<[^>]+>.*$', '', choice_text)
                choice_text = re.sub(r'\s*SCORES:.*$', '', choice_text, flags=re.IGNORECASE)
                if choice_text and len(choice_text) > 3:
                    choices.append({
                        'id': match.group(1).upper(),
                        'text': choice_text
                    })
        
        return choices[:3]


# =============================================================================
# SIMPLE SYNCHRONOUS WRAPPER (for simpler integrations)
# =============================================================================

class GameSession:
    """
    Simplified wrapper that collects generator output into lists.
    Useful for request/response style APIs (e.g., REST endpoints).
    """
    
    def __init__(self):
        self.api = GameAPI()
    
    def start(self) -> List[Dict]:
        """Start game, return all setup messages"""
        return list(self.api.start_game())
    
    def set_name(self, name: str) -> List[Dict]:
        """Set player name"""
        return list(self.api.set_player_name(name))
    
    def set_region(self, region: str) -> List[Dict]:
        """Set region preference"""
        return list(self.api.set_region(region))
    
    def enter_first_era(self) -> List[Dict]:
        """Enter first era"""
        return list(self.api.enter_first_era())
    
    def choose(self, choice: str) -> List[Dict]:
        """Make a choice"""
        return list(self.api.make_choice(choice))
    
    def continue_to_next_era(self) -> List[Dict]:
        """Continue after departure"""
        return list(self.api.continue_to_next_era())
    
    def get_state(self) -> Dict:
        """Get current state"""
        return self.api.get_current_state()



