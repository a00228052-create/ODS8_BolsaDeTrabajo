"""Historial de solicitudes y aceptación de cotizaciones."""
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from ..core import datos
from .ui import cerrar_vista, crear_ventana, encabezado, aviso_error, notificar_cambio, GRIS, dinero, fecha_corta


def open_win_table(parent):
    win = crear_ventana(parent,"Mis solicitudes",1120,740)
    if isinstance(win,tk.Toplevel):win.minsize(900,560)
    frame = ttk.Frame(win,padding=22);frame.pack(fill="both",expand=True)
    encabezado(frame,"Mis solicitudes","Revisa tus trabajos, acepta una cotización o consulta el seguimiento.")
    filtros = ttk.Frame(frame);filtros.pack(fill="x",pady=(0,14))
    ttk.Label(filtros,text="Estado").pack(side="left",padx=(0,8))
    estado = ttk.Combobox(filtros,values=["Todos"]+list(datos.ESTADOS.values()),state="readonly",width=18)
    estado.current(0);estado.pack(side="left")
    busqueda = tk.StringVar()
    ttk.Label(filtros,text="Buscar").pack(side="left",padx=(18,8))
    entrada = ttk.Entry(filtros,textvariable=busqueda);entrada.pack(side="left",fill="x",expand=True)
    ttk.Button(filtros,text="Actualizar",command=lambda: actualizar()).pack(side="left",padx=(8,0))
    botones = ttk.Frame(frame);botones.pack(side="bottom",fill="x")
    mensaje = ttk.Label(frame,text="",style="Muted.TLabel")
    mensaje.pack(side="bottom",anchor="w",pady=12)
    contenedor = ttk.Frame(frame);contenedor.pack(fill="both",expand=True)
    cols=("numero","servicio","trabajador","fecha","importe","estado")
    tabla = ttk.Treeview(contenedor,columns=cols,show="headings",selectmode="browse",height=10)
    for col,titulo,ancho in zip(cols,["Solicitud","Servicio","Trabajador","Fecha deseada","Acordado MXN","Estado"],[100,150,180,125,130,130]):
        tabla.heading(col,text=titulo);tabla.column(col,width=ancho,minwidth=85)
    barra = ttk.Scrollbar(contenedor,orient="vertical",command=tabla.yview)
    tabla.tag_configure("completada",foreground="#087F72")
    tabla.tag_configure("cancelada",foreground="#8D737A")
    tabla.tag_configure("cotizada",foreground="#95631D")
    tabla.configure(yscrollcommand=barra.set);tabla.pack(side="left",fill="both",expand=True);barra.pack(side="right",fill="y")
    registros = {}
    visibles = []

    def seleccion():
        filas = tabla.selection()
        if not filas:
            messagebox.showwarning("Selecciona una solicitud","Elige una fila de la tabla para continuar.",parent=win.winfo_toplevel())
            return None
        return registros.get(filas[0])

    def actualizar(event=None):
        anterior = tabla.selection()
        try:
            solicitudes = datos.obtener_solicitudes()
        except (OSError,datos.sqlite3.Error) as error:
            aviso_error(win,error);return
        registros.clear();visibles.clear()
        for fila in tabla.get_children():tabla.delete(fila)
        texto = datos.texto_busqueda(busqueda.get().strip())
        for s in solicitudes:
            registros[s["id"]]=s
            coincide = texto in datos.texto_busqueda(f"{s['numero']} {s['servicio']} {s['trabajador']} {s['cliente']}")
            if coincide and (estado.get()=="Todos" or estado.get()==s["estado_texto"]):
                visibles.append(s)
                tabla.insert("","end",iid=s["id"],values=(s["numero"],s["servicio"],s["trabajador"],fecha_corta(s["fecha"]),
                    dinero(s["importe"]) if s["importe"] is not None else "Por cotizar",s["estado_texto"]),tags=(s["estado"],))
        if anterior and tabla.exists(anterior[0]):tabla.selection_set(anterior[0])
        if not solicitudes:mensaje.configure(text="Todavía no tienes solicitudes. Busca un servicio para crear la primera.")
        elif not visibles:mensaje.configure(text="No hay solicitudes con estos filtros. Prueba otro estado o búsqueda.")
        else:mensaje.configure(text=f"{len(visibles)} solicitud(es) · {sum(s['estado']=='cotizada' for s in visibles)} por revisar · "
            f"{sum(s['estado']=='completada' for s in visibles)} finalizadas · Guardado automático")

    def seguimiento():
        s=seleccion()
        if s:
            from .win_canvas import open_win_canvas
            open_win_canvas(win,s["id"])

    def cancelar(s,detalle=None):
        if s["estado"] not in ("pendiente","cotizada","cotizacion_aceptada"):
            messagebox.showinfo("No se puede cancelar","Solo puedes cancelar antes de iniciar el trabajo.",parent=(detalle or win).winfo_toplevel());return
        if not messagebox.askyesno("Cancelar solicitud",f"¿Cancelar la solicitud #{s['numero']} de {s['servicio']}?",parent=(detalle or win).winfo_toplevel()):return
        try:datos.cancelar_solicitud(s["id"])
        except (ValueError,OSError,datos.sqlite3.Error) as error:aviso_error(detalle or win,error);return
        if detalle:cerrar_vista(detalle)
        actualizar();notificar_cambio(win)

    def ver_detalles():
        s=seleccion()
        if s:abrir_detalles(win,s["id"],actualizar)

    def cancelar_seleccion():
        s=seleccion()
        if s:cancelar(s)

    def exportar():
        if not visibles:
            messagebox.showinfo("Sin resultados","No hay solicitudes visibles para exportar.",parent=win.winfo_toplevel());return
        ruta=filedialog.asksaveasfilename(parent=win.winfo_toplevel(),title="Exportar solicitudes",defaultextension=".csv",
            initialfile="solicitudes_ofivanta.csv",filetypes=[("Archivo CSV","*.csv")])
        if not ruta:return
        try:
            with open(ruta,"w",newline="",encoding="utf-8-sig") as archivo:
                writer=csv.writer(archivo);writer.writerow(["Solicitud","Servicio","Trabajador","Fecha","Horario preferido","Prioridad","Importe acordado MXN","Estado"])
                for s in visibles:
                    fila=[s["numero"],s["servicio"],s["trabajador"],s["fecha"],s["horario"],s["urgencia"],
                        str(s["importe"]) if s["importe"] is not None else "Por cotizar",s["estado_texto"]]
                    writer.writerow(["'"+v if str(v).startswith(("=","+","-","@")) else v for v in fila])
        except OSError as error:aviso_error(win,error);return
        messagebox.showinfo("Archivo guardado","Las solicitudes visibles se exportaron correctamente.",parent=win.winfo_toplevel())

    ttk.Button(botones,text="Ver detalles",style="Primary.TButton",command=ver_detalles).pack(side="left")
    ttk.Button(botones,text="Seguimiento",command=seguimiento).pack(side="left",padx=8)
    ttk.Button(botones,text="Cancelar solicitud",style="Danger.TButton",command=cancelar_seleccion).pack(side="left")
    ttk.Button(botones,text="Exportar CSV",command=exportar).pack(side="right",padx=(8,0))
    ttk.Button(botones,text="Cerrar",command=lambda:cerrar_vista(win)).pack(side="right")
    estado.bind("<<ComboboxSelected>>",actualizar);busqueda.trace_add("write",lambda *_:actualizar())
    tabla.bind("<Double-1>",lambda e:ver_detalles());win.bind("<<DatosActualizados>>",actualizar)
    win.actualizar=actualizar;win.tabla=tabla
    actualizar();return win


def abrir_detalles(parent,solicitud_id,on_change=None):
    win=crear_ventana(parent,"Detalle de solicitud",840,740)
    if isinstance(win,tk.Toplevel):win.minsize(780,680)
    frame=ttk.Frame(win,padding=22);frame.pack(fill="both",expand=True)
    encabezado(frame,"Detalle de solicitud","Elige una cotización y revisa sus condiciones antes de aceptarla.")
    resumen=ttk.Label(frame,text="",style="Subtitle.TLabel");resumen.pack(anchor="w",pady=(0,8))
    info=ScrolledText(frame,height=7,wrap="word",relief="flat",padx=12,pady=10,font=("Segoe UI",10))
    info.pack(fill="x",pady=(0,14))
    ttk.Label(frame,text="Cotizaciones recibidas",style="Subtitle.TLabel").pack(anchor="w",pady=(0,8))
    botones=ttk.Frame(frame);botones.pack(side="bottom",fill="x")
    condiciones=ScrolledText(frame,height=3,wrap="word",font=("Segoe UI",10),relief="flat",padx=8,pady=8)
    condiciones.pack(side="bottom",fill="x",pady=10)

    def mostrar_condiciones(texto):
        condiciones.configure(state="normal")
        condiciones.delete("1.0","end")
        condiciones.insert("1.0",texto)
        condiciones.configure(state="disabled")

    cot=ttk.Treeview(frame,columns=("importe","materiales","estado"),show="headings",selectmode="browse",height=3)
    for col,titulo in [("importe","Importe MXN"),("materiales","Materiales"),("estado","Estado")]:
        cot.heading(col,text=titulo);cot.column(col,width=170)
    cot.pack(fill="both",expand=True)
    cotizaciones={}
    solicitud={}

    def cargar(event=None):
        datos_s=datos.obtener_solicitud(solicitud_id)
        if not datos_s:cerrar_vista(win);return
        solicitud.clear();solicitud.update(datos_s)
        resumen.configure(text=f"#{datos_s['numero']} · {datos_s['servicio']} · {datos_s['estado_texto']}")
        texto=(f"Trabajador: {datos_s['trabajador']} · {datos_s['zona']}\nCliente: {datos_s['cliente']}\n"
            f"Contacto: {datos_s['contacto']}\nDomicilio: {datos_s['domicilio']}\n"
            f"Fecha deseada: {fecha_corta(datos_s['fecha'])} · {datos_s['horario']} · Prioridad: {datos_s['urgencia']}\nTrabajo: {datos_s['descripcion']}")
        info.configure(state="normal");info.delete("1.0","end");info.insert("1.0",texto);info.configure(state="disabled")
        for fila in cot.get_children():cot.delete(fila)
        cotizaciones.clear()
        for q in datos_s["cotizaciones"]:
            cotizaciones[q["id"]]=q
            cot.insert("","end",iid=q["id"],values=(f"${q['importe']:,.2f}",
                "Incluidos" if q["materiales_incluidos"] else "Por separado",q["estado"].replace("_"," ").capitalize()))
        if not cotizaciones:mostrar_condiciones("Aún no hay cotizaciones. Puedes crear una desde la simulación de seguimiento.")
        else:
            mostrar_condiciones("Selecciona una cotización para revisar sus condiciones y el reparto de ejemplo.")
            elegida=next((q['id'] for q in datos_s['cotizaciones'] if q['estado']=='aceptada'),datos_s['cotizaciones'][0]['id'])
            cot.selection_set(elegida)
        aceptar_btn.state(["disabled"])

    def elegir(event=None):
        filas=cot.selection()
        q=cotizaciones.get(filas[0]) if filas else None
        if q:
            d=q["desglose"]
            mostrar_condiciones(f"{q['condiciones']}\n\nReparto de ejemplo: total cliente {dinero(d['total'])} MXN. "
                f"Comisión Ofivanta ({d['porcentaje']} %): {dinero(d['comision'])}. Neto trabajador: {dinero(d['neto'])}. "
                "La comisión está incluida en el total. No hay cobro real.")
            aceptar_btn.state(["!disabled"] if q["estado"]=="pendiente" and solicitud["estado"]=="cotizada" else ["disabled"])

    def aceptar():
        filas=cot.selection()
        if not filas:return
        q=cotizaciones[filas[0]]
        mensaje=(f"¿Aceptar la cotización por ${q['importe']:,.2f} MXN?\n"
            f"Materiales: {'incluidos' if q['materiales_incluidos'] else 'se cobran por separado'}\n\n{q['condiciones']}\n\n"
            "Esto confirma la solicitud en el prototipo. No se realiza ningún pago.")
        if not messagebox.askyesno("Aceptar cotización",mensaje,parent=win.winfo_toplevel()):return
        try:datos.aceptar_cotizacion(q["id"])
        except (ValueError,OSError,datos.sqlite3.Error) as error:aviso_error(win,error);return
        cargar();notificar_cambio(win)
        if on_change:on_change()

    aceptar_btn=ttk.Button(botones,text="Aceptar cotización",style="Primary.TButton",command=aceptar)
    aceptar_btn.pack(side="left")
    def seguimiento():
        from .win_canvas import open_win_canvas
        open_win_canvas(win,solicitud_id)
    ttk.Button(botones,text="Ver seguimiento",command=seguimiento).pack(side="left",padx=8)
    ttk.Button(botones,text="Cerrar",command=lambda:cerrar_vista(win)).pack(side="right")
    cot.bind("<<TreeviewSelect>>",elegir);win.bind("<<DatosActualizados>>",cargar)
    cargar();return win
