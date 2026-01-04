
<img src="https://raw.githubusercontent.com/DavidTheD3veloper/Solar-Lang/refs/heads/main/solar.png">

# Solar Programming Language

**Latest Version:** v1.0.0

Solar is a **simple, experimental, and open-source programming language written in Python**, designed as a learning project and a foundation for future expansion. While the current version is intentionally minimal, Solar aims to grow into a more capable and flexible language over time.

This first release focuses on **basic syntax, arithmetic, printing, function calls, and simple UI creation**. Solar is not meant to compete with existing languages (yet), but rather to explore how a custom language can be built, extended, and improved step by step.

---

## ✨ Current Features (v1.0.0)

Solar is still in its early stages, but it already supports several core features:

* ✅ **Simple arithmetic**

  * Addition
  * Multiplication
* ✅ **Variables**
* ✅ **Print output**
* ✅ **Call-style commands**
* ✅ **Basic UI system**

  * Windows
  * Labels
  * Text entries
  * Checkboxes
  * Buttons

### 🚧 Planned Features (Future Versions)

These features are planned but **not yet implemented**:

* ❌ Changing UI styles *(coming in v1.0.1)*
* ❌ Advanced UI components
* ❌ Reading system information (e.g. drives, files, hardware)
* ❌ More advanced logic and control flow

> Solar is still small, but future versions such as **v1.0.1**, **v2.0.0**, or even **v3.0.0** aim to significantly expand its capabilities assuming the project survives 😅.

---

## 📖 What Can Solar Do Right Now?

### 🔹 Variables & Printing

You can define variables and print their values:

```
let x = 10 - variable
print x
```

**Output:**

```
10
```

---

### 🔹 Arithmetic Operations

Solar supports basic arithmetic using simple commands:

```
add 1 2 - add 1 + 2
mul 3 4 - multiply 3 * 4
```

**Output:**

```
3
12
```

---

## 🖥️ Simple UI System

One of Solar’s most interesting features is its **basic UI framework**. While still very simple, it allows you to create windows and interact with user input.

### Example UI Code:

```
ui window main - creates the main window loop
ui title main "Solar UI Test" - sets the title
ui size main 420 260 - sets window size

ui label main l1 "Name:" at 20 20 - adds a label
ui entry main name at 100 20 - adds a textbox

ui checkbox main agree "I agree to everything" at 20 70 - checkbox
ui button main submit "Submit" at 20 120 do print name agree - Submit button

ui text submit "SEND" - sets button text (not fully working yet)
ui text agree "Actually I'm serious" - sets checkbox text

ui run main - runs the main window loop
```

This allows you to:

* Create windows
* Display text
* Accept user input
* React to button presses

⚠️ Some UI features (like changing text dynamically) are **experimental and partially broken**, but they will be improved in future updates.

---

## 🎯 Project Goals

Solar is one of my **most ambitious personal projects** so far. The main goals are:

* Learn how programming languages work internally
* Experiment with syntax design
* Build a flexible base for future features
* Keep everything **open-source and hackable**

The first version is not perfect—and it’s not meant to be. Solar is a **work in progress**, and each new version will bring improvements, fixes, and new ideas.

---

## 🚀 What’s Next?

* **v1.0.1** → UI improvements & styling
* **Future versions** → more powerful logic, better UI, system access, and advanced features

Stay tuned, and thanks for checking out **Solar** 🌞
The journey is just getting started.
