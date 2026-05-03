import pennylane as qml

from abc import ABC, abstractmethod

class ObservableBuilder(ABC):
    """
    Classe base abstrata responsável por montar o Observável (Hamiltoniano)
    de acordo com as restrições da mecânica quântica usando o Pennylane.
    """
    def __init__(self, pairs: list, coupling_constants: list):
        self.pairs = pairs
        self.coupling_constants = coupling_constants

    @abstractmethod
    def build(self):
        """
        Constrói e retorna o Observável completo do Pennylane.
        Este observável pode ser derivado e integrado aos cálculos de Work e Heat.
        """
        pass


class HeisenbergXX(ObservableBuilder):
    """
    Constrói o Observável para o modelo Heisenberg nas componentes XX.
    """
    def build(self):
        ops = [qml.X(pair[0]) @ qml.X(pair[1]) for pair in self.pairs]
        return qml.dot(self.coupling_constants, ops)


class HeisenbergXY(ObservableBuilder):
    """
    Constrói o Observável para o modelo Heisenberg nas componentes XY.
    Exige que `coupling_constants` possua 2 elementos (acoplamento em Y e em X)
    para cada par de topologia passado.
    """
    def build(self):
        ops = []
        for pair in self.pairs:
            ops.append(qml.Y(pair[0]) @ qml.Y(pair[1]))
            ops.append(qml.X(pair[0]) @ qml.X(pair[1]))
        return qml.dot(self.coupling_constants, ops)


class IsotropicHeisenberg(ObservableBuilder):
    """
    Constrói o Observável para o modelo Heisenberg isotrópico XYZ.
    Exige que `coupling_constants` possua 3 elementos (X, Y e Z) por par de qubits.
    """
    def build(self):
        ops = []
        for pair in self.pairs:
            ops.append(qml.X(pair[0]) @ qml.X(pair[1]))
            ops.append(qml.Y(pair[0]) @ qml.Y(pair[1]))
            ops.append(qml.Z(pair[0]) @ qml.Z(pair[1]))
        return qml.dot(self.coupling_constants, ops)
