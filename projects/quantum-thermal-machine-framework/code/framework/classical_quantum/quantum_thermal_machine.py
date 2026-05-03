import pennylane as qml
import qutip as qt

from functools import partial

from framework.quantum.operations import QuantumOperation

class QuantumThermalMachine:
    """
    Construção e execução unificada de circuitos quânticos parametrizados para 
    a simulação termodinâmica do motor quântico.

    Responsável por gerenciar o dispositivo (`qml.device`), unificando o uso das classes de
    `QuantumOperation` nos QNodes internos do PennyLane. Substitui a passagem
    livre de funções isoladas por instâncias estritas do tipo `QuantumOperation`.
    """

    def __init__(
        self,
        num_qubits: int = 2,
        shot=None,
        type_dev: str = "lightning.qubit",
        backend_dev=None,
    ):
        """
        Inicializa a Máquina Térmica e seus nós quânticos (QNodes).

        Args:
            num_qubits: O número de qubits do circuito em simulação.
            shot: Modifica a simulação para tiros discretos se não for None.
            type_dev: Tipo de dispositivo PennyLane local.
            backend_dev: Se usado, designará um backend externo, como a IBM Quantum.
        """
        self.num_qubits = num_qubits
        self.shot = shot

        # Configuração flexível do simulador quântico
        if shot is None:
            self.dev = qml.device(type_dev, wires=self.num_qubits)
        elif backend_dev is None:
            self.dev = qml.device(type_dev, wires=self.num_qubits, shots=shot)
        else:
            self.dev = qml.device(type_dev, wires=self.num_qubits, shots=shot, backend=backend_dev)

        # Registro e compilação das subrotinas como QNodes reais do Pennylane.
        self._initial_state_node = qml.QNode(self.__initial_state_circuit, self.dev)
        self._final_state_node = qml.QNode(self.__final_state_circuit, self.dev)
        self._swap_node = qml.QNode(self.__swap_circuit, self.dev)

    # ----------------------------------------------------------------------
    # Internals: Pennylane QNodes 
    # (Definição dos circuitos executados internamente)
    # ----------------------------------------------------------------------

    def __initial_state_circuit(self, thermal_op: QuantumOperation, corr_op: QuantumOperation):
        """
        Circuito quântico interno para preparar o estado de correlação inicial ρ₀ de equilíbrio.
        """
        if thermal_op:
            thermal_op.apply(self.num_qubits)
        if corr_op:
            corr_op.apply(self.num_qubits)
        return qml.state()

    def __final_state_circuit(self, thermal_op: QuantumOperation, corr_op: QuantumOperation, work_op: QuantumOperation):
        """
        Circuito quântico interno que encadeia a termalização, a correlação e a evolução de extração de trabalho.
        """
        if thermal_op:
            thermal_op.apply(self.num_qubits)
        if corr_op:
            corr_op.apply(self.num_qubits)
        if work_op:
            work_op.apply(self.num_qubits)
        return qml.state()

    def __swap_circuit(self, rho, work_op: QuantumOperation):
        """
        Circuito de Swap/Trabalho. Inicializa com base em uma matriz de densidade de estado
        comum da biblioteca QuTiP (ρ₀) e extrai ou converte trabalho sobre ela.
        """
        wires_list = list(range(self.num_qubits))
        # Inicialização arbitrária usando o ket expandido proveniente do QuTiP
        qml.StatePrep(rho.full().reshape(2 ** self.num_qubits), wires=wires_list)
        work_op.apply(self.num_qubits)
        return qml.state()

    # ----------------------------------------------------------------------
    # API Pública 
    # (Envelopa os QNodes retornando diretamente o StateVector compilado)
    # ----------------------------------------------------------------------

    def get_initial_state(self, thermal_op: QuantumOperation, corr_op: QuantumOperation):
        """
        Compila e devolve o StateVector representativo estado de repouso quântico ρ₀.
        
        Args:
            thermal_op: Operação de termalização instanciada.
            corr_op: Operação construtora de emaranhamento instanciada.
        """
        return self._initial_state_node(thermal_op, corr_op)

    def get_final_state(self, thermal_op: QuantumOperation, corr_op: QuantumOperation, work_op: QuantumOperation):
        """
        Devolve o StateVector representativo do estado final de trabalho concluído ρ_f.
        """
        return self._final_state_node(thermal_op, corr_op, work_op)

    def apply_work_operator(self, rho: qt.Qobj, work_op: QuantumOperation):
        """
        Inicializa a função de extração de ergotropia sobre um Qobj local do QuTiP 
        e retorna seu vetor de estado evoluído termodinamicamente após ação do `work_op`.
        """
        return self._swap_node(rho, work_op)

    def draw(self, circuit_fn, *args, **kwargs):
        """
        Exibe o rascunho visual do circuito usando Matplotlib sobre o Pennylane.
        """
        qml.draw_mpl(circuit_fn)(*args, **kwargs)

    def compiled_ibm(self, circuit):
        """
        Compila um dado circuito ajustando a base de portas ('basis_set') e simplificando
        o design para execução nativa no hardware quântico oficial da IBM Quantum.
        """
        return qml.compile(
            circuit,
            pipeline=[
                partial(qml.transforms.commute_controlled, direction="left"),
                partial(qml.transforms.merge_rotations, atol=1e-6),
                qml.transforms.cancel_inverses,
            ],
            basis_set=["CNOT", "SX", "RZ"],
            num_passes=4,
        )
