"""
Anachron - Configuration Module

All tunable game parameters live here. Adjust these to change game feel
without touching game logic.
"""

# =============================================================================
# ERA REGIONS
# =============================================================================

# Which eras are considered "European/Western" vs global
# European focus includes Western culture (Americas colonized by Europeans)
EUROPEAN_ERA_IDS = [
    "classical_athens",      # Greece
    "viking_age",            # Scandinavia
    "medieval_plague",       # Europe
    "american_revolution",   # Colonial America (Western culture)
    "industrial_britain",    # Britain
    "civil_war",             # America (Western culture)
    "ww2_europe",            # Europe
    "ww2_pacific",           # American Home Front (Western culture)
]

# All other eras are "worldwide/global"
# ancient_egypt, han_dynasty, aztec_empire, mughal_india, indian_partition

# =============================================================================
# TIME MACHINE SETTINGS
# =============================================================================

# Minimum turns before window can open (prevents slot-machine gameplay)
WINDOW_MIN_TURNS = 7

# Window probability by turn (guaranteed by turn 10)
# Turn 7: 30%, Turn 8: 50%, Turn 9: 75%, Turn 10: 100%
WINDOW_PROBABILITIES = {
    7: 0.30,
    8: 0.50,
    9: 0.75,
    10: 1.00,  # Guaranteed
}

# Legacy settings (kept for reference, no longer used)
WINDOW_BASE_PROBABILITY = 0.30  # Starting probability at turn 7
WINDOW_PROBABILITY_INCREMENT = 0.20  # Roughly matches new curve
WINDOW_PROBABILITY_CAP = 1.0  # Guaranteed by turn 10

# Small chance of very long gap (makes some playthroughs feel different)
# DISABLED - we now guarantee window by turn 10
LONG_GAP_PROBABILITY = 0.0  # Was 0.05
LONG_GAP_EXTRA_TURNS = 0  # Was 10

# Window duration in turns (how long player has to decide)
WINDOW_DURATION_TURNS = 3  # Represents about a week in-game

# =============================================================================
# TIME PACING
# =============================================================================

# Normal turns per year (each turn = ~7-8 weeks when window is closed)
TURNS_PER_YEAR = 7

# When window opens, time compresses - turns represent days not weeks
# This creates urgency around the decision
WINDOW_TIME_COMPRESSED = True

# =============================================================================
# STARTING ITEMS (Fixed - these always come with you)
# =============================================================================

STARTING_ITEMS = [
    {
        "id": "ibuprofen",
        "name": "Bottle of Ibuprofen",
        "description": "100 tablets of 200mg ibuprofen",
        "uses": 100,
        "utility": "Reduce fever, ease pain, reduce inflammation - seems miraculous",
        "risk": "Can't cure infections, supplies run out, overdose danger",
        "hooks": ["heal", "trade", "gain trust", "save someone important"],
        "from_era": None,  # Modern item
    },
    {
        "id": "knife",
        "name": "Swiss Army Knife",
        "description": "Multi-tool with blade, screwdriver, scissors, can opener, tweezers",
        "uses": None,  # Durable
        "utility": "Superior cutting tool, versatile, compact",
        "risk": "Theft target, questions about craftsmanship origin",
        "hooks": ["craft", "repair", "defend", "impress artisans", "medical"],
        "from_era": None,
    },
    {
        "id": "phone_kit",
        "name": "Smartphone + Solar Charger",
        "description": "Modern smartphone with offline Wikipedia, camera, flashlight, calculator, maps, compass, and foldable solar charger to keep it powered",
        "uses": None,  # Renewable with solar
        "utility": "Encyclopedic knowledge, light source, mirror, camera for records, calculator, compass",
        "risk": "Obviously impossible technology - extremely dangerous to reveal",
        "hooks": ["reference knowledge", "flashlight", "photograph", "calculate", "navigate", "prove otherworldly origin", "trade as magical artifact"],
        "features": [
            "Wikipedia offline - encyclopedic knowledge of history, science, medicine",
            "Camera - record images, use as mirror",
            "Flashlight - bright LED light",
            "Calculator - complex math instantly",
            "Compass app - navigation",
            "Maps - though only shows modern geography",
            "Clock - keeps accurate time",
            "Solar charger - renewable power as long as there's sun"
        ],
        "from_era": None,
    },
]

# =============================================================================
# FULFILLMENT ANCHORS (Hidden from player)
# =============================================================================

ANCHORS = {
    "belonging": {
        "name": "Belonging",
        "description": "Community, acceptance, found family",
        "arrival_threshold": 70,
        "mastery_threshold": 90,
    },
    "legacy": {
        "name": "Legacy", 
        "description": "Lasting impact, teaching, building",
        "arrival_threshold": 70,
        "mastery_threshold": 90,
    },
    "freedom": {
        "name": "Freedom",
        "description": "Autonomy, self-determination, independence",
        "arrival_threshold": 70,
        "mastery_threshold": 90,
    }
}

# =============================================================================
# GAME MODES
# =============================================================================

MODES = {
    "kid": {
        "name": "Kid Mode",
        "age_rating": "11+",
        "description": "Educational, age-appropriate content",
        "violence": "consequences, not graphic",
        "death": "framed respectfully",
        "sexual_content": False,
        "profanity": False,
    },
    "mature": {
        "name": "Mature Mode",
        "age_rating": "18+",
        "description": "Unflinching historical realism",
        "violence": "graphic when accurate",
        "death": "visceral, specific",
        "sexual_content": "implied, referenced",
        "profanity": True,
    }
}

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

TEXT_SPEED = 0.012  # Seconds per character for typewriter effect
SHOW_DEVICE_STATUS = True  # Show time machine indicator in UI
