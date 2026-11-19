"""Entrada de Ofivanta: ejecutar con python -m src.app.main."""
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from .ui import aplicar_estilo, cargar_logo, AZUL, FONDO, VERDE
from .win_home import construir_inicio, open_win_home
from .win_list import open_win_list
from .win_form import open_win_form
from .win_table import open_win_table
from .win_canvas import open_win_canvas
from ..core import datos


def main():
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError,OSError):
            pass
    root = tk.Tk()
    root.title("Ofivanta | Servicios para tu hogar")
    root.geometry("1240x790")
    root.minsize(1100,700)
    root.configure(bg=FONDO)
    aplicar_estilo(root)
    icono=cargar_logo(root,32)
    if icono is not None:
        root.iconphoto(True,icono)
        root._icono=icono
    try:
        datos.inicializar_base()
    except (OSError, datos.sqlite3.Error) as error:
        messagebox.showerror("No se pudo iniciar Ofivanta",str(error),parent=root)
        root.destroy()
        return
    ventanas = {}

    def abrir(nombre, funcion, *args):
        anterior = ventanas.get(nombre)
        if anterior is not None and anterior.winfo_exists():
            # Si llega otra categoría, se actualiza el catálogo abierto.
            if args and hasattr(anterior,"seleccionar_categoria"):
                anterior.seleccionar_categoria(args[0])
            anterior.deiconify();anterior.lift();anterior.focus_force()
            return anterior
        win = funcion(root,*args)
        if hasattr(win,"ventana"):win=win.ventana
        ventanas[nombre] = win
        return win

    def catalogo(categoria=None):
        return abrir("catalogo",open_win_list,categoria)

    def solicitudes():return abrir("solicitudes",open_win_table)
    def seguimiento():return abrir("seguimiento",open_win_canvas)

    def inicio(vista="cliente"):
        home.mostrar_vista(vista)
        root.lift()
        root.focus_force()
        scroll.yview_moveto(0)

    def ver_solicitud(identificador):
        historial=solicitudes()
        historial.actualizar()
        historial.tabla.selection_set(identificador)
        historial.tabla.see(identificador)

    root.ver_solicitud=ver_solicitud
    # Las cinco ventanas originales también se pueden abrir desde este menú.
    menu=tk.Menu(root)
    ventanas_menu=tk.Menu(menu,tearoff=False)
    for nombre,accion in [("Inicio",lambda:abrir("inicio",open_win_home)),
        ("Solicitar servicio",lambda:abrir("formulario",open_win_form)),
        ("Buscar servicio",catalogo),("Mis solicitudes",solicitudes),("Seguimiento",seguimiento)]:
        ventanas_menu.add_command(label=nombre,command=accion)
    menu.add_cascade(label="Ir a",menu=ventanas_menu)
    ayuda=tk.Menu(menu,tearoff=False)
    ayuda.add_command(label="Cómo usar Ofivanta",command=lambda:messagebox.showinfo("Cómo usar Ofivanta",
        "1. Busca un oficio y elige un trabajador.\n2. Describe el trabajo y envía la solicitud.\n"
        "3. Revisa la cotización en Mis solicitudes.\n4. Consulta el avance en Seguimiento.\n\n"
        "Planes e ingresos permite probar la suscripción y las comisiones.\nEs una demostración local, sin cobros reales.",parent=root))
    menu.add_cascade(label="Ayuda",menu=ayuda)
    root.configure(menu=menu)
    root.menu_ventanas=ventanas_menu

    lateral = tk.Frame(root,bg=AZUL,width=240,padx=18,pady=24)
    lateral.pack(side="left",fill="y");lateral.pack_propagate(False)
    marca=tk.Frame(lateral,bg=AZUL);marca.pack(fill="x")
    logo=cargar_logo(root,42)
    if logo is not None:
        imagen=tk.Canvas(marca,width=46,height=46,bg=AZUL,highlightthickness=0)
        imagen.create_oval(0,0,45,45,fill="white",outline="")
        imagen.create_image(23,23,image=logo)
        imagen.image=logo;imagen.pack(side="left",padx=(0,9))
    tk.Label(marca,text="Ofivanta",bg=AZUL,fg="white",font=("Segoe UI",20,"bold")).pack(side="left")
    tk.Label(lateral,text="Servicios para tu hogar",bg=AZUL,fg="#CBD5E1",font=("Segoe UI",9)).pack(anchor="w",pady=(12,30))
    tk.Label(lateral,text="TU ESPACIO",bg=AZUL,fg="#60A5FA",font=("Segoe UI",8,"bold")).pack(anchor="w",pady=(0,10))
    botones_menu={}
    def navegar(nombre,accion):
        for texto,boton in botones_menu.items():
            boton.configure(style="Selected.Sidebar.TButton" if texto==nombre else "Sidebar.TButton")
        accion()
    for nombre,accion in [("Inicio",inicio),("Buscar servicio",catalogo),
        ("Mis solicitudes",solicitudes),("Seguimiento",seguimiento),("Planes e ingresos",lambda:inicio("negocio"))]:
        boton=ttk.Button(lateral,text=nombre,command=lambda n=nombre,a=accion:navegar(n,a),style="Sidebar.TButton",cursor="hand2")
        boton.pack(fill="x",pady=3);botones_menu[nombre]=boton
    botones_menu["Inicio"].configure(style="Selected.Sidebar.TButton")
    ttk.Button(lateral,text="Salir",command=root.destroy,style="Sidebar.TButton").pack(side="bottom",fill="x")
    tk.Label(lateral,text="Proyecto ODS 8\nEquipo Ofivanta",bg=AZUL,fg="#94A3B8",justify="left",
        font=("Segoe UI",9)).pack(side="bottom",anchor="w",pady=18)
    cuerpo = ttk.Frame(root)
    cuerpo.pack(side="left",fill="both",expand=True)
    scroll=tk.Canvas(cuerpo,bg=FONDO,highlightthickness=0)
    barra=ttk.Scrollbar(cuerpo,orient="vertical",command=scroll.yview)
    scroll.configure(yscrollcommand=barra.set)
    scroll.pack(side="left",fill="both",expand=True);barra.pack(side="right",fill="y")
    home = construir_inicio(scroll,catalogo,solicitudes,seguimiento,mostrar_pestanas=False)
    contenido=scroll.create_window((0,0),window=home,anchor="nw")
    home.bind("<Configure>",lambda e:scroll.configure(scrollregion=scroll.bbox("all")))
    scroll.bind("<Configure>",lambda e:scroll.itemconfigure(contenido,width=e.width))
    root.bind("<MouseWheel>",lambda e:scroll.yview_scroll(-1 if e.delta>0 else 1,"units"))
    root.bind("<<DatosActualizados>>",home.actualizar)
    root.inicio=home
    root.scroll_inicio=scroll
    root.mainloop()
    return root


if __name__ == "__main__":
    main()
