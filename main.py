##########################################################
#
# --- Archivo main.py ---
#
# - Ultima actualización: 08 - 5 - 2026
# - Aporte: Daniel Serrano Rivera
#
# Descripción: Contiene la lógica principal llamando a las clases y funciones de los demas archivos 
#
##########################################################


######################################
# IMPORTACIONES
######################################

import sys
from datetime import datetime
import uuid

# Importación de módulos
# Asegurarse de que classes.py y log.py estén en la misma carpeta
from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)


#Se importa el script log una vez este creado   --- A IMPLEMENTAR --- 
"""from log import registrar_evento, registrar_excepcion, registrar_inicio_sesion, registrar_cierre_sesion"""


######################################
# CLASE PROGRAMA
######################################

class Programa:
    
    def __init__(self):
        #Inicializamos las listas donde se alojaran los clientes, servicios y reservas, funciona como base de datos temporal
        
        self.clientes = []
        self.servicios = []
        self.reservas = []

# SE IMPLEMENTA EL PROGRAMA EN LA TERMINAL PARA PRUEBAS 
# A IMPLEMENTAR HUD CON TKINTER

    def mostrar_menu(self):
        print(f"\n{'='*20} SOFTWARE FJ - GESTIÓN {'='*20}\n")
        print("1. Registrar Cliente")
        #print("2. Crear Servicio (Sala/Equipo/Asesoría)")
        #print("3. Crear Reserva")
        #print("4. Listar Reservas y Calcular Costos")
        #print("5. Salir")
        print("---test--- Consultar Lista clientes")
        return input("Seleccione una opción: ")

    def ejecutar_registro_cliente(self):
        try:
            print("\n--- Registro de Cliente ---")

            id_sistema = str(uuid.uuid4())

            id_c      = input("ID Cliente:  ").strip()
            nombre    = input("Nombre:      ").strip()
            direccion = input("Dirección:   ").strip()
            correo    = input("Correo:      ").strip()
            telefono  = input("Teléfono:    ").strip()

            nuevo_cliente = Cliente(id_sistema, id_c, nombre, direccion, correo, telefono)

            self.clientes.append(nuevo_cliente)

            print(f"\n✅ Cliente registrado exitosamente: {nuevo_cliente}")

        except:
            pass #IMPLEMENTAR EXCEPCION, PARA ERRORES

    def ejecutar_crear_reserva(self):
        """Lógica para conectar un cliente con un servicio"""
        if not self.clientes:
            print("⚠️ No hay clientes registrados.")
            return

        try:
            print("\n--- Crear Nueva Reserva ---")
            # Simulación de selección (en GUI sería un ComboBox)
            cliente = self.clientes[-1] 
            
            # Crear un servicio rápido para la prueba
            servicio = ReservaSala("S01", "Sala de Juntas A", 50000, 10)
            
            nueva_reserva = Reserva(cliente, servicio)
            nueva_reserva.confirmar_reserva()
            self.reservas.append(nueva_reserva)
            
            #registrar_evento(f"Reserva creada para {cliente.nombre}", nivel="info")
            print(f"✅ Reserva exitosa: {nueva_reserva}")
            
        except (ErrorDisponibilidadServicio, ErrorReserva) as e:
            #registrar_excepcion(e, contexto="Creación de Reserva")
            print(f"❌ No se pudo crear la reserva: {e}")

    def listar_operaciones(self):
        print("\n--- Resumen de Operaciones ---")
        for res in self.reservas:
            try:
                costo = res.calcular_costo_reserva(aplicar_iva=True)
                print(f"{res} | Costo Total (IVA): ${costo:,.2f}")
            except ErrorCalculoFinanciero as e:
                print(f"❌ Error al calcular costo de {res._id}: {e}")

    def mostrar_clientes(self):
        print("\n--- Lista de Clientes Registrados ---\n")
        
        if not self.clientes:
            print("No hay clientes registrados aún.")
            return
        
        for i, cliente in enumerate(self.clientes, start=1):
            print(f"\n[{i}] {cliente.mostrar_info()}")
        
        print(f"\nTotal: {len(self.clientes)} cliente(s)")

    def iniciar(self):
        #registrar_inicio_sesion()
        while True:
            opcion = self.mostrar_menu()
            if opcion == "1":
                self.ejecutar_registro_cliente()
            elif opcion == "2":
                print("Lógica de creación de servicios (prototipo)")
                
            elif opcion == "3":
                self.ejecutar_crear_reserva()
            elif opcion == "4":
                self.listar_operaciones()
            elif opcion == "test":
                self.mostrar_clientes()
            elif opcion == "5":
                #registrar_cierre_sesion()
                print("Saliendo del sistema...")
                break
            else:
                print("Opción no válida.")

if __name__ == "__main__":
    app = Programa()
    
    cliente = Cliente(900, "1004208724", "Daniel", "Calle 1 456", "test1@example.com", "345678901")
    app.clientes.append(cliente)
    cliente = Cliente(901, "1004208726", "Carlos", "Calle 2 098", "test2@example.com", "542624566")
    app.clientes.append(cliente)
    cliente = Cliente(902, "1004208724", "Ronald", "Carrera 1 N 5 6", "test3@example.com", "256246545")
    app.clientes.append(cliente)
    cliente = Cliente(903, "1004208724", "Camila", "Carrera 2 # 6", "test4@example.com", "456456455")
    app.clientes.append(cliente)
    cliente = Cliente(904, "1004208724", "Miguel", "Av Jim 56 45", "test5@example.com", "134534536")
    app.clientes.append(cliente)
    
    app.iniciar()
    