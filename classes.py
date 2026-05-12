##########################################################
#
# --- Archivo classes.py ---
#
# - Última actualización: 12 - 5 - 2026
# - Aporte: Daniel Serrano Rivera / Ronald Molina /
#           Camila Meneses / Yuliana Morcillo Chatez
#
# Descripción: Contiene todas las clases del sistema FJ:
#              la clase abstracta raíz Entidad, la clase
#              Cliente con encapsulación completa, la clase
#              abstracta Servicio y sus tres subclases
#              especializadas, y la clase Reserva con
#              gestión completa del ciclo de vida.
#
##########################################################

from abc import ABC, abstractmethod       # Para definir clases y métodos abstractos
from datetime import datetime, timedelta  # Para manejo de fechas y duraciones
from typing import List, Optional         # Para anotaciones de tipo en listas y opcionales
import re                                 # Para validación con expresiones regulares

# Importa el módulo de validación de datos del cliente
from validadores import ValidadorDatos

# Importa las excepciones personalizadas del sistema
from excepciones import (
    ErrorDatosCliente,
    ErrorCalculoFinanciero,
    ErrorDisponibilidadServicio
)

######################################
# CLASES DE EXCEPCIONES PERSONALIZADAS
# (redeclaradas aquí para uso interno
#  dentro del módulo classes.py)
######################################

class ErrorDatosCliente(Exception):
    """
    Excepción para fallos en datos del cliente.
    Se lanza cuando nombre, correo o teléfono tienen formato inválido.
    """
    def __init__(self, campo: str, mensaje: str):
        self.campo = campo      # Campo específico que falló (ej: "correo")
        self.mensaje = mensaje  # Descripción legible del error
        # Construye el mensaje de la excepción con formato estandarizado
        super().__init__(f"[Cliente/{campo}] {mensaje}")


class ErrorDisponibilidadServicio(Exception):
    """
    Excepción para cuando un servicio no puede ser reservado o creado.
    Se lanza cuando parámetros como capacidad o nivel son inválidos.
    """
    def __init__(self, mensaje: str):
        # Antepone "[Servicio]" al mensaje para identificar el origen
        super().__init__(f"[Servicio] {mensaje}")


class ErrorCalculoFinanciero(Exception):
    """
    Excepción para errores en cálculos de costos, horas o días.
    Se lanza cuando los valores numéricos son negativos o de tipo incorrecto.
    """
    def __init__(self, campo: str, mensaje: str):
        self.campo = campo  # Campo numérico que causó el error
        # Construye el mensaje con prefijo financiero
        super().__init__(f"[Financiero/{campo}] {mensaje}")


class ErrorReserva(Exception):
    """
    Excepción para errores en el ciclo de vida de una reserva.
    Se lanza cuando se intenta confirmar, cancelar o procesar
    una reserva en un estado no permitido, o cuando hay solapamiento.
    """
    def __init__(self, contexto: str, mensaje: str):
        self.contexto = contexto  # Etapa donde ocurrió el error (ej: "Estado")
        # Construye el mensaje identificando el contexto dentro de la reserva
        super().__init__(f"[Reserva/{contexto}] {mensaje}")


######################################
# CLASE GENERAL ABSTRACTA
######################################

class Entidad(ABC):
    """
    Clase abstracta raíz del sistema Software FJ.
    Toda entidad del sistema (Cliente, Servicio) hereda de esta clase.
    Garantiza que todos los objetos tengan un ID único y fecha de registro.

    Al ser abstracta (ABC), no puede instanciarse directamente:
    solo sus subclases concretas pueden crear objetos.
    """

    def __init__(self, id_objeto):
        # Identificador único del objeto en el sistema (UUID generado externamente)
        self.id_objeto = id_objeto

        # Fecha y hora exacta en que se creó este objeto en memoria
        self.fecha_registro = datetime.now()

    @abstractmethod
    def mostrar_info(self) -> str:
        """
        Método abstracto que cada subclase DEBE implementar.
        Retorna una cadena con la información principal del objeto.
        Al ser abstracto, si una subclase no lo implementa, Python
        lanzará TypeError al intentar instanciarla.
        """
        pass  # Sin implementación en la clase base


######################################
# CLASE CLIENTE
######################################

class Cliente(Entidad):
    """
    Representa un cliente registrado en el sistema Software FJ.

    Implementa encapsulación completa:
    - Todos los atributos son privados (doble guion bajo __)
    - El acceso y modificación se hace SOLO a través de properties
    - Cada setter valida el valor antes de asignarlo

    Hereda de Entidad, por lo que tiene id_objeto y fecha_registro.
    """

    def __init__(self, id_sistema, id_cliente, nombre, direccion, correo, telefono):
        """
        Constructor del cliente. Primero valida con ValidadorDatos,
        luego inicializa los atributos privados a None, y finalmente
        los asigna a través de los setters (que re-validan).

        Parámetros:
            id_sistema (str): UUID generado automáticamente por el sistema.
            id_cliente (str): identificador legible asignado por el usuario.
            nombre     (str): nombre completo del cliente.
            direccion  (str): dirección de residencia o empresa.
            correo     (str): correo electrónico en formato válido.
            telefono   (str): número de 10 dígitos.
        """
        # Llama al constructor de Entidad para asignar id_objeto y fecha_registro
        super().__init__(id_sistema)

        # Validaciones previas usando el módulo externo ValidadorDatos
        # Estas pueden lanzar ErrorDatosCliente si los datos son inválidos
        ValidadorDatos.validar_nombre(nombre)    # Verifica longitud mínima del nombre
        ValidadorDatos.validar_correo(correo)    # Verifica formato usuario@dominio.ext
        ValidadorDatos.validar_telefono(telefono) # Verifica 10 dígitos numéricos

        # Inicializa los atributos privados a None antes de asignarlos
        # El doble guion bajo (__) activa el "name mangling" de Python,
        # haciendo que el atributo sea inaccesible directamente desde fuera
        self.__id_cliente = None
        self.__nombre     = None
        self.__direccion  = None
        self.__correo     = None
        self.__telefono   = None

        # Asigna los valores a través de los setters (con validación adicional)
        self.id_cliente = id_cliente
        self.nombre     = nombre
        self.direccion  = direccion
        self.correo     = correo
        self.telefono   = telefono

    # ─── GETTERS Y SETTERS (Properties) ───────────────────

    @property
    def id_cliente(self):
        """Getter: retorna el ID del cliente."""
        return self.__id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        """Setter: valida que el ID no sea vacío antes de asignar."""
        if not str(valor).strip():
            # Lanza excepción si el ID está vacío o solo tiene espacios
            raise ErrorDatosCliente("id_cliente", "El ID de cliente es obligatorio.")
        # Convierte a string y elimina espacios antes de guardar
        self.__id_cliente = str(valor).strip()

    @property
    def nombre(self):
        """Getter: retorna el nombre del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        """Setter: valida que el nombre no esté vacío y tenga al menos 3 caracteres."""
        if not valor or not valor.strip():
            raise ErrorDatosCliente("nombre", "El nombre no puede estar vacío.")
        if len(valor.strip()) < 3:
            raise ErrorDatosCliente("nombre", "El nombre debe tener al menos 3 caracteres.")
        # Guarda el nombre sin espacios al inicio o al final
        self.__nombre = valor.strip()

    @property
    def direccion(self):
        """Getter: retorna la dirección del cliente."""
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        """Setter: valida que la dirección no esté vacía."""
        if not valor or not valor.strip():
            raise ErrorDatosCliente("direccion", "La dirección no puede estar vacía.")
        self.__direccion = valor.strip()

    @property
    def correo(self):
        """Getter: retorna el correo electrónico del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor):
        """Setter: valida el formato del correo antes de asignar."""
        # Llama al método privado de validación de formato
        self.__validar_formato_correo(valor)
        self.__correo = valor.strip()

    @property
    def telefono(self):
        """Getter: retorna el número de teléfono del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        """Setter: valida el formato del teléfono antes de asignar."""
        # Llama al método privado de validación de formato
        self.__validar_formato_telefono(valor)
        self.__telefono = str(valor).strip()

    # ─── MÉTODOS PRIVADOS DE VALIDACIÓN ───────────────────

    def __validar_formato_correo(self, correo):
        """
        Valida el formato del correo usando expresión regular.
        Método privado: solo accesible desde dentro de la clase Cliente.

        Lanza ErrorDatosCliente si el correo es None o mal formado.
        """
        if not correo:
            # El correo no puede ser None ni cadena vacía
            raise ErrorDatosCliente("correo", "El correo electrónico es obligatorio.")

        # Patrón estándar para correos: acepta letras, dígitos, puntos, etc.
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, correo):
            raise ErrorDatosCliente("correo", f"El formato de correo '{correo}' no es válido.")

    def __validar_formato_telefono(self, telefono):
        """
        Valida que el teléfono sea numérico y tenga entre 7 y 15 dígitos.
        Método privado: solo accesible desde dentro de la clase Cliente.

        Lanza ErrorDatosCliente si el teléfono es None, no numérico o
        tiene una longitud fuera del rango permitido.
        """
        if not telefono:
            raise ErrorDatosCliente("telefono", "El número de teléfono es obligatorio.")

        # Elimina espacios y guiones antes de validar (ej: "300 123-4567" → "3001234567")
        limpio = str(telefono).replace(" ", "").replace("-", "")

        # Verifica que todos los caracteres sean dígitos (0-9)
        if not limpio.isdigit():
            raise ErrorDatosCliente("telefono", "El teléfono debe contener solo números.")

        # Verifica que la longitud esté entre 7 y 15 dígitos
        if not (7 <= len(limpio) <= 15):
            raise ErrorDatosCliente("telefono", "El teléfono debe tener entre 7 y 15 dígitos.")

    # ─── MÉTODOS PÚBLICOS ─────────────────────────────────

    def mostrar_info(self) -> str:
        """
        Implementación del método abstracto de Entidad.
        Retorna un resumen legible de los datos del cliente.
        """
        return (f"CLIENTE [{self.__id_cliente}] | "
                f"Nombre: {self.__nombre} | "
                f"Correo: {self.__correo} | "
                f"Tel: {self.__telefono}")

    def actualizar_datos(self, **kwargs):
        """
        Permite actualizar múltiples atributos del cliente en una sola llamada.
        Usa **kwargs para recibir pares clave=valor de forma flexible.

        Ejemplo: cliente.actualizar_datos(nombre="Nuevo Nombre", correo="nuevo@mail.com")

        Lanza AttributeError si alguna clave no corresponde a un atributo existente.
        """
        for clave, valor in kwargs.items():
            # hasattr verifica si el objeto tiene el atributo antes de asignarlo
            if hasattr(self, clave):
                # setattr asigna el valor al atributo (pasa por el setter)
                setattr(self, clave, valor)
            else:
                raise AttributeError(f"El atributo '{clave}' no existe en Cliente.")

    def to_dict(self) -> dict:
        """
        Convierte el cliente a un diccionario Python.
        Útil para serialización, reportes o pruebas unitarias.
        """
        return {
            "ID Sistema": self.id_objeto,     # UUID interno del sistema
            "ID Cliente": self.__id_cliente,   # ID legible asignado por el usuario
            "Nombre":     self.__nombre,
            "Dirección":  self.__direccion,
            "Correo":     self.__correo,
            "Teléfono":   self.__telefono
        }

    def __str__(self):
        """
        Representación en cadena del cliente.
        Se usa cuando se hace print(cliente) o f"{cliente}".
        """
        return f"Cliente: {self.__nombre} ({self.__id_cliente})"


######################################
# CLASE ABSTRACTA SERVICIO
######################################

class Servicio(Entidad, ABC):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Hereda de Entidad (para tener ID y fecha) y de ABC (para ser abstracta).

    Define la interfaz común que TODAS las subclases de servicio deben cumplir:
    - calcular_costo(): cada servicio calcula su costo de forma distinta
    - obtener_detalles(): descripción específica del tipo de servicio

    No puede instanciarse directamente; se debe usar una subclase concreta.
    """

    def __init__(self, id_sistema, nombre, precio_base):
        """
        Constructor del servicio base.

        Parámetros:
            id_sistema  (str): UUID único generado para este servicio.
            nombre      (str): nombre descriptivo del servicio.
            precio_base (float): precio unitario antes de aplicar fórmulas.
        """
        # Llama al constructor de Entidad
        super().__init__(id_sistema)

        # Inicializa los atributos privados a None antes de los setters
        self.__nombre      = None
        self.__precio_base = None

        # Asigna valores a través de setters que validan el contenido
        self.nombre      = nombre
        self.precio_base = precio_base

    # ─── GETTERS Y SETTERS ────────────────────────────────

    @property
    def nombre(self):
        """Getter: retorna el nombre del servicio."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        """Setter: valida que el nombre no esté vacío antes de asignar."""
        if not valor or not str(valor).strip():
            raise ErrorDisponibilidadServicio("El nombre del servicio no puede estar vacío.")
        self.__nombre = valor.strip()

    @property
    def precio_base(self):
        """Getter: retorna el precio base del servicio."""
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, valor):
        """
        Setter: valida que el precio sea un número positivo.
        Usa try/except para manejar valores no convertibles a float.
        """
        try:
            valor_float = float(valor)     # Intenta convertir a número decimal
            if valor_float < 0:
                raise ValueError           # Precio negativo no permitido
            self.__precio_base = valor_float
        except (ValueError, TypeError):
            # Captura tanto precio negativo como tipos no convertibles (ej: "abc")
            raise ErrorCalculoFinanciero(
                "precio_base",
                "El precio base debe ser un número positivo."
            )

    # ─── MÉTODOS ABSTRACTOS ───────────────────────────────

    @abstractmethod
    def calcular_costo(self, **kwargs) -> float:
        """
        Método abstracto: cada subclase implementa su propia fórmula de costo.
        Los parámetros opcionales (**kwargs) permiten variantes como IVA o descuentos.
        """
        pass

    @abstractmethod
    def obtener_detalles(self) -> str:
        """
        Método abstracto: retorna descripción específica del tipo de servicio.
        Cada subclase personaliza el formato de su descripción.
        """
        pass

    # ─── MÉTODOS COMUNES A TODOS LOS SERVICIOS ────────────

    def mostrar_info(self) -> str:
        """
        Implementación del método abstracto de Entidad.
        Retorna información básica común a todos los servicios.
        Las subclases pueden extender este método con super().mostrar_info().
        """
        return f"SERVICIO: {self.__nombre} | Precio Base: ${self.__precio_base:,.2f}"

    def to_dict(self) -> dict:
        """
        Convierte el servicio a diccionario con sus datos base.
        Las subclases pueden extender este método agregando sus atributos.
        """
        return {
            "ID Sistema":  self.id_objeto,
            "Servicio":    self.__nombre,
            "Precio Base": self.__precio_base
        }


######################################
# SUBCLASES DE SERVICIOS
######################################

class ReservaSala(Servicio):
    """
    Servicio de reserva de sala de reuniones.

    Fórmula de costo:
        subtotal = precio_base × horas
        Si capacidad > 20 personas: subtotal × 1.10 (recargo del 10%)
        Si aplicar_iva=True: subtotal × 1.19 (IVA colombiano del 19%)

    Demuestra sobrecarga de método: calcular_costo tiene parámetro
    opcional 'aplicar_iva' que distingue esta variante de las otras.
    """

    def __init__(self, id_sistema, nombre, precio_base, capacidad, horas):
        """
        Constructor de ReservaSala.

        Parámetros adicionales a Servicio:
            capacidad (int): número máximo de personas en la sala.
            horas    (float): duración de la reserva en horas.
        """
        # Llama al constructor de Servicio (que a su vez llama a Entidad)
        super().__init__(id_sistema, nombre, precio_base)

        # Inicializa atributos privados propios de este servicio
        self.__capacidad = None
        self.__horas     = None

        # Asigna a través de setters que validan los valores
        self.capacidad = capacidad
        self.horas     = horas

    @property
    def capacidad(self):
        """Getter: retorna la capacidad de la sala."""
        return self.__capacidad

    @capacidad.setter
    def capacidad(self, valor):
        """Setter: valida que la capacidad sea un entero positivo."""
        if not isinstance(valor, int) or valor <= 0:
            # Solo acepta enteros mayores a cero
            raise ErrorDisponibilidadServicio(
                "Se requiere que la capacidad de la sala sea un número entero positivo."
            )
        self.__capacidad = valor

    @property
    def horas(self):
        """Getter: retorna las horas de reserva."""
        return self.__horas

    @horas.setter
    def horas(self, valor):
        """Setter: valida que la duración sea un número mayor a cero."""
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ErrorCalculoFinanciero(
                "horas", "La duración debe ser mayor a 0 horas."
            )
        self.__horas = valor

    def calcular_costo(self, aplicar_iva=True) -> float:
        """
        Calcula el costo de reservar la sala.
        Demuestra sobrecarga de método con parámetro opcional.

        Fórmula:
            subtotal = precio_base × horas
            + 10% si capacidad > 20 personas
            + 19% de IVA si aplicar_iva=True

        Parámetros:
            aplicar_iva (bool): si True, agrega el 19% de IVA al subtotal.

        Retorna:
            float: costo total redondeado a 2 decimales.
        """
        # Costo base: precio por hora multiplicado por la cantidad de horas
        subtotal = self.precio_base * self.horas

        # Recargo del 10% si la sala tiene capacidad para más de 20 personas
        if self.__capacidad > 20:
            subtotal *= 1.10  # Incrementa el subtotal en un 10%

        # Aplica IVA del 19% si el parámetro lo indica; de lo contrario retorna sin IVA
        return round(subtotal * 1.19 if aplicar_iva else subtotal, 2)

    def obtener_detalles(self) -> str:
        """Retorna descripción compacta de la sala para mostrar en listas."""
        return f"Sala para {self.__capacidad} personas | Duración: {self.__horas}h"

    def to_dict(self) -> dict:
        """
        Extiende el diccionario base de Servicio con datos específicos de la sala.
        Llama a super().to_dict() para no duplicar código.
        """
        d = super().to_dict()         # Obtiene el diccionario base
        d.update({                    # Agrega los campos específicos de sala
            "Tipo":           "Reserva de Sala",
            "Especificación": f"{self.__capacidad} pers / {self.__horas}h",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d

    def mostrar_info(self) -> str:
        """
        Extiende mostrar_info() de Servicio agregando los detalles de la sala.
        Demuestra polimorfismo: cada subclase personaliza su representación.
        """
        return super().mostrar_info() + f" | {self.obtener_detalles()}"


class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.

    Fórmula de costo:
        total = precio_base × días
        Si incluye_seguro: total + $50,000
        descuento: total × (1 - descuento)  [0.0 a 1.0]

    Demuestra sobrecarga de método: calcular_costo acepta un
    parámetro opcional 'descuento' que no existe en ReservaSala.
    """

    def __init__(self, id_sistema, nombre, precio_base, dias, incluye_seguro=False):
        """
        Constructor de AlquilerEquipo.

        Parámetros adicionales a Servicio:
            dias           (int): número de días de alquiler.
            incluye_seguro (bool): si True, agrega $50,000 al costo.
        """
        super().__init__(id_sistema, nombre, precio_base)

        self.__dias = None                    # Días de alquiler (privado)
        self.incluye_seguro = incluye_seguro  # Boolean de seguro (no privado)
        self.dias = dias                      # Asigna via setter con validación

    @property
    def dias(self):
        """Getter: retorna los días de alquiler."""
        return self.__dias

    @dias.setter
    def dias(self, valor):
        """Setter: valida que los días sean un entero positivo."""
        if not isinstance(valor, int) or valor <= 0:
            raise ErrorCalculoFinanciero(
                "dias", "El alquiler debe ser de al menos 1 día."
            )
        self.__dias = valor

    def calcular_costo(self, descuento=0.0) -> float:
        """
        Calcula el costo del alquiler del equipo.
        Demuestra sobrecarga de método con parámetro opcional.

        Fórmula:
            total = precio_base × días
            + $50,000 si incluye seguro
            - total × descuento (porcentaje en decimal, ej: 0.10 = 10%)

        Parámetros:
            descuento (float): porcentaje de descuento entre 0.0 y 1.0.

        Retorna:
            float: costo total redondeado a 2 decimales.
        """
        # Costo base: precio por día multiplicado por días totales
        total = self.precio_base * self.__dias

        # Agrega el costo fijo del seguro si fue seleccionado
        if self.incluye_seguro:
            total += 50000  # Valor fijo del seguro en pesos colombianos

        # Aplica el descuento si se proporcionó uno mayor a cero
        total -= total * descuento

        return round(total, 2)  # Redondea a 2 decimales para evitar errores de punto flotante

    def obtener_detalles(self) -> str:
        """Retorna descripción compacta del equipo para mostrar en listas."""
        seguro_str = "Con Seguro" if self.incluye_seguro else "Sin Seguro"
        return f"Equipo: {self.nombre} | Tiempo: {self.__dias} días | {seguro_str}"

    def to_dict(self) -> dict:
        """Extiende el diccionario base con datos específicos del equipo."""
        d = super().to_dict()
        d.update({
            "Tipo":           "Alquiler Equipo",
            "Especificación": f"{self.__dias} días | Seguro: {self.incluye_seguro}",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d

    def mostrar_info(self) -> str:
        """Extiende mostrar_info() de Servicio con detalles del equipo."""
        return super().mostrar_info() + f" | {self.obtener_detalles()}"


class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría profesional por nivel de complejidad.

    Fórmula de costo:
        total = precio_base × multiplicador_nivel
        Multiplicadores: Basico=1.0, Intermedio=1.5, Avanzado=2.0

    Demuestra validación de dominio: solo acepta niveles predefinidos.
    """

    # Constantes de clase: valores válidos para el nivel de complejidad
    NIVELES_VALIDOS = ['Basico', 'Intermedio', 'Avanzado']

    # Diccionario que mapea cada nivel a su multiplicador de precio
    TARIFAS = {
        'Basico':      1.0,  # Sin recargo adicional
        'Intermedio':  1.5,  # 50% más que el precio base
        'Avanzado':    2.0   # El doble del precio base
    }

    def __init__(self, id_sistema, nombre, precio_base, consultor, nivel_complejidad):
        """
        Constructor de AsesoriaEspecializada.

        Parámetros adicionales a Servicio:
            consultor         (str): nombre del profesional que realizará la asesoría.
            nivel_complejidad (str): nivel de dificultad (Basico/Intermedio/Avanzado).
        """
        super().__init__(id_sistema, nombre, precio_base)

        self.consultor = consultor    # Nombre del consultor (no privado)
        self.__nivel   = None         # Nivel de complejidad (privado)

        # Asigna el nivel a través del setter que valida el dominio
        self.nivel_complejidad = nivel_complejidad

    @property
    def nivel_complejidad(self):
        """Getter: retorna el nivel de complejidad."""
        return self.__nivel

    @nivel_complejidad.setter
    def nivel_complejidad(self, valor):
        """
        Setter: valida que el nivel pertenezca a los valores permitidos.
        Si no está en NIVELES_VALIDOS, lanza ErrorDisponibilidadServicio.
        """
        if valor not in self.NIVELES_VALIDOS:
            raise ErrorDisponibilidadServicio(
                f"Nivel '{valor}' no válido. Use: {self.NIVELES_VALIDOS}"
            )
        self.__nivel = valor

    def calcular_costo(self) -> float:
        """
        Calcula el costo de la asesoría según el nivel de complejidad.

        Fórmula:
            total = precio_base × TARIFAS[nivel]

        Retorna:
            float: costo total redondeado a 2 decimales.
        """
        # Busca el multiplicador correspondiente al nivel actual en el diccionario
        return round(self.precio_base * self.TARIFAS[self.__nivel], 2)

    def obtener_detalles(self) -> str:
        """Retorna descripción compacta de la asesoría para mostrar en listas."""
        return f"Consultor: {self.consultor} | Nivel: {self.__nivel}"

    def to_dict(self) -> dict:
        """Extiende el diccionario base con datos específicos de la asesoría."""
        d = super().to_dict()
        d.update({
            "Tipo":           "Asesoría",
            "Especificación": f"Nivel {self.__nivel} ({self.consultor})",
            "Costo Estimado": f"${self.calcular_costo():,.0f}"
        })
        return d

    def mostrar_info(self) -> str:
        """Extiende mostrar_info() de Servicio con detalles de la asesoría."""
        return super().mostrar_info() + f" | {self.obtener_detalles()}"


######################################
# CLASE RESERVA
######################################

class Reserva:
    """
    Gestiona el ciclo de vida completo de una reserva en Software FJ.

    Estados posibles y transiciones permitidas:
        pendiente → confirmar() → confirmada → procesar() → completada
        pendiente → cancelar()  → cancelada
        confirmada → cancelar() → cancelada

    Mantiene un registro global en memoria (sin base de datos) de todas
    las reservas activas, usado para detectar solapamientos de horario.
    """

    # Lista de clase compartida entre todas las instancias de Reserva.
    # Almacena todas las reservas creadas durante la sesión (sin base de datos).
    todas_las_reservas: List['Reserva'] = []

    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio,
                    fecha_hora: datetime, duracion: float, notas: str = ""):
        """
        Constructor de Reserva. Valida disponibilidad de horario antes
        de aceptar la nueva reserva.

        Parámetros:
            id_reserva (int):      número identificador de la reserva.
            cliente    (Cliente):  objeto Cliente que hace la reserva.
            servicio   (Servicio): objeto de servicio a reservar.
            fecha_hora (datetime): fecha y hora de inicio de la reserva.
            duracion   (float):    duración en horas.
            notas      (str):      observaciones opcionales.
        """
        self._id             = id_reserva   # ID visible (protegido, no privado)
        self.__cliente       = cliente       # Cliente asociado (privado)
        self.__servicio      = servicio      # Servicio reservado (privado)
        self.__fecha_hora    = fecha_hora    # Fecha/hora de inicio (privada)
        self.__duracion      = duracion      # Duración en horas (privada)
        self.__notas         = notas         # Notas adicionales (privadas)
        self.__estado        = "pendiente"   # Estado inicial siempre es pendiente
        self._fecha_creacion = datetime.now() # Momento exacto de creación

        # Verifica que no haya solapamiento con otras reservas del mismo servicio
        # Puede lanzar ErrorReserva si el horario no está disponible
        self._validar_disponibilidad(fecha_hora, servicio)

    def _validar_disponibilidad(self, fecha_evaluar: datetime, servicio_evaluar: Servicio):
        """
        Verifica que no exista otra reserva activa del mismo servicio
        que se solape con el horario solicitado.

        Una reserva solapa si:
            fecha_nueva < fin_reserva_existente
            (es decir, la nueva empieza antes de que termine la actual)

        Lanza ErrorReserva si detecta solapamiento.
        """
        for r in Reserva.todas_las_reservas:
            # Ignora las reservas canceladas o ya completadas
            if r.estado in ("cancelada", "completada"):
                continue

            # Verifica si es el mismo servicio por nombre
            if r.servicio.nombre == servicio_evaluar.nombre:
                # Calcula cuándo termina la reserva existente
                fin_existente = r.fecha_hora + timedelta(hours=r.duracion)

                # Si la nueva reserva empieza antes de que termine la existente, hay solapamiento
                if fecha_evaluar < fin_existente:
                    raise ErrorReserva(
                        "Disponibilidad",
                        f"'{servicio_evaluar.nombre}' ya está ocupado en ese horario."
                    )

    # ─── GETTERS ──────────────────────────────────────────

    @property
    def id(self):
        """Retorna el ID numérico de la reserva."""
        return self._id

    @property
    def cliente(self):
        """Retorna el objeto Cliente asociado a la reserva."""
        return self.__cliente

    @property
    def servicio(self):
        """Retorna el objeto Servicio asociado a la reserva."""
        return self.__servicio

    @property
    def fecha_hora(self):
        """Retorna la fecha y hora de inicio de la reserva."""
        return self.__fecha_hora

    @property
    def estado(self):
        """Retorna el estado actual de la reserva (pendiente/confirmada/completada/cancelada)."""
        return self.__estado

    @property
    def duracion(self):
        """Retorna la duración de la reserva en horas."""
        return self.__duracion

    @property
    def notas(self):
        """Retorna las notas adicionales de la reserva."""
        return self.__notas

    # ─── GESTORES DE ESTADO ───────────────────────────────

    def confirmar(self):
        """
        Cambia el estado de la reserva de 'pendiente' a 'confirmada'.
        Solo se puede confirmar si la reserva está en estado pendiente.

        Lanza ErrorReserva si el estado actual no es 'pendiente'.
        """
        if self.__estado != "pendiente":
            raise ErrorReserva(
                "Estado",
                "Solo se pueden confirmar reservas pendientes."
            )
        self.__estado = "confirmada"  # Transición de estado

    def cancelar(self):
        """
        Cancela la reserva cambiando su estado a 'cancelada'.
        No se puede cancelar una reserva que ya fue completada.

        Lanza ErrorReserva si la reserva ya está completada.
        """
        if self.__estado == "completada":
            raise ErrorReserva(
                "Cancelación",
                "No se puede cancelar una reserva ya completada."
            )
        self.__estado = "cancelada"  # Marca la reserva como cancelada

    def procesar(self) -> float:
        """
        Ejecuta el procesamiento final de la reserva:
        calcula el costo y la marca como completada.

        Requiere que la reserva esté en estado 'confirmada'.
        Demuestra encadenamiento de excepciones: si calcular_costo()
        falla, la excepción se relanza como ErrorReserva con 'from e'.

        Retorna:
            float: costo total calculado por el servicio.

        Lanza:
            ErrorReserva si no está confirmada o si el cálculo falla.
        """
        if self.__estado != "confirmada":
            raise ErrorReserva(
                "Procesamiento",
                "La reserva debe estar confirmada antes de procesarse."
            )
        try:
            # Llama al método polimórfico calcular_costo() del servicio
            costo = self.__servicio.calcular_costo()
        except ErrorCalculoFinanciero as e:
            # Encadenamiento de excepciones: convierte ErrorCalculoFinanciero
            # en ErrorReserva preservando la excepción original con 'from e'
            raise ErrorReserva("Financiero", f"Error al procesar costo: {e}") from e

        self.__estado = "completada"  # Cambia el estado solo si el cálculo fue exitoso
        return costo                  # Retorna el costo para mostrarlo al usuario

    # ─── MÉTODO DE FÁBRICA ────────────────────────────────

    @classmethod
    def crear_reserva(cls, id_reserva: int, cliente: Cliente, servicio: Servicio,
                        fecha_str: str, hora_str: str, duracion: float, notas: str = "") -> 'Reserva':
        """
        Método de fábrica (classmethod): crea una Reserva a partir de strings
        de fecha y hora en lugar de objetos datetime.

        Pasos:
            1. Convierte los strings de fecha y hora a un objeto datetime.
            2. Verifica que la fecha no esté en el pasado.
            3. Crea y registra la reserva en la lista global.

        Parámetros:
            fecha_str (str): fecha en formato "YYYY-MM-DD".
            hora_str  (str): hora en formato "HH:MM".
            (el resto igual al constructor)

        Retorna:
            Reserva: nueva instancia registrada en todas_las_reservas.

        Lanza:
            ErrorReserva si el formato de fecha/hora es incorrecto o si
            la fecha es anterior al momento actual.
        """
        try:
            # Combina los strings de fecha y hora y los convierte a datetime
            fecha_dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            # strptime lanza ValueError si el formato no coincide
            raise ErrorReserva(
                "Formato",
                "Formato de fecha/hora incorrecto. Use YYYY-MM-DD HH:MM."
            )

        # Verifica que la reserva no sea en el pasado
        if fecha_dt < datetime.now():
            raise ErrorReserva(
                "Fecha",
                "La fecha de la reserva no puede estar en el pasado."
            )

        # Crea la instancia de Reserva (cls = la clase actual o una subclase)
        nueva = cls(id_reserva, cliente, servicio, fecha_dt, duracion, notas)

        # Registra la nueva reserva en la lista global de memoria
        cls.todas_las_reservas.append(nueva)

        return nueva  # Retorna la reserva recién creada

    def __str__(self) -> str:
        """
        Representación en cadena de la reserva.
        Incluye: ID, nombre del cliente, nombre del servicio,
        fecha/hora formateada, estado y duración.
        """
        return (f"Reserva #{self._id} | {self.__cliente.nombre} | "
                f"{self.__servicio.nombre} | "
                f"{self.__fecha_hora.strftime('%d/%m/%Y %H:%M')} | "
                f"Estado: {self.__estado} | Duración: {self.__duracion}h")