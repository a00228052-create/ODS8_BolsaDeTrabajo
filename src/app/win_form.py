"""Formulario para solicitar un servicio a un trabajador del catálogo."""
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from ..core.datos import guardar_solicitud as _guardar_solicitud
from ..core import datos
from .ui import cerrar_vista, crear_ventana, encabezado, tarjeta, etiqueta, aviso_error, notificar_cambio, FONDO, GRIS, VERDE


class VentanaSolicitud:
    def __init__(self,parent,servicio=None,trabajador=None,guardar_callback=None,on_close=None,on_submit=None):
        self.servicio=servicio
        self.trabajador=trabajador
        self.guardar_callback=guardar_callback if guardar_callback is not None else _guardar_solicitud
        self.on_close=on_close
        self.on_submit=on_submit
        self.guardando=False
        self.ventana=crear_ventana(parent,"Solicitar servicio",760,730)
        self.ventana.formulario=self
        if isinstance(self.ventana,tk.Toplevel):
            self.ventana.transient(parent.winfo_toplevel())
            self.ventana.protocol("WM_DELETE_WINDOW",self.cerrar)
        frame=ttk.Frame(self.ventana,padding=22);frame.pack(fill="both",expand=True)
        encabezado(frame,"Cuéntanos qué necesitas","Envía una solicitud. El precio y la fecha de atención se acuerdan en la cotización.")
        pie=ttk.Frame(frame);pie.pack(side="bottom",fill="x",pady=(12,0))
        ttk.Button(pie,text="Cancelar",command=self.cerrar).pack(side="left")
        self.enviar_btn=ttk.Button(pie,text="Revisar y enviar solicitud",style="Primary.TButton",command=self.validar_y_confirmar)
        self.enviar_btn.pack(side="right")

        area=ttk.Frame(frame);area.pack(fill="both",expand=True)
        canvas=tk.Canvas(area,bg=FONDO,highlightthickness=0)
        self.canvas=canvas
        self.ventana.scroll_canvas=canvas
        barra=ttk.Scrollbar(area,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=barra.set);canvas.pack(side="left",fill="both",expand=True);barra.pack(side="right",fill="y")
        contenido=ttk.Frame(canvas)
        elemento=canvas.create_window((0,0),window=contenido,anchor="nw")
        contenido.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfigure(elemento,width=e.width))
        if isinstance(self.ventana,tk.Toplevel):
            self.ventana.bind("<MouseWheel>",lambda e:canvas.yview_scroll(-1 if e.delta>0 else 1,"units"))

        seleccion=tarjeta(contenido,padx=16,pady=14);seleccion.pack(fill="x",pady=(0,14))
        etiqueta(seleccion,"SERVICIO Y TRABAJADOR",color=GRIS).pack(anchor="w")
        self.lbl_servicio=etiqueta(seleccion,self.texto_seleccion(servicio),grande=True,color=VERDE)
        self.lbl_servicio.pack(anchor="w",pady=(6,4))
        self.lbl_trabajador=etiqueta(seleccion,self.texto_seleccion(trabajador));self.lbl_trabajador.pack(anchor="w")
        if isinstance(trabajador,dict):
            etiqueta(seleccion,"Zona: "+trabajador.get("zona","Por acordar"),color=GRIS).pack(anchor="w",pady=(6,0))
        if not servicio or not trabajador:
            def elegir():
                raiz=self.ventana._root()
                self.cerrar()
                from .win_list import open_win_list
                open_win_list(raiz)
            ttk.Button(seleccion,text="Elegir en el catálogo",command=elegir).pack(anchor="w",pady=(10,0))

        self.nombre=tk.StringVar();self.contacto=tk.StringVar();self.domicilio=tk.StringVar()
        self.fecha=tk.StringVar(value=date.today().isoformat())
        self.horario=tk.StringVar(value="Por acordar")
        self.urgencia=tk.StringVar(value="Normal")
        campos=tarjeta(contenido,padx=16,pady=16);campos.pack(fill="x")
        self._campo(campos,"Nombre completo",self.nombre)
        self._campo(campos,"Teléfono o correo de contacto",self.contacto)
        self._campo(campos,"Domicilio donde necesitas el servicio",self.domicilio)
        self._campo(campos,"Fecha deseada (AAAA-MM-DD)",self.fecha)
        fechas=tk.Frame(campos,bg="white");fechas.pack(fill="x",pady=(6,0))
        ttk.Button(fechas,text="Hoy",command=lambda:self.fecha.set(date.today().isoformat())).pack(side="left")
        ttk.Button(fechas,text="Mañana",command=lambda:self.fecha.set((date.today()+timedelta(days=1)).isoformat())).pack(side="left",padx=8)
        preferencias=tk.Frame(campos,bg="white");preferencias.pack(fill="x",pady=(12,0))
        preferencias.columnconfigure(0,weight=1);preferencias.columnconfigure(1,weight=1)
        etiqueta(preferencias,"Horario preferido").grid(row=0,column=0,sticky="w",pady=(0,5))
        etiqueta(preferencias,"Prioridad").grid(row=0,column=1,sticky="w",pady=(0,5))
        ttk.Combobox(preferencias,textvariable=self.horario,values=datos.HORARIOS,state="readonly").grid(row=1,column=0,sticky="ew",padx=(0,10))
        ttk.Combobox(preferencias,textvariable=self.urgencia,values=datos.URGENCIAS,state="readonly").grid(row=1,column=1,sticky="ew")
        etiqueta(campos,"Describe el trabajo").pack(anchor="w",pady=(10,5))
        self.descripcion=tk.Text(campos,height=4,wrap="word",font=("Segoe UI",10),relief="solid",bd=1,padx=8,pady=8)
        self.descripcion.pack(fill="x")
        self.contador=etiqueta(campos,"0 / 3000 caracteres",color=GRIS)
        self.contador.pack(anchor="e",pady=(4,0))
        self.descripcion.bind("<<Modified>>",self.actualizar_contador)
        ttk.Button(campos,text="Usar descripción de ejemplo",command=self.usar_ejemplo).pack(anchor="w",pady=(8,0))
        etiqueta(campos,"Ejemplo: hay una fuga debajo del lavabo y necesito una revisión.",color=GRIS).pack(anchor="w",pady=(6,0))
        ttk.Label(contenido,text="La fecha y el horario son preferencias. El trabajador debe confirmar disponibilidad. "
            "El precio se acuerda después; aquí no hay pagos.",
            style="Muted.TLabel",wraplength=640).pack(anchor="w",pady=(12,6))
        self.ventana.bind("<Control-Return>",lambda e:self.validar_y_confirmar())

    @staticmethod
    def texto_seleccion(valor):
        return str(valor.get("nombre","Sin selección")) if isinstance(valor,dict) else str(valor or "Sin selección")

    def _campo(self,parent,texto,variable):
        etiqueta(parent,texto).pack(anchor="w",pady=(8,4))
        entrada=ttk.Entry(parent,textvariable=variable)
        entrada.pack(fill="x")
        if variable is self.nombre:entrada.focus_set()

    def actualizar_contador(self,event=None):
        if not self.descripcion.edit_modified():return
        cantidad=len(self.descripcion.get("1.0","end-1c"))
        self.contador.configure(text=f"{cantidad} / 3000 caracteres",fg=GRIS if cantidad<=3000 else "#A73A45")
        self.descripcion.edit_modified(False)

    def usar_ejemplo(self):
        ejemplos={"serv-plomeria":"Hay una fuga debajo del lavabo. Necesito revisar la conexión y reparar la fuga.",
            "serv-electricidad":"Un contacto de la sala dejó de funcionar. Necesito revisar la instalación.",
            "serv-limpieza":"Necesito limpieza general de una casa de dos habitaciones. Quisiera acordar qué materiales incluye.",
            "serv-pintura":"Quiero pintar las paredes de una habitación. Necesito una cotización de mano de obra y materiales."}
        if self.descripcion.get("1.0","end").strip():
            if not messagebox.askyesno("Cambiar descripción","¿Reemplazar tu descripción por un ejemplo editable?",parent=self.ventana.winfo_toplevel()):return
        self.descripcion.delete("1.0","end")
        self.descripcion.insert("1.0",ejemplos.get(self.servicio.get("id") if isinstance(self.servicio,dict) else "",
            "Necesito ayuda con un trabajo en casa. Quisiera acordar una revisión, el alcance y el costo."))

    def _validar(self):
        if not isinstance(self.servicio,dict) or not isinstance(self.trabajador,dict):
            messagebox.showwarning("Elige un servicio","Selecciona el oficio y el trabajador desde el catálogo.",parent=self.ventana.winfo_toplevel())
            return None
        campos={"cliente":self.nombre.get().strip(),"contacto":self.contacto.get().strip(),
            "domicilio":self.domicilio.get().strip(),"descripcion":self.descripcion.get("1.0","end").strip(),
            "fecha_deseada":self.fecha.get().strip(),"servicio":self.servicio.copy(),
            "trabajador":self.trabajador.copy(),"estado":"Pendiente",
            "horario":self.horario.get(),"urgencia":self.urgencia.get()}
        try:datos.validar_campos(campos["cliente"],campos["contacto"],campos["domicilio"],campos["descripcion"],campos["fecha_deseada"])
        except ValueError as error:aviso_error(self.ventana,error);return None
        return campos

    def validar_y_confirmar(self):
        if self.guardando:return
        campos=self._validar()
        if campos is None:return
        resumen=(f"Servicio: {self.texto_seleccion(self.servicio)}\nTrabajador: {self.texto_seleccion(self.trabajador)}\n"
            f"Nombre: {campos['cliente']}\nContacto: {campos['contacto']}\nDomicilio: {campos['domicilio']}\n"
            f"Fecha deseada: {campos['fecha_deseada']}\nHorario preferido: {campos['horario']}\nPrioridad: {campos['urgencia']}\n\n{campos['descripcion']}\n\n"
            "Se registrará como Pendiente. La cotización se acepta después y no se realiza ningún pago.\n\n¿Enviar solicitud?")
        if messagebox.askyesno("Revisar solicitud",resumen,parent=self.ventana.winfo_toplevel()):self._guardar(campos)

    def _guardar(self,campos):
        self.guardando=True;self.enviar_btn.state(["disabled"])
        try:
            resultado=self.guardar_callback(campos)
            identificador=resultado.get("id") if isinstance(resultado,dict) else resultado
            if not identificador:raise ValueError("No se recibió una confirmación de guardado. Revisa la integración del formulario.")
        except (ValueError,OSError,datos.sqlite3.Error,TypeError) as error:
            self.guardando=False;self.enviar_btn.state(["!disabled"]);aviso_error(self.ventana,error);return
        notificar_cambio(self.ventana)
        messagebox.showinfo("Solicitud registrada",f"Tu solicitud #{str(identificador)[:8].upper()} quedó pendiente de cotización.\nPuedes consultarla en Mis solicitudes.",parent=self.ventana.winfo_toplevel())
        self.cerrar()
        if self.on_submit:self.on_submit(str(identificador))

    def cerrar(self):
        cerrar_vista(self.ventana)
        if self.on_close:self.on_close()


def open_win_form(parent,servicio=None,trabajador=None,guardar_callback=None,on_close=None,on_submit=None):
    raiz=parent._root()
    if hasattr(raiz,"navegador"):
        anterior=raiz.navegador.paginas.get("Solicitar servicio")
        if anterior is not None and hasattr(anterior,"formulario"):
            formulario=anterior.formulario
            misma_seleccion=(isinstance(servicio,dict) and isinstance(trabajador,dict)
                and isinstance(formulario.servicio,dict) and isinstance(formulario.trabajador,dict)
                and formulario.servicio.get("id")==servicio.get("id")
                and formulario.trabajador.get("id")==trabajador.get("id"))
            if misma_seleccion or servicio is None:
                raiz.navegador.mostrar(anterior)
                return formulario
            tiene_datos=any(v.get().strip() for v in (formulario.nombre,formulario.contacto,formulario.domicilio)) or formulario.descripcion.get("1.0","end").strip()
            if tiene_datos and not messagebox.askyesno("Cambiar trabajador","Hay una solicitud sin enviar. ¿Descartarla para elegir otro trabajador?",parent=raiz):
                raiz.navegador.mostrar(anterior)
                return formulario
    return VentanaSolicitud(parent,servicio,trabajador,guardar_callback,on_close,on_submit)
