import concurrent.futures
import numpy as np
import matplotlib.pyplot as plt

from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from scipy.linalg import expm

# Importações dos módulos do framework
from framework.quantum.single_qubit_operators import single_qubit_Hamiltonian
from framework.quantum.many_qubit_operators import many_body_hamiltonian_from_local_operators
from framework.classical.topologies import LinearTopology, RainbowTopology
from framework.quantum.operations import CorrelationOperation, ThermalizationOperation, ImaginaryParametricCorrelation, TrotterizedHeisenbergXX, WorkOperation
from framework.classical_quantum.ergotropy_optimizer import ErgotropyOptimizer

def calculate_ergotropy(
        process_index, 
        num_qubits: int, 
        thermalization_operation_class: ThermalizationOperation, 
        correlation_operation_class: CorrelationOperation, 
        work_operation_class: WorkOperation, 
        correlation_topology: list, 
        work_topology: list,
        e_a, e_b, beta_A, beta_B_list):
    """
    Função que encapsula o trabalho para um único valor de e_B.
    Será executada por um processo separado.
    Retorna os resultados Ws_XX para esta fatia de e_B.
    """

    half = num_qubits // 2

    e_list = [e_a] * half + [e_b] * half

    H_AB_list = [0 for _ in range(num_qubits)]

    for i in range(half):
        H_A = single_qubit_Hamiltonian(e_list[i])
        H_B = single_qubit_Hamiltonian(e_list[i + half])

        H_AB_list[i] = (H_A)
        H_AB_list[i + half] = (H_B)

    H_AB_list = H_AB_list[1:-1]

    H_AB = many_body_hamiltonian_from_local_operators(num_qubits - 2, H_AB_list)

    e_B_XX_results = np.zeros(len(beta_B_list))

    # 1. Crie um array para armazenar os parâmetros (o tamanho é len(work_topology))
    num_params_XX = len(work_topology)
    e_B_XX_results_params = np.zeros((len(beta_B_list), num_params_XX))

    for b_index, beta_B in enumerate(beta_B_list):

        b_B = beta_B
        b_A = beta_A

        theta_A, theta_B = 2 * np.arctan(np.exp(e_b * b_B * 0.5)), 2 * np.arctan(np.exp(e_a * b_A * 0.5))

        sz = np.array([[1, 0], [0, -1]])

        H_A = -0.5 * e_a * sz
        H_B = -0.5 * e_b * sz

        Za = np.trace(expm(-b_A * H_A))
        Zb = np.trace(expm(-b_B * H_B))

        p_a = np.exp(-e_a * b_A / 2) / Za
        p_b = np.exp(-e_b * b_B / 2) / Zb

        p00 = p_a * p_b
        p01 = p_a * (1 - p_b)
        p10 = p_b * (1 - p_a)
        p11 = (1 - p_b) * (1 - p_a)

        a = 1 / (Za * Zb)

        numero1 = 2 * a / (p00 - p10)
        numero2 = 2 * a / (p01 - p11)

        if abs(numero1) > 1:
            numero1 = 1
        if abs(numero2) > 1:
            numero2 = 1

        theta, phi = np.arcsin(numero1) / 2, np.arcsin(numero2) / 2

        ws_xx, params_XX, loss_vec = ErgotropyOptimizer.optimize(
            num_qubits=num_qubits, 
            thermalization_operation_class=thermalization_operation_class, 
            correlation_operation_class=correlation_operation_class, 
            work_operation_class=work_operation_class, 
            work_topology=work_topology,
            correlation_topology=correlation_topology,
            H_AB=H_AB, 
            params_ther=[theta_A, theta_B], 
            params_corr=[theta, phi] * len(correlation_topology)
        )

        e_B_XX_results[b_index] = ws_xx

        e_B_XX_results_params[b_index,:] = params_XX

    return process_index, e_B_XX_results, e_B_XX_results_params

def plot_results(e_Bs, e_A, beta_B_list, beta_A, Ws_XX):

    # Configuração da Matplotlib Latex
    plt.rc('font', **{'weight': 'bold', 'size': 16})

    # Plotando os resultados de Ws_XX para ns = 0 (N = 4)
    plt.figure(figsize=(10, 6))
    
    # Eb values na abscissa (pois e_A = 1, então x = e_B / e_A)
    x_axis = e_Bs / e_A
    
    for bb, beta_B in enumerate(beta_B_list):
        # A razão beta_B / beta_A
        beta_ratio = beta_B / beta_A
        # Valores de Ws_XX para todo eb_index com o beta_index específico
        y_values = Ws_XX[0, :, bb] 
        
        plt.plot(
            x_axis, 
            y_values, 
            marker='o', 
            linestyle='-', 
            label=f'$\\beta_B/\\beta_A={beta_ratio:.2f}$'
        )

    plt.xlabel(r'$\epsilon_B / \epsilon_A$')
    plt.ylabel(r'$W_{s}^{XX}$')
    plt.title(r'Best $W_{s}^{XX}$ vs $\epsilon_B / \epsilon_A$ for different $\beta_B / \beta_A$')
    plt.legend()
    plt.grid(True)
    
    # Salvar o gráfico e mostrar (caso em ambiente iterativo)
    plt.savefig('Ws_XX_plot.png', dpi=300, bbox_inches='tight')
    print("Gráfico do Ws_XX salvo como 'Ws_XX_plot.png'")
    # Não chamamos plt.show() em um .py executado em background para não travar o terminal, 
    # mas caso precise descomente:
    # plt.show()

# FLUXO (0): Início do programa. 

# OBS: Usando o Hamiltoniano XX.

if __name__ == "__main__":

    # CONFIGURAÇÕES INICIAIS PARA O PROGRAMA
    
    N_QUBITS = 4
    THERMALIZATION_OPERATION_CLASS = ThermalizationOperation
    CORRELATION_OPERATION_CLASS = ImaginaryParametricCorrelation
    WORK_OPERATION_CLASS = TrotterizedHeisenbergXX
    CORRELATION_TOPOLOGY_CLASS = RainbowTopology
    WORK_TOPOLOGY_CLASS = LinearTopology

    # FLUXO (1): Criando os parâmetros para serem passados para as máquinas.

    # ESPECIFICO =======================

    beta_A = 1
    e_A = 1

    # variables for countor plots
    beta_B_list = [1.1, 1.25, 1.5, 2]
    beta_B_list_len = len(beta_B_list)

    partitions = 21
    e_B_list = np.linspace(0.1, 1.5, partitions)

    # FIM_ESPECIFICO =======================

    # Defina os tamanhos (num_qubits) de cada máquina térmica.
    n_qubits_per_machine = [N_QUBITS] 
    n_machines = len(n_qubits_per_machine)

    # Listas para armazenar os resultados de W_XX para cada máquina, e para cada combinação de e_B e beta_B
    W_list_XX = np.zeros((n_machines, partitions, beta_B_list_len))

    # FLUXO (2): Roda uma quantidade x de máquinas térmicas. Elas tem o tamanho N, passado pelo vetor Ns. 
    # Para cada máquina térmica, roda um loop.

    # Loop para cada máquina térmica (cada tamanho N)
    for n_index, num_qubits in enumerate(tqdm(n_qubits_per_machine, desc="Processando num_qubits")):
        # FLUXO (3): Escolher as topologias de correlação e trabalho para num_qubits.

        # CUSTOMIZAVEL =======================

        correlation_topology = CORRELATION_TOPOLOGY_CLASS().get_pairs(num_qubits)
        work_topology = WORK_TOPOLOGY_CLASS().get_pairs(num_qubits) 

        # FIM_CUSTOMIZAVEL ======================= 

        # FLUXO (4): Redefine o array de parâmetros a cada iteração de N (se N mudar). 
        # Cria uma matriz com 0's para armazenar os parâmetros.
        num_params = len(work_topology)

        # FLUXO (5): Define um array para armazenar os parâmetros do Hamiltoniano (XX, XY, XYZ...)
        params_XX_N = np.zeros((partitions, beta_B_list_len, num_params))

        # FLUXO (6): Roda em paralela cada
        with ProcessPoolExecutor() as executor:
            # Mapeia a função `calculate_ergotropy` para cada item em `e_B_list`
            # `tqdm` é usado para mostrar o progresso do ProcessPoolExecutor

            # FLUXO (7): Cria varios processos com os diferentes parâmetros definidos
            # Essas instâncias são processadas em paralelo usando ProcessPoolExecutor.
            process_list = [executor.submit(calculate_ergotropy, process_index, num_qubits, THERMALIZATION_OPERATION_CLASS, CORRELATION_OPERATION_CLASS, WORK_OPERATION_CLASS, correlation_topology, work_topology, e_A, e_B, beta_A, beta_B_list)
                       for process_index, e_B in enumerate(e_B_list)]

            # FLUXO (8): Conforme cada processo termina, os resultados são coletados e armazenados.
            for process in tqdm(concurrent.futures.as_completed(process_list), total=len(process_list), desc=f"Paralelizando e_Bs para E_A={e_A:.2f}"):
                e_B_index, W_XX_for_e_B, results_params_XX_for_e_B = process.result()

                W_list_XX[n_index, e_B_index, :] = W_XX_for_e_B

                params_XX_N[e_B_index,:,:] = results_params_XX_for_e_B

    print("Cálculos concluídos!")

    plot_results(e_B_list, e_A, beta_B_list, beta_A, W_list_XX)