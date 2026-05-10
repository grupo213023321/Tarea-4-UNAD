##########################################################
#
# --- Archivo gui.py ---
#
# - Interfaz Gráfica con Tkinter
# - Gestión de Clientes, Servicios y Reservas
#
##########################################################

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional

from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)


class AplicacionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión FJ - Reservas")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Datos
        self.clientes = []
        self.servicios = []
        self.reservas = []
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=5)
        
        # Crear interfaz
        self.crear_menu_superior()
        self.crear_frames_principales()
        self.mostrar_frame_clientes()
        
    def crear_menu_superior(self):
        """Barra de menú superior"""
        menu_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        menu_frame.pack(fill=tk.X, padx=0, pady=0)
        menu_frame.pack_propagate(False)
        
        # Título
        titulo = tk.Label(menu_frame, text="🏢 SISTEMA DE GESTIÓN DE RESERVAS", 
                         bg="#2c3e50", fg="white", font=("Arial", 16, "bold"))
        titulo.pack(pady=10)
        
        # Botones de navegación
        nav_frame = tk.Frame(self.root, bg="#34495e", height=40)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)
        
        btn_clientes = tk.Button(nav_frame, text="👥 Clientes", command=self.mostrar_frame_clientes,
                                bg="#34495e", fg="white", relief=tk.FLAT, cursor="hand2",
                                font=("Arial", 10, "bold"))
        btn_clientes.pack(side=tk.LEFT, padx=20, pady=5)
        
        btn_servicios = tk.Button(nav_frame, text="🎯 Servicios", command=self.mostrar_frame_servicios,
                                 bg="#34495e", fg="white", relief=tk.FLAT, cursor="hand2",
                                 font=("Arial", 10, "bold"))
        btn_servicios.pack(side=tk.LEFT, padx=20, pady=5)
        
        btn_reservas = tk.Button(nav_frame, text="📅 Reservas", command=self.mostrar_frame_reservas,
                                bg="#34495e", fg="white", relief=tk.FLAT, cursor="hand2",
                                font=("Arial", 10, "bold"))
        btn_reservas.pack(side=tk.LEFT, padx=20, pady=5)
        
        btn_reportes = tk.Button(nav_frame, text="📊 Reportes", command=self.mostrar_frame_reportes,
                                bg="#34495e", fg="white", relief=tk.FLAT, cursor="hand2",
                                font=("Arial", 10, "bold"))
        btn_reportes.pack(side=tk.LEFT, padx=20, pady=5)
        
    def crear_frames_principales(self):
        """Crear los contenedores para cada sección"""
        # Frame Clientes
        self.frame_clientes = tk.Frame(self.root, bg="#ecf0f1")
        
        # Frame Servicios
        self.frame_servicios = tk.Frame(self.root, bg="#ecf0f1")
        
        # Frame Reservas
        self.frame_reservas = tk.Frame(self.root, bg="#ecf0f1")
        
        # Frame Reportes
        self.frame_reportes = tk.Frame(self.root, bg="#ecf0f1")
        
    def limpiar_frames(self):
        """Ocultar todos los frames"""
        self.frame_clientes.pack_forget()
        self.frame_servicios.pack_forget()
        self.frame_reservas.pack_forget()
        self.frame_reportes.pack_forget()
        
    # ==================== GESTIÓN DE CLIENTES ====================
    
    def mostrar_frame_clientes(self):
        """Mostrar sección de clientes"""
        self.limpiar_frames()
        self.frame_clientes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(self.frame_clientes, text="GESTIÓN DE CLIENTES", 
                font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        
        # Frame formulario
        form_frame = tk.LabelFrame(self.frame_clientes, text="Registrar Nuevo Cliente", 
                                  font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Campos del formulario
        campos = [
            ("ID Cliente:", "id_cliente"),
            ("Nombre:", "nombre"),
            ("Dirección:", "direccion"),
            ("Correo:", "correo"),
            ("Teléfono:", "telefono")
        ]
        
        self.entries_cliente = {}
        
        for i, (label_text, field_name) in enumerate(campos):
            tk.Label(form_frame, text=label_text, bg="white").grid(row=i//3, column=(i%3)*2, 
                                                                   sticky="e", padx=5, pady=5)
            entry = tk.Entry(form_frame, width=25)
            entry.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)
            self.entries_cliente[field_name] = entry
        
        # Botón registrar
        btn_registrar = tk.Button(form_frame, text="💾 Registrar Cliente", 
                                 command=self.registrar_cliente, bg="#27ae60", fg="white",
                                 font=("Arial", 10, "bold"), padx=20)
        btn_registrar.grid(row=2, column=0, columnspan=6, pady=15)
        
        # Treeview para listar clientes
        list_frame = tk.LabelFrame(self.frame_clientes, text="Clientes Registrados", 
                                  font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("ID", "ID Cliente", "Nombre", "Dirección", "Correo", "Teléfono")
        self.tree_clientes = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=scrollbar.set)
        
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción
        btn_frame = tk.Frame(self.frame_clientes, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="🔄 Actualizar Lista", command=self.actualizar_lista_clientes,
                 bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_cliente,
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)
        
    def registrar_cliente(self):
        """Registrar un nuevo cliente"""
        try:
            import uuid
            
            id_cliente = self.entries_cliente["id_cliente"].get().strip()
            nombre = self.entries_cliente["nombre"].get().strip()
            direccion = self.entries_cliente["direccion"].get().strip()
            correo = self.entries_cliente["correo"].get().strip()
            telefono = self.entries_cliente["telefono"].get().strip()
            
            if not all([id_cliente, nombre, direccion, correo, telefono]):
                messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
                return
            
            id_sistema = str(uuid.uuid4())
            
            nuevo_cliente = Cliente(id_sistema, id_cliente, nombre, direccion, correo, telefono)
            self.clientes.append(nuevo_cliente)
            
            messagebox.showinfo("Éxito", f"Cliente {nombre} registrado correctamente")
            
            # Limpiar formulario
            for entry in self.entries_cliente.values():
                entry.delete(0, tk.END)
            
            self.actualizar_lista_clientes()
            
        except ErrorDatosCliente as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            
    def actualizar_lista_clientes(self):
        """Actualizar el treeview de clientes"""
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
            
        for cliente in self.clientes:
            self.tree_clientes.insert("", tk.END, values=(
                cliente.id_objeto[:8] + "...",
                cliente.id_cliente,
                cliente.nombre,
                cliente.direccion,
                cliente.correo,
                cliente.telefono
            ))
            
    def eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        seleccion = self.tree_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente para eliminar")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?"):
            item = self.tree_clientes.item(seleccion[0])
            id_cliente = item['values'][1]
            
            self.clientes = [c for c in self.clientes if c.id_cliente != id_cliente]
            self.actualizar_lista_clientes()
            messagebox.showinfo("Éxito", "Cliente eliminado")
    
    # ==================== GESTIÓN DE SERVICIOS ====================
    
    def mostrar_frame_servicios(self):
        """Mostrar sección de servicios"""
        self.limpiar_frames()
        self.frame_servicios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(self.frame_servicios, text="GESTIÓN DE SERVICIOS", 
                font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        
        # Notebook para tipos de servicio
        notebook = ttk.Notebook(self.frame_servicios)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame Reserva de Sala
        self.frame_sala = tk.Frame(notebook, bg="white")
        notebook.add(self.frame_sala, text="🏛️ Reserva de Sala")
        self.crear_formulario_sala()
        
        # Frame Alquiler de Equipo
        self.frame_equipo = tk.Frame(notebook, bg="white")
        notebook.add(self.frame_equipo, text="🔧 Alquiler de Equipo")
        self.crear_formulario_equipo()
        
        # Frame Asesoría
        self.frame_asesoria = tk.Frame(notebook, bg="white")
        notebook.add(self.frame_asesoria, text="💼 Asesoría Especializada")
        self.crear_formulario_asesoria()
        
        # Lista de servicios
        list_frame = tk.LabelFrame(self.frame_servicios, text="Servicios Registrados", 
                                  font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("ID", "Tipo", "Nombre", "Precio Base", "Detalles")
        self.tree_servicios = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree_servicios.heading(col, text=col)
            self.tree_servicios.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscroll=scrollbar.set)
        
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def crear_formulario_sala(self):
        """Formulario para reserva de sala"""
        campos = [
            ("Nombre:", "nombre"),
            ("Precio Base:", "precio"),
            ("Capacidad:", "capacidad"),
            ("Horas:", "horas")
        ]
        
        self.entries_sala = {}
        
        for i, (label_text, field_name) in enumerate(campos):
            tk.Label(self.frame_sala, text=label_text, bg="white").grid(row=i, column=0, 
                                                                        sticky="e", padx=10, pady=10)
            entry = tk.Entry(self.frame_sala, width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries_sala[field_name] = entry
            
        btn = tk.Button(self.frame_sala, text="Crear Sala", command=self.crear_sala,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        btn.grid(row=4, column=0, columnspan=2, pady=20)
        
    def crear_formulario_equipo(self):
        """Formulario para alquiler de equipo"""
        campos = [
            ("Nombre:", "nombre"),
            ("Precio Base:", "precio"),
            ("Días:", "dias")
        ]
        
        self.entries_equipo = {}
        
        for i, (label_text, field_name) in enumerate(campos):
            tk.Label(self.frame_equipo, text=label_text, bg="white").grid(row=i, column=0, 
                                                                          sticky="e", padx=10, pady=10)
            entry = tk.Entry(self.frame_equipo, width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries_equipo[field_name] = entry
            
        self.chk_seguro = tk.BooleanVar()
        chk = tk.Checkbutton(self.frame_equipo, text="Incluir Seguro ($50,000)", 
                            variable=self.chk_seguro, bg="white")
        chk.grid(row=3, column=0, columnspan=2, pady=10)
        
        btn = tk.Button(self.frame_equipo, text="Crear Equipo", command=self.crear_equipo,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        btn.grid(row=4, column=0, columnspan=2, pady=20)
        
    def crear_formulario_asesoria(self):
        """Formulario para asesoría"""
        campos = [
            ("Nombre:", "nombre"),
            ("Precio Base:", "precio"),
            ("Consultor:", "consultor")
        ]
        
        self.entries_asesoria = {}
        
        for i, (label_text, field_name) in enumerate(campos):
            tk.Label(self.frame_asesoria, text=label_text, bg="white").grid(row=i, column=0, 
                                                                            sticky="e", padx=10, pady=10)
            entry = tk.Entry(self.frame_asesoria, width=30)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries_asesoria[field_name] = entry
            
        tk.Label(self.frame_asesoria, text="Nivel:", bg="white").grid(row=3, column=0, 
                                                                      sticky="e", padx=10, pady=10)
        self.combo_nivel = ttk.Combobox(self.frame_asesoria, values=["Basico", "Intermedio", "Avanzado"], 
                                       state="readonly", width=27)
        self.combo_nivel.grid(row=3, column=1, padx=10, pady=10)
        self.combo_nivel.current(0)
        
        btn = tk.Button(self.frame_asesoria, text="Crear Asesoría", command=self.crear_asesoria,
                       bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        btn.grid(row=4, column=0, columnspan=2, pady=20)
        
    def crear_sala(self):
        """Crear servicio de sala"""
        try:
            nombre = self.entries_sala["nombre"].get()
            precio = float(self.entries_sala["precio"].get())
            capacidad = int(self.entries_sala["capacidad"].get())
            horas = float(self.entries_sala["horas"].get())
            
            import uuid
            servicio = ReservaSala(str(uuid.uuid4()), nombre, precio, capacidad, horas)
            self.servicios.append(servicio)
            
            messagebox.showinfo("Éxito", "Sala creada correctamente")
            self.actualizar_lista_servicios()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique los valores numéricos")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def crear_equipo(self):
        """Crear servicio de equipo"""
        try:
            nombre = self.entries_equipo["nombre"].get()
            precio = float(self.entries_equipo["precio"].get())
            dias = int(self.entries_equipo["dias"].get())
            seguro = self.chk_seguro.get()
            
            import uuid
            servicio = AlquilerEquipo(str(uuid.uuid4()), nombre, precio, dias, seguro)
            self.servicios.append(servicio)
            
            messagebox.showinfo("Éxito", "Equipo creado correctamente")
            self.actualizar_lista_servicios()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique los valores numéricos")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def crear_asesoria(self):
        """Crear servicio de asesoría"""
        try:
            nombre = self.entries_asesoria["nombre"].get()
            precio = float(self.entries_asesoria["precio"].get())
            consultor = self.entries_asesoria["consultor"].get()
            nivel = self.combo_nivel.get()
            
            import uuid
            servicio = AsesoriaEspecializada(str(uuid.uuid4()), nombre, precio, consultor, nivel)
            self.servicios.append(servicio)
            
            messagebox.showinfo("Éxito", "Asesoría creada correctamente")
            self.actualizar_lista_servicios()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique los valores numéricos")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def actualizar_lista_servicios(self):
        """Actualizar treeview de servicios"""
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
            
        for servicio in self.servicios:
            tipo = tipo_servicio(servicio)
            detalles = servicio.obtener_detalles()
            precio = f"${servicio.precio_base:,.0f}"
            
            self.tree_servicios.insert("", tk.END, values=(
                servicio.id_objeto[:8] + "...",
                tipo,
                servicio.nombre,
                precio,
                detalles
            ))
    
    # ==================== GESTIÓN DE RESERVAS ====================
    
    def mostrar_frame_reservas(self):
        """Mostrar sección de reservas"""
        self.limpiar_frames()
        self.frame_reservas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(self.frame_reservas, text="GESTIÓN DE RESERVAS", 
                font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        
        # Frame superior: Formulario
        form_frame = tk.LabelFrame(self.frame_reservas, text="Nueva Reserva", 
                                  font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cliente
        tk.Label(form_frame, text="Cliente:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_clientes = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_clientes.grid(row=0, column=1, padx=5, pady=5)
        self.actualizar_combo_clientes()
        
        # Servicio
        tk.Label(form_frame, text="Servicio:", bg="white").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.combo_servicios = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_servicios.grid(row=0, column=3, padx=5, pady=5)
        self.actualizar_combo_servicios()
        
        # Fecha y Hora
        tk.Label(form_frame, text="Fecha (YYYY-MM-DD):", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_fecha = tk.Entry(form_frame, width=15)
        self.entry_fecha.grid(row=1, column=1, padx=5, pady=5)
        self.entry_fecha.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        
        tk.Label(form_frame, text="Hora (HH:MM):", bg="white").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_hora = tk.Entry(form_frame, width=15)
        self.entry_hora.grid(row=1, column=3, padx=5, pady=5)
        self.entry_hora.insert(0, "09:00")
        
        # Duración
        tk.Label(form_frame, text="Duración (horas):", bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_duracion = tk.Entry(form_frame, width=15)
        self.entry_duracion.grid(row=2, column=1, padx=5, pady=5)
        self.entry_duracion.insert(0, "2.0")
        
        # Notas
        tk.Label(form_frame, text="Notas:", bg="white").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_notas = tk.Entry(form_frame, width=30)
        self.entry_notas.grid(row=2, column=3, padx=5, pady=5)
        
        # Botones
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        tk.Button(btn_frame, text="📅 Crear Reserva", command=self.crear_reserva,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✅ Confirmar", command=self.confirmar_reserva,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Cancelar", command=self.cancelar_reserva,
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="💰 Procesar", command=self.procesar_reserva,
                 bg="#f39c12", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)
        
        # Treeview de reservas
        list_frame = tk.LabelFrame(self.frame_reservas, text="Reservas Registradas", 
                                  font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("ID", "Cliente", "Servicio", "Fecha/Hora", "Duración", "Estado", "Costo")
        self.tree_reservas = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.tree_reservas.heading(col, text=col)
            self.tree_reservas.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscroll=scrollbar.set)
        
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.actualizar_lista_reservas()
        
    def actualizar_combo_clientes(self):
        """Actualizar combo de clientes"""
        clientes_str = [f"{c.id_cliente} - {c.nombre}" for c in self.clientes]
        self.combo_clientes['values'] = clientes_str
        
    def actualizar_combo_servicios(self):
        """Actualizar combo de servicios"""
        servicios_str = [f"{s.nombre} (${s.precio_base:,.0f})" for s in self.servicios]
        self.combo_servicios['values'] = servicios_str
        
    def crear_reserva(self):
        """Crear nueva reserva"""
        try:
            if not self.clientes or not self.servicios:
                messagebox.showwarning("Atención", "Debe haber clientes y servicios registrados")
                return
                
            idx_cliente = self.combo_clientes.current()
            idx_servicio = self.combo_servicios.current()
            
            if idx_cliente == -1 or idx_servicio == -1:
                messagebox.showwarning("Atención", "Seleccione cliente y servicio")
                return
                
            cliente = self.clientes[idx_cliente]
            servicio = self.servicios[idx_servicio]
            
            fecha_str = self.entry_fecha.get()
            hora_str = self.entry_hora.get()
            duracion = float(self.entry_duracion.get())
            notas = self.entry_notas.get()
            
            import uuid
            id_reserva = len(self.reservas) + 1
            
            from datetime import datetime
            fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            
            reserva = Reserva(id_reserva, cliente, servicio, fecha_hora, duracion, notas)
            self.reservas.append(reserva)
            
            messagebox.showinfo("Éxito", "Reserva creada correctamente")
            self.actualizar_lista_reservas()
            
        except ValueError:
            messagebox.showerror("Error", "Verifique el formato de fecha/hora o duración")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def confirmar_reserva(self):
        """Confirmar reserva seleccionada"""
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una reserva")
            return
            
        try:
            item = self.tree_reservas.item(seleccion[0])
            id_reserva = int(item['values'][0])
            
            reserva = next((r for r in self.reservas if r.id == id_reserva), None)
            if reserva:
                reserva.confirmar()
                messagebox.showinfo("Éxito", "Reserva confirmada")
                self.actualizar_lista_reservas()
            else:
                messagebox.showerror("Error", "Reserva no encontrada")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def cancelar_reserva(self):
        """Cancelar reserva seleccionada"""
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una reserva")
            return
            
        if messagebox.askyesno("Confirmar", "¿Cancelar esta reserva?"):
            try:
                item = self.tree_reservas.item(seleccion[0])
                id_reserva = int(item['values'][0])
                
                reserva = next((r for r in self.reservas if r.id == id_reserva), None)
                if reserva:
                    reserva.cancelar()
                    messagebox.showinfo("Éxito", "Reserva cancelada")
                    self.actualizar_lista_reservas()
                    
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def procesar_reserva(self):
        """Procesar reserva seleccionada"""
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una reserva")
            return
            
        try:
            item = self.tree_reservas.item(seleccion[0])
            id_reserva = int(item['values'][0])
            
            reserva = next((r for r in self.reservas if r.id == id_reserva), None)
            if reserva:
                costo = reserva.procesar()
                messagebox.showinfo("Procesado", f"Reserva procesada\nCosto total: ${costo:,.0f}")
                self.actualizar_lista_reservas()
            else:
                messagebox.showerror("Error", "Reserva no encontrada")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def actualizar_lista_reservas(self):
        """Actualizar treeview de reservas"""
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
            
        for reserva in self.reservas:
            try:
                costo = reserva.servicio.calcular_costo()
                costo_str = f"${costo:,.0f}"
            except:
                costo_str = "N/A"
                
            self.tree_reservas.insert("", tk.END, values=(
                reserva.id,
                reserva.cliente.nombre,
                reserva.servicio.nombre,
                reserva.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                f"{reserva.duracion}h",
                reserva.estado.capitalize(),
                costo_str
            ))
    
    # ==================== REPORTES ====================
    
    def mostrar_frame_reportes(self):
        """Mostrar sección de reportes"""
        self.limpiar_frames()
        self.frame_reportes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(self.frame_reportes, text="REPORTES Y ESTADÍSTICAS", 
                font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        
        # Frame de estadísticas
        stats_frame = tk.LabelFrame(self.frame_reportes, text="Resumen", 
                                   font=("Arial", 10, "bold"), bg="white", padx=20, pady=20)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Calcular estadísticas
        total_clientes = len(self.clientes)
        total_servicios = len(self.servicios)
        total_reservas = len(self.reservas)
        reservas_confirmadas = len([r for r in self.reservas if r.estado == "confirmada"])
        reservas_completadas = len([r for r in self.reservas if r.estado == "completada"])
        
        ingresos = 0
        for r in self.reservas:
            if r.estado == "completada":
                try:
                    ingresos += r.servicio.calcular_costo()
                except:
                    pass
        
        # Mostrar estadísticas
        stats = [
            ("Total Clientes:", total_clientes),
            ("Total Servicios:", total_servicios),
            ("Total Reservas:", total_reservas),
            ("Reservas Confirmadas:", reservas_confirmadas),
            ("Reservas Completadas:", reservas_completadas),
            ("Ingresos Totales:", f"${ingresos:,.0f}")
        ]
        
        for i, (label, valor) in enumerate(stats):
            tk.Label(stats_frame, text=label, font=("Arial", 10, "bold"), bg="white").grid(
                row=i//3, column=(i%3)*2, sticky="e", padx=20, pady=10)
            tk.Label(stats_frame, text=str(valor), font=("Arial", 10), bg="#ecf0f1", 
                    padx=20, pady=10).grid(row=i//3, column=(i%3)*2+1, sticky="w")
        
        # Botón actualizar
        tk.Button(self.frame_reportes, text="🔄 Actualizar Reportes", 
                 command=self.mostrar_frame_reportes, bg="#3498db", fg="white",
                 font=("Arial", 10, "bold"), padx=20, pady=10).pack(pady=20)


def tipo_servicio(servicio):
    """Determinar el tipo de servicio"""
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