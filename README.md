# Python Dungeon Crawler Game

A complete 2D top-down dungeon crawler built with Python and Pygame, featuring advanced combat systems, strategic AI, and procedural dungeon generation.

## 🎮 Game Features

### Core Gameplay
- **Top-down dungeon crawler** with WASD/arrow key movement
- **10-level progression system** with increasing difficulty
- **Procedural dungeon generation** with connected rooms and corridors
- **Line-of-sight visibility system** with fog of war exploration
- **Boss battles** every level with unique abilities and mechanics

### Combat System
- **Dual combat modes**: Melee attacks (left click) and ranged spells (right click)
- **Weapon-specific animations**: Each weapon type has distinct attack patterns and swing ranges
  - Swords: Variable arc swings with silver blade effects
  - Maces: 145° arc swings with heavy impact
  - Daggers: 165° arc with fast stabbing motions
  - Spears: Straight thrust attacks with extended range
  - War Axes: 160° arc with triangular strike patterns
  - Twin Blades: 90° arc with dual-strike effects
  - Fists: 90° arc punching attacks
- **Visual feedback system**: Floating damage numbers, hit effects, and weapon rendering
- **Attack cooldowns** and weapon-specific speed multipliers

### Advanced AI System
- **Strategic enemy behavior** based on enemy type:
  - **Fast enemies**: Aggressive flanking with sprint attacks when positioned behind/beside player
  - **Heavy enemies**: Tank behavior with head-on engagement
  - **Ranged enemies**: Kiting tactics maintaining optimal distance
  - **Basic enemies**: Balanced aggressive approach
- **Enhanced turn coat spell**: Mind-controlled enemies attack each other and bosses
- **Position-aware combat**: Enemies attack 30% faster when flanking from advantageous positions

### Item & Progression System
- **Comprehensive item types**: Melee weapons, enchantments, spells, and health items
- **High item frequency**: 10-18 items per level with 85% enemy drop rate
- **XP progression**: Automatic leveling with stat increases
- **Inventory management**: Equip weapons, use spells, and apply enchantments
- **Boss rewards**: 3-6 health items per boss encounter

### Visual & Audio Systems
- **Weapon rendering**: All equipped weapons visually displayed on characters
- **Damage numbers**: Color-coded floating damage/healing indicators
- **UI notifications**: Item pickup/drop notifications with descriptions
- **Sound system**: Music tracks and sound effects (plug-and-play audio files)
- **Enhanced UI**: Health/XP bars, minimap, enemy counter, and control instructions

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Pygame library
- NumPy library

### Installation
```bash
# Install dependencies
pip install pygame numpy

# Run the game
python main.py
```

### Controls
- **Movement**: WASD or Arrow Keys
- **Melee Attack**: Left Mouse Click
- **Ranged Attack/Spells**: Right Mouse Click
- **Item Pickup**: Walk over items (automatic)
- **Item Drop**: Press Q
- **Item Use**: Press E (for health items)
- **Altar Activation**: Press E when near altar (requires key)

## 📁 Project Structure

### Core Game Files
- `main.py` - Game initialization, main loop, and rendering coordination
- `player.py` - Player class with movement, stats, combat, and progression
- `enemy.py` - Enemy AI system with strategic behaviors and state machines
- `combat.py` - Combat mechanics, projectiles, and collision detection
- `level.py` - Procedural dungeon generation and level management
- `items.py` - Item system with weapons, spells, and enchantments

### Enhanced Features
- `weapon_renderer.py` - Visual weapon rendering system
- `damage_numbers.py` - Floating damage/healing number system
- `notifications.py` - UI notification system for item interactions
- `visibility.py` - Line-of-sight raycasting and fog of war
- `ui.py` - Comprehensive HUD and user interface
- `assets.py` - Runtime sprite generation and asset management

### Boss & Enemy Types
- `boss_weapons.py` - Boss weapon systems and abilities
- `new_enemy_types.py` - Advanced enemy variants with unique abilities
- `boss_dagger_haste.py` - Enhanced boss with haste ability

### Game State & Audio
- `game_state.py` - Game state management and statistics
- `sound_system.py` - Audio management for music and effects

## 🎯 Recent Enhancements

### Enhanced Combat System
- **Weapon-specific attack animations** matching actual swing ranges
- **Aggressive fast enemy flanking** with sprint attacks from sides/behind
- **Position-aware AI** that adapts tactics based on relative player position
- **Enhanced turn coat mechanics** with comprehensive enemy targeting

### Improved Gameplay Balance
- **Increased item frequency** (10-18 items per level) for more engaging gameplay
- **Higher enemy drop rates** (85% chance) and enhanced boss rewards
- **Balanced enemy counts** (18 + player_level × 5) to match increased loot
- **Strategic depth** with weapon choice affecting combat effectiveness

## 🔧 Technical Details

- **Engine**: Pygame 2.6.1
- **Architecture**: Modular component-based design across 15+ files
- **Performance**: 60 FPS target with optimized collision detection
- **Save System**: Automatic progress tracking and statistics
- **Scalability**: Level-based difficulty scaling and procedural content

## 🎲 Game Balance

- **Enemy scaling**: Health and damage increase with player level
- **Weapon variety**: 7+ weapon types with unique characteristics
- **Strategic gameplay**: Positioning, timing, and weapon choice matter
- **Reward progression**: Higher levels offer better loot and challenges

---

**Note**: This is a standalone Python game that runs independently. The web application components in this repository are separate and not required for the Python game to function.