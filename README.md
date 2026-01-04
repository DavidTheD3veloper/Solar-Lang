
<img src="https://raw.githubusercontent.com/DavidTheD3veloper/Solar-Lang/refs/heads/main/solar.png" width="150" height="150" alt="Solar logo">


Here’s the **final polished v1.0.1 description** with the **examples folder** clearly mentioned and integrated naturally into the text:

---

## Solar Programming Language — v1.0.1

**A Big Jump from v1.0.0**

Solar v1.0.1 is a major step forward in the evolution of the Solar programming language. While still experimental and learning-focused, this release significantly expands Solar’s capabilities—especially in UI control, Python integration, and extensibility.

This version lays the groundwork for Solar becoming more than just a toy language, while keeping its syntax simple, hackable, and fun.

---

## ✨ What’s New in v1.0.1

### 🎨 Much Greater UI Control

Solar’s UI system has been upgraded and is now powered by **customtkinter**, allowing for:

* Modern-looking widgets
* Reliable text rendering on buttons, labels, and checkboxes
* Per-window foreground (`ui fg`) and background (`ui bg`) styling
* More predictable widget behavior and layout

This makes Solar’s UI system far more usable and visually appealing than in v1.0.0.

---

### 📦 Working Imports with `contain <package>`

Solar now supports importing **real Python packages** directly:

```
contain pygame
contain numpy
contain pygame.mixer
```

This translates to actual Python `import` statements at runtime.
If the package exists in your Python environment, Solar can use it immediately.

---

### 🐍 Python Passthrough (Intentional)

Solar v1.0.1 officially supports **raw Python passthrough**:

* Full Python blocks (`def`, `class`, `if`, `for`, etc.)
* Single-line Python statements
* Direct access to Solar variables and the `funcs` registry
* Seamless mixing of Solar syntax and Python code

This keeps Solar small while still allowing advanced users to drop down to Python when needed.

---

### 📂 Examples Included in the Repository

To make Solar easier to learn and experiment with, **ready-to-run examples** are now included in the repository:

* UI examples demonstrating windows, buttons, inputs, and styling
* Import examples showing how to use `contain <package>`
* Mixed Solar + Python examples for advanced use cases

All examples can be found in the **`examples/` folder** and are meant to be modified, broken, and learned from.

---

### 🧩 A Stronger Language Core

Internally, Solar now features:

* Correct handling of quoted strings
* Cleaner separation between Solar code and Python code
* More reliable parsing and execution
* A more stable foundation for future language features

---

## 🚀 What’s Coming Next

Solar v1.0.1 is not the end goal—it’s a foundation for much bigger ideas.

### 🎮 Pygame as Solar Syntax

Future versions will introduce **native Solar syntax for Pygame**, including:

* Window creation
* Input handling
* Rendering and drawing
* Game loops

All without writing Python directly.

---

### 📦 A Solar Package Manager

A future Solar release will introduce a **package manager** built specifically for the language.

This will allow:

* Installing Solar-specific packages
* Creating and sharing reusable UI components
* Writing community-driven extensions
* Building useful libraries on top of Solar and Python

The goal is to let Solar grow through its users, not just its core.

---

### 🌱 Beyond v1.0.1

Other planned improvements include:

* More UI styling and layout options
* Solar-level control flow (`if`, loops, etc.)
* System and file access
* Plugin-style extensibility

---

## 🎯 Project Philosophy

Solar remains:

* Experimental
* Open-source
* Hackable
* Built as a learning project

It’s not trying to replace Python.
It’s trying to **learn from it, build on it, and explore what’s possible**.

Solar v1.0.1 is a real milestone—and it’s just the beginning.

