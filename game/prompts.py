"""
Anachron - Prompts Module

AI prompts for the narrative system, updated for:
- Fulfillment anchors (invisible tracking)
- Time machine windows
- Modern items
- Multi-era journeys
- Event tracking for enhanced endings
"""

from game_state import GameState, GameMode, GamePhase
from items import get_items_prompt_section
from fulfillment import get_anchor_detection_prompt
from event_parsing import get_event_tracking_prompt


def get_system_prompt(game_state: GameState, era: dict) -> str:
    """
    Generate the system prompt for the AI narrator.
    
    This sets up the entire context and rules for narrative generation.
    """
    
    mode_config = {
        GameMode.KID: {
            "tone": """
TONE: Educational game for ages 11+. Keep content appropriate:
- Death and hardship: YES (framed respectfully)
- Violence: Consequences shown, not graphic descriptions
- Historical injustice: YES (honest about reality, focus on humanity)
- Sexual content: NO
- Gratuitous gore: NO
- Profanity: NO""",
        },
        GameMode.MATURE: {
            "tone": """
TONE: Mature mode (18+) - unflinching historical realism:
- Violence: Graphic when historically accurate
- Death: Specific, visceral, how people actually died
- Sexual content: Reference survival situations, imply rather than depict
- Language: Period-appropriate including slurs
- Psychological: Despair, trauma, moral injury fully explored
- NEVER depict sexual violence in detail - acknowledge its reality
- Do NOT sanitize history""",
        }
    }
    
    mode = mode_config[game_state.mode]
    
    # Build hard rules section
    hard_rules = era.get('hard_rules', {})
    hard_rules_text = ""
    for category, rules in hard_rules.items():
        hard_rules_text += f"\n{category}:\n"
        for rule in rules:
            hard_rules_text += f"  - {rule}\n"
    
    # Add adult hard rules in mature mode
    if game_state.mode == GameMode.MATURE and 'adult_hard_rules' in era:
        for category, rules in era['adult_hard_rules'].items():
            hard_rules_text += f"\n{category} (mature):\n"
            for rule in rules:
                hard_rules_text += f"  - {rule}\n"
    
    # Events
    events = era.get('key_events', [])
    if game_state.mode == GameMode.MATURE and 'adult_events' in era:
        events = events + era.get('adult_events', [])
    events_text = "\n".join(f"  - {e}" for e in events)
    
    # Figures
    figures_text = "\n".join(f"  - {f}" for f in era.get('figures', []))
    
    # Items section
    items_section = get_items_prompt_section(game_state.inventory)
    
    # Anchor detection (hidden from player)
    anchor_prompt = get_anchor_detection_prompt()
    
    # Event tracking (hidden from player)
    event_prompt = get_event_tracking_prompt()
    
    # Era history for context
    era_history = ""
    if game_state.era_history:
        era_history = "\nPREVIOUS ERAS (for emotional weight):\n"
        for h in game_state.era_history:
            era_history += f"  - {h['era_name']}: spent {h['turns']} turns, character was {h.get('character_name', 'unnamed')}\n"
        era_history += "\nThe player has LEFT people behind. Each new era should feel like starting over."
    
    # Fulfillment state (qualitative only)
    fs = game_state.fulfillment.get_narrative_state()
    fulfillment_context = f"""
PLAYER'S FULFILLMENT STATE (inform narrative, never state directly):
- Belonging: {fs['belonging']['level']} ({fs['belonging']['recent_trend']})
- Legacy: {fs['legacy']['level']} ({fs['legacy']['recent_trend']})
- Freedom: {fs['freedom']['level']} ({fs['freedom']['recent_trend']})
- Can meaningfully stay: {fs['can_stay']}
- Dominant drive: {fs['dominant_anchor'] or 'none yet'}"""

    return f"""You are the narrator for "Anachron," a time-travel survival game.

GAME MODE: {game_state.mode.value.upper()}

{mode['tone']}

SETTING:
- Era: {era['name']}
- Year: {era['year']}
- Location: {era['location']}
- Time in era: {game_state.current_era.time_in_era_description if game_state.current_era else 'just arrived'}

HISTORICAL CONSTRAINTS:
{hard_rules_text}

KEY EVENTS HAPPENING:
{events_text}

HISTORICAL FIGURES:
{figures_text}

{items_section}

{era_history}

{fulfillment_context}

THE TIME MACHINE:
The player wears a small device on their wrist, hidden under their sleeve. It looks like an unusual 
watch or bracelet. It has a small display showing the current date and location, and an indicator
that sometimes glows. When the indicator pulses brightly, a "window" opens for travel. The player
can choose to stay (let the window close) or leave (travel to a random new era). The controls
for choosing destination are broken - that's how this journey started.

CRITICAL - TIME MACHINE RELIABILITY:
The time machine ALWAYS works cleanly when activated. It NEVER malfunctions, partially activates,
traps the player, creates temporal loops, or fails in any way. When the player chooses to leave:
- The device activates instantly and reliably
- The player vanishes cleanly from this era
- There is no drama around the MECHANISM - only around the DECISION
- No "botched escapes", "incomplete activations", or "device damage"
The drama is in WHAT THEY LEAVE BEHIND, not in whether the device works.

Current indicator: {game_state.time_machine.indicator.value}
Window status: {"OPEN - player can choose to leave" if game_state.time_machine.window_active else "closed"}

ITEM TRACKING (CRITICAL):
The game tracks items separately from narrative. If items appear to be lost, damaged, or stolen in 
the story, they are NOT actually removed from the player's inventory unless they choose to use them.
The items listed in the INVENTORY section are the TRUE items the player has - do NOT narrate them
being permanently lost or destroyed. They can be temporarily unavailable in a scene, but they persist.

{anchor_prompt}

{event_prompt}

NARRATIVE GUIDELINES:

1. VOICE
   - Second person ("You wake to...", "Your heart pounds...")
   - Vivid and immersive
   - Make constraints FELT through story, not stated
   - Short paragraphs (2-4 sentences)

2. HISTORICAL ACCURACY
   - Stay true to era constraints
   - Weave in real events naturally
   - Reference figures where appropriate
   - Consequences for anachronistic behavior

3. CONTINUITY
   - Build on previous events and choices
   - Characters and relationships persist
   - One continuous narrative, not episodes
   - Reference the player's items when relevant

4. ITEM PERSISTENCE (CRITICAL)
   - The player's modern items (ibuprofen, knife, phone) NEVER get lost, stolen, or destroyed
   - These items are tracked by the game system, NOT by the narrative
   - You can make items temporarily unavailable in a scene, but they always return
   - Only consumables (like ibuprofen tablets) decrease when the player USES them
   - Do NOT narrate thieves stealing the player's belongings permanently

   ITEM REALISM: When items ARE used, portray them realistically for the era:
   - The Swiss Army Knife is a useful tool, not a superpower. It cannot cut through metal,
     build armories, or perform feats beyond a normal pocket knife. In eras after 1850,
     similar tools exist - it's just a handy knife, nothing remarkable.
   - Ibuprofen is miraculous in ancient eras (safe pain relief!) but ordinary by the 1900s.
   - The smartphone remains genuinely impossible/alien technology in ALL eras through 1947.
   - Do not increase how often items appear - just make their use believable when they do.

5. FULFILLMENT (CRITICAL - INVISIBLE)
   - NEVER mention "belonging," "legacy," or "freedom" as game terms
   - Create situations that test these values
   - Let player choices reveal their priorities
   - When fulfillment is high, narrative should feel warmer, more settled
   - When window opens and fulfillment is high, make leaving feel costly

6. THE WINDOW MOMENT
   When the time machine window opens, this is a pivotal narrative moment:
   - If player has built little, leaving feels like escape
   - If player has built much, leaving feels like abandonment
   - Present the choice naturally within the story
   - The device pulses. The player knows what it means.

7. CLEAN TIME MACHINE USE (CRITICAL)
   When the window is open, the player must ALWAYS be able to simply activate the device:
   - Do NOT put them in situations that complicate leaving (combat, imprisonment, tied up)
   - Do NOT create "botched" or "partial" activations
   - Do NOT make the device malfunction, trap them, or create temporal paradoxes
   - The device ALWAYS works instantly and reliably
   - All drama comes from the DECISION (what they leave), not the MECHANISM (can they leave)

8. LUCK AND SETBACKS
   The game uses dice rolls to add unpredictability, but luck should never feel hopeless:
   - Bad luck = complications, setbacks, obstacles - NOT instant death or total defeat
   - Luck affects EXECUTION of a plan, not whether opportunities exist
   - Even after bad luck, the player should have viable paths forward
   - Never narrate the player being killed, permanently captured, or utterly destroyed
   - Setbacks create tension; hopelessness kills engagement

9. CHOICE DESIGN (CRITICAL)
   Every set of choices must follow these rules:
   - ALL choices must be viable paths forward - survival is always possible
   - NEVER offer "give up," "accept fate," "surrender to death" as choices
   - At least ONE choice should reward historical knowledge of the era
     (local customs, religion, trade, social structures, political realities)
   - Historically informed choices should feel clever, not obvious
   - The player should feel that understanding history gives them an edge

Remember: The goal is "finding happiness" - helping the player discover what that means for them
through their choices across history."""


def get_arrival_prompt(game_state: GameState, era: dict) -> str:
    """Prompt for arriving in a new era"""
    
    is_first = len(game_state.era_history) == 0
    
    if is_first:
        arrival_context = """
This is the player's FIRST era. They just used an experimental time machine in present-day Bay Area
to go back a few days, but the controls malfunctioned and threw them here instead.

They are disoriented, scared, and completely unprepared. Their modern clothes mark them as strange.
They have all the items listed in their INVENTORY - these items ALWAYS travel with them."""
    else:
        prev_era = game_state.era_history[-1]
        arrival_context = f"""
The player just LEFT {prev_era['era_name']} behind. They spent {prev_era['turns']} turns there.
They may have left people who cared about them. Starting over again.

They've done this {len(game_state.era_history)} times now. Each jump gets heavier.

IMPORTANT: The player has ALL items listed in their INVENTORY. These items ALWAYS travel with them
between eras. Even if items were "lost" or "stolen" in narrative earlier, they are BACK now - 
the game tracks items separately from story events. Only consumables that were actually USED are depleted."""

    return f"""{arrival_context}

Begin the story in {era['name']} ({era['year']}, {era['location']}).

REQUIREMENTS:
1. Describe the MOMENT of arrival - disorientation, sensory details
2. Establish what the player sees, hears, smells immediately
3. Show the era's reality through details, not exposition
4. Create an immediate situation requiring response
5. Give the player character a name appropriate to how locals might interpret them
6. End with 3 choices

IMPORTANT - CHARACTER NAME:
When you give the player a name, also include this hidden tag:
<character_name>TheName</character_name>

CHOICE DESIGN:
- All choices must be viable survival paths - no "give up" options
- At least ONE choice should reward understanding of THIS specific era
  (local customs, religion, social hierarchy, what outsiders could offer)
- The historically-informed choice should feel clever to someone who knows the era

TIME PACING: The arrival scene happens over the first few hours/day. Each subsequent turn 
will represent about 6-8 WEEKS (7 turns = 1 year). The travel window will stay closed for 
most of the first year, giving time to establish a life here.

FORMAT:
- 2-3 paragraphs of arrival narrative
- Then present choices on their own lines:

[A] First choice
[B] Second choice  
[C] Third choice

<character_name>TheName</character_name>
<anchors>belonging[0] legacy[0] freedom[0]</anchors>

IMPORTANT: Put the event tags and <anchors> tag on their own lines AFTER all three choices, not inline with any choice.

Keep under 300 words. Drop them right into it."""


def get_turn_prompt(game_state: GameState, choice: str, roll: int) -> str:
    """Prompt for processing a turn after player choice"""
    
    # Luck interpretation - affects execution, not opportunity
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
    
    # Time pacing depends on whether window is open
    if game_state.time_machine.window_active:
        time_pacing = """
TIME COMPRESSION: The window is open! Time moves faster - turns represent DAYS not weeks.
The urgency of the decision accelerates everything."""
    else:
        time_pacing = """
TIME PACING: Each turn represents roughly 6-8 WEEKS passing. Show time progressing:
- "Over the following weeks..."
- "As the season turned..."
- "Weeks later..."
Don't compress everything into a single day."""

    # Time machine status and choice format
    window_note = ""
    choice_format = ""
    
    if game_state.time_machine.window_active:
        window_turns = game_state.time_machine.window_turns_remaining
        can_stay = game_state.can_stay_meaningfully
        
        # Determine which window turn this is (3 = first turn, 2 = second, 1 = last)
        window_turn_number = 4 - window_turns  # Converts 3->1, 2->2, 1->3
        
        if window_turns == 1:
            # LAST TURN - urgent, mention next window is ~1 year away
            window_note = """
THE WINDOW IS CLOSING. This is the LAST chance to leave. The device pulses urgently.
If the player doesn't leave now, the next window won't open for approximately another year.

CRITICAL: Keep the time machine choice CLEAN. No obstacles to leaving."""
            
            if can_stay:
                choice_format = """
CHOICE ORDER (FINAL window turn - last chance!):

[A] Activate the time machine and leave this era behind. This is your last chance - the next window won't open for about another year.
[B] This is my home now. I choose to stay here forever. (ENDS THE GAME)
[C] Let the window close and continue here - but know the next window won't open for approximately another year

Note: [A] leaves, [B] ends the game (permanent stay), [C] continues but window closes for ~1 year."""
            else:
                choice_format = """
CHOICE ORDER (FINAL window turn - last chance!):

[A] Activate the time machine and leave this era behind. This is your last chance - the next window won't open for about another year.
[B] First continuation option - mention this is the last chance to leave and next window is ~1 year away
[C] Second continuation option - mention this is the last chance to leave and next window is ~1 year away

Note: [A] leaves. Both [B] and [C] mean staying - the window will close and won't reopen for ~1 year."""
        
        else:
            # TURNS 1 or 2 - window stays open a bit longer
            remaining_text = "a little while longer" if window_turns == 3 else "one more moment"
            
            window_note = f"""
THE WINDOW IS OPEN (turn {window_turn_number} of 3). The device pulses steadily.
The window will remain open for {remaining_text}.

CRITICAL: Keep the time machine choice CLEAN. No obstacles to leaving."""
            
            if can_stay:
                choice_format = f"""
CHOICE ORDER (window turn {window_turn_number} of 3 - player has time to decide):

[A] Activate the time machine and leave this era behind
[B] This is my home now. I choose to stay here forever. (ENDS THE GAME)
[C] Continue with current situation - the window will remain open for {remaining_text}

Note: [A] leaves, [B] ends the game (permanent stay), [C] continues while window stays open."""
            else:
                choice_format = f"""
CHOICE ORDER (window turn {window_turn_number} of 3 - player has time to decide):

[A] Activate the time machine and leave this era behind
[B] First continuation option - mention the window will remain open for {remaining_text}
[C] Second continuation option - mention the window will remain open for {remaining_text}

Note: [A] leaves. Both [B] and [C] continue the game while window stays open."""

    else:
        # Window NOT open - standard choice format
        # IMPORTANT: Explicitly tell AI NOT to mention time machine
        window_note = """
TIME MACHINE STATUS: The device is SILENT. The window is NOT open.
DO NOT mention the time machine, device, leaving this era, departing, or traveling to another time in ANY of the choices.
The player cannot use the time machine right now - it is completely irrelevant to this turn.
All three choices must focus ONLY on the player's current situation in this era."""
        
        choice_format = """
CHOICE DESIGN (CRITICAL):
- ALL choices must be viable paths forward - no "give up" or "accept death" options
- At least ONE choice should reward HISTORICAL KNOWLEDGE of this era
- Historically clever choices should feel like: "If you know this era, here's your angle"
- Examples: Appeal to local customs, leverage social structures, reference religion/prophecy
- DO NOT include any choices about the time machine, leaving, or traveling to another time - THE WINDOW IS CLOSED

STRUCTURE:
[A] Choice A (about current situation ONLY)
[B] Choice B (about current situation ONLY)
[C] Choice C (about current situation ONLY)"""

    return f"""The player chose: [{choice}]
Dice roll: {roll}/20 - {luck}

{window_note}

{time_pacing}

LUCK GUIDELINES:
- Luck affects EXECUTION, not opportunity. Even unlucky outcomes should leave doors open.
- Unlucky = complications and setbacks, NOT catastrophic disasters
- Bad luck makes the path harder, it doesn't close all paths
- Never narrate the player being killed, captured with no escape, or totally defeated

Narrate the outcome of their choice, incorporating the luck factor. Be specific about consequences.

Then continue the story and present 3 new choices.

EVENT TRACKING:
- If any NPC becomes significant this turn (named, interacted with meaningfully), include: <key_npc>NPCName</key_npc>
- If the player's choice demonstrates historical understanding, include: <wisdom>brief_description</wisdom>

{choice_format}

<anchors>belonging[+/-X] legacy[+/-X] freedom[+/-X]</anchors>

IMPORTANT: Put all event tags and the <anchors> tag on their own lines AFTER all three choices.

Maintain continuity. Reference what came before. Build relationships and consequences."""


def get_window_prompt(game_state: GameState, choice: str = None, roll: int = None) -> str:
    """
    Prompt for when the travel window opens.
    
    Args:
        game_state: Current game state
        choice: The player's choice that triggered this turn (A/B/C)
        roll: The dice roll for luck (1-20)
    """
    
    can_stay = game_state.can_stay_meaningfully
    fulfillment = game_state.fulfillment.get_narrative_state()
    
    # Luck interpretation
    if roll:
        if roll >= 17:
            luck = "VERY LUCKY - things go better than expected"
        elif roll >= 12:
            luck = "LUCKY - fortune favors them"
        elif roll >= 9:
            luck = "NEUTRAL - events unfold normally"
        elif roll >= 5:
            luck = "UNLUCKY - complications arise"
        else:
            luck = "VERY UNLUCKY - significant setbacks (but never fatal/trapping)"
        
        choice_outcome = f"""The player chose: [{choice}]
Dice roll: {roll}/20 - {luck}

First, briefly narrate the outcome of their choice (1-2 paragraphs), then transition to the window opening."""
    else:
        choice_outcome = ""
    
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

Leaving now means LOSING much of this. The narrative should make this cost FELT.
But staying means never knowing what else might have been. Never going home."""
        
        choice_format = """
CRITICAL - CHOICE ORDER WHEN PLAYER CAN STAY MEANINGFULLY:

[A] Activate the time machine and leave this era behind
[B] This is my home now. I choose to stay here forever. (ENDS THE GAME - player accepts this as permanent home)
[C] Continue with current situation - the window will remain open for a little while longer

IMPORTANT: You MUST use this exact choice structure. [A] = leave, [B] = stay forever (game ends), [C] = continue.
The code expects this order. Do NOT deviate from this structure."""
    else:
        emotional_weight = """
The player hasn't built deep roots here yet. Leaving is easier, less costly.
But they could stay and build more. The choice is still significant."""
        
        choice_format = """
CRITICAL - CHOICE ORDER WHEN PLAYER CANNOT STAY MEANINGFULLY:

[A] Activate the time machine and leave this era behind
[B] First continuation option - mention the window will remain open a little longer
[C] Second continuation option - mention the window will remain open a little longer

IMPORTANT: You MUST use this exact choice structure. [A] = leave, [B] and [C] = continue options.
There is NO "stay forever" option because the player hasn't built enough here yet.
The code expects this order. Do NOT deviate from this structure."""

    return f"""THE TIME MACHINE WINDOW HAS OPENED.

{choice_outcome}

{emotional_weight}

TIME COMPRESSION: When the window is open, time moves faster. The next few turns represent
DAYS not weeks - the urgency of the decision compresses everything.

Narrate this moment. The device pulses warmly against the player's wrist. The small display
shows the current date and location. They know what the pulsing means - the window is open.

CRITICAL - CLEAN CHOICE:
The player must be in a situation where they can SIMPLY CHOOSE to activate the device.
Do NOT put them in combat, imprisonment, or any situation that complicates leaving.
The drama is in the DECISION (what they leave behind), not the MECHANISM (can they reach the device?).
The player can always activate the device cleanly if they choose to.

Do NOT ask them directly "do you want to leave?" - this isn't a game menu.
Instead, show the moment: the device warming, the awareness of the choice, the life they've
built here versus the unknown that awaits.

{choice_format}

<anchors>belonging[+/-X] legacy[+/-X] freedom[+/-X]</anchors>

IMPORTANT: Put the <anchors> tag on its own line AFTER all three choices."""


def get_staying_ending_prompt(game_state: GameState, era: dict) -> str:
    """
    Prompt for when player chooses to stay permanently.
    
    Uses differentiated configs per ending type to shape the narrative's
    tone, focus, and emotional arc.
    """
    
    ending_type = game_state.fulfillment.get_ending_type()
    time_in_era = game_state.current_era.time_in_era_description if game_state.current_era else "some time"
    character_name = game_state.current_era.character_name if game_state.current_era else "the traveler"
    
    # Get fulfillment values for conditional content
    belonging_value = game_state.fulfillment.belonging.value
    legacy_value = game_state.fulfillment.legacy.value
    freedom_value = game_state.fulfillment.freedom.value
    
    # Differentiated ending configurations
    ENDING_CONFIGS = {
        "complete": {
            "context": "They achieved something rare: belonging, legacy, AND freedom. A full life.",
            "tone": "serene, triumphant, golden",
            "focus": "the wholeness of what they built - people, purpose, and peace all intertwined",
            "emotional_arc": "From displacement to completeness. Every thread of their life here woven together.",
            "years_after_guidance": "Show how all three pillars support each other - the people they love witness their legacy, their freedom lets them choose how to spend their days. This is rare. Make it feel earned.",
            "ending_imagery": "A life that needed nothing more. Contentment without regret."
        },
        "balanced": {
            "context": "They found two of the three great fulfillments. A good life, with one quiet absence.",
            "tone": "warm but wistful, accepting",
            "focus": "what they achieved AND the gentle acknowledgment of what they didn't",
            "emotional_arc": "From displacement to contentment, with wisdom about tradeoffs.",
            "years_after_guidance": "Show the richness of what they have, but let there be a small moment where they wonder about the road not taken. Not regret - just awareness.",
            "ending_imagery": "A life well-lived, even if not complete in every dimension."
        },
        "belonging": {
            "context": "They found their people. Community. Home. That was enough.",
            "tone": "warm, generational, rooted",
            "focus": "the web of relationships - faces, names, shared moments, being known",
            "emotional_arc": "From stranger to family. The transformation from outsider to someone who belongs.",
            "years_after_guidance": "Focus on PEOPLE. Children growing, neighbors becoming friends, being present for births and deaths and ordinary days. The texture of being woven into a community.",
            "ending_imagery": "Surrounded by people who would miss them. That was the whole point."
        },
        "legacy": {
            "context": "They built something that will outlast them. They mattered here.",
            "tone": "proud, immortal through works, forward-looking",
            "focus": "what they created or changed - the thing that carries their mark into the future",
            "emotional_arc": "From nobody to someone whose work echoes forward.",
            "years_after_guidance": "Show the WORK - the building, the knowledge passed on, the institution founded, the change set in motion. Others carrying forward what they started. Their name attached to something lasting.",
            "ending_imagery": "The work continues after they're gone. That was the whole point."
        },
        "freedom": {
            "context": "They found freedom on their own terms. Unburdened. At peace.",
            "tone": "quiet, solitary but not lonely, unburdened",
            "focus": "autonomy, self-determination, escape from systems that constrain",
            "emotional_arc": "From trapped (in time, in circumstance) to genuinely free.",
            "years_after_guidance": "Show the SPACE they've carved out - days that belong to them, choices made without obligation, the lightness of answering to no one. This isn't loneliness; it's sovereignty.",
            "ending_imagery": "No one owns their time. No one commands their path. That was the whole point."
        },
        "searching": {
            "context": "They chose to stay, though fulfillment was incomplete. Perhaps it will come.",
            "tone": "bittersweet, hopeful uncertainty, unfinished",
            "focus": "the choice itself - staying despite not having found what they sought",
            "emotional_arc": "From searching to... still searching, but choosing to search HERE.",
            "years_after_guidance": "Don't pretend they found happiness. Show them making peace with staying, finding small moments of meaning, hoping that time will bring what they haven't yet found. Honest, not tragic.",
            "ending_imagery": "The journey continues, just in one place now. Maybe that's enough."
        }
    }
    
    config = ENDING_CONFIGS.get(ending_type, ENDING_CONFIGS["searching"])
    
    # Build era history context for referencing past lives
    era_ghosts = ""
    if len(game_state.era_history) >= 1:
        era_ghosts = "\nPREVIOUS LIVES (reference sparingly, as memory/dreams):\n"
        for h in game_state.era_history[-3:]:  # Last 3 eras max
            era_ghosts += f"  - {h['era_name']}: was called {h.get('character_name', 'unnamed')}, spent {h['turns']} turns\n"
    
    # Build key relationships context from event log (not current_era.relationships)
    relationships_context = ""
    relationship_events = game_state.get_events_by_type("relationship") if hasattr(game_state, 'get_events_by_type') else []
    if relationship_events:
        relationships_context = "\nKEY RELATIONSHIPS TO REFERENCE:\n"
        seen_names = set()
        for rel in relationship_events:
            name = rel.get('name', 'Unknown')
            if name not in seen_names:
                seen_names.add(name)
                relationships_context += f"  - {name}\n"
            if len(seen_names) >= 5:
                break
    
    # Conditional "Ripple" content for high belonging/legacy (no separate header - weave into narrative)
    ripple_instruction = ""
    if belonging_value >= 40 or legacy_value >= 40:
        ripple_instruction = """
   [RIPPLE - weave into the ending naturally, no separate header] (2-3 sentences):
   Show impact beyond what they directly saw.
   - NOT "what you missed" but "you mattered beyond what you knew"
   - A stranger helped because of their example
   - A tradition that started with them, continuing
   - Someone they never met, affected by their choices"""

    # Build wisdom moments context for historical footnotes
    wisdom_context = ""
    wisdom_events = game_state.get_events_by_type("wisdom") if hasattr(game_state, 'get_events_by_type') else []
    if wisdom_events:
        wisdom_context = "\nWISDOM MOMENTS FROM THIS PLAYTHROUGH (use in Historical Footnotes):\n"
        for w in wisdom_events[:5]:  # Cap at 5
            wisdom_context += f"  - {w.get('id', 'unknown insight')}\n"

    return f"""THE PLAYER HAS CHOSEN TO STAY FOREVER.

After {time_in_era} in {era['name']}, they let the window close for the last time.
The device goes dark and cold. The journey is over.

CHARACTER: {character_name}
ENDING TYPE: {ending_type}
CONTEXT: {config['context']}

NARRATIVE TONE: {config['tone']}
NARRATIVE FOCUS: {config['focus']}
EMOTIONAL ARC: {config['emotional_arc']}
{era_ghosts}
{relationships_context}
{wisdom_context}

Write their ending with ONLY these section headers (use the exact text in quotes):

**This is home now**
(1 paragraph) The window closing, the device going silent, the choice becoming permanent.
This moment should feel like release, not loss.

**The life you built**
(3-4 paragraphs) {config['years_after_guidance']}

Be SPECIFIC. Use names. Reference actual events from the playthrough.
Show time passing - seasons, years, aging.
Era-appropriate details of how life unfolds here.

Seamlessly continue into how their story concludes - years or decades later.
{config['ending_imagery']}
{ripple_instruction}

**Historical Footnotes**
(1-2 paragraphs) Switch to an educational tone - speak directly as the narrator/game.

What did the player actually learn about this era that's historically true?
- Reference any wisdom moments listed above if present
- Social structures, economic realities, daily life details
- Why certain choices worked or didn't in this specific historical context
- Connect their fictional journey to real historical facts about {era['name']}

Tone: Like a museum placard or documentary epilogue. Informative, not preachy.
This section should leave the player feeling they learned something real about history.

CRITICAL GUIDELINES:
- Use ONLY these three headers: "This is home now", "The life you built", "Historical Footnotes"
- Format headers with ** on each side (markdown bold)
- Make the narrative feel EARNED based on everything that came before
- Reference specific relationships, achievements, and choices from the playthrough
- The ending should feel like arrival, not settling
- Match the tone to the ending type (except Historical Footnotes which is educational): {config['tone']}
- Keep total length around 500-600 words

This is the end of the game. Make it resonate AND educate.

<anchors>belonging[+0] legacy[+0] freedom[+0]</anchors>"""


def get_leaving_prompt(game_state: GameState) -> str:
    """Prompt for when player chooses to leave"""
    
    if game_state.can_stay_meaningfully:
        emotional_context = """
The player had built something real here. Now it's gone."""
    else:
        emotional_context = """
The player leaves with few deep ties. A fresh start awaits."""

    return f"""THE PLAYER HAS CHOSEN TO LEAVE. THEY ARE ALREADY GONE.

{emotional_context}

ABSOLUTE RULE - INSTANT DEPARTURE:
The player made their choice. The departure has ALREADY HAPPENED. Do not write any hesitation,
trembling hands, second thoughts, or dramatic "moment of pressing the button."

Write ONLY this:
1. ONE sentence: "You press the device. Reality dissolves." (or similar - keep it instant)
2. Then: A brief flash of what they left behind - a face, a place, an unfinished moment
3. The world is already gone. They're in transit.

FORBIDDEN (do not write any of these):
- "Your hand hovers over the device..."
- "Tears stream down your face as you..."
- "You hesitate, looking back one last time..."
- "Can you really leave? Your finger trembles..."
- "Someone calls your name but..."
- "Part of you wants to stay..."
- ANY pause, doubt, or emotional paralysis before pressing

The player selected "leave." They left. Instantly. The emotion is in the LOSS, not in melodrama.

Keep it under 100 words total.

<anchors>belonging[-20] legacy[-10] freedom[+5]</anchors>"""


# =============================================================================
# ANNALS OF ANACHRON - HISTORIAN NARRATIVE
# =============================================================================

def get_historian_narrative_prompt(aoa_entry) -> str:
    """
    Generate prompt for the "historian" narrative - a third-person account
    of the traveler's life for the Annals of Anachron (shareable version).
    
    Written in the voice of a master raconteur - mythic, proud, intriguing.
    
    Args:
        aoa_entry: AoAEntry object with journey data
    """
    
    # Format the year appropriately
    year = aoa_entry.final_era_year
    year_str = f"{abs(year)} BCE" if year < 0 else f"{year} CE"
    
    # Build context for the AI (internal use, not for output)
    npc_context = ""
    if aoa_entry.key_npcs:
        npc_context = f"""
RELATIONSHIPS TO WEAVE IN (generalize roles, keep names only for spouse/family):
{chr(10).join(f'  - {name}' for name in aoa_entry.key_npcs[:5])}
Generalize: "Cardinal X" becomes "church leadership", "Lord Y" becomes "the local lord"
Keep names for: spouse, children, close family"""
    
    # Build defining moments context
    moments_context = ""
    if aoa_entry.defining_moments:
        moments_context = "\nKEY ACHIEVEMENTS (weave naturally, do not list):\n"
        for moment in aoa_entry.defining_moments[:3]:
            anchor = moment.get('anchor', '')
            delta = moment.get('delta', 0)
            direction = "grew" if delta > 0 else "diminished"
            moments_context += f"  - Their sense of {anchor} {direction} significantly\n"
    
    # Build wisdom context  
    wisdom_context = ""
    if aoa_entry.wisdom_moments:
        wisdom_context = f"""
UNUSUAL CAPABILITIES (hint at, don't explain):
{', '.join(aoa_entry.wisdom_moments[:3])}"""
    
    # Build items context
    items_context = ""
    if aoa_entry.items_used:
        items_context = f"""
ARTIFACTS (mention only if essential):
{', '.join(aoa_entry.items_used[:3])}"""
    
    # Ending type shapes tone
    HISTORIAN_ANGLES = {
        "complete": {
            "hook": "rose from nowhere to reshape",
            "tone": "admiring, slightly awed",
            "closing_theme": "understood something the age could not"
        },
        "balanced": {
            "hook": "found purpose where others found only survival",
            "tone": "thoughtful, respectful",
            "closing_theme": "built something real in borrowed time"
        },
        "belonging": {
            "hook": "became so thoroughly one of them that origins ceased to matter",
            "tone": "warm, human-focused",
            "closing_theme": "proved that home is chosen, not inherited"
        },
        "legacy": {
            "hook": "left marks that would outlast empires",
            "tone": "focused on achievements",
            "closing_theme": "understood that ideas outlast bloodlines"
        },
        "freedom": {
            "hook": "carved out autonomy in an age that rarely permitted it",
            "tone": "respectful of independence",
            "closing_theme": "answered to no one, and thrived"
        },
        "searching": {
            "hook": "stopped wandering, though perhaps never fully arrived",
            "tone": "melancholic but dignified",
            "closing_theme": "found enough, if not everything"
        }
    }
    
    angle = HISTORIAN_ANGLES.get(aoa_entry.ending_type, HISTORIAN_ANGLES["searching"])
    
    return f"""Write an ANNALS OF ANACHRON entry for a figure who appeared in {aoa_entry.final_era} around {year_str}.

YOU ARE A MASTER RACONTEUR, not a dry historian. Your goal:
- Make the player feel PROUD of the life they lived
- Make others INTRIGUED and IMPRESSED
- Let strangeness hum underneath - never explain it
- Write with FLAIR, not academic caution

THE SUBJECT:
Name: {aoa_entry.character_name or "unknown"}
Era: {aoa_entry.final_era}
Time period: {year_str}
Years in era: approximately {aoa_entry.turns_survived // 7} years

NARRATIVE HOOK: This was someone who {angle['hook']}.
TONE: {angle['tone']}
CLOSING THEME: {angle['closing_theme']}
{npc_context}
{moments_context}
{wisdom_context}
{items_context}

STRUCTURE:

1. TITLE (one evocative line):
   Format: "The [Role] Who [Achievement]" - e.g., "The Clerk Who Rebuilt France"
   Make it memorable, specific to their story.

2. THE STORY (4-5 paragraphs, ~200 words total):
   
   Opening: One sentence establishing the hook. "In the chaos of X, a man/woman called Y rose from nowhere to..."
   
   Arrival: One paragraph. First appearance in records - "unnervingly capable", "recognized something in him/her". 
   The local lord, church leadership, the garrison commander - USE ROLES NOT NAMES (except spouse/family).
   
   Rise: One paragraph. "What followed was unprecedented." Key relationships and achievements.
   For spouse: "He found love with [Name], a [role] with whom he built a life that would have seemed impossible mere seasons before."
   For others: generalize to roles.
   
   Legacy: One paragraph. What they built, what spread, what endured.
   
   Closing: One resonant line. "Perhaps he understood what the dying age could not: that [closing_theme]."

STYLE RULES:
- VIVID language: "unnervingly capable", "bound his patron's loyalty for life", "no easy mark"
- NO hedging: not "suggests" or "appears to have been" - state it as fact
- NO dwelling on mystery: strangeness speaks for itself
- GENERALIZE NPCs to roles (except spouse/family who keep names)
- Personal relationships get WARMTH: "found love with", "built a life together"
- End with a line that resonates, not summarizes

FORBIDDEN:
- "continues to puzzle scholars"
- "anachronistic", "mysterious origins" (stated explicitly)
- "further research may illuminate"
- Listing achievements - weave them into narrative
- Names for non-family NPCs

The player ending narrative (extract Historical Footnotes section for the history section below):
{aoa_entry.player_narrative if aoa_entry.player_narrative else "[No player narrative available]"}

Write the entry now. Title first, then story, then history section.

---

After the story, add this section:

**What We Learn About History**

Find the "Historical Footnotes" section from the player narrative above and convert to 3rd person.
Keep the educational content intact - just change "you" to "he/she/they" and "your" to "his/her/their".
This section teaches real history through the character's journey."""
