# Hungry Robots 🤖

A terminal-based strategy game inspired by *Hungry Robots* by Al Sweigart.

You are trapped in an arena with malfunctioning robots that relentlessly move toward you.
Your goal is simple: **survive** — by making the robots crash into each other.

---

## 🎮 Gameplay Overview

- You are represented by `@`
- Robots are represented by `R`
- Destroyed robots become wrecks `X`
- Walls are `#`
- Obstacles are `+`

Each turn:
1. You move (8 directions or stay still)
2. Robots move **simultaneously** toward you
3. Collisions are resolved

The game ends when:
- A robot reaches you → **Game Over**
- All robots are destroyed → **Victory**

---

## 🧠 Core Mechanics

### Player
- Can move in 8 directions (diagonals included)
- Can stay still
- Has a limited number of **teleports**

### Robots
- Move deterministically toward the player using Cartesian logic
- Can move diagonally
- Do **not** pathfind
- Can get temporarily or permanently stuck
- Avoid walls and obstacles

### Collisions
- Robot + Robot → both destroyed, leave wreck `X`
- Robot + wreck `X` → robot destroyed
- Robot + player → game over
- Robots never die by hitting walls

All robot movements are resolved **simultaneously**, not sequentially.

---

## 🗺 World Representation

The game world is a 2D grid.

Internally, the grid is represented as a **dictionary** mapping coordinates to symbols:

```python
(x, y) -> cell content
```

### Static Elements

Static elements are stored directly in the grid dictionary and **never move once placed**:

- Walls (`#`)
- Obstacles (`+`)
- Destroyed robots / wrecks (`X`)

Walls and obstacles act as **blocking terrain**.
Wrecks act as **passive hazards** that destroy any robot entering them.

### Dynamic Elements

Dynamic entities are **not permanently stored** in the grid structure:

- The player (`@`)
- Living robots (`R`)

Their positions are tracked separately and rendered onto the grid at display time.

---

## 🛠 Technical Details

- Language: **Python 3**
- Interface: **Terminal (ASCII)**
- External libraries: **None**
- Board size adapts to terminal dimensions
- The entire screen is **re-rendered each turn**
- No cursor positioning or partial redraw

This design favors:
- determinism
- explicit state transitions
- ease of reasoning and debugging

---

## ▶️ How to Run

```bash
python hungry_robots.py
```

Ensure your terminal window is large enough for correct rendering.

---

## 🎯 Controls

```
(Q) (W) (E)
(A) (S) (D)
(Z) (X) (C)
```

- `S` → stay still
- `T` → teleport (limited charges)
- `QUIT` → exit the game

Unavailable moves are shown as `( )`.

---

## 🧪 Design Philosophy

This project is intentionally implemented as a **procedural simulation**.

Key principles:
- explicit game state
- simultaneous multi-agent updates
- minimal abstraction
- clarity over cleverness

Object-oriented refactoring is intentionally deferred to keep the core mechanics visible.

---

## 🚀 Possible Extensions

- Multiple robot types with different movement rules
- Traps or temporary obstacles
- Additional tactical items
- Multiple levels or difficulty scaling
- Post-hoc refactor to an object-oriented architecture