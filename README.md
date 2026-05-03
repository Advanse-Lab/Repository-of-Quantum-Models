# Repository-of-Quantum-Models

This repository is a **collaborative collection of quantum computing system models**, in which each contribution explores how problems involving quantum implementations can be represented, structured, and developed.

Its purpose is to bridge the gap between:

- Quantum computing theory
- Software design and architecture for quantum computing
- System modeling approaches within the context of quantum computing

## Purpose

The modeling of quantum systems remains an open challenge. Various approaches have been proposed — ranging from UML adaptations to custom abstractions — yet there is still no widely adopted standard. 

Therefore, this repository aims to:

- Provide **real examples** of quantum system modeling
- Compare **different modeling approaches**
- Encourage **experimentation and discussion**
- Serve as a **reference for researchers and developers**

## What You'll Find

Within each example in the [projects](./projects) folder, it is possible to explore the implementation and/or modeling of a problem involving quantum computing. Each project presents its own description, a specific implementation in a given language or framework (e.g., Qiskit, QuTiP, etc.), modeling diagrams (UML, QuanUML, or other approaches), as well as discussions and conceptual insights.

## Repository Structure

```
projects/        → Individual modeling cases
templates/       → Contribution templates
docs/            → Guidelines and supporting material
```

## Featured Examples

- **quantum-thermal-machine-framework** _(initial contribution)_. This project implements a simulation system for quantum engines and quantum thermal machines. The architecture uses PennyLane for the construction of parameterized quantum circuits and QuTiP for the manipulation of quantum states (Density Matrices and State Vectors).

_(More coming soon — contributions are welcome!)_

## Contributing

We welcome contributions from anyone interested in:

- Quantum computing
- System modeling
- Software architecture

To contribute:

1. Fork the repository
2. Create a new example inside [projects](./projects)
3. Follow the provided template
4. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for full guidelines.

## Why This Matters

Quantum computing is evolving rapidly, but the engineering practices used to model and structure quantum software are still not well established. Most available projects focus only on implementation, leaving aside important architectural and documentation perspectives.

This repository is an attempt to:

> Explore how we can think, design, and communicate quantum systems more effectively.

## License

This project is licensed under the MIT License.
