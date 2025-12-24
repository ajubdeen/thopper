"""
Time Hopper - Scoring Module

Tracks player score invisibly during gameplay, calculates final score,
and manages the leaderboard.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class Score:
    """
    Player's score breakdown.
    
    Scoring:
    - Survival: 10 points per turn survived
    - Belonging: 0-100 based on final fulfillment
    - Legacy: 0-100 based on final fulfillment
    - Freedom: 0-100 based on final fulfillment
    - Exploration: 50 points per era visited
    - Ending Bonus: Based on ending type (complete=200, balanced=150, single anchor=100, searching=50)
    """
    
    turns_survived: int = 0
    eras_visited: int = 0
    belonging_score: int = 0
    legacy_score: int = 0
    freedom_score: int = 0
    ending_type: str = "searching"
    
    # Metadata
    player_name: str = ""
    final_era: str = ""
    timestamp: str = ""
    
    @property
    def survival_points(self) -> int:
        """Points from surviving turns"""
        return self.turns_survived * 10
    
    @property
    def exploration_points(self) -> int:
        """Points from visiting different eras"""
        return self.eras_visited * 50
    
    @property
    def fulfillment_points(self) -> int:
        """Points from fulfillment anchors"""
        return self.belonging_score + self.legacy_score + self.freedom_score
    
    @property
    def ending_bonus(self) -> int:
        """Bonus points based on ending type"""
        bonuses = {
            "complete": 200,      # All three anchors high
            "balanced": 150,      # Two anchors high
            "belonging": 100,     # Found community
            "legacy": 100,        # Built something lasting
            "freedom": 100,       # Found independence
            "searching": 50,      # Chose to stay without fulfillment
            "abandoned": 25       # Quit before finding happiness
        }
        return bonuses.get(self.ending_type, 25)
    
    @property
    def total(self) -> int:
        """Total score"""
        return (self.survival_points + self.exploration_points + 
                self.fulfillment_points + self.ending_bonus)
    
    def get_breakdown_display(self) -> str:
        """Get formatted score breakdown for display"""
        lines = []
        lines.append("═" * 40)
        lines.append("           FINAL SCORE")
        lines.append("═" * 40)
        lines.append("")
        lines.append(f"  Survival ({self.turns_survived} turns × 10)    {self.survival_points:>6}")
        lines.append(f"  Exploration ({self.eras_visited} eras × 50)   {self.exploration_points:>6}")
        lines.append("")
        lines.append("  Fulfillment:")
        lines.append(f"    Belonging                    {self.belonging_score:>6}")
        lines.append(f"    Legacy                       {self.legacy_score:>6}")
        lines.append(f"    Freedom                      {self.freedom_score:>6}")
        lines.append("")
        lines.append(f"  Ending Bonus ({self.ending_type})".ljust(33) + f"{self.ending_bonus:>6}")
        lines.append("")
        lines.append("─" * 40)
        lines.append(f"  TOTAL                          {self.total:>6}")
        lines.append("═" * 40)
        return "\n".join(lines)
    
    def get_narrative_summary(self) -> str:
        """Generate a narrative summary of the player's journey"""
        
        # Survival narrative
        if self.turns_survived < 10:
            survival_text = "A brief journey through time"
        elif self.turns_survived < 30:
            survival_text = "Several years spent across history"
        elif self.turns_survived < 50:
            survival_text = "Decades of experience in other eras"
        else:
            survival_text = "A lifetime's worth of temporal wandering"
        
        # Exploration narrative
        if self.eras_visited == 1:
            explore_text = "finding your place in a single era"
        elif self.eras_visited <= 3:
            explore_text = f"passing through {self.eras_visited} different periods of history"
        else:
            explore_text = f"an extensive tour across {self.eras_visited} distinct eras"
        
        # Fulfillment narrative
        high_anchors = []
        if self.belonging_score >= 60:
            high_anchors.append("community")
        if self.legacy_score >= 60:
            high_anchors.append("lasting impact")
        if self.freedom_score >= 60:
            high_anchors.append("personal freedom")
        
        # For abandoned games, skip the fulfillment text
        if self.ending_type == "abandoned":
            fulfillment_text = "The search continues elsewhere—or perhaps it doesn't."
        elif len(high_anchors) == 3:
            fulfillment_text = "You achieved the rare trifecta: belonging, legacy, and freedom."
        elif len(high_anchors) == 2:
            fulfillment_text = f"You found {high_anchors[0]} and {high_anchors[1]}."
        elif len(high_anchors) == 1:
            fulfillment_text = f"Above all, you found {high_anchors[0]}."
        else:
            fulfillment_text = "You chose to stay, seeking what fulfillment might come."
        
        # Ending narrative
        ending_texts = {
            "complete": "Your journey ended in completeness—a full life, fully lived.",
            "balanced": "You found balance, if not perfection. A life well-chosen.",
            "belonging": "In the end, it was people who made a place worth staying.",
            "legacy": "You built something that would outlast you. That was enough.",
            "freedom": "You found freedom on your own terms. Unburdened at last.",
            "searching": "Perhaps happiness would find you yet, in this new home.",
            "abandoned": "Your journey ended before you found what you were seeking."
        }
        ending_text = ending_texts.get(self.ending_type, ending_texts["searching"])
        
        return f"""{survival_text}, {explore_text}.

{fulfillment_text}

{ending_text}"""
    
    def get_blurb(self) -> str:
        """Generate a short blurb for leaderboard display"""
        if self.ending_type == "abandoned":
            return f"Quit in {self.final_era}"
        elif self.ending_type == "complete":
            return f"Found happiness in {self.final_era}"
        elif self.ending_type in ["belonging", "legacy", "freedom"]:
            return f"Stayed in {self.final_era} ({self.ending_type})"
        elif self.ending_type == "balanced":
            return f"Found balance in {self.final_era}"
        else:
            return f"Settled in {self.final_era}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            "player_name": self.player_name,
            "total": self.total,
            "turns_survived": self.turns_survived,
            "eras_visited": self.eras_visited,
            "belonging_score": self.belonging_score,
            "legacy_score": self.legacy_score,
            "freedom_score": self.freedom_score,
            "ending_type": self.ending_type,
            "final_era": self.final_era,
            "timestamp": self.timestamp,
            "blurb": self.get_blurb()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Score':
        """Create from dictionary"""
        return cls(
            player_name=data.get("player_name", "Unknown"),
            turns_survived=data.get("turns_survived", 0),
            eras_visited=data.get("eras_visited", 0),
            belonging_score=data.get("belonging_score", 0),
            legacy_score=data.get("legacy_score", 0),
            freedom_score=data.get("freedom_score", 0),
            ending_type=data.get("ending_type", "searching"),
            final_era=data.get("final_era", "Unknown"),
            timestamp=data.get("timestamp", "")
        )


class Leaderboard:
    """Manages high scores across games"""
    
    def __init__(self, filepath: str = "leaderboard.json"):
        self.filepath = filepath
        self.scores: List[dict] = []
        self._load()
    
    def _load(self):
        """Load leaderboard from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.scores = []
        else:
            self.scores = []
    
    def _save(self):
        """Save leaderboard to file"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save
    
    def add_score(self, score: Score) -> int:
        """
        Add a score to the leaderboard.
        Returns the rank (1-indexed).
        """
        score_dict = score.to_dict()
        self.scores.append(score_dict)
        
        # Sort by total score descending
        self.scores.sort(key=lambda x: x.get("total", 0), reverse=True)
        
        # Keep only top 100
        self.scores = self.scores[:100]
        
        self._save()
        
        # Find rank
        for i, s in enumerate(self.scores):
            if s["timestamp"] == score_dict["timestamp"] and s["player_name"] == score_dict["player_name"]:
                return i + 1
        return len(self.scores)
    
    def get_top_scores(self, n: int = 10) -> List[dict]:
        """Get top N scores"""
        return self.scores[:n]
    
    def get_display(self, highlight_score: Optional[Score] = None) -> str:
        """Get formatted leaderboard display"""
        lines = []
        lines.append("═" * 60)
        lines.append("                    LEADERBOARD")
        lines.append("═" * 60)
        lines.append("")
        
        top_scores = self.get_top_scores(10)
        
        if not top_scores:
            lines.append("  No scores yet. You're the first!")
        else:
            for i, s in enumerate(top_scores):
                rank = i + 1
                name = s.get("player_name", "Unknown")[:16].ljust(16)
                total = s.get("total", 0)
                blurb = s.get("blurb", "")[:40]
                
                # Highlight current score if provided
                marker = ""
                if highlight_score and s.get("timestamp") == highlight_score.timestamp:
                    marker = " ◀"
                
                lines.append(f"  {rank:>2}. {name}   {total:>5} pts{marker}")
                if blurb:
                    lines.append(f"      {blurb}")
                lines.append("")
        
        lines.append("═" * 60)
        return "\n".join(lines)


def calculate_score(game_state, ending_type_override: str = None) -> Score:
    """Calculate the final score from game state
    
    Args:
        game_state: The current game state
        ending_type_override: If provided, use this instead of calculating from fulfillment
                              (e.g., "abandoned" when player quits)
    """
    
    # Get values from game state
    turns = game_state.time_machine.total_turns
    eras = len(game_state.time_machine.eras_visited)
    
    # Get fulfillment scores (they're 0-100, stored in Anchor objects)
    belonging = game_state.fulfillment.belonging.value
    legacy = game_state.fulfillment.legacy.value
    freedom = game_state.fulfillment.freedom.value
    
    # Get ending type (use override if provided)
    if ending_type_override:
        ending_type = ending_type_override
    else:
        ending_type = game_state.fulfillment.get_ending_type()
    
    # Create score
    score = Score(
        turns_survived=turns,
        eras_visited=eras,
        belonging_score=belonging,
        legacy_score=legacy,
        freedom_score=freedom,
        ending_type=ending_type,
        player_name=game_state.player_name,
        final_era=game_state.current_era.era_name if game_state.current_era else "Unknown",
        timestamp=datetime.now().isoformat()
    )
    
    return score


class GameHistory:
    """
    Stores the full narrative history of each playthrough.
    Saved to game_history.json for players to revisit their stories.
    """
    
    def __init__(self, filepath: str = "game_history.json"):
        self.filepath = filepath
        self.games: List[dict] = []
        self._load()
    
    def _load(self):
        """Load history from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.games = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.games = []
        else:
            self.games = []
    
    def _save(self):
        """Save history to file"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silently fail if can't save
    
    def start_new_game(self, player_name: str) -> dict:
        """Create a new game record and return it"""
        game = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "player_name": player_name,
            "started_at": datetime.now().isoformat(),
            "ended_at": None,
            "eras": [],  # List of era records
            "current_era_narrative": [],  # Narrative chunks for current era
            "final_score": None,
            "ending_type": None,
            "blurb": None
        }
        return game
    
    def add_narrative(self, game: dict, text: str):
        """Add a narrative chunk to the current era"""
        game["current_era_narrative"].append(text)
    
    def start_era(self, game: dict, era_name: str, era_year: int, era_location: str):
        """Start recording a new era"""
        # Save previous era if exists
        if game["current_era_narrative"]:
            if game["eras"]:
                game["eras"][-1]["narrative"] = "\n\n".join(game["current_era_narrative"])
        
        # Start new era record
        game["eras"].append({
            "era_name": era_name,
            "era_year": era_year,
            "era_location": era_location,
            "narrative": ""
        })
        game["current_era_narrative"] = []
    
    def end_game(self, game: dict, score: Score):
        """Finalize the game record"""
        # Save final era narrative
        if game["current_era_narrative"] and game["eras"]:
            game["eras"][-1]["narrative"] = "\n\n".join(game["current_era_narrative"])
        
        game["ended_at"] = datetime.now().isoformat()
        game["final_score"] = score.to_dict()
        game["ending_type"] = score.ending_type
        game["blurb"] = score.get_blurb()
        
        # Add to history
        self.games.append(game)
        self._save()
    
    def get_game_summary(self, game: dict) -> str:
        """Get a readable summary of a game"""
        lines = []
        lines.append(f"═══ {game['player_name']}'s Journey ═══")
        lines.append(f"Started: {game['started_at'][:10]}")
        
        if game['final_score']:
            lines.append(f"Score: {game['final_score'].get('total', 0)} pts")
            lines.append(f"Ending: {game.get('blurb', 'Unknown')}")
        
        lines.append("")
        lines.append("Eras Visited:")
        for era in game.get('eras', []):
            year = era.get('era_year', 0)
            year_str = f"{abs(year)} BCE" if year < 0 else f"{year} CE"
            lines.append(f"  • {era.get('era_name', 'Unknown')} ({year_str})")
        
        return "\n".join(lines)
    
    def get_full_story(self, game_id: str) -> Optional[str]:
        """Get the full narrative of a specific game"""
        for game in self.games:
            if game.get('id') == game_id:
                lines = []
                lines.append("═" * 60)
                lines.append(f"  THE JOURNEY OF {game['player_name'].upper()}")
                lines.append("═" * 60)
                lines.append("")
                
                for era in game.get('eras', []):
                    year = era.get('era_year', 0)
                    year_str = f"{abs(year)} BCE" if year < 0 else f"{year} CE"
                    
                    lines.append(f"━━━ {era.get('era_name', 'Unknown')} ({year_str}) ━━━")
                    lines.append("")
                    lines.append(era.get('narrative', '[No narrative recorded]'))
                    lines.append("")
                    lines.append("")
                
                if game.get('final_score'):
                    lines.append("═" * 60)
                    lines.append(f"  Final Score: {game['final_score'].get('total', 0)}")
                    lines.append(f"  {game.get('blurb', '')}")
                    lines.append("═" * 60)
                
                return "\n".join(lines)
        
        return None
    
    def list_games(self) -> str:
        """List all saved games"""
        if not self.games:
            return "No saved games yet."
        
        lines = []
        lines.append("═" * 60)
        lines.append("               SAVED JOURNEYS")
        lines.append("═" * 60)
        lines.append("")
        
        for i, game in enumerate(reversed(self.games[-20:])):  # Last 20 games, newest first
            score = game.get('final_score', {}).get('total', 0)
            date = game.get('started_at', '')[:10]
            name = game.get('player_name', 'Unknown')
            blurb = game.get('blurb', 'Unknown ending')
            game_id = game.get('id', '')
            
            lines.append(f"  [{game_id}] {name} - {score} pts")
            lines.append(f"      {date} | {blurb}")
            lines.append("")
        
        lines.append("═" * 60)
        lines.append("  To read a story, open game_history.json")
        lines.append("═" * 60)
        
        return "\n".join(lines)
