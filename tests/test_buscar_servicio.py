import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
from src.core import datos
from src.app.win_list import open_win_list


def widgets(parent,kind):
    resultado=[]
    for hijo in parent.winfo_children():
        if isinstance(hijo,kind):resultado.append(hijo)
        resultado.extend(widgets(hijo,kind))
    return resultado


def boton(win,nombre):return next(b for b in widgets(win,ttk.Button) if b.cget("text")==nombre)


class BuscarServicioTests(unittest.TestCase):
    def setUp(self):
        self.carpeta=tempfile.TemporaryDirectory()
        self.parche=patch.object(datos,"DB_path",Path(self.carpeta.name)/"catalogo.sqlite3");self.parche.start()
        self.root=tk.Tk();self.root.withdraw();self.root.update_idletasks()

    def tearDown(self):
        self.root.update_idletasks();self.root.destroy();self.parche.stop();self.carpeta.cleanup()

    def test_filtra_por_oficio_y_disponibilidad(self):
        win=open_win_list(self.root,"plomeria")
        self.assertEqual(len(win.tabla.get_children()),2)
        win.seleccionar_categoria("serv-electricidad")
        self.assertEqual(len(win.tabla.get_children()),2)
        widgets(win,ttk.Checkbutton)[0].invoke()
        self.assertEqual(win.tabla.get_children(),("3|serv-electricidad",))

    def test_aviso_sin_seleccion_y_no_disponible(self):
        win=open_win_list(self.root)
        with patch("src.app.win_list.messagebox.showwarning") as aviso,patch("src.app.win_list.open_win_form") as form:
            boton(win,"Solicitar servicio").invoke();boton(win,"Seleccionar trabajador").invoke()
            win.tabla.selection_set("4|serv-electricidad");boton(win,"Solicitar servicio").invoke()
            self.assertEqual(aviso.call_count,3);form.assert_not_called()

    def test_pasa_ids_que_existen_en_base(self):
        win=open_win_list(self.root,"plomeria");win.tabla.selection_set("2|serv-plomeria")
        with patch("src.app.win_list.open_win_form") as form:boton(win,"Solicitar servicio").invoke()
        self.assertEqual(form.call_args.kwargs["servicio"]["id"],"serv-plomeria")
        self.assertEqual(form.call_args.kwargs["trabajador"]["id"],"2")

    def test_busqueda_y_catalogo_no_editable(self):
        win=open_win_list(self.root)
        entrada=next(w for w in widgets(win,ttk.Entry) if not isinstance(w,ttk.Combobox))
        entrada.insert(0,"carpinteria")
        self.assertEqual(win.tabla.get_children(),("8|serv-carpinteria",))
        nombres=[b.cget("text") for b in widgets(win,ttk.Button)]
        self.assertFalse(set(nombres)&{"Agregar","Eliminar seleccionado","Limpiar"})


if __name__=="__main__":unittest.main()
