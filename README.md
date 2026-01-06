
<img src="https://raw.githubusercontent.com/DavidTheD3veloper/Solar-Lang/refs/heads/main/solar.png" width="150" height="150" alt="Solar logo">

## Solar Programming Language — v1.0.3

**Before you ask:** Why is the releases tab empty now? Well, Solar is a pip downloadable package!
To install it run:

```text
pip install solar-lang
```

To update run:

```text
solar update
```

(NOTE: After updating, run `solar version`. If it still shows the old version number, run the update command again. This is a pip behavior, not a Solar bug.)
To see all available commands run:

```text
solar help
```

---

**Documentation available at:** https://solardocs.davidthed3veloper.is-a.dev

## Stability, Functions, and a Major Language Leap

Solar v1.0.3 is a **major evolution** of the language. While v1.0.2 focused on stability and expressions, v1.0.3 focuses on **language power**.

This release introduces real Solar-level functions, structured control flow, richer built-in functionality, and a much clearer path toward building full applications and games *entirely in Solar syntax*.

Solar is no longer just a scripting experiment — it is becoming a small but capable language.

---

## What’s New in v1.0.3

### Solar-Level Functions with `solar_def`

Solar now supports defining functions directly in Solar syntax:

```text
solar_def greet(name, ok):
    print "Hello"
    print name ok
end
```

* Functions are first-class Solar constructs
* Automatically registered and callable like built-ins
* Can be reused across UI, game logic, and scripts
* Designed to feel familiar to Python users, without being Python

This removes the need to drop into Python just to define reusable logic.

---

### Structured Control Flow

Solar v1.0.3 introduces **block-based control flow**, closed explicitly with `end`:

```text
if score > 10:
    print "Nice"
else:
    print "Try again"
end
```

Supported constructs include:

* `if / elif / else`
* `while` loops
* `for` loops using ranges
* Function blocks (`solar_def`)
* Game loops (`pg loop`)

This makes Solar scripts readable, predictable, and far more expressive.

---

### Expanded Expression Power

Building on v1.0.2, Solar v1.0.3 improves expression handling even further:

* Arithmetic with precedence
* Comparisons and boolean logic
* Parentheses
* Lists and dictionaries
* Indexing and simple data manipulation

Example:

```text
let speed = clamp(base_speed + level * 0.5, 1, 10)
```

Expressions now feel natural and powerful, without unnecessary boilerplate.

---

### Solar-Native Pygame Game Syntax

v1.0.3 continues and expands Solar’s **game-oriented direction**.

Solar-native Pygame commands allow you to write simple games using only Solar syntax:

```text
contain pygame

pg init
pg window 800 600 title "Solar Game"
pg fps 60

pg loop:
    pg clear 20 20 30
    pg rect player 100 100 40 40 color 255 80 80
    pg draw player
    pg flip
end
```

This is an early but important step toward making Solar a lightweight game scripting language.

---

### Greatly Expanded Built-in Functions

Solar v1.0.3 ships with **many more built-in functions**, covering:

* Math helpers (`clamp`, `round`, `abs`)
* String utilities (`upper`, `lower`, `split`, `join`)
* List helpers (`push`, `pop`, `len`)
* Random and time utilities
* Conversion helpers (`str`, `int`, `float`)

These reduce the need for Python passthrough in common cases.

---

### Imports with `contain <package>`

The `contain` keyword remains a core feature:

```text
contain pygame
contain numpy
contain pygame.mixer
```

Solar v1.0.3 continues to improve reliability and integration with Python packages installed via pip.

---

### Python Passthrough (Still Supported)

Solar still allows intentional Python passthrough for advanced use cases:

* Full Python blocks
* Single-line Python statements
* Direct access to Solar variables and the function registry

Solar does not attempt to replace Python — it integrates with it cleanly.

---

### Improved Examples and Documentation

The repository includes:

* Updated examples for v1.0.3
* Solar-only game demos
* UI and function examples
* Documentation pages built for Jekyll

All examples are meant to be explored, modified, and learned from.

---

## What’s Next

Solar v1.0.3 opens the door to larger ideas:

* A Solar-specific package manager
* Community-built Solar packages
* Deeper game abstractions
* Better tooling and error messages
* Performance improvements

---

## Project Philosophy

Solar remains:

* Experimental
* Open-source
* Hackable
* Learning-focused

It is not trying to replace Python.

Solar exists to explore how far a small, readable language can go when it is built **on top of Python, not against it**.

**Solar v1.0.3 is the biggest step forward yet — and the foundation for what comes next.**
