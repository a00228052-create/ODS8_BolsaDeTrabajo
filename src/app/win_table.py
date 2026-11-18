frm = ttk.Frame(win, padding=14)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Mis solicitudes", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))

    filtros = ttk.Frame(frm)
    filtros.pack(fill="x", pady=(0, 10))
    ttk.Label(filtros, text="Filtrar por estado:").pack(side="left", padx=(0, 8))
    filtro = tk.StringVar(value="Todos")
    estados = ("Todos", "Pendiente", "Cotizada", "Confirmada", "En proceso", "Finalizada", "Cancelada")
    combo = ttk.Combobox(filtros, textvariable=filtro, values=estados, state="readonly", width=20)
    combo.pack(side="left")

    contenedor = ttk.Frame(frm)
    contenedor.pack(fill="both", expand=True)
    columnas = ("numero", "servicio", "trabajador", "fecha", "estado")
    titulos = ("Número de solicitud", "Servicio", "Trabajador", "Fecha", "Estado")
    tv = ttk.Treeview(contenedor, columns=columnas, show="headings", selectmode="browse")
    for col, titulo in zip(columnas, titulos):
        tv.heading(col, text=titulo)
        tv.column(col, width=175 if col in ("numero", "trabajador") else 140, anchor="center", stretch=True)
    scroll = ttk.Scrollbar(contenedor, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=scroll.set)
    tv.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    mensaje = ttk.Label(frm, text="", foreground="gray")
    mensaje.pack(anchor="w", pady=(8, 4))
    solicitudes_actuales = {}

    def actualizar():

        for fila in tv.get_children():
            tv.delete(fila)
        solicitudes_actuales.clear()
        try:
            registros = obtener_solicitudes()
            if registros is None:
                registros = []
            for solicitud in registros:
                numero = str(solicitud.get("numero", ""))
                if not numero or numero in solicitudes_actuales:
                    continue
                solicitudes_actuales[numero] = solicitud
                if filtro.get() != "Todos" and solicitud.get("estado") != filtro.get():
                    continue
                tv.insert("", "end", iid=numero, values=(
                    numero, solicitud.get("servicio", ""),
                    solicitud.get("trabajador", ""), solicitud.get("fecha", ""),
                    solicitud.get("estado", "")))
            if not solicitudes_actuales:
                mensaje.config(text="Todavía no hay solicitudes registradas.")
            elif not tv.get_children():
                mensaje.config(text="No hay solicitudes con el estado seleccionado.")
            else:
                mensaje.config(text=f"Mostrando {len(tv.get_children())} solicitud(es).")
        except Exception as exc:
            mensaje.config(text="No se pudieron cargar las solicitudes.")
            messagebox.showerror("Error", f"No se pudieron consultar las solicitudes:\n{exc}", parent=win)

    def seleccionada():
        seleccion = tv.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una solicitud primero.", parent=win)
            return None
        return solicitudes_actuales.get(seleccion[0])

    def cambiar_estado(accion, numero, ventana_detalle):
        pregunta = ("¿Aceptar esta cotización y confirmar la solicitud?" if accion == "aceptar"
                    else "¿Cancelar esta solicitud?")
        if not messagebox.askyesno("Confirmar cambio", pregunta, parent=ventana_detalle):
            return
        try:
            if accion == "aceptar":
                aceptar_cotizacion(numero)
            else:
                cancelar_solicitud(numero)
        except Exception as exc:
            messagebox.showerror("No se pudo realizar el cambio", str(exc), parent=ventana_detalle)
            return
        messagebox.showinfo("Cambio realizado", "El estado se actualizó en el modo demostración.", parent=ventana_detalle)
        ventana_detalle.destroy()
        actualizar()

    def ver_detalles():
        solicitud = seleccionada()
        if solicitud is None:
            return
        numero = str(solicitud["numero"])
        detalle = tk.Toplevel(win)
        detalle.title(f"Detalles - {numero}")
        detalle.geometry("580x430")
        detalle.transient(win)
        contenido = ttk.Frame(detalle, padding=18)
        contenido.pack(fill="both", expand=True)
        ttk.Label(contenido, text=f"Solicitud {numero}", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))
        for campo, clave in (("Servicio", "servicio"), ("Trabajador", "trabajador"),
                             ("Fecha", "fecha"), ("Estado", "estado")):
            ttk.Label(contenido, text=f"{campo}: {solicitud.get(clave, 'No disponible')}").pack(anchor="w", pady=2)
        ttk.Label(contenido, text="Descripción:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 2))
        ttk.Label(contenido, text=solicitud.get("descripcion") or "Sin descripción registrada.", wraplength=520).pack(anchor="w")
        ttk.Label(contenido, text="Condiciones de la cotización:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 2))
        ttk.Label(contenido, text=solicitud.get("condiciones") or "Sin condiciones registradas.", wraplength=520).pack(anchor="w")
        botones = ttk.Frame(contenido)
        botones.pack(side="bottom", fill="x", pady=(16, 0))
        btn_aceptar = ttk.Button(botones, text="Aceptar cotización", command=lambda: cambiar_estado("aceptar", numero, detalle))
        btn_aceptar.pack(side="left", padx=(0, 6))
        if solicitud.get("estado") != "Cotizada":
            btn_aceptar.state(["disabled"])
        btn_cancelar = ttk.Button(botones, text="Cancelar solicitud", command=lambda: cambiar_estado("cancelar", numero, detalle))
        btn_cancelar.pack(side="left", padx=(0, 6))
        if solicitud.get("estado") in ("En proceso", "En progreso", "Iniciada", "Finalizada", "Completada", "Cancelada"):
            btn_cancelar.state(["disabled"])
        ttk.Button(botones, text="Cerrar", command=detalle.destroy).pack(side="right")

    botones = ttk.Frame(frm)
    botones.pack(fill="x", pady=(10, 0))
    ttk.Button(botones, text="Actualizar", command=actualizar).pack(side="left", padx=(0, 8))
    ttk.Button(botones, text="Ver detalles", command=ver_detalles).pack(side="left", padx=(0, 8))

    def seguimiento():
        solicitud = seleccionada()
        if solicitud is not None:
            abrir_seguimiento(win, str(solicitud["numero"]))

    ttk.Button(botones, text="Abrir seguimiento", command=seguimiento).pack(side="left")
    ttk.Button(botones, text="Cerrar", command=win.destroy).pack(side="right")
    combo.bind("<<ComboboxSelected>>", lambda event: actualizar())
