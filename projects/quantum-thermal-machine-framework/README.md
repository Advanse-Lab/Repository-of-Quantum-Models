# Quantum Thermal Machine Framework

> Implementation of a hybrid (classical-quantum) quantum thermal machine for ergotropy extraction through Variational Quantum Algorithms (VQA), with an object-oriented architecture modeled using UML.

## Problem Description

The central problem addressed is the **optimal extraction of work (ergotropy)** from a quantum system composed of multiple qubits coupled to thermal baths at different temperatures.

- **The system**: A quantum thermal machine composed of `N` qubits, where the edge qubits (indices `0` and `N-1`) act as hot and cold thermal reservoirs, while the internal qubits form the working subsystem.
- **The key concepts**: Ergotropy (the maximum extractable work from a quantum state), parameterized quantum thermalization, quantum correlations (entanglement), and Trotterized unitary evolution for Heisenberg Hamiltonians (XX, XY, XYZ).
- **The relevance**: Quantum thermal machines are promising candidates for thermodynamic advantages at the nanoscale. Understanding how to maximize work extraction in systems with quantum correlations remains an open problem in quantum thermodynamics, with direct applications in quantum computing and metrology.

The process is divided into three sequential stages:

1. **Thermalization** — the boundary qubits are prepared in thermal states parameterized by the angles `θ_A` and `θ_B`, derived from the inverse temperatures `β_A` and `β_B` and the energy gaps `ε_A` and `ε_B`.
2. **Correlation Generation** — pairs of internal qubits are entangled through parameterized circuits (e.g., `ImaginaryParametricCorrelation`) following a configurable topology (e.g., `RainbowTopology`).
3. **Work Extraction** — the correlated state evolves under an interaction Hamiltonian (e.g., Heisenberg-XX). The coupling parameters are classically optimized via Adam to maximize the extracted work: `W = ⟨H⟩_ρ₀ − ⟨H⟩_ρ_f`.

## Implementation

**Libraries used:**

| Library | Role |
|---|---|
| PennyLane ≥ 0.36 | Definition and execution of parameterized quantum circuits (`lightning.qubit`) |
| QuTiP ≥ 5.1 | Manipulation of density matrices and quantum state vectors |
| NumPy ≥ 2.0 | Numerical operations and linear algebra |
| SciPy ≥ 1.13 | Matrix exponentials for thermal state computation |
| Matplotlib ≥ 3.9 | Visualization of ergotropy results |
| `concurrent.futures` | Parallelization of parameter sweeps |

**Language:** Python 3.10+

**How to run:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main simulation
python main.py
```

The simulation performs a parallelized sweep over different energy gap ratios `ε_B/ε_A` and temperature ratios `β_B/β_A`, saving the ergotropy plot as `Ws_XX_plot.png`.

**Quick configuration** — the main parameters are exposed in the `__main__` block of `main.py`:

```python
N_QUBITS = 4
THERMALIZATION_OPERATION_CLASS = ThermalizationOperation
CORRELATION_OPERATION_CLASS = ImaginaryParametricCorrelation
WORK_OPERATION_CLASS = TrotterizedHeisenbergXX
CORRELATION_TOPOLOGY_CLASS = RainbowTopology
WORK_TOPOLOGY_CLASS = LinearTopology
```

## Modeling Approach

The architecture was modeled using **UML (Unified Modeling Language)** extended with specific profiles for quantum systems.

- **Adopted approach**: Standard UML + Pérez-Castillo Profile + QuanUML, with emphasis on the explicit separation between classical, quantum, and hybrid layers.
- **Main abstractions**:
  - `Topology` (classical) — interchangeable strategy for qubit connectivity.
  - `QuantumOperation` (quantum) — encapsulated sequence of quantum gates with a uniform `.apply()` interface.
  - `QuantumThermalMachine` (hybrid) — PennyLane QNode compiler and executor.
  - `ErgotropyOptimizer` (hybrid) — Adam controller with central finite-difference gradient estimation over quantum circuits.
- **Why this approach**: The separation into three layers (`classical/`, `quantum/`, `classical_quantum/`) maps directly to UML stereotypes, making the extraction of class, activity, and sequence diagrams a systematic process. Abstract hierarchies (`ABC`) remove modeling ambiguity and make each component representable as a well-defined UML element.

## Diagrams

The UML diagrams derived from this implementation are available in the `/diagrams` folder (when provided).

```text
./diagrams/
├── perez_activity_diagram.png    # The 3 stages of the thermodynamic cycle using Pérez-Castillo profile 
├── perez_class_diagram.png    # Complete component hierarchy using Pérez-Castillo profile 
├── quanuml_circuit_diagram.png    # The 3 stages of the thermodynamic cycle using QuanUML profile
├── quanuml_class_diagram.png       # Complete component hierarchy using QuanUML profile
└── quanuml_sequence_diagram.png    # Sequence diagram of the QuanUML profile used to represent the code execution flow.
```

### Class Diagram

The class diagram captures the central hierarchy of the framework:

- `Topology` ← `LinearTopology`, `RingTopology`, `RainbowTopology`, `CompleteTopology`, ...
- `QuantumOperation` ← `ThermalizationOperation`, `CorrelationOperation` ← `ImaginaryParametricCorrelation`, `WorkOperation` ← `TrotterizedHeisenbergXX` / `XY` / `XYZ`
- `QuantumThermalMachine` depends on `QuantumOperation` (injection via `.apply()`)
- `ErgotropyOptimizer` depends on `QuantumThermalMachine` and `ThermodynamicsCalculator`

### Activity Diagram

Models the thermodynamic cycle as a sequential activity flow:

1. Compute `θ_A`, `θ_B` from `β`, `ε`
2. `ThermalizationOperation.apply()` → prepare ρ₀
3. `CorrelationOperation.apply()` → generate entanglement
4. Adam loop: estimate gradient → update parameters → evaluate work
5. Return optimal ergotropy

### Sequence Diagram

Models the runtime interaction among `main.py`, `ErgotropyOptimizer`, `QuantumThermalMachine`, and `ThermodynamicsCalculator` during one optimization epoch.

## Insights

### What Worked Well

- The **three-layer separation** (`classical/`, `quantum/`, `classical_quantum/`) proved to be the most important architectural decision.
- The use of **abstract classes** (`ABC`) as interfaces enforced clear contracts and facilitated extensibility.
- The **topology strategy** as an interchangeable object allows experiments with different qubit arrangements.
- The **central finite-difference gradient estimation** is backend-independent.

### Limitations

- Central finite-difference gradient estimation requires `2 × N_params` circuit evaluations per epoch.
- The number of epochs and convergence tolerance (`tol`) must be manually tuned.
- The current implementation does not support analytical gradients.

### UML Modeling Trade-offs

- Standard UML does not provide primitives to represent qubits, quantum gates, or superposition states.
- Closures and anonymous functions are not representable in UML.
- `ErgotropyOptimizer` accumulates multiple responsibilities.

### Possible Improvements

- Migrate the gradient computation to `qml.grad`.
- Separate the Adam optimizer state into a dedicated `AdamState` class.
- Add support for real hardware backends.
- Implement heat-related metrics beyond work.

## References

- **Allahverdyan, A. E., Balian, R., & Nieuwenhuizen, T. M.** (2004). Maximal work extraction from finite quantum systems.
- **Cerezo, M., et al.** (2021). Variational quantum algorithms.
- **Kingma, D. P., & Ba, J.** (2014). Adam: A method for stochastic optimization.
- **Pérez-Castillo, R., et al.** — UML Profile for quantum computing.
- **PennyLane Documentation**
- **QuTiP Documentation**
- **Araujo, A.** (2026). *Applying UML for Modeling a Quantum Thermal Machine Framework.*

## Structure

```text
.
├── README.md
├── README_2.md
├── CONTRIBUTING.md
├── requirements.txt
├── main.py
├── framework/
│   ├── classical/
│   │   └── topologies.py
│   ├── quantum/
│   │   ├── operations.py
│   │   ├── hamiltonians.py
│   │   ├── single_qubit_operators.py
│   │   └── many_qubit_operators.py
│   └── classical_quantum/
│       ├── quantum_thermal_machine.py
│       ├── ergotropy_optimizer.py
│       └── thermodynamics_calculator.py
└── Ws_XX_plot.png
```