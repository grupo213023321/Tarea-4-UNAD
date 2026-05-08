import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import datetime

# Configuración de logs a archivo
logging.basicConfig(
    filename='logs_sistema.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)

from entidades import Cliente, ErrorCliente
from servicios import Sala, Equipo, Asesoria, ErrorServicio
from reservas import Reserva, ErrorReserva

class SoftwareFJApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software FJ - Gestión Integral")
        self.geometry("1000x750")
        
        # Almacenamiento en memoria (sin BD)
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self._cont_reserva = 1000

        self._construir_interfaz()

    def _construir_interfaz(self):
        # ================= BARRA SUPERIOR =================
        top_frame = ttk.Frame(self, padding=(10, 5))
        top_frame.pack(fill="x")
        
        ttk.Label(top_frame, text="🖥️ Software FJ - Panel de Control", font=("Segoe UI", 14, "bold")).pack(side="left")
        self.btn_demo = ttk.Button(top_frame, text="▶ EJECUTAR 10 OPERACIONES DE PRUEBA", command=self._simulacion_10)
        self.btn_demo.pack(side="right")

        # ================= PESTAÑAS CENTRALES =================
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=5)

        self._pestana_clientes(nb)
        self._pestana_servicios(nb)
        self._pestana_reservas(nb)

        # ================= PANEL DE LOGS INFERIOR =================
        log_frame = ttk.LabelFrame(self, text="📋 Registro de Actividad (Logs del Sistema)", padding=8)
        log_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        self.txt_log = scrolledtext.ScrolledText(log_frame, height=8, state="disabled", 
                                                 font=("Consolas", 10), bg="#0d1117", fg="#c9d1d9")
        self.txt_log.pack(fill="both", expand=True)
        
        self._log_ui("✅ Sistema inicializado. Ingrese datos manualmente o ejecute la simulación automática.")
        self._log_ui("ℹ️ Todos los eventos se registran automáticamente en 'logs_sistema.log'")

    # ================= CLIENTES =================
    def _pestana_clientes(self, parent):
        f = ttk.Frame(parent)
        parent.add(f, text="👤 Clientes")
        
        ttk.Label(f, text="ID Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ent_c_id = ttk.Entry(f); self.ent_c_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Nombre Completo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ent_c_nom = ttk.Entry(f); self.ent_c_nom.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ent_c_email = ttk.Entry(f); self.ent_c_email.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Teléfono (10 dígitos):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.ent_c_tel = ttk.Entry(f); self.ent_c_tel.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(f, text="✅ Registrar Cliente", command=self._registrar_cliente_gui).grid(row=4, column=0, columnspan=2, pady=15)
        self.lbl_c_stat = ttk.Label(f, text="", foreground="blue")
        self.lbl_c_stat.grid(row=5, column=0, columnspan=2)
        f.grid_columnconfigure(1, weight=1)

    def _registrar_cliente_gui(self):
        try:
            id_c = self.ent_c_id.get().strip()
            nom = self.ent_c_nom.get().strip()
            email = self.ent_c_email.get().strip()
            tel = self.ent_c_tel.get().strip()

            if not all([id_c, nom, email, tel]):
                raise ValueError("Todos los campos son obligatorios.")

            c = Cliente(id_c, nom, email, tel)
            self.clientes.append(c)
            
            self.lbl_c_stat.config(text="✅ Registrado exitosamente.", foreground="green")
            self._log_ui(f"Cliente registrado: {c.info()}")
            self._limpiar([self.ent_c_id, self.ent_c_nom, self.ent_c_email, self.ent_c_tel])
            
        except Exception as e:
            self.lbl_c_stat.config(text=f"❌ Error: {e}", foreground="red")
            messagebox.showerror("Error de Validación", str(e))
            logging.error(f"Error UI -> Cliente: {e}")

    # ================= SERVICIOS =================
    def _pestana_servicios(self, parent):
        f = ttk.Frame(parent)
        parent.add(f, text="🛠️ Servicios")
        
        ttk.Label(f, text="ID Servicio:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ent_s_id = ttk.Entry(f); self.ent_s_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ent_s_nom = ttk.Entry(f); self.ent_s_nom.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Costo Base ($):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ent_s_costo = ttk.Entry(f); self.ent_s_costo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Tipo:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.combo_s_tipo = ttk.Combobox(f, values=["Sala", "Equipo", "Asesoria"], state="readonly")
        self.combo_s_tipo.current(0)
        self.combo_s_tipo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(f, text="✅ Crear Servicio", command=self._crear_servicio_gui).grid(row=4, column=0, columnspan=2, pady=15)
        self.lbl_s_stat = ttk.Label(f, text="", foreground="blue")
        self.lbl_s_stat.grid(row=5, column=0, columnspan=2)
        f.grid_columnconfigure(1, weight=1)

    def _crear_servicio_gui(self):
        try:
            id_s = self.ent_s_id.get().strip()
            nom = self.ent_s_nom.get().strip()
            costo = float(self.ent_s_costo.get().strip())
            tipo = self.combo_s_tipo.get()

            clases = {"Sala": Sala, "Equipo": Equipo, "Asesoria": Asesoria}
            s = clases[tipo](id_s, nom, costo)
            self.servicios.append(s)

            self.lbl_s_stat.config(text="✅ Servicio creado exitosamente.", foreground="green")
            self._log_ui(f"Servicio registrado: {s.info()}")
            self._limpiar([self.ent_s_id, self.ent_s_nom, self.ent_s_costo])
            
        except ValueError:
            self.lbl_s_stat.config(text="❌ El costo debe ser un número válido.", foreground="red")
            messagebox.showerror("Error", "Ingrese un número válido para el costo base.")
        except Exception as e:
            self.lbl_s_stat.config(text=f"❌ Error: {e}", foreground="red")
            messagebox.showerror("Error de Servicio", str(e))
            logging.error(f"Error UI -> Servicio: {e}")

    # ================= RESERVAS =================
    def _pestana_reservas(self, parent):
        f = ttk.Frame(parent)
        parent.add(f, text="📅 Reservas")
        
        ttk.Label(f, text="ID Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ent_r_idc = ttk.Entry(f); self.ent_r_idc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="ID Servicio:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ent_r_ids = ttk.Entry(f); self.ent_r_ids.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(f, text="Duración (horas):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ent_r_horas = ttk.Entry(f); self.ent_r_horas.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(f, text="✅ Procesar Reserva", command=self._crear_reserva_gui).grid(row=3, column=0, columnspan=2, pady=15)
        self.lbl_r_stat = ttk.Label(f, text="", foreground="blue")
        self.lbl_r_stat.grid(row=4, column=0, columnspan=2)
        f.grid_columnconfigure(1, weight=1)

    def _crear_reserva_gui(self):
        try:
            id_c = self.ent_r_idc.get().strip()
            id_s = self.ent_r_ids.get().strip()
            horas = int(self.ent_r_horas.get().strip())

            c = next((x for x in self.clientes if x.id == id_c), None)
            s = next((x for x in self.servicios if x.id == id_s), None)
            if not c: raise ValueError("ID de cliente no encontrado en el sistema.")
            if not s: raise ValueError("ID de servicio no encontrado en el sistema.")

            self._cont_reserva += 1
            r = Reserva(f"RES-{self._cont_reserva}", c, s, horas)
            r.procesar()
            self.reservas.append(r)

            self.lbl_r_stat.config(text=f"✅ Reserva {r.id} confirmada | Costo: ${r.costo_final}", foreground="green")
            self._log_ui(f"Reserva {r.id}: {c.nombre} -> {s.nombre} | {horas}h | ${r.costo_final}")
            self._limpiar([self.ent_r_idc, self.ent_r_ids, self.ent_r_horas])
            
        except ValueError:
            self.lbl_r_stat.config(text="❌ Las horas deben ser un número entero.", foreground="red")
            messagebox.showerror("Error", "Ingrese horas como número entero.")
        except Exception as e:
            self.lbl_r_stat.config(text=f"❌ Error: {e}", foreground="red")
            messagebox.showerror("Error de Reserva", str(e))
            logging.error(f"Error UI -> Reserva: {e}")

    # ================= LOGS & SIMULACIÓN =================
    def _log_ui(self, mensaje: str):
        """Escribe en la UI y en el archivo de logs simultáneamente."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {mensaje}"
        
        # Actualizar archivo
        logging.info(mensaje)
        
        # Actualizar interfaz
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", log_msg + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")
        self.update()

    def _limpiar(self, entradas):
        for ent in entradas:
            ent.delete(0, tk.END)

    def _simulacion_10(self):
        self._log_ui("\n🚀 INICIANDO SIMULACIÓN DE 10 OPERACIONES...")
        casos = [
            ("Registro Cliente Válido", lambda: self.clientes.append(Cliente("C01", "Ana López", "ana@correo.com", "0999887766"))),
            ("Registro Cliente Inválido (Email)", lambda: self._forzar_error(Cliente, "C02", "Pedro", "pedro-invalido", "0987654321")),
            ("Servicio Sala Válido", lambda: self.servicios.append(Sala("S01", "Sala Conferencias", 50.0))),
            ("Servicio Inválido (Costo <= 0)", lambda: self._forzar_error(Sala, "S02", "Proyector", -10.0)),
            ("Servicio Asesoría Válido", lambda: self.servicios.append(Asesoria("S03", "Consultoría TI", 120.0))),
            ("Reserva Exitosa (Sala 3h)", lambda: self._crear_reserva_interna("C01", "S01", 3)),
            ("Reserva Fallida (Servicio Inexistente)", lambda: self._crear_reserva_interna("C01", "S99", 2)),
            ("Cliente Inválido (Teléfono)", lambda: self._forzar_error(Cliente, "C03", "María", "m@x.com", "123")),
            ("Reserva Fallida (Horas <= 0)", lambda: self._crear_reserva_interna("C01", "S03", -1)),
            ("Reserva Exitosa (Asesoría 2h)", lambda: self._crear_reserva_interna("C01", "S03", 2)),
        ]

        for i, (desc, accion) in enumerate(casos, 1):
            try:
                accion()
                self._log_ui(f"✅ {i:02}. {desc}: EXITOSO")
            except Exception as e:
                self._log_ui(f"❌ {i:02}. {desc}: {e} (Sistema estable)")
            finally:
                self._log_ui("-" * 45)

        self._log_ui("🏁 SIMULACIÓN FINALIZADA. Ver `logs_sistema.log` para registro técnico completo.")
        messagebox.showinfo("Demo Finalizada", "Las 10 operaciones se ejecutaron correctamente.\nRevisa el panel inferior y el archivo de logs.")

    def _forzar_error(self, clase, *args):
        return clase(*args)

    def _crear_reserva_interna(self, id_c, id_s, horas):
        c = next((x for x in self.clientes if x.id == id_c), None)
        s = next((x for x in self.servicios if x.id == id_s), None)
        if not c or not s: raise ValueError("ID no encontrado")
        self._cont_reserva += 1
        r = Reserva(f"RES-{self._cont_reserva}", c, s, horas)
        r.procesar()
        self.reservas.append(r)

if __name__ == "__main__":
    app = SoftwareFJApp()
    app.mainloop()