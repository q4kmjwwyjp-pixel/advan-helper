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
        self.geometry("430x700")
        
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
        self.modo_mini = False

        self.bind("<Enter>", self.on_mouse_enter)
        self.bind("<Leave>", self.on_mouse_leave)

        # --- 1. TOP HEADER BAR ---
        self.header = ctk.CTkFrame(self, fg_color="#111827", corner_radius=12, height=44, border_width=1, border_color="#1f2937")
        self.header.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(self.header, text="RESP:", font=("Segoe UI", 11, "bold"), text_color="#9ca3af").pack(side="left", padx=(12, 4), pady=8)
        self.seg_resp = ctk.CTkSegmentedButton(
            self.header, values=["FS", "FF"], width=72, height=26,
            selected_color="#2563eb", selected_hover_color="#1d4ed8",
            unselected_color="#1f2937", font=("Segoe UI", 11, "bold")
        )
        self.seg_resp.set("FS")
        self.seg_resp.pack(side="left", padx=2)

        self.btn_mini = ctk.CTkButton(
            self.header, text="🔼 Mini", width=58, height=26, corner_radius=8,
            fg_color="#1f2937", hover_color="#374151", text_color="#e5e7eb",
            font=("Segoe UI", 11, "bold"), command=self.toggle_mini
        )
        self.btn_mini.pack(side="right", padx=8)

        self.sw_ghost = ctk.CTkSwitch(
            self.header, text="👻 Fantasma", font=("Segoe UI", 11, "bold"), text_color="#9ca3af",
            progress_color="#6366f1", width=40
        )
        self.sw_ghost.select()
        self.sw_ghost.pack(side="right", padx=6)

        # --- CONTENEDOR PRINCIPAL ---
        self.main_body = ctk.CTkFrame(self, fg_color="transparent")
        self.main_body.pack(fill="both", expand=True, padx=12, pady=2)

        # --- 2. BANNER DE UNIDAD ACTIVA (DESTACADO) ---
        self.uni_card = ctk.CTkFrame(self.main_body, fg_color="#0f172a", corner_radius=12, border_width=1, border_color="#0284c7")
        self.uni_card.pack(fill="x", pady=4)

        ctk.CTkLabel(self.uni_card, text="🚛 UNIDAD:", font=("Segoe UI", 12, "bold"), text_color="#38bdf8").pack(side="left", padx=(12, 6), pady=8)
        self.ent_uni = ctk.CTkEntry(
            self.uni_card, placeholder_text="Ej. P280", width=110, height=30, corner_radius=8,
            fg_color="#090d16", border_color="#0284c7", text_color="#ffffff", font=("Segoe UI", 14, "bold")
        )
        self.ent_uni.pack(side="left", pady=8)
        self.ent_uni.bind("<KeyRelease>", self.actualizar_preview)

        self.btn_nueva_uni = ctk.CTkButton(
            self.uni_card, text="🧹 Nueva Unidad", width=115, height=28, corner_radius=8,
            fg_color="#be123c", hover_color="#9f1239", font=("Segoe UI", 11, "bold"),
            command=self.limpiar_toda_la_unidad
        )
        self.btn_nueva_uni.pack(side="right", padx=10, pady=8)

        # --- 3. CARD DE CAPTURA (ESTILO DASHBOARD GRID) ---
        self.form_card = ctk.CTkFrame(self.main_body, fg_color="#111827", corner_radius=12, border_width=1, border_color="#1f2937")
        self.form_card.pack(fill="x", pady=4)

        self.entries = {}

        # Fila 1: Código + Pegar Ctrl+C + Lupita
        row_cod = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_cod.pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkLabel(row_cod, text="CÓDIGO:", width=75, anchor="w", font=("Segoe UI", 11, "bold"), text_color="#38bdf8").pack(side="left")

        self.btn_buscar_cod = ctk.CTkButton(
            row_cod, text="🔍", width=34, height=28, corner_radius=8,
            fg_color="#2563eb", hover_color="#1d4ed8", font=("Segoe UI", 12, "bold"), command=self.buscar_ultimo_codigo
        )
        self.btn_buscar_cod.pack(side="right", padx=(4, 0))

        self.btn_pegar_cod = ctk.CTkButton(
            row_cod, text="📥 Pegar Ctrl+C", width=102, height=28, corner_radius=8,
            fg_color="#7c3aed", hover_color="#6d28d9", font=("Segoe UI", 11, "bold"),
            command=self.pegar_y_buscar_codigo
        )
        self.btn_pegar_cod.pack(side="right", padx=(4, 0))

        ent_cod = ctk.CTkEntry(
            row_cod, placeholder_text="Ej. AA0-168", height=28, corner_radius=8,
            fg_color="#090d16", border_color="#3b82f6", font=("Segoe UI", 12, "bold")
        )
        ent_cod.pack(side="left", fill="x", expand=True)
        ent_cod.bind("<Return>", self.buscar_ultimo_codigo)
        self.entries["cod"] = ent_cod

        # Fila 2: Orden de Compra + Check Entrada + Buscar OC + Limpiar
        row_oc = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_oc.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row_oc, text="O. COMPRA:", width=75, anchor="w", font=("Segoe UI", 11, "bold"), text_color="#d1d5db").pack(side="left")

        self.btn_otra_oc = ctk.CTkButton(
            row_oc, text="✖ Limpiar", width=60, height=28, corner_radius=8,
            fg_color="#374151", hover_color="#4b5563", font=("Segoe UI", 10, "bold"),
            command=self.limpiar_oc_fact_prov
        )
        self.btn_otra_oc.pack(side="right", padx=(4, 0))

        self.btn_buscar_oc = ctk.CTkButton(
            row_oc, text="🔍 OC", width=48, height=28, corner_radius=8,
            fg_color="#0284c7", hover_color="#0369a1", font=("Segoe UI", 11, "bold"), command=self.buscar_datos_por_oc
        )
        self.btn_buscar_oc.pack(side="right", padx=(4, 0))

        self.chk_entrada = ctk.CTkCheckBox(
            row_oc, text="Entrada", width=68, height=24, checkbox_width=18, checkbox_height=18,
            corner_radius=5, fg_color="#10b981", hover_color="#059669",
            border_color="#10b981", font=("Segoe UI", 11, "bold"), text_color="#10b981"
        )
        self.chk_entrada.pack(side="right", padx=(4, 2))

        ent_oc = ctk.CTkEntry(
            row_oc, placeholder_text="Ej. 88104", height=28, corner_radius=8,
            fg_color="#090d16", border_color="#374151", font=("Segoe UI", 12)
        )
        ent_oc.pack(side="left", fill="x", expand=True)
        ent_oc.bind("<KeyRelease>", self.actualizar_preview)
        ent_oc.bind("<Return>", self.buscar_datos_por_oc)
        self.entries["oc"] = ent_oc

        # Fila 3 (GRID 2 COLUMNAS): Factura y Proveedor lado a lado
        row_grid = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_grid.pack(fill="x", padx=10, pady=4)

        # Columna Izquierda: Factura
        col_fact = ctk.CTkFrame(row_grid, fg_color="transparent")
        col_fact.pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkLabel(col_fact, text="FACTURA / REF:", font=("Segoe UI", 10, "bold"), text_color="#9ca3af").pack(anchor="w")
        ent_fact = ctk.CTkEntry(
            col_fact, placeholder_text="FAC-20411", height=28, corner_radius=8,
            fg_color="#090d16", border_color="#374151", font=("Segoe UI", 12)
        )
        ent_fact.pack(fill="x", pady=(2, 0))
        ent_fact.bind("<KeyRelease>", self.actualizar_preview)
        self.entries["fact"] = ent_fact

        # Columna Derecha: Proveedor
        col_prov = ctk.CTkFrame(row_grid, fg_color="transparent")
        col_prov.pack(side="right", fill="x", expand=True, padx=(4, 0))
        ctk.CTkLabel(col_prov, text="PROVEEDOR:", font=("Segoe UI", 10, "bold"), text_color="#9ca3af").pack(anchor="w")
        ent_prov = ctk.CTkEntry(
            col_prov, placeholder_text="Ej. 1042", height=28, corner_radius=8,
            fg_color="#090d16", border_color="#374151", font=("Segoe UI", 12)
        )
        ent_prov.pack(fill="x", pady=(2, 0))
        ent_prov.bind("<KeyRelease>", self.actualizar_preview)
        self.entries["prov"] = ent_prov

        # Fila 4: Descripción corta
        row_desc = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row_desc.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row_desc, text="DESCRIP.:", width=75, anchor="w", font=("Segoe UI", 11, "bold"), text_color="#d1d5db").pack(side="left")
        ent_desc = ctk.CTkEntry(
            row_desc, placeholder_text="Ej. MANGUERA (Enter agrega a la unidad)", height=28, corner_radius=8,
            fg_color="#090d16", border_color="#374151", font=("Segoe UI", 12)
        )
        ent_desc.pack(side="left", fill="x", expand=True)
        ent_desc.bind("<KeyRelease>", self.actualizar_preview)
        ent_desc.bind("<Return>", lambda ev: self.agregar_a_cola_unidad())
        self.entries["desc"] = ent_desc

        # Navegación Enter entre Factura -> Proveedor -> Descripción
        ent_fact.bind("<Return>", lambda ev: ent_prov.focus())
        ent_prov.bind("<Return>", lambda ev: ent_desc.focus())

        # Caja de Vista Previa tipo Terminal
        self.preview_box = ctk.CTkFrame(self.form_card, fg_color="#090d16", corner_radius=8, border_width=1, border_color="#1e293b")
        self.preview_box.pack(fill="x", padx=10, pady=4)
        self.lbl_preview = ctk.CTkLabel(
            self.preview_box, text="OC MTY (FACT PROV )", font=("Consolas", 10, "bold"),
            text_color="#38bdf8", wraplength=380
        )
        self.lbl_preview.pack(pady=5, padx=6)

        # Botón Principal Esmeralda
        self.btn_agregar = ctk.CTkButton(
            self.form_card, text="➕ AGREGAR A LA UNIDAD (AUTO-EMPALMA MISMA OC)",
            height=36, corner_radius=8, fg_color="#10b981", hover_color="#059669",
            text_color="#052e16", font=("Segoe UI", 11, "bold"),
            command=self.agregar_a_cola_unidad
        )
        self.btn_agregar.pack(fill="x", padx=10, pady=(4, 10))

        # Barra de Estado
        self.lbl_status = ctk.CTkLabel(
            self.main_body, text="✨ Pon la Unidad, copia el código en Advan y dale a '📥 Pegar Ctrl+C'",
            font=("Segoe UI", 11, "bold"), text_color="#9ca3af", wraplength=400
        )
        self.lbl_status.pack(pady=2)

        # --- 4. SECCIÓN INFERIOR: COLA DE SALIDAS ARMADAS ---
        ctk.CTkLabel(
            self.main_body, text="📦 SALIDAS ARMADAS DE LA UNIDAD (Copia y registra Póliza):",
            font=("Segoe UI", 11, "bold"), text_color="#e5e7eb"
        ).pack(anchor="w", padx=4, pady=(4, 2))

        self.scroll_cola = ctk.CTkScrollableFrame(
            self.main_body, fg_color="#111827", corner_radius=12, height=210,
            border_width=1, border_color="#1f2937"
        )
        self.scroll_cola.pack(fill="both", expand=True, pady=(0, 8))

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
            self.geometry("430x700")
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
            borde_col = "#10b981" if item["pol"] else "#1f2937"
            card = ctk.CTkFrame(self.scroll_cola, fg_color="#090d16", corner_radius=10, border_width=1, border_color=borde_col)
            card.pack(fill="x", pady=4, padx=4)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=8, pady=(6, 2))
            
            badge_ent = " 📥" if item.get("entrada") else ""
            titulo = f"#{idx+1} · Fila {item['row']} | OC: {item['oc']}{badge_ent} | {item['desc']}"
            ctk.CTkLabel(top, text=titulo, font=("Segoe UI", 11, "bold"), text_color="#38bdf8", anchor="w").pack(side="left", fill="x")
            
            lbl_cods = ctk.CTkLabel(card, text=f"🏷️ {item['cod']}", font=("Consolas", 10, "bold"), text_color="#d1d5db", anchor="w")
            lbl_cods.pack(fill="x", padx=8, pady=(0, 4))

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=8, pady=(2, 6))

            btn_cp = ctk.CTkButton(
                bot, text="📋 Copiar OC MTY", width=118, height=26, corner_radius=6,
                fg_color="#2563eb", hover_color="#1d4ed8", font=("Segoe UI", 10, "bold"),
                command=lambda it=item: self.copiar_item_cola(it)
            )
            btn_cp.pack(side="left")

            ent_p = ctk.CTkEntry(
                bot, placeholder_text="N° Póliza", width=85, height=26, corner_radius=6,
                fg_color="#111827", border_color="#10b981", font=("Segoe UI", 11, "bold")
            )
            if item["pol"]:
                ent_p.insert(0, item["pol"])
            ent_p.pack(side="left", padx=6)

            btn_ok = ctk.CTkButton(
                bot, text="💾 Guardar" if not item["pol"] else f"✅ Pól: {item['pol']}",
                width=95, height=26, corner_radius=6,
                fg_color="#10b981" if not item["pol"] else "#059669",
                text_color="#052e16" if not item["pol"] else "#ffffff",
                font=("Segoe UI", 10, "bold"),
                command=lambda it=item, ep=ent_p: self.guardar_poliza_item(it, ep.get())
            )
            btn_ok.pack(side="right")
            ent_p.bind("<Return>", lambda ev, it=item, ep=ent_p: self.guardar_poliza_item(it, ep.get()))

    def copiar_item_cola(self, item):
        self.clipboard_clear()
        self.clipboard_append(item["contab"])
        self.update()
        self.lbl_status.configure(text=f"📋 Copiado al Ctrl+V: {item['contab']}", text_color="#38bdf8")

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
            self.renderizar_cola()
            self.lbl_status.configure(text=f"✅ Póliza {pol} guardada en Fila {item['row']}", text_color="#10b981")
        except Exception:
            self.lbl_status.configure(text="❌ Error al guardar póliza", text_color="#ef4444")

    def limpiar_toda_la_unidad(self):
        self.cola_salidas = []
        self.ent_uni.delete(0, "end")
        for k in ["cod", "oc", "fact", "desc", "prov"]:
            self.entries[k].delete(0, "end")
        self.chk_entrada.deselect()
        self.renderizar_cola()
        self.actualizar_preview()
        self.lbl_status.configure(text="🧹 Cola limpia. Ingresa la nueva Unidad.", text_color="#38bdf8")
        self.ent_uni.focus()

if __name__ == "__main__":
    app = AdvanHelperApp()
    app.mainloop()
