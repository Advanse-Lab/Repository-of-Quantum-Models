import numpy as np
import qutip as qt

from typing import Tuple


# Single-qubit identity and Pauli matrices
si = qt.qeye(2)   # Identity matrix
sx = qt.sigmax()  # Pauli X
sy = qt.sigmay()  # Pauli Y
sz = qt.sigmaz()  # Pauli Z
sp = qt.sigmap()  # Raising operator
sm = qt.sigmam()  # Lowering operator

# Projection operators onto |0⟩ and |1⟩ states
zero_proj = (si + sz) / 2  
one_proj = (si - sz) / 2  


def single_qubit_Hamiltonian(e_j: float) -> qt.Qobj:
    """
    Constructs the single-qubit Hamiltonian H = - (e_j / 2) * sz.

    Inputs:
        - e_j: Energy splitting of the qubit.

    Output:
        - The single-qubit Hamiltonian as a Qobj.
    """
    return -e_j / 2.0 * sz


def single_qubit_thermal_state(H_j: qt.Qobj, beta_j: float) -> Tuple[float, qt.Qobj]:
    """
    Computes the thermal state ρ_j = exp(-β H_j) / Z_j for a single qubit.

    Inputs:
        - H_j: Hamiltonian of the qubit (Qobj).
        - beta_j: Inverse temperature β = 1/(k_B T).

    Output:
        - Z_j: Partition function (float).
        - ρ_j: Thermal state (Qobj).
    """
    eH_j = (-beta_j * H_j).expm()
    Z_j = eH_j.tr()
    return Z_j, eH_j / Z_j
