# Time Hopper - Web Terminal Game

## Overview

Time Hopper is a time-travel survival text adventure game presented through a web-based terminal emulator. The application wraps a Python-based interactive fiction game in a React frontend, connecting them via WebSocket PTY sessions. Players travel through historical eras with modern items, building fulfillment until they choose to stay in a time period.

The web interface is a **faithful terminal wrapper** - the Python game runs unchanged and displays its exact text-based UI through xterm.js. All game logic, narrative generation, and state management lives in Python.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React with TypeScript, bundled by Vite
- **Routing**: Wouter for lightweight client-side routing
- **UI Components**: shadcn/ui component library with Radix primitives
- **Styling**: Tailwind CSS with CSS custom properties for theming
- **Terminal Emulator**: xterm.js (@xterm/xterm) with fit and web-links addons
- **State Management**: TanStack Query for server state, React hooks for local state

The frontend's primary purpose is displaying a full-screen terminal that connects to the Python game via WebSocket.

### Backend Architecture
- **Server**: Express.js with TypeScript
- **PTY Sessions**: node-pty spawns Python game processes
- **WebSocket**: ws library for real-time terminal I/O over `/ws/terminal`
- **Build**: Custom esbuild script bundles server, Vite builds client

The server creates isolated PTY sessions for each WebSocket connection, running `game/game.py` and streaming output to the browser.

### Python Game Architecture
Located in `/game/` directory with modular design:
- **game.py**: Main game loop and UI rendering
- **game_state.py**: Central state coordination (time machine, fulfillment, inventory)
- **eras.py**: Historical era definitions (13 eras spanning 3000+ years)
- **time_machine.py**: Window mechanics and era transitions
- **fulfillment.py**: Hidden anchor tracking (Belonging, Legacy, Freedom)
- **items.py**: Modern item inventory management
- **prompts.py**: AI narrative generation prompts
- **config.py**: Tunable game parameters
- **scoring.py**: Score calculation and leaderboard

The game uses Anthropic's Claude API for narrative generation (optional - has demo mode fallback).

### Data Flow
1. Browser opens WebSocket to `/ws/terminal`
2. Server spawns Python process via node-pty
3. Terminal input flows: Browser → WebSocket → PTY → Python stdin
4. Terminal output flows: Python stdout → PTY → WebSocket → xterm.js

### Database Schema
- PostgreSQL with Drizzle ORM
- Current schema: Simple users table (id, username, password)
- Schema location: `shared/schema.ts`
- Migrations output: `./migrations/`

## External Dependencies

### Third-Party Services
- **Anthropic Claude API**: Powers narrative generation in the Python game (requires ANTHROPIC_API_KEY environment variable, falls back to demo mode if unavailable)

### Key NPM Packages
- **node-pty**: Terminal emulation for spawning Python processes
- **ws**: WebSocket server for terminal communication
- **@xterm/xterm**: Browser terminal emulator
- **drizzle-orm**: Database ORM with PostgreSQL dialect
- **express**: HTTP server framework

### Python Dependencies
- **anthropic**: Claude API client for AI narrative generation

### Environment Requirements
- **DATABASE_URL**: PostgreSQL connection string (required for Drizzle)
- **ANTHROPIC_API_KEY**: Optional, enables AI narrative generation