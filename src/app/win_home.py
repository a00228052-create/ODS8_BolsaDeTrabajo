"""Inicio del cliente y demostración del modelo de negocio del equipo."""
import tkinter as tk
from tkinter import ttk, messagebox
from ..core import datos
from .ui import (
    crear_ventana, tarjeta, etiqueta, aviso_error, notificar_cambio,
    dinero, fecha_corta, cargar_logo, dibujar_degradado, ACENTO, FONDO, TEXTO, GRIS, VERDE, AZUL,
)


def construir_inicio(parent, abrir_catalogo, abrir_solicitudes, abrir_seguimiento, mostrar_pestanas=True):
    frame = ttk.Frame(parent, padding=24)
    pestanas = ttk.Frame(frame)
    if mostrar_pestanas:
        pestanas.pack(fill="x", pady=(0, 18))
    cliente = ttk.Frame(frame)
    negocio = ttk.Frame(frame)
    vistas = {"cliente": cliente, "negocio": negocio}
    botones_vista = {}

    def mostrar_vista(nombre="cliente"):
        for clave, vista in vistas.items():
            vista.pack_forget()
            botones_vista[clave].configure(
                style="Active.Tab.TButton" if clave == nombre else "Tab.TButton")
        vistas[nombre].pack(fill="both", expand=True)

    for clave, texto in [("cliente", "Para tu hogar"), ("negocio", "Planes e ingresos")]:
        boton = ttk.Button(pestanas, text=texto, style="Tab.TButton",
                           command=lambda valor=clave: mostrar_vista(valor))
        boton.pack(side="left", padx=(0, 8))
        botones_vista[clave] = boton

    hero = tk.Canvas(cliente, height=270, highlightthickness=0, bg=AZUL)
    hero.pack(fill="x", pady=(0,18))
    logo = cargar_logo(hero, 150)
    hero._logo = logo
    boton_buscar = ttk.Button(hero, text="Buscar un servicio", style="Hero.TButton", command=abrir_catalogo)

    def dibujar_portada(event=None):
        hero.delete("all")
        dibujar_degradado(hero)
        ancho = hero.winfo_width()
        hero.create_text(26,28,text="SERVICIOS PARA TU HOGAR",anchor="nw",fill="#BFDBFE",font=("Segoe UI",9,"bold"))
        titulo=hero.create_text(26,62,text="El cuidado de tu casa,\nen un solo lugar.",anchor="nw",fill="white",font=("Segoe UI",25,"bold"),width=max(400,ancho-250))
        descripcion=hero.create_text(26,hero.bbox(titulo)[3]+12,text="Elige un oficio, explica el trabajo y revisa tu cotización.",anchor="nw",fill="#DBEAFE",font=("Segoe UI",10),width=max(400,ancho-250))
        boton_y=hero.bbox(descripcion)[3]+18
        hero.create_window(26,boton_y,window=boton_buscar,anchor="nw")
        alto=max(270,boton_y+max(44,boton_buscar.winfo_reqheight())+20)
        if int(hero.cget("height"))!=alto:hero.configure(height=alto)
        if logo is not None:
            x=ancho-125
            hero.create_oval(x-81,alto/2-81,x+81,alto/2+81,fill="white",outline="")
            hero.create_image(x,alto/2,image=logo)

    hero.bind("<Configure>",dibujar_portada)

    buscador = tarjeta(cliente, padx=12, pady=10)
    buscador.pack(fill="x", pady=(0, 18))
    busqueda = tk.StringVar()
    etiqueta(buscador, "Oficio o zona", color=GRIS).pack(side="left", padx=(0, 12))
    entrada = ttk.Entry(buscador, textvariable=busqueda)
    entrada.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def buscar():
        ventana = abrir_catalogo()
        if ventana is not None and hasattr(ventana, "buscar"):
            ventana.buscar(busqueda.get())

    ttk.Button(buscador, text="Buscar", command=buscar).pack(side="right")
    entrada.bind("<Return>", lambda evento: buscar())
    resumen = ttk.Frame(cliente)
    resumen.pack(fill="x", pady=(0, 20))
    contadores = []
    for i, titulo in enumerate(["Oficios", "Solicitudes abiertas", "Trabajos finalizados", "Favoritos guardados"]):
        resumen.columnconfigure(i, weight=1, uniform="resumen")
        card = tarjeta(resumen, padx=14, pady=12)
        card.grid(row=0, column=i, sticky="nsew", padx=(0, 10 if i < 3 else 0))
        numero = etiqueta(card, "0", grande=True, color=VERDE)
        numero.configure(font=("Segoe UI", 22, "bold"))
        numero.pack(anchor="w")
        titulo_label = etiqueta(card, titulo, color=GRIS)
        titulo_label.configure(wraplength=160, font=("Segoe UI", 9))
        titulo_label.pack(anchor="w", pady=(4, 0))
        contadores.append(numero)

    ttk.Label(cliente, text="¿Qué necesitas resolver?", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
    categorias = ttk.Frame(cliente)
    categorias.pack(fill="x", pady=(0, 18))
    for i, servicio in enumerate(datos.obtener_servicios()):
        categorias.columnconfigure(i % 4, weight=1, uniform="oficio")
        ttk.Button(categorias, text=servicio["nombre"],
                   command=lambda s=servicio: abrir_catalogo(s["id"])).grid(
            row=i // 4, column=i % 4, sticky="ew", padx=(0, 8), pady=(0, 8))

    titulo_recientes = ttk.Frame(cliente)
    titulo_recientes.pack(fill="x", pady=(0, 10))
    ttk.Label(titulo_recientes, text="Tus últimas solicitudes", style="Subtitle.TLabel").pack(side="left")
    ttk.Button(titulo_recientes, text="Ver mis solicitudes", command=abrir_solicitudes).pack(side="right")
    ultimas = ttk.Frame(cliente)
    ultimas.pack(fill="x")
    ttk.Button(cliente, text="Ver seguimiento", command=abrir_seguimiento).pack(anchor="w", pady=(12, 0))
    ttk.Label(cliente, text="1. Elige un trabajador   /   2. Explica el trabajo   /   3. Revisa la cotización",
              style="Small.TLabel").pack(anchor="w", pady=(18, 6))
    ttk.Label(cliente, text="Prototipo local · Perfiles ficticios · Sin cobros reales", style="Small.TLabel").pack(anchor="w")

    # El apartado del prestador permanece dentro de win_home.py.
    ttk.Label(negocio, text="Planes y ganancias", style="Title.TLabel").pack(anchor="w")
    ttk.Label(negocio, text="Comisión por servicio y plan opcional. Demostración sin cobros.",
              style="Muted.TLabel").pack(anchor="w", pady=(5, 16))
    apartados = ttk.Notebook(negocio)
    apartados.pack(fill="both", expand=True)
    pagina_planes = ttk.Frame(apartados, padding=16)
    pagina_agenda = ttk.Frame(apartados, padding=16)
    pagina_ingresos = ttk.Frame(apartados, padding=16)
    for pagina, nombre in [(pagina_planes, "Planes"), (pagina_agenda, "Mi agenda"), (pagina_ingresos, "Ingresos")]:
        apartados.add(pagina, text=nombre)
    aviso = tarjeta(pagina_planes, padx=14, pady=12)
    aviso.pack(fill="x", pady=(0, 16))
    nota = etiqueta(aviso, "DEMO: Básico 10 %; Pro 7 % + $149 por 30 días. Importes de ejemplo.\n"
                    "No se solicita tarjeta, no se cobra y no hay renovación automática.", color=VERDE)
    nota.configure(wraplength=790)
    nota.pack(anchor="w")
    planes = ttk.Frame(pagina_planes)
    planes.pack(fill="x", pady=(0, 18))
    for i, (nombre, precio, descripcion) in enumerate([
        ("Básico", "$0 de mensualidad", "Recibe solicitudes y envía cotizaciones.\nComisión del 10 % al finalizar un servicio."),
        ("Pro", "$149 / 30 días de ejemplo", "Incluye agenda por trabajador y resumen de ganancias.\nComisión reducida al 7 % en nuevas cotizaciones."),
    ]):
        planes.columnconfigure(i, weight=1, uniform="planes")
        card = tarjeta(planes, padx=18, pady=16)
        card.grid(row=0, column=i, sticky="nsew", padx=(0, 12 if i == 0 else 0))
        etiqueta(card, nombre, grande=True, color=VERDE).pack(anchor="w")
        etiqueta(card, precio, grande=True).pack(anchor="w", pady=(6, 10))
        detalle = etiqueta(card, descripcion, color=GRIS)
        detalle.configure(wraplength=335)
        detalle.pack(anchor="w")

    calculadora = tarjeta(pagina_planes, padx=16, pady=14)
    calculadora.pack(fill="x", pady=(0, 18))
    etiqueta(calculadora, "Compara cuánto te quedaría", grande=True).pack(anchor="w")
    fila_calculo = tk.Frame(calculadora, bg="white")
    fila_calculo.pack(fill="x", pady=(10, 6))
    etiqueta(fila_calculo, "Importe MXN").pack(side="left", padx=(0, 8))
    importe = tk.StringVar(value="500")
    importe_entry = ttk.Entry(fila_calculo, textvariable=importe, width=14)
    importe_entry.pack(side="left", padx=(0, 10))
    etiqueta(fila_calculo, "Trabajos / 30 días").pack(side="left",padx=(8,8))
    cantidad=tk.StringVar(value="20")
    ttk.Spinbox(fila_calculo,from_=0,to=10000,textvariable=cantidad,width=6).pack(side="left",padx=(0,10))
    resultado = etiqueta(calculadora, "", color=VERDE)
    resultado.configure(wraplength=790)
    resultado.pack(anchor="w", pady=(5, 0))

    def calcular():
        try:
            r=datos.comparar_planes(importe.get(),cantidad.get())
        except ValueError as error:
            resultado.configure(text=str(error),fg="#A73A45")
            return
        comparacion=(f"Pro dejaría {dinero(r['diferencia'])} más en este ejemplo." if r['diferencia']>=0 else
                     f"Básico dejaría {dinero(-r['diferencia'])} más en este ejemplo.")
        resultado.configure(text=f"Volumen de servicios: {dinero(r['volumen'])} MXN\n"
                            f"Básico: comisión {dinero(r['comision_basica'])}; neto {dinero(r['neto_basico'])}.\n"
                            f"Pro: comisión {dinero(r['comision_pro'])} + cuota {dinero(r['cuota_pro'])}; neto {dinero(r['neto_pro'])}.\n"
                            f"{comparacion}",fg=VERDE)

    ttk.Button(fila_calculo, text="Calcular reparto", command=calcular).pack(side="right")
    importe_entry.bind("<Return>", lambda evento: calcular())
    calcular()
    aclaracion = etiqueta(calculadora, "La comisión se descuenta del importe acordado; el cliente no paga una cuota extra. "
                          "El neto no descuenta materiales, impuestos ni otros gastos.", color=GRIS)
    aclaracion.configure(wraplength=790, font=("Segoe UI", 9))
    aclaracion.pack(anchor="w", pady=(8, 0))

    ttk.Button(pagina_planes, text="Probar Pro en Mi agenda", style="Primary.TButton",
               command=lambda: apartados.select(pagina_agenda)).pack(anchor="w", pady=(0, 6))
    ttk.Label(pagina_agenda, text="Elige un trabajador de ejemplo", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
    selector = ttk.Frame(pagina_agenda)
    selector.pack(fill="x", pady=(0, 10))
    proveedor = ttk.Combobox(selector, state="readonly")
    proveedor.pack(side="left", fill="x", expand=True, padx=(0, 10))
    trabajadores = {t["id"]: t for t in datos.obtener_trabajadores()}
    por_nombre = {t["nombre"]: t["id"] for t in trabajadores.values()}
    proveedor.configure(values=list(por_nombre))
    proveedor.current(0)
    estado_plan = ttk.Label(pagina_agenda, text="", style="Accent.TLabel")
    estado_plan.pack(anchor="w", pady=(0, 8))
    acciones = ttk.Frame(selector)
    acciones.pack(side="right")
    ganancias = ttk.Label(pagina_agenda, text="", style="Muted.TLabel", wraplength=800)
    ganancias.pack(anchor="w", pady=(0, 12))
    lista = ttk.Frame(pagina_agenda)
    lista.pack(fill="x")
    agenda = ttk.Treeview(lista, columns=("fecha", "horario", "servicio", "estado"), show="headings", height=4)
    for columna, titulo, ancho in [("fecha", "Fecha deseada", 125), ("horario", "Horario preferido", 185),
                                   ("servicio", "Servicio", 180), ("estado", "Estado", 140)]:
        agenda.heading(columna, text=titulo)
        agenda.column(columna, width=ancho, minwidth=95)
    agenda.pack(side="left", fill="both", expand=True)
    barra = ttk.Scrollbar(lista, orient="vertical", command=agenda.yview)
    barra.pack(side="right", fill="y")
    agenda.configure(yscrollcommand=barra.set)
    nota_agenda = ttk.Label(pagina_agenda, text="", style="Small.TLabel")
    nota_agenda.pack(anchor="w", pady=(8, 0))

    def actualizar_prestador(event=None):
        trabajador_id = por_nombre.get(proveedor.get())
        if not trabajador_id:
            return
        plan = datos.obtener_plan(trabajador_id)
        for fila in agenda.get_children():
            agenda.delete(fila)
        pro = plan["plan"] == "pro"
        estado_plan.configure(text=f"Plan Pro de ejemplo · vence el {fecha_corta(plan['vence'])}" if pro else "Plan Básico · sin mensualidad")
        activar_btn.state(["disabled"] if pro else ["!disabled"])
        cancelar_btn.state(["!disabled"] if pro else ["disabled"])
        if pro:
            resumen_trabajador = datos.resumen_negocio(trabajador_id)
            ganancias.configure(text=f"Trabajos finalizados: {resumen_trabajador['servicios_finalizados']}   /   "
                                f"Neto por servicios: {dinero(resumen_trabajador['neto_trabajadores'])}   /   "
                                f"Suscripciones simuladas: {dinero(resumen_trabajador['suscripciones'])}")
            pendientes = datos.obtener_agenda(trabajador_id)
            for s in pendientes:
                agenda.insert("", "end", iid=s["id"], values=(fecha_corta(s["fecha"]), s["horario"], s["servicio"], s["estado_texto"]))
            nota_agenda.configure(text="Agenda de solicitudes abiertas. La fecha y el horario están por acordar con el cliente."
                                 if pendientes else "No tienes solicitudes abiertas. Las próximas aparecerán aquí.")
        else:
            ganancias.configure(text="La agenda y el resumen por trabajador se habilitan con el plan Pro de ejemplo.")
            nota_agenda.configure(text="Puedes activar la demostración sin pagar ni introducir datos bancarios.")

    def cambiar_plan(activar):
        trabajador_id = por_nombre[proveedor.get()]
        mensaje = ("¿Activar Pro de ejemplo para este trabajador?\n"
                   "Cada periodo de 30 días registra $149 simulados. Reactivar un periodo vigente no lo duplica. "
                   "No hay cargo ni renovación automática." if activar else
                   "¿Volver a Básico en esta demostración? Se conserva el historial del periodo simulado.")
        if not messagebox.askyesno("Simulación de plan", mensaje, parent=frame.winfo_toplevel()):
            return
        try:
            if activar:
                datos.activar_plan_pro(trabajador_id)
            else:
                datos.cancelar_plan_pro(trabajador_id)
        except (ValueError, OSError, datos.sqlite3.Error) as error:
            aviso_error(frame.winfo_toplevel(), error)
            return
        actualizar()
        notificar_cambio(frame)

    activar_btn = ttk.Button(acciones, text="Simular Pro", style="Primary.TButton", command=lambda: cambiar_plan(True))
    activar_btn.pack(side="left", padx=(0, 8))
    cancelar_btn = ttk.Button(acciones, text="Volver a Básico", command=lambda: cambiar_plan(False))
    cancelar_btn.pack(side="left")
    proveedor.bind("<<ComboboxSelected>>", actualizar_prestador)

    def ver_agenda():
        if not agenda.selection():
            messagebox.showwarning("Elige una solicitud", "Selecciona una fila de la agenda.", parent=frame.winfo_toplevel())
            return
        from .win_table import abrir_detalles
        abrir_detalles(frame.winfo_toplevel(), agenda.selection()[0])

    ttk.Button(pagina_agenda, text="Abrir solicitud de la agenda", command=ver_agenda).pack(anchor="w", pady=(10, 18))
    ttk.Label(pagina_ingresos, text="Resumen del negocio · acumulado simulado", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
    resumen_negocio = tarjeta(pagina_ingresos, padx=16, pady=14)
    resumen_negocio.pack(fill="x")
    ingresos = etiqueta(resumen_negocio, "", grande=True, color=VERDE)
    ingresos.configure(wraplength=790)
    ingresos.pack(anchor="w")
    detalle_ingresos = etiqueta(resumen_negocio, "", color=GRIS)
    detalle_ingresos.configure(wraplength=790)
    detalle_ingresos.pack(anchor="w", pady=(6, 0))
    nota_ingresos = etiqueta(resumen_negocio, "Solo se cuentan comisiones de servicios finalizados y periodos Pro activados. "
                            "Son registros de demostración, no dinero recibido.", color=GRIS)
    nota_ingresos.configure(wraplength=790, font=("Segoe UI", 9))
    nota_ingresos.pack(anchor="w", pady=(8, 0))
    grafica=tk.Canvas(resumen_negocio,height=190,bg="white",highlightthickness=0)
    grafica.pack(fill="x",pady=(18,0))
    ultimo_resumen={}

    def dibujar_ingresos(event=None):
        grafica.delete("all")
        ancho=max(600,grafica.winfo_width())
        maximo=max(ultimo_resumen.get("comisiones",0),ultimo_resumen.get("suscripciones",0),1)
        for i,(clave,titulo,color) in enumerate([("comisiones","Comisiones",TEXTO),("suscripciones","Planes Pro",VERDE)]):
            y=30+i*60
            valor=ultimo_resumen.get(clave,0)
            grafica.create_text(0,y+12,text=titulo,anchor="w",fill=TEXTO,font=("Segoe UI",10))
            grafica.create_rectangle(130,y,ancho-130,y+24,fill=FONDO,outline="")
            if valor:
                grafica.create_rectangle(130,y,130+(ancho-260)*valor/maximo,y+24,fill=color,outline="")
            grafica.create_text(ancho-5,y+12,text=dinero(valor),anchor="e",fill=TEXTO,font=("Segoe UI",10,"bold"))
        grafica.create_text(0,160,text="Acumulado de la demostración. No representa pagos recibidos.",anchor="w",fill=GRIS,font=("Segoe UI",9))

    grafica.bind("<Configure>",dibujar_ingresos)

    def actualizar(event=None):
        solicitudes = datos.obtener_solicitudes()
        favoritos = {t["id"] for t in datos.obtener_trabajadores(solo_favoritos=True)}
        valores = [len(datos.obtener_servicios()),
                   sum(s["estado"] not in ("completada", "cancelada") for s in solicitudes),
                   sum(s["estado"] == "completada" for s in solicitudes), len(favoritos)]
        for label, valor in zip(contadores, valores):
            label.configure(text=str(valor))
        for hijo in ultimas.winfo_children():
            hijo.destroy()
        if not solicitudes:
            vacio = tarjeta(ultimas, padx=18, pady=18)
            vacio.pack(fill="x")
            etiqueta(vacio, "Tu primer servicio empieza aquí", grande=True).pack(anchor="w")
            etiqueta(vacio, "Busca un oficio y cuéntanos qué necesitas. Tus solicitudes aparecerán en este espacio.", color=GRIS).pack(anchor="w", pady=(6, 0))
        for s in solicitudes[:3]:
            card = tarjeta(ultimas, padx=14, pady=12)
            card.pack(fill="x", pady=(0, 8))
            def revisar(sid=s["id"]):
                from .win_table import abrir_detalles
                abrir_detalles(frame.winfo_toplevel(), sid)
            ttk.Button(card, text="Revisar", command=revisar).pack(side="right", padx=(10, 0))
            etiqueta(card, f"{s['servicio']} · {s['trabajador']}", grande=True).pack(anchor="w")
            etiqueta(card, f"#{s['numero']}   /   {fecha_corta(s['fecha'])}   /   {s['estado_texto']}", color=GRIS).pack(anchor="w", pady=(4, 0))
        actualizar_prestador()
        r = datos.resumen_negocio()
        ultimo_resumen.clear()
        ultimo_resumen.update(r)
        dibujar_ingresos()
        ingresos.configure(text=f"Ofivanta: {dinero(r['total_ofivanta'])} MXN simulados")
        detalle_ingresos.configure(text=f"Comisiones: {dinero(r['comisiones'])}   /   Planes Pro: {dinero(r['suscripciones'])}\n"
                                  f"Servicios finalizados: {r['servicios_finalizados']}   /   Planes activos: {r['planes_activos']}")

    frame.apartados = apartados
    frame.actualizar = actualizar
    frame.mostrar_vista = mostrar_vista
    frame.proveedor_combo = proveedor
    frame.agenda = agenda
    frame.importe_simulador = importe
    mostrar_vista()
    actualizar()
    return frame


def open_win_home(parent):
    win = crear_ventana(parent, "Inicio", 1100, 740)
    from .win_list import open_win_list
    from .win_table import open_win_table
    from .win_canvas import open_win_canvas
    canvas = tk.Canvas(win, bg=FONDO, highlightthickness=0)
    barra = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    frame = construir_inicio(canvas, lambda categoria=None: open_win_list(win, categoria),
                             lambda: open_win_table(win), lambda: open_win_canvas(win))
    elemento = canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda evento: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda evento: canvas.itemconfigure(elemento, width=evento.width))
    win.bind("<MouseWheel>", lambda evento: canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units"))
    win.bind("<<DatosActualizados>>", frame.actualizar)
    return win
