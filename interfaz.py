##########################################################
#
# --- Archivo interfaz.py ---
#
# - Ultima actualización: 11 - 5 - 2026
#
# Descripción: Interfaz gráfica con Tkinter.
#              Gestión de Clientes, Servicios y Reservas.
#              Conectada a log.py para registro de eventos.
#
##########################################################

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import uuid

from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)
from log import registrar_evento, registrar_excepcion, leer_log


class AplicacionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión FJ - Reservas")
        # Centrar la ventana en pantalla
        ancho, alto = 1200, 700
        x = (self.root.winfo_screenwidth()  - ancho) // 2
        y = (self.root.winfo_screenheight() - alto)  // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.configure(bg="#f0f0f0")

        # Icono: se aplica con after() para que Windows lo cargue
        # correctamente en la barra de tareas una vez la ventana esté lista
        self.root.after(100, self._aplicar_icono)

        # Datos en memoria
        self.clientes = []
        self.servicios = []
        self.reservas = []

        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=5)

        self.crear_menu_superior()
        self.crear_frames_principales()
        self.mostrar_frame_clientes()

    def _aplicar_icono(self):
        """Aplica el icono en la ventana y en la barra de tareas de Windows."""
        try:
            # Icono en la barra de título de la ventana
            self.root.iconbitmap("iconosistema.ico")
        except Exception:
            pass

        try:
            # Forzar icono en la barra de tareas de Windows via ctypes
            import ctypes
            import os
            ruta_ico = os.path.abspath("iconosistema.ico")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SoftwareFJ.Sistema.1.0")
            ctypes.windll.user32.SendMessageW(
                ctypes.windll.user32.GetActiveWindow(), 0x0080, 0,
                ctypes.windll.user32.LoadImageW(
                    None, ruta_ico, 1, 0, 0, 0x0010 | 0x0040
                )
            )
        except Exception:
            pass  # Si no es Windows o falla, continúa sin problema

    # ==================== MENÚ SUPERIOR ====================

    def crear_menu_superior(self):
        menu_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        menu_frame.pack(fill=tk.X)
        menu_frame.pack_propagate(False)

        tk.Label(menu_frame, text="🏢 SISTEMA DE GESTIÓN DE RESERVAS — Software FJ",
                    bg="#2c3e50", fg="white", font=("Arial", 16, "bold")).pack(pady=10)

        nav_frame = tk.Frame(self.root, bg="#34495e", height=40)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)

        botones_nav = [
            ("👥 Clientes",  self.mostrar_frame_clientes),
            ("🎯 Servicios", self.mostrar_frame_servicios),
            ("📅 Reservas",  self.mostrar_frame_reservas),
            ("📊 Reportes",  self.mostrar_frame_reportes),
            ("📋 Log",       self.mostrar_frame_log),
        ]
        for texto, comando in botones_nav:
            tk.Button(nav_frame, text=texto, command=comando,
                        bg="#34495e", fg="white", relief=tk.FLAT,
                        cursor="hand2", font=("Arial", 10, "bold")
                        ).pack(side=tk.LEFT, padx=15, pady=5)

    # ==================== FRAMES PRINCIPALES ====================

    def crear_frames_principales(self):
        self.frame_clientes  = tk.Frame(self.root, bg="#ecf0f1")
        self.frame_servicios = tk.Frame(self.root, bg="#ecf0f1")
        self.frame_reservas  = tk.Frame(self.root, bg="#ecf0f1")
        self.frame_reportes  = tk.Frame(self.root, bg="#ecf0f1")
        self.frame_log       = tk.Frame(self.root, bg="#ecf0f1")

    def limpiar_frames(self):
        for f in [self.frame_clientes, self.frame_servicios,
                    self.frame_reservas, self.frame_reportes, self.frame_log]:
            f.pack_forget()
        # Limpiar widgets internos para que no se dupliquen al navegar
        for f in [self.frame_clientes, self.frame_servicios,
                    self.frame_reservas, self.frame_reportes, self.frame_log]:
            for widget in f.winfo_children():
                widget.destroy()

    # ==================== GESTIÓN DE CLIENTES ====================

    def mostrar_frame_clientes(self):
        self.limpiar_frames()
        self.frame_clientes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_clientes, text="GESTIÓN DE CLIENTES",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        form_frame = tk.LabelFrame(self.frame_clientes, text="Registrar Nuevo Cliente",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        campos = [
            ("ID Cliente:", "id_cliente"),
            ("Nombre:", "nombre"),
            ("Dirección:", "direccion"),
            ("Correo:", "correo"),
            ("Teléfono:", "telefono"),
        ]
        self.entries_cliente = {}

        for i, (label_text, field_name) in enumerate(campos):
            tk.Label(form_frame, text=label_text, bg="white").grid(
                row=i // 3, column=(i % 3) * 2, sticky="e", padx=5, pady=5)
            entry = tk.Entry(form_frame, width=25)
            entry.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5)
            self.entries_cliente[field_name] = entry

        tk.Button(form_frame, text="💾 Registrar Cliente", command=self.registrar_cliente,
                    bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=20
                    ).grid(row=2, column=0, columnspan=6, pady=15)

        list_frame = tk.LabelFrame(self.frame_clientes, text="Clientes Registrados",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "ID Cliente", "Nombre", "Dirección", "Correo", "Teléfono")
        self.tree_clientes = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=150)

        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=sb.set)
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.frame_clientes, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="🔄 Actualizar Lista", command=self.actualizar_lista_clientes,
                    bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_cliente,
                    bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)

        self.actualizar_lista_clientes()

    def registrar_cliente(self):
        try:
            id_cliente = self.entries_cliente["id_cliente"].get().strip()
            nombre     = self.entries_cliente["nombre"].get().strip()
            direccion  = self.entries_cliente["direccion"].get().strip()
            correo     = self.entries_cliente["correo"].get().strip()
            telefono   = self.entries_cliente["telefono"].get().strip()

            if not all([id_cliente, nombre, direccion, correo, telefono]):
                messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios.")
                return

            nuevo_cliente = Cliente(str(uuid.uuid4()), id_cliente, nombre, direccion, correo, telefono)
            self.clientes.append(nuevo_cliente)
            registrar_evento(f"GUI: Cliente registrado: {nuevo_cliente}")
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado correctamente.")
            for entry in self.entries_cliente.values():
                entry.delete(0, tk.END)
            self.actualizar_lista_clientes()

        except ErrorDatosCliente as e:
            registrar_excepcion(e, "GUI Registro Cliente")
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            registrar_excepcion(e, "GUI Registro Cliente (inesperado)")
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def actualizar_lista_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.clientes:
            self.tree_clientes.insert("", tk.END, values=(
                c.id_objeto[:8] + "...", c.id_cliente,
                c.nombre, c.direccion, c.correo, c.telefono
            ))

    def eliminar_cliente(self):
        seleccion = self.tree_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            id_cliente = self.tree_clientes.item(seleccion[0])['values'][1]
            self.clientes = [c for c in self.clientes if c.id_cliente != id_cliente]
            registrar_evento(f"GUI: Cliente {id_cliente} eliminado.")
            self.actualizar_lista_clientes()
            messagebox.showinfo("Éxito", "Cliente eliminado.")

    # ==================== GESTIÓN DE SERVICIOS ====================

    def mostrar_frame_servicios(self):
        self.limpiar_frames()
        self.frame_servicios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_servicios, text="GESTIÓN DE SERVICIOS",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        notebook = ttk.Notebook(self.frame_servicios)
        notebook.pack(fill=tk.X, padx=10, pady=5)

        self.frame_sala     = tk.Frame(notebook, bg="white")
        self.frame_equipo   = tk.Frame(notebook, bg="white")
        self.frame_asesoria = tk.Frame(notebook, bg="white")
        notebook.add(self.frame_sala,     text="🏛️ Reserva de Sala")
        notebook.add(self.frame_equipo,   text="🔧 Alquiler de Equipo")
        notebook.add(self.frame_asesoria, text="💼 Asesoría Especializada")

        self._form_sala()
        self._form_equipo()
        self._form_asesoria()

        list_frame = tk.LabelFrame(self.frame_servicios, text="Servicios Registrados",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Tipo", "Nombre", "Precio Base", "Detalles")
        self.tree_servicios = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree_servicios.heading(col, text=col)
            self.tree_servicios.column(col, width=200)
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscroll=sb.set)
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.actualizar_lista_servicios()

    def _form_sala(self):
        self.entries_sala = {}
        for i, (lbl, key) in enumerate([("Nombre:", "nombre"), ("Precio Base:", "precio"),
                                            ("Capacidad:", "capacidad"), ("Horas:", "horas")]):
            tk.Label(self.frame_sala, text=lbl, bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=8)
            e = tk.Entry(self.frame_sala, width=30)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.entries_sala[key] = e
        tk.Button(self.frame_sala, text="Crear Sala", command=self.crear_sala,
                    bg="#27ae60", fg="white", font=("Arial", 10, "bold")
                    ).grid(row=4, column=0, columnspan=2, pady=15)

    def _form_equipo(self):
        self.entries_equipo = {}
        for i, (lbl, key) in enumerate([("Nombre:", "nombre"), ("Precio Base:", "precio"),
                                            ("Días:", "dias")]):
            tk.Label(self.frame_equipo, text=lbl, bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=8)
            e = tk.Entry(self.frame_equipo, width=30)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.entries_equipo[key] = e
        self.chk_seguro = tk.BooleanVar()
        tk.Checkbutton(self.frame_equipo, text="Incluir Seguro ($50,000)",
                        variable=self.chk_seguro, bg="white"
                        ).grid(row=3, column=0, columnspan=2, pady=8)
        tk.Button(self.frame_equipo, text="Crear Equipo", command=self.crear_equipo,
                    bg="#27ae60", fg="white", font=("Arial", 10, "bold")
                    ).grid(row=4, column=0, columnspan=2, pady=15)

    def _form_asesoria(self):
        self.entries_asesoria = {}
        for i, (lbl, key) in enumerate([("Nombre:", "nombre"), ("Precio Base:", "precio"),
                                            ("Consultor:", "consultor")]):
            tk.Label(self.frame_asesoria, text=lbl, bg="white").grid(row=i, column=0, sticky="e", padx=10, pady=8)
            e = tk.Entry(self.frame_asesoria, width=30)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.entries_asesoria[key] = e
        tk.Label(self.frame_asesoria, text="Nivel:", bg="white").grid(row=3, column=0, sticky="e", padx=10, pady=8)
        self.combo_nivel = ttk.Combobox(self.frame_asesoria,
                                        values=["Basico", "Intermedio", "Avanzado"],
                                        state="readonly", width=27)
        self.combo_nivel.grid(row=3, column=1, padx=10, pady=8)
        self.combo_nivel.current(0)
        tk.Button(self.frame_asesoria, text="Crear Asesoría", command=self.crear_asesoria,
                    bg="#27ae60", fg="white", font=("Arial", 10, "bold")
                    ).grid(row=4, column=0, columnspan=2, pady=15)

    def crear_sala(self):
        try:
            nombre    = self.entries_sala["nombre"].get()
            precio    = float(self.entries_sala["precio"].get())
            capacidad = int(self.entries_sala["capacidad"].get())
            horas     = float(self.entries_sala["horas"].get())
            svc = ReservaSala(str(uuid.uuid4()), nombre, precio, capacidad, horas)
            self.servicios.append(svc)
            registrar_evento(f"GUI: Sala creada: {svc.mostrar_info()}")
            messagebox.showinfo("Éxito", "Sala creada correctamente.")
            self.actualizar_lista_servicios()
        except (ValueError, ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "GUI Crear Sala")
            messagebox.showerror("Error", str(e))

    def crear_equipo(self):
        try:
            nombre = self.entries_equipo["nombre"].get()
            precio = float(self.entries_equipo["precio"].get())
            dias   = int(self.entries_equipo["dias"].get())
            seguro = self.chk_seguro.get()
            svc = AlquilerEquipo(str(uuid.uuid4()), nombre, precio, dias, seguro)
            self.servicios.append(svc)
            registrar_evento(f"GUI: Equipo creado: {svc.mostrar_info()}")
            messagebox.showinfo("Éxito", "Equipo creado correctamente.")
            self.actualizar_lista_servicios()
        except (ValueError, ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "GUI Crear Equipo")
            messagebox.showerror("Error", str(e))

    def crear_asesoria(self):
        try:
            nombre    = self.entries_asesoria["nombre"].get()
            precio    = float(self.entries_asesoria["precio"].get())
            consultor = self.entries_asesoria["consultor"].get()
            nivel     = self.combo_nivel.get()
            svc = AsesoriaEspecializada(str(uuid.uuid4()), nombre, precio, consultor, nivel)
            self.servicios.append(svc)
            registrar_evento(f"GUI: Asesoría creada: {svc.mostrar_info()}")
            messagebox.showinfo("Éxito", "Asesoría creada correctamente.")
            self.actualizar_lista_servicios()
        except (ValueError, ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "GUI Crear Asesoría")
            messagebox.showerror("Error", str(e))

    def actualizar_lista_servicios(self):
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        for svc in self.servicios:
            tipo = _tipo_servicio(svc)
            self.tree_servicios.insert("", tk.END, values=(
                svc.id_objeto[:8] + "...", tipo, svc.nombre,
                f"${svc.precio_base:,.0f}", svc.obtener_detalles()
            ))

    # ==================== GESTIÓN DE RESERVAS ====================

    def mostrar_frame_reservas(self):
        self.limpiar_frames()
        self.frame_reservas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_reservas, text="GESTIÓN DE RESERVAS",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        form_frame = tk.LabelFrame(self.frame_reservas, text="Nueva Reserva",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Fila 0: Cliente y Servicio
        tk.Label(form_frame, text="Cliente:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_clientes = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_clientes.grid(row=0, column=1, padx=5, pady=5)
        self._actualizar_combo_clientes()

        tk.Label(form_frame, text="Servicio:", bg="white").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.combo_servicios = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_servicios.grid(row=0, column=3, padx=5, pady=5)
        self._actualizar_combo_servicios()

        # Fila 1: Fecha y Hora
        tk.Label(form_frame, text="Fecha (YYYY-MM-DD):", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_fecha = tk.Entry(form_frame, width=15)
        self.entry_fecha.grid(row=1, column=1, padx=5, pady=5)
        self.entry_fecha.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Hora (HH:MM):", bg="white").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_hora = tk.Entry(form_frame, width=15)
        self.entry_hora.grid(row=1, column=3, padx=5, pady=5)
        self.entry_hora.insert(0, "09:00")

        # Fila 2: Duración y Notas
        tk.Label(form_frame, text="Duración (horas):", bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_duracion = tk.Entry(form_frame, width=15)
        self.entry_duracion.grid(row=2, column=1, padx=5, pady=5)
        self.entry_duracion.insert(0, "2.0")

        tk.Label(form_frame, text="Notas:", bg="white").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_notas = tk.Entry(form_frame, width=30)
        self.entry_notas.grid(row=2, column=3, padx=5, pady=5)

        # Fila 3: Botones  ← INDENTACIÓN CORREGIDA
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)

        tk.Button(btn_frame, text="📅 Crear Reserva", command=self.crear_reserva,
                    bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15
                    ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✅ Confirmar", command=self.confirmar_reserva,
                    bg="#3498db", fg="white", font=("Arial", 10, "bold"), padx=15
                    ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Cancelar", command=self.cancelar_reserva,
                    bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), padx=15
                    ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="💰 Procesar", command=self.procesar_reserva,
                    bg="#f39c12", fg="white", font=("Arial", 10, "bold"), padx=15
                    ).pack(side=tk.LEFT, padx=5)

        # Treeview  ← INDENTACIÓN CORREGIDA
        list_frame = tk.LabelFrame(self.frame_reservas, text="Reservas Registradas",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Cliente", "Servicio", "Fecha/Hora", "Duración", "Estado", "Costo")
        self.tree_reservas = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree_reservas.heading(col, text=col)
            self.tree_reservas.column(col, width=120)
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscroll=sb.set)
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.actualizar_lista_reservas()

    def _actualizar_combo_clientes(self):
        self.combo_clientes['values'] = [f"{c.id_cliente} - {c.nombre}" for c in self.clientes]

    def _actualizar_combo_servicios(self):
        self.combo_servicios['values'] = [f"{s.nombre} (${s.precio_base:,.0f})" for s in self.servicios]

    def crear_reserva(self):
        try:
            if not self.clientes or not self.servicios:
                messagebox.showwarning("Atención", "Debe haber clientes y servicios registrados.")
                return
            idx_c = self.combo_clientes.current()
            idx_s = self.combo_servicios.current()
            if idx_c == -1 or idx_s == -1:
                messagebox.showwarning("Atención", "Seleccione cliente y servicio.")
                return

            cliente  = self.clientes[idx_c]
            servicio = self.servicios[idx_s]
            fecha_str = self.entry_fecha.get()
            hora_str  = self.entry_hora.get()
            duracion  = float(self.entry_duracion.get())
            notas     = self.entry_notas.get()
            id_res    = len(self.reservas) + 1

            reserva = Reserva.crear_reserva(
                id_res, cliente, servicio, fecha_str, hora_str, duracion, notas
            )
            self.reservas.append(reserva)
            registrar_evento(f"GUI: Reserva creada: {reserva}")
            messagebox.showinfo("Éxito", "Reserva creada correctamente.")
            self.actualizar_lista_reservas()

        except ErrorReserva as e:
            registrar_excepcion(e, "GUI Crear Reserva")
            messagebox.showerror("Error de Reserva", str(e))
        except ValueError:
            messagebox.showerror("Error", "Verifique el formato de fecha/hora o duración.")
        except Exception as e:
            registrar_excepcion(e, "GUI Crear Reserva (inesperado)")
            messagebox.showerror("Error", str(e))

    def _get_reserva_seleccionada(self) -> 'Reserva | None':
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return None
        id_reserva = int(self.tree_reservas.item(seleccion[0])['values'][0])
        return next((r for r in self.reservas if r.id == id_reserva), None)

    def confirmar_reserva(self):
        reserva = self._get_reserva_seleccionada()
        if not reserva:
            return
        try:
            reserva.confirmar()
            registrar_evento(f"GUI: Reserva #{reserva.id} confirmada.")
            messagebox.showinfo("Éxito", "Reserva confirmada.")
            self.actualizar_lista_reservas()
        except ErrorReserva as e:
            registrar_excepcion(e, "GUI Confirmar Reserva")
            messagebox.showerror("Error", str(e))

    def cancelar_reserva(self):
        reserva = self._get_reserva_seleccionada()
        if not reserva:
            return
        if messagebox.askyesno("Confirmar", "¿Cancelar esta reserva?"):
            try:
                reserva.cancelar()
                registrar_evento(f"GUI: Reserva #{reserva.id} cancelada.")
                messagebox.showinfo("Éxito", "Reserva cancelada.")
                self.actualizar_lista_reservas()
            except ErrorReserva as e:
                registrar_excepcion(e, "GUI Cancelar Reserva")
                messagebox.showerror("Error", str(e))

    def procesar_reserva(self):
        reserva = self._get_reserva_seleccionada()
        if not reserva:
            return
        try:
            costo = reserva.procesar()
            registrar_evento(f"GUI: Reserva #{reserva.id} procesada. Costo: ${costo:,.0f}")
            messagebox.showinfo("Procesado", f"Reserva procesada.\nCosto total: ${costo:,.0f}")
            self.actualizar_lista_reservas()
        except ErrorReserva as e:
            registrar_excepcion(e, "GUI Procesar Reserva")
            messagebox.showerror("Error", str(e))

    def actualizar_lista_reservas(self):
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for reserva in self.reservas:
            try:
                costo_str = f"${reserva.servicio.calcular_costo():,.0f}"
            except Exception:
                costo_str = "N/A"
            self.tree_reservas.insert("", tk.END, values=(
                reserva.id, reserva.cliente.nombre, reserva.servicio.nombre,
                reserva.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                f"{reserva.duracion}h", reserva.estado.capitalize(), costo_str
            ))

    # ==================== REPORTES ====================

    def mostrar_frame_reportes(self):
        self.limpiar_frames()
        self.frame_reportes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_reportes, text="REPORTES Y ESTADÍSTICAS",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        stats_frame = tk.LabelFrame(self.frame_reportes, text="Resumen",
                                    font=("Arial", 10, "bold"), bg="white", padx=20, pady=20)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        reservas_confirmadas = [r for r in self.reservas if r.estado == "confirmada"]
        reservas_completadas = [r for r in self.reservas if r.estado == "completada"]
        ingresos = sum(r.servicio.calcular_costo() for r in reservas_completadas
                        if self._safe_costo(r) is not None)

        stats = [
            ("Total Clientes:",        len(self.clientes)),
            ("Total Servicios:",       len(self.servicios)),
            ("Total Reservas:",        len(self.reservas)),
            ("Confirmadas:",           len(reservas_confirmadas)),
            ("Completadas:",           len(reservas_completadas)),
            ("Ingresos Totales:",      f"${ingresos:,.0f}"),
        ]
        for i, (lbl, val) in enumerate(stats):
            tk.Label(stats_frame, text=lbl, font=("Arial", 10, "bold"), bg="white"
                     ).grid(row=i // 3, column=(i % 3) * 2, sticky="e", padx=20, pady=10)
            tk.Label(stats_frame, text=str(val), font=("Arial", 10), bg="#ecf0f1",
                     padx=20, pady=10).grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w")

        tk.Button(self.frame_reportes, text="🔄 Actualizar Reportes",
                    command=self.mostrar_frame_reportes,
                    bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                    padx=20, pady=10).pack(pady=20)

    def _safe_costo(self, reserva):
        try:
            return reserva.servicio.calcular_costo()
        except Exception:
            return None

    # ==================== LOG ====================

    def mostrar_frame_log(self):
        self.limpiar_frames()
        self.frame_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_log, text="REGISTRO DE EVENTOS (LOG)",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        text_frame = tk.Frame(self.frame_log, bg="#ecf0f1")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_log = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 9),
                                bg="#1e1e1e", fg="#d4d4d4", height=30)
        sb = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=sb.set)
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(self.frame_log, text="🔄 Actualizar Log",
                    command=self._cargar_log,
                    bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                    padx=20).pack(pady=10)

        self._cargar_log()

    def _cargar_log(self):
        self.text_log.config(state=tk.NORMAL)
        self.text_log.delete("1.0", tk.END)
        for linea in leer_log(50):
            self.text_log.insert(tk.END, linea)
        self.text_log.config(state=tk.DISABLED)
        self.text_log.see(tk.END)


# ==================== FUNCIÓN AUXILIAR ====================

def _tipo_servicio(servicio) -> str:
    if isinstance(servicio, ReservaSala):
        return "Sala"
    elif isinstance(servicio, AlquilerEquipo):
        return "Equipo"
    elif isinstance(servicio, AsesoriaEspecializada):
        return "Asesoría"
    return "Desconocido"


def main():
    root = tk.Tk()
    app = AplicacionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()