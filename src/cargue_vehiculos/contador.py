"""Contador de operaciones elementales del cargue de vehículos."""


class Contador:
    """Lleva la cuenta de las operaciones elementales de un algoritmo.

    Se pasa como argumento opcional a cada solución. Cuando se cronometra se
    pasa None, para que contar no ensucie el tiempo medido.
    """

    def __init__(self) -> None:
        """Crea un contador en cero."""
        self.total = 0

    def sumar(self, cantidad: int = 1) -> None:
        """Suma operaciones al contador.

        Args:
            cantidad: número de operaciones elementales que se agregan.
        """
        self.total += cantidad
