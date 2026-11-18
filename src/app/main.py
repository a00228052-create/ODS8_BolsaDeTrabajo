import tkinter as tk
from tkinter import ttk, messagebox
from .win_home import open_win_home
from .win_form import open_win_form
from .win_list import open_win_list
from .win_canvas import open_win_canvas


def open_win_table(parent):
    # La tabla se carga al abrirla para no bloquear las otras ventanas.
    try:
        from .win_table import open_win_table as abrir_tabla
    except (ImportError, SyntaxError):
        messagebox.showerror(
            "Ventana pendiente",
            "La ventana de solicitudes todavía no está lista. "
            "Puedes seguir usando Buscar servicio.",
            parent=parent,
        )
        return
    return abrir_tabla(parent)

def main():
    root = tk.Tk()
    root.title("Ofivanta - Servicios con confianza")
    root.geometry("480x380")

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Ofivanta · Servicios con confianza", font=("Segoe UI", 12, "bold")).pack(pady=(0, 12))
    ttk.Button(frame, text="1) Home / Bienvenida", command=lambda: open_win_home(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="2) Formulario", command=lambda: open_win_form(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="3) Buscar servicio", command=lambda: open_win_list(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="4) Tabla (Treeview)", command=lambda: open_win_table(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="5) Canvas (Dibujo)", command=lambda: open_win_canvas(root)).pack(pady=4, fill="x")
    ttk.Separator(frame).pack(pady=6, fill="x")
    ttk.Button(frame, text="Salir", command=root.destroy).pack(pady=6)

    root.mainloop()

if __name__ == "__main__":
    main()



