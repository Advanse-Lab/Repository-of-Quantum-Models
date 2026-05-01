# Ergotropy Optimizer

Modeling a quantum thermodynamic system focused on ergotropy optimization using structured abstractions and system design principles.

---

## 📌 Problem Description

This project explores a quantum thermodynamics scenario where the goal is to **optimize ergotropy**, i.e., the maximum extractable work from a quantum system.

The system involves:

* Quantum states and Hamiltonians
* Thermalization processes
* Correlation operations
* Work extraction mechanisms

This problem is relevant in the study of **quantum heat engines** and **energy-efficient quantum systems**.

---

## ⚙️ Implementation

* Language: Python
* Libraries: QuTiP, NumPy

### How to run

```bash
pip install -r requirements.txt
python main.py
```

---

## 🧠 Modeling Approach

This example models the system using a **modular, object-oriented design**, separating responsibilities into distinct components:

* `QuantumThermalMachine` → represents the system
* `ThermalizationOperation` → handles thermal processes
* `CorrelationOperation` → introduces correlations
* `WorkOperation` → extracts work

The modeling focuses on:

* Clear separation of concerns
* Reusable abstractions
* Extensibility for different strategies

Although inspired by UML-like thinking, the design is adapted to better represent **quantum-specific behaviors**.

---

## 📊 Diagrams

Diagrams are available in the `/diagrams` folder.

They illustrate:

* Class structure
* Interaction flow (sequence diagrams)
* System decomposition

Example:

![Class Diagram](./diagrams/class-diagram.png)

---

## 💡 Insights

* Classical modeling approaches (e.g., UML) require adaptation to represent quantum behavior effectively
* Separating operations into independent components improves flexibility
* Some quantum concepts (e.g., entanglement, state evolution) are difficult to represent clearly in traditional diagrams

This highlights the need for **better modeling abstractions for quantum systems**.

---

## 📚 References

* Nielsen & Chuang — *Quantum Computation and Quantum Information*
* QuTiP Documentation
* Research on quantum thermodynamics and ergotropy

---

## 📁 Structure

```text
.
├── README.md
├── diagrams/
├── code/
└── assets/
```
