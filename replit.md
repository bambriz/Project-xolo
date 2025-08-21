# Overview

This project is now a complete 2D top-down dungeon crawler game built with Python and Pygame, featuring a fully modular architecture across multiple files. The game includes comprehensive gameplay mechanics including player movement, multiple enemy types with AI, combat systems (both melee and ranged), XP progression, line-of-sight visibility with fog of war, and procedural dungeon generation.

The game is fully functional and ready to play, with all core systems tested and working properly. Additionally, the repository contains a modern web application built with React, TypeScript, and Express.js for potential future web-based features.

# User Preferences

Preferred communication style: Simple, everyday language.
Preferred programming language: Python (specifically requested over JavaScript for game development).

# System Architecture

## Game Architecture (Python) - COMPLETED

**Core Game Engine**: Built on pygame with a fully modular component-based architecture across 9 separate files. The main game loop handles event processing, game state updates, and rendering at 60 FPS.

**Modular File Structure**:
- **main.py**: Game initialization, main loop, event handling, and rendering coordination
- **player.py**: Player class with movement, stats, leveling, combat integration, and health management
- **enemy.py**: Multiple enemy types (basic, fast, heavy, ranged) with state-based AI, pathfinding, and scaling based on player level
- **combat.py**: Complete combat system handling melee attacks, ranged projectiles, collision detection, and visual effects
- **level.py**: Procedural dungeon generation with room-based layouts, corridor connections, wall collision detection
- **visibility.py**: Line-of-sight raycasting system implementing fog of war with exploration tracking
- **assets.py**: Runtime sprite generation creating colored circles with type-specific visual indicators
- **ui.py**: Comprehensive HUD with health/XP bars, minimap, enemy counter, cooldown timers, and control instructions
- **game_state.py**: Game state management, statistics tracking, settings, and session data

**Game Features Implemented**:
- Player movement with WASD/Arrow keys and normalized diagonal movement
- Melee combat (left click) with arc-based attack detection and cooldowns
- Ranged combat (right click) with projectile physics, trails, and collision
- Four enemy types with unique behaviors: basic (balanced), fast (quick/agile), heavy (tanky), ranged (long-distance attacks)
- XP progression system with automatic leveling, stat increases, and scaling enemy difficulty
- Line-of-sight visibility system with 360-degree raycasting and fog of war
- Procedural dungeon generation with connected rooms and appropriate enemy spawning
- Real-time collision detection for walls, entities, and projectiles
- Health regeneration system with damage immunity periods
- Comprehensive UI showing all game stats, minimap, and control instructions

## Web Application Architecture

**Frontend**: React 18 with TypeScript using Vite as the build tool. Implements a component-based architecture with modern React patterns including hooks and context.

**3D Graphics**: Three.js integration through @react-three/fiber and @react-three/drei for 3D rendering capabilities, with post-processing effects support.

**State Management**: Zustand for lightweight state management, specifically handling game state and audio controls.

**UI Framework**: Radix UI primitives with Tailwind CSS for styling, providing accessible and customizable components.

**Backend**: Express.js server with TypeScript support, featuring middleware for request logging and error handling.

**Build System**: Vite for frontend bundling with esbuild for server-side compilation, supporting hot module replacement in development.

## Data Architecture

**Database**: PostgreSQL integration using Drizzle ORM with type-safe schema definitions and migrations.

**Schema Design**: Simple user management system with username/password authentication structure.

**Storage Interface**: Abstracted storage layer with in-memory fallback for development, allowing easy database provider switching.

**Query Management**: React Query (@tanstack/react-query) for server state management with optimistic updates and caching.

## Development Architecture

**Monorepo Structure**: Organized with separate client, server, and shared directories for code organization.

**Type Safety**: Full TypeScript coverage across frontend, backend, and shared utilities with strict compilation settings.

**Path Resolution**: Configured path aliases for clean imports (@/ for client, @shared/ for shared utilities).

**Asset Handling**: Support for various file types including 3D models (GLTF/GLB) and audio files (MP3, OGG, WAV).

# External Dependencies

## Game Dependencies (Python)
- **pygame**: Core game engine for graphics, input, and audio
- **math/random**: Built-in Python modules for calculations and procedural generation

## Web Application Dependencies
- **React Ecosystem**: React 18, React DOM, React Query for frontend framework and state management
- **Three.js Stack**: @react-three/fiber, @react-three/drei, @react-three/postprocessing for 3D graphics
- **UI Libraries**: Radix UI component primitives, Tailwind CSS for styling
- **Build Tools**: Vite, TypeScript, esbuild for development and production builds
- **Database**: @neondatabase/serverless for PostgreSQL connectivity, Drizzle ORM for database management
- **Utilities**: clsx for conditional classes, date-fns for date manipulation, nanoid for ID generation

## Development Tools
- **Package Management**: npm with lockfile for dependency resolution
- **Code Quality**: TypeScript for type checking, ESLint configurations
- **Asset Processing**: GLSL shader support, PostCSS with Autoprefixer
- **Database Migration**: Drizzle Kit for schema management and migrations

## Runtime Services
- **Database**: PostgreSQL (via Neon serverless or compatible provider)
- **Session Management**: Potential session storage with connect-pg-simple
- **Environment**: NODE_ENV-based configuration for development/production modes