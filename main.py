import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json

# PEGA AQUÍ LA URL QUE TE DIO APPS SCRIPT EN EL PASO 1:
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbylxSqmSdiTUrYCKhllKQ7eTu9sLU8Yb27pAUBbmAFnUMRiILfH9zANmzczrAzoYCj58g/exec"

ultima_fila_guardada = None

def copiar_portapapeles(texto):
    root.clipboard_clear()
    root.clipboard_append(texto)
    root.update()

def armar_texto():
    oc = entry_oc.get().strip().upper()
    fact = entry_fact.get().strip().upper()
    desc = entry_desc.get().strip().upper()
    uni = entry_uni.get().strip().upper()
    prov = entry_prov.get().strip().upper()
    texto = f"OC MTY {oc} {desc} {uni} (FACT {fact} PROV {prov})"
    return " ".join(texto.split())

def actualizar_preview(*args):
    lbl_preview.config(text=armar_texto())

def guardar_y_copiar():
    global ultima_fila_guardada
    if not entry_desc.get().strip():
        messagebox.showwarning("Faltan datos", "Escribe al menos la Descripción.")
        return

    texto_contab = armar_texto()
    copiar_portapapeles(texto_contab) # ¡Ya quedó en tu Ctrl+V!

    datos = {
        "action": "nuevo",
        "oc": entry_oc.get(),
        "factura": entry_fact.get(),
        "descripcion": entry_desc.get(),
        "unidad": entry_uni.get(),
        "proveedor": entry_prov.get(),
        "codigo": entry_cod.get(),
        "responsable": combo_resp.get(),
        "poliza": entry_pol.get()
    }

    lbl_status.config(text="⏳ Guardando en Sheets...", fg="#f39c12")
    root.update()

    try:
        req = urllib.request.Request(
            WEBHOOK_URL, 
            data=json.dumps(datos).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            ultima_fila_guardada = res.get("row")
            lbl_status.config(text=f"✅ Copiado y Guardado (Fila {ultima_fila_guardada})", fg="#2ecc71")
            entry_pol.focus() # Pasa el cursor directo a Póliza esperando que contabilices
    except Exception as e:
        lbl_status.config(text="⚠️ Copiado (Error de red con Sheets)", fg="#e74c3c")

def guardar_poliza(event=None):
    global ultima_fila_guardada
    poliza = entry_pol.get().strip()
    if not ultima_fila_guardada or not poliza:
        return

    datos = {"action": "actualizar_poliza", "row": ultima_fila_guardada, "poliza": poliza}
    try:
        req = urllib.request.Request(
            WEBHOOK_URL, 
            data=json.dumps(datos).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        lbl_status.config(text=f"✅ Póliza {poliza} guardada en fila {ultima_fila_guardada}", fg="#3498db")
        limpiar_campos()
    except Exception as e:
        lbl_status.config(text="❌ Error al guardar póliza", fg="#e74c3c")

def limpiar_campos():
    # Si el switch de "Repetir OC/Fact/Prov" está activo, solo limpia la Unidad y Póliza
    if not var_repetir.get():
        entry_oc.delete(0, tk.END)
        entry_fact.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        entry_prov.delete(0, tk.END)
        entry_cod.delete(0, tk.END)
        entry_oc.focus()
    else:
        entry_uni.focus()
    
    entry_uni.delete(0, tk.END)
    entry_pol.delete(0, tk.END)
    actualizar_preview()

# --- INTERFAZ GRÁFICA FLOTANTE (MODO OSCURO) ---
root = tk.Tk()
root.title("Advan Helper - Tradelossa")
root.geometry("340x430")
root.configure(bg="#1e1e2e")
root.attributes("-topmost", True) # ¡SIEMPRE VISIBLE ENCIMA DE ADVAN TRUCKS!

style_lbl = {"bg": "#1e1e2e", "fg": "#cdd6f4", "font": ("Segoe UI", 9, "bold")}
style_ent = {"bg": "#313244", "fg": "#ffffff", "insertbackground": "white", "relief": "flat", "font": ("Segoe UI", 10)}

frame = tk.Frame(root, bg="#1e1e2e", padx=12, pady=8)
frame.pack(fill="both", expand=True)

# Selector Responsable y Modo Repetir
top_frame = tk.Frame(frame, bg="#1e1e2e")
top_frame.pack(fill="x", pady=2)
tk.Label(top_frame, text="Resp:", **style_lbl).pack(side="left")
combo_resp = ttk.Combobox(top_frame, values=["FF", "FS"], width=4, state="readonly")
combo_resp.set("FF")
combo_resp.pack(side="left", padx=5)

var_repetir = tk.BooleanVar()
chk_rep = tk.Checkbutton(top_frame, text="Fijar OC/Fact (Mult. Unidades)", variable=var_repetir, 
                         bg="#1e1e2e", fg="#a6adc8", selectcolor="#313244", activebackground="#1e1e2e")
chk_rep.pack(side="right")

# Campos de captura
campos = [
    ("Orden de Compra:", "oc"),
    ("Factura / Ref:", "fact"),
    ("Descripción:", "desc"),
    ("Unidad (Ej. K234):", "uni"),
    ("Proveedor:", "prov"),
    ("Código (Ej. A00-416):", "cod")
]

entries = {}
for texto, clave in campos:
    row_f = tk.Frame(frame, bg="#1e1e2e")
    row_f.pack(fill="x", pady=3)
    tk.Label(row_f, text=texto, width=16, anchor="w", **style_lbl).pack(side="left")
    ent = tk.Entry(row_f, **style_ent)
    ent.pack(side="right", fill="x", expand=True, ipady=3)
    ent.bind("<KeyRelease>", actualizar_preview)
    entries[clave] = ent

entry_oc = entries["oc"]
entry_fact = entries["fact"]
entry_desc = entries["desc"]
entry_uni = entries["uni"]
entry_prov = entries["prov"]
entry_cod = entries["cod"]

# Vista previa de Contabilización
lbl_preview = tk.Label(frame, text="OC MTY  (FACT  PROV )", bg="#181825", fg="#89b4fa", 
                       font=("Consolas", 8), wraplength=310, pady=6)
lbl_preview.pack(fill="x", pady=6)

# Botón Principal
btn_guardar = tk.Button(frame, text="📋 1. COPIAR Y GUARDAR EN SHEETS", command=guardar_y_copiar,
                        bg="#89b4fa", fg="#11111b", font=("Segoe UI", 9, "bold"), relief="flat", pady=6, cursor="hand2")
btn_guardar.pack(fill="x", pady=4)

# Sección de Póliza (Post-Contabilización)
pol_frame = tk.Frame(frame, bg="#1e1e2e")
pol_frame.pack(fill="x", pady=6)
tk.Label(pol_frame, text="N° Póliza (Enter):", **style_lbl).pack(side="left")
entry_pol = tk.Entry(pol_frame, width=10, **style_ent)
entry_pol.pack(side="left", padx=6, ipady=3)
entry_pol.bind("<Return>", guardar_poliza)

btn_pol = tk.Button(pol_frame, text="💾 2. Guardar Póliza", command=guardar_poliza,
                    bg="#a6e3a1", fg="#11111b", font=("Segoe UI", 8, "bold"), relief="flat", padx=6)
btn_pol.pack(side="right")

lbl_status = tk.Label(frame, text="Listo para capturar", bg="#1e1e2e", fg="#a6adc8", font=("Segoe UI", 8))
lbl_status.pack(pady=4)

root.mainloop()
