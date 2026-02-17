# AI_A1_23F0774_23F0805
# GOOD PERFORMANCE TIME APP

## 🧠 AI Pathfinder – Uninformed Search Visualization

GOOD PERFORMANCE TIME APP is an interactive AI Pathfinder developed for AI2002 – Artificial Intelligence (Spring 2026).

This project demonstrates how different Uninformed Search Algorithms explore a grid environment to find a path from a Start node (S) to a Target node (T).

Instead of directly jumping to the result, the program visually shows how the algorithm works step-by-step:
- Which nodes are explored
- Which nodes are in the frontier
- How the final path is constructed

It also supports dynamic obstacles that may appear during runtime. If the path becomes blocked, the algorithm automatically re-plans a new path.

---

## 🎯 Objective

- Implement 6 uninformed search algorithms
- Animate search process step-by-step
- Compare performance differences
- Handle dynamic obstacles
- Re-plan path if blocked

---

## 🔎 Algorithms Implemented

1. **Breadth-First Search (BFS)** – Finds shortest path in unweighted grid.
2. **Depth-First Search (DFS)** – Explores deeply before backtracking.
3. **Uniform Cost Search (UCS)** – Expands lowest cost node first.
4. **Depth-Limited Search (DLS)** – DFS with fixed depth limit.
5. **Iterative Deepening DFS (IDDFS)** – Repeated DLS with increasing depth.
6. **Bidirectional Search** – Searches from both start and target.

---

## ⚡ Features

✔ Interactive grid  
✔ Step-by-step animation  
✔ Adjustable speed  
✔ Dynamic obstacle spawning  
✔ Automatic path re-calculation  
✔ Real-time statistics  
✔ 8-directional movement  

---

## 🎮 Controls

S → Set Start  
T → Set Target  
SPACE → Run  
C → Clear  
R → Reset  
1–6 → Select algorithm  
Mouse Drag → Create walls  
ESC → Exit  

---

## 💻 Installation

pip install pygame

Run:

python main.py

---

## 📚 Learning Outcomes

- Completeness vs Optimality
- Time and Space complexity trade-offs
- Practical implementation of search algorithms
- GUI-based algorithm visualization
- Dynamic environment handling
