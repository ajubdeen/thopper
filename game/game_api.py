#!/usr/bin/env python3
"""
Anachron - Game API Module

JSON-based API for the game, designed for web/mobile frontends.
Separates game logic from presentation entirely.

All methods return structured JSON that frontends can render as they wish.

Features:
- User ID support for multi-user deployments
- Save/load game state for session persistence
- Resume functionality with full narrative/choice restoration
- Intent-based choice resolution (not position-based)
- Comprehensive API error logging and handling
"""

import json
import random
import re
import os
import logging
import time
from typing import Optional, Generator, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure module logger
logger = logging.getLogger('anachron.api')

# Create a file handler for API errors (in addition to any root handlers)
# This ensures API errors are captured even if root logging isn't configured
_log_dir = os.environ.get('ANACHRON_LOG_DIR', 'logs')
if not os.path.exists(_log_dir):
    try:
        os.makedirs(_log_dir)
    except OSError:
        _log_dir = '.'  # Fall back to current directory

_api_log_file = os.path.join(_log_dir, 'anachron_api.log')
_file_handler = logging.FileHandler(_api_log_file)
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(_file_handler)

# Also log to console
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
logger.addHandler(_console_handler)

logger.setLevel(logging.DEBUG)

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
    logger.info("Anthropic SDK loaded successfully")
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not available - running in demo mode")

# Local imports
from config import EUROPEAN_ERA_IDS, get_debug_era_id
from game_state import GameState, GameMode, GamePhase, RegionPreference
from time_machine import select_random_era, IndicatorState
from fulfillment import parse_anchor_adjustments, strip_anchor_tags
from items import parse_item_usage
from event_parsing import (
    parse_character_name, parse_key_npcs, parse_wisdom_moment,
    strip_event_tags, check_defining_moment
)
from eras import ERAS, get_era_by_id
from prompts import (
    get_system_prompt, get_arrival_prompt, get_turn_prompt,
    get_window_prompt, get_staying_ending_prompt, get_leaving_prompt,
    get_historian_narrative_prompt, get_quit_ending_prompt
)
from scoring import calculate_score, Leaderboard, AoAEntry, AnnalsOfAnachron
from db_storage import DatabaseSaveManager, DatabaseLeaderboardStorage, DatabaseGameHistory
from choice_intent import (
    ChoiceIntent, detect_choice_intent, filter_choices, 
    get_choice_intent_for_submission
)


# =============================================================================
# MESSAGE TYPES
# =============================================================================

class MessageType:
    """Types of messages the API can emit"""
    # Game flow
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_SAVED = "game_saved"
    GAME_LOADED = "game_loaded"
    GAME_RESUMED = "game_resumed"
    
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
    API_ERROR = "api_error"  # New: specific API error type
    
    # User data
    USER_GAMES = "user_games"
    LEADERBOARD = "leaderboard"
    ANNALS = "annals"
    ANNALS_ENTRY = "annals_entry"


def emit(msg_type: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a standardized message"""
    return {
        "type": msg_type,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# API ERROR LOGGING UTILITIES
# =============================================================================

def log_rate_limit_error(error: 'anthropic.RateLimitError', context: str = ""):
    """Log detailed rate limit error information"""
    error_details = {
        "error_type": "RateLimitError",
        "status_code": getattr(error, 'status_code', 429),
        "context": context,
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    # Try to extract retry-after header
    response = getattr(error, 'response', None)
    if response:
        headers = getattr(response, 'headers', {})
        error_details["retry_after"] = headers.get('retry-after')
        error_details["rate_limit_requests_remaining"] = headers.get('anthropic-ratelimit-requests-remaining')
        error_details["rate_limit_tokens_remaining"] = headers.get('anthropic-ratelimit-tokens-remaining')
        error_details["rate_limit_requests_reset"] = headers.get('anthropic-ratelimit-requests-reset')
        error_details["request_id"] = headers.get('request-id')
    
    logger.error(f"RATE_LIMIT_ERROR: {json.dumps(error_details)}")
    return error_details


def log_api_connection_error(error: 'anthropic.APIConnectionError', context: str = ""):
    """Log API connection errors"""
    error_details = {
        "error_type": "APIConnectionError",
        "context": context,
        "message": str(error),
        "cause": str(error.__cause__) if error.__cause__ else None,
        "timestamp": datetime.now().isoformat()
    }
    logger.error(f"API_CONNECTION_ERROR: {json.dumps(error_details)}")
    return error_details


def log_api_status_error(error: 'anthropic.APIStatusError', context: str = ""):
    """Log API status errors (4xx, 5xx)"""
    error_details = {
        "error_type": type(error).__name__,
        "status_code": getattr(error, 'status_code', None),
        "context": context,
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    response = getattr(error, 'response', None)
    if response:
        headers = getattr(response, 'headers', {})
        error_details["request_id"] = headers.get('request-id')
    
    logger.error(f"API_STATUS_ERROR: {json.dumps(error_details)}")
    return error_details


def log_generic_error(error: Exception, context: str = ""):
    """Log any other errors"""
    error_details = {
        "error_type": type(error).__name__,
        "context": context,
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    logger.error(f"GENERIC_ERROR: {json.dumps(error_details)}")
    return error_details


# =============================================================================
# NARRATIVE ENGINE (JSON-based)
# =============================================================================

class NarrativeEngine:
    """Handles AI-generated narrative with JSON output"""
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1.0  # seconds
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.messages = []
        self.system_prompt = ""
        self.last_error = None  # Track last error for debugging
        
        if ANTHROPIC_AVAILABLE:
            # Configure client with increased retries for rate limits
            self.client = anthropic.Anthropic(
                max_retries=3,  # SDK will auto-retry 429s with exponential backoff
                timeout=120.0   # 2 minute timeout for long responses
            )
            logger.info("Anthropic client initialized with max_retries=3, timeout=120s")
        else:
            self.client = None
    
    def set_era(self, era: dict):
        """Set up system prompt for current era"""
        self.system_prompt = get_system_prompt(self.game_state, era)
        self.messages = []
        logger.debug(f"Era set: {era.get('name', 'Unknown')}")
    
    def restore_conversation(self, messages: List[Dict]):
        """Restore conversation history from saved state"""
        self.messages = messages
        logger.debug(f"Conversation restored with {len(messages)} messages")
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history for saving"""
        return self.messages.copy()
    
    def generate_streaming(self, user_prompt: str) -> Generator[Dict, None, str]:
        """
        Generate narrative response with streaming.
        Yields message dicts, returns full response.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        self.last_error = None
        
        if not self.client:
            logger.warning("No API client - using demo response")
            response = self._demo_response(user_prompt)
            # Simulate streaming for demo mode
            words = response.split(' ')
            for i, word in enumerate(words):
                chunk = word + (' ' if i < len(words) - 1 else '')
                yield emit(MessageType.NARRATIVE_CHUNK, {"text": chunk})
        else:
            response = yield from self._api_call_streaming_with_retry(user_prompt)
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def generate(self, user_prompt: str) -> str:
        """Generate narrative response (non-streaming)"""
        self.messages.append({"role": "user", "content": user_prompt})
        self.last_error = None
        
        if not self.client:
            logger.warning("No API client - using demo response")
            response = self._demo_response(user_prompt)
        else:
            response = self._api_call_with_retry(user_prompt)
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def _api_call_streaming_with_retry(self, user_prompt: str) -> Generator[Dict, None, str]:
        """
        Make streaming API call with comprehensive error handling.
        Yields message dicts, returns full response.
        """
        last_error_details = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = yield from self._api_call_streaming()
                
                # Validate we got a real response
                if response and len(response.strip()) > 50:
                    return response
                else:
                    logger.warning(f"API returned empty/short response on attempt {attempt + 1}")
                    if attempt < self.MAX_RETRIES - 1:
                        continue
                    
            except anthropic.RateLimitError as e:
                last_error_details = log_rate_limit_error(e, f"streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                # Get retry delay from header or calculate exponential backoff
                retry_after = last_error_details.get('retry_after')
                if retry_after:
                    delay = float(retry_after)
                else:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Rate limited - waiting {delay}s before retry {attempt + 2}")
                    yield emit(MessageType.LOADING, {
                        "message": f"High demand - retrying in {int(delay)}s...",
                        "retry_attempt": attempt + 1
                    })
                    time.sleep(delay)
                    continue
                    
            except anthropic.APIConnectionError as e:
                last_error_details = log_api_connection_error(e, f"streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Connection error - waiting {delay}s before retry {attempt + 2}")
                    yield emit(MessageType.LOADING, {
                        "message": "Connection issue - retrying...",
                        "retry_attempt": attempt + 1
                    })
                    time.sleep(delay)
                    continue
                    
            except anthropic.APIStatusError as e:
                last_error_details = log_api_status_error(e, f"streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                # Don't retry 4xx errors (except 429 which is handled above)
                if 400 <= e.status_code < 500:
                    logger.error(f"Client error {e.status_code} - not retrying")
                    break
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Server error - waiting {delay}s before retry {attempt + 2}")
                    yield emit(MessageType.LOADING, {
                        "message": "Server issue - retrying...",
                        "retry_attempt": attempt + 1
                    })
                    time.sleep(delay)
                    continue
                    
            except Exception as e:
                last_error_details = log_generic_error(e, f"streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
        
        # All retries exhausted - emit error and use contextual fallback
        logger.error(f"All {self.MAX_RETRIES} API attempts failed")
        
        # Emit user-facing error with details
        error_msg = "The story couldn't be generated. "
        if last_error_details:
            error_type = last_error_details.get('error_type', 'Unknown')
            if error_type == 'RateLimitError':
                error_msg += "Service is experiencing high demand. "
            elif error_type == 'APIConnectionError':
                error_msg += "Connection issue occurred. "
            else:
                error_msg += "A technical issue occurred. "
            
            # Include request_id for support if available
            request_id = last_error_details.get('request_id')
            if request_id:
                error_msg += f"(ref: {request_id[:8]})"
        
        yield emit(MessageType.API_ERROR, {
            "message": error_msg,
            "recoverable": True,
            "error_type": last_error_details.get('error_type') if last_error_details else "Unknown"
        })
        
        # Return contextual fallback response
        response = self._contextual_fallback_response(user_prompt)
        
        # Stream the fallback response
        words = response.split(' ')
        for i, word in enumerate(words):
            chunk = word + (' ' if i < len(words) - 1 else '')
            yield emit(MessageType.NARRATIVE_CHUNK, {"text": chunk})
        
        return response
    
    def _api_call_streaming(self) -> Generator[Dict, None, str]:
        """Make streaming API call, yield chunks, return full response"""
        response = ""
        buffer = ""
        in_hidden_tag = False
        
        # Tags that should be hidden from the player
        hidden_tag_patterns = ['<anchors>', '<character_name>', '<key_npc>', '<wisdom>']
        
        with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=self.system_prompt,
            messages=self.messages
        ) as api_stream:
            for text in api_stream.text_stream:
                response += text
                buffer += text
                
                # Check for any hidden tag opening
                for tag_start in hidden_tag_patterns:
                    if tag_start in buffer and not in_hidden_tag:
                        before_tag = buffer.split(tag_start)[0]
                        if before_tag:
                            yield emit(MessageType.NARRATIVE_CHUNK, {"text": before_tag})
                        buffer = tag_start + buffer.split(tag_start, 1)[1]
                        in_hidden_tag = True
                        break
                
                # Check for tag closing
                if in_hidden_tag:
                    # Check for any closing tag
                    closing_tags = ['</anchors>', '</character_name>', '</key_npc>', '</wisdom>']
                    for close_tag in closing_tags:
                        if close_tag in buffer:
                            after_tag = buffer.split(close_tag, 1)[1] if close_tag in buffer else ''
                            buffer = after_tag
                            in_hidden_tag = False
                            break
                
                # Emit non-tag content
                if not in_hidden_tag and '<' not in buffer:
                    if buffer:
                        yield emit(MessageType.NARRATIVE_CHUNK, {"text": buffer})
                    buffer = ""
                elif not in_hidden_tag and '<' in buffer and '>' in buffer:
                    # Check if this is a hidden tag
                    is_hidden = any(tag in buffer for tag in hidden_tag_patterns)
                    if not is_hidden:
                        yield emit(MessageType.NARRATIVE_CHUNK, {"text": buffer})
                        buffer = ""
        
        # Emit remaining buffer after cleaning all hidden tags
        if buffer and not in_hidden_tag:
            clean_buffer = buffer
            clean_buffer = re.sub(r'<anchors>.*?</anchors>', '', clean_buffer, flags=re.DOTALL)
            clean_buffer = re.sub(r'<character_name>.*?</character_name>', '', clean_buffer, flags=re.DOTALL | re.IGNORECASE)
            clean_buffer = re.sub(r'<key_npc>.*?</key_npc>', '', clean_buffer, flags=re.DOTALL | re.IGNORECASE)
            clean_buffer = re.sub(r'<wisdom>.*?</wisdom>', '', clean_buffer, flags=re.DOTALL | re.IGNORECASE)
            if clean_buffer.strip():
                yield emit(MessageType.NARRATIVE_CHUNK, {"text": clean_buffer})
        
        logger.debug(f"Streaming response completed: {len(response)} chars")
        return response
    
    def _api_call_with_retry(self, user_prompt: str) -> str:
        """Make non-streaming API call with retry logic"""
        last_error_details = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    system=self.system_prompt,
                    messages=self.messages
                )
                result = response.content[0].text
                logger.debug(f"Non-streaming response: {len(result)} chars")
                return result
                
            except anthropic.RateLimitError as e:
                last_error_details = log_rate_limit_error(e, f"non-streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                retry_after = last_error_details.get('retry_after')
                delay = float(retry_after) if retry_after else self.BASE_RETRY_DELAY * (2 ** attempt)
                
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Rate limited - waiting {delay}s before retry")
                    time.sleep(delay)
                    continue
                    
            except anthropic.APIConnectionError as e:
                last_error_details = log_api_connection_error(e, f"non-streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
                    
            except anthropic.APIStatusError as e:
                last_error_details = log_api_status_error(e, f"non-streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                if 400 <= e.status_code < 500:
                    break
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
                    
            except Exception as e:
                last_error_details = log_generic_error(e, f"non-streaming attempt {attempt + 1}")
                self.last_error = last_error_details
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
        
        # All retries exhausted
        logger.error(f"All {self.MAX_RETRIES} non-streaming API attempts failed")
        return self._contextual_fallback_response(user_prompt)
    
    def _api_call(self) -> str:
        """Make non-streaming API call (legacy method - now uses retry wrapper)"""
        return self._api_call_with_retry("")
    
    def _contextual_fallback_response(self, prompt: str) -> str:
        """
        Generate a contextual fallback response when API fails.
        Uses game state to create a more relevant placeholder.
        """
        logger.warning(f"Using contextual fallback response (prompt hint: {prompt[:50] if prompt else 'none'}...)")
        
        # Check game state for context
        era_name = "this era"
        character_name = "you"
        turn_count = 0
        window_open = False
        
        if self.game_state:
            if self.game_state.current_era:
                era_name = self.game_state.current_era.era_name or "this era"
                character_name = self.game_state.current_era.character_name or "you"
                turn_count = self.game_state.current_era.turns_in_era
            if hasattr(self.game_state, 'time_machine'):
                window_open = self.game_state.time_machine.window_active
        
        # Check if this is an arrival
        is_arrival = "arrival" in prompt.lower() or turn_count == 0 or len(self.messages) <= 2
        
        if is_arrival:
            return f"""The world shifts and settles around you. Your senses slowly adjust to {era_name}.

The air is different here—carrying unfamiliar scents and sounds. People nearby regard you with curiosity, uncertainty written in their expressions.

You'll need to find your footing in this place. The device at your wrist is silent for now.

[A] Look for a place to gather information
[B] Seek out someone who might offer guidance  
[C] Find a quiet spot to observe and plan

<character_name>Stranger</character_name>
<anchors>belonging[0] legacy[0] freedom[0]</anchors>"""
        
        elif window_open:
            return f"""Time passes in {era_name}. The familiar routines of life here continue.

The device at your wrist pulses with energy—the window is open. You feel the pull of possibility, the chance to move on or the weight of what you've built here.

[A] Activate the time machine and leave this era behind
[B] Continue building your life here - the window will remain open a while longer
[C] Take time to reflect on your journey before deciding

<anchors>belonging[+1] legacy[+1] freedom[+1]</anchors>"""
        
        else:
            return f"""Time passes in {era_name}. Your presence here has become part of the rhythm of daily life.

Some faces are familiar now. Some doors open more easily than before. The future remains uncertain, but you've made a place for yourself, however small.

[A] Pursue the path you've been building
[B] Seek out connections you've made before
[C] Explore new possibilities in {era_name}

<anchors>belonging[+2] legacy[+1] freedom[+1]</anchors>"""
    
    def _demo_response(self, prompt: str) -> str:
        """Demo response when API unavailable - uses contextual fallback"""
        return self._contextual_fallback_response(prompt)


# =============================================================================
# GAME SAVE/LOAD MANAGER
# =============================================================================

class GameSaveManager:
    """Manages saving and loading game states"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure save directory exists"""
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except OSError:
                pass
    
    def _get_save_path(self, user_id: str, game_id: str) -> str:
        """Get path for a save file"""
        return os.path.join(self.save_dir, f"{user_id}_{game_id}.json")
    
    def _get_user_dir(self, user_id: str) -> str:
        """Get directory for user's saves"""
        return os.path.join(self.save_dir, user_id)
    
    def save_game(self, user_id: str, game_id: str, state: GameState) -> bool:
        """
        Save game state to file.
        Returns True if successful.
        """
        try:
            save_data = state.to_save_dict()
            save_data["user_id"] = user_id
            save_data["game_id"] = game_id
            
            filepath = self._get_save_path(user_id, game_id)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False
    
    def load_game(self, user_id: str, game_id: str) -> Optional[GameState]:
        """
        Load game state from file.
        Returns GameState or None if not found.
        """
        try:
            filepath = self._get_save_path(user_id, game_id)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            return GameState.from_save_dict(save_data)
        except Exception as e:
            logger.error(f"Load error: {e}")
            return None
    
    def delete_game(self, user_id: str, game_id: str) -> bool:
        """Delete a saved game"""
        try:
            filepath = self._get_save_path(user_id, game_id)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception:
            return False
    
    def list_user_games(self, user_id: str) -> List[Dict]:
        """List all saved games for a user"""
        games = []
        prefix = f"{user_id}_"
        
        try:
            for filename in os.listdir(self.save_dir):
                if filename.startswith(prefix) and filename.endswith('.json'):
                    filepath = os.path.join(self.save_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                        
                        games.append({
                            "game_id": save_data.get("game_id", ""),
                            "player_name": save_data.get("player_name", "Unknown"),
                            "phase": save_data.get("phase", "unknown"),
                            "current_era": save_data.get("current_era", {}).get("era_name", "Unknown") if save_data.get("current_era") else None,
                            "total_turns": save_data.get("time_machine", {}).get("total_turns", 0),
                            "saved_at": save_data.get("saved_at", ""),
                            "started_at": save_data.get("started_at", "")
                        })
                    except Exception:
                        continue
        except Exception:
            pass
        
        # Sort by saved_at, newest first
        games.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
        return games


# =============================================================================
# GAME API CLASS
# =============================================================================

class GameAPI:
    """
    JSON-based game API for web/mobile frontends.
    
    All methods are generators that yield message dicts.
    This allows streaming output to clients in real-time.
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.game_id = None
        self.state = GameState()
        self.narrator = None
        self.current_era = None
        self.save_manager = DatabaseSaveManager()
        
        # History tracking
        self.history = DatabaseGameHistory()
        self.current_game = None
        
        logger.info(f"GameAPI initialized for user: {user_id}")
    
    # =========================================================================
    # GAME SETUP
    # =========================================================================
    
    def start_game(self) -> Generator[Dict, None, None]:
        """Start a new game session"""
        self.game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state = GameState()
        
        logger.info(f"Starting new game: {self.game_id} for user: {self.user_id}")
        
        yield emit(MessageType.GAME_START, {
            "game_id": self.game_id,
            "user_id": self.user_id
        })
        
        yield emit(MessageType.SETUP_NAME, {
            "prompt": "What is your name, traveler?"
        })
    
    def set_player_name(self, name: str) -> Generator[Dict, None, None]:
        """Set the player's name"""
        self.state.player_name = name
        logger.debug(f"Player name set: {name}")
        
        yield emit(MessageType.INTRO_STORY, {
            "name": name,
            "story": self._get_intro_story(name)
        })
    
    def set_region(self, region: str) -> Generator[Dict, None, None]:
        """Set region preference and show items"""
        region_map = {
            'european': RegionPreference.EUROPEAN,
            'worldwide': RegionPreference.WORLDWIDE,
            'asian': RegionPreference.ASIAN,
            'african': RegionPreference.AFRICAN,
            'americas': RegionPreference.AMERICAS
        }
        self.state.region_preference = region_map.get(region.lower(), RegionPreference.WORLDWIDE)
        logger.debug(f"Region preference set: {self.state.region_preference}")
        
        yield emit(MessageType.INTRO_ITEMS, {
            "items": [
                {
                    "id": item.item_id,
                    "name": item.name,
                    "description": item.description
                }
                for item in self.state.inventory.items.values()
            ]
        })
        
        yield emit(MessageType.INTRO_DEVICE, {
            "description": "A small device is strapped to your wrist. Its surface is smooth, almost organic. A faint pulse of light suggests it's active, but you don't understand its controls."
        })
    
    def select_mode(self, mode: str) -> Generator[Dict, None, None]:
        """Set game mode (kid/mature)"""
        if mode.lower() == 'mature':
            self.state.mode = GameMode.MATURE
        else:
            self.state.mode = GameMode.KID
        
        logger.debug(f"Game mode set: {self.state.mode}")
        yield emit(MessageType.LOADING, {"message": "Preparing your journey..."})
    
    def enter_first_era(self) -> Generator[Dict, None, None]:
        """Enter the first era"""
        # Start history tracking
        self.current_game = self.history.start_game(
            user_id=self.user_id,
            game_id=self.game_id,
            player_name=self.state.player_name
        )
        
        logger.info(f"Entering first era for game: {self.game_id}")
        yield from self._enter_random_era()
    
    def _get_intro_story(self, name: str) -> str:
        """Get the intro story text"""
        return f"""You are {name}, 24 years old, living in the Bay Area.

Last week, you found something impossible: a device that manipulates time. You've tested it carefully—it works, but only backward. Only to the past.

Today, you planned a simple test. Go back three days. Verify the stock prices you wrote down. Return with proof.

But as you activate the device, something goes wrong. The readings spike. The numbers don't make sense. You try to abort, but—

The world tears apart around you.

When you can see again, nothing is familiar. The air smells wrong. The sky is the wrong color. And your device—your only way home—is dark and silent.

You are lost in time. The only way out is through."""
    
    # =========================================================================
    # ERA HANDLING
    # =========================================================================
    
    def _enter_random_era(self) -> Generator[Dict, None, None]:
        """Enter a randomly selected era"""
        # Select era based on region preference
        if self.state.region_preference == RegionPreference.EUROPEAN:
            available_eras = [e for e in ERAS if e['id'] in EUROPEAN_ERA_IDS]
        else:
            available_eras = ERAS
        
        # Filter out already visited eras if possible
        visited_ids = self.state.time_machine.eras_visited
        unvisited = [e for e in available_eras if e['id'] not in visited_ids]
        
        if unvisited:
            self.current_era = random.choice(unvisited)
        else:
            self.current_era = random.choice(available_eras)
        
        logger.info(f"Selected era: {self.current_era['name']}")
        
        # Debug override
        debug_era_id = get_debug_era_id()
        if debug_era_id:
            debug_era = get_era_by_id(debug_era_id)
            if debug_era:
                self.current_era = debug_era
                logger.info(f"DEBUG: Overriding to era {debug_era_id}")
        
        yield from self._enter_era(self.current_era)
    
    def _enter_era(self, era: dict) -> Generator[Dict, None, None]:
        """Enter a specific era"""
        # Update state
        self.state.enter_era(era)
        
        # Set up narrator for this era
        self.narrator = NarrativeEngine(self.state)
        self.narrator.set_era(era)
        
        # Record era in history
        if self.current_game:
            self.history.add_era(self.current_game, era['id'], era['name'])
        
        # Format year display
        year = era['year']
        if year < 0:
            year_str = f"{abs(year)} BCE"
        else:
            year_str = f"{year} CE"
        
        yield emit(MessageType.ERA_ARRIVAL, {
            "era_id": era['id'],
            "era_name": era['name'],
            "year": year,
            "year_display": year_str,
            "location": era['location'],
            "era_number": self.state.eras_count,
            "turn_in_era": (self.state.current_era.turns_in_era + 1) if self.state.current_era else 1,
            "time_in_era": self.state.current_era.time_in_era_description if self.state.current_era else "just arrived"
        })
        
        # Era summary for every era arrival
        yield emit(MessageType.ERA_SUMMARY, {
            "location": self.current_era['location'],
            "year_display": year_str,
            "key_events": self.current_era.get('key_events', [])[:5]
        })
        
        yield emit(MessageType.LOADING, {"message": "Arriving..."})
        
        # Generate arrival narrative
        prompt = get_arrival_prompt(self.state, self.current_era)
        response = ""
        
        # Stream the narrative - capture full response from generator
        generator = self.narrator.generate_streaming(prompt)
        try:
            while True:
                msg = next(generator)
                yield msg
        except StopIteration as e:
            response = e.value if e.value else ""
        
        if not response:
            response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
        
        # Record narrative
        if self.current_game:
            self.history.add_narrative(self.current_game, response)
        
        # Process response (with is_arrival=True to capture character name)
        self._process_response(response, is_arrival=True)
        
        # Log era arrival event
        self.state.log_event(
            "era_arrival",
            era_id=self.current_era['id'],
            era_name=self.current_era['name']
        )
        
        # Parse choices and filter (window is always closed on arrival)
        raw_choices = self._parse_choices(response)
        filtered_choices = filter_choices(
            raw_choices,
            window_open=False,
            can_stay_meaningfully=self.state.can_stay_meaningfully
        )
        
        # Store for session resume
        self.state.set_last_turn(response, filtered_choices)
        
        yield emit(MessageType.CHOICES, {
            "choices": filtered_choices,
            "can_quit": True
        })
        
        # Set phase
        self.state.phase = GamePhase.LIVING
        
        # Emit device status
        yield self._get_device_status()
        
        # Auto-save after era entry
        self.state.conversation_history = self.narrator.get_conversation_history()
        self.save_manager.save_game(self.user_id, self.game_id, self.state)
    
    # =========================================================================
    # SAVE/LOAD FUNCTIONALITY
    # =========================================================================
    
    def save_game(self) -> Generator[Dict, None, None]:
        """Save current game state"""
        if self.narrator:
            self.state.conversation_history = self.narrator.get_conversation_history()
        
        success = self.save_manager.save_game(self.user_id, self.game_id, self.state)
        
        if success:
            logger.info(f"Game saved: {self.game_id}")
            yield emit(MessageType.GAME_SAVED, {
                "game_id": self.game_id,
                "message": "Game saved successfully"
            })
        else:
            yield emit(MessageType.ERROR, {
                "message": "Failed to save game"
            })
    
    def load_game(self, game_id: str) -> Generator[Dict, None, None]:
        """Load a saved game"""
        loaded_state = self.save_manager.load_game(self.user_id, game_id)
        
        if not loaded_state:
            yield emit(MessageType.ERROR, {
                "message": f"Could not load game {game_id}"
            })
            return
        
        self.state = loaded_state
        self.game_id = game_id
        
        # Restore era
        if self.state.current_era:
            self.current_era = get_era_by_id(self.state.current_era.era_id)
            
            # Restore narrator
            self.narrator = NarrativeEngine(self.state)
            if self.current_era:
                self.narrator.set_era(self.current_era)
            
            # Restore conversation history
            if self.state.conversation_history:
                self.narrator.restore_conversation(self.state.conversation_history)
        
        logger.info(f"Game loaded: {game_id}")
        yield emit(MessageType.GAME_LOADED, {
            "game_id": game_id,
            "player_name": self.state.player_name,
            "phase": self.state.phase.value,
            "era": self.current_era['name'] if self.current_era else None,
            "total_turns": self.state.total_turns
        })
    
    def resume_game(self) -> Generator[Dict, None, None]:
        """Resume a loaded game with full context"""
        if not self.current_era:
            yield emit(MessageType.ERROR, {"message": "No game loaded to resume"})
            return
        
        # Format year display
        year = self.current_era['year']
        year_str = f"{abs(year)} BCE" if year < 0 else f"{year} CE"
        
        yield emit(MessageType.GAME_RESUMED, {
            "game_id": self.game_id,
            "player_name": self.state.player_name
        })
        
        yield emit(MessageType.ERA_ARRIVAL, {
            "era_id": self.current_era['id'],
            "era_name": self.current_era['name'],
            "year": self.current_era['year'],
            "year_display": year_str,
            "location": self.current_era['location'],
            "era_number": self.state.eras_count,
            "turn_in_era": (self.state.current_era.turns_in_era + 1) if self.state.current_era else 1,
            "time_in_era": self.state.current_era.time_in_era_description if self.state.current_era else "just arrived"
        })
        
        # Re-emit the last narrative if available
        if self.state.last_narrative:
            clean_narrative = strip_anchor_tags(self.state.last_narrative)
            clean_narrative = strip_event_tags(clean_narrative)
            
            # Remove choices from narrative for display
            lines = clean_narrative.split('\n')
            narrative_lines = []
            for line in lines:
                if not re.match(r'^\[([A-C])\]', line.strip()):
                    narrative_lines.append(line)
            
            yield emit(MessageType.NARRATIVE, {
                "text": '\n'.join(narrative_lines).strip()
            })
        
        # Re-emit choices
        if self.state.last_choices:
            window_open = self.state.time_machine.window_active
            can_stay_forever = self.state.can_stay_meaningfully and window_open
            
            yield emit(MessageType.CHOICES, {
                "choices": self.state.last_choices,
                "can_quit": not can_stay_forever,
                "window_open": window_open,
                "can_stay_forever": can_stay_forever
            })
        
        yield self._get_device_status()
    
    def list_saved_games(self) -> Generator[Dict, None, None]:
        """List all saved games for current user"""
        games = self.save_manager.list_user_games(self.user_id)
        yield emit(MessageType.USER_GAMES, {"games": games})
    
    def get_leaderboard(self, global_board: bool = True) -> Generator[Dict, None, None]:
        """Get leaderboard entries"""
        storage = DatabaseLeaderboardStorage()
        leaderboard = Leaderboard(storage)
        
        if global_board:
            entries = leaderboard.get_top_scores(20)
        else:
            entries = leaderboard.get_user_scores(self.user_id, 10)
        
        yield emit(MessageType.LEADERBOARD, {
            "entries": entries,
            "is_global": global_board
        })
    
    def get_annals(self, user_only: bool = False, limit: int = 20, offset: int = 0) -> Generator[Dict, None, None]:
        """Get Annals of Anachron entries"""
        annals = AnnalsOfAnachron()
        
        if user_only:
            entries = annals.get_user_entries(self.user_id, limit=limit)
        else:
            entries = annals.get_recent_entries(limit=limit, offset=offset)
        
        yield emit(MessageType.ANNALS, {
            "entries": [
                {
                    "entry_id": e.entry_id,
                    "player_name": e.player_name,
                    "character_name": e.character_name,
                    "title": e.title,
                    "final_era": e.final_era,
                    "final_era_year": e.final_era_year,
                    "ending_type": e.ending_type,
                    "score": e.score,
                    "created_at": e.created_at
                }
                for e in entries
            ],
            "user_only": user_only
        })
    
    def get_annals_entry(self, entry_id: str) -> Generator[Dict, None, None]:
        """Get a single Annals entry by ID"""
        annals = AnnalsOfAnachron()
        entry = annals.get_entry(entry_id)
        
        if not entry:
            yield emit(MessageType.ERROR, {"message": "Entry not found"})
            return
        
        yield emit(MessageType.ANNALS_ENTRY, {
            "entry_id": entry.entry_id,
            "player_name": entry.player_name,
            "character_name": entry.character_name,
            "title": entry.title,
            "historian_narrative": entry.historian_narrative,
            "share_text": entry.get_share_text(),
            "og_description": entry.get_og_description(),
            "created_at": entry.created_at
        })
    
    # =========================================================================
    # GAMEPLAY - CHOICE HANDLING
    # =========================================================================
    
    def make_choice(self, choice: str) -> Generator[Dict, None, None]:
        """
        Process a player choice (A, B, C, or Q).
        
        Uses intent-based resolution - the choice text determines what happens,
        not the position (A/B/C). This makes the system robust to AI generating
        choices in any order.
        """
        choice = choice.upper()
        logger.debug(f"Processing choice: {choice}")
        
        # Handle quit
        if choice == 'Q':
            yield from self._handle_quit()
            return
        
        # Validate choice ID
        if choice not in ('A', 'B', 'C'):
            yield emit(MessageType.ERROR, {"message": f"Invalid choice: {choice}"})
            return
        
        # Get intent from the stored choice text
        window_open = self.state.time_machine.window_active
        intent, choice_text = get_choice_intent_for_submission(
            choice, 
            self.state.last_choices,
            window_open
        )
        
        if intent is None:
            yield emit(MessageType.ERROR, {"message": f"Choice {choice} not found"})
            return
        
        logger.debug(f"Choice intent: {intent}, text: {choice_text[:50] if choice_text else 'none'}...")
        
        # Route based on intent
        if intent == ChoiceIntent.LEAVE_ERA:
            yield from self._handle_leaving()
            return
        
        if intent == ChoiceIntent.STAY_FOREVER:
            # Double-check eligibility (should always pass if filter worked)
            if not self.state.can_stay_meaningfully:
                yield emit(MessageType.ERROR, {
                    "message": "You haven't built enough to stay permanently."
                })
                yield from self._re_emit_choices()
                return
            yield from self._handle_stay_forever()
            return
        
        # Intent is CONTINUE_STORY - process as normal turn
        yield from self._process_story_turn(choice)
    
    def _process_story_turn(self, choice: str) -> Generator[Dict, None, None]:
        """
        Process a normal story turn (not leave/stay-forever).
        
        This handles:
        - Rolling dice
        - Advancing the turn (which may open/close window)
        - Generating narrative
        - Processing response (anchors, items)
        - Filtering and emitting choices
        """
        # Roll dice for this turn
        roll = random.randint(1, 20)
        
        # Advance turn - this may open or close the window
        events = self.state.advance_turn()
        
        yield emit(MessageType.LOADING, {"message": "The story unfolds..."})
        
        # Determine which prompt to use based on what happened
        window_just_opened = events["window_opened"]
        window_active_after_turn = events["window_active_after_turn"]
        
        if window_just_opened:
            # Window just opened - use window prompt
            self.state.phase = GamePhase.WINDOW_OPEN
            
            yield emit(MessageType.WINDOW_OPEN, {
                "message": "THE WINDOW IS OPEN",
                "can_stay_meaningfully": self.state.can_stay_meaningfully,
                "stay_message": "You've built something here. You could stay forever..." if self.state.can_stay_meaningfully else None
            })
            
            prompt = get_window_prompt(self.state, choice, roll)
            history_prefix = "[The time machine window opens]\n"
        else:
            # Normal turn - use turn prompt
            prompt = get_turn_prompt(self.state, choice, roll)
            history_prefix = ""
        
        # Generate narrative
        response = ""
        generator = self.narrator.generate_streaming(prompt)
        try:
            while True:
                msg = next(generator)
                yield msg
        except StopIteration as e:
            response = e.value if e.value else ""
        
        # Fallback if response is empty
        if not response:
            response = self.narrator.messages[-1]["content"] if self.narrator.messages else ""
            logger.warning("Empty response from generator - using last message fallback")
        
        # Record narrative
        if self.current_game:
            self.history.add_narrative(self.current_game, history_prefix + response)
        
        # Process response (anchors, items) - this may change can_stay_meaningfully
        self._process_response(response)
        
        # Parse choices from AI response
        raw_choices = self._parse_choices(response)
        
        # Filter choices - remove stay_forever if not eligible
        # This is the safety layer in case AI generated invalid options
        filtered_choices = filter_choices(
            raw_choices,
            window_active_after_turn,
            self.state.can_stay_meaningfully
        )
        
        # Log if we got no valid choices (indicates a problem)
        if not filtered_choices:
            logger.error(f"No valid choices parsed from response. Response length: {len(response)}")
            logger.debug(f"Raw response: {response[:500]}...")
        
        # Store filtered choices for next submission
        self.state.set_last_turn(response, filtered_choices)
        
        # Determine if quit should be available
        # Hide quit when stay_forever is an option (to avoid confusion)
        can_stay_forever = self.state.can_stay_meaningfully and window_active_after_turn
        can_quit = not can_stay_forever
        
        # Emit choices to frontend
        yield emit(MessageType.CHOICES, {
            "choices": filtered_choices,
            "can_quit": can_quit,
            "window_open": window_active_after_turn,
            "can_stay_forever": can_stay_forever
        })
        
        # Emit window status messages
        if not window_just_opened:
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
        
        # Auto-save after each turn
        if self.narrator:
            self.state.conversation_history = self.narrator.get_conversation_history()
        self.save_manager.save_game(self.user_id, self.game_id, self.state)
    
    def _re_emit_choices(self) -> Generator[Dict, None, None]:
        """Re-emit the current choices after an error."""
        window_open = self.state.time_machine.window_active
        can_stay_forever = self.state.can_stay_meaningfully and window_open
        
        yield emit(MessageType.CHOICES, {
            "choices": self.state.last_choices,
            "can_quit": not can_stay_forever,
            "window_open": window_open,
            "can_stay_forever": can_stay_forever
        })
    
    def get_current_state(self) -> Dict:
        """Get the current game state for frontend rendering"""
        return {
            "game_id": self.game_id,
            "user_id": self.user_id,
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
            "eras_visited": self.state.eras_count,
            "fulfillment": {
                "belonging": self.state.fulfillment.belonging.value,
                "legacy": self.state.fulfillment.legacy.value,
                "freedom": self.state.fulfillment.freedom.value
            },
            "last_api_error": self.narrator.last_error if self.narrator else None
        }
    
    # =========================================================================
    # SPECIAL ACTIONS
    # =========================================================================
    
    def _handle_leaving(self) -> Generator[Dict, None, None]:
        """Handle player choosing to leave the era"""
        self.state.choose_to_travel()
        
        logger.info(f"Player leaving era: {self.current_era['name'] if self.current_era else 'unknown'}")
        
        yield emit(MessageType.DEPARTURE, {
            "message": "You activate the device...",
            "from_era": self.current_era['name'] if self.current_era else None
        })
        
        # Generate departure narrative
        prompt = get_leaving_prompt(self.state)
        response = self.narrator.generate(prompt)
        
        # Record in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[You activate the time machine]\n" + response)
        
        yield emit(MessageType.NARRATIVE, {"text": response})
        
        yield emit(MessageType.WAITING_INPUT, {
            "prompt": "continue",
            "message": "Press continue to see where you land..."
        })
    
    def continue_to_next_era(self) -> Generator[Dict, None, None]:
        """Continue to the next era after departure"""
        yield from self._enter_random_era()
    
    def _handle_stay_forever(self) -> Generator[Dict, None, None]:
        """Handle player choosing to stay forever"""
        self.state.choose_to_stay(is_final=True)
        
        logger.info(f"Player staying forever in: {self.current_era['name'] if self.current_era else 'unknown'}")
        
        yield emit(MessageType.STAYING_FOREVER, {
            "message": "You've chosen to make this your home...",
            "era": self.current_era['name'] if self.current_era else None
        })
        
        # Generate staying ending
        prompt = get_staying_ending_prompt(self.state, self.current_era)
        response = self.narrator.generate(prompt)
        
        # Record in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[You choose to stay forever]\n" + response)
        
        # Store the ending narrative
        self.state.ending_narrative = response
        
        yield emit(MessageType.ENDING_NARRATIVE, {"text": response})
        
        # End game
        self.state.end_game()
        
        yield emit(MessageType.WAITING_INPUT, {
            "prompt": "continue",
            "message": "Press continue to see your final score..."
        })
    
    def continue_to_score(self) -> Generator[Dict, None, None]:
        """Show the final score after viewing the ending narrative"""
        yield from self._show_final_score()
    
    def _handle_quit(self) -> Generator[Dict, None, None]:
        """Handle player quitting the game"""
        logger.info(f"Player quitting game: {self.game_id}")
        
        yield emit(MessageType.NARRATIVE, {
            "text": "You set down the device.\nSome journeys end before the destination is found."
        })
        
        # Generate quit ending narrative
        prompt = get_quit_ending_prompt(self.state, self.current_era)
        response = self.narrator.generate(prompt)
        
        # Store the ending narrative
        self.state.ending_narrative = response
        
        # Record in history
        if self.current_game:
            self.history.add_narrative(self.current_game, "[Journey abandoned]\n" + response)
        
        yield emit(MessageType.ENDING_NARRATIVE, {"text": response})
        
        # End the game
        self.state.end_game()
        
        yield emit(MessageType.WAITING_INPUT, {
            "prompt": "continue",
            "message": "Press continue to see your final score..."
        })
    
    def _show_final_score(self, ending_type_override: str = None) -> Generator[Dict, None, None]:
        """Calculate and display final score"""
        # Calculate score - pass user_id and game_id so they're included in the Score object
        score = calculate_score(
            self.state,
            ending_type_override or self.state.ending_type,
            user_id=self.user_id,
            game_id=self.game_id
        )
        
        # Add ending narrative to score if available
        score.ending_narrative = self.state.ending_narrative
        
        # Update final_era in score object
        if self.current_era:
            score.final_era = self.current_era['name']
        
        # Save to leaderboard - pass the Score object, not keyword arguments
        storage = DatabaseLeaderboardStorage()
        leaderboard = Leaderboard(storage)
        
        rank = leaderboard.add_score(score)
        
        # Record final game stats in history
        if self.current_game:
            self.history.end_game(
                self.current_game,
                score=score
            )
        
        # Try to create Annals of Anachron entry
        aoa_data = None
        try:
            annals = AnnalsOfAnachron()
            can_add, reason = annals.can_add_entry(self.state, score)
            
            if can_add:
                # Generate historian narrative for the entry
                historian_prompt = get_historian_narrative_prompt(self.state, self.current_era, score)
                historian_narrative = self.narrator.generate(historian_prompt)
                
                # Create entry
                aoa_entry = annals.create_entry(
                    user_id=self.user_id,
                    game_state=self.state,
                    score=score,
                    era=self.current_era,
                    historian_narrative=historian_narrative
                )
                
                if aoa_entry:
                    aoa_data = {
                        "qualified": True,
                        "entry_id": aoa_entry.entry_id,
                        "title": aoa_entry.title,
                        "share_text": aoa_entry.get_share_text(),
                        "historian_narrative": aoa_entry.historian_narrative,
                        "character_name": aoa_entry.character_name,
                        "final_era": aoa_entry.final_era,
                        "final_era_year": aoa_entry.final_era_year
                    }
            else:
                aoa_data = {
                    "qualified": False,
                    "reason": reason
                }
        except Exception as e:
            # Don't fail the whole score display if AoA fails
            logger.error(f"AoA entry creation failed: {e}")
            aoa_data = {
                "qualified": False,
                "reason": "Error creating entry"
            }
        
        # Build response data
        response_data = {
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
            "summary": score.get_narrative_summary(),
            "blurb": score.get_blurb(),
            "final_era": score.final_era,
            "ending_narrative": strip_event_tags(score.ending_narrative) if score.ending_narrative else None
        }
        
        # Add AoA data if available
        if aoa_data:
            response_data["annals"] = aoa_data
        
        yield emit(MessageType.FINAL_SCORE, response_data)
    
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
        
        if self.state.current_era:
            status_data["era_number"] = self.state.eras_count
            status_data["turn_in_era"] = self.state.current_era.turns_in_era + 1
            status_data["time_in_era"] = self.state.current_era.time_in_era_description
        
        return emit(MessageType.DEVICE_STATUS, status_data)
    
    def _process_response(self, response: str, is_arrival: bool = False):
        """Process AI response - extract anchors, items, and log events"""
        # Parse anchor adjustments
        adjustments = parse_anchor_adjustments(response)
        for anchor, delta in adjustments.items():
            if delta != 0:
                self.state.fulfillment.adjust(anchor, delta, "choice")
        
        # Check for defining moment (large anchor shift)
        defining = check_defining_moment(adjustments)
        if defining:
            anchor_name, delta = defining
            self.state.log_event(
                "defining_moment",
                anchor=anchor_name,
                delta=delta
            )
        
        # Parse item usage
        used_items = parse_item_usage(response, self.state.inventory)
        for item_id in used_items:
            self.state.inventory.use_item(item_id)
            self.state.log_event("item_use", item_id=item_id)
        
        # Parse character name (primarily on arrival)
        if is_arrival:
            char_name = parse_character_name(response)
            if char_name:
                if self.state.current_era:
                    self.state.current_era.character_name = char_name
                self.state.log_event("character_named", name=char_name)
        
        # Parse key NPCs
        npcs = parse_key_npcs(response)
        for npc_name in npcs:
            self.state.log_event("relationship", name=npc_name)
        
        # Parse wisdom moments
        wisdom_id = parse_wisdom_moment(response)
        if wisdom_id:
            self.state.log_event("wisdom", id=wisdom_id)
        
        # Store turn event in era state
        if self.state.current_era:
            self.state.current_era.events.append(f"Turn {self.state.current_era.turns_in_era}")
    
    def _parse_choices(self, response: str) -> List[Dict]:
        """Extract choices from response"""
        # Strip both anchor tags and event tags
        clean_response = strip_anchor_tags(response)
        clean_response = strip_event_tags(clean_response)
        
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
    
    def __init__(self, user_id: str = "default"):
        self.api = GameAPI(user_id=user_id)
    
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
    
    def continue_to_score(self) -> List[Dict]:
        """Continue to show final score after ending narrative"""
        return list(self.api.continue_to_score())
    
    def get_state(self) -> Dict:
        """Get current state"""
        return self.api.get_current_state()
    
    def save(self) -> List[Dict]:
        """Save current game"""
        return list(self.api.save_game())
    
    def load(self, game_id: str) -> List[Dict]:
        """Load a saved game"""
        return list(self.api.load_game(game_id))
    
    def resume(self) -> List[Dict]:
        """Resume loaded game with full context"""
        return list(self.api.resume_game())
    
    def list_saves(self) -> List[Dict]:
        """List saved games"""
        return list(self.api.list_saved_games())
    
    def leaderboard(self, global_board: bool = True) -> List[Dict]:
        """Get leaderboard"""
        return list(self.api.get_leaderboard(global_board))
    
    def annals(self, user_only: bool = False, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get Annals of Anachron entries"""
        return list(self.api.get_annals(user_only, limit, offset))
    
    def annals_entry(self, entry_id: str) -> List[Dict]:
        """Get a single Annals entry"""
        return list(self.api.get_annals_entry(entry_id))
