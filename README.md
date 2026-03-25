# ♟️ Checkers Playing Bot — AI Agent

> An adversarial search AI that plays Checkers against a human player, built for **CSC3309: Introduction to Artificial Intelligence** at Al Akhawayn University.

**Team:** Doha Ilyass · Salma Madoud · Zineb Akhouad · Omar El Mokhtar El Bousouni

---

## 📖 Overview

This project implements a fully playable Checkers game where a human competes against an AI agent. The agent uses classic adversarial search algorithms to evaluate board states and select optimal moves, with real-time performance analytics and an optional graphical interface.

---

## ✨ Features

- 🤖 **Three AI search strategies** — Minimax, Alpha-Beta Pruning, Alpha-Beta with Node Ordering
- ♟️ **Full checkers rules** — mandatory captures, multi-jump sequences, king promotion
- 📊 **Live analytics** — nodes expanded, pruning count, search depth, execution time
- 🖥️ **Optional GUI** — visual board powered by Python Tkinter
- ⏱️ **Configurable constraints** — set your own time limit and search depth

---

## 🗂️ Project Structure

```
checkers-bot/
│
├── CheckersBot.py          # Main source file (all 4 classes)
└── README.md
```

### Class Architecture

| Class | Responsibility |
|---|---|
| `GameBoard` | Board representation, rules, successor function, goal test, heuristic |
| `SearchToolBox` | Minimax, Alpha-Beta, node ordering, time management |
| `OtherStuff` | Analytics tracking and reporting per move / overall |
| `PlayingTheGame` | Game loop, human input handling, GUI launcher |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.7+**
- `tkinter` (included in standard Python; required only for GUI mode)

No external packages needed — the bot uses only the Python standard library.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/checkers-bot.git
cd checkers-bot

# 2. Run the bot
python CheckersBot.py
```

---

## 🎮 How to Play

When you launch the program you will be prompted to configure the game:

```
Select Search Strategy (S): 1. Minimax | 2. Alpha-Beta | 3. Alpha-Beta w/ Ordering
Enter 1, 2, or 3: 3

Enter Time limit in seconds (T) [1 to 3]: 2
Enter Look-forward plies (P) [5 to 9]: 5

Run with GUI (y/n)? y
```

### Making a Move

Enter the row and column of the piece you want to move, then the target square:

```
Line of piece to move: 5
Column of piece to move: 0
Target Line: 4
Target Column: 1
```

> For **multi-jump captures**, enter the **final** destination square — the bot resolves the full jump chain automatically.

### Board Legend

| Symbol | Meaning |
|---|---|
| `w` | White man (Human) |
| `W` | White king (Human) |
| `b` | Black man (AI) |
| `B` | Black king (AI) |

The **human plays White** and always moves first.

---

## 🧠 AI Algorithms

### Minimax
Explores the full game tree to the configured depth, assuming both players play optimally. The AI maximizes its score; the human minimizes it.

### Alpha-Beta Pruning
Extends Minimax by tracking two bounds:
- **Alpha** — best score the maximizer can guarantee
- **Beta** — best score the minimizer can guarantee

Whenever `β ≤ α`, the remaining nodes in that branch are skipped (pruned), reducing computation significantly.

### Alpha-Beta with Node Ordering
Before exploring successors, states are sorted by their heuristic value. Evaluating the most promising nodes first increases the chance of early pruning, maximizing efficiency.

---

## 📊 Heuristic Evaluation

Non-terminal states are scored using a weighted piece count:

| Piece | Score |
|---|---|
| White Man | −1 |
| White King | −3 |
| Black Man | +1 |
| Black King | +3 |

A **positive score** favors the AI (Black); a **negative score** favors the human (White).

---

## 📈 Analytics Output

After every AI move, the system prints a performance report:

```
--- Analytics for Agent Bot (Black) ---
Nodes Expanded: 1075
Pruning Count : 378
Space Complex.: Max Recursion Depth Reached: 5
Pruning Occurred at Depths: [2, 3, 4]
Time Taken    : 0.2389 seconds
Target Plies  : 5 plies
---------------------------------
```

At the end of the game, cumulative totals are displayed:

```
=== FINAL CUMULATIVE ANALYTICS ===
Total Nodes Expanded : 12340
Total Pruning Done   : 4210
Total Time Taken     : 18.4321 seconds
Total Ordering Gain  : 142 extra prunes caught
==================================
```

---

## ⚙️ Configuration Parameters

| Parameter | Options | Default |
|---|---|---|
| Search Strategy (S) | `1` Minimax / `2` Alpha-Beta / `3` Alpha-Beta + Ordering | `3` |
| Time Limit (T) | 1 – 3 seconds | — |
| Search Depth (P) | 5 – 9 plies | — |

---

## 🏁 Game Over Conditions

The game ends when:
1. A player has **no pieces remaining**, or
2. A player has **no legal moves available**

---

## 📌 Known Limitations & Future Improvements

- The heuristic is purely piece-count based — a positional or mobility-aware heuristic could improve play strength
- The GUI is read-only (text input is still done via the terminal)
- Future versions could support AI vs AI matches for benchmarking strategies

---

## 📄 License

This project was developed as an academic assignment. Feel free to reference or build upon it with attribution.
