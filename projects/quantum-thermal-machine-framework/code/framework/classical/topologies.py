from abc import ABC, abstractmethod

class Topology(ABC):
    """
    Classe base abstrata para todas as topologias de conexão entre qubits.
    Define o contrato para que qualquer topologia forneça a lista de pares.
    """
    @abstractmethod
    def get_pairs(self, num_qubits: int) -> list:
        """
        Retorna uma lista de pares de índices de qubits [i, j] que representam as conexões.
        
        Args:
            num_qubits: Número total de qubits no circuito.
            
        Returns:
            Uma lista de pares, por exemplo, [[0, 1], [1, 2], ...].
        """
        pass


class LinearTopology(Topology):
    """
    Topologia linear (cadeia): conecta cada qubit i ao qubit (i + 1).
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, i + 1] for i in range(num_qubits - 1)]


class RingTopology(Topology):
    """
    Topologia em anel: conecta cada qubit ao próximo, fechando o ciclo do último para o primeiro.
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, (i + 1) % num_qubits] for i in range(num_qubits)]


class StarTopology(Topology):
    """
    Topologia em estrela (one_to_all): O qubit central (índice 0) é conectado a todos os outros qubits.
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, 0] for i in range(1, num_qubits)]


class CompleteTopology(Topology):
    """
    Topologia completa (all_to_all): Todos os qubits estão conectados entre si formando um grafo completo.
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, j] for i in range(num_qubits) for j in range(i + 1, num_qubits)]


class CompleteInternalTopology(Topology):
    """
    Topologia completa apenas para qubits internos (all_to_all_bath).
    Exclui os qubits que atuam como banhos térmicos (0 e num_qubits-1).
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [
            [i, j]
            for i in range(1, num_qubits - 1)
            for j in range(i + 1, num_qubits - 1)
        ]


class RainbowTopology(Topology):
    """
    Topologia 'arco-íris': Conexões simétricas das bordas em direção ao centro.
    Exemplo: [0, N-1], [1, N-2], etc.
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, num_qubits - i - 1] for i in range(num_qubits // 2)]


class RingInternalTopology(Topology):
    """
    Topologia em anel restrita apenas aos qubits internos, excluindo os banhos térmicos.
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [
            [i, (i + 1) % (num_qubits - 1)]
            for i in range(1, num_qubits - 1)
        ]


class LinearInternalTopology(Topology):
    """
    Topologia linear restrita apenas aos qubits internos, excluindo os banhos térmicos.
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, i + 1] for i in range(1, num_qubits - 2)]


class PairInternalRainbowTopology(Topology):
    """
    Topologia do tipo Rainbow (arco-íris) apenas para os qubits internos (excluindo os banhos).
    """
    def get_pairs(self, num_qubits: int) -> list:
        return [[i, num_qubits - i - 1] for i in range(1, num_qubits // 2)]
