import re
from log import registrar_evento, NIVEL_WARNING
from excepciones import ErrorDatosCliente

##########################################################
# Módulo de Validación Estricta - Software FJ
# Aporte: Yuliana Morcillo Chatez
##########################################################

class ValidadorDatos:
    @staticmethod
    def validar_correo(correo: str) -> bool:
        """Valida que el correo tenga un formato real usuario@dominio.com"""
        patron = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.match(patron, correo.lower()):
            # Registra el error en el log
            registrar_evento(f"Validación Fallida: Correo '{correo}'", nivel=NIVEL_WARNING)
            raise ErrorDatosCliente("correo", f"Formato de correo inválido.")
        return True

    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """Valida que el teléfono tenga exactamente 10 números."""
        if not (len(telefono) == 10 and telefono.isdigit()):
            # Registra también este error
            registrar_evento(f"Validación Fallida: Teléfono '{telefono}'", nivel=NIVEL_WARNING)
            raise ErrorDatosCliente("telefono", "El teléfono debe tener 10 dígitos numéricos.")
        return True

    @staticmethod
    def validar_nombre_servicio(nombre: str) -> bool:
        """Evita que el nombre del servicio esté vacío."""
        if len(nombre.strip()) < 4:
            registrar_evento(f"Validación Fallida: Nombre servicio corto '{nombre}'", nivel=NIVEL_WARNING)
            return False
        return True