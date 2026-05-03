import numpy as np
import qutip as qt

from typing import Sequence, Tuple

from framework.quantum.single_qubit_operators import si, sx, sy, sz, sp, sm, one_proj, zero_proj


def local_many_qubit_operator(N: int, j: int, Op_j: qt.Qobj) -> qt.Qobj:
    """
    Constructs a local operator acting on qubit j in an N-qubit system.

    Inputs:
        - N: Total number of qubits.
        - j: Index of the qubit where the operator acts.
        - Op_j: Operator acting on qubit j (Qobj).

    Output:
        - A many-body operator with Op_j acting on qubit j and identities elsewhere.
    """
    mq_Op = [Op_j] + (N-1) * [si]
    if(j != 0 and j != N-1):
        mq_Op = j*[si] + [Op_j] + (N-j-1) * [si]
    elif(j == N-1): 
        mq_Op = (N-1) * [si] + [Op_j]

    return qt.tensor(mq_Op)


def pair_many_qubit_operator(N: int, i: int, j: int, Op_i: qt.Qobj, Op_j: qt.Qobj) -> qt.Qobj:
    """
    Constructs a two-qubit operator acting on qubits i and j in an N-qubit system.

    Inputs:
        - N: Total number of qubits.
        - i: Index of the first qubit.
        - j: Index of the second qubit.
        - Op_i: Operator acting on qubit i (Qobj).
        - Op_j: Operator acting on qubit j (Qobj).

    Output:
        - A many-body operator with Op_i on qubit i, Op_j on qubit j, and identities elsewhere.
    """
    mq_Op = []
    for k in range(N):
        if(k == i):
            mq_Op.append(Op_i)
        elif(k == j):
            mq_Op.append(Op_j)
        else:
            mq_Op.append(si)
    return qt.tensor(mq_Op)


def create_correlated_terms_01(N: int, coupling_indices: Sequence[Tuple[int, int]], 
                               coupling_values: Sequence[complex]) -> qt.Qobj:
    """
    Constructs a sum of correlated terms using raising and lowering operators.

    Inputs:
        - N: Total number of qubits.
        - coupling_indices: List of index pairs indicating coupled qubits.
        - coupling_values: Coupling strengths for each pair (real or complex).

    Output:
        - The correlated operator sum as a Qobj.
    """
    op_corr_AB = 0
    for k, pair in enumerate(coupling_indices):
        op_corr_AB += coupling_values[k] * pair_many_qubit_operator(N, pair[0], pair[1], sp, sm)
        op_corr_AB += np.conj(coupling_values[k]) * pair_many_qubit_operator(N, pair[0], pair[1], sm, sp)

    return op_corr_AB



def many_body_hamiltonian_from_local_operators(N: int, list_operators: Sequence[qt.Qobj]) -> qt.Qobj:
    """
    Constructs a many-body Hamiltonian from a list of local operators.

    Inputs:
        - N: Total number of qubits.
        - list_operators: List of local operators acting on each qubit.

    Output:
        - The many-body Hamiltonian as a Qobj.
    """
    Hmb = local_many_qubit_operator(N, 0, list_operators[0]) 
    for j in range(1,N):
        Hmb += local_many_qubit_operator(N, j, list_operators[j])

    return Hmb 



