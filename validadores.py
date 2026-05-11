import re
from classes import ErrorDatosCliente

##########################################################
# Módulo de Validación Estricta - Software FJ
# Aporte: Yuliana Morcillo Chatez
##########################################################

class ValidadorDatos:
    @staticmethod
    def validar_correo(correo: str) -> bool:
        """Valida que el correo tenga un formato real usuario@dominio.com"""
        patron = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.match(patron, correo.lower()):
            raise ErrorDatosCliente(f"Formato de correo inválido: '{correo}'")
        return True

    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """Valida que el teléfono tenga exactamente 10 números."""
        if not (len(telefono) == 10 and telefono.isdigit()):
            raise ErrorDatosCliente("El teléfono debe tener 10 dígitos numéricos.")
        return True

    @staticmethod
    def validar_nombre_servicio(nombre: str) -> bool:
        """Evita que el nombre del servicio esté vacío."""
        if len(nombre.strip()) < 4:
            return False
        return True