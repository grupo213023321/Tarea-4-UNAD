##########################################################
#
# --- Archivo classes.py ---
#
# - Ultima actualización: 11 - 5 - 2026
# - Aporte: Daniel Serrano Rivera / Ronald Molina /Camila Meneses / Yuliana Morcillo Chatez
#
# Descripción: Contiene las clases base, excepciones,
#              servicios y reservas del sistema FJ.
#
##########################################################

from abc import ABC, abstractmethod
from datetime import datetime, timedelta   # ← timedelta agregado (faltaba)
from typing import List, Optional
import re
#Nuevas integraciones 
from validadores import ValidadorDatos
from excepciones import ErrorDatosCliente, ErrorCalculoFinanciero, ErrorDisponibilidadServicio

######################################
# CLASES DE EXCEPCIONES PERSONALIZADAS
######################################

class ErrorDatosCliente(Exception):
    """Excepción para fallos en datos del cliente."""
    def __init__(self, campo: str, mensaje: str):
        self.campo = campo
        self.mensaje = mensaje
        super().__init__(f"[Cliente/{campo}] {mensaje}")

class ErrorDisponibilidadServicio(Exception):
    """Excepción para cuando un servicio no puede ser reservado."""
    def __init__(self, mensaje: str):
        super().__init__(f"[Servicio] {mensaje}")

class ErrorCalculoFinanciero(Exception):
    """Excepción para errores en cálculos de costos o IVA."""
    def __init__(self, campo: str, mensaje: str):
        self.campo = campo
        super().__init__(f"[Financiero/{campo}] {mensaje}")

class ErrorReserva(Exception):
    """Excepción para errores en el ciclo de vida de una reserva."""
    def __init__(self, contexto: str, mensaje: str):
        self.contexto = contexto
        super().__init__(f"[Reserva/{contexto}] {mensaje}")

######################################
# CLASE GENERAL ABSTRACTA
######################################

class Entidad(ABC):
    """Clase abstracta raíz del sistema. Toda entidad tiene un ID y fecha de registro."""

    def __init__(self, id_objeto):
        self.id_objeto = id_objeto
        self.fecha_registro = datetime.now()

    @abstractmethod
    def mostrar_info(self) -> str:
        """Método abstracto implementado por cada subclase."""
        pass

######################################
# CLASE CLIENTE
######################################

class Cliente(Entidad):
    """
    Representa un cliente del sistema.
    Implementa encapsulación completa con getters/setters validados.
    """

    def __init__(self, id_sistema, id_cliente, nombre, direccion, correo, telefono):
        super().__init__(id_sistema)
        
        # Se aplican reglas de integridad mediante expresiones regulares (Regex)
        ValidadorDatos.validar_nombre(nombre)
        ValidadorDatos.validar_correo(correo)
        ValidadorDatos.validar_telefono(telefono)

        # Atributos privados
        self.__id_cliente = None
        self.__nombre = None
        self.__direccion = None
        self.__correo = None
        self.__telefono = None

        # Asignación mediante setters (con validación)
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.direccion = direccion
        self.correo = correo
        self.telefono = telefono

    # --- GETTERS Y SETTERS ---

    @property
    def id_cliente(self):
        return self.__id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        if not str(valor).strip():
            raise ErrorDatosCliente("id_cliente", "El ID de cliente es obligatorio.")
        self.__id_cliente = str(valor).strip()

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ErrorDatosCliente("nombre", "El nombre no puede estar vacío.")
        if len(valor.strip()) < 3:
            raise ErrorDatosCliente("nombre", "El nombre debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        if not valor or not valor.strip():
            raise ErrorDatosCliente("direccion", "La dirección no puede estar vacía.")
        self.__direccion = valor.strip()

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        self.__validar_formato_correo(valor)
        self.__correo = valor.strip()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__validar_formato_telefono(valor)
        self.__telefono = str(valor).strip()

    # --- MÉTODOS PRIVADOS DE VALIDACIÓN ---

    def __validar_formato_correo(self, correo):
        if not correo:
            raise ErrorDatosCliente("correo", "El correo electrónico es obligatorio.")
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, correo):
            raise ErrorDatosCliente("correo", f"El formato de correo '{correo}' es inválido.")

    def __validar_formato_telefono(self, telefono):
        if not telefono:
            raise ErrorDatosCliente("telefono", "El número de teléfono es obligatorio.")
        limpio = str(telefono).replace(" ", "").replace("-", "")
        if not limpio.isdigit():
            raise ErrorDatosCliente("telefono", "El teléfono debe contener solo números.")
        if not (7 <= len(limpio) <= 15):
            raise ErrorDatosCliente("telefono", "El teléfono debe tener entre 7 y 15 dígitos.")

    # --- MÉTODOS PÚBLICOS ---

    def mostrar_info(self) -> str:
        return (f"CLIENTE [{self.__id_cliente}] | "
                f"Nombre: {self.__nombre} | "
                f"Correo: {self.__correo} | "
                f"Tel: {self.__telefono}")

    def actualizar_datos(self, **kwargs):
        """Permite actualizar múltiples atributos de forma segura."""
        for clave, valor in kwargs.items():
            if hasattr(self, clave):
                setattr(self, clave, valor)
            else:
                raise AttributeError(f"El atributo '{clave}' no existe en Cliente.")

    def to_dict(self) -> dict:
        return {
            "ID Sistema": self.id_objeto,
            "ID Cliente": self.__id_cliente,
            "Nombre": self.__nombre,
            "Dirección": self.__direccion,
            "Correo": self.__correo,
            "Teléfono": self.__telefono
        }

    def __str__(self):
        return f"Cliente: {self.__nombre} ({self.__id_cliente})"

######################################
# CLASE ABSTRACTA SERVICIO
######################################

class Servicio(Entidad, ABC):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Define la interfaz que deben implementar todas las subclases.
    """

    def __init__(self, id_sistema, nombre, precio_base):
        super().__init__(id_sistema)
        self.__nombre = None
        self.__precio_base = None
        self.nombre = nombre
        self.precio_base = precio_base

    # --- GETTERS Y SETTERS ---

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not str(valor).strip():
            raise ErrorDisponibilidadServicio("El nombre del servicio no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def precio_base(self):
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, valor):
        try:
            valor_float = float(valor)
            if valor_float < 0:
                raise ValueError
            self.__precio_base = valor_float
        except (ValueError, TypeError):
            raise ErrorCalculoFinanciero("precio_base", "El precio base debe ser un número positivo.")

    # --- MÉTODOS ABSTRACTOS ---

    @abstractmethod
    def calcular_costo(self, **kwargs) -> float:
        """Cada subclase implementa su propia fórmula de costo."""
        pass

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Retorna descripción específica del tipo de servicio."""
        pass

    # --- MÉTODOS COMUNES ---

    def mostrar_info(self) -> str:
        return f"SERVICIO: {self.__nombre} | Precio Base: ${self.__precio_base:,.2f}"

    def to_dict(self) -> dict:
        return {
            "ID Sistema": self.id_objeto,
            "Servicio": self.__nombre,
            "Precio Base": self.__precio_base
        }

######################################
# SUBCLASES DE SERVICIOS
######################################

class ReservaSala(Servicio):
    """
    Servicio de reserva de sala de reuniones.
    Costo = precio_base * horas. Si capacidad > 20, recargo del 10%.
    """

    def __init__(self, id_sistema, nombre, precio_base, capacidad, horas):
        super().__init__(id_sistema, nombre, precio_base)
        self.__capacidad = None
        self.__horas = None
        self.capacidad = capacidad
        self.horas = horas

    @property
    def capacidad(self):
        return self.__capacidad

    @capacidad.setter
    def capacidad(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ErrorDisponibilidadServicio("La capacidad de la sala debe ser un entero positivo.")
        self.__capacidad = valor

    @property
    def horas(self):
        return self.__horas

    @horas.setter
    def horas(self, valor):
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ErrorCalculoFinanciero("horas", "La duración debe ser mayor a 0 horas.")
        self.__horas = valor

    def calcular_costo(self, aplicar_iva=True) -> float:
        """Costo = (precio_base * horas). Recargo 10% si capacidad > 20. IVA 19% opcional."""
        subtotal = self.precio_base * self.horas
        if self.__capacidad > 20:
            subtotal *= 1.10
        return round(subtotal * 1.19 if aplicar_iva else subtotal, 2)

    def obtener_detalles(self) -> str:
        return f"Sala para {self.__capacidad} personas | Duración: {self.__horas}h"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "Tipo": "Reserva de Sala",
            "Especificación": f"{self.__capacidad} pers / {self.__horas}h",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d

    def mostrar_info(self) -> str:
        return super().mostrar_info() + f" | {self.obtener_detalles()}"


class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    Costo = precio_base * días + seguro opcional ($50,000).
    """

    def __init__(self, id_sistema, nombre, precio_base, dias, incluye_seguro=False):
        super().__init__(id_sistema, nombre, precio_base)
        self.__dias = None
        self.incluye_seguro = incluye_seguro
        self.dias = dias

    @property
    def dias(self):
        return self.__dias

    @dias.setter
    def dias(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ErrorCalculoFinanciero("dias", "El alquiler debe ser de al menos 1 día.")
        self.__dias = valor

    def calcular_costo(self, descuento=0.0) -> float:
        """Costo = (precio_base * días) + seguro. Descuento opcional en porcentaje (0.0–1.0)."""
        total = self.precio_base * self.__dias
        if self.incluye_seguro:
            total += 50000
        total -= total * descuento
        return round(total, 2)

    def obtener_detalles(self) -> str:
        seguro_str = "Con Seguro" if self.incluye_seguro else "Sin Seguro"
        return f"Equipo: {self.nombre} | Tiempo: {self.__dias} días | {seguro_str}"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "Tipo": "Alquiler Equipo",
            "Especificación": f"{self.__dias} días | Seguro: {self.incluye_seguro}",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d

    def mostrar_info(self) -> str:
        return super().mostrar_info() + f" | {self.obtener_detalles()}"


class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría profesional.
    Costo = precio_base * multiplicador según nivel (Básico, Intermedio, Avanzado).
    """

    NIVELES_VALIDOS = ['Basico', 'Intermedio', 'Avanzado']
    TARIFAS = {'Basico': 1.0, 'Intermedio': 1.5, 'Avanzado': 2.0}

    def __init__(self, id_sistema, nombre, precio_base, consultor, nivel_complejidad):
        super().__init__(id_sistema, nombre, precio_base)
        self.consultor = consultor
        self.__nivel = None
        self.nivel_complejidad = nivel_complejidad

    @property
    def nivel_complejidad(self):
        return self.__nivel

    @nivel_complejidad.setter
    def nivel_complejidad(self, valor):
        if valor not in self.NIVELES_VALIDOS:
            raise ErrorDisponibilidadServicio(
                f"Nivel '{valor}' no válido. Use: {self.NIVELES_VALIDOS}")
        self.__nivel = valor

    def calcular_costo(self) -> float:
        """Costo = precio_base × multiplicador de complejidad."""
        return round(self.precio_base * self.TARIFAS[self.__nivel], 2)

    def obtener_detalles(self) -> str:
        return f"Consultor: {self.consultor} | Nivel: {self.__nivel}"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "Tipo": "Asesoría",
            "Especificación": f"Nivel {self.__nivel} ({self.consultor})",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d

    def mostrar_info(self) -> str:
        return super().mostrar_info() + f" | {self.obtener_detalles()}"

######################################
# CLASE RESERVA
######################################

class Reserva:
    """
    Gestiona el ciclo de vida de una reserva:
    pendiente → confirmada → completada
                            → cancelada
    """

    # Registro global en memoria (sin base de datos)
    todas_las_reservas: List['Reserva'] = []

    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio,
                    fecha_hora: datetime, duracion: float, notas: str = ""):
        self._id = id_reserva
        self.__cliente = cliente
        self.__servicio = servicio
        self.__fecha_hora = fecha_hora
        self.__duracion = duracion
        self.__notas = notas
        self.__estado = "pendiente"
        self._fecha_creacion = datetime.now()

        # Validar disponibilidad antes de aceptar la reserva
        self._validar_disponibilidad(fecha_hora, servicio)

    def _validar_disponibilidad(self, fecha_evaluar: datetime, servicio_evaluar: Servicio):
        """Verifica que no haya solapamiento de horario para el mismo servicio."""
        for r in Reserva.todas_las_reservas:
            if r.estado in ("cancelada", "completada"):
                continue
            if r.servicio.nombre == servicio_evaluar.nombre:
                fin_existente = r.fecha_hora + timedelta(hours=r.duracion)
                if fecha_evaluar < fin_existente:
                    raise ErrorReserva("Disponibilidad",
                                        f"'{servicio_evaluar.nombre}' ya está ocupado en ese horario.")

    # --- GETTERS ---

    @property
    def id(self): return self._id

    @property
    def cliente(self): return self.__cliente

    @property
    def servicio(self): return self.__servicio

    @property
    def fecha_hora(self): return self.__fecha_hora

    @property
    def estado(self): return self.__estado

    @property
    def duracion(self): return self.__duracion

    @property
    def notas(self): return self.__notas

    # --- GESTORES DE ESTADO ---

    def confirmar(self):
        """Cambia estado de pendiente → confirmada."""
        if self.__estado != "pendiente":
            raise ErrorReserva("Estado", "Solo se pueden confirmar reservas pendientes.")
        self.__estado = "confirmada"

    def cancelar(self):
        """Cancela la reserva si no está ya completada."""
        if self.__estado == "completada":
            raise ErrorReserva("Cancelación", "No se puede cancelar una reserva ya completada.")
        self.__estado = "cancelada"

    def procesar(self) -> float:
        """
        Ejecuta la reserva: calcula el costo y la marca como completada.
        Requiere que esté confirmada previamente.
        """
        if self.__estado != "confirmada":
            raise ErrorReserva("Procesamiento", "La reserva debe estar confirmada antes de procesarse.")
        try:
            costo = self.__servicio.calcular_costo()
        except ErrorCalculoFinanciero as e:
            raise ErrorReserva("Financiero", f"Error al procesar costo: {e}") from e
        self.__estado = "completada"
        return costo

    # --- MÉTODO DE FÁBRICA ---

    @classmethod
    def crear_reserva(cls, id_reserva: int, cliente: Cliente, servicio: Servicio,
                        fecha_str: str, hora_str: str, duracion: float, notas: str = "") -> 'Reserva':
        """
        Método de fábrica: convierte strings de fecha/hora a datetime,
        valida que no sea en el pasado y crea la instancia.
        """
        try:
            fecha_dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ErrorReserva("Formato", "Formato de fecha/hora incorrecto. Use YYYY-MM-DD HH:MM.")

        if fecha_dt < datetime.now():
            raise ErrorReserva("Fecha", "La fecha de la reserva no puede estar en el pasado.")

        nueva = cls(id_reserva, cliente, servicio, fecha_dt, duracion, notas)
        cls.todas_las_reservas.append(nueva)
        return nueva

    def __str__(self) -> str:
        return (f"Reserva #{self._id} | {self.__cliente.nombre} | "
                f"{self.__servicio.nombre} | {self.__fecha_hora.strftime('%d/%m/%Y %H:%M')} | "
                f"Estado: {self.__estado} | Duración: {self.__duracion}h")