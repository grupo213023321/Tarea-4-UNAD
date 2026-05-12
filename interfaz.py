##########################################################
#
# --- Archivo interfaz.py ---
#
# - Última actualización: 12 - 5 - 2026
#
# Descripción: Interfaz gráfica con Tkinter para el sistema
#              Software FJ. Permite gestionar Clientes,
#              Servicios y Reservas a través de una ventana
#              con navegación por secciones. Se conecta a
#              log.py para registrar todos los eventos.
#
##########################################################

import tkinter as tk               # Módulo principal de la GUI de Python
from tkinter import ttk, messagebox  # ttk: widgets mejorados; messagebox: ventanas de diálogo
from datetime import datetime, timedelta  # Para manejo de fechas en el formulario de reservas
import uuid                         # Para generar IDs únicos para clientes y servicios

# Importa todas las clases del dominio del sistema
from classes import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    Reserva, ErrorDatosCliente, ErrorDisponibilidadServicio,
    ErrorCalculoFinanciero, ErrorReserva
)

# Importa funciones del módulo de log para registrar eventos y errores
from log import registrar_evento, registrar_excepcion, leer_log


class AplicacionGUI:
    """
    Clase principal de la interfaz gráfica del sistema Software FJ.
    Administra la ventana principal, la navegación entre secciones
    y todas las operaciones CRUD sobre clientes, servicios y reservas.
    Los datos se almacenan en listas en memoria (sin base de datos).
    """

    def __init__(self, root):
        """
        Constructor de la aplicación. Configura la ventana principal,
        inicializa las listas de datos en memoria y construye los
        componentes gráficos iniciales.

        Parámetros:
            root (tk.Tk): instancia de la ventana raíz de Tkinter.
        """
        self.root = root  # Referencia a la ventana principal
        self.root.title("Sistema de Gestión FJ - Reservas")  # Título en la barra

        # Calcula la posición para centrar la ventana en la pantalla
        ancho, alto = 1200, 700
        x = (self.root.winfo_screenwidth()  - ancho) // 2  # Posición horizontal centrada
        y = (self.root.winfo_screenheight() - alto)  // 2  # Posición vertical centrada
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")      # Aplica tamaño y posición
        self.root.configure(bg="#f0f0f0")                   # Color de fondo de la ventana

        # Aplica el icono después de 100ms para que Windows lo cargue correctamente
        self.root.after(100, self._aplicar_icono)

        # ── Datos en memoria (sin base de datos) ──────────
        self.clientes  = []  # Lista de objetos Cliente creados en la sesión
        self.servicios = []  # Lista de objetos Servicio creados en la sesión
        self.reservas  = []  # Lista de objetos Reserva creados en la sesión

        # ── Configuración de estilo visual ────────────────
        self.style = ttk.Style()
        self.style.theme_use('clam')                        # Tema visual moderno
        self.style.configure("Treeview", rowheight=25)      # Altura de filas en tablas
        self.style.configure("TButton", padding=5)          # Relleno interno de botones
        self.style.configure("TLabel", padding=5)           # Relleno interno de etiquetas

        # ── Construcción de la interfaz ────────────────────
        self.crear_menu_superior()       # Barra de título y botones de navegación
        self.crear_frames_principales()  # Crea los 5 paneles de contenido
        self.mostrar_frame_clientes()    # Muestra el panel de Clientes por defecto

    def _aplicar_icono(self):
        """
        Aplica el icono personalizado a la ventana y a la barra de tareas de Windows.
        El método se llama con after(100ms) para garantizar que la ventana esté lista.
        Los bloques try/except evitan que la app falle si el icono no está disponible.
        """
        try:
            # Aplica el icono en la barra de título de la ventana
            self.root.iconbitmap("iconosistema.ico")
        except Exception:
            pass  # Si el archivo no existe, continúa sin icono

        try:
            # Fuerza la actualización del icono en la barra de tareas de Windows
            import ctypes
            import os
            ruta_ico = os.path.abspath("iconosistema.ico")  # Ruta absoluta del icono

            # Establece un identificador único para la app en Windows
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "SoftwareFJ.Sistema.1.0"
            )

            # Envía un mensaje de Windows para actualizar el icono en la barra de tareas
            ctypes.windll.user32.SendMessageW(
                ctypes.windll.user32.GetActiveWindow(), 0x0080, 0,
                ctypes.windll.user32.LoadImageW(
                    None, ruta_ico, 1, 0, 0, 0x0010 | 0x0040
                )
            )
        except Exception:
            pass  # Si no es Windows o ctypes falla, continúa normalmente

    # ==================== MENÚ SUPERIOR ====================

    def crear_menu_superior(self):
        """
        Construye la barra superior de navegación con dos franjas:
        1. Franja oscura con el título del sistema.
        2. Franja media con botones de navegación entre secciones.
        """
        # Franja de título: fondo oscuro (#2c3e50 = azul marino)
        menu_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        menu_frame.pack(fill=tk.X)           # Ocupa todo el ancho
        menu_frame.pack_propagate(False)     # Mantiene la altura fija

        # Etiqueta con el nombre del sistema en letra grande y blanca
        tk.Label(menu_frame,
                    text="🏢 SISTEMA DE GESTIÓN DE RESERVAS — Software FJ",
                    bg="#2c3e50", fg="white",
                    font=("Arial", 16, "bold")).pack(pady=10)

        # Franja de navegación: fondo gris oscuro (#34495e)
        nav_frame = tk.Frame(self.root, bg="#34495e", height=40)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)

        # Lista de pares (texto del botón, función a llamar al hacer clic)
        botones_nav = [
            ("👥 Clientes",  self.mostrar_frame_clientes),
            ("🎯 Servicios", self.mostrar_frame_servicios),
            ("📅 Reservas",  self.mostrar_frame_reservas),
            ("📊 Reportes",  self.mostrar_frame_reportes),
            ("📋 Log",       self.mostrar_frame_log),
        ]

        # Crea un botón de navegación para cada sección
        for texto, comando in botones_nav:
            tk.Button(nav_frame, text=texto, command=comando,
                        bg="#34495e", fg="white", relief=tk.FLAT,
                        cursor="hand2",                    # Cursor de mano al pasar
                        font=("Arial", 10, "bold")
                        ).pack(side=tk.LEFT, padx=15, pady=5)

    # ==================== FRAMES PRINCIPALES ====================

    def crear_frames_principales(self):
        """
        Crea los cinco paneles de contenido del sistema.
        Cada panel corresponde a una sección de la navegación.
        Solo uno estará visible a la vez (el que el usuario seleccione).
        """
        self.frame_clientes  = tk.Frame(self.root, bg="#ecf0f1")  # Panel de Clientes
        self.frame_servicios = tk.Frame(self.root, bg="#ecf0f1")  # Panel de Servicios
        self.frame_reservas  = tk.Frame(self.root, bg="#ecf0f1")  # Panel de Reservas
        self.frame_reportes  = tk.Frame(self.root, bg="#ecf0f1")  # Panel de Reportes
        self.frame_log       = tk.Frame(self.root, bg="#ecf0f1")  # Panel de Log

    def limpiar_frames(self):
        """
        Oculta todos los paneles y destruye sus widgets internos.
        Se llama antes de mostrar un nuevo panel para evitar duplicados
        de widgets cuando el usuario navega entre secciones.
        """
        # Oculta todos los frames del flujo de layout
        for f in [self.frame_clientes, self.frame_servicios,
                    self.frame_reservas, self.frame_reportes, self.frame_log]:
            f.pack_forget()

        # Destruye los widgets internos de cada frame para limpiar el estado
        for f in [self.frame_clientes, self.frame_servicios,
                    self.frame_reservas, self.frame_reportes, self.frame_log]:
            for widget in f.winfo_children():
                widget.destroy()

    # ==================== GESTIÓN DE CLIENTES ====================

    def mostrar_frame_clientes(self):
        """
        Construye y muestra el panel de gestión de clientes.
        Incluye:
        - Formulario de registro con 5 campos de entrada.
        - Tabla (Treeview) con los clientes registrados.
        - Botones para actualizar y eliminar clientes.
        """
        self.limpiar_frames()  # Limpia paneles anteriores
        # Muestra este frame ocupando todo el espacio disponible
        self.frame_clientes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título de la sección
        tk.Label(self.frame_clientes, text="GESTIÓN DE CLIENTES",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Marco del formulario de registro
        form_frame = tk.LabelFrame(self.frame_clientes, text="Registrar Nuevo Cliente",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Definición de los campos del formulario: (etiqueta, nombre interno)
        campos = [
            ("ID Cliente:", "id_cliente"),
            ("Nombre:",     "nombre"),
            ("Dirección:",  "direccion"),
            ("Correo:",     "correo"),
            ("Teléfono:",   "telefono"),
        ]
        self.entries_cliente = {}  # Diccionario para acceder a los campos por nombre

        # Crea dinámicamente etiquetas y campos de entrada en una cuadrícula
        for i, (label_text, field_name) in enumerate(campos):
            # Coloca la etiqueta; i//3 = fila, (i%3)*2 = columna par
            tk.Label(form_frame, text=label_text, bg="white").grid(
                row=i // 3, column=(i % 3) * 2, sticky="e", padx=5, pady=5)
            # Crea el campo de entrada
            entry = tk.Entry(form_frame, width=25)
            entry.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5)
            # Guarda la referencia al campo por nombre para leerlo después
            self.entries_cliente[field_name] = entry

        # Botón que llama al método de registro del cliente
        tk.Button(form_frame, text="💾 Registrar Cliente",
                    command=self.registrar_cliente,
                    bg="#27ae60", fg="white",       # Verde con texto blanco
                    font=("Arial", 10, "bold"),
                    padx=20).grid(row=2, column=0, columnspan=6, pady=15)

        # Marco de la tabla de clientes registrados
        list_frame = tk.LabelFrame(self.frame_clientes, text="Clientes Registrados",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Define las columnas de la tabla
        columns = ("ID", "ID Cliente", "Nombre", "Dirección", "Correo", "Teléfono")
        self.tree_clientes = ttk.Treeview(list_frame, columns=columns,
                                            show="headings", height=10)
        for col in columns:
            self.tree_clientes.heading(col, text=col)  # Encabezado de cada columna
            self.tree_clientes.column(col, width=150)  # Ancho fijo por columna

        # Barra de desplazamiento vertical para la tabla
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                            command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=sb.set)
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame con botones de acción sobre la tabla
        btn_frame = tk.Frame(self.frame_clientes, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Botón para refrescar la tabla con los datos actuales de la lista en memoria
        tk.Button(btn_frame, text="🔄 Actualizar Lista",
                    command=self.actualizar_lista_clientes,
                    bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)

        # Botón para eliminar el cliente seleccionado en la tabla
        tk.Button(btn_frame, text="🗑️ Eliminar Seleccionado",
                    command=self.eliminar_cliente,
                    bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)

        # Carga los clientes actuales en la tabla al abrir el panel
        self.actualizar_lista_clientes()

    def registrar_cliente(self):
        """
        Lee los datos del formulario de clientes y crea un nuevo objeto Cliente.
        Implementa try/except para capturar errores de validación y mostrárselos
        al usuario mediante una ventana de diálogo (messagebox).
        """
        try:
            # Lee y limpia los valores de cada campo del formulario
            id_cliente = self.entries_cliente["id_cliente"].get().strip()
            nombre     = self.entries_cliente["nombre"].get().strip()
            direccion  = self.entries_cliente["direccion"].get().strip()
            correo     = self.entries_cliente["correo"].get().strip()
            telefono   = self.entries_cliente["telefono"].get().strip()

            # Verifica que ningún campo esté vacío antes de intentar crear el cliente
            if not all([id_cliente, nombre, direccion, correo, telefono]):
                messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios.")
                return  # Sale sin crear el cliente

            # Intenta crear el objeto Cliente con todas las validaciones
            # Puede lanzar ErrorDatosCliente si correo, teléfono o nombre son inválidos
            nuevo_cliente = Cliente(str(uuid.uuid4()), id_cliente, nombre,
                                    direccion, correo, telefono)

            # Agrega el cliente a la lista en memoria
            self.clientes.append(nuevo_cliente)

            # Registra el evento exitoso en el archivo de log
            registrar_evento(f"GUI: Cliente registrado: {nuevo_cliente}")

            # Muestra ventana de éxito al usuario
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado correctamente.")

            # Limpia los campos del formulario para el próximo registro
            for entry in self.entries_cliente.values():
                entry.delete(0, tk.END)

            # Actualiza la tabla para mostrar el nuevo cliente
            self.actualizar_lista_clientes()

        except ErrorDatosCliente as e:
            # Captura errores de validación específicos del cliente
            registrar_excepcion(e, "GUI Registro Cliente")
            # Muestra el error en una ventana de diálogo de error
            messagebox.showerror("Error de Validación", str(e))

        except Exception as e:
            # Captura cualquier otro error inesperado
            registrar_excepcion(e, "GUI Registro Cliente (inesperado)")
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def actualizar_lista_clientes(self):
        """
        Recarga la tabla de clientes con los datos actuales de la lista en memoria.
        Primero borra todas las filas existentes y luego las vuelve a insertar.
        """
        # Elimina todas las filas actuales de la tabla
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)

        # Inserta una fila por cada cliente en la lista de memoria
        for c in self.clientes:
            self.tree_clientes.insert("", tk.END, values=(
                c.id_objeto[:8] + "...",  # Solo los primeros 8 caracteres del UUID
                c.id_cliente,
                c.nombre,
                c.direccion,
                c.correo,
                c.telefono
            ))

    def eliminar_cliente(self):
        """
        Elimina el cliente seleccionado en la tabla después de pedir confirmación.
        Filtra la lista de clientes en memoria por el ID del cliente seleccionado.
        """
        seleccion = self.tree_clientes.selection()  # Obtiene la fila seleccionada
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente para eliminar.")
            return

        # Muestra diálogo de confirmación antes de eliminar
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            # Obtiene el ID del cliente desde los valores de la fila seleccionada
            id_cliente = self.tree_clientes.item(seleccion[0])['values'][1]

            # Filtra la lista manteniendo solo los clientes con ID diferente
            self.clientes = [c for c in self.clientes if c.id_cliente != id_cliente]

            # Registra la eliminación en el log
            registrar_evento(f"GUI: Cliente {id_cliente} eliminado.")

            # Actualiza la tabla para reflejar el cambio
            self.actualizar_lista_clientes()
            messagebox.showinfo("Éxito", "Cliente eliminado.")

    # ==================== GESTIÓN DE SERVICIOS ====================

    #####################
    # MÉTODOS LIMPIADORES
    #####################

    def _limpiar_sala(self):
        """
        Limpia todos los campos del formulario de sala de reuniones.
        Se llama después de crear exitosamente una sala para dejar
        el formulario listo para un nuevo registro.
        """
        for e in self.entries_sala.values():
            e.delete(0, tk.END)    # Borra el contenido del campo
        self.entries_sala["nombre"].focus()  # Pone el foco en el primer campo

    def _limpiar_equipo(self):
        """
        Limpia todos los campos del formulario de alquiler de equipo.
        También desmarca el checkbox de seguro y pone el foco en el nombre.
        """
        for e in self.entries_equipo.values():
            e.delete(0, tk.END)
        self.chk_seguro.set(False)           # Desmarca el checkbox de seguro
        self.entries_equipo["nombre"].focus()

    def _limpiar_asesoria(self):
        """
        Limpia todos los campos del formulario de asesoría especializada.
        También resetea el combobox de nivel al primer valor (Basico).
        """
        for e in self.entries_asesoria.values():
            e.delete(0, tk.END)
        self.combo_nivel.current(0)          # Restablece nivel a "Basico"
        self.entries_asesoria["nombre"].focus()

    def mostrar_frame_servicios(self):
        """
        Construye y muestra el panel de gestión de servicios.
        Usa un Notebook (pestañas) para organizar los tres formularios:
        1. Reserva de Sala
        2. Alquiler de Equipo
        3. Asesoría Especializada

        Debajo del Notebook muestra la tabla con todos los servicios creados.
        """
        self.limpiar_frames()
        self.frame_servicios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título de la sección
        tk.Label(self.frame_servicios, text="GESTIÓN DE SERVICIOS",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Notebook: widget de pestañas de Tkinter
        notebook = ttk.Notebook(self.frame_servicios)
        notebook.pack(fill=tk.X, padx=10, pady=5)

        # Crea un frame interno para cada pestaña
        self.frame_sala     = tk.Frame(notebook, bg="white")
        self.frame_equipo   = tk.Frame(notebook, bg="white")
        self.frame_asesoria = tk.Frame(notebook, bg="white")

        # Agrega cada frame como pestaña del Notebook con su etiqueta
        notebook.add(self.frame_sala,     text="🏛️ Reserva de Sala")
        notebook.add(self.frame_equipo,   text="🔧 Alquiler de Equipo")
        notebook.add(self.frame_asesoria, text="💼 Asesoría Especializada")

        # Construye el formulario dentro de cada pestaña
        self._form_sala()
        self._form_equipo()
        self._form_asesoria()

        # Marco de la tabla de servicios registrados
        list_frame = tk.LabelFrame(self.frame_servicios, text="Servicios Registrados",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tabla para mostrar todos los servicios con sus detalles
        columns = ("ID", "Tipo", "Nombre", "Precio Base", "Detalles")
        self.tree_servicios = ttk.Treeview(list_frame, columns=columns,
                                            show="headings", height=8)
        for col in columns:
            self.tree_servicios.heading(col, text=col)
            self.tree_servicios.column(col, width=200)

        # Barra de desplazamiento vertical
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                            command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscroll=sb.set)
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Carga los servicios actuales en la tabla
        self.actualizar_lista_servicios()

    def _form_sala(self):
        """
        Construye el formulario de Reserva de Sala dentro de su pestaña.
        Campos: Nombre, Precio Base, Capacidad, Horas.
        """
        self.entries_sala = {}  # Diccionario de campos del formulario

        # Crea una fila por cada campo del formulario de sala
        for i, (lbl, key) in enumerate([
            ("Nombre:",       "nombre"),
            ("Precio Base:",  "precio"),
            ("Capacidad:",    "capacidad"),
            ("Horas:",        "horas")
        ]):
            tk.Label(self.frame_sala, text=lbl, bg="white").grid(
                row=i, column=0, sticky="e", padx=10, pady=8)
            e = tk.Entry(self.frame_sala, width=30)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.entries_sala[key] = e  # Guarda referencia al campo

        # Botón para crear la sala con los datos ingresados
        tk.Button(self.frame_sala, text="Crear Sala",
                    command=self.crear_sala,
                    bg="#27ae60", fg="white",
                    font=("Arial", 10, "bold")
                    ).grid(row=4, column=0, columnspan=2, pady=15)

    def _form_equipo(self):
        """
        Construye el formulario de Alquiler de Equipo dentro de su pestaña.
        Campos: Nombre, Precio Base, Días, y checkbox de Seguro.
        """
        self.entries_equipo = {}  # Diccionario de campos del formulario

        # Crea una fila por cada campo de texto del formulario
        for i, (lbl, key) in enumerate([
            ("Nombre:",      "nombre"),
            ("Precio Base:", "precio"),
            ("Días:",        "dias")
        ]):
            tk.Label(self.frame_equipo, text=lbl, bg="white").grid(
                row=i, column=0, sticky="e", padx=10, pady=8)
            e = tk.Entry(self.frame_equipo, width=30)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.entries_equipo[key] = e

        # Variable booleana vinculada al checkbox de seguro
        self.chk_seguro = tk.BooleanVar()
        tk.Checkbutton(self.frame_equipo,
                        text="Incluir Seguro ($50,000)",
                        variable=self.chk_seguro,
                        bg="white").grid(row=3, column=0, columnspan=2, pady=8)

        # Botón para crear el equipo con los datos ingresados
        tk.Button(self.frame_equipo, text="Crear Equipo",
                    command=self.crear_equipo,
                    bg="#27ae60", fg="white",
                    font=("Arial", 10, "bold")
                    ).grid(row=4, column=0, columnspan=2, pady=15)

    def _form_asesoria(self):
        """
        Construye el formulario de Asesoría Especializada dentro de su pestaña.
        Campos: Nombre, Precio Base, Consultor, y Combobox de Nivel.
        """
        self.entries_asesoria = {}  # Diccionario de campos del formulario

        # Crea una fila por cada campo de texto
        for i, (lbl, key) in enumerate([
            ("Nombre:",     "nombre"),
            ("Precio Base:", "precio"),
            ("Consultor:",  "consultor")
        ]):
            tk.Label(self.frame_asesoria, text=lbl, bg="white").grid(
                row=i, column=0, sticky="e", padx=10, pady=8)
            e = tk.Entry(self.frame_asesoria, width=30)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.entries_asesoria[key] = e

        # Etiqueta y Combobox para seleccionar el nivel de complejidad
        tk.Label(self.frame_asesoria, text="Nivel:", bg="white").grid(
            row=3, column=0, sticky="e", padx=10, pady=8)

        # Combobox con los tres niveles válidos del sistema
        self.combo_nivel = ttk.Combobox(
            self.frame_asesoria,
            values=["Basico", "Intermedio", "Avanzado"],
            state="readonly",  # Solo permite seleccionar; no permite texto libre
            width=27
        )
        self.combo_nivel.grid(row=3, column=1, padx=10, pady=8)
        self.combo_nivel.current(0)  # Selecciona "Basico" por defecto

        # Botón para crear la asesoría con los datos ingresados
        tk.Button(self.frame_asesoria, text="Crear Asesoría",
                    command=self.crear_asesoria,
                    bg="#27ae60", fg="white",
                    font=("Arial", 10, "bold")
                    ).grid(row=4, column=0, columnspan=2, pady=15)

    def crear_sala(self):
        """
        Lee los datos del formulario de sala y crea un objeto ReservaSala.
        Implementa try/except para capturar errores de tipo (ValueError) y
        errores de dominio (ErrorDisponibilidadServicio, ErrorCalculoFinanciero).
        """
        try:
            # Lee y convierte los valores del formulario al tipo esperado
            nombre    = self.entries_sala["nombre"].get()
            precio    = float(self.entries_sala["precio"].get())     # Puede lanzar ValueError
            capacidad = int(self.entries_sala["capacidad"].get())    # Puede lanzar ValueError
            horas     = float(self.entries_sala["horas"].get())      # Puede lanzar ValueError

            # Crea la sala; puede lanzar ErrorDisponibilidadServicio o ErrorCalculoFinanciero
            svc = ReservaSala(str(uuid.uuid4()), nombre, precio, capacidad, horas)
            self.servicios.append(svc)  # Agrega a la lista en memoria

            # Limpia el formulario para el siguiente registro
            self._limpiar_sala()

            # Registra el evento y notifica al usuario
            registrar_evento(f"GUI: Sala creada: {svc.mostrar_info()}")
            messagebox.showinfo("Éxito", "Sala creada correctamente.")
            self.actualizar_lista_servicios()  # Refresca la tabla

        except (ValueError, ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "GUI Crear Sala")
            messagebox.showerror("Error", str(e))

    def crear_equipo(self):
        """
        Lee los datos del formulario de equipo y crea un objeto AlquilerEquipo.
        El estado del checkbox de seguro se lee con self.chk_seguro.get().
        """
        try:
            nombre = self.entries_equipo["nombre"].get()
            precio = float(self.entries_equipo["precio"].get())   # Puede lanzar ValueError
            dias   = int(self.entries_equipo["dias"].get())        # Puede lanzar ValueError
            seguro = self.chk_seguro.get()                         # True/False del checkbox

            # Crea el equipo; puede lanzar ErrorCalculoFinanciero si dias <= 0
            svc = AlquilerEquipo(str(uuid.uuid4()), nombre, precio, dias, seguro)
            self.servicios.append(svc)

            # Limpia el formulario para el siguiente registro
            self._limpiar_equipo()

            registrar_evento(f"GUI: Equipo creado: {svc.mostrar_info()}")
            messagebox.showinfo("Éxito", "Equipo creado correctamente.")
            self.actualizar_lista_servicios()

        except (ValueError, ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "GUI Crear Equipo")
            messagebox.showerror("Error", str(e))

    def crear_asesoria(self):
        """
        Lee los datos del formulario de asesoría y crea un AsesoriaEspecializada.
        El nivel se obtiene del Combobox que solo permite valores predefinidos.
        """
        try:
            nombre    = self.entries_asesoria["nombre"].get()
            precio    = float(self.entries_asesoria["precio"].get())   # Puede lanzar ValueError
            consultor = self.entries_asesoria["consultor"].get()
            nivel     = self.combo_nivel.get()  # Valor seleccionado en el Combobox

            # Crea la asesoría; puede lanzar ErrorDisponibilidadServicio si nivel inválido
            svc = AsesoriaEspecializada(str(uuid.uuid4()), nombre, precio, consultor, nivel)
            self.servicios.append(svc)

            # Limpia el formulario para el siguiente registro
            self._limpiar_asesoria()

            registrar_evento(f"GUI: Asesoría creada: {svc.mostrar_info()}")
            messagebox.showinfo("Éxito", "Asesoría creada correctamente.")
            self.actualizar_lista_servicios()

        except (ValueError, ErrorDisponibilidadServicio, ErrorCalculoFinanciero) as e:
            registrar_excepcion(e, "GUI Crear Asesoría")
            messagebox.showerror("Error", str(e))

    def actualizar_lista_servicios(self):
        """
        Recarga la tabla de servicios con los datos actuales de la lista en memoria.
        Determina el tipo de cada servicio usando la función auxiliar _tipo_servicio().
        """
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)  # Borra todas las filas actuales

        for svc in self.servicios:
            tipo = _tipo_servicio(svc)  # Determina el tipo por instancia (polimorfismo)
            self.tree_servicios.insert("", tk.END, values=(
                svc.id_objeto[:8] + "...",       # UUID abreviado
                tipo,                             # "Sala", "Equipo" o "Asesoría"
                svc.nombre,
                f"${svc.precio_base:,.0f}",       # Precio con formato monetario
                svc.obtener_detalles()            # Método polimórfico de cada subclase
            ))

    # ==================== GESTIÓN DE RESERVAS ====================

    def mostrar_frame_reservas(self):
        """
        Construye y muestra el panel de gestión de reservas.
        Incluye:
        - Formulario con Comboboxes para seleccionar cliente y servicio.
        - Campos para fecha, hora, duración y notas.
        - Botones para crear, confirmar, cancelar y procesar reservas.
        - Tabla con todas las reservas y su estado actual.
        """
        self.limpiar_frames()
        self.frame_reservas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_reservas, text="GESTIÓN DE RESERVAS",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Marco del formulario de nueva reserva
        form_frame = tk.LabelFrame(self.frame_reservas, text="Nueva Reserva",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        # Fila 0: Comboboxes de Cliente y Servicio
        tk.Label(form_frame, text="Cliente:", bg="white").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_clientes = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_clientes.grid(row=0, column=1, padx=5, pady=5)
        self._actualizar_combo_clientes()  # Carga los clientes disponibles

        tk.Label(form_frame, text="Servicio:", bg="white").grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        self.combo_servicios = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_servicios.grid(row=0, column=3, padx=5, pady=5)
        self._actualizar_combo_servicios()  # Carga los servicios disponibles

        # Fila 1: Campos de fecha y hora con valores por defecto
        tk.Label(form_frame, text="Fecha (YYYY-MM-DD):", bg="white").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_fecha = tk.Entry(form_frame, width=15)
        self.entry_fecha.grid(row=1, column=1, padx=5, pady=5)
        # Pre-llena con la fecha de mañana para evitar fechas en el pasado
        self.entry_fecha.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Hora (HH:MM):", bg="white").grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_hora = tk.Entry(form_frame, width=15)
        self.entry_hora.grid(row=1, column=3, padx=5, pady=5)
        self.entry_hora.insert(0, "09:00")  # Hora por defecto: 9 AM

        # Fila 2: Duración en horas y notas adicionales
        tk.Label(form_frame, text="Duración (horas):", bg="white").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_duracion = tk.Entry(form_frame, width=15)
        self.entry_duracion.grid(row=2, column=1, padx=5, pady=5)
        self.entry_duracion.insert(0, "2.0")  # Duración por defecto: 2 horas

        tk.Label(form_frame, text="Notas:", bg="white").grid(
            row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_notas = tk.Entry(form_frame, width=30)
        self.entry_notas.grid(row=2, column=3, padx=5, pady=5)

        # Fila 3: Botones de acción sobre la reserva
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)

        # Botón para crear una nueva reserva en estado pendiente
        tk.Button(btn_frame, text="📅 Crear Reserva",
                    command=self.crear_reserva,
                    bg="#27ae60", fg="white",
                    font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)

        # Botón para confirmar la reserva seleccionada (pendiente → confirmada)
        tk.Button(btn_frame, text="✅ Confirmar",
                    command=self.confirmar_reserva,
                    bg="#3498db", fg="white",
                    font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)

        # Botón para cancelar la reserva seleccionada
        tk.Button(btn_frame, text="❌ Cancelar",
                    command=self.cancelar_reserva,
                    bg="#e74c3c", fg="white",
                    font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)

        # Botón para procesar la reserva (confirmada → completada + calcular costo)
        tk.Button(btn_frame, text="💰 Procesar",
                    command=self.procesar_reserva,
                    bg="#f39c12", fg="white",
                    font=("Arial", 10, "bold"), padx=15).pack(side=tk.LEFT, padx=5)

        # Marco de la tabla de reservas
        list_frame = tk.LabelFrame(self.frame_reservas, text="Reservas Registradas",
                                    font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Define las columnas de la tabla de reservas
        columns = ("ID", "Cliente", "Servicio", "Fecha/Hora", "Duración", "Estado", "Costo")
        self.tree_reservas = ttk.Treeview(list_frame, columns=columns,
                                            show="headings", height=12)
        for col in columns:
            self.tree_reservas.heading(col, text=col)
            self.tree_reservas.column(col, width=120)

        # Barra de desplazamiento vertical
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                            command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscroll=sb.set)
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Carga las reservas actuales en la tabla
        self.actualizar_lista_reservas()

    def _actualizar_combo_clientes(self):
        """Actualiza los valores del Combobox de clientes con la lista en memoria."""
        self.combo_clientes['values'] = [
            f"{c.id_cliente} - {c.nombre}" for c in self.clientes
        ]

    def _actualizar_combo_servicios(self):
        """Actualiza los valores del Combobox de servicios con la lista en memoria."""
        self.combo_servicios['values'] = [
            f"{s.nombre} (${s.precio_base:,.0f})" for s in self.servicios
        ]

    def crear_reserva(self):
        """
        Lee el formulario de reservas y crea un nuevo objeto Reserva.
        Usa el método de fábrica Reserva.crear_reserva() que valida
        fechas pasadas, formato de hora y solapamiento de horarios.
        """
        try:
            # Verifica que haya datos disponibles para seleccionar
            if not self.clientes or not self.servicios:
                messagebox.showwarning(
                    "Atención", "Debe haber clientes y servicios registrados.")
                return

            # Obtiene el índice seleccionado en cada Combobox (-1 = nada seleccionado)
            idx_c = self.combo_clientes.current()
            idx_s = self.combo_servicios.current()
            if idx_c == -1 or idx_s == -1:
                messagebox.showwarning("Atención", "Seleccione cliente y servicio.")
                return

            # Obtiene los objetos correspondientes al índice seleccionado
            cliente  = self.clientes[idx_c]
            servicio = self.servicios[idx_s]

            # Lee los campos del formulario
            fecha_str = self.entry_fecha.get()
            hora_str  = self.entry_hora.get()
            duracion  = float(self.entry_duracion.get())  # Puede lanzar ValueError
            notas     = self.entry_notas.get()
            id_res    = len(self.reservas) + 1  # ID auto-incremental

            # Crea la reserva con validación completa del método de fábrica
            reserva = Reserva.crear_reserva(
                id_res, cliente, servicio, fecha_str, hora_str, duracion, notas
            )
            self.reservas.append(reserva)  # Agrega a la lista en memoria

            registrar_evento(f"GUI: Reserva creada: {reserva}")
            messagebox.showinfo("Éxito", "Reserva creada correctamente.")
            self.actualizar_lista_reservas()  # Refresca la tabla

        except ErrorReserva as e:
            # Captura errores específicos de reservas (solapamiento, fecha pasada, etc.)
            registrar_excepcion(e, "GUI Crear Reserva")
            messagebox.showerror("Error de Reserva", str(e))

        except ValueError:
            # Captura error si la duración no es un número válido
            messagebox.showerror("Error", "Verifique el formato de fecha/hora o duración.")

        except Exception as e:
            # Captura cualquier otro error no anticipado
            registrar_excepcion(e, "GUI Crear Reserva (inesperado)")
            messagebox.showerror("Error", str(e))

    def _get_reserva_seleccionada(self) -> 'Reserva | None':
        """
        Obtiene el objeto Reserva correspondiente a la fila seleccionada en la tabla.
        Retorna None si no hay ninguna fila seleccionada.
        """
        seleccion = self.tree_reservas.selection()  # Obtiene la fila seleccionada
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una reserva.")
            return None

        # Obtiene el ID de la reserva desde la primera columna de la fila
        id_reserva = int(self.tree_reservas.item(seleccion[0])['values'][0])

        # Busca y retorna la reserva con ese ID en la lista de memoria
        # next() retorna el primer elemento que cumpla la condición, o None
        return next((r for r in self.reservas if r.id == id_reserva), None)

    def confirmar_reserva(self):
        """
        Confirma la reserva seleccionada en la tabla.
        Cambia su estado de 'pendiente' a 'confirmada'.
        Maneja ErrorReserva si la reserva no está en estado permitido.
        """
        reserva = self._get_reserva_seleccionada()
        if not reserva:
            return  # Sale si no hay reserva seleccionada

        try:
            reserva.confirmar()  # Lanza ErrorReserva si no está en estado 'pendiente'
            registrar_evento(f"GUI: Reserva #{reserva.id} confirmada.")
            messagebox.showinfo("Éxito", "Reserva confirmada.")
            self.actualizar_lista_reservas()  # Refresca para mostrar el nuevo estado

        except ErrorReserva as e:
            registrar_excepcion(e, "GUI Confirmar Reserva")
            messagebox.showerror("Error", str(e))

    def cancelar_reserva(self):
        """
        Cancela la reserva seleccionada en la tabla después de pedir confirmación.
        No permite cancelar reservas ya completadas.
        """
        reserva = self._get_reserva_seleccionada()
        if not reserva:
            return

        # Pide confirmación antes de cancelar (acción irreversible)
        if messagebox.askyesno("Confirmar", "¿Cancelar esta reserva?"):
            try:
                reserva.cancelar()  # Lanza ErrorReserva si ya está completada
                registrar_evento(f"GUI: Reserva #{reserva.id} cancelada.")
                messagebox.showinfo("Éxito", "Reserva cancelada.")
                self.actualizar_lista_reservas()

            except ErrorReserva as e:
                registrar_excepcion(e, "GUI Cancelar Reserva")
                messagebox.showerror("Error", str(e))

    def procesar_reserva(self):
        """
        Procesa la reserva seleccionada: calcula el costo total y la marca
        como completada. Solo funciona con reservas en estado 'confirmada'.
        Muestra el costo calculado al usuario en una ventana de diálogo.
        """
        reserva = self._get_reserva_seleccionada()
        if not reserva:
            return

        try:
            # procesar() llama a calcular_costo() (polimórfico) y cambia estado
            costo = reserva.procesar()

            registrar_evento(f"GUI: Reserva #{reserva.id} procesada. Costo: ${costo:,.0f}")
            # Muestra el costo total calculado al usuario
            messagebox.showinfo("Procesado", f"Reserva procesada.\nCosto total: ${costo:,.0f}")
            self.actualizar_lista_reservas()

        except ErrorReserva as e:
            # Puede fallar si la reserva no está confirmada o si calcular_costo() falla
            registrar_excepcion(e, "GUI Procesar Reserva")
            messagebox.showerror("Error", str(e))

    def actualizar_lista_reservas(self):
        """
        Recarga la tabla de reservas con el estado actual de cada reserva en memoria.
        Intenta calcular el costo de cada reserva; si falla, muestra "N/A".
        """
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)  # Borra todas las filas actuales

        for reserva in self.reservas:
            try:
                # calcular_costo() es polimórfico según el tipo de servicio
                costo_str = f"${reserva.servicio.calcular_costo():,.0f}"
            except Exception:
                # Si el cálculo falla por cualquier razón, muestra "N/A"
                costo_str = "N/A"

            self.tree_reservas.insert("", tk.END, values=(
                reserva.id,
                reserva.cliente.nombre,
                reserva.servicio.nombre,
                reserva.fecha_hora.strftime("%Y-%m-%d %H:%M"),  # Formato legible
                f"{reserva.duracion}h",
                reserva.estado.capitalize(),   # Primera letra en mayúscula
                costo_str
            ))

    # ==================== REPORTES ====================

    def mostrar_frame_reportes(self):
        """
        Construye y muestra el panel de reportes y estadísticas.
        Calcula y muestra métricas clave: totales, reservas por estado
        e ingresos generados por reservas completadas.
        """
        self.limpiar_frames()
        self.frame_reportes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_reportes, text="REPORTES Y ESTADÍSTICAS",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Marco con el resumen de estadísticas
        stats_frame = tk.LabelFrame(self.frame_reportes, text="Resumen",
                                    font=("Arial", 10, "bold"),
                                    bg="white", padx=20, pady=20)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        # Filtra las reservas por estado para calcular las métricas
        reservas_confirmadas = [r for r in self.reservas if r.estado == "confirmada"]
        reservas_completadas = [r for r in self.reservas if r.estado == "completada"]

        # Suma los ingresos de reservas completadas usando _safe_costo()
        # _safe_costo() maneja excepciones para evitar que una falla interrumpa el total
        ingresos = sum(
            r.servicio.calcular_costo()
            for r in reservas_completadas
            if self._safe_costo(r) is not None
        )

        # Lista de métricas a mostrar: (etiqueta, valor)
        stats = [
            ("Total Clientes:",   len(self.clientes)),
            ("Total Servicios:",  len(self.servicios)),
            ("Total Reservas:",   len(self.reservas)),
            ("Confirmadas:",      len(reservas_confirmadas)),
            ("Completadas:",      len(reservas_completadas)),
            ("Ingresos Totales:", f"${ingresos:,.0f}"),
        ]

        # Muestra cada métrica en una cuadrícula de 3 columnas
        for i, (lbl, val) in enumerate(stats):
            tk.Label(stats_frame, text=lbl,
                        font=("Arial", 10, "bold"),
                     bg="white").grid(row=i // 3, column=(i % 3) * 2,
                                        sticky="e", padx=20, pady=10)
            tk.Label(stats_frame, text=str(val),
                        font=("Arial", 10),
                        bg="#ecf0f1", padx=20, pady=10
                     ).grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w")

        # Botón para recalcular y refrescar los reportes
        tk.Button(self.frame_reportes, text="🔄 Actualizar Reportes",
                    command=self.mostrar_frame_reportes,
                    bg="#3498db", fg="white",
                    font=("Arial", 10, "bold"),
                    padx=20, pady=10).pack(pady=20)

    def _safe_costo(self, reserva):
        """
        Calcula el costo de una reserva de forma segura.
        Si calcular_costo() lanza una excepción, retorna None
        en lugar de interrumpir el proceso de generación del reporte.
        """
        try:
            return reserva.servicio.calcular_costo()  # Llamada polimórfica
        except Exception:
            return None  # Retorna None si el cálculo falla

    # ==================== LOG ====================

    def mostrar_frame_log(self):
        """
        Construye y muestra el panel del visualizador del archivo de log.
        Muestra las últimas 50 líneas del archivo sistema_fj.log en un
        widget de texto con fondo oscuro estilo terminal.
        """
        self.limpiar_frames()
        self.frame_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.frame_log, text="REGISTRO DE EVENTOS (LOG)",
                    font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Frame contenedor del área de texto
        text_frame = tk.Frame(self.frame_log, bg="#ecf0f1")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Área de texto estilo terminal: fondo negro, texto gris claro
        self.text_log = tk.Text(text_frame, wrap=tk.WORD,
                                font=("Courier", 9),   # Fuente monoespaciada para logs
                                bg="#1e1e1e",           # Fondo oscuro estilo terminal
                                fg="#d4d4d4",           # Texto gris claro
                                height=30)

        # Barra de desplazamiento vertical vinculada al área de texto
        sb = ttk.Scrollbar(text_frame, orient=tk.VERTICAL,
                            command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=sb.set)
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Botón para recargar el log manualmente
        tk.Button(self.frame_log, text="🔄 Actualizar Log",
                    command=self._cargar_log,
                    bg="#3498db", fg="white",
                    font=("Arial", 10, "bold"),
                    padx=20).pack(pady=10)

        # Carga el log al abrir el panel
        self._cargar_log()

    def _cargar_log(self):
        """
        Lee las últimas 50 líneas del archivo de log y las muestra
        en el widget de texto. Activa el widget para escribir,
        borra el contenido anterior, inserta las nuevas líneas,
        y luego vuelve a desactivarlo para que sea solo lectura.
        """
        self.text_log.config(state=tk.NORMAL)       # Habilita edición para actualizar
        self.text_log.delete("1.0", tk.END)          # Borra todo el contenido actual

        # Lee e inserta cada línea del log en el área de texto
        for linea in leer_log(50):
            self.text_log.insert(tk.END, linea)

        self.text_log.config(state=tk.DISABLED)      # Deshabilita edición (solo lectura)
        self.text_log.see(tk.END)                    # Desplaza automáticamente al final


# ==================== FUNCIÓN AUXILIAR ====================

def _tipo_servicio(servicio) -> str:
    """
    Determina el tipo de servicio basándose en la instancia del objeto.
    Implementa polimorfismo con isinstance() para identificar la subclase.

    Parámetros:
        servicio: objeto de cualquier subclase de Servicio.

    Retorna:
        str: nombre del tipo de servicio ("Sala", "Equipo", "Asesoría" o "Desconocido").
    """
    if isinstance(servicio, ReservaSala):
        return "Sala"          # Es una instancia de ReservaSala
    elif isinstance(servicio, AlquilerEquipo):
        return "Equipo"        # Es una instancia de AlquilerEquipo
    elif isinstance(servicio, AsesoriaEspecializada):
        return "Asesoría"      # Es una instancia de AsesoriaEspecializada
    return "Desconocido"       # Tipo no reconocido (no debería ocurrir en operación normal)


def main():
    """
    Función de entrada de la interfaz gráfica.
    Crea la ventana raíz de Tkinter e inicia el bucle principal de eventos.
    mainloop() mantiene la ventana abierta hasta que el usuario la cierre.
    """
    root = tk.Tk()          # Crea la ventana raíz de la aplicación
    app = AplicacionGUI(root)  # Inicializa la aplicación con la ventana raíz
    root.mainloop()         # Inicia el bucle de eventos de Tkinter


if __name__ == "__main__":
    """
    Ejecuta la GUI solo cuando el archivo se corre directamente,
    no cuando es importado como módulo.
    """
    main()