"""
##########################################################
#
# --- Archivo excepciones.py ---
#
# - Última actualización: 12 - 5 - 2026
# 
#
# Descripción: Define todas las excepciones personalizadas
#              del sistema Software FJ. Cada excepción
#              hereda de ErrorSistema (clase base propia),
#              que a su vez hereda de la clase built-in
#              Exception de Python.
#
##########################################################
"""

# ─── Clase base de excepciones del sistema ────────────────

class ErrorSistema(Exception):
    """
    Clase raíz de todas las excepciones personalizadas del sistema.
    Al heredar de Exception, permite capturar cualquier error
    del sistema con un solo bloque 'except ErrorSistema'.
    """
    pass  # No agrega lógica propia; es un marcador de jerarquía


# ─── Error en datos del cliente ───────────────────────────

class ErrorDatosCliente(ErrorSistema):
    """
    Se lanza cuando los datos de un Cliente son inválidos.
    Casos de uso: nombre vacío, correo mal formado, teléfono
    con caracteres no numéricos o longitud incorrecta.
    """

    def __init__(self, campo, mensaje):
        # Guarda el campo específico que falló (ej: "correo", "telefono")
        self.campo = campo

        # Guarda el mensaje descriptivo del error
        self.mensaje = mensaje

        # Llama al constructor de Exception con un mensaje formateado
        # que combina el campo y la descripción del error
        super().__init__(f"Error en el campo '{campo}': {mensaje}")


# ─── Error en cálculos financieros ────────────────────────

class ErrorCalculoFinanciero(ErrorSistema):
    """
    Se lanza cuando hay errores en costos, horas o presupuestos.
    Casos de uso: precio negativo, horas en cero, días de
    alquiler inválidos.
    """

    def __init__(self, operacion, mensaje):
        # Guarda el nombre de la operación financiera que falló
        # (ej: "precio_base", "horas", "dias")
        self.operacion = operacion

        # Guarda el mensaje descriptivo del error
        self.mensaje = mensaje

        # Construye el mensaje final combinando operación y detalle
        super().__init__(f"Error financiero en '{operacion}': {mensaje}")


# ─── Error de disponibilidad de servicio ──────────────────

class ErrorDisponibilidadServicio(ErrorSistema):
    """
    Se lanza cuando un servicio (sala, equipo) no está disponible
    o sus parámetros de configuración son inválidos.
    Casos de uso: capacidad de sala en cero, nivel de asesoría
    no reconocido, nombre de servicio vacío.
    """

    def __init__(self, mensaje):
        # Guarda el mensaje descriptivo de por qué no está disponible
        self.mensaje = mensaje

        # Construye el mensaje con prefijo "Disponibilidad:" para
        # facilitar la identificación en los logs
        super().__init__(f"Disponibilidad: {mensaje}")