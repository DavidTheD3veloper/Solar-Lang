<img src="https://raw.githubusercontent.com/DavidTheD3veloper/Solar-Lang/refs/heads/main/solar.png" width="150" height="150" alt="Solar logo">

## Solar Programming Language — v1.0.2

**Stability, Expression Power, and Game-Oriented Growth**

Solar v1.0.2 is a refinement and expansion of the ideas introduced in v1.0.1. This release focuses on **stability**, **better expression handling**, and **stronger foundations for game and UI development**, while keeping Solar simple, readable, and fun to experiment with.

This version represents Solar’s transition from a proof-of-concept language into a more cohesive and usable tool.

---

## ✨ What’s New in v1.0.2

### 🧮 Expression Evaluation (Major Upgrade)

Solar v1.0.2 introduces a **proper expression evaluator**, allowing for:

- Arithmetic expressions (`+`, `-`, `*`, `/`)
- Parentheses and operator precedence
- Inline math in assignments
- Cleaner and more readable logic

Example:
```text
let x = clamp(x + (right - left) * speed, 0, 760)
```

This removes the need for awkward intermediate variables and makes real logic possible directly in Solar.

---

### 🎮 Native Pygame-Style Solar Syntax

Solar now includes **Solar-native commands for Pygame**, making game development far more approachable:

- Window creation
- Input handling
- Drawing rectangles and text
- Game loops and FPS control

All without writing raw Python.

This is a major step toward Solar becoming a **game-oriented scripting language**.

---

### 📦 Improved `contain <package>` Imports

The `contain` keyword is now more robust and reliable:

```text
contain pygame
contain pygame.mixer
contain numpy
```

Imports are resolved cleanly at runtime and work seamlessly alongside Solar-native systems.

---

### 🐍 Python Passthrough (Still First-Class)

Solar v1.0.2 continues to support **intentional Python passthrough**:

- Full Python blocks and statements
- Direct access to Solar variables
- Seamless mixing of Solar and Python code

Solar doesn’t fight Python — it **embraces it**.

---

### 📂 Expanded Examples

The repository now includes **more complete and realistic examples**, including:

- Small games built with Solar + pygame
- Input and collision examples
- UI and rendering demonstrations

All examples are meant to be modified, explored, and broken.

---

### 🧩 Stronger Core & Stability Improvements

Internally, Solar v1.0.2 improves:

- Parsing reliability
- Execution consistency
- Error handling
- Cleaner separation of Solar vs Python code

This makes Solar more predictable and safer to extend in future versions.

---

## 🚀 What’s Next

Solar v1.0.2 sets the stage for much bigger ideas.

### 📦 Solar Package Ecosystem

Planned future features include:

- A Solar-specific package manager
- Community-built extensions
- Reusable UI and game components

---

### 🎮 Deeper Game Development Support

Upcoming versions aim to expand Solar’s game focus with:

- More drawing primitives
- Event-driven input
- Scene and entity helpers
- Asset loading helpers

---

### 🌱 Beyond v1.0.2

Longer-term goals include:

- Solar-level control flow (`if`, loops)
- File and system access
- Plugin-style extensibility
- Performance improvements

---

## 🎯 Project Philosophy

Solar remains:

- Experimental
- Open-source
- Hackable
- Learning-focused

It is **not trying to replace Python**.

Solar exists to explore how far a small, readable language can go when it stands on Python’s shoulders.

**Solar v1.0.2 is a solid step forward — and the foundation for what comes next.**
