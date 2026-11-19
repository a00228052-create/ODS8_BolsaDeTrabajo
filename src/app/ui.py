"""Colores y piezas pequeñas para que las ventanas se vean iguales."""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import sqlite3
from pathlib import Path
from math import sqrt

FONDO = "#F5F7FB"
TEXTO = "#111827"
GRIS = "#64748B"
PRIMARIO = "#2563EB"
ACENTO = "#1D4ED8"
SUAVE = "#DBEAFE"
BORDE = "#E2E8F0"
AZUL = "#111827"
# Estos nombres se conservan para los archivos de las sesiones anteriores.
VERDE = PRIMARIO


def aplicar_estilo(parent):
    root = parent.winfo_toplevel()._root()
    if getattr(root, "_estilo_ofivanta", False):
        return
    root._estilo_ofivanta = True
    estilo = ttk.Style(root)
    estilo.theme_use("clam")
    tkfont.nametofont("TkDefaultFont", root=root).configure(family="Segoe UI", size=10)
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("TLabel", background=FONDO, foreground=TEXTO, font=("Segoe UI",10))
    estilo.configure("Muted.TLabel", foreground=GRIS)
    estilo.configure("Title.TLabel", font=("Segoe UI",22,"bold"))
    estilo.configure("Subtitle.TLabel", font=("Segoe UI",12,"bold"))
    estilo.configure("Small.TLabel", font=("Segoe UI",9), foreground=GRIS)
    estilo.configure("Accent.TLabel", foreground=VERDE, font=("Segoe UI",11,"bold"))
    estilo.configure("Tab.TButton", padding=(18,10), borderwidth=0)
    estilo.configure("Active.Tab.TButton", background=SUAVE, foreground=PRIMARIO, borderwidth=0)
    estilo.map("Active.Tab.TButton", background=[("active","#BFDBFE")])
    estilo.configure("TButton", font=("Segoe UI",10), padding=(14,9), background="white", foreground=TEXTO, borderwidth=1)
    estilo.map("TButton", background=[("active","#EFF6FF")], foreground=[("disabled","#94A3B8")])
    estilo.configure("Primary.TButton", background=VERDE, foreground="white", borderwidth=0)
    estilo.map("Primary.TButton", background=[("disabled","#BDD0F5"),("active","#1D4ED8")], foreground=[("disabled","white")])
    estilo.configure("Accent.TButton", background=ACENTO, foreground="white", borderwidth=0)
    estilo.configure("Hero.TButton",background="white",foreground="#1E40AF",borderwidth=0,font=("Segoe UI",10,"bold"))
    estilo.map("Hero.TButton",background=[("active","#DBEAFE")],foreground=[("active","#1E40AF")])
    estilo.map("Accent.TButton", background=[("active","#1E40AF")], foreground=[("active","white")])
    estilo.configure("Danger.TButton", foreground="#B43E43")
    estilo.configure("TEntry", padding=7, fieldbackground="white")
    estilo.configure("TCombobox", padding=7, fieldbackground="white")
    estilo.map("TCombobox", fieldbackground=[("readonly","white")], foreground=[("readonly",TEXTO)])
    estilo.configure("TCheckbutton", background=FONDO, foreground=TEXTO)
    estilo.configure("Treeview", background="white", fieldbackground="white", foreground=TEXTO,
        rowheight=38, borderwidth=0, font=("Segoe UI",10))
    estilo.configure("Treeview.Heading", background="#F1F5F9", foreground=TEXTO,
        padding=(8,10), font=("Segoe UI",10,"bold"), relief="flat")
    estilo.map("Treeview", background=[("selected",SUAVE)], foreground=[("selected",TEXTO)])
    estilo.configure("TNotebook", background=FONDO, borderwidth=0)
    estilo.configure("TNotebook.Tab", background="#E8EEF8", foreground=TEXTO, padding=(20,11), font=("Segoe UI",10))
    estilo.map("TNotebook.Tab", background=[("selected","white")], foreground=[("selected",PRIMARIO)])
    estilo.configure("TLabelframe", background=FONDO, bordercolor=BORDE)
    estilo.configure("TLabelframe.Label", background=FONDO, foreground=GRIS)
    redondear_controles(root,estilo)


def crear_ventana(parent, titulo, ancho=980, alto=650):
    aplicar_estilo(parent)
    raiz=parent._root()
    if hasattr(raiz,"navegador"):
        return raiz.navegador.crear(titulo)
    win = tk.Toplevel(parent)
    win.title("Ofivanta | " + titulo)
    win.configure(bg=FONDO)
    icono = cargar_logo(win, 32)
    if icono is not None:
        win.iconphoto(False, icono)
        win._icono = icono
    ancho = min(ancho, win.winfo_screenwidth()-80)
    alto = min(alto, win.winfo_screenheight()-100)
    x = max(20, (win.winfo_screenwidth()-ancho)//2)
    y = max(20, (win.winfo_screenheight()-alto)//2-20)
    win.geometry(f"{ancho}x{alto}+{x}+{y}")
    win.minsize(min(ancho,680), min(alto,480))
    return win


def encabezado(parent, titulo, descripcion):
    box = ttk.Frame(parent)
    box.pack(fill="x", pady=(0,18))
    ttk.Label(box, text=titulo, style="Title.TLabel").pack(anchor="w")
    ttk.Label(box, text=descripcion, style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=(5,0))


def tarjeta(parent, **kwargs):
    card=tk.Frame(parent,bg="white",**kwargs)
    try:
        fondo=parent.cget("background")
    except tk.TclError:
        fondo=FONDO
    lienzo=tk.Canvas(card,bg=fondo,highlightthickness=0)
    px=card.winfo_pixels(card.cget("padx"))
    py=card.winfo_pixels(card.cget("pady"))
    lienzo.place(x=-px,y=-py,relwidth=1,relheight=1,width=px*2,height=py*2)
    lienzo.tk.call("lower",lienzo._w)
    def dibujar(event=None):
        lienzo.delete("all")
        ancho,alto=lienzo.winfo_width(),lienzo.winfo_height()
        r=min(14,ancho/2,alto/2)
        puntos=[r,1,ancho-r,1,ancho-1,1,ancho-1,r,ancho-1,alto-r,
            ancho-1,alto-1,ancho-r,alto-1,r,alto-1,1,alto-1,1,alto-r,1,r,1,1]
        lienzo.create_polygon(puntos,smooth=True,splinesteps=24,fill="white",outline=BORDE,width=1)
    lienzo.bind("<Configure>",dibujar)
    return card


def etiqueta(parent, texto, grande=False, color=TEXTO):
    return tk.Label(parent, text=texto, bg=parent.cget("background"), fg=color,
        font=("Segoe UI", 13 if grande else 10, "bold" if grande else "normal"), anchor="w", justify="left")


def aviso_error(win, error):
    if isinstance(error, sqlite3.Error):
        mensaje = "No se pudieron guardar o leer los datos. Cierra otras copias de la app e inténtalo de nuevo."
    else:
        mensaje = str(error)
    messagebox.showerror("Revisa estos datos", mensaje, parent=win.winfo_toplevel())


def notificar_cambio(parent):
    root = parent._root()
    def recorrer(widget):
        if widget == root or isinstance(widget, (tk.Toplevel,Pantalla)):
            widget.event_generate("<<DatosActualizados>>", when="tail")
        for hijo in widget.winfo_children():
            recorrer(hijo)
    recorrer(root)


def fecha_legible(valor):
    from datetime import datetime
    try:
        return datetime.fromisoformat(valor).astimezone().strftime("%d/%m/%Y %H:%M")
    except (ValueError,TypeError):
        return str(valor)


def dinero(valor):
    return f"${valor:,.2f}"


def fecha_corta(valor):
    from datetime import date
    try:
        return date.fromisoformat(valor).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(valor)


def cargar_logo(parent, tamano=64):
    root=parent._root()
    if not hasattr(root,"_logos_ofivanta"):
        root._logos_ofivanta={}
    if tamano in root._logos_ofivanta:
        return root._logos_ofivanta[tamano]
    ruta = Path(__file__).resolve().parents[2] / "assets" / "ofivanta_logo_azul.png"
    if not ruta.exists():
        return None
    if not hasattr(root,"_logo_original"):
        root._logo_original=tk.PhotoImage(master=root,file=str(ruta))
    original = root._logo_original
    factor = max(1, round(original.width() / tamano))
    root._logos_ofivanta[tamano]=original.subsample(factor, factor)
    return root._logos_ofivanta[tamano]


def dibujar_degradado(canvas, inicio="#111827", final="#2563EB"):
    """Un fondo horizontal dibujado con tkinter, sin instalar bibliotecas."""
    ancho=max(1,canvas.winfo_width())
    alto=max(1,canvas.winfo_height())
    colores=[tuple(int(valor[i:i+2],16) for i in (1,3,5)) for valor in (inicio,final)]
    for paso in range(100):
        proporcion=paso/99
        rgb=[round(a+(b-a)*proporcion) for a,b in zip(*colores)]
        color='#{:02x}{:02x}{:02x}'.format(*rgb)
        canvas.create_rectangle(ancho*paso/100,0,ancho*(paso+1)/100+1,alto,fill=color,outline="")


def imagen_redonda(root, relleno, borde, radio=12):
    """Fondo pequeño que ttk estira conservando las esquinas redondas."""
    lado=radio*2+8
    imagen=tk.PhotoImage(master=root,width=lado,height=lado)
    for y in range(lado):
        distancia=radio-y-.5 if y<radio else y-(lado-radio)+.5 if y>=lado-radio else 0
        margen=round(radio-sqrt(max(0,radio*radio-distancia*distancia))) if distancia else 0
        imagen.put(borde,to=(margen,y,lado-margen,y+1))
        if 0<y<lado-1:
            imagen.put(relleno,to=(margen+1,y,lado-margen-1,y+1))
    return imagen


def redondear_controles(root, estilo):
    # Se mantienen ttk.Button, su teclado y sus funciones originales.
    root._fondos_botones=[]
    estilos=[
        ("TButton","white","#EFF6FF",BORDE,TEXTO),
        ("Primary.TButton",PRIMARIO,"#1D4ED8",PRIMARIO,"white"),
        ("Accent.TButton",ACENTO,"#1E40AF",ACENTO,"white"),
        ("Hero.TButton","white","#DBEAFE","white","#1E40AF"),
        ("Danger.TButton","#FFF1F2","#FFE4E6","#FECDD3","#9F1239"),
        ("Sidebar.TButton",AZUL,"#1E3A5F",AZUL,"white"),
        ("Selected.Sidebar.TButton","#1E3A5F","#234B78","#1E3A5F","white"),
        ("Tab.TButton","white","#EFF6FF",BORDE,TEXTO),
        ("Active.Tab.TButton",SUAVE,"#BFDBFE",SUAVE,PRIMARIO),
    ]
    for indice,(nombre,normal,activo,borde,texto) in enumerate(estilos):
        imagenes=[imagen_redonda(root,normal,borde),imagen_redonda(root,activo,activo),
                  imagen_redonda(root,"#E2E8F0","#E2E8F0")]
        root._fondos_botones.extend(imagenes)
        elemento=f"Ofivanta{indice}.border"
        estilo.element_create(elemento,"image",imagenes[0],("disabled",imagenes[2]),
            ("pressed",imagenes[1]),("active",imagenes[1]),border=12,padding=0,sticky="nsew")
        estilo.layout(nombre,[(elemento,{"sticky":"nsew","children":[
            ("Button.focus",{"sticky":"nsew","children":[
                ("Button.padding",{"sticky":"nsew","children":[("Button.label",{"sticky":"nsew"})]})]})]})])
        estilo.configure(nombre,foreground=texto,padding=(16,10),borderwidth=0)
        fondo=AZUL if "Sidebar" in nombre else FONDO
        estilo.configure(nombre,background=fondo)
        estilo.map(nombre,background=[("disabled",fondo),("!disabled",fondo)])
        estilo.map(nombre,foreground=[("disabled","#64748B"),("active",texto),("!disabled",texto)])
    estilo.configure("Sidebar.TButton",anchor="w",padding=(16,15))
    estilo.configure("Selected.Sidebar.TButton",anchor="w",padding=(16,15))

    def adaptar_fondo(event):
        boton=event.widget
        if not isinstance(boton,ttk.Button):return
        nombre=boton.cget("style") or "TButton"
        if nombre.startswith("Fondo"):
            nombre=nombre.split(".",1)[1]
        padre=boton.master
        try:
            color=padre.cget("background")
        except tk.TclError:
            color=FONDO
        if isinstance(padre,tk.Canvas):
            # El botón de la portada usa un fondo azul cercano al degradado.
            color="#192B4D" if nombre=="Hero.TButton" else color
        variante="Fondo"+color.replace("#","")+"."+nombre
        estilo.configure(variante,background=color)
        estilo.map(variante,background=[("disabled",color),("!disabled",color)])
        boton.configure(style=variante)

    root.bind_class("TButton","<Map>",adaptar_fondo,add="+")


class Pantalla(ttk.Frame):
    """Una sección dentro de la ventana principal."""
    def __init__(self,parent,navegador,titulo):
        super().__init__(parent)
        self.navegador=navegador
        self.titulo=titulo


class Navegador:
    def __init__(self,contenedor,al_cambiar=None):
        self.contenedor=contenedor
        self.al_cambiar=al_cambiar
        self.paginas={}
        self.historial=[]
        self.actual=None
        contenedor.rowconfigure(0,weight=1)
        contenedor.columnconfigure(0,weight=1)

    def crear(self,titulo):
        anterior=self.paginas.get(titulo)
        if anterior is not None:
            self.eliminar(anterior)
        pantalla=Pantalla(self.contenedor,self,titulo)
        self.paginas[titulo]=pantalla
        self.mostrar(pantalla)
        return pantalla

    def mostrar(self,pantalla):
        if self.actual is not None and self.actual.winfo_exists():
            self.actual.grid_remove()
        if pantalla in self.historial:
            self.historial=self.historial[:self.historial.index(pantalla)+1]
        else:
            self.historial.append(pantalla)
        pantalla.grid(row=0,column=0,sticky="nsew")
        pantalla.tkraise()
        self.actual=pantalla
        if self.al_cambiar:self.al_cambiar(pantalla.titulo)

    def volver(self):
        if len(self.historial)<2:return
        self.historial.pop()
        self.mostrar(self.historial[-1])

    def eliminar(self,pantalla):
        self.historial=[p for p in self.historial if p is not pantalla]
        if self.paginas.get(pantalla.titulo) is pantalla:
            self.paginas.pop(pantalla.titulo)
        if self.actual is pantalla:self.actual=None
        pantalla.destroy()

    def cerrar(self,pantalla):
        visible=self.actual is pantalla
        self.eliminar(pantalla)
        if visible and self.historial:self.mostrar(self.historial[-1])


def cerrar_vista(vista):
    if isinstance(vista,Pantalla):
        vista.navegador.cerrar(vista)
    else:
        vista.destroy()
