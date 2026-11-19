"""Seguimiento del trabajo y controles de simulación del prestador."""
import tkinter as tk
from tkinter import ttk, messagebox
from ..core import datos
from .ui import cerrar_vista, crear_ventana, encabezado, tarjeta, etiqueta, aviso_error, notificar_cambio, fecha_legible, fecha_corta, dinero, FONDO, VERDE, GRIS, TEXTO, BORDE


def open_win_canvas(parent,solicitud_id=None):
    win=crear_ventana(parent,"Seguimiento",1060,760)
    if isinstance(win,tk.Toplevel):win.minsize(960,700)
    frame=ttk.Frame(win,padding=22);frame.pack(fill="both",expand=True)
    acciones=ttk.Frame(frame);acciones.pack(side="bottom",fill="x")
    simulacion=tk.BooleanVar(value=False)
    ttk.Checkbutton(frame,text="Activar simulación de prestador (solo datos de ejemplo)",variable=simulacion,
        command=lambda:dibujar()).pack(side="bottom",anchor="w",pady=(14,6))
    encabezado(frame,"Seguimiento de tu servicio","Consulta el avance y los movimientos de cada solicitud.")
    selector=ttk.Frame(frame);selector.pack(fill="x",pady=(0,14))
    ttk.Label(selector,text="Solicitud").pack(side="left",padx=(0,10))
    combo=ttk.Combobox(selector,state="readonly");combo.pack(side="left",fill="x",expand=True)
    ttk.Button(selector,text="Actualizar",command=lambda:actualizar()).pack(side="left",padx=(8,0))
    resumen=ttk.Label(frame,text="",style="Subtitle.TLabel");resumen.pack(anchor="w")
    siguiente=ttk.Label(frame,text="",style="Accent.TLabel",wraplength=940)
    siguiente.pack(anchor="w",pady=(8,0))
    canvas=tk.Canvas(frame,height=130,bg=FONDO,highlightthickness=0)
    canvas.pack(fill="x",pady=(12,10))
    texto=ttk.Label(frame,text="",style="Muted.TLabel",wraplength=850)
    texto.pack(anchor="w",pady=(0,14))
    ttk.Label(frame,text="Movimientos de la solicitud",style="Subtitle.TLabel").pack(anchor="w",pady=(0,8))
    lista_movimientos=ttk.Frame(frame)
    lista_movimientos.pack(fill="both",expand=True)
    historial=ttk.Treeview(lista_movimientos,columns=("fecha","detalle"),show="headings",height=5)
    historial.heading("fecha",text="Fecha");historial.heading("detalle",text="Movimiento")
    historial.column("fecha",width=160,minwidth=140,stretch=False);historial.column("detalle",width=650)
    historial.pack(side="left",fill="both",expand=True)
    barra=ttk.Scrollbar(lista_movimientos,orient="vertical",command=historial.yview)
    barra.pack(side="right",fill="y")
    historial.configure(yscrollcommand=barra.set)
    solicitudes={};actual={}
    seleccion_id=[solicitud_id]

    def dibujar(event=None):
        canvas.delete("all")
        if not actual:
            canvas.create_text(20,55,text="Crea una solicitud para ver su seguimiento.",anchor="w",fill=GRIS,font=("Segoe UI",12))
        elif actual["estado"]=="cancelada":
            canvas.create_rectangle(12,12,max(100,canvas.winfo_width()-12),108,fill="#FCEEEF",outline="")
            canvas.create_text(30,42,text="Solicitud cancelada",anchor="w",fill="#A73A45",font=("Segoe UI",16,"bold"))
            canvas.create_text(30,75,text="Este servicio ya no continuará. Puedes buscar otro trabajador.",anchor="w",fill=GRIS)
        else:
            paso=datos.ORDEN_ESTADOS.index(actual["estado"])
            ancho=max(canvas.winfo_width(),650);espacio=(ancho-100)/4
            canvas.create_line(50,42,ancho-50,42,fill=BORDE,width=4)
            if paso:canvas.create_line(50,42,50+paso*espacio,42,fill=VERDE,width=4)
            for i,estado in enumerate(datos.ORDEN_ESTADOS):
                x=50+i*espacio;hecho=i<=paso
                canvas.create_oval(x-18,24,x+18,60,fill=VERDE if hecho else "white",outline=VERDE if hecho else BORDE,width=2)
                canvas.create_text(x,42,text=str(i+1),fill="white" if hecho else GRIS,font=("Segoe UI",11,"bold"))
                canvas.create_text(x,86,text=datos.ESTADOS[estado],width=130,fill=TEXTO if hecho else GRIS,font=("Segoe UI",10))
        estado=actual.get("estado")
        cotizar_btn.state(["!disabled"] if simulacion.get() and estado in ("pendiente","cotizada") else ["disabled"])
        iniciar_btn.state(["!disabled"] if simulacion.get() and estado=="cotizacion_aceptada" else ["disabled"])
        finalizar_btn.state(["!disabled"] if simulacion.get() and estado=="en_proceso" else ["disabled"])

    def actualizar(event=None):
        anterior=combo.get()
        try:registros=datos.obtener_solicitudes()
        except (OSError,datos.sqlite3.Error) as error:aviso_error(win,error);return
        solicitudes.clear()
        for s in registros:solicitudes[f"#{s['numero']} · {s['servicio']} · {s['estado_texto']}"]=s["id"]
        combo.configure(values=list(solicitudes))
        etiqueta_actual=next((k for k,v in solicitudes.items() if v==seleccion_id[0]),None)
        if etiqueta_actual:combo.set(etiqueta_actual)
        elif anterior in solicitudes:combo.set(anterior)
        elif solicitudes:combo.current(0)
        else:combo.set("")
        elegir()

    def elegir(event=None):
        identificador=solicitudes.get(combo.get())
        seleccion_id[0]=identificador
        actual.clear()
        for fila in historial.get_children():historial.delete(fila)
        if identificador:
            s=datos.obtener_solicitud(identificador)
            if s:actual.update(s)
        if actual:
            resumen.configure(text=f"{actual['servicio']} con {actual['trabajador']} · {actual['estado_texto']}")
            instrucciones={"pendiente":"Siguiente paso: espera una cotización del trabajador.",
                "cotizada":"Siguiente paso: abre Mis solicitudes y revisa la cotización.",
                "cotizacion_aceptada":"Cotización aceptada. Falta acordar e iniciar el trabajo.",
                "en_proceso":"El trabajo está en proceso. Aquí verás cuando finalice.",
                "completada":"Trabajo finalizado. El historial y la cotización quedan disponibles.",
                "cancelada":"Solicitud cancelada. Puedes buscar otro servicio."}
            siguiente.configure(text=instrucciones[actual['estado']])
            descripcion=actual['descripcion']
            if len(descripcion)>180:descripcion=descripcion[:177]+"..."
            texto.configure(text=f"{fecha_corta(actual['fecha'])} · {actual['horario']} · Prioridad: {actual['urgencia']} · {actual['zona']}\n{descripcion}")
            for movimiento in actual["movimientos"]:
                historial.insert("","end",values=(fecha_legible(movimiento["fecha"]),movimiento["detalle"]))
            historial.yview_moveto(1)
        else:
            resumen.configure(text="Todavía no hay solicitudes")
            siguiente.configure(text="Primero elige a un trabajador en Buscar servicio.")
            texto.configure(text="Busca un servicio y envía una solicitud para comenzar.")
        dibujar()

    def cambiar(nuevo_estado):
        if not actual or not simulacion.get():return
        if not messagebox.askyesno("Simular avance",f"¿Marcar como {datos.ESTADOS[nuevo_estado]} en este prototipo?",parent=win.winfo_toplevel()):return
        try:datos.actualizar_estado(actual["id"],nuevo_estado)
        except (ValueError,OSError,datos.sqlite3.Error) as error:aviso_error(win,error);return
        actualizar();notificar_cambio(win)

    def cotizar():
        if not actual or not simulacion.get():return
        identificador=actual["id"]
        plan=datos.obtener_plan(actual["trabajador_id"])
        porcentaje=datos.COMISION_PRO_PORCENTAJE if plan["plan"]=="pro" else datos.COMISION_PORCENTAJE
        cot=crear_ventana(win,"Cotización de ejemplo",740,650)
        if isinstance(cot,tk.Toplevel):cot.minsize(700,600)
        box=ttk.Frame(cot,padding=22);box.pack(fill="both",expand=True)
        pie=ttk.Frame(box);pie.pack(side="bottom",fill="x")
        encabezado(box,"Cotización de ejemplo","Simula la propuesta de un prestador. No se realiza un cobro.")
        ttk.Label(box,text="Importe en pesos mexicanos").pack(anchor="w")
        importe=ttk.Entry(box);importe.pack(fill="x",pady=(5,12));importe.focus_set()
        reparto=ttk.Label(box,text=f"Comisión del plan {'Pro' if plan['plan']=='pro' else 'Básico'}: {porcentaje} %. Se descuenta del total acordado.",style="Small.TLabel",wraplength=640)
        reparto.pack(anchor="w",pady=(0,12))
        def calcular_reparto(event=None):
            try:
                d=datos.desglosar_importe(importe.get(),porcentaje)
                reparto.configure(text=f"Ofivanta ({d['porcentaje']} %): {dinero(d['comision'])} · Neto trabajador: {dinero(d['neto'])}. "
                    "Simulación; no incluye otros gastos del trabajador.")
            except ValueError:reparto.configure(text="Escribe el importe para ver el reparto de ejemplo.")
        importe.bind("<KeyRelease>",calcular_reparto)
        materiales=tk.BooleanVar(value=False)
        ttk.Checkbutton(box,text="El importe incluye materiales",variable=materiales).pack(anchor="w",pady=(0,12))
        ttk.Label(box,text="Condiciones y alcance del trabajo").pack(anchor="w")
        condiciones=tk.Text(box,height=5,wrap="word",font=("Segoe UI",10),relief="solid",bd=1,padx=8,pady=8)
        condiciones.pack(fill="both",expand=True,pady=(5,14))
        def guardar():
            try:datos.registrar_cotizacion(identificador,importe.get(),materiales.get(),condiciones.get("1.0","end").strip())
            except (ValueError,OSError,datos.sqlite3.Error) as error:aviso_error(cot,error);return
            cerrar_vista(cot);actualizar();notificar_cambio(win)
        ttk.Button(pie,text="Guardar cotización",style="Primary.TButton",command=guardar).pack(side="left")
        ttk.Button(pie,text="Cerrar",command=lambda:cerrar_vista(cot)).pack(side="right")

    cotizar_btn=ttk.Button(acciones,text="Crear cotización",command=cotizar);cotizar_btn.pack(side="left")
    iniciar_btn=ttk.Button(acciones,text="Iniciar servicio",command=lambda:cambiar("en_proceso"));iniciar_btn.pack(side="left",padx=8)
    finalizar_btn=ttk.Button(acciones,text="Finalizar servicio",command=lambda:cambiar("completada"));finalizar_btn.pack(side="left")
    ttk.Button(acciones,text="Cerrar",command=lambda:cerrar_vista(win)).pack(side="right")
    combo.bind("<<ComboboxSelected>>",elegir);canvas.bind("<Configure>",dibujar)
    win.bind("<<DatosActualizados>>",actualizar)
    win.actualizar=actualizar;win.canvas=canvas
    actualizar();return win
