"""
Anachron - Game State Module

Central game state that coordinates all systems:
- Time machine
- Fulfillment anchors
- Inventory
- Era and narrative state
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from config import MODES, TURNS_PER_YEAR
from time_machine import TimeMachine, DeviceState
from fulfillment import FulfillmentState
from items import Inventory


class GameMode(Enum):
    KID = "kid"
    MATURE = "mature"


class RegionPreference(Enum):
    EUROPEAN = "european"      # European/Western eras only
    WORLDWIDE = "worldwide"    # All eras


class GamePhase(Enum):
    """Current phase of the game"""
    SETUP = "setup"             # Initial setup
    ARRIVAL = "arrival"         # Just arrived in new era
    LIVING = "living"           # Normal gameplay in era
    WINDOW_OPEN = "window_open" # Time machine window is active
    STAYING = "staying"         # Chose to stay, playing out ending
    TRAVELING = "traveling"     # Using window to leave
    ENDED = "ended"             # Game complete


@dataclass
class EraState:
    """State for the current era"""
    
    era_id: str
    era_name: str
    era_year: int
    era_location: str
    
    turns_in_era: int = 0
    character_name: Optional[str] = None
    
    # Relationships built (for narrative continuity)
    relationships: List[Dict] = field(default_factory=list)
    
    # Key events that have happened
    events: List[str] = field(default_factory=list)
    
    # Player's current situation summary
    situation: str = ""
    
    def advance_turn(self):
        self.turns_in_era += 1
    
    @property
    def time_in_era_description(self) -> str:
        """Human-readable time spent in era"""
        turns = self.turns_in_era
        
        # 7 turns = 1 year, so each turn is ~7-8 weeks
        if turns == 0:
            return "just arrived"
        elif turns == 1:
            return "a few weeks"
        elif turns == 2:
            return "a couple months"
        elif turns <= 4:
            return "several months"
        elif turns <= 6:
            return "most of a year"
        elif turns <= 7:
            return "about a year"
        elif turns <= 14:
            return f"about {turns // 7} years"
        else:
            years = turns // 7
            return f"over {years} years"


@dataclass
class GameState:
    """
    Complete game state.
    
    This is the single source of truth for the entire game.
    """
    
    # Core systems
    time_machine: TimeMachine = field(default_factory=TimeMachine)
    fulfillment: FulfillmentState = field(default_factory=FulfillmentState)
    inventory: Inventory = field(default_factory=Inventory)
    
    # Current era
    current_era: Optional[EraState] = None
    
    # Game settings
    mode: GameMode = GameMode.KID
    region_preference: RegionPreference = RegionPreference.WORLDWIDE
    player_name: str = ""
    
    # Phase tracking
    phase: GamePhase = GamePhase.SETUP
    
    # History across eras
    era_history: List[Dict] = field(default_factory=list)
    
    # Timestamps
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Ending info
    ending_type: Optional[str] = None
    final_era: Optional[str] = None
    
    def start_game(self, player_name: str, mode: GameMode, region: RegionPreference = RegionPreference.WORLDWIDE):
        """Initialize a new game"""
        self.player_name = player_name
        self.mode = mode
        self.region_preference = region
        self.started_at = datetime.now()
        self.phase = GamePhase.SETUP
        self.inventory = Inventory.create_starting()
    
    def enter_era(self, era: Dict):
        """Enter a new era"""
        # Save previous era to history if exists
        if self.current_era:
            self._save_era_to_history()
        
        # Create new era state
        self.current_era = EraState(
            era_id=era["id"],
            era_name=era["name"],
            era_year=era["year"],
            era_location=era["location"]
        )
        
        # Handle fulfillment transition if not first era
        if self.era_history:
            self.fulfillment.transition_to_new_era()
        
        # IMPORTANT: Close the window and reset turns when entering new era
        # This ensures window is always closed on arrival
        self.time_machine.window_active = False
        self.time_machine.window_turns_remaining = 0
        self.time_machine.turns_since_last_window = 0
        self.time_machine._accumulated_probability = 0.0
        
        # Track era if not already tracked (travel() may have added it)
        if era["id"] not in self.time_machine.eras_visited:
            self.time_machine.eras_visited.append(era["id"])
        
        self.phase = GamePhase.ARRIVAL
    
    def advance_turn(self) -> Dict[str, Any]:
        """
        Advance one turn and return events that occurred.
        
        Returns dict with:
        - window_opened: bool
        - window_closing: bool (last turn of window)
        - window_closed: bool
        """
        events = {
            "window_opened": False,
            "window_closing": False,
            "window_closed": False
        }
        
        if self.current_era:
            self.current_era.advance_turn()
        
        self.fulfillment.advance_turn()
        
        # Check time machine
        was_active = self.time_machine.window_active
        window_opened = self.time_machine.advance_turn()
        
        if window_opened:
            events["window_opened"] = True
            self.phase = GamePhase.WINDOW_OPEN
        elif was_active and not self.time_machine.window_active:
            events["window_closed"] = True
            self.phase = GamePhase.LIVING
        elif self.time_machine.window_active and self.time_machine.window_turns_remaining == 1:
            events["window_closing"] = True
        
        return events
    
    def choose_to_stay(self, is_final: bool = False):
        """Player chooses to stay in current era"""
        if is_final:
            # This is the final staying - end game
            self.phase = GamePhase.STAYING
            self.ending_type = self.fulfillment.get_ending_type()
            self.final_era = self.current_era.era_id if self.current_era else None
        else:
            # Just letting window close
            self.time_machine.choose_to_stay()
            self.phase = GamePhase.LIVING
    
    def choose_to_travel(self):
        """Player chooses to use the window"""
        self.phase = GamePhase.TRAVELING
    
    def complete_travel(self, new_era: Dict):
        """Complete travel to new era"""
        self.time_machine.travel(new_era["id"])
        self.enter_era(new_era)
    
    def end_game(self):
        """Finalize game ending"""
        self._save_era_to_history()
        self.phase = GamePhase.ENDED
        self.ended_at = datetime.now()
    
    def _save_era_to_history(self):
        """Save current era state to history"""
        if not self.current_era:
            return
        
        self.era_history.append({
            "era_id": self.current_era.era_id,
            "era_name": self.current_era.era_name,
            "turns": self.current_era.turns_in_era,
            "character_name": self.current_era.character_name,
            "relationships": self.current_era.relationships.copy(),
            "events": self.current_era.events.copy(),
            "fulfillment_snapshot": {
                "belonging": self.fulfillment.belonging.value,
                "legacy": self.fulfillment.legacy.value,
                "freedom": self.fulfillment.freedom.value
            }
        })
    
    @property
    def can_stay_meaningfully(self) -> bool:
        """Has player built enough to make staying meaningful?"""
        return self.fulfillment.can_stay
    
    @property
    def total_turns(self) -> int:
        """Total turns across all eras"""
        return self.time_machine.total_turns
    
    @property
    def eras_count(self) -> int:
        """Number of eras visited"""
        return len(self.time_machine.eras_visited)
    
    def get_narrative_context(self) -> Dict:
        """
        Get full context for AI narrator.
        This is what the AI uses to generate responses.
        """
        return {
            "mode": self.mode.value,
            "player_name": self.player_name,
            "current_era": {
                "id": self.current_era.era_id,
                "name": self.current_era.era_name,
                "year": self.current_era.era_year,
                "location": self.current_era.era_location,
                "turns": self.current_era.turns_in_era,
                "time_description": self.current_era.time_in_era_description,
                "character_name": self.current_era.character_name,
                "relationships": self.current_era.relationships,
                "recent_events": self.current_era.events[-5:] if self.current_era.events else []
            } if self.current_era else None,
            "items": self.inventory.to_narrative_dict(),
            "fulfillment": self.fulfillment.get_narrative_state(),
            "time_machine": {
                "indicator": self.time_machine.indicator.value,
                "window_active": self.time_machine.window_active,
                "window_turns_remaining": self.time_machine.window_turns_remaining,
                "eras_visited_count": len(self.time_machine.eras_visited),
            },
            "phase": self.phase.value,
            "can_stay_meaningfully": self.can_stay_meaningfully,
            "era_history_summary": [
                {"era": h["era_name"], "turns": h["turns"]} 
                for h in self.era_history
            ]
        }
    
    def to_save_dict(self) -> Dict:
        """Serialize state for saving"""
        # Implementation for save/load feature
        pass
    
    @classmethod
    def from_save_dict(cls, data: Dict) -> "GameState":
        """Deserialize state from save"""
        # Implementation for save/load feature
        pass
