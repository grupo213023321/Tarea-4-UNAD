##########################################################
#
# --- Archivo log.py ---
#
# - Última actualización: 12 - 5 - 2026
# - Aporte: Angie Camila Meneses Rojas
#
# Descripción: Módulo de registro de eventos y errores.
#              Escribe en 'sistema_fj.log' usando bloques
#              try/except/finally para garantizar que el
#              archivo siempre se cierre correctamente,
#              incluso si ocurre un error de disco.
#
##########################################################

import os          # Para verificar si el archivo de log ya existe en disco
import traceback   # Para capturar el traceback completo de una excepción
from datetime import datetime  # Para obtener la fecha y hora actuales

# ─── Nombre del archivo de log ────────────────────────────

# Ruta del archivo donde se almacenan todos los eventos y errores
LOG_FILE = "sistema_fj.log"

# ─── Constantes de nivel de log ───────────────────────────

# Nivel informativo: operaciones normales del sistema
NIVEL_INFO    = "INFO"

# Nivel de advertencia: situaciones inesperadas pero no críticas
NIVEL_WARNING = "WARNING"

# Nivel de error: excepciones capturadas que afectan una operación
NIVEL_ERROR   = "ERROR"

# Nivel crítico: errores graves que podrían comprometer el sistema
NIVEL_CRITICO = "CRITICO"


# ─── Función interna de escritura ─────────────────────────

def _escribir(nivel: str, mensaje: str, detalle: str = "") -> None:
    """
    Función privada (prefijo _) que escribe una línea formateada
    en el archivo de log.

    Implementa try/except/finally para garantizar que el archivo
    siempre se cierre, incluso si ocurre un error de escritura.

    Parámetros:
        nivel   (str): categoría del evento (INFO, WARNING, ERROR, CRITICO).
        mensaje (str): descripción principal del evento.
        detalle (str): información adicional opcional (traceback, contexto).
    """
    # Obtiene la fecha y hora actual con formato legible
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construye la línea del log con el formato estándar:
    # [FECHA HORA] [NIVEL] MENSAJE
    linea = f"[{timestamp}] [{nivel}] {mensaje}"

    # Si hay detalle adicional, lo agrega separado por " | DETALLE: "
    if detalle:
        linea += f" | DETALLE: {detalle}"

    # Agrega salto de línea al final para separar entradas en el archivo
    linea += "\n"

    # Variable que referencia al archivo; se declara antes del try
    # para poder verificarla en el bloque finally
    archivo = None

    try:
        # Abre el archivo en modo "a" (append): agrega sin borrar contenido previo
        # encoding="utf-8" garantiza compatibilidad con caracteres especiales
        archivo = open(LOG_FILE, "a", encoding="utf-8")

        # Escribe la línea construida en el archivo
        archivo.write(linea)

    except OSError as e:
        # OSError cubre errores de disco: permisos denegados, disco lleno, etc.
        # Si no se puede escribir, se imprime en consola como respaldo
        print(f"[LOG-ERROR] No se pudo escribir en {LOG_FILE}: {e}")
        print(f"  → Mensaje perdido: {linea.strip()}")

    finally:
        # El bloque finally SIEMPRE se ejecuta, sin importar si hubo error.
        # Cierra el archivo solo si fue abierto exitosamente (no es None)
        if archivo:
            archivo.close()


# ─── API pública del módulo ───────────────────────────────

def registrar_evento(mensaje: str, nivel: str = NIVEL_INFO) -> None:
    """
    Registra un evento informativo o de advertencia en el log.
    Es la función más usada en el sistema para eventos normales.

    Parámetros:
        mensaje (str): descripción del evento ocurrido.
        nivel   (str): nivel de severidad (por defecto INFO).

    Ejemplo de uso:
        registrar_evento("Cliente registrado: Daniel", nivel="INFO")
        registrar_evento("Correo inválido ingresado", nivel="WARNING")
    """
    # Delega la escritura a la función interna _escribir
    _escribir(nivel, mensaje)


def registrar_excepcion(excepcion: Exception, contexto: str = "") -> None:
    """
    Registra una excepción con su tipo, mensaje y traceback completo.
    Se usa en bloques except para dejar trazabilidad de los errores.

    Parámetros:
        excepcion (Exception): el objeto de excepción capturado.
        contexto  (str): descripción de dónde ocurrió el error.

    Ejemplo de uso:
        except ErrorDatosCliente as e:
            registrar_excepcion(e, contexto="Registro de Cliente")
    """
    # Obtiene el nombre de la clase de la excepción (ej: "ErrorDatosCliente")
    tipo = type(excepcion).__name__

    # Construye el mensaje base incluyendo el tipo de excepción
    mensaje_base = f"Excepción [{tipo}]"

    # Si se proporcionó contexto, lo antepone al mensaje
    if contexto:
        mensaje_base = f"{contexto} → {mensaje_base}"

    # Convierte la excepción a string para obtener su descripción
    detalle = str(excepcion)

    # Obtiene el traceback completo (pila de llamadas) como texto
    tb = traceback.format_exc()

    # Solo agrega el traceback si contiene información útil
    # (format_exc retorna "NoneType: None" cuando no hay excepción activa)
    if tb and tb.strip() != "NoneType: None":
        detalle += f"\n{tb}"

    # Escribe la entrada como ERROR en el log con el detalle completo
    _escribir(NIVEL_ERROR, mensaje_base, detalle)


def registrar_inicio_sesion() -> None:
    """
    Escribe un separador visual en el log para marcar el inicio
    de una nueva sesión del sistema. Facilita la lectura del log
    cuando hay múltiples sesiones registradas.
    """
    separador = "=" * 60  # Línea de 60 signos igual como separador visual

    _escribir(NIVEL_INFO, separador)                        # Línea superior
    _escribir(NIVEL_INFO, "INICIO DE SESIÓN — Software FJ") # Título de sesión
    _escribir(NIVEL_INFO, separador)                        # Línea inferior


def registrar_cierre_sesion() -> None:
    """
    Escribe un separador visual en el log para marcar el cierre
    de la sesión actual. Deja una línea en blanco al final para
    separar visualmente las sesiones entre sí.
    """
    separador = "=" * 60  # Misma línea separadora del inicio

    _escribir(NIVEL_INFO, "CIERRE DE SESIÓN — Software FJ") # Título de cierre
    # Se agrega "\n" extra al separador final para crear espacio entre sesiones
    _escribir(NIVEL_INFO, separador + "\n")


def leer_log(ultimas_n: int = 20) -> list:
    """
    Lee el archivo de log y retorna las últimas N líneas.
    Útil para mostrar el historial reciente en la GUI o consola.

    Parámetros:
        ultimas_n (int): cantidad de líneas a retornar (por defecto 20).

    Retorna:
        list: lista de strings, cada uno es una línea del log.
                Retorna un mensaje de error en caso de fallo.
    """
    try:
        # Verifica si el archivo de log existe antes de intentar abrirlo
        if not os.path.exists(LOG_FILE):
            # Si aún no se ha creado, retorna un mensaje informativo
            return ["(El archivo de log aún no existe)"]

        # Abre el archivo en modo lectura con codificación UTF-8
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            # Lee todas las líneas del archivo en una lista
            lineas = f.readlines()

        # Retorna solo las últimas N líneas para no saturar la pantalla
        # Si el archivo tiene menos de N líneas, retorna todas
        return lineas[-ultimas_n:] if len(lineas) > ultimas_n else lineas

    except OSError as e:
        # Si ocurre un error al leer (permisos, disco), retorna mensaje de error
        return [f"(No se pudo leer el log: {e})"]