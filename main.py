import customtkinter as ctk
import urllib.request
import json
import sys
import os
import ctypes

# =========================================================================
# PEGA AQUÍ TU URL DE APPS SCRIPT:
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbylxSqmSdiTUrYCKhllKQ7eTu9sLU8Yb27pAUBbmAFnUMRiILfH9zANmzczrAzoYCj58g/exec"
# =========================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdvanHelperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advan Helper Pro v4 - Tradelossa")
        self.geometry("430x740")
        
         # --- CARGAR LOGO PERSONALIZADO EN VENTANA Y BARRA DE TAREAS ---
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("tradelossa.advanhelper.v4")
            ruta_base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            ruta_ico = os.path.join(ruta_base, "logo.ico")
            if os.path.exists(ruta_ico):
                self.iconbitmap(ruta_ico)
        except Exception:
            pass
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#090d16") # Fondo ultra oscuro tipo Shadcn/Linear

        self.cola_salidas = []
        self.cola_sin_poliza = []
        self.vista_actual = "unidad"
        self.modo_mini = False

        self.bind("<Enter>", self.on_mouse_enter)
        self.bind("<Leave>", self.on_mouse_leave)

        # --- 1. TOP HEADER BAR ---
        self.header = ctk.CTkFrame(self, fg_color="#111827", corner_radius=10, height=42, border_width=1, border_color="#1e293b")
        self.header.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(self.header, text="RESP:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8").pack(side="left", padx=(12, 4), pady=7)
        self.seg_resp = ctk.CTkSegmentedButton(
            self.header, values=["FS", "FF"], width=72, height=26,
            selected_color="#2563eb", selected_hover_color="#1d4ed8",
            unselected_color="#1e293b", font=("Segoe UI", 11, "bold")
        )
        self.seg_resp.set("FS")
        self.seg_resp.pack(side="left", padx=2)

        self.btn_mini = ctk.CTkButton(
            self.header, text="🔼 Mini", width=58, height=26, corner_radius=7,
            fg_color="#1e293b", hover_color="#334155", text_color="#e2e8f0",
            font=("Segoe UI", 11, "bold"), command=self.toggle_mini
        )
        self.btn_mini.pack(side="right", padx=8)

        self.sw_ghost = ctk.CTkSwitch(
            self.header, text="👻 Fantasma", font=("Segoe UI", 11, "bold"), text_color="#94a3b8",
            progress_color="#2563eb", width=40
        )
        self.sw_ghost.select()
        self.sw_ghost.pack(side="right", padx=6)

        # --- CONTENEDOR PRINCIPAL ---
        self.main_body = ctk.CTkFrame(self, fg_color="transparent")
        self.main_body.pack(fill="both", expand=True, padx=12, pady=2)

        # --- 2. APARTADO DE ENTRADA DIRECTA (VERDE ALMACÉN / INBOUND) ---
        self.entrada_card = ctk.CTkFrame(self.main_body, fg_color="#081713", corner_radius=10, border_width=1, border_color="#0d5743")
        self.entrada_card.pack(fill="x", pady=3)

        row_ent = ctk.CTkFrame(self.entrada_card, fg_color="transparent")
        row_ent.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row_ent, text="📥 ENTRADA:", width=78, anchor="w", font=("Segoe UI", 10, "bold"), text_color="#34d399").pack(side="left")

        self.ent_directa_oc = ctk.CTkEntry(
            row_ent, placeholder_text="OC (Enter registra)", height=28, corner_radius=7,
            fg_color="#040e0b", border_color="#0d5743", text_color="#f0fdf4", font=("Segoe UI", 11, "bold")
        )
        self.ent_directa_oc.pack(side="left", fill="x", expand=True, padx=(2, 6))
        self.ent_directa_oc.bind("<Return>", self.registrar_entrada_directa)

        self.btn_reg_entrada = ctk.CTkButton(
            row_ent, text="Registrar", width=84, height=28, corner_radius=7,
            fg_color="#059669", hover_color="#047857", text_color="#ffffff",
            font=("Segoe UI", 11, "bold"), command=self.registrar_entrada_directa
        )
        self.btn_reg_entrada.pack(side="right")

        # --- 3. BANNER DE UNIDAD ACTIVA (ÁMBAR FLOTA / ASSET) ---
        self.uni_card = ctk.CTkFrame(self.main_body, fg_color="#181308", corner_radius=10, border_width=1, border_color="#78350f")
        self.uni_card.pack(fill="x", pady=3)

        ctk.CTkLabel(self.uni_card, text="🚛 UNIDAD:", width=78, anchor="w", font=("Segoe UI", 11, "bold"), text_color="#fbbf24").pack(side="left", padx=(10, 2), pady=6)
        self.ent_uni = ctk.CTkEntry(
            self.uni_card, placeholder_text="Ej. P280", height=28, corner_radius=7,
            fg_color="#0d0903", border_color="#78350f", text_color="#fef3c7", font=("Segoe UI", 13, "bold")
        )
        self.ent_uni.pack(side="left", fill="x", expand=True, padx=(2, 6), pady=6)
        self.ent_uni.bind("<KeyRelease>", self.actualizar_preview)

        self.btn_nueva_uni = ctk.CTkButton(
            self.uni_card, text="Limpiar", width=72, height=28, corner_radius=7,
            fg_color="#2b1c07", hover_color="#991b1b", text_color="#fca5a5", font=("Segoe UI", 11, "bold"),
            command=self.limpiar_toda_la_unidad
        )
        self.btn_nueva_uni.pack(side="right", padx=(0, 10), pady=6)

        # --- 4. CARD DE CAPTURA (AZUL DESPACHO / CONTABILIDAD) ---
        self.form_card = ctk.CTkFrame(self.main_body, fg_color="#0c1527", corner_radius=10, border_width=1, border_color="#1e3a8a")
        self.form_card.pack(fill="x", pady=3)

        self.entries = {}

        # Fila 1: Código + Pegar + Lupita
        row_cod = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_cod.pack(fill="x", padx=10, pady=(8, 3))
        ctk.CTkLabel(row_cod, text="CÓDIGO:", width=78, anchor="w", font=("Segoe UI", 10, "bold"), text_color="#60a5fa").pack(side="left")

        self.btn_buscar_cod = ctk.CTkButton(
            row_cod, text="🔍", width=34, height=28, corner_radius=7,
            fg_color="#172554", hover_color="#1e3a8a", text_color="#93c5fd", font=("Segoe UI", 11, "bold"), command=self.buscar_ultimo_codigo
        )
        self.btn_buscar_cod.pack(side="right", padx=(4, 0))

        self.btn_pegar_cod = ctk.CTkButton(
            row_cod, text="📋 Pegar", width=78, height=28, corner_radius=7,
            fg_color="#172554", hover_color="#1e3a8a", text_color="#93c5fd", font=("Segoe UI", 11, "bold"),
            command=self.pegar_y_buscar_codigo
        )
        self.btn_pegar_cod.pack(side="right", padx=(4, 0))

        ent_cod = ctk.CTkEntry(
            row_cod, placeholder_text="Ej. AA0-168", height=28, corner_radius=7,
            fg_color="#070d18", border_color="#1e3a8a", text_color="#ffffff", font=("Segoe UI", 12, "bold")
        )
        ent_cod.pack(side="left", fill="x", expand=True)
        ent_cod.bind("<Return>", self.buscar_ultimo_codigo)
        self.entries["cod"] = ent_cod

        # Fila 2: Orden de Compra + Check Entrada + Buscar OC + Limpiar
        row_oc = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_oc.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(row_oc, text="O. COMPRA:", width=78, anchor="w", font=("Segoe UI", 10, "bold"), text_color="#93c5fd").pack(side="left")

        self.btn_otra_oc = ctk.CTkButton(
            row_oc, text="✕", width=34, height=28, corner_radius=7,
            fg_color="#172554", hover_color="#1e3a8a", text_color="#94a3b8", font=("Segoe UI", 11, "bold"),
            command=self.limpiar_oc_fact_prov
        )
        self.btn_otra_oc.pack(side="right", padx=(4, 0))

        self.btn_buscar_oc = ctk.CTkButton(
            row_oc, text="🔍", width=34, height=28, corner_radius=7,
            fg_color="#172554", hover_color="#1e3a8a", text_color="#93c5fd", font=("Segoe UI", 11, "bold"), command=self.buscar_datos_por_oc
        )
        self.btn_buscar_oc.pack(side="right", padx=(4, 0))

        self.chk_entrada = ctk.CTkCheckBox(
            row_oc, text="Entrada", width=68, height=24, checkbox_width=17, checkbox_height=17,
            corner_radius=4, fg_color="#10b981", hover_color="#059669",
            border_color="#1e3a8a", font=("Segoe UI", 10, "bold"), text_color="#34d399"
        )
        self.chk_entrada.pack(side="right", padx=(4, 2))

        ent_oc = ctk.CTkEntry(
            row_oc, placeholder_text="Ej. 88104", height=28, corner_radius=7,
            fg_color="#070d18", border_color="#1e3a8a", text_color="#ffffff", font=("Segoe UI", 12)
        )
        ent_oc.pack(side="left", fill="x", expand=True)
        ent_oc.bind("<KeyRelease>", self.actualizar_preview)
        ent_oc.bind("<Return>", self.buscar_datos_por_oc)
        self.entries["oc"] = ent_oc

        # Fila 3: Factura y Proveedor
        row_grid = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_grid.pack(fill="x", padx=10, pady=3)

        col_fact = ctk.CTkFrame(row_grid, fg_color="transparent")
        col_fact.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkLabel(col_fact, text="FACTURA:", font=("Segoe UI", 9, "bold"), text_color="#64748b").pack(anchor="w")
        ent_fact = ctk.CTkEntry(
            col_fact, placeholder_text="FAC-20411", height=28, corner_radius=7,
            fg_color="#070d18", border_color="#1e3a8a", text_color="#ffffff", font=("Segoe UI", 12)
        )
        ent_fact.pack(fill="x", pady=(2, 0))
        ent_fact.bind("<KeyRelease>", self.actualizar_preview)
        self.entries["fact"] = ent_fact

        col_prov = ctk.CTkFrame(row_grid, fg_color="transparent")
        col_prov.pack(side="right", fill="x", expand=True, padx=(4, 0))
        ctk.CTkLabel(col_prov, text="PROVEEDOR:", font=("Segoe UI", 9, "bold"), text_color="#64748b").pack(anchor="w")
        ent_prov = ctk.CTkEntry(
            col_prov, placeholder_text="Ej. 1042", height=28, corner_radius=7,
            fg_color="#070d18", border_color="#1e3a8a", text_color="#ffffff", font=("Segoe UI", 12)
        )
        ent_prov.pack(fill="x", pady=(2, 0))
        ent_prov.bind("<KeyRelease>", self.actualizar_preview)
        self.entries["prov"] = ent_prov

        # Fila 4: Descripción
        row_desc = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_desc.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(row_desc, text="DESCRIP.:", width=78, anchor="w", font=("Segoe UI", 10, "bold"), text_color="#93c5fd").pack(side="left")
        ent_desc = ctk.CTkEntry(
            row_desc, placeholder_text="Manguera, foco, filtro...", height=28, corner_radius=7,
            fg_color="#070d18", border_color="#1e3a8a", text_color="#ffffff", font=("Segoe UI", 12)
        )
        ent_desc.pack(side="left", fill="x", expand=True)
        ent_desc.bind("<KeyRelease>", self.actualizar_preview)
        ent_desc.bind("<Return>", lambda ev: self.agregar_a_cola_unidad())
        self.entries["desc"] = ent_desc

        ent_fact.bind("<Return>", lambda ev: ent_prov.focus())
        ent_prov.bind("<Return>", lambda ev: ent_desc.focus())

        # Preview Terminal Box
        self.preview_box = ctk.CTkFrame(self.form_card, fg_color="#030712", corner_radius=7, border_width=1, border_color="#172554")
        self.preview_box.pack(fill="x", padx=10, pady=4)
        self.lbl_preview = ctk.CTkLabel(
            self.preview_box, text="OC MTY (FACT PROV )", font=("Consolas", 10, "bold"),
            text_color="#38bdf8", wraplength=380
        )
        self.lbl_preview.pack(pady=4, padx=6)

        # Botón Principal
        self.btn_agregar = ctk.CTkButton(
            self.form_card, text="➕ Agregar a la Unidad",
            height=34, corner_radius=7, fg_color="#2563eb", hover_color="#1d4ed8",
            text_color="#ffffff", font=("Segoe UI", 11, "bold"),
            command=self.agregar_a_cola_unidad
        )
        self.btn_agregar.pack(fill="x", padx=10, pady=(3, 8))

        # Barra de Estado
        self.lbl_status = ctk.CTkLabel(
            self.main_body, text="Listo para capturar. Escribe o pega código para iniciar.",
            font=("Segoe UI", 10), text_color="#94a3b8", wraplength=400
        )
        self.lbl_status.pack(pady=1)

        # --- 5. SECCIÓN INFERIOR: COLA Y PENDIENTES ---
        row_cola_hdr = ctk.CTkFrame(self.main_body, fg_color="transparent")
        row_cola_hdr.pack(fill="x", padx=4, pady=(3, 2))

        self.seg_vista_cola = ctk.CTkSegmentedButton(
            row_cola_hdr, values=["📦 Unidad Actual", "⚠️ Sin Póliza"],
            height=26, selected_color="#2563eb", selected_hover_color="#1d4ed8",
            unselected_color="#1e293b", font=("Segoe UI", 10, "bold"),
            command=self.cambiar_vista_cola
        )
        self.seg_vista_cola.set("📦 Unidad Actual")
        self.seg_vista_cola.pack(side="left")

        self.btn_refrescar_sin_poliza = ctk.CTkButton(
            row_cola_hdr, text="🔄 Actualizar", width=76, height=26, corner_radius=7,
            fg_color="#1e293b", hover_color="#334155", text_color="#93c5fd",
            font=("Segoe UI", 10, "bold"), command=self.cargar_sin_poliza
        )
        self.btn_refrescar_sin_poliza.pack(side="right")

        self.scroll_cola = ctk.CTkScrollableFrame(
            self.main_body, fg_color="#111827", corner_radius=10, height=210,
            border_width=1, border_color="#1e293b"
        )
        self.scroll_cola.pack(fill="both", expand=True, pady=(0, 6))

        self.renderizar_cola()

    # --- TRANSPARENCIA Y MODO MINI ---
    def on_mouse_enter(self, event=None):
        self.attributes("-alpha", 1.0)

    def on_mouse_leave(self, event=None):
        if self.sw_ghost.get() == 1:
            self.attributes("-alpha", 0.55)

    def toggle_mini(self):
        if not self.modo_mini:
            self.main_body.pack_forget()
            self.geometry("430x64")
            self.btn_mini.configure(text="🔽 Abrir")
            self.modo_mini = True
        else:
            self.geometry("430x740")
            self.main_body.pack(fill="both", expand=True, padx=12, pady=2)
            self.btn_mini.configure(text="🔼 Mini")
            self.modo_mini = False

    # --- BÚSQUEDAS INTELIGENTES ---
    def pegar_y_buscar_codigo(self):
        try:
            clip = self.clipboard_get().strip().upper()
            if clip:
                self.entries["cod"].delete(0, "end")
                self.entries["cod"].insert(0, clip)
                self.buscar_ultimo_codigo()
        except Exception:
            self.lbl_status.configure(text="⚠️ El portapapeles está vacío", text_color="#f59e0b")

    def buscar_ultimo_codigo(self, event=None):
        cod = self.entries["cod"].get().strip().upper()
        if not cod:
            return
        self.lbl_status.configure(text=f"🔍 Buscando historial de {cod}...", text_color="#38bdf8")
        self.update()

        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps({"action": "buscar_codigo", "codigo": cod}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get("status") == "found":
                    for k, val in [("oc", res.get("oc")), ("fact", res.get("factura")),
                                   ("desc", res.get("descripcion")), ("prov", res.get("proveedor"))]:
                        self.entries[k].delete(0, "end")
                        self.entries[k].insert(0, val)
                    self.actualizar_preview()
                    self.lbl_status.configure(
                        text=f"✅ Cargado de {res.get('hoja')}. Si es otra OC en Kardex, cámbiala y da Enter en OC.",
                        text_color="#10b981"
                    )
                else:
                    self.lbl_status.configure(text="ℹ️ Código nuevo. Escribe la OC del Kardex y da Enter.", text_color="#f59e0b")
                    self.entries["oc"].focus()
        except Exception:
            self.lbl_status.configure(text="⚠️ Error de conexión al buscar código.", text_color="#ef4444")

    def buscar_datos_por_oc(self, event=None):
        oc = self.entries["oc"].get().strip().upper()
        if not oc:
            return
        self.lbl_status.configure(text=f"🔍 Buscando Factura y Proveedor de OC {oc}...", text_color="#38bdf8")
        self.update()

        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps({"action": "buscar_oc", "oc": oc}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get("status") == "found":
                    self.entries["fact"].delete(0, "end")
                    self.entries["fact"].insert(0, res.get("factura", ""))
                    self.entries["prov"].delete(0, "end")
                    self.entries["prov"].insert(0, res.get("proveedor", ""))
                    self.actualizar_preview()
                    self.lbl_status.configure(text=f"✅ ¡Factura y Proveedor de OC {oc} cargados automáticamente!", text_color="#10b981")
                    self.entries["desc"].focus()
                else:
                    self.lbl_status.configure(text=f"ℹ️ OC {oc} no registrada antes. Llena Factura y Proveedor.", text_color="#f59e0b")
                    self.entries["fact"].focus()
        except Exception:
            self.lbl_status.configure(text="⚠️ Error al consultar OC.", text_color="#ef4444")

    def limpiar_oc_fact_prov(self):
        for k in ["oc", "fact", "prov"]:
            self.entries[k].delete(0, "end")
        self.chk_entrada.deselect()
        self.actualizar_preview()
        self.entries["oc"].focus()

    def armar_texto_personalizado(self, oc, desc, uni, fact, prov):
        return " ".join(f"OC MTY {oc} {desc} {uni} (FACT {fact} PROV {prov})".split())

    def armar_texto(self):
        return self.armar_texto_personalizado(
            self.entries["oc"].get().strip().upper(),
            self.entries["desc"].get().strip().upper(),
            self.ent_uni.get().strip().upper(),
            self.entries["fact"].get().strip().upper(),
            self.entries["prov"].get().strip().upper()
        )

    def actualizar_preview(self, event=None):
        self.lbl_preview.configure(text=self.armar_texto())

    # --- LÓGICA DE AUTO-EMPALME (SUMA DE CÓDIGOS Y SUMA DE DESCRIPCIONES) ---
    def agregar_a_cola_unidad(self):
        uni = self.ent_uni.get().strip().upper()
        cod = self.entries["cod"].get().strip().upper()
        oc = self.entries["oc"].get().strip().upper()
        fact = self.entries["fact"].get().strip().upper()
        desc = self.entries["desc"].get().strip().upper()
        prov = self.entries["prov"].get().strip().upper()
        entrada_oc = bool(self.chk_entrada.get() == 1 and oc != "")

        if not uni or not desc:
            if entrada_oc and not uni and not desc:
                self.enviar_registro_entrada(oc)
                self.chk_entrada.deselect()
                self.entries["oc"].delete(0, "end")
                return
            self.lbl_status.configure(text="⚠️ Falta escribir la Unidad o la Descripción", text_color="#f59e0b")
            return

        grupo_existente = None
        if oc != "":
            for item in self.cola_salidas:
                if item["uni"] == uni and item["oc"] == oc and item["fact"] == fact:
                    grupo_existente = item
                    break

        if grupo_existente:
            # 1. Sumar el nuevo código con " / "
            codigos_actuales = [c.strip() for c in grupo_existente["cod"].split("/") if c.strip()]
            if cod and cod not in codigos_actuales:
                codigos_actuales.append(cod)
            nuevo_cod_str = " / ".join(codigos_actuales)

            # 2. Sumar la nueva descripción si no estaba repetida (ej. "MANGUERA FOCO FILTRO")
            palabras_desc_actual = grupo_existente["desc"].split()
            for palabra in desc.split():
                if palabra not in palabras_desc_actual:
                    palabras_desc_actual.append(palabra)
            nueva_desc_str = " ".join(palabras_desc_actual)

            # 3. Re-armar el texto OC MTY con las descripciones sumadas
            nueva_contab_str = self.armar_texto_personalizado(oc, nueva_desc_str, uni, fact, prov)

            grupo_existente["cod"] = nuevo_cod_str
            grupo_existente["desc"] = nueva_desc_str
            grupo_existente["contab"] = nueva_contab_str
            if entrada_oc:
                grupo_existente["entrada"] = True

            self.lbl_status.configure(text=f"⏳ Empalmando {cod} y sumando descripción en OC {oc}...", text_color="#f59e0b")
            self.update()

            try:
                req = urllib.request.Request(
                    WEBHOOK_URL,
                    data=json.dumps({
                        "action": "empalmar_codigo",
                        "row": grupo_existente["row"],
                        "codigo": nuevo_cod_str,
                        "descripcion": nueva_desc_str,
                        "contab": nueva_contab_str,
                        "oc": oc,
                        "responsable": self.seg_resp.get(),
                        "entrada_oc": entrada_oc
                    }).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req)
                self.clipboard_clear()
                self.clipboard_append(nueva_contab_str)
                msg_extra = " + 📥 Entrada OC" if entrada_oc else ""
                self.lbl_status.configure(
                    text=f"🔗 ¡Empalmado en Fila {grupo_existente['row']}{msg_extra}! ({nueva_desc_str})",
                    text_color="#10b981"
                )
            except Exception:
                self.lbl_status.configure(text="❌ Error de red al actualizar el empalme en Sheets", text_color="#ef4444")
        else:
            # Crear un grupo nuevo
            contab = self.armar_texto()
            self.clipboard_clear()
            self.clipboard_append(contab)
            self.lbl_status.configure(text="⏳ Creando grupo en Google Sheets...", text_color="#f59e0b")
            self.update()

            datos = {
                "action": "nuevo", "oc": oc, "factura": fact, "descripcion": desc,
                "unidad": uni, "proveedor": prov, "codigo": cod,
                "responsable": self.seg_resp.get(), "poliza": "",
                "entrada_oc": entrada_oc
            }
            try:
                req = urllib.request.Request(
                    WEBHOOK_URL, data=json.dumps(datos).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req) as resp:
                    res = json.loads(resp.read().decode('utf-8'))
                    fila_nueva = res.get("row")
                    self.cola_salidas.append({
                        "row": fila_nueva, "uni": uni, "oc": oc, "fact": fact,
                        "desc": desc, "prov": prov, "cod": cod, "contab": contab, "pol": "",
                        "entrada": entrada_oc
                    })
                    msg_extra = " + 📥 Entrada OC registrada" if entrada_oc else ""
                    self.lbl_status.configure(text=f"✅ Grupo #{len(self.cola_salidas)} creado (Fila {fila_nueva}){msg_extra}", text_color="#10b981")
            except Exception:
                self.lbl_status.configure(text="❌ Error de red con Sheets", text_color="#ef4444")

        self.renderizar_cola()
        for k in ["cod", "oc", "fact", "desc", "prov"]:
            self.entries[k].delete(0, "end")
        self.chk_entrada.deselect()
        self.actualizar_preview()
        self.entries["cod"].focus()

    def renderizar_cola(self):
        for widget in self.scroll_cola.winfo_children():
            widget.destroy()

        if not self.cola_salidas:
            ctk.CTkLabel(
                self.scroll_cola,
                text="Aún no hay grupos para esta unidad.\nRevisa tus códigos arriba y presiona '➕ AGREGAR A LA UNIDAD'.",
                font=("Segoe UI", 11), text_color="#6b7280"
            ).pack(pady=35)
            return

        for idx, item in enumerate(self.cola_salidas):
            borde_col = "#059669" if item["pol"] else "#1e3a8a"
            card = ctk.CTkFrame(self.scroll_cola, fg_color="#070d18", corner_radius=8, border_width=1, border_color=borde_col)
            card.pack(fill="x", pady=3, padx=2)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=8, pady=(5, 2))
            
            badge_ent = " 📥" if item.get("entrada") else ""
            titulo = f"#{idx+1} · Fila {item['row']} | OC: {item['oc']}{badge_ent} | {item['desc']}"
            ctk.CTkLabel(top, text=titulo, font=("Segoe UI", 10, "bold"), text_color="#38bdf8", anchor="w").pack(side="left", fill="x")
            
            lbl_cods = ctk.CTkLabel(card, text=f"🏷️ {item['cod']}", font=("Consolas", 9, "bold"), text_color="#94a3b8", anchor="w")
            lbl_cods.pack(fill="x", padx=8, pady=(0, 3))

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=8, pady=(2, 5))

            btn_cp = ctk.CTkButton(
                bot, text="📋 Copiar", width=85, height=26, corner_radius=6,
                fg_color="#1e293b", hover_color="#2563eb", text_color="#f8fafc", font=("Segoe UI", 10, "bold"),
                command=lambda it=item: self.copiar_item_cola(it)
            )
            btn_cp.pack(side="left")

            ent_p = ctk.CTkEntry(
                bot, placeholder_text="N° Póliza", width=85, height=26, corner_radius=6,
                fg_color="#070b12", border_color="#1e293b", text_color="#ffffff", font=("Segoe UI", 11, "bold")
            )
            if item["pol"]:
                ent_p.insert(0, item["pol"])
            ent_p.pack(side="left", padx=6)

            btn_del = ctk.CTkButton(
                bot, text="🗑️", width=28, height=26, corner_radius=6,
                fg_color="#1e293b", hover_color="#ef4444", text_color="#f87171", font=("Segoe UI", 10),
                command=lambda it=item: self.eliminar_fila_remota(it)
            )
            btn_del.pack(side="right", padx=(4, 0))

            btn_ok = ctk.CTkButton(
                bot, text="💾 Guardar" if not item["pol"] else f"✅ Pól: {item['pol']}",
                width=90, height=26, corner_radius=6,
                fg_color="#10b981" if not item["pol"] else "#065f46",
                text_color="#ffffff", font=("Segoe UI", 10, "bold"),
                command=lambda it=item, ep=ent_p: self.guardar_poliza_item(it, ep.get())
            )
            btn_ok.pack(side="right")
            ent_p.bind("<Return>", lambda ev, it=item, ep=ent_p: self.guardar_poliza_item(it, ep.get()))

    def copiar_item_cola(self, item):
        self.clipboard_clear()
        self.clipboard_append(item["contab"])
        self.update()
        self.lbl_status.configure(text=f"📋 Copiado al Ctrl+V: {item['contab']}", text_color="#38bdf8")

    def eliminar_fila_remota(self, item):
        fila = item.get("row")
        if not fila:
            return
        self.lbl_status.configure(text=f"⏳ Eliminando fila {fila} en Google Sheets...", text_color="#38bdf8")
        self.update()
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps({"action": "eliminar_fila", "row": fila}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get("status") == "ok":
                    if item in self.cola_salidas:
                        self.cola_salidas.remove(item)
                    if item in self.cola_sin_poliza:
                        self.cola_sin_poliza.remove(item)
                    for it in self.cola_salidas:
                        if it.get("row", 0) > fila:
                            it["row"] -= 1
                    for it in self.cola_sin_poliza:
                        if it.get("row", 0) > fila:
                            it["row"] -= 1
                    if self.vista_actual == "sin_poliza":
                        self.renderizar_cola_sin_poliza()
                    else:
                        self.renderizar_cola()
                    self.lbl_status.configure(text=f"🗑️ Fila {fila} eliminada en Google Sheets", text_color="#10b981")
                else:
                    self.lbl_status.configure(text=f"⚠️ No se pudo eliminar fila {fila} en Sheets", text_color="#f59e0b")
        except Exception:
            self.lbl_status.configure(text=f"❌ Error al eliminar fila {fila}", text_color="#ef4444")

    def guardar_poliza_item(self, item, poliza_txt):
        pol = poliza_txt.strip()
        if not pol:
            return
        self.lbl_status.configure(text=f"⏳ Guardando póliza {pol} en Fila {item['row']}...", text_color="#38bdf8")
        self.update()
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps({"action": "actualizar_poliza", "row": item["row"], "poliza": pol}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
            item["pol"] = pol
            if self.vista_actual == "sin_poliza":
                self.renderizar_cola_sin_poliza()
            else:
                self.renderizar_cola()
            self.lbl_status.configure(text=f"✅ Póliza {pol} guardada en Fila {item['row']}", text_color="#10b981")
        except Exception:
            self.lbl_status.configure(text="❌ Error al guardar póliza", text_color="#ef4444")

    def cambiar_vista_cola(self, seleccion):
        if seleccion == "⚠️ Sin Póliza":
            self.seg_vista_cola.configure(selected_color="#d97706", selected_hover_color="#b45309")
            self.vista_actual = "sin_poliza"
            self.cargar_sin_poliza()
        else:
            self.seg_vista_cola.configure(selected_color="#2563eb", selected_hover_color="#1d4ed8")
            self.vista_actual = "unidad"
            self.renderizar_cola()

    def cargar_sin_poliza(self):
        self.lbl_status.configure(text="⏳ Buscando salidas sin póliza en Google Sheets...", text_color="#38bdf8")
        self.update()
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps({"action": "obtener_sin_poliza"}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get("status") == "ok":
                    self.cola_sin_poliza = res.get("pendientes", [])
                    if self.vista_actual == "sin_poliza":
                        self.renderizar_cola_sin_poliza()
                    if self.cola_sin_poliza:
                        self.lbl_status.configure(
                            text=f"⚠️ {len(self.cola_sin_poliza)} salida(s) pendientes de póliza encontradas.",
                            text_color="#f59e0b"
                        )
                    else:
                        self.lbl_status.configure(
                            text="🎉 ¡Al día! No hay salidas pendientes de póliza.",
                            text_color="#10b981"
                        )
                else:
                    self.lbl_status.configure(text="⚠️ Error al consultar pendientes de póliza.", text_color="#f59e0b")
        except Exception:
            self.lbl_status.configure(text="❌ Error de red al consultar salidas pendientes.", text_color="#ef4444")

    def renderizar_cola_sin_poliza(self):
        for widget in self.scroll_cola.winfo_children():
            widget.destroy()

        if not self.cola_sin_poliza:
            ctk.CTkLabel(
                self.scroll_cola,
                text="🎉 ¡Al día! No hay salidas pendientes de póliza en este mes.\nUsa '🔄 Actualizar' para volver a checar.",
                font=("Segoe UI", 11), text_color="#10b981"
            ).pack(pady=35)
            return

        for idx, item in enumerate(self.cola_sin_poliza):
            borde_col = "#10b981" if item.get("pol") else "#f43f5e"
            card = ctk.CTkFrame(self.scroll_cola, fg_color="#0b1120", corner_radius=8, border_width=1, border_color=borde_col)
            card.pack(fill="x", pady=3, padx=2)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=8, pady=(5, 2))

            uni_txt = item.get("uni", "S/U")
            titulo = f"Fila {item['row']} | 🚛 {uni_txt} | OC: {item['oc']}"
            ctk.CTkLabel(top, text=titulo, font=("Segoe UI", 10, "bold"), text_color="#f43f5e" if not item.get("pol") else "#10b981", anchor="w").pack(side="left")

            resp_txt = f"Resp: {item.get('resp', '-')}"
            ctk.CTkLabel(top, text=resp_txt, font=("Segoe UI", 9, "bold"), text_color="#64748b").pack(side="right")

            lbl_desc = ctk.CTkLabel(card, text=f"📦 {item['desc']}", font=("Segoe UI", 10, "bold"), text_color="#e2e8f0", anchor="w")
            lbl_desc.pack(fill="x", padx=8, pady=(0, 2))

            if item.get("cod"):
                lbl_cods = ctk.CTkLabel(card, text=f"🏷️ {item['cod']}", font=("Consolas", 9), text_color="#94a3b8", anchor="w")
                lbl_cods.pack(fill="x", padx=8, pady=(0, 3))

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=8, pady=(2, 5))

            btn_cp = ctk.CTkButton(
                bot, text="📋 Copiar", width=85, height=26, corner_radius=6,
                fg_color="#1e293b", hover_color="#2563eb", text_color="#f8fafc", font=("Segoe UI", 10, "bold"),
                command=lambda it=item: self.copiar_item_cola(it)
            )
            btn_cp.pack(side="left")

            ent_p = ctk.CTkEntry(
                bot, placeholder_text="N° Póliza", width=85, height=26, corner_radius=6,
                fg_color="#070b12", border_color="#1e293b", text_color="#ffffff", font=("Segoe UI", 11, "bold")
            )
            if item.get("pol"):
                ent_p.insert(0, item["pol"])
            ent_p.pack(side="left", padx=6)

            btn_del = ctk.CTkButton(
                bot, text="🗑️", width=28, height=26, corner_radius=6,
                fg_color="#1e293b", hover_color="#ef4444", text_color="#f87171", font=("Segoe UI", 10),
                command=lambda it=item: self.eliminar_fila_remota(it)
            )
            btn_del.pack(side="right", padx=(4, 0))

            btn_ok = ctk.CTkButton(
                bot, text="💾 Guardar" if not item.get("pol") else f"✅ Pól: {item['pol']}",
                width=90, height=26, corner_radius=6,
                fg_color="#10b981" if not item.get("pol") else "#065f46",
                text_color="#ffffff", font=("Segoe UI", 10, "bold"),
                command=lambda it=item, ep=ent_p: self.guardar_poliza_item(it, ep.get())
            )
            btn_ok.pack(side="right")
            ent_p.bind("<Return>", lambda ev, it=item, ep=ent_p: self.guardar_poliza_item(it, ep.get()))

    def registrar_entrada_directa(self, event=None):
        oc = self.ent_directa_oc.get().strip().upper()
        if not oc:
            oc = self.entries["oc"].get().strip().upper()
        if not oc:
            self.lbl_status.configure(text="⚠️ Escribe la Orden de Compra para registrar su entrada", text_color="#f59e0b")
            self.ent_directa_oc.focus()
            return
        self.enviar_registro_entrada(oc)
        self.ent_directa_oc.delete(0, "end")
        self.ent_directa_oc.focus()

    def enviar_registro_entrada(self, oc_raw):
        import re
        ocs = [item.strip() for item in re.split(r'[,/]+', oc_raw) if item.strip()]
        if not ocs:
            return

        resp = self.seg_resp.get()
        self.lbl_status.configure(text=f"⏳ Registrando entrada de OC {', '.join(ocs)}...", text_color="#38bdf8")
        self.update()

        exitos = []
        errores = []
        for oc in ocs:
            try:
                req = urllib.request.Request(
                    WEBHOOK_URL,
                    data=json.dumps({
                        "action": "registrar_entrada",
                        "oc": oc,
                        "responsable": resp
                    }).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req) as response:
                    res = json.loads(response.read().decode('utf-8'))
                    if res.get("status") == "ok":
                        exitos.append(oc)
                    else:
                        errores.append(oc)
            except Exception:
                errores.append(oc)

        if exitos and not errores:
            msg = f"✅ Entrada registrada en reporte: OC {', '.join(exitos)} ({resp})"
            self.lbl_status.configure(text=msg, text_color="#10b981")
        elif exitos and errores:
            self.lbl_status.configure(
                text=f"⚠️ Guardadas: {', '.join(exitos)} | Error en: {', '.join(errores)}",
                text_color="#f59e0b"
            )
        else:
            self.lbl_status.configure(
                text="❌ Error al registrar entrada. Verifica conexión o Apps Script.",
                text_color="#ef4444"
            )

    def limpiar_toda_la_unidad(self):
        sin_pol = sum(1 for it in self.cola_salidas if not it.get("pol"))
        self.cola_salidas = []
        self.ent_uni.delete(0, "end")
        for k in ["cod", "oc", "fact", "desc", "prov"]:
            self.entries[k].delete(0, "end")
        self.chk_entrada.deselect()
        if self.vista_actual == "sin_poliza":
            self.renderizar_cola_sin_poliza()
        else:
            self.renderizar_cola()
        self.actualizar_preview()
        if sin_pol > 0:
            self.lbl_status.configure(
                text=f"🧹 Nueva Unidad. ({sin_pol} salida(s) pendientes en '⚠️ Sin Póliza')",
                text_color="#f59e0b"
            )
        else:
            self.lbl_status.configure(text="🧹 Cola limpia. Ingresa la nueva Unidad.", text_color="#38bdf8")
        self.ent_uni.focus()

if __name__ == "__main__":
    app = AdvanHelperApp()
    app.mainloop()
