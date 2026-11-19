"""Ventana 3: buscar un oficio y elegir un trabajador."""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from ..core.servicios import obtener_servicios
from ..core.trabajadores import obtener_trabajadores
from ..core import datos
from .win_form import open_win_form
from .ui import crear_ventana, encabezado, tarjeta, etiqueta, aviso_error, notificar_cambio, GRIS, VERDE, TEXTO


def open_win_list(parent, categoria=None):
    win = crear_ventana(parent, "Buscar servicio", 1100, 740)
    win.minsize(980, 640)
    frame = ttk.Frame(win, padding=22)
    frame.pack(fill="both", expand=True)
    encabezado(frame, "Buscar servicio", "1. Elige un oficio    2. Toca un trabajador    3. Solicita el servicio")
    filtros = ttk.Frame(frame)
    filtros.pack(fill="x", pady=(0, 10))
    ttk.Label(filtros, text="Oficio").grid(row=0, column=0, sticky="w", pady=(0, 5))
    filtro = ttk.Combobox(filtros, state="readonly", width=22)
    filtro.grid(row=1, column=0, sticky="ew", padx=(0, 12))
    ttk.Label(filtros, text="Nombre, oficio o zona").grid(row=0, column=1, sticky="w", pady=(0, 5))
    busqueda = tk.StringVar()
    entrada = ttk.Entry(filtros, textvariable=busqueda)
    entrada.grid(row=1, column=1, sticky="ew", padx=(0, 12))
    filtros.columnconfigure(1, weight=1)
    solo_disponibles = tk.BooleanVar(value=False)
    ttk.Checkbutton(filtros, text="Solo disponibles", variable=solo_disponibles,
                    command=lambda: cargar_lista()).grid(row=1, column=2, sticky="w")
    opciones = ttk.Frame(frame)
    def mas_filtros():
        if opciones.winfo_manager():
            opciones.pack_forget()
            mas_btn.configure(text="Más filtros")
        else:
            opciones.pack(fill="x",pady=(0,14),before=cuerpo)
            mas_btn.configure(text="Menos filtros")
    mas_btn=ttk.Button(filtros,text="Más filtros",command=mas_filtros)
    mas_btn.grid(row=0,column=2,sticky="e",pady=(0,5))
    favoritos = tk.BooleanVar(value=False)
    ttk.Checkbutton(opciones, text="Mis favoritos", variable=favoritos,
                    command=lambda: cargar_lista()).pack(side="left")
    ttk.Label(opciones, text="Ordenar por", style="Small.TLabel").pack(side="left", padx=(20, 8))
    orden = ttk.Combobox(opciones, state="readonly", values=["Nombre", "Disponibilidad"], width=16)
    orden.current(0)
    orden.pack(side="left")
    ttk.Button(opciones, text="Restablecer filtros", command=lambda: restablecer()).pack(side="right")

    botones = ttk.Frame(frame)
    botones.pack(side="bottom", fill="x")
    cantidad = ttk.Label(frame, text="", style="Small.TLabel")
    cantidad.pack(side="bottom", anchor="w", pady=12)
    cuerpo = ttk.Frame(frame)
    cuerpo.pack(fill="both", expand=True)
    listado = ttk.Frame(cuerpo)
    listado.pack(side="left", fill="both", expand=True, padx=(0, 16))
    tabla = ttk.Treeview(listado, columns=("nombre", "oficio", "zona", "disponibilidad"),
                         show="headings", selectmode="browse", height=8)
    for columna, titulo, ancho in zip(("nombre", "oficio", "zona", "disponibilidad"),
        ("Trabajador", "Oficio", "Zona", "Disponibilidad"), (165, 125, 125, 120)):
        tabla.heading(columna, text=titulo)
        tabla.column(columna, width=ancho, minwidth=95)
    tabla.tag_configure("no_disponible", foreground="#8B6570")
    barra = ttk.Scrollbar(listado, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    perfil = tarjeta(cuerpo, padx=16, pady=16, width=270)
    perfil.pack(side="right", fill="y")
    perfil.pack_propagate(False)
    etiqueta(perfil, "CONOCE EL PERFIL", color=GRIS).pack(anchor="w", pady=(0, 10))
    nombre = etiqueta(perfil, "Elige un trabajador", grande=True)
    nombre.configure(wraplength=230)
    nombre.pack(anchor="w")
    disponibilidad = etiqueta(perfil, "", color=VERDE)
    disponibilidad.pack(anchor="w", pady=(8, 10))
    nota = etiqueta(perfil, "Perfil ficticio. Sin reseñas ni verificación de identidad.", color=GRIS)
    nota.configure(wraplength=230, font=("Segoe UI", 9))
    nota.pack(side="bottom", anchor="w", pady=(10, 0))
    favorito_btn = ttk.Button(perfil, text="Guardar favorito", command=lambda: cambiar_favorito())
    favorito_btn.pack(side="bottom", fill="x")
    detalle = ScrolledText(perfil, height=5, wrap="word", relief="flat", bg="white", fg=TEXTO,
                       font=("Segoe UI", 10), cursor="arrow", borderwidth=0)
    detalle.pack(fill="both", expand=True, pady=(0, 10))

    servicios = obtener_servicios()
    por_nombre = {s["nombre"]: s for s in servicios}
    filtro.configure(values=["Todos los oficios"] + list(por_nombre))
    filtro.current(0)
    registros = {}

    def obtener_seleccion():
        seleccion = tabla.selection()
        return registros.get(seleccion[0]) if seleccion else None

    def mostrar_detalles(event=None):
        trabajador = obtener_seleccion()
        nombre.configure(text=trabajador["nombre"] if trabajador else "Elige un trabajador")
        disponibilidad.configure(text=("Disponible" if trabajador["disponible"] else "No disponible") if trabajador else "",
                                   fg=VERDE if not trabajador or trabajador["disponible"] else "#A04449")
        texto = (f"{trabajador['servicio']}\nZona: {trabajador['zona']}\n\n{trabajador['descripcion']}" if trabajador else
                 "Selecciona una fila para revisar el oficio, la zona y la descripción del trabajador.")
        detalle.configure(state="normal")
        detalle.delete("1.0", "end")
        detalle.insert("1.0", texto)
        detalle.configure(state="disabled")
        favorito_btn.configure(text="Quitar favorito" if trabajador and trabajador["favorito"] else "Guardar favorito")
        favorito_btn.state(["!disabled"] if trabajador else ["disabled"])

    def cargar_lista(event=None):
        anterior = tabla.selection()
        servicio = por_nombre.get(filtro.get())
        try:
            trabajadores = obtener_trabajadores(
                servicio["id"] if servicio else None, busqueda.get(),
                solo_disponibles=solo_disponibles.get(), solo_favoritos=favoritos.get(),
                orden="disponibilidad" if orden.get() == "Disponibilidad" else "nombre")
        except (OSError, datos.sqlite3.Error) as error:
            aviso_error(win, error)
            return
        for fila in tabla.get_children():
            tabla.delete(fila)
        registros.clear()
        for trabajador in trabajadores:
            clave = f"{trabajador['id']}|{trabajador['servicio_id']}"
            registros[clave] = trabajador
            tabla.insert("", "end", iid=clave,
                         values=(trabajador["nombre"], trabajador["servicio"], trabajador["zona"],
                                 "Disponible" if trabajador["disponible"] else "No disponible"),
                         tags=() if trabajador["disponible"] else ("no_disponible",))
        if anterior and tabla.exists(anterior[0]):
            tabla.selection_set(anterior[0])
        cantidad.configure(text=f"{len(trabajadores)} resultados · Los favoritos se guardan en esta computadora." if trabajadores
                           else "Sin resultados. Cambia la búsqueda o restablece los filtros.")
        mostrar_detalles()

    def seleccionar_trabajador():
        if not obtener_seleccion():
            messagebox.showwarning("Elige un trabajador", "Primero selecciona una fila de la tabla.", parent=win)
            return
        mostrar_detalles()
        detalle.focus_set()

    def solicitar_servicio():
        trabajador = obtener_seleccion()
        if not trabajador:
            messagebox.showwarning("Elige un trabajador", "Primero selecciona una fila de la tabla.", parent=win)
            return
        if not trabajador["disponible"]:
            messagebox.showwarning("No disponible", "Este trabajador no está disponible. Elige otro.", parent=win)
            return
        servicio = next(s for s in servicios if s["id"] == trabajador["servicio_id"])
        def mostrar_solicitud(identificador):
            raiz=win._root()
            if hasattr(raiz,"ver_solicitud"):
                raiz.ver_solicitud(identificador)
            else:
                from .win_table import open_win_table
                historial=open_win_table(raiz)
                historial.tabla.selection_set(identificador)
                historial.tabla.see(identificador)
        open_win_form(win, servicio=servicio.copy(), trabajador=trabajador.copy(),on_submit=mostrar_solicitud)

    def cambiar_favorito():
        trabajador = obtener_seleccion()
        if not trabajador:
            return
        try:
            datos.alternar_favorito(trabajador["id"])
        except (ValueError, OSError, datos.sqlite3.Error) as error:
            aviso_error(win, error)
            return
        cargar_lista()
        notificar_cambio(win)

    def seleccionar_categoria(valor):
        for servicio in servicios:
            if valor in (servicio["id"], servicio["nombre"], servicio["id"].removeprefix("serv-")):
                filtro.set(servicio["nombre"])
                cargar_lista()
                return
        filtro.current(0)
        cargar_lista()

    def restablecer():
        filtro.current(0)
        solo_disponibles.set(False)
        favoritos.set(False)
        orden.current(0)
        busqueda.set("")
        cargar_lista()
        opciones.pack_forget()
        mas_btn.configure(text="Más filtros")

    def buscar(texto):
        restablecer()
        busqueda.set(texto)
        entrada.focus_set()

    ttk.Button(botones, text="Seleccionar trabajador", command=seleccionar_trabajador).pack(side="left")
    ttk.Button(botones, text="Solicitar servicio", style="Primary.TButton", command=solicitar_servicio).pack(side="left", padx=8)
    ttk.Button(botones, text="Cerrar", command=win.destroy).pack(side="right")
    filtro.bind("<<ComboboxSelected>>", cargar_lista)
    orden.bind("<<ComboboxSelected>>", cargar_lista)
    busqueda.trace_add("write", lambda *_: cargar_lista())
    tabla.bind("<<TreeviewSelect>>", mostrar_detalles)
    tabla.bind("<Double-1>", lambda evento: solicitar_servicio())
    win.bind("<<DatosActualizados>>", cargar_lista)
    win.seleccionar_categoria = seleccionar_categoria
    win.tabla = tabla
    win.actualizar = cargar_lista
    win.buscar = buscar
    seleccionar_categoria(categoria)
    return win
