##########################################################
#
# --- Archivo servicios.py ---
#
# - Ultima actualización: 09 - 5 - 2026
#
# Descripción: Funciones auxiliares para gestión y
#              simulación de servicios y reservas.
#              Usado por main.py para las pruebas de
#              las 10 operaciones requeridas por la guía.
#
##########################################################

import uuid
from datetime import datetime, timedelta

from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)
from log import registrar_evento, registrar_excepcion

# ─── Helpers de creación ───────────────────────────────────

def crear_cliente(id_cliente, nombre, direccion, correo, telefono) -> Cliente | None:
    """
    Intenta crear un Cliente con manejo de excepciones completo.
    Retorna el objeto si tiene éxito, None si falla.
    Usa try/except/else/finally tal como exige la guía.
    """
    cliente = None
    try:
        id_sistema = str(uuid.uuid4())
        cliente = Cliente(id_sistema, id_cliente, nombre, direccion, correo, telefono)
    except ErrorDatosCliente as e:
        registrar_excepcion(e, contexto="Registro de Cliente")
        print(f"  ✗ Error al registrar cliente '{nombre}': {e}")
    except Exception as e:
        registrar_excepcion(e, contexto="Registro de Cliente (inesperado)")
        print(f"  ✗ Error inesperado: {e}")
    else:
        registrar_evento(f"Cliente registrado: {cliente}")
        print(f"  ✓ Cliente registrado: {cliente}")
    finally:
        pass  # Aquí podría cerrarse una conexión; se deja como punto de extensión
    return cliente


def crear_sala(nombre, precio_base, capacidad, horas) -> ReservaSala | None:
    """Crea una ReservaSala con manejo de excepciones."""
    servicio = None
    try:
        servicio = ReservaSala(str(uuid.uuid4()), nombre, precio_base, capacidad, horas)
    except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
        registrar_excepcion(e, contexto="Creación Sala")
        print(f"  ✗ Error al crear sala '{nombre}': {e}")
    else:
        registrar_evento(f"Sala creada: {servicio.mostrar_info()}")
        print(f"  ✓ Sala creada: {servicio.obtener_detalles()}")
    return servicio


def crear_equipo(nombre, precio_base, dias, incluye_seguro=False) -> AlquilerEquipo | None:
    """Crea un AlquilerEquipo con manejo de excepciones."""
    servicio = None
    try:
        servicio = AlquilerEquipo(str(uuid.uuid4()), nombre, precio_base, dias, incluye_seguro)
    except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
        registrar_excepcion(e, contexto="Creación Equipo")
        print(f"  ✗ Error al crear equipo '{nombre}': {e}")
    else:
        registrar_evento(f"Equipo creado: {servicio.mostrar_info()}")
        print(f"  ✓ Equipo creado: {servicio.obtener_detalles()}")
    return servicio


def crear_asesoria(nombre, precio_base, consultor, nivel) -> AsesoriaEspecializada | None:
    """Crea una AsesoriaEspecializada con manejo de excepciones."""
    servicio = None
    try:
        servicio = AsesoriaEspecializada(str(uuid.uuid4()), nombre, precio_base, consultor, nivel)
    except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
        registrar_excepcion(e, contexto="Creación Asesoría")
        print(f"  ✗ Error al crear asesoría '{nombre}': {e}")
    else:
        registrar_evento(f"Asesoría creada: {servicio.mostrar_info()}")
        print(f"  ✓ Asesoría creada: {servicio.obtener_detalles()}")
    return servicio


def crear_reserva(id_reserva, cliente, servicio, fecha_str, hora_str,
                    duracion, notas="") -> Reserva | None:
    """
    Crea una Reserva usando el método de fábrica.
    Maneja ErrorReserva y excepciones encadenadas.
    """
    reserva = None
    try:
        reserva = Reserva.crear_reserva(
            id_reserva, cliente, servicio, fecha_str, hora_str, duracion, notas
        )
    except ErrorReserva as e:
        registrar_excepcion(e, contexto="Crear Reserva")
        print(f"  ✗ Reserva fallida: {e}")
    except Exception as e:
        registrar_excepcion(e, contexto="Crear Reserva (inesperado)")
        print(f"  ✗ Error inesperado en reserva: {e}")
    else:
        registrar_evento(f"Reserva creada: {reserva}")
        print(f"  ✓ Reserva creada: {reserva}")
    return reserva


# ─── Simulación de las 10 operaciones requeridas ──────────

def simular_10_operaciones():
    """
    Ejecuta al menos 10 operaciones completas (válidas e inválidas)
    demostrando el manejo robusto de excepciones.
    """
    print("\n" + "="*60)
    print("  SIMULACIÓN AUTOMÁTICA — 10 OPERACIONES (según guía)")
    print("="*60)

    clientes = []
    servicios = []
    reservas = []

    # ── BLOQUE 1: REGISTRO DE CLIENTES ────────────────────
    print("\n[1] Registro de cliente válido:")
    c1 = crear_cliente("C001", "Daniel Serrano", "Calle 1 #45", "daniel@fj.com", "3001234567")
    if c1: clientes.append(c1)

    print("\n[2] Registro de cliente con correo inválido (debe fallar):")
    c2 = crear_cliente("C002", "Carlos Ruiz", "Carrera 2", "correo_invalido", "3109876543")
    # c2 será None

    print("\n[3] Registro de cliente con nombre muy corto (debe fallar):")
    c3 = crear_cliente("C003", "Al", "Av. 3", "al@fj.com", "3207654321")
    # c3 será None

    print("\n[4] Registro de segundo cliente válido:")
    c4 = crear_cliente("C004", "Camila Torres", "Carrera 5 #12", "camila@fj.com", "3154443322")
    if c4: clientes.append(c4)

    # ── BLOQUE 2: CREACIÓN DE SERVICIOS ───────────────────
    print("\n[5] Crear sala válida (capacidad 15, 3h):")
    s1 = crear_sala("Sala de Juntas A", 50000, 15, 3)
    if s1: servicios.append(s1)

    print("\n[6] Crear equipo válido con seguro:")
    s2 = crear_equipo("Proyector HD", 30000, 2, incluye_seguro=True)
    if s2: servicios.append(s2)

    print("\n[7] Crear asesoría inválida (nivel inexistente, debe fallar):")
    s3 = crear_asesoria("Consultoría TI", 200000, "Dr. García", "Expert")
    # s3 será None

    print("\n[8] Crear asesoría válida nivel Avanzado:")
    s4 = crear_asesoria("Consultoría TI", 200000, "Dr. García", "Avanzado")
    if s4: servicios.append(s4)

    # ── BLOQUE 3: RESERVAS ────────────────────────────────
    if len(clientes) >= 1 and len(servicios) >= 1:
        manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        print("\n[9] Crear reserva válida y procesarla:")
        r1 = crear_reserva(1, clientes[0], servicios[0], manana, "10:00", 3.0, "Reunión de equipo")
        if r1:
            reservas.append(r1)
            try:
                r1.confirmar()
                costo = r1.procesar()
                registrar_evento(f"Reserva #{r1.id} procesada. Costo: ${costo:,.0f}")
                print(f"  ✓ Reserva procesada. Costo total: ${costo:,.0f}")
            except ErrorReserva as e:
                registrar_excepcion(e, "Procesamiento R1")
                print(f"  ✗ {e}")

        print("\n[10] Intentar reservar el mismo servicio en horario solapado (debe fallar):")
        r2 = crear_reserva(2, clientes[0], servicios[0], manana, "11:00", 2.0)
        # Fallará por solapamiento de horario (sala A aún no termina)

    print("\n" + "="*60)
    print("  FIN DE SIMULACIÓN")
    print("="*60)

    return clientes, servicios, reservas