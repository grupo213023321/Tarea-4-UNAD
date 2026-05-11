##########################################################
#
# --- Archivo log.py ---
#
# - Ultima actualización: 09 - 5 - 2026
# -Aporte: Angie Camila Meneses Rojas
# Descripción: Módulo de registro de eventos y errores.
#              Escribe en 'sistema_fj.log' usando bloques
#              try/except/finally según requiere la guía.
#
##########################################################

import os
import traceback
from datetime import datetime

LOG_FILE = "sistema_fj.log"

# ─── Niveles de log ───────────────────────────────────────
NIVEL_INFO    = "INFO"
NIVEL_WARNING = "WARNING"
NIVEL_ERROR   = "ERROR"
NIVEL_CRITICO = "CRITICO"

# ─── Función interna de escritura ─────────────────────────

def _escribir(nivel: str, mensaje: str, detalle: str = "") -> None:
    """
    Escribe una línea en el archivo de log.
    Usa try/except/finally para garantizar que el archivo
    siempre se cierre, incluso ante errores de disco.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] [{nivel}] {mensaje}"
    if detalle:
        linea += f" | DETALLE: {detalle}"
    linea += "\n"

    archivo = None
    try:
        archivo = open(LOG_FILE, "a", encoding="utf-8")
        archivo.write(linea)
    except OSError as e:
        # Si no se puede escribir en disco, imprimir en consola como respaldo
        print(f"[LOG-ERROR] No se pudo escribir en {LOG_FILE}: {e}")
        print(f"  → Mensaje perdido: {linea.strip()}")
    finally:
        if archivo:
            archivo.close()

# ─── API pública ───────────────────────────────────────────

def registrar_evento(mensaje: str, nivel: str = NIVEL_INFO) -> None:
    """
    Registra un evento informativo o de advertencia.
    
    Ejemplo:
        registrar_evento("Cliente registrado: Daniel", nivel="INFO")
    """
    _escribir(nivel, mensaje)


def registrar_excepcion(excepcion: Exception, contexto: str = "") -> None:
    """
    Registra una excepción con su traceback completo.

    Ejemplo:
        registrar_excepcion(e, contexto="Creación de Reserva")
    """
    tipo = type(excepcion).__name__
    mensaje_base = f"Excepción [{tipo}]"
    if contexto:
        mensaje_base = f"{contexto} → {mensaje_base}"

    detalle = str(excepcion)
    tb = traceback.format_exc()
    if tb and tb.strip() != "NoneType: None":
        detalle += f"\n{tb}"

    _escribir(NIVEL_ERROR, mensaje_base, detalle)


def registrar_inicio_sesion() -> None:
    """Marca el inicio de una sesión en el log."""
    separador = "=" * 60
    _escribir(NIVEL_INFO, separador)
    _escribir(NIVEL_INFO, "INICIO DE SESIÓN — Software FJ")
    _escribir(NIVEL_INFO, separador)


def registrar_cierre_sesion() -> None:
    """Marca el cierre de una sesión en el log."""
    separador = "=" * 60
    _escribir(NIVEL_INFO, "CIERRE DE SESIÓN — Software FJ")
    _escribir(NIVEL_INFO, separador + "\n")


def leer_log(ultimas_n: int = 20) -> list:
    """
    Retorna las últimas N líneas del archivo de log.
    Útil para mostrar en la GUI o en reportes de consola.
    """
    try:
        if not os.path.exists(LOG_FILE):
            return ["(El archivo de log aún no existe)"]
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        return lineas[-ultimas_n:] if len(lineas) > ultimas_n else lineas
    except OSError as e:
        return [f"(No se pudo leer el log: {e})"]