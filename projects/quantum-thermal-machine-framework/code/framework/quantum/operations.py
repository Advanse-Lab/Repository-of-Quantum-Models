import numpy as np
import pennylane as qml

from abc import ABC, abstractmethod

class QuantumOperation(ABC):
    """
    Classe base abstrata para todas as operações aplicadas em um circuito quântico.
    Obriga a implementação do método `apply` que executará as portas quânticas.
    """
    @abstractmethod
    def apply(self, num_qubits: int):
        """
        Aplica a operação quântica correspondente ao circuito. 
        Este método deve ser chamado apenas DEBTRO de um QNode (função decorada por qml.qnode).
        
        Args:
            num_qubits (int): Número total de qubits presentes no circuito para dimensionar as portas.
        """
        pass


class ThermalizationOperation(QuantumOperation):
    """
    Operação de termalização.
    Aplica rotações nos qubits das extremidades (que funcionam como banhos térmicos)
    e espalha o emaranhamento para o interior do sistema através de portas CNOT.
    """
    def __init__(self, theta_a: float, theta_b: float):
        self.theta_a = theta_a
        self.theta_b = theta_b

    def apply(self, num_qubits: int):
        # Rotações nos qubits das bordas simulando interação com banhos quentes/frios
        qml.RX(self.theta_a, wires=0)
        qml.RX(self.theta_b, wires=num_qubits - 1)

        # CNOTs simétricos para espalhar a termalização pelo sistema de qubits iterativos
        for i in range(1, int(num_qubits / 2)):
            qml.CNOT(wires=[0, i])
            qml.CNOT(wires=[num_qubits - 1, num_qubits - (i + 1)])


class CorrelationOperation(QuantumOperation):
    """
    Classe base para operações de correlação que dependem de uma lista de pares de qubits.
    """
    def __init__(self, pairs: list):
        self.pairs = pairs


class IsotropicCorrelation(CorrelationOperation):
    """
    Aplica uma correlação fixa (unitária) entre os pares de qubits utilizando CNOT 
    e uma porta controlada unitária com matriz fixa já estabelecida.
    """
    def __init__(self, pairs: list):
        super().__init__(pairs)
        # Matriz unitária baseada no modelo isotrópico anterior
        self._U = np.array([[0.632, 0.774], [0.774, 0.632]])

    def apply(self, num_qubits: int):
        for pair in self.pairs:
            qml.CNOT(wires=[pair[0], pair[1]])
            qml.ctrl(qml.QubitUnitary(self._U, wires=[pair[0]]), control=[pair[1]])
            qml.CNOT(wires=[pair[0], pair[1]])


class ParametricCorrelation(CorrelationOperation):
    """
    Aplica uma correlação paramétrica usando rotações RY dependentes de theta e phi.
    Exige 2 parâmetros paramétricos para cada par de correlação.
    """
    def __init__(self, pairs: list, params: list):
        super().__init__(pairs)
        if len(params) != 2 * len(pairs):
            raise ValueError("Esperados exatamente 2 parâmetros (theta, phi) por par.")
        self.params = params

    def apply(self, num_qubits: int):
        for i, pair in enumerate(self.pairs):
            theta = self.params[2 * i]
            phi = self.params[2 * i + 1]
            qml.RY(theta + phi, wires=pair[0])
            qml.CNOT(wires=[pair[1], pair[0]])
            qml.RY(theta - phi, wires=pair[0])
            qml.CNOT(wires=[pair[0], pair[1]])


class ImaginaryParametricCorrelation(CorrelationOperation):
    """
    Aplica uma correlação paramétrica similar ao `ParametricCorrelation`, 
    incluindo uma rotação RZ(pi/2) no final para introduzir uma fase imaginária.
    """
    def __init__(self, pairs: list, params: list):
        super().__init__(pairs)
        if len(params) != 2 * len(pairs):
            raise ValueError("Esperados exatamente 2 parâmetros (theta, phi) por par.")
        self.params = params

    def apply(self, num_qubits: int):
        for i, pair in enumerate(self.pairs):
            theta = self.params[2 * i]
            phi = self.params[2 * i + 1]
            qml.RY(theta + phi, wires=pair[0])
            qml.CNOT(wires=[pair[1], pair[0]])
            qml.RY(theta - phi, wires=pair[0])
            qml.CNOT(wires=[pair[0], pair[1]])
            # Introduz a fase imaginária
            qml.RZ(np.pi / 2, wires=pair[1])


class WorkOperation(QuantumOperation):
    """
    Classe base para simular a extração/inserção de trabalho (SWAP) via evolução de tempo 
    usando decomposição de Trotter para Hamiltonianos.
    """
    def __init__(self, pairs: list, time: float = np.pi / 2, n_trotter: int = 4):
        self.pairs = pairs
        self.time = time
        self.n_trotter = n_trotter

    @abstractmethod
    def _get_hamiltonian(self):
        """Retorna o observável PennyLane que representa o Hamiltoniano evolutivo."""
        pass

    @abstractmethod
    def _get_inital_params(self):
        """Retorna os parâmetros iniciais para a otimização, caso necessário."""
        pass

    def apply(self, num_qubits: int):
        H = self._get_hamiltonian()
        # Aplica a evolução paramétrica e^(-iHt)
        qml.ApproxTimeEvolution(H, time=self.time, n=self.n_trotter)


class TrotterizedHeisenbergXX(WorkOperation):
    """
    Evolução do Trabalho baseada apenas na interação Heisenberg-XX.
    """
    def __init__(self, pairs: list, coupling_constants: list, time: float = np.pi / 2, n_trotter: int = 4):
        super().__init__(pairs, time, n_trotter)
        self.coupling_constants = coupling_constants

    def _get_hamiltonian(self):
        ops = [qml.X(pair[0]) @ qml.X(pair[1]) for pair in self.pairs]
        return qml.dot(self.coupling_constants, ops)
    
    def _get_inital_params(self):
        return np.random.random(len(self.pairs))


class TrotterizedHeisenbergXY(WorkOperation):
    """
    Evolução do Trabalho baseada na interação Heisenberg-XY (interações em X e Y separadas).
    A lista `coupling_constants` deve conter parâmetros duplos (YY, XX) para cada par.
    """
    def __init__(self, pairs: list, coupling_constants: list, time: float = np.pi / 2, n_trotter: int = 4):
        super().__init__(pairs, time, n_trotter)
        self.coupling_constants = coupling_constants

    def _get_hamiltonian(self):
        ops = []
        for pair in self.pairs:
            ops.append(qml.Y(pair[0]) @ qml.Y(pair[1]))  # Termo de Y
            ops.append(qml.X(pair[0]) @ qml.X(pair[1]))  # Termo de X
        return qml.dot(self.coupling_constants, ops)
    
    def _get_inital_params(self):
        return np.random.random(2*len(self.pairs))


class TrotterizedHeisenbergXYZ(WorkOperation):
    """
    Evolução do Trabalho baseada no modelo isotrópico de Heisenberg-XYZ completo.
    A lista `coupling_constants` deve conter parâmetros triplos (XX, YY, ZZ) para cada par.
    """
    def __init__(self, pairs: list, coupling_constants: list, time: float = np.pi / 2, n_trotter: int = 4):
        super().__init__(pairs, time, n_trotter)
        self.coupling_constants = coupling_constants

    def _get_hamiltonian(self):
        ops = []
        for pair in self.pairs:
            ops.append(qml.X(pair[0]) @ qml.X(pair[1]))
            ops.append(qml.Y(pair[0]) @ qml.Y(pair[1]))
            ops.append(qml.Z(pair[0]) @ qml.Z(pair[1]))
        return qml.dot(self.coupling_constants, ops)
    
    def _get_inital_params(self):
        return np.random.random(3*len(self.pairs))
