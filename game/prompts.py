"""
Anachron - Prompts Module

AI prompts for the narrative system, updated for:
- Fulfillment anchors (invisible tracking)
- Time machine windows
- Modern items
- Multi-era journeys
"""

from game_state import GameState, GameMode, GamePhase
from items import get_items_prompt_section
from fulfillment import get_anchor_detection_prompt


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

<anchors>belonging[0] legacy[0] freedom[0]</anchors>

IMPORTANT: Put the <anchors> tag on its own line AFTER all three choices, not inline with any choice.

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

{choice_format}

<anchors>belonging[+/-X] legacy[+/-X] freedom[+/-X]</anchors>

IMPORTANT: Put the <anchors> tag on its own line AFTER all three choices.

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
    """Prompt for when player chooses to stay permanently"""
    
    ending_type = game_state.fulfillment.get_ending_type()
    time_in_era = game_state.current_era.time_in_era_description if game_state.current_era else "some time"
    
    ending_contexts = {
        "complete": "They achieved something rare: belonging, legacy, AND freedom. A full life.",
        "balanced": "They found two of the three great fulfillments. A good life.",
        "belonging": "They found their people. Community. Home. That was enough.",
        "legacy": "They built something that will outlast them. They mattered here.",
        "freedom": "They found freedom on their own terms. Unburdened. At peace.",
        "searching": "They chose to stay, though fulfillment was incomplete. Perhaps it will come."
    }
    
    return f"""THE PLAYER HAS CHOSEN TO STAY.

After {time_in_era} in {era['name']}, they let the window close for the last time.
The device goes dark and cold. The journey is over.

Ending type: {ending_type}
Context: {ending_contexts.get(ending_type, ending_contexts['searching'])}

Write their ending:

1. THE MOMENT: The window closing, the choice becoming permanent (1 paragraph)
2. THE YEARS AFTER: What their life becomes - be specific, earned, true to what they built (2 paragraphs)
3. THE END: How their story concludes - years or decades later (1 paragraph)

Make it feel EARNED based on everything that came before. Reference specific relationships,
achievements, and choices from the playthrough.

This is the end of the game. Make it resonate.

<anchors>belonging[+0] legacy[+0] freedom[+0]</anchors>
ENDING_TYPE: {ending_type}"""


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
