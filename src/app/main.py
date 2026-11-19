"""Menú principal de Ofivanta y navegación entre sus cinco secciones."""
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from .ui import aplicar_estilo, cargar_logo, Navegador, AZUL, FONDO
from .win_home import construir_inicio
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
        except (AttributeError, OSError):
            pass
    root = tk.Tk()
    root.title("Ofivanta | Servicios para tu hogar")
    ancho = min(1280, root.winfo_screenwidth() - 80)
    alto = min(830, root.winfo_screenheight() - 90)
    root.geometry(f"{ancho}x{alto}")
    root.minsize(min(1120, ancho), min(720, alto))
    root.configure(bg=FONDO)
    aplicar_estilo(root)
    icono = cargar_logo(root, 32)
    if icono is not None:
        root.iconphoto(True, icono)
        root._icono = icono
    try:
        datos.inicializar_base()
    except (OSError, datos.sqlite3.Error) as error:
        messagebox.showerror("No se pudo iniciar Ofivanta", str(error), parent=root)
        root.destroy()
        return

    lateral = tk.Frame(root, bg=AZUL, width=225, padx=14, pady=24)
    lateral.pack(side="left", fill="y")
    lateral.pack_propagate(False)
    cuerpo = ttk.Frame(root)
    cuerpo.pack(side="left", fill="both", expand=True)
    cabecera = ttk.Frame(cuerpo, padding=(22, 12))
    cabecera.pack(fill="x")
    volver_btn = ttk.Button(cabecera, text="Volver", command=lambda: root.navegador.volver())
    volver_btn.pack(side="left", padx=(0, 16))
    ubicacion = ttk.Label(cabecera, text="Inicio", style="Accent.TLabel")
    ubicacion.pack(side="left")
    ttk.Label(cabecera, text="Ofivanta", style="Small.TLabel").pack(side="right")
    contenedor = ttk.Frame(cuerpo)
    contenedor.pack(fill="both", expand=True)
    botones_menu = {}
    ventanas = {}
    root._vista_inicio = "cliente"

    def actualizar_navegacion(titulo):
        nombre = titulo
        if titulo == "Inicio" and root._vista_inicio == "negocio":
            nombre = "Planes e ingresos"
        ubicacion.configure(text=nombre)
        volver_btn.state(["!disabled"] if len(root.navegador.historial) > 1 else ["disabled"])
        grupo = {"Solicitar servicio": "Buscar servicio", "Detalle de solicitud": "Mis solicitudes",
                 "Cotización de ejemplo": "Seguimiento"}.get(nombre, nombre)
        for texto, boton in botones_menu.items():
            boton.configure(style="Selected.Sidebar.TButton" if texto == grupo else "Sidebar.TButton")

    root.navegador = Navegador(contenedor, actualizar_navegacion)

    def abrir(nombre, funcion, *args):
        anterior = ventanas.get(nombre)
        if anterior is not None and anterior.winfo_exists():
            if args and args[0] is not None and hasattr(anterior, "seleccionar_categoria"):
                anterior.seleccionar_categoria(args[0])
            elif hasattr(anterior, "actualizar"):
                anterior.actualizar()
            root.navegador.mostrar(anterior)
            return anterior
        vista = funcion(root, *args)
        if hasattr(vista, "ventana"):
            vista = vista.ventana
        ventanas[nombre] = vista
        return vista

    def catalogo(categoria=None):
        return abrir("catalogo", open_win_list, categoria)

    def solicitudes():
        return abrir("solicitudes", open_win_table)

    def seguimiento():
        return abrir("seguimiento", open_win_canvas)

    def inicio(vista="cliente"):
        root._vista_inicio = vista
        home.mostrar_vista(vista)
        root.navegador.mostrar(pagina_inicio)
        scroll.yview_moveto(0)

    def ver_solicitud(identificador):
        historial = solicitudes()
        historial.actualizar()
        historial.tabla.selection_set(identificador)
        historial.tabla.see(identificador)

    root.ver_solicitud = ver_solicitud
    marca = tk.Frame(lateral, bg=AZUL)
    marca.pack(fill="x")
    logo = cargar_logo(root, 42)
    if logo is not None:
        imagen = tk.Canvas(marca, width=46, height=46, bg=AZUL, highlightthickness=0)
        imagen.create_oval(0, 0, 45, 45, fill="white", outline="")
        imagen.create_image(23, 23, image=logo)
        imagen.image = logo
        imagen.pack(side="left", padx=(0, 7))
    tk.Label(marca, text="Ofivanta", bg=AZUL, fg="white", font=("Segoe UI", 19, "bold")).pack(side="left")
    tk.Label(lateral, text="Servicios para tu hogar", bg=AZUL, fg="#CBD5E1", font=("Segoe UI", 9)).pack(anchor="w", pady=(12, 30))
    tk.Label(lateral, text="TU ESPACIO", bg=AZUL, fg="#60A5FA", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 10))
    for texto, accion in [("Inicio", inicio), ("Buscar servicio", catalogo), ("Mis solicitudes", solicitudes),
                           ("Seguimiento", seguimiento), ("Planes e ingresos", lambda: inicio("negocio"))]:
        boton = ttk.Button(lateral, text=texto, command=accion, style="Sidebar.TButton", cursor="hand2")
        boton.pack(fill="x", pady=3)
        botones_menu[texto] = boton
    ttk.Button(lateral, text="Salir", command=root.destroy, style="Sidebar.TButton").pack(side="bottom", fill="x")
    tk.Label(lateral, text="Proyecto ODS 8\nEquipo Ofivanta", bg=AZUL, fg="#94A3B8", justify="left",
             font=("Segoe UI", 9)).pack(side="bottom", anchor="w", pady=18)

    pagina_inicio = root.navegador.crear("Inicio")
    scroll = tk.Canvas(pagina_inicio, bg=FONDO, highlightthickness=0)
    barra = ttk.Scrollbar(pagina_inicio, orient="vertical", command=scroll.yview)
    scroll.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    scroll.pack(side="left", fill="both", expand=True)
    pagina_inicio.scroll_canvas = scroll
    home = construir_inicio(scroll, catalogo, solicitudes, seguimiento, mostrar_pestanas=False)
    contenido = scroll.create_window((0, 0), window=home, anchor="nw")
    home.bind("<Configure>", lambda evento: scroll.configure(scrollregion=scroll.bbox("all")))
    scroll.bind("<Configure>", lambda evento: scroll.itemconfigure(contenido, width=evento.width))

    def desplazar(evento):
        if isinstance(evento.widget, (tk.Text, ttk.Treeview, ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            return
        actual = root.navegador.actual
        canvas = getattr(actual, "scroll_canvas", None)
        if canvas is not None and canvas.winfo_exists() and evento.delta:
            canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units")

    root.bind("<MouseWheel>", desplazar)
    root.bind("<<DatosActualizados>>", home.actualizar)
    root.inicio = home
    root.scroll_inicio = scroll
    root.botones_menu = botones_menu
    menu = tk.Menu(root)
    ventanas_menu = tk.Menu(menu, tearoff=False)
    for texto, accion in [("Inicio", inicio), ("Solicitar servicio", lambda: abrir("formulario", open_win_form)),
                           ("Buscar servicio", catalogo), ("Mis solicitudes", solicitudes), ("Seguimiento", seguimiento)]:
        ventanas_menu.add_command(label=texto, command=accion)
    menu.add_cascade(label="Ir a", menu=ventanas_menu)
    ayuda = tk.Menu(menu, tearoff=False)
    ayuda.add_command(label="Cómo usar Ofivanta", command=lambda: messagebox.showinfo("Cómo usar Ofivanta",
        "1. Busca un oficio y elige un trabajador.\n2. Describe el trabajo y envía la solicitud.\n"
        "3. Revisa la cotización en Mis solicitudes.\n4. Consulta el avance en Seguimiento.\n\n"
        "Usa Volver para regresar o el menú lateral para cambiar de sección.\n"
        "Es una demostración local, sin cobros reales.", parent=root))
    menu.add_cascade(label="Ayuda", menu=ayuda)
    root.configure(menu=menu)
    root.menu_ventanas = ventanas_menu
    actualizar_navegacion("Inicio")
    root.mainloop()
    return root


if __name__ == "__main__":
    main()
