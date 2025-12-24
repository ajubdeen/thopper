# Design Guidelines: Time Hopper Web Terminal

## Design Approach
**Terminal Emulation Approach**: This is a **terminal-in-browser** implementation. The Python game runs unchanged, displaying its exact text-based UI through a web-based terminal emulator. All ANSI colors, box drawings (╔═══╗), typewriter effects, and formatting are preserved exactly as they appear in the original terminal game.

## Core Design Principle
The web interface is a **faithful terminal wrapper** - not a redesign. The game's visual identity lives in its terminal output. Our job is to present that terminal in a polished web context.

---

## Layout System

### Page Structure
```
┌─────────────────────────────────────────┐
│  Header (optional minimal chrome)      │
├─────────────────────────────────────────┤
│                                         │
│    [Terminal Emulator - Full Focus]    │
│                                         │
│    • Max width: 1000px centered         │
│    • Min height: 600px                  │
│    • Responsive: 100% on mobile         │
│                                         │
└─────────────────────────────────────────┘
```

**Spacing**: Use Tailwind units of 4, 6, and 8 for consistent layout (p-4, m-6, gap-8)

### Terminal Container
- **Desktop**: Centered container, max-w-5xl, with subtle shadow and border
- **Mobile**: Full viewport width and height, no margins
- **Padding**: Minimal internal padding to maximize terminal space (p-2 or p-3)

---

## Typography

The terminal emulator handles all game text rendering. Our only typography concerns are:

### Minimal UI Chrome (if needed)
- **Header/Title**: Inter or system font, font-semibold, text-sm
- **Status indicators**: Monospace font (matches terminal), text-xs
- All actual game content uses the terminal's monospace font (Courier New, Monaco, or Consolas)

---

## Component Library

### Primary Component: Terminal Emulator
- Full-featured xterm.js instance
- Supports ANSI color codes (all 16 terminal colors)
- Handles box-drawing characters (╔═══╗)
- Implements blinking cursor
- Captures keyboard input and sends to Python backend
- Scrollback buffer enabled (500+ lines)

### Optional Minimal Chrome
**Floating Status Bar** (top-right corner, semi-transparent):
- Connection status indicator (connected/disconnected)
- Subtle dot indicator (green = active, red = disconnected)
- Text: text-xs, opacity-80

**Fullscreen Toggle** (icon button, top-right):
- Icon-only button to toggle fullscreen mode
- Heroicons expand/compress icon
- Background blur effect when overlaying terminal

---

## Terminal Styling

### Terminal Colors
Use the standard xterm.js theme that faithfully renders ANSI codes:
- Black, Red, Green, Yellow, Blue, Magenta, Cyan, White
- Bright variants of all colors
- Let the Python game control all color output

### Terminal Background
- Pure black (#000000) or very dark gray (#0a0a0a) to match traditional terminal
- Alternative: Dark navy (#0f1419) for slight warmth
- Background should not distract from text

### Cursor
- Blinking block cursor (xterm.js default)
- Bright color that contrasts with background

---

## Responsive Behavior

### Desktop (1024px+)
- Terminal container centered with max-width
- Subtle shadow and border around terminal
- Optional header with game title

### Tablet (768px - 1023px)
- Terminal takes most of viewport
- Minimal margins (m-4)
- Header collapses to icon/title only

### Mobile (< 768px)
- Terminal fills entire viewport (100vw × 100vh)
- No header or chrome - pure terminal
- Fixed positioning to prevent scroll issues
- Ensure keyboard appears properly for input

---

## Interactions & Animations

### Terminal Interactions
All interactions are handled by the terminal emulator:
- Keyboard input sent directly to Python game
- Mouse clicks for text selection only
- No custom overlays or interruptions

### Loading States
**Initial Connection**:
- Centered spinner with "Connecting to Time Machine..." text
- Once connected, spinner fades out and terminal appears

**Reconnection** (if connection drops):
- Semi-transparent overlay with reconnection message
- Terminal output frozen but visible underneath

### No Custom Animations
The Python game handles typewriter effects and timing. Do not add additional animations that would interfere.

---

## Special Considerations

### Box Drawing Characters
Ensure the terminal font supports Unicode box-drawing characters (U+2500–U+257F):
```
╔═══╗
║   ║
╚═══╝
```
Test that these render correctly.

### Typewriter Effect
The Python game implements character-by-character output. The terminal must render this smoothly without buffering delays.

### Input Handling
- Capture all keyboard input and forward to Python process
- Support special keys (Arrow keys, Backspace, Enter)
- Handle both uppercase and lowercase input

---

## Images
**No images needed**. This is a pure terminal interface. The visual richness comes from the game's text output, not graphical assets.

---

## Key Implementation Notes

1. **xterm.js Configuration**: Use default xterm.js styling with ANSI color support enabled
2. **WebSocket/SSE**: Real-time streaming of Python output to terminal
3. **Pseudo-terminal Backend**: Use `node-pty` to run Python game with full terminal emulation
4. **No UI Framework Needed**: This isn't a component-based UI - it's a terminal emulator with minimal chrome
5. **Preserve All ANSI Codes**: Do not strip or modify terminal escape sequences

---

## Success Criteria

The web version is successful if:
- A player cannot visually distinguish it from running `python game.py` in their terminal
- All colors, box drawings, and formatting appear identical
- Typewriter effects and timing feel the same
- Input and output are responsive with no lag
- The game plays exactly as it does in the original terminal