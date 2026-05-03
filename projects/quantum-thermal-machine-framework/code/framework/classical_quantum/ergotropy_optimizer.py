import numpy as np
import qutip as qt

from qutip_qip.operations import cnot

from framework.classical.topologies import Topology
from framework.classical_quantum.quantum_thermal_machine import QuantumThermalMachine
from framework.classical_quantum.thermodynamics_calculator import ThermodynamicsCalculator
from framework.quantum.operations import CorrelationOperation, ThermalizationOperation, WorkOperation

class ErgotropyOptimizer:
    """
    Otimizador de circuitos quânticos dedicado a maximizar a extração de ergotropia
    das baterias (sistemas quânticos termalizados).

    Utiliza um motor empírico de backpropagation customizado, que calcula a diferença 
    do trabalho por diferenças finitas para buscar os parâmetros do Hamiltoniano de
    Extração (`WorkOperation`, tal como `TrotterizedHeisenbergXX`) usando otimizador Adam.
    """

    def __init__(
        self,
        rho_0: qt.Qobj,
        H_i: qt.Qobj,
        H_f: qt.Qobj,
        num_qubits: int = 2,
        epsilon: float = 1e-5,
        learning_rate: float = 0.01,
        beta1: float = 0.9,
        beta2: float = 0.999,
        adam_epsilon: float = 1e-8,
        num_epochs: int = 100,
        tol: float = 1e-3,
        bath: bool = True,
    ):
        """
        Inicializa os hiper-parâmetros do modelo Adam e o sistema quântico base.

        Args:
            rho_0 (qt.Qobj): Matriz de estado da bateria original (pré-otimização).
            H_i (qt.Qobj): Hamiltoniano inicial do sistema (usado para o cálculo do trabalho).
            H_f (qt.Qobj): Hamiltoniano final, podendo referenciar extração diferente na simulação.
            num_qubits (int): Contagem de qubits que ditará as matrizes do PennyLane e QuTiP.
            epsilon: Escalar epsilon utilizado para calcular o gradiente finito central.
            learning_rate: A taxa de salto para o atualizador estocástico Adam.
            beta1, beta2: Momentos do otimizador Adam.
            adam_epsilon: Prevenção estatística a divisões por zero durante o backpropagation.
            num_epochs: Definição de limite de épocas antes do early stop forçado.
            tol: Tolerância da curva de perda de forma a ativar o "Early Stop".
            bath: Parâmetro boleano; se os banhos quânticos estiverem instanciados, não aplica
                  o traço sobre todo o espaço de Hilbert (não influencia o trabalho atual).
        """
        self.num_qubits = num_qubits
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.tol = tol
        self.rho_0 = rho_0
        self.beta1 = beta1
        self.beta2 = beta2
        self.adam_epsilon = adam_epsilon

        self.trace = (
            list(range(1, num_qubits - 1)) if bath else list(range(num_qubits))
        )

        self.H_i = H_i
        self.H_f = H_f

        # Como os observáveis costumam ser definidos apenas no subsistema da bateria, é
        # forçada uma correção com produto tensorial adicionando um 'olho' quântico
        # nos contornos, igualizando a dimensionalidade efetiva ao circuito como um todo.
        self.H_eff = qt.tensor(qt.qeye(2), qt.tensor(self.H_f, qt.qeye(2)))

        self.machine = QuantumThermalMachine(num_qubits)

    def __apply_optimize(
        self, 
        work_operation_class: WorkOperation, 
        work_topology: list, 
        initial_params: np.ndarray
    ):
        """
        Executa os ciclos de iteração do otimizador Adam maximizando o Work (Ergotropia).
        Para cada época, os parâmetros da operação quântica são modificados por gradiente
        central (variação + epsilon e variação - epsilon) e em seguida atualizados
        com as taxas de decaimento do modelo Adam.
        
        Args:
            work_op_class: Uma subclasse herdando de `WorkOperation` em que a busca se baseia
                           ex: TrotterizedHeisenbergXYZ dependente de acoplamentos.
            pair_work: Configurações em matriz pareada `[i, j]` direcionando o Swap/Trabalho.
            initial_params: Conjectura do peso numérico inicial iterativo antes do Start.
            
        Returns:
            tuple:
                - params (numpy.ndarray): Pesos dos acoplamentos finais alcançados.
                - loss_vec (list): Registo de Ergotropia obtida a cada época da simulação.
                - final_loss (float): A Ergotropia avaliada final.
        """
        params = initial_params.copy()
        
        # Históricos momentâneos Adam m1 e m2 (ambos zerados)
        m = np.zeros(len(params))
        v = np.zeros(len(params))

        epoch = 0
        loss = 1.0
        loss_vec = []
        flag = -1.0 # Usado para checar "tol" de parada prematura (Early Stop)

        # Dimensionalidade requerida ao sistema no formato base (Ket) QuTiP.
        dimension = [cnot(self.num_qubits, 0, 1).dims[0], [1]]
        initial_state = qt.Qobj(self.rho_0, dims=dimension)

        # Ciclo principal de gradient-descent Adam
        while self.num_epochs > epoch and abs(loss - flag) > self.tol:
            epoch += 1
            flag = loss

            for j in range(len(params)):
                
                # Derivada analógica: Derivada por diferenças finitas centrais
                params_plus = params.copy()
                params_plus[j] += self.epsilon

                params_minus = params.copy()
                params_minus[j] -= self.epsilon

                work_op_plus = work_operation_class(work_topology, params_plus)
                work_op_minus = work_operation_class(work_topology, params_minus)

                # Avalia o work numérico real positivo (+Epsilon)
                state_p = qt.Qobj(
                    self.machine.apply_work_operator(initial_state, work_op_plus),
                    dims=dimension,
                )
                
                # Avalia o work numérico real negativo (-Epsilon)
                state_m = qt.Qobj(
                    self.machine.apply_work_operator(initial_state, work_op_minus),
                    dims=dimension,
                )

                gradient = ThermodynamicsCalculator.compute_average_work(
                    state_m, state_p, self.H_eff, self.H_eff
                )
                
                # Encontramos a inclinação gradiente aproximada dividindo os estados centrais pela taxa.
                gradient_real = np.real(gradient) / (2 * self.epsilon)

                # Atualiza pesos momentâneos (Momento Estocástico de Primeira e Segunda Ordem)
                m[j] = self.beta1 * m[j] + (1 - self.beta1) * gradient_real
                v[j] = self.beta2 * v[j] + (1 - self.beta2) * (gradient_real ** 2)

                m_hat = m[j] / (1 - self.beta1 ** epoch)
                v_hat = v[j] / (1 - self.beta2 ** epoch)

                # Desconta o avanço com a taxa de aprendizado normalizada
                params[j] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.adam_epsilon)

            # Reavalia e salva a perda termodinâmica atual com os parâmetros normalizados globais
            work_op_f = work_operation_class(work_topology, params)
            state_f = qt.Qobj(
                self.machine.apply_work_operator(initial_state, work_op_f),
                dims=dimension,
            )
            
            loss = ThermodynamicsCalculator.compute_average_work(initial_state, state_f, self.H_eff, self.H_eff)
            loss_vec.append(float(np.real(loss)))

        return params, loss_vec, float(np.real(loss))

    def optimize(
            num_qubits: int, 
            thermalization_operation_class: ThermalizationOperation, 
            correlation_operation_class: CorrelationOperation, 
            work_operation_class: WorkOperation, 
            correlation_topology: list, 
            work_topology: list,
            H_AB, params_ther, params_corr):
        machine = QuantumThermalMachine(num_qubits=num_qubits)
        thermal_op = thermalization_operation_class(params_ther[0], params_ther[1])
        corr_op = correlation_operation_class(correlation_topology, params_corr)

        initial_state_vec = machine.get_initial_state(thermal_op, corr_op)
        rho = qt.Qobj(initial_state_vec)

        optimizer = ErgotropyOptimizer(
            rho_0=rho, H_i=H_AB, H_f=H_AB, num_qubits=num_qubits, 
            learning_rate=0.005, num_epochs=10000, tol=0.0000001
        )

        initial_params = np.random.random(len(work_topology))  # Parâmetros iniciais genéricos para otimização
        params, loss_vec, ergotropy = optimizer.__apply_optimize(work_operation_class, work_topology, initial_params)

        return ergotropy, params, loss_vec