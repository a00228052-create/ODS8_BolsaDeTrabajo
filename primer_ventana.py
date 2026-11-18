import tkinter as tk
from tkinter import messagebox
ventana = tk.Tk()

ventana.title("OFANTIVA")
ventana.geometry("650x500")
ventana.resizable(False, False)
ventana.configure(bg="#EAEAEA")
contenedor = tk.Frame(ventana, bg="#EAEAEA")
contenedor.pack(fill="both", expand=True)
def limpiar():
    for elemento in contenedor.winfo_children():
        elemento.destroy()
def mostrar_pantalla(funcion):
    limpiar()
    funcion()
def bienvenida():
    titulo = tk.Label(
        contenedor,
        text="¡Bienvenidos a OFANTIVA!",
        font=("Arial", 23, "bold"),
        bg="#EAEAEA",
        fg="#243447"
    )

    titulo.pack(pady=25)

    boton = tk.Button(
        contenedor,
        text="Mostrar mensaje",
        command=lambda: messagebox.showinfo(
            "Bienvenida",
            "¡Bienvenidos a OFANTIVA!"
        )
    )

    boton.pack(pady=20)
bienvenida()
ventana.mainloop()
