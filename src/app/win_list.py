import tkinter as tk
from tkinter import messagebox, ttk
from ..core.servicios import obtener_servicios
from ..core.trabajadores import obtener_trabajadores
from .win_form import open_win_form


def open_win_list(parent, categoria=None):
    win = tk.Toplevel(parent)
    win.title("Ofivanta - Buscar servicio")
    win.geometry("820x550")
    win.minsize(760, 500)

    frame = ttk.Frame(win, padding=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    ttk.Label(frame, text="Buscar servicio", font=("Segoe UI", 14, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
    )
    ttk.Label(frame, text="Datos ficticios para practicar. No se contratan servicios reales.").grid(
        row=1, column=0, columnspan=2, sticky="w", pady=(0, 12)
    )

    # Usamos los servicios que ya están en el catálogo del proyecto.
    servicios = obtener_servicios()
    trabajadores = obtener_trabajadores()
    nombres_servicios = {servicio["id"]: servicio["nombre"] for servicio in servicios}
    opciones = ["Todos los oficios"] + [servicio["nombre"] for servicio in servicios]

    ttk.Label(frame, text="Oficio:").grid(row=2, column=0, sticky="w", padx=(0, 8))
    filtro = ttk.Combobox(frame, values=opciones, state="readonly")
    filtro.current(0)
    filtro.grid(row=2, column=1, sticky="ew", pady=(0, 12))

    # Cada fila conserva el identificador del trabajador.
    columnas = ("nombre", "oficio", "zona", "disponibilidad")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings", selectmode="browse", height=10)
    for columna, titulo, ancho in zip(
        columnas,
        ["Trabajador", "Oficio", "Zona", "Disponibilidad"],
        [150, 240, 130, 125],
    ):
        tabla.heading(columna, text=titulo)
        tabla.column(columna, width=ancho, minwidth=90)
    tabla.grid(row=3, column=0, columnspan=2, sticky="nsew")
    barra = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    barra.grid(row=3, column=2, sticky="ns")
    tabla.configure(yscrollcommand=barra.set)

    cantidad = tk.StringVar()
    ttk.Label(frame, textvariable=cantidad).grid(row=4, column=0, columnspan=2, sticky="w", pady=6)
    detalles = tk.StringVar(value="Selecciona un trabajador para ver sus datos.")
    ttk.Label(frame, textvariable=detalles, wraplength=700).grid(
        row=5, column=0, columnspan=2, sticky="w", pady=6
    )

    def cargar_lista(event=None):
        # Limpiamos las filas antes de aplicar otro filtro.
        for fila in tabla.get_children():
            tabla.delete(fila)
        detalles.set("Selecciona un trabajador para ver sus datos.")
        for trabajador in trabajadores:
            oficio = nombres_servicios.get(trabajador["servicio_id"])
            if oficio is None:
                continue
            if filtro.get() == "Todos los oficios" or filtro.get() == oficio:
                disponible = "Disponible" if trabajador["disponible"] else "No disponible"
                tabla.insert("", "end", iid=str(trabajador["id"]), values=(
                    trabajador["nombre"], oficio, trabajador["zona"], disponible
                ))
        total = len(tabla.get_children())
        if total == 0:
            cantidad.set("No hay trabajadores para este oficio.")
        else:
            cantidad.set(f"Trabajadores encontrados: {total}")

    def obtener_seleccion():
        seleccion = tabla.selection()
        if not seleccion:
            return None
        for trabajador in trabajadores:
            if str(trabajador["id"]) == seleccion[0]:
                return trabajador
        return None

    def mostrar_detalles(event=None):
        trabajador = obtener_seleccion()
        if trabajador is None:
            return
        disponible = "Disponible" if trabajador["disponible"] else "No disponible"
        detalles.set(
            f"{trabajador['nombre']} | {nombres_servicios[trabajador['servicio_id']]}\n"
            f"Zona: {trabajador['zona']} | {disponible}\n"
            "Perfil ficticio, sin reseñas ni verificación de identidad."
        )

    def seleccionar_trabajador():
        if obtener_seleccion() is None:
            messagebox.showwarning("Aviso", "Primero selecciona un trabajador de la lista.", parent=win)
            return
        mostrar_detalles()

    def solicitar_servicio():
        trabajador = obtener_seleccion()
        if trabajador is None:
            messagebox.showwarning("Aviso", "Primero selecciona un trabajador de la lista.", parent=win)
            return
        if not trabajador["disponible"]:
            messagebox.showwarning("Aviso", "Este trabajador no está disponible. Elige otro.", parent=win)
            return
        for servicio in servicios:
            if servicio["id"] == trabajador["servicio_id"]:
                # El formulario recibe los datos y sus identificadores.
                open_win_form(win, servicio=servicio.copy(), trabajador=trabajador.copy())
                break

    botones = ttk.Frame(frame)
    botones.grid(row=6, column=0, columnspan=2, sticky="e", pady=(12, 0))
    ttk.Button(botones, text="Seleccionar trabajador", command=seleccionar_trabajador).pack(side="left", padx=4)
    ttk.Button(botones, text="Solicitar servicio", command=solicitar_servicio).pack(side="left", padx=4)
    ttk.Button(botones, text="Cerrar", command=win.destroy).pack(side="left", padx=4)

    filtro.bind("<<ComboboxSelected>>", cargar_lista)
    tabla.bind("<<TreeviewSelect>>", mostrar_detalles)
    # La pantalla de inicio podrá enviar el id de un oficio.
    for servicio in servicios:
        if categoria in (servicio["id"], servicio["nombre"]):
            filtro.set(servicio["nombre"])
            break
    cargar_lista()
    return win
