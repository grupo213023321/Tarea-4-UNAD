##########################################################
#
# --- Archivo servicios.py ---
#
# - Última actualización: 12 - 5 - 2026
#
# Descripción: Funciones auxiliares para gestión y
#              simulación de servicios y reservas.
#              Usado por main.py para ejecutar las 10
#              operaciones requeridas por la guía,
#              demostrando manejo completo de excepciones
#              con try/except/else/finally.
#
##########################################################

import uuid                                  # Para generar IDs únicos automáticamente
from datetime import datetime, timedelta     # Para manejar fechas y calcular el día siguiente

# Importa todas las clases del sistema
from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)

# Importa funciones del módulo de log para registrar eventos y errores
from log import registrar_evento, registrar_excepcion


# ─── Helpers de creación ───────────────────────────────────
# Estas funciones encapsulan la lógica de creación de objetos
# con manejo completo de excepciones (try/except/else/finally)


def crear_cliente(id_cliente, nombre, direccion, correo, telefono) -> Cliente | None:
    """
    Intenta crear un objeto Cliente con manejo robusto de excepciones.

    Implementa el patrón try/except/else/finally requerido por la guía:
    - try: intenta crear el cliente
    - except: captura errores de datos inválidos
    - else: se ejecuta solo si NO hubo excepción (registro exitoso)
    - finally: siempre se ejecuta (punto de extensión para liberar recursos)

    Parámetros:
        id_cliente (str): identificador legible del cliente.
        nombre     (str): nombre completo.
        direccion  (str): dirección de residencia.
        correo     (str): correo electrónico.
        telefono   (str): número de teléfono (10 dígitos).

    Retorna:
        Cliente si la creación fue exitosa, None si falló.
    """
    cliente = None  # Valor por defecto si la creación falla

    try:
        # Genera un UUID único como identificador interno del sistema
        id_sistema = str(uuid.uuid4())

        # Intenta crear el objeto Cliente; puede lanzar ErrorDatosCliente
        # si algún campo no cumple las validaciones
        cliente = Cliente(id_sistema, id_cliente, nombre, direccion, correo, telefono)

    except ErrorDatosCliente as e:
        # Captura errores específicos de datos de cliente (correo, teléfono, nombre)
        registrar_excepcion(e, contexto="Registro de Cliente")
        print(f"  ✗ Error al registrar cliente '{nombre}': {e}")

    except Exception as e:
        # Captura cualquier otro error inesperado que no sea ErrorDatosCliente
        registrar_excepcion(e, contexto="Registro de Cliente (inesperado)")
        print(f"  ✗ Error inesperado: {e}")

    else:
        # Este bloque SOLO se ejecuta si el try terminó sin excepciones
        # Registra el evento exitoso en el log y notifica por consola
        registrar_evento(f"Cliente registrado: {cliente}")
        print(f"  ✓ Cliente registrado: {cliente}")

    finally:
        # Este bloque SIEMPRE se ejecuta (con o sin excepción)
        # Aquí se podría cerrar una conexión, liberar un lock, etc.
        # Se deja como punto de extensión del sistema
        pass

    return cliente  # Retorna el cliente creado o None si falló


def crear_sala(nombre, precio_base, capacidad, horas) -> ReservaSala | None:
    """
    Crea una ReservaSala con manejo de excepciones.

    Implementa try/except/else para garantizar que solo se registre
    en el log si la sala fue creada exitosamente.

    Parámetros:
        nombre      (str):   nombre descriptivo de la sala.
        precio_base (float): precio por hora de la sala.
        capacidad   (int):   número máximo de personas.
        horas       (float): duración de la reserva en horas.

    Retorna:
        ReservaSala si fue creada exitosamente, None si falló.
    """
    servicio = None  # Valor por defecto si la creación falla

    try:
        # Intenta crear la sala; puede lanzar ErrorDisponibilidadServicio
        # (capacidad inválida) o ErrorCalculoFinanciero (horas inválidas)
        servicio = ReservaSala(str(uuid.uuid4()), nombre, precio_base, capacidad, horas)

    except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
        # Captura errores de parámetros inválidos de la sala
        registrar_excepcion(e, contexto="Creación Sala")
        print(f"  ✗ Error al crear sala '{nombre}': {e}")

    else:
        # Solo se ejecuta si la sala fue creada sin errores
        registrar_evento(f"Sala creada: {servicio.mostrar_info()}")
        print(f"  ✓ Sala creada: {servicio.obtener_detalles()}")

    return servicio  # Retorna la sala creada o None si falló


def crear_equipo(nombre, precio_base, dias, incluye_seguro=False) -> AlquilerEquipo | None:
    """
    Crea un AlquilerEquipo con manejo de excepciones.

    Parámetros:
        nombre         (str):  nombre del equipo.
        precio_base    (float): precio por día de alquiler.
        dias           (int):  número de días de alquiler.
        incluye_seguro (bool): si True, agrega $50,000 al costo (por defecto False).

    Retorna:
        AlquilerEquipo si fue creado exitosamente, None si falló.
    """
    servicio = None  # Valor por defecto si la creación falla

    try:
        # Intenta crear el equipo; puede lanzar ErrorCalculoFinanciero si dias <= 0
        servicio = AlquilerEquipo(str(uuid.uuid4()), nombre, precio_base, dias, incluye_seguro)

    except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
        # Captura errores de parámetros inválidos del equipo
        registrar_excepcion(e, contexto="Creación Equipo")
        print(f"  ✗ Error al crear equipo '{nombre}': {e}")

    else:
        # Solo se ejecuta si el equipo fue creado sin errores
        registrar_evento(f"Equipo creado: {servicio.mostrar_info()}")
        print(f"  ✓ Equipo creado: {servicio.obtener_detalles()}")

    return servicio  # Retorna el equipo creado o None si falló


def crear_asesoria(nombre, precio_base, consultor, nivel) -> AsesoriaEspecializada | None:
    """
    Crea una AsesoriaEspecializada con manejo de excepciones.

    Parámetros:
        nombre      (str):   nombre de la asesoría.
        precio_base (float): precio base antes de aplicar multiplicador.
        consultor   (str):   nombre del profesional a cargo.
        nivel       (str):   nivel de complejidad (Basico/Intermedio/Avanzado).

    Retorna:
        AsesoriaEspecializada si fue creada exitosamente, None si falló.
    """
    servicio = None  # Valor por defecto si la creación falla

    try:
        # Intenta crear la asesoría; puede lanzar ErrorDisponibilidadServicio
        # si el nivel no está en ['Basico', 'Intermedio', 'Avanzado']
        servicio = AsesoriaEspecializada(str(uuid.uuid4()), nombre, precio_base, consultor, nivel)

    except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
        # Captura errores de nivel inválido u otros parámetros incorrectos
        registrar_excepcion(e, contexto="Creación Asesoría")
        print(f"  ✗ Error al crear asesoría '{nombre}': {e}")

    else:
        # Solo se ejecuta si la asesoría fue creada sin errores
        registrar_evento(f"Asesoría creada: {servicio.mostrar_info()}")
        print(f"  ✓ Asesoría creada: {servicio.obtener_detalles()}")

    return servicio  # Retorna la asesoría creada o None si falló


def crear_reserva(id_reserva, cliente, servicio, fecha_str, hora_str,
                    duracion, notas="") -> Reserva | None:
    """
    Crea una Reserva usando el método de fábrica Reserva.crear_reserva().

    Demuestra el manejo de ErrorReserva y excepciones encadenadas
    que pueden generarse durante la creación de una reserva.

    Parámetros:
        id_reserva (int):      número de la reserva.
        cliente    (Cliente):  cliente que realiza la reserva.
        servicio   (Servicio): servicio a reservar.
        fecha_str  (str):      fecha en formato "YYYY-MM-DD".
        hora_str   (str):      hora en formato "HH:MM".
        duracion   (float):    duración en horas.
        notas      (str):      observaciones opcionales.

    Retorna:
        Reserva si fue creada exitosamente, None si falló.
    """
    reserva = None  # Valor por defecto si la creación falla

    try:
        # Llama al método de fábrica que valida fechas y solapamientos
        # Puede lanzar ErrorReserva por: fecha pasada, formato incorrecto,
        # solapamiento de horario
        reserva = Reserva.crear_reserva(
            id_reserva, cliente, servicio, fecha_str, hora_str, duracion, notas
        )

    except ErrorReserva as e:
        # Captura errores específicos del ciclo de vida de la reserva
        registrar_excepcion(e, contexto="Crear Reserva")
        print(f"  ✗ Reserva fallida: {e}")

    except Exception as e:
        # Captura cualquier otro error inesperado durante la creación
        registrar_excepcion(e, contexto="Crear Reserva (inesperado)")
        print(f"  ✗ Error inesperado en reserva: {e}")

    else:
        # Solo se ejecuta si la reserva fue creada sin errores
        registrar_evento(f"Reserva creada: {reserva}")
        print(f"  ✓ Reserva creada: {reserva}")

    return reserva  # Retorna la reserva creada o None si falló


# ─── Simulación de las 10 operaciones requeridas ──────────

def simular_10_operaciones():
    """
    Ejecuta al menos 10 operaciones completas (válidas e inválidas)
    para demostrar el manejo robusto de excepciones del sistema.

    Incluye:
    - Registros válidos e inválidos de clientes
    - Creación correcta e incorrecta de servicios
    - Reservas exitosas y fallidas (solapamiento de horario)

    El sistema sigue funcionando después de cada error, demostrando
    la estabilidad y robustez requerida por la guía.

    Retorna:
        tuple: (clientes, servicios, reservas) listas de objetos creados exitosamente.
    """
    # Separador visual para identificar el inicio de la simulación en consola
    print("\n" + "="*60)
    print("  SIMULACIÓN AUTOMÁTICA — 10 OPERACIONES (según guía)")
    print("="*60)

    # Listas en memoria donde se almacenarán los objetos creados exitosamente
    clientes  = []
    servicios = []
    reservas  = []

    # ── BLOQUE 1: REGISTRO DE CLIENTES ────────────────────

    print("\n[1] Registro de cliente válido:")
    # Datos correctos: correo y teléfono válidos, nombre suficientemente largo
    c1 = crear_cliente("C001", "Daniel Serrano", "Calle 1 #45", "daniel@fj.com", "3001234567")
    if c1:
        clientes.append(c1)  # Solo agrega si la creación fue exitosa

    print("\n[2] Registro de cliente con correo inválido (debe fallar):")
    # El correo "correo_invalido" no tiene formato usuario@dominio.ext
    # Se espera que lanze ErrorDatosCliente y retorne None
    c2 = crear_cliente("C002", "Carlos Ruiz", "Carrera 2", "correo_invalido", "3109876543")
    # c2 será None → el sistema continúa sin interrumpirse

    print("\n[3] Registro de cliente con nombre muy corto (debe fallar):")
    # El nombre "Al" tiene solo 2 caracteres; el mínimo es 3
    # Se espera que lanze ErrorDatosCliente y retorne None
    c3 = crear_cliente("C003", "Al", "Av. 3", "al@fj.com", "3207654321")
    # c3 será None → el sistema continúa sin interrumpirse

    print("\n[4] Registro de segundo cliente válido:")
    # Datos correctos para el segundo cliente
    c4 = crear_cliente("C004", "Camila Torres", "Carrera 5 #12", "camila@fj.com", "3154443322")
    if c4:
        clientes.append(c4)  # Solo agrega si la creación fue exitosa

    # ── BLOQUE 2: CREACIÓN DE SERVICIOS ───────────────────

    print("\n[5] Crear sala válida (capacidad 15, 3h):")
    # Sala con parámetros correctos: capacidad entero positivo, horas > 0
    s1 = crear_sala("Sala de Juntas A", 50000, 15, 3)
    if s1:
        servicios.append(s1)

    print("\n[6] Crear equipo válido con seguro:")
    # Equipo con 2 días de alquiler e inclusión de seguro
    s2 = crear_equipo("Proyector HD", 30000, 2, incluye_seguro=True)
    if s2:
        servicios.append(s2)

    print("\n[7] Crear asesoría inválida (nivel inexistente, debe fallar):")
    # "Expert" no está en ['Basico', 'Intermedio', 'Avanzado']
    # Se espera que lanze ErrorDisponibilidadServicio y retorne None
    s3 = crear_asesoria("Consultoría TI", 200000, "Dr. García", "Expert")
    # s3 será None → el sistema continúa sin interrumpirse

    print("\n[8] Crear asesoría válida nivel Avanzado:")
    # "Avanzado" sí está en los niveles válidos → creación exitosa
    s4 = crear_asesoria("Consultoría TI", 200000, "Dr. García", "Avanzado")
    if s4:
        servicios.append(s4)

    # ── BLOQUE 3: RESERVAS ────────────────────────────────

    # Solo ejecuta las reservas si hay al menos un cliente y un servicio
    if len(clientes) >= 1 and len(servicios) >= 1:

        # Calcula la fecha de mañana para evitar reservas en el pasado
        manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        print("\n[9] Crear reserva válida y procesarla:")
        # Reserva con datos correctos: cliente real, servicio real, fecha futura
        r1 = crear_reserva(
            1, clientes[0], servicios[0],
            manana, "10:00", 3.0, "Reunión de equipo"
        )
        if r1:
            reservas.append(r1)
            try:
                # Confirma la reserva: cambia estado de pendiente → confirmada
                r1.confirmar()

                # Procesa la reserva: calcula costo y cambia a completada
                # Demuestra encadenamiento de excepciones si calcular_costo() falla
                costo = r1.procesar()

                # Registra el costo final en el log
                registrar_evento(f"Reserva #{r1.id} procesada. Costo: ${costo:,.0f}")
                print(f"  ✓ Reserva procesada. Costo total: ${costo:,.0f}")

            except ErrorReserva as e:
                # Captura errores en confirmar() o procesar()
                registrar_excepcion(e, "Procesamiento R1")
                print(f"  ✗ {e}")

        print("\n[10] Intentar reservar el mismo servicio en horario solapado (debe fallar):")
        # La Sala de Juntas A tiene una reserva de 3h desde las 10:00
        # Una nueva reserva a las 11:00 solapará con la anterior (termina a las 13:00)
        # Se espera ErrorReserva por solapamiento → retorna None
        r2 = crear_reserva(2, clientes[0], servicios[0], manana, "11:00", 2.0)
        # r2 será None → el sistema continúa funcionando correctamente

    # Separador visual de cierre de la simulación
    print("\n" + "="*60)
    print("  FIN DE SIMULACIÓN")
    print("="*60)

    # Retorna las listas de objetos creados exitosamente para
    # que main.py los integre al estado del programa
    return clientes, servicios, reservas