##########################################################
#
# --- Archivo Classes.py ---
#
# - Ultima actualización: 2023-06-30
# - Aporte: Daniel Serrano Rivera
#
##########################################################



from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import re

######################################
# CLASES EXCEPCIONES
######################################

class ErrorDatosCliente(Exception):
    #Excepción para fallos en datos del cliente
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class ErrorDisponibilidadServicio(Exception):
    #Excepción para cuando un servicio no puede ser reservado
    pass

class ErrorCalculoFinanciero(Exception):
    # Excepción para errores en cálculos de costos o IVA
    pass

class ErrorReserva(Exception):
    # Excepción para errores en cálculos de costos o IVA
    pass

######################################
# CLASE GENERAL ABSTRACTA
######################################

class Entidad(ABC):
    def __init__(self, id_objeto):
        self.id_objeto = id_objeto
        self.fecha_registro = datetime.now()

    @abstractmethod
    def mostrar_info(self):
        # Metodo abstracto, lo usara cada clase en su codigo
        pass

######################################
# CLASE CLIENTE
######################################

class Cliente(Entidad):
    def __init__(self, id_sistema, id_cliente, nombre, direccion, correo, telefono):

        super().__init__(id_sistema)
        
        self.__id_cliente = None
        self.__nombre = None
        self.__direccion = None
        self.__correo = None
        self.__telefono = None

        self.id_cliente = id_cliente
        self.nombre = nombre
        self.direccion = direccion
        self.correo = correo
        self.telefono = telefono

    # --- GETTERS Y SETTERS  ---

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
        self.__telefono = valor.strip()

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
        
        # Eliminar espacios o guiones si los hubiera para la validación
        limpio = str(telefono).replace(" ", "").replace("-", "")
        
        if not limpio.isdigit():
            raise ErrorDatosCliente("telefono", "El teléfono debe contener solo números.")
        if not (7 <= len(limpio) <= 15):
            raise ErrorDatosCliente("telefono", "El teléfono debe tener entre 7 y 15 dígitos.")

    # --- MÉTODOS DE INTERACCIÓN CON EL SISTEMA ---

    def mostrar_info(self) -> str:
        """
        Implementación del método abstracto de Entidad.
        Ideal para mostrar en consola, reportes rápidos o logs de auditoría.
        """
        return (f"CLIENTE [{self.__id_cliente}] | "
                f"Nombre: {self.__nombre} | "
                f"Correo: {self.__correo} | "
                f"Tel: {self.__telefono}")

    def actualizar_datos(self, **kwargs):
        """
        Permite actualizar múltiples atributos a la vez de forma segura.
        Ejemplo: cliente.actualizar_datos(nombre="Nuevo Nombre", telefono="3001234567")
        """
        for clave, valor in kwargs.items():
            if hasattr(self, clave):
                setattr(self, clave, valor)
            else:
                raise AttributeError(f"El atributo '{clave}' no existe en la clase Cliente.")

    def to_dict(self) -> dict:
        """
        Vital para la integración con el Treeview de la GUI (gui.py).
        Serializa el estado actual del objeto.
        """
        return {
            "ID Sistema": self.id_objeto,  # Heredado de Entidad
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
    def __init__(self, id_sistema, nombre, precio_base):
        """
        Constructor de la clase abstracta Servicio.
        
        
            id_sistema: id unico generado por el sistema.
            nombre: Nombre descriptivo del servicio.
            precio_base: Valor inicial antes de cálculos adicionales.
        """
        super().__init__(id_sistema)
        
        # Atributos privados
        self.__nombre = None
        self.__precio_base = None
        
        # Uso de setters para validación inicial
        self.nombre = nombre
        self.precio_base = precio_base

    # --- GETTERS Y SETTERS CON VALIDACIÓN ---

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not str(valor).strip():
            raise ErrorDisponibilidadServicio("General", "El nombre del servicio no puede estar vacío.")
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

    # --- MÉTODOS ABSTRACTOS (Obligatorios para las subclases) ---

    @abstractmethod
    def calcular_costo(self, **kwargs) -> float:
        """
        Método abstracto para calcular el costo total. 
        Cada subclase (Sala, Equipo, Asesoría) tendrá su propia fórmula.
        """
        pass

    @abstractmethod
    def obtener_detalles(self) -> str:
        """
        Retorna una descripción técnica específica del tipo de servicio.
        """
        pass

    # --- MÉTODOS COMUNES ---

    def mostrar_info(self):
        """Implementación del método de Entidad."""
        return f"SERVICIO: {self.__nombre} | Precio Base: ${self.__precio_base:,.2f}"

    def to_dict(self):
        """Base para la serialización de servicios hacia la GUI."""
        return {
            "ID Sistema": self.id_objeto,
            "Servicio": self.__nombre,
            "Precio Base": self.__precio_base
        }

######################################
# SUBCLASES DE SERVICIOS
#
# - ReservaSala
# - AlquilerEquipo
# - AsesoriaEspecializada
# 
######################################

class ReservaSala(Servicio):
    def __init__(self, id_sistema, nombre, precio_base, capacidad, horas):
        super().__init__(id_sistema, nombre, precio_base)
        self.__capacidad = None
        self.__horas = None
        
        # Validaciones mediante setters
        self.capacidad = capacidad
        self.horas = horas

    @property
    def capacidad(self):
        return self.__capacidad

    @capacidad.setter
    def capacidad(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ErrorDisponibilidadServicio("La capacidad de la sala debe ser un número entero positivo.")
        self.__capacidad = valor

    @property
    def horas(self):
        return self.__horas

    @horas.setter
    def horas(self, valor):
        if not (isinstance(valor, (int, float))) or valor <= 0:
            raise ErrorCalculoFinanciero("horas", "La duración debe ser mayor a 0 horas.")
        self.__horas = valor

    def calcular_costo(self, aplicar_iva=True) -> float:
        """Costo = (Precio Base * Horas). Si capacidad > 20, recargo del 10%."""
        subtotal = self.precio_base * self.horas
        if self.capacidad > 20:
            subtotal *= 1.10
        
        return subtotal * 1.19 if aplicar_iva else subtotal

    def obtener_detalles(self) -> str:
        return f"Sala para {self.capacidad} personas | Duración: {self.horas}h"

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "Tipo": "Reserva de Sala",
            "Especificación": f"{self.capacidad} pers / {self.horas}h",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d


class AlquilerEquipo(Servicio):
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
        """Costo = (Precio Base * Días). Seguro fijo de $50,000 opcional."""
        total = self.precio_base * self.dias
        if self.incluye_seguro:
            total += 50000
        
        total -= (total * descuento)
        return total

    def obtener_detalles(self) -> str:
        seguro_str = "Con Seguro" if self.incluye_seguro else "Sin Seguro"
        return f"Equipo: {self.nombre} | Tiempo: {self.dias} días | {seguro_str}"

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "Tipo": "Alquiler Equipo",
            "Especificación": f"{self.dias} días | Seguro: {self.incluye_seguro}",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_sistema, nombre, precio_base, consultor, nivel_complejidad):
        """
        nivel_complejidad: 'Basico', 'Intermedio', 'Avanzado'
        """
        super().__init__(id_sistema, nombre, precio_base)
        self.consultor = consultor
        self.__nivel = None
        self.nivel_complejidad = nivel_complejidad

    @property
    def nivel_complejidad(self):
        return self.__nivel

    @nivel_complejidad.setter
    def nivel_complejidad(self, valor):
        niveles_validos = ['Basico', 'Intermedio', 'Avanzado']
        if valor not in niveles_validos:
            raise ErrorDisponibilidadServicio(f"Nivel '{valor}' no válido. Use: {niveles_validos}")
        self.__nivel = valor

    def calcular_costo(self) -> float:
        """Costo base + recargo por complejidad."""
        tarifas = {'Basico': 1.0, 'Intermedio': 1.5, 'Avanzado': 2.0}
        return self.precio_base * tarifas[self.nivel_complejidad]

    def obtener_detalles(self) -> str:
        return f"Consultor: {self.consultor} | Nivel: {self.nivel_complejidad}"

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "Tipo": "Asesoría",
            "Especificación": f"Nivel {self.nivel_complejidad} ({self.consultor})",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d
    
######################################
# CLASE RESERVA
######################################

class Reserva:
    """
    Clase que gestiona la unión entre un Cliente y un Servicio.
    Implementa validaciones de fecha y control de duplicados.
    """
    
    # Lista estática para simular la persistencia en memoria y validar disponibilidad
    todas_las_reservas: List['Reserva'] = []

    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio, 
                 fecha_hora: datetime, notas: str = ""):
        self._id = id_reserva
        self.__cliente = cliente
        self.__servicio = servicio
        self.__fecha_hora = fecha_hora
        self.__notas = notas
        self.__estado = "pendiente"  # Estados: pendiente, confirmada, cancelada, completada
        self._fecha_creacion = datetime.now()

        # Al instanciar, validamos si el horario está ocupado
        self._validar_disponibilidad(fecha_hora, servicio)

    def _validar_disponibilidad(self, fecha_evaluar: datetime, servicio_evaluar: Servicio):
        """
        Verifica si ya existe una reserva activa para el mismo servicio y hora.
        """
        for r in Reserva.todas_las_reservas:
            if r.estado != "cancelada":
                # Validamos si es el mismo servicio a la misma hora
                if r.servicio.nombre == servicio_evaluar.nombre and r.fecha_hora == fecha_evaluar:
                    raise ErrorReserva(
                        "Disponibilidad", 
                        f"El servicio '{servicio_evaluar.nombre}' ya tiene una reserva para {fecha_evaluar}."
                    )

    # --- Getters y Setters ---
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

    @estado.setter
    def estado(self, nuevo_estado: str):
        estados_validos = ["pendiente", "confirmada", "cancelada", "completada"]
        if nuevo_estado.lower() in estados_validos:
            self.__estado = nuevo_estado.lower()
        else:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido.")

    # --- Métodos de Gestión ---
    @classmethod
    def crear_reserva(cls, id_reserva: int, cliente: Cliente, servicio: Servicio, 
                      fecha_str: str, hora_str: str, notas: str = "") -> 'Reserva':
        """
        Método de fábrica para crear reservas validando el formato de fecha.
        """
        try:
            fecha_dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            
            # Validación: No permitir fechas pasadas
            if fecha_dt < datetime.now():
                raise ErrorReserva("Fecha", "No se pueden crear reservas en fechas pasadas.")
                
            nueva_reserva = cls(id_reserva, cliente, servicio, fecha_dt, notas)
            cls.todas_las_reservas.append(nueva_reserva)
            return nueva_reserva
        except ValueError:
            raise ErrorReserva("Formato", "El formato de fecha (AAAA-MM-DD) o hora (HH:MM) es incorrecto.")

    def modificar_reserva(self, nueva_fecha_hora: Optional[datetime] = None, nuevas_notas: Optional[str] = None):
        """
        Permite editar la reserva verificando nuevamente la disponibilidad si cambia la fecha.
        """
        if self.__estado == "completada":
            raise ErrorReserva("Edición", "No se puede modificar una reserva ya completada.")

        if nueva_fecha_hora:
            # Validar que no choque con otras (excluyéndose a sí misma)
            for r in Reserva.todas_las_reservas:
                if r != self and r.estado != "cancelada" and r.fecha_hora == nueva_fecha_hora:
                    raise ErrorReserva("Conflicto", "La nueva fecha/hora ya está ocupada.")
            self.__fecha_hora = nueva_fecha_hora
        
        if nuevas_notas is not None:
            self.__notas = nuevas_notas

    @classmethod
    def eliminar_reserva(cls, id_reserva: int):
        """
        Elimina físicamente la reserva de la lista global.
        """
        cls.todas_las_reservas = [r for r in cls.todas_las_reservas if r.id != id_reserva]

    def cancelar(self):
        """Cambio de estado lógico a cancelada."""
        self.__estado = "cancelada"

    def __str__(self) -> str:
        return (f"Reserva #{self._id} | {self.__cliente.nombre} | "
                f"{self.__servicio.nombre} | {self.__fecha_hora.strftime('%d/%m/%Y %H:%M')} | "
                f"Estado: {self.__estado}")