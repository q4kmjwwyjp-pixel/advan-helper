import customtkinter as ctk
import urllib.request
import json

# =========================================================================
# PEGA AQUÍ TU URL DE APPS SCRIPT:
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbylxSqmSdiTUrYCKhllKQ7eTu9sLU8Yb27pAUBbmAFnUMRiILfH9zANmzczrAzoYCj58g/exec"
# =========================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdvanHelperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advan Helper Pro - Tradelossa")
        self.geometry("380x610")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0f111a")

        self.ultima_fila = None
        self.historial = []
        self.modo_mini = False

        # Eventos para Transparencia Inteligente
        self.bind("<Enter>", self.on_mouse_enter)
        self.bind("<Leave>", self.on_mouse_leave)

        # --- BARRA SUPERIOR (HEADER) ---
        self.header = ctk.CTkFrame(self, fg_color="#181b28", corner_radius=12, height=45)
        self.header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(self.header, text="Resp:", font=("Segoe UI", 12, "bold"), text_color="#a6adc8").pack(side="left", padx=(10, 4), pady=8)
        
        self.seg_resp = ctk.CTkSegmentedButton(
            self.header, values=["FS", "FF"], width=70, height=26,
            selected_color="#3b82f6", selected_hover_color="#2563eb",
            font=("Segoe UI", 11, "bold")
        )
        self.seg_resp.set("FS")
        self.seg_resp.pack(side="left", padx=2)

        self.btn_mini = ctk.CTkButton(
            self.header, text="🔼 Mini", width=55, height=26, corner_radius=8,
            fg_color="#26293c", hover_color="#3b405e", font=("Segoe UI", 11, "bold"),
            command=self.toggle_mini
        )
        self.btn_mini.pack(side="right", padx=8)

        self.sw_ghost = ctk.CTkSwitch(
            self.header, text="Fantasma", font=("Segoe UI", 11), text_color="#a6adc8",
            progress_color="#8b5cf6", width=40
        )
        self.sw_ghost.select()
        self.sw_ghost.pack(side="right", padx=6)

        # --- CONTENEDOR PRINCIPAL ---
        self.main_body = ctk.CTkFrame(self, fg_color="transparent")
        self.main_body.pack(fill="both", expand=True, padx=10, pady=2)

        # Switch Fijar OC/Factura
        self.frame_fijar = ctk.CTkFrame(self.main_body, fg_color="#181b28", corner_radius=10)
        self.frame_fijar.pack(fill="x", pady=3)
        self.sw_repetir = ctk.CTkSwitch(
            self.frame_fijar, text="Fijar OC / Factura (Múltiples Unidades)",
            font=("Segoe UI", 11, "bold"), text_color="#cbd5e1", progress_color="#10b981"
        )
        self.sw_repetir.pack(padx=12, pady=6, anchor="w")

        # --- TARJETA DE FORMULARIO ---
        self.form_card = ctk.CTkFrame(self.main_body, fg_color="#181b28", corner_radius=12)
        self.form_card.pack(fill="x", pady=4)

        self.entries = {}

        # 1. FILA ESPECIAL PARA CÓDIGO (ARRIBA CON BOTÓN BUSCAR Y OTRA OC)
        row_cod = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_cod.pack(fill="x", padx=10, pady=(8, 4))
        
        ctk.CTkLabel(row_cod, text="1° Código(s):", width=85, anchor="w", font=("Segoe UI", 12, "bold"), text_color="#38bdf8").pack(side="left")
        
        self.btn_cancelar_busq = ctk.CTkButton(
            row_cod, text="✖ Otra OC", width=62, height=28, corner_radius=8,
            fg_color="#ef4444", hover_color="#dc2626", font=("Segoe UI", 10, "bold"),
            command=self.descartar_autocompletado
        )
        self.btn_cancelar_busq.pack(side="right", padx=(4, 0))

        self.btn_buscar = ctk.CTkButton(
            row_cod, text="🔍", width=32, height=28, corner_radius=8,
            fg_color="#3b82f6", hover_color="#2563eb", font=("Segoe UI", 12, "bold"),
            command=self.buscar_ultimo_codigo
        )
        self.btn_buscar.pack(side="right", padx=(4, 0))

        ent_cod = ctk.CTkEntry(
            row_cod, placeholder_text="Ej. A00-012 (Enter)", height=28, corner_radius=8,
            fg_color="#0f111a", border_color="#38bdf8", border_width=1,
            text_color="#ffffff", font=("Segoe UI", 12, "bold")
        )
        ent_cod.pack(side="right", fill="x", expand=True)
        ent_cod.bind("<Return>", self.buscar_ultimo_codigo)
        self.entries["cod"] = ent_cod

        # 2. RESTO DE CAMPOS
        otros_campos = [
            ("Orden Compra:", "oc", "Ej. 88027"),
            ("Factura / Ref:", "fact", "Ej. 70545 o PTE"),
            ("Descripción:", "desc", "Ej. ACUMULADOR"),
            ("Proveedor:", "prov", "Ej. 7302"),
            ("Unidad:", "uni", "Ej. K234 (Enter guarda)")
        ]

        claves_orden = [c[1] for c in otros_campos]

        for idx, (label_txt, key, placeholder) in enumerate(otros_campos):
            row = ctk.CTkFrame(self.form_card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            
            lbl = ctk.CTkLabel(row, text=label_txt, width=95, anchor="w", font=("Segoe UI", 12, "bold"), text_color="#e2e8f0")
            lbl.pack(side="left")

            ent = ctk.CTkEntry(
                row, placeholder_text=placeholder, height=28, corner_radius=8,
                fg_color="#0f111a", border_color="#2e344e", border_width=1,
                text_color="#ffffff", font=("Segoe UI", 12)
            )
            ent.pack(side="right", fill="x", expand=True)
            ent.bind("<KeyRelease>", self.actualizar_preview)

            if idx < len(otros_campos) - 1:
                next_key = claves_orden[idx + 1]
                ent.bind("<Return>", lambda e, nk=next_key: self.entries[nk].focus())
            else:
                ent.bind("<Return>", lambda e: self.guardar_y_copiar())

            self.entries[key] = ent

        # --- VISTA PREVIA ---
        self.preview_box = ctk.CTkFrame(self.main_body, fg_color="#141824", corner_radius=8, border_width=1, border_color="#1e293b")
        self.preview_box.pack(fill="x", pady=5)
        self.lbl_preview = ctk.CTkLabel(
            self.preview_box, text="OC MTY (FACT PROV )", font=("Consolas", 11, "bold"),
            text_color="#38bdf8", wraplength=340
        )
        self.lbl_preview.pack(pady=6, padx=6)

        # --- BOTÓN 1: COPIAR Y GUARDAR ---
        self.btn_guardar = ctk.CTkButton(
            self.main_body, text="📋 1. COPIAR Y GUARDAR EN SHEETS", height=36, corner_radius=10,
            fg_color="#3b82f6", hover_color="#2563eb", font=("Segoe UI", 12, "bold"),
            command=self.guardar_y_copiar
        )
        self.btn_guardar.pack(fill="x", pady=4)

        # --- SECCIÓN DE PÓLIZA ---
        self.pol_card = ctk.CTkFrame(self.main_body, fg_color="#181b28", corner_radius=10)
        self.pol_card.pack(fill="x", pady=4)

        ctk.CTkLabel(self.pol_card, text="N° Póliza:", font=("Segoe UI", 12, "bold"), text_color="#e2e8f0").pack(side="left", padx=(12, 6), pady=7)
        
        self.entry_pol = ctk.CTkEntry(
            self.pol_card, placeholder_text="Folio...", width=95, height=28, corner_radius=8,
            fg_color="#0f111a", border_color="#10b981", border_width=1, font=("Segoe UI", 12, "bold")
        )
        self.entry_pol.pack(side="left", pady=7)
        self.entry_pol.bind("<Return>", self.guardar_poliza)

        self.btn_pol = ctk.CTkButton(
            self.pol_card, text="💾 2. Guardar Póliza", height=28, corner_radius=8,
            fg_color="#10b981", hover_color="#059669", text_color="#052e16",
            font=("Segoe UI", 11, "bold"), command=self.guardar_poliza
        )
        self.btn_pol.pack(side="right", padx=10, pady=7)

        # Estado
        self.lbl_status = ctk.CTkLabel(self.main_body, text="✨ Escribe un Código y presiona Enter", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        self.lbl_status.pack(pady=1)

        # --- HISTORIAL DE ÚLTIMOS 3 REGISTROS ---
        self.hist_card = ctk.CTkFrame(self.main_body, fg_color="#141622", corner_radius=10)
        self.hist_card.pack(fill="x", pady=(4, 2))
        
        ctk.CTkLabel(self.hist_card, text="🕒 Últimos 3 registros de esta sesión:", font=("Segoe UI", 10, "bold"), text_color="#64748b").pack(anchor="w", padx=10, pady=(4, 0))
        self.lbl_hist = ctk.CTkLabel(
            self.hist_card, text="Sin capturas recientes...", font=("Consolas", 10),
            text_color="#94a3b8", justify="left", anchor="w"
        )
        self.lbl_hist.pack(fill="x", padx=10, pady=(2, 6))

    # --- TRANSPARENCIA Y MODO MINI ---
    def on_mouse_enter(self, event=None):
        self.attributes("-alpha", 1.0)

    def on_mouse_leave(self, event=None):
        if self.sw_ghost.get() == 1:
            self.attributes("-alpha", 0.55)

    def toggle_mini(self):
        if not self.modo_mini:
            self.main_body.pack_forget()
            self.geometry("380x65")
            self.btn_mini.configure(text="🔽 Abrir")
            self.modo_mini = True
        else:
            self.geometry("380x610")
            self.main_body.pack(fill="both", expand=True, padx=10, pady=2)
            self.btn_mini.configure(text="🔼 Mini")
            self.modo_mini = False

    # --- BÚSQUEDA INTELIGENTE POR CÓDIGO ---
    def buscar_ultimo_codigo(self, event=None):
        cod = self.entries["cod"].get().strip().upper()
        if not cod:
            return

        self.lbl_status.configure(text=f"🔍 Buscando último registro de {cod}...", text_color="#38bdf8")
        self.update()

        datos = {"action": "buscar_codigo", "codigo": cod}
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps(datos).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                if res.get("status") == "found":
                    for campo, valor in [("oc", res.get("oc")), ("fact", res.get("factura")), 
                                         ("desc", res.get("descripcion")), ("prov", res.get("proveedor"))]:
                        self.entries[campo].delete(0, "end")
                        self.entries[campo].insert(0, valor)
                    
                    self.actualizar_preview()
                    fecha_ant = res.get("fecha", "")
                    uni_ant = res.get("unidad_anterior", "")
                    self.lbl_status.configure(
                        text=f"✅ Últ: {fecha_ant} [{uni_ant}]. Valida o da '✖ Otra OC'",
                        text_color="#10b981"
                    )
                    self.entries["uni"].focus()
                else:
                    self.lbl_status.configure(text="ℹ️ Código nuevo. Llena los datos manualmente.", text_color="#f59e0b")
                    self.entries["oc"].focus()
        except Exception:
            self.lbl_status.configure(text="⚠️ No se pudo buscar en Sheets. Llena manual.", text_color="#ef4444")
            self.entries["oc"].focus()

    def descartar_autocompletado(self):
        for key in ["oc", "fact", "prov"]:
            self.entries[key].delete(0, "end")
        self.actualizar_preview()
        self.lbl_status.configure(text="✏️ Ingresa la nueva OC, Factura y Proveedor", text_color="#f59e0b")
        self.entries["oc"].focus()

    # --- LÓGICA DE GUARDADO ---
    def armar_texto(self):
        oc = self.entries["oc"].get().strip().upper()
        fact = self.entries["fact"].get().strip().upper()
        desc = self.entries["desc"].get().strip().upper()
        uni = self.entries["uni"].get().strip().upper()
        prov = self.entries["prov"].get().strip().upper()
        texto = f"OC MTY {oc} {desc} {uni} (FACT {fact} PROV {prov})"
        return " ".join(texto.split())

    def actualizar_preview(self, event=None):
        self.lbl_preview.configure(text=self.armar_texto())

    def actualizar_vista_historial(self):
        if not self.historial:
            self.lbl_hist.configure(text="Sin capturas recientes...")
            return
        lineas = []
        for item in self.historial[:3]:
            lineas.append(f"• [Fila {item['row']}] {item['uni']} | {item['desc'][:10]} | Pól: {item['pol']}")
        self.lbl_hist.configure(text="\n".join(lineas))

    def guardar_y_copiar(self):
        desc = self.entries["desc"].get().strip()
        if not desc:
            self.lbl_status.configure(text="⚠️ Escribe al menos la Descripción", text_color="#f59e0b")
            return

        texto_contab = self.armar_texto()
        self.clipboard_clear()
        self.clipboard_append(texto_contab)
        self.update()

        datos = {
            "action": "nuevo",
            "oc": self.entries["oc"].get(),
            "factura": self.entries["fact"].get(),
            "descripcion": desc,
            "unidad": self.entries["uni"].get(),
            "proveedor": self.entries["prov"].get(),
            "codigo": self.entries["cod"].get(),
            "responsable": self.seg_resp.get(),
            "poliza": self.entry_pol.get()
        }

        self.lbl_status.configure(text="⏳ Copiado. Guardando en Google Sheets...", text_color="#f59e0b")
        self.update()

        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps(datos).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                self.ultima_fila = res.get("row")
                
                pol_actual = self.entry_pol.get().strip() or "Pend."
                self.historial.insert(0, {
                    "row": self.ultima_fila,
                    "uni": self.entries["uni"].get().strip().upper() or "S/U",
                    "desc": desc.upper(),
                    "pol": pol_actual
                })
                self.actualizar_vista_historial()

                self.lbl_status.configure(text=f"✅ Copiado y Guardado (Fila {self.ultima_fila})", text_color="#10b981")
                self.entry_pol.focus()
        except Exception:
            self.lbl_status.configure(text="❌ Copiado al Ctrl+V, pero falló red con Sheets", text_color="#ef4444")

    def guardar_poliza(self, event=None):
        poliza = self.entry_pol.get().strip()
        if not self.ultima_fila or not poliza:
            return

        self.lbl_status.configure(text="⏳ Guardando póliza...", text_color="#38bdf8")
        self.update()

        datos = {"action": "actualizar_poliza", "row": self.ultima_fila, "poliza": poliza}
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps(datos).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
            
            if self.historial and self.historial[0]["row"] == self.ultima_fila:
                self.historial[0]["pol"] = poliza
                self.actualizar_vista_historial()

            self.lbl_status.configure(text=f"✅ Póliza {poliza} guardada en Fila {self.ultima_fila}", text_color="#38bdf8")
            self.limpiar_campos()
        except Exception:
            self.lbl_status.configure(text="❌ Error al guardar la póliza", text_color="#ef4444")

    def limpiar_campos(self):
        if self.sw_repetir.get() == 0:
            for key in ["cod", "oc", "fact", "desc", "prov"]:
                self.entries[key].delete(0, "end")
            self.entries["cod"].focus()
        else:
            self.entries["uni"].focus()

        self.entries["uni"].delete(0, "end")
        self.entry_pol.delete(0, "end")
        self.actualizar_preview()

if __name__ == "__main__":
    app = AdvanHelperApp()
    app.mainloop()
