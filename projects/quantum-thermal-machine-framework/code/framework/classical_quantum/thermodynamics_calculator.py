import qutip

class ThermodynamicsCalculator:
    """
    Classe utilitária para centralizar e computar métricas de termodinâmica quântica.
    Como os cálculos usam as matrizes de densidade já reduzidas, esta classe não guarda estado.
    """
    
    @staticmethod
    def compute_average_work(
        rho_0: qutip.Qobj,
        rho_f: qutip.Qobj,
        H_0: qutip.Qobj,
        H_f: qutip.Qobj,
    ) -> float:
        """
        Calcula o trabalho médio exercido no sistema quântico durante o ciclo da máquina.

        Definição de Trabalho (W):
        O Trabalho corresponde à variação do valor esperado do Hamiltoniano do sistema
        antes e depois da operação de SWAP ou Evolução correspondente.
            W = <H_f>_ρ_f − <H_0>_ρ_0

        Args:
            rho_0: Matriz de densidade antes da extração de trabalho; estado preparado (Qobj do QuTiP).
            rho_f: Matriz de densidade final após o operador termodinâmico evoluir (Qobj).
            H_0: Hamiltoniano inicial de referência (Qobj).
            H_f: Hamiltoniano final para referência do esperado (Qobj).

        Returns:
            Trabalho médio extraído em float. Caso seja negativo, trabalho foi introduzido.
        """
        # qutip.expect extrai o traço do produto: Tr(H * rho)
        return qutip.expect(H_f, rho_f) - qutip.expect(H_0, rho_0)
