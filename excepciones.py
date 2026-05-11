"""
Módulo de Excepciones Personalizadas
Este archivo define errores específicos para el sistema Software FJ
"""

class ErrorSistema(Exception):
    """Clase base para todas las excepciones del sistema."""
    pass

class ErrorDatosCliente(ErrorSistema):
    """Se lanza cuando los datos de un Cliente (nombre, correo, teléfono) son inválidos."""
    def __init__(self, campo, mensaje):
        self.campo = campo
        self.mensaje = mensaje
        super().__init__(f"Error en el campo '{campo}': {mensaje}")

class ErrorCalculoFinanciero(ErrorSistema):
    """Se lanza cuando hay errores en costos, horas o presupuestos."""
    def __init__(self, operacion, mensaje):
        self.operacion = operacion
        self.mensaje = mensaje
        super().__init__(f"Error financiero en '{operacion}': {mensaje}")

class ErrorDisponibilidadServicio(ErrorSistema):
    """Se lanza cuando un servicio (sala, equipo) no está disponible."""
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(f"Disponibilidad: {mensaje}")