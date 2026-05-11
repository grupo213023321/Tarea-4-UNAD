##########################################################
#
# --- Archivo main.py ---
#
# - Ultima actualización: 09 - 5 - 2026
# - Aporte: Daniel Serrano Rivera
#
# Descripción: Punto de entrada del sistema.
#              Integra la lógica principal, el menú de
#              consola y la simulación automática de
#              operaciones requeridas por la guía.
#
##########################################################

import sys
import uuid
from datetime import datetime, timedelta

from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)
from log import (
    registrar_evento, registrar_excepcion,
    registrar_inicio_sesion, registrar_cierre_sesion,
    leer_log
)
from servicios import simular_10_operaciones

######################################
# CLASE PROGRAMA (MENÚ DE CONSOLA)
######################################

class Programa:
    """Controlador principal del sistema Software FJ en modo consola."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    # ── Menú ──────────────────────────────────────────────

    def mostrar_menu(self) -> str:
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
        print("\n--- Registro de Cliente ---")
        try:
            id_sistema = str(uuid.uuid4())
            id_c      = input("  ID Cliente:  ").strip()
            nombre    = input("  Nombre:      ").strip()
            direccion = input("  Dirección:   ").strip()
            correo    = input("  Correo:      ").strip()
            telefono  = input("  Teléfono:    ").strip()

            nuevo_cliente = Cliente(id_sistema, id_c, nombre, direccion, correo, telefono)

        except ErrorDatosCliente as e:
            registrar_excepcion(e, "Registro de Cliente")
            print(f"  ✗ Dato inválido: {e}")
        except Exception as e:
            registrar_excepcion(e, "Registro de Cliente (inesperado)")
            print(f"  ✗ Error inesperado: {e}")
        else:
            self.clientes.append(nuevo_cliente)
            registrar_evento(f"Cliente registrado: {nuevo_cliente}")
            print(f"  ✓ Cliente registrado: {nuevo_cliente}")
        finally:
            print("  (Operación de registro finalizada)")

    # ── Creación de Servicios ─────────────────────────────

    def ejecutar_crear_servicio(self):
        print("\n--- Crear Servicio ---")
        print("  a) Sala de reuniones")
        print("  b) Alquiler de equipo")
        print("  c) Asesoría especializada")
        tipo = input("  Tipo (a/b/c): ").strip().lower()

        try:
            nombre    = input("  Nombre del servicio: ").strip()
            precio    = float(input("  Precio base ($): ").strip())
            id_svc    = str(uuid.uuid4())

            if tipo == "a":
                capacidad = int(input("  Capacidad (personas): ").strip())
                horas     = float(input("  Horas reservadas: ").strip())
                svc = ReservaSala(id_svc, nombre, precio, capacidad, horas)

            elif tipo == "b":
                dias   = int(input("  Días de alquiler: ").strip())
                seguro = input("  ¿Incluye seguro? (s/n): ").strip().lower() == "s"
                svc = AlquilerEquipo(id_svc, nombre, precio, dias, seguro)

            elif tipo == "c":
                consultor = input("  Nombre del consultor: ").strip()
                print("  Nivel: Basico / Intermedio / Avanzado")
                nivel = input("  Nivel: ").strip()
                svc = AsesoriaEspecializada(id_svc, nombre, precio, consultor, nivel)

            else:
                print("  ✗ Opción no válida.")
                return

        except (ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "Creación de Servicio")
            print(f"  ✗ Error en servicio: {e}")
        except ValueError:
            print("  ✗ Valor numérico inválido.")
        except Exception as e:
            registrar_excepcion(e, "Creación de Servicio (inesperado)")
            print(f"  ✗ Error inesperado: {e}")
        else:
            self.servicios.append(svc)
            registrar_evento(f"Servicio creado: {svc.mostrar_info()}")
            print(f"  ✓ Servicio creado: {svc.obtener_detalles()}")

    # ── Creación de Reserva ───────────────────────────────

    def ejecutar_crear_reserva(self):
        if not self.clientes:
            print("  ⚠ No hay clientes registrados.")
            return
        if not self.servicios:
            print("  ⚠ No hay servicios creados.")
            return

        print("\n--- Crear Reserva ---")

        # Mostrar clientes
        print("  Clientes disponibles:")
        for i, c in enumerate(self.clientes):
            print(f"    [{i}] {c}")
        try:
            idx_c = int(input("  Seleccione cliente (número): ").strip())
            cliente = self.clientes[idx_c]
        except (ValueError, IndexError):
            print("  ✗ Selección de cliente inválida.")
            return

        # Mostrar servicios
        print("  Servicios disponibles:")
        for i, s in enumerate(self.servicios):
            print(f"    [{i}] {s.nombre} — {s.obtener_detalles()}")
        try:
            idx_s = int(input("  Seleccione servicio (número): ").strip())
            servicio = self.servicios[idx_s]
        except (ValueError, IndexError):
            print("  ✗ Selección de servicio inválida.")
            return

        try:
            fecha_str = input("  Fecha (YYYY-MM-DD): ").strip()
            hora_str  = input("  Hora  (HH:MM):      ").strip()
            duracion  = float(input("  Duración (horas):   ").strip())
            notas     = input("  Notas (opcional):   ").strip()
            id_res    = len(self.reservas) + 1

            reserva = Reserva.crear_reserva(
                id_res, cliente, servicio, fecha_str, hora_str, duracion, notas
            )
        except ErrorReserva as e:
            registrar_excepcion(e, "Crear Reserva")
            print(f"  ✗ No se pudo crear la reserva: {e}")
        except ValueError:
            print("  ✗ Duración inválida.")
        except Exception as e:
            registrar_excepcion(e, "Crear Reserva (inesperado)")
            print(f"  ✗ Error inesperado: {e}")
        else:
            self.reservas.append(reserva)
            registrar_evento(f"Reserva creada: {reserva}")
            print(f"  ✓ {reserva}")

            # Preguntar si confirmar de inmediato
            if input("  ¿Confirmar ahora? (s/n): ").strip().lower() == "s":
                try:
                    reserva.confirmar()
                    registrar_evento(f"Reserva #{reserva.id} confirmada")
                    print("  ✓ Reserva confirmada.")
                except ErrorReserva as e:
                    registrar_excepcion(e, "Confirmar Reserva")
                    print(f"  ✗ {e}")

    # ── Listado de Reservas ───────────────────────────────

    def listar_reservas(self):
        print("\n--- Reservas Registradas ---")
        if not self.reservas:
            print("  (No hay reservas registradas)")
            return

        for reserva in self.reservas:
            try:
                costo = reserva.servicio.calcular_costo()
                costo_str = f"${costo:,.2f}"
            except ErrorCalculoFinanciero as e:
                registrar_excepcion(e, "Listar Reservas")
                costo_str = "(error de cálculo)"

            print(f"  {reserva} | Costo estimado: {costo_str}")

    # ── Mostrar Clientes ──────────────────────────────────

    def mostrar_clientes(self):
        print("\n--- Lista de Clientes ---")
        if not self.clientes:
            print("  (No hay clientes registrados)")
            return
        for i, c in enumerate(self.clientes, 1):
            print(f"  [{i}] {c.mostrar_info()}")
        print(f"\n  Total: {len(self.clientes)} cliente(s)")

    # ── Ver Log ───────────────────────────────────────────

    def mostrar_log(self):
        print("\n--- Últimas 20 líneas del Log ---")
        for linea in leer_log(20):
            print(" ", linea.rstrip())

    # ── Ciclo principal ───────────────────────────────────

    def iniciar(self):
        registrar_inicio_sesion()
        while True:
            opcion = self.mostrar_menu()

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
                clientes, servicios, reservas = simular_10_operaciones()
                # Integrar resultados de la simulación en el programa
                self.clientes.extend(clientes)
                self.servicios.extend(servicios)
                self.reservas.extend(reservas)
            elif opcion == "8":
                registrar_cierre_sesion()
                print("\n  Hasta pronto. Sistema cerrado.\n")
                break
            else:
                print("  ⚠ Opción no válida. Intente de nuevo.")


######################################
# PUNTO DE ENTRADA
######################################

if __name__ == "__main__":
    app = Programa()

    # ── Datos de prueba precargados ────────────────────────
    try:
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C001", "Daniel Serrano", "Calle 1 #456",
                    "daniel@example.com", "3001234567"))
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C002", "Carlos Ruiz", "Carrera 2 #098",
                    "carlos@example.com", "3109876543"))
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C003", "Ronald Molina", "Carrera 1 N5-6",
                    "ronald@example.com", "3207654321"))
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C004", "Camila Torres", "Carrera 2 #6",
                    "camila@example.com", "3154443322"))
        app.clientes.append(
            Cliente(str(uuid.uuid4()), "C005", "Miguel Pérez", "Av Jim 56-45",
                    "miguel@example.com", "3003332211"))

        registrar_evento("5 clientes de prueba cargados al inicio.")
    except ErrorDatosCliente as e:
        registrar_excepcion(e, "Carga inicial de clientes")
        print(f"Advertencia: no se pudieron cargar todos los clientes de prueba: {e}")

    app.iniciar()