##########################################################
#
# --- Archivo validadores.py ---
#
# - Última actualización: 12 - 5 - 2026
# - Aporte: Yuliana Morcillo Chatez 

# Descripción: Módulo de validación estricta de datos.
#              Contiene la clase ValidadorDatos con métodos
#              estáticos para verificar correo, teléfono y
#              nombre de servicio antes de que sean asignados
#              a cualquier objeto del sistema.
#
##########################################################

import re  # Módulo de expresiones regulares de Python (built-in)

# Importa la función de registro de advertencias del módulo de log
from log import registrar_evento, NIVEL_WARNING

# Importa la excepción personalizada para errores de datos de cliente
from excepciones import ErrorDatosCliente


class ValidadorDatos:
    """
    Clase utilitaria con validaciones reutilizables.
    Todos sus métodos son estáticos: no necesitan instancia
    de la clase para ser llamados (ValidadorDatos.validar_correo(...)).
    """

    @staticmethod
    def validar_correo(correo: str) -> bool:
        """
        Verifica que el correo tenga formato válido: usuario@dominio.ext
        Usa una expresión regular (regex) para validar la estructura.

        Parámetros:
            correo (str): cadena de texto a validar.

        Retorna:
            True si el correo es válido.

        Lanza:
            ErrorDatosCliente si el formato no coincide con el patrón.
        """
        # Patrón regex: acepta letras, dígitos, punto y guion bajo
        # antes del @, luego dominio con punto y extensión
        patron = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

        # re.match compara desde el inicio de la cadena; se convierte
        # el correo a minúsculas para comparación case-insensitive
        if not re.match(patron, correo.lower()):
            # Registra en el log el intento fallido como advertencia
            registrar_evento(
                f"Validación Fallida: Correo '{correo}'",
                nivel=NIVEL_WARNING
            )
            # Lanza excepción indicando qué campo falló y por qué
            raise ErrorDatosCliente("correo", f"Formato de correo inválido.")

        # Si llegó hasta aquí, el correo es válido
        return True

    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """
        Verifica que el teléfono tenga exactamente 10 dígitos numéricos.
        Esta regla aplica para números de teléfono colombianos.

        Parámetros:
            telefono (str): cadena de texto a validar.

        Retorna:
            True si el teléfono es válido.

        Lanza:
            ErrorDatosCliente si la longitud o los caracteres no son válidos.
        """
        # len(telefono) == 10 verifica la longitud exacta
        # telefono.isdigit() verifica que todos los caracteres sean números
        if not (len(telefono) == 10 and telefono.isdigit()):
            # Registra la advertencia en el archivo de log
            registrar_evento(
                f"Validación Fallida: Teléfono '{telefono}'",
                nivel=NIVEL_WARNING
            )
            # Lanza excepción con el campo y la descripción del error
            raise ErrorDatosCliente(
                "telefono",
                "El teléfono debe tener 10 dígitos numéricos."
            )

        # Si llegó hasta aquí, el teléfono es válido
        return True
    
    @staticmethod
    def validar_nombre_servicio(nombre: str) -> bool:
        """
        Valida la integridad del nombre del servicio.
        Lanza ErrorDatosCliente para detener el flujo del programa si el dato es inválido.
        """
        #Se eliminan espacios para evitar nombres que sean solo "   "
        nombre_limpio = nombre.strip() if nombre else ""

        # Mínimo 4 caracteres para ser un nombre válido
        if len(nombre_limpio) < 4:
            # Se deja rastro del intento fallido
            registrar_evento(
                f"Validación Fallida: Nombre servicio corto '{nombre}'",
                nivel=NIVEL_WARNING
            )
            
            raise ErrorDatosCliente("nombre", "El nombre del servicio debe tener al menos 4 caracteres.")

        # Si llega aquí, el flujo en el main.py continúa normalmente
        return True