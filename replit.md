# Overview

This project appears to be a hybrid application combining a 2D dungeon crawler game written in Python with pygame and a modern web application built with React, TypeScript, and Express.js. The repository contains both a Python-based game implementation and a full-stack web application setup with database integration.

The Python game is a complete dungeon crawler featuring player movement, enemy AI, combat systems, procedural level generation, and various game mechanics like experience points and upgrades. The web application side provides a modern React frontend with Three.js integration, a Node.js/Express backend, and PostgreSQL database connectivity using Drizzle ORM.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Game Architecture (Python)

**Core Game Engine**: Built on pygame with a modular component-based architecture. The main game loop handles event processing, game state updates, and rendering at 60 FPS.

**Game Systems**:
- **Player System**: Manages player stats, movement, leveling, and combat abilities with real-time input processing
- **Enemy AI**: State-based AI system with different enemy types (basic, fast, heavy, ranged) featuring pathfinding and combat behaviors
- **Combat System**: Handles both melee and ranged combat with projectile physics and damage calculations
- **Level Generation**: Procedural dungeon generation with tile-based collision detection and enemy spawning
- **Asset Management**: Runtime sprite generation system creating textures and visual elements programmatically
- **UI System**: HUD rendering with health bars, minimap, experience tracking, and game statistics
- **Visibility System**: Line-of-sight calculations using raycasting for fog of war effects

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