##########################################################
#
# --- Archivo main.py ---
#
# - Última actualización: 12 - 5 - 2026
# - Aporte: Daniel Serrano Rivera
#
# Descripción: Punto de entrada del sistema Software FJ
#              en modo consola. Contiene la clase Programa
#              que implementa el menú interactivo y conecta
#              todos los módulos del sistema. También
#              pre-carga datos de prueba al iniciar.
#
##########################################################

import sys   # Módulo del sistema (disponible para manejo de errores críticos)
import uuid  # Para generar IDs únicos tipo UUID para cada cliente
from datetime import datetime, timedelta  # Para manejo de fechas en reservas

# Importa todas las clases del dominio del sistema
from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva
)

from excepciones import (
    ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva,
)
# Importa las funciones de log para registro de eventos y errores
from log import (
    registrar_evento, registrar_excepcion,
    registrar_inicio_sesion, registrar_cierre_sesion,
    leer_log
)

# Importa la función que ejecuta la simulación automática de 10 operaciones
from servicios import simular_10_operaciones

# Importa la clase de validación para asegurar la integridad de los datos de entrada
from validadores import ValidadorDatos

######################################
# CLASE PROGRAMA (MENÚ DE CONSOLA)
######################################

class Programa:
    """
    Controlador principal del sistema Software FJ en modo consola.
    Mantiene las listas de datos en memoria (sin base de datos)
    y expone un menú numerado para que el usuario interactúe.
    """

    def __init__(self):
        """
        Inicializa las tres listas principales del sistema en memoria.
        Estas listas reemplazan a una base de datos, cumpliendo con
        el requisito de "sin base de datos" de la guía.
        """
        self.clientes  = []  # Lista de objetos Cliente registrados en sesión
        self.servicios = []  # Lista de objetos Servicio creados en sesión
        self.reservas  = []  # Lista de objetos Reserva creados en sesión

    # ── Menú ──────────────────────────────────────────────

    def mostrar_menu(self) -> str:
        """
        Imprime el menú principal en consola y captura la opción del usuario.

        Retorna:
            str: la opción ingresada por el usuario (sin espacios al inicio/final).
        """
        print(f"\n{'='*22} SOFTWARE FJ {'='*22}")
        print("  1. Registrar Cliente")
        print("  2. Crear Servicio (Sala / Equipo / Asesoría)")
        print("  3. Crear Reserva")
        print("  4. Listar Reservas y Calcular Costos")
        print("  5. Mostrar Clientes")
        print("  6. Mostrar últimas líneas del Log")
        print("  7. Simular 10 operaciones automáticas")
        print("  8. Salir")
        print(f"{'='*57}")
        return input("  Seleccione una opción: ").strip()

    # ── Registro de Cliente ───────────────────────────────

    def ejecutar_registro_cliente(self):
        """
        Guía al usuario para registrar un nuevo cliente mediante consola.

        Implementa try/except/else/finally completo:
        - try: lee los datos y crea el objeto Cliente
        - except ErrorDatosCliente: captura errores de validación esperados
        - except Exception: captura errores inesperados no anticipados
        - else: se ejecuta si NO hubo error (registro exitoso)
        - finally: se ejecuta SIEMPRE (mensaje de cierre de la operación)
        """
        print("\n--- Registro de Cliente ---")
        try:
            # Genera un UUID único como identificador interno del sistema
            id_sistema = str(uuid.uuid4())

            # Lee todos los datos del cliente desde la entrada estándar (consola)
            id_c      = input("  ID Cliente:  ").strip()
            nombre    = input("  Nombre:      ").strip()
            direccion = input("  Dirección:   ").strip()
            correo    = input("  Correo:      ").strip()
            telefono  = input("  Teléfono:    ").strip()

            # Intenta crear el objeto Cliente; puede lanzar ErrorDatosCliente
            # si algún dato no pasa las validaciones del constructor o los setters
            nuevo_cliente = Cliente(id_sistema, id_c, nombre, direccion, correo, telefono)

        except ErrorDatosCliente as e:
            # Captura errores conocidos de datos inválidos del cliente
            registrar_excepcion(e, "Registro de Cliente")  # Guarda en el log
            print(f"  ✗ Dato inválido: {e}")               # Muestra en consola

        except Exception as e:
            # Captura cualquier otro error no anticipado
            registrar_excepcion(e, "Registro de Cliente (inesperado)")
            print(f"  ✗ Error inesperado: {e}")

        else:
            # Este bloque solo se ejecuta si el try terminó sin excepciones
            self.clientes.append(nuevo_cliente)  # Agrega a la lista en memoria
            registrar_evento(f"Cliente registrado: {nuevo_cliente}")  # Registra en log
            print(f"  ✓ Cliente registrado: {nuevo_cliente}")

        finally:
            # Este bloque SIEMPRE se ejecuta, haya o no excepción
            # Sirve como confirmación visual de que la operación finalizó
            print("  (Operación de registro finalizada)")

    # ── Creación de Servicios ─────────────────────────────

    def ejecutar_crear_servicio(self):
        """
        Guía al usuario para crear uno de los tres tipos de servicio.
        Cada tipo tiene sus propios campos de entrada.

        Maneja errores específicos de cada tipo de servicio:
        - ErrorDisponibilidadServicio: capacidad o nivel inválido
        - ErrorCalculoFinanciero: precio, horas o días inválidos
        - ValueError: datos no numéricos donde se esperan números
        """
        print("\n--- Crear Servicio ---")
        # Muestra las opciones disponibles de tipo de servicio
        print("  a) Sala de reuniones")
        print("  b) Alquiler de equipo")
        print("  c) Asesoría especializada")
        tipo = input("  Tipo (a/b/c): ").strip().lower()  # Normaliza a minúscula

        try:
            # Lee los campos comunes a todos los servicios
            nombre = input("  Nombre del servicio: ").strip()
            # Valida el nombre de inmediato; si es inválido, detiene el proceso y salta al manejo de errores
            ValidadorDatos.validar_nombre_servicio(nombre)
            
            precio = float(input("  Precio base ($): ").strip())  # float() puede lanzar ValueError
            id_svc = str(uuid.uuid4())  # ID único para el servicio

            if tipo == "a":
                # Campos específicos de sala de reuniones
                capacidad = int(input("  Capacidad (personas): ").strip())
                horas     = float(input("  Horas reservadas: ").strip())
                # Crea la sala; puede lanzar ErrorDisponibilidadServicio o ErrorCalculoFinanciero
                svc = ReservaSala(id_svc, nombre, precio, capacidad, horas)

            elif tipo == "b":
                # Campos específicos de alquiler de equipo
                dias   = int(input("  Días de alquiler: ").strip())
                seguro = input("  ¿Incluye seguro? (s/n): ").strip().lower() == "s"
                # Crea el equipo; puede lanzar ErrorCalculoFinanciero si dias <= 0
                svc = AlquilerEquipo(id_svc, nombre, precio, dias, seguro)

            elif tipo == "c":
                # Campos específicos de asesoría especializada
                consultor = input("  Nombre del consultor: ").strip()
                print("  Nivel: Basico / Intermedio / Avanzado")
                nivel = input("  Nivel: ").strip()
                # Crea la asesoría; puede lanzar ErrorDisponibilidadServicio si nivel inválido
                svc = AsesoriaEspecializada(id_svc, nombre, precio, consultor, nivel)

            else:
                # Si el usuario ingresa una opción diferente a a, b o c
                print("  ✗ Opción no válida.")
                return  # Sale del método sin crear ningún servicio

        except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero, ErrorDatosCliente) as e:
            # Captura errores específicos de creación de servicios
            registrar_excepcion(e, "Creación de Servicio")
            print(f"  ✗ error en servicio: {e}")
    
        except ValueError:
            # Captura errores cuando el usuario ingresa texto donde se esperaba número
            print("  ✗ Valor numérico inválido.")

        except Exception as e:
            # Captura cualquier otro error no anticipado
            registrar_excepcion(e, "Creación de Servicio (inesperado)")
            print(f"  ✗ Error inesperado: {e}")

        else:
            # Solo se ejecuta si el servicio fue creado sin errores
            self.servicios.append(svc)                          # Agrega a la lista en memoria
            registrar_evento(f"Servicio creado: {svc.mostrar_info()}")  # Registra en log
            print(f"  ✓ Servicio creado: {svc.obtener_detalles()}")

    # ── Creación de Reserva ───────────────────────────────

    def ejecutar_crear_reserva(self):
        """
        Guía al usuario para crear una reserva asociando un cliente con un servicio.
        Verifica que existan clientes y servicios antes de continuar.
        Ofrece también confirmar la reserva inmediatamente después de crearla.
        """
        # Verificaciones previas: no se puede reservar sin clientes o servicios
        if not self.clientes:
            print("  ⚠ No hay clientes registrados.")
            return
        if not self.servicios:
            print("  ⚠ No hay servicios creados.")
            return

        print("\n--- Crear Reserva ---")

        # Muestra la lista de clientes disponibles con su índice
        print("  Clientes disponibles:")
        for i, c in enumerate(self.clientes):
            print(f"    [{i}] {c}")

        try:
            # El usuario elige el índice del cliente
            idx_c   = int(input("  Seleccione cliente (número): ").strip())
            cliente = self.clientes[idx_c]  # IndexError si el índice está fuera de rango
        except (ValueError, IndexError):
            print("  ✗ Selección de cliente inválida.")
            return

        # Muestra la lista de servicios disponibles con su índice
        print("  Servicios disponibles:")
        for i, s in enumerate(self.servicios):
            print(f"    [{i}] {s.nombre} — {s.obtener_detalles()}")

        try:
            # El usuario elige el índice del servicio
            idx_s    = int(input("  Seleccione servicio (número): ").strip())
            servicio = self.servicios[idx_s]  # IndexError si el índice está fuera de rango
        except (ValueError, IndexError):
            print("  ✗ Selección de servicio inválida.")
            return

        try:
            # Lee los parámetros de la reserva desde consola
            fecha_str = input("  Fecha (YYYY-MM-DD): ").strip()
            hora_str  = input("  Hora  (HH:MM):      ").strip()
            duracion  = float(input("  Duración (horas):   ").strip())
            notas     = input("  Notas (opcional):   ").strip()
            id_res    = len(self.reservas) + 1  # ID auto-incremental

            # Usa el método de fábrica para crear la reserva con validaciones
            # Puede lanzar: ErrorReserva (fecha pasada, solapamiento, formato)
            reserva = Reserva.crear_reserva(
                id_res, cliente, servicio, fecha_str, hora_str, duracion, notas
            )

        except ErrorReserva as e:
            # Captura errores específicos del ciclo de vida de reservas
            registrar_excepcion(e, "Crear Reserva")
            print(f"  ✗ No se pudo crear la reserva: {e}")

        except ValueError:
            # Captura error si la duración ingresada no es un número válido
            print("  ✗ Duración inválida.")

        except Exception as e:
            # Captura cualquier otro error no anticipado
            registrar_excepcion(e, "Crear Reserva (inesperado)")
            print(f"  ✗ Error inesperado: {e}")

        else:
            # Solo se ejecuta si la reserva fue creada sin errores
            self.reservas.append(reserva)                     # Agrega a la lista en memoria
            registrar_evento(f"Reserva creada: {reserva}")   # Registra en log
            print(f"  ✓ {reserva}")

            # Ofrece confirmar la reserva inmediatamente después de crearla
            if input("  ¿Confirmar ahora? (s/n): ").strip().lower() == "s":
                try:
                    reserva.confirmar()  # Cambia estado: pendiente → confirmada
                    registrar_evento(f"Reserva #{reserva.id} confirmada")
                    print("  ✓ Reserva confirmada.")
                except ErrorReserva as e:
                    # Podría fallar si la reserva ya fue confirmada o cancelada
                    registrar_excepcion(e, "Confirmar Reserva")
                    print(f"  ✗ {e}")

    # ── Listado de Reservas ───────────────────────────────

    def listar_reservas(self):
        """
        Muestra todas las reservas registradas con su costo estimado.
        Si el cálculo del costo falla para alguna reserva, lo indica
        sin interrumpir la visualización del resto.
        """
        print("\n--- Reservas Registradas ---")
        if not self.reservas:
            print("  (No hay reservas registradas)")
            return

        for reserva in self.reservas:
            try:
                # calcular_costo() es polimórfico: cada servicio aplica su fórmula
                costo     = reserva.servicio.calcular_costo()
                costo_str = f"${costo:,.2f}"  # Formato monetario con separadores de miles

            except ErrorCalculoFinanciero as e:
                # Si el cálculo falla, registra el error pero continúa con las demás
                registrar_excepcion(e, "Listar Reservas")
                costo_str = "(error de cálculo)"  # Muestra indicador de error

            print(f"  {reserva} | Costo estimado: {costo_str}")

    # ── Mostrar Clientes ──────────────────────────────────

    def mostrar_clientes(self):
        """
        Muestra la lista completa de clientes registrados en memoria.
        Incluye el total al final para referencia rápida.
        """
        print("\n--- Lista de Clientes ---")
        if not self.clientes:
            print("  (No hay clientes registrados)")
            return

        # enumerate(lista, 1) empieza el contador en 1 para visualización
        for i, c in enumerate(self.clientes, 1):
            print(f"  [{i}] {c.mostrar_info()}")  # mostrar_info() es polimórfico

        print(f"\n  Total: {len(self.clientes)} cliente(s)")

    # ── Ver Log ───────────────────────────────────────────

    def mostrar_log(self):
        """
        Muestra las últimas 20 líneas del archivo sistema_fj.log en consola.
        Útil para depuración y verificación de eventos durante la sesión.
        """
        print("\n--- Últimas 20 líneas del Log ---")
        for linea in leer_log(20):
            # rstrip() elimina el salto de línea al final de cada línea del log
            print(" ", linea.rstrip())

    # ── Ciclo principal ───────────────────────────────────

    def iniciar(self):
        """
        Inicia el bucle principal del programa.
        Registra inicio de sesión en el log y presenta el menú en un
        ciclo continuo hasta que el usuario elija la opción de salir.
        """
        # Marca el inicio de sesión en el archivo de log
        registrar_inicio_sesion()

        # Bucle infinito: continúa hasta que el usuario elija salir (opción 8)
        while True:
            opcion = self.mostrar_menu()  # Muestra menú y captura opción

            if opcion == "1":
                self.ejecutar_registro_cliente()

            elif opcion == "2":
                self.ejecutar_crear_servicio()

            elif opcion == "3":
                self.ejecutar_crear_reserva()

            elif opcion == "4":
                self.listar_reservas()

            elif opcion == "5":
                self.mostrar_clientes()

            elif opcion == "6":
                self.mostrar_log()

            elif opcion == "7":
                # Ejecuta la simulación automática y recibe los objetos creados
                clientes, servicios, reservas = simular_10_operaciones()

                # Integra los resultados de la simulación al estado actual del programa
                # extend() agrega todos los elementos de la lista sin reemplazar los existentes
                self.clientes.extend(clientes)
                self.servicios.extend(servicios)
                self.reservas.extend(reservas)

            elif opcion == "8":
                # Marca el cierre de sesión en el log y termina el bucle
                registrar_cierre_sesion()
                print("\n  Hasta pronto. Sistema cerrado.\n")
                break  # Sale del while True

            else:
                # Cualquier entrada distinta a 1-8 se considera inválida
                print("  ⚠ Opción no válida. Intente de nuevo.")


######################################
# PUNTO DE ENTRADA
######################################

if __name__ == "__main__":
    """
    Bloque de ejecución principal.
    Solo se ejecuta cuando el archivo se corre directamente
    (no cuando es importado como módulo por otro archivo).
    """
    # Crea la instancia principal del programa
    app = Programa()

    # ── Datos de prueba precargados ────────────────────────
    # Se cargan 5 clientes de muestra al inicio para facilitar las pruebas
    # del sistema sin necesidad de registrarlos manualmente cada vez.
    try:
        # Cliente 1: datos completamente válidos
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C001", "Daniel Serrano", "Calle 1 #456",
                    "daniel@example.com", "3001234567"))

        # Cliente 2: datos completamente válidos
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C002", "Carlos Ruiz", "Carrera 2 #098",
                    "carlos@example.com", "3109876543"))

        # Cliente 3: datos completamente válidos
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C003", "Ronald Molina", "Carrera 1 N5-6",
                    "ronald@example.com", "3207654321"))

        # Cliente 4: datos completamente válidos
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C004", "Camila Torres", "Carrera 2 #6",
                    "camila@example.com", "3154443322"))

        # Cliente 5: datos completamente válidos
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C005", "Miguel Pérez", "Av Jim 56-45",
                    "miguel@example.com", "3003332211"))

        # Registra en el log que los clientes de prueba fueron cargados correctamente
        registrar_evento("5 clientes de prueba cargados al inicio.")

    except ErrorDatosCliente as e:
        # Si algún cliente de prueba falla (por ejemplo, si se modifica algún dato),
        # lo registra y continúa con los clientes que sí se cargaron
        registrar_excepcion(e, "Carga inicial de clientes")
        print(f"Advertencia: no se pudieron cargar todos los clientes de prueba: {e}")

    # Inicia el bucle principal del programa con el menú de consola
    app.iniciar()