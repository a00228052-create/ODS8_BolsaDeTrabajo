"""Pruebas de integración con widgets reales; ejecutar en un escritorio Windows."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
from src.app.win_home import open_win_home
from src.app.win_form import open_win_form
from src.app.win_list import open_win_list
from src.app.win_table import open_win_table
from src.app.win_canvas import open_win_canvas


def widgets(parent, kind):
    result = []
    for child in parent.winfo_children():
        if isinstance(child, kind):
            result.append(child)
        result.extend(widgets(child, kind))
    return result


def button(win, text):
    return next(w for w in widgets(win, ttk.Button) if w.cget('text') == text)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_home_message(self):
        win = open_win_home(self.root)
        with patch('src.app.win_home.messagebox.showinfo') as info:
            button(win, 'Mostrar mensaje').invoke()
            info.assert_called_once()

    def test_form_validation_cancel_and_save(self):
        win = open_win_form(self.root)
        name, age = widgets(win, ttk.Entry)
        with patch('src.app.win_form.messagebox.showerror') as error:
            button(win, 'Guardar').invoke()
            self.assertEqual(error.call_count, 1)
            name.insert(0, 'Persona de prueba')
            age.insert(0, 'abc')
            button(win, 'Guardar').invoke()
            self.assertEqual(error.call_count, 2)
        age.delete(0, 'end')
        age.insert(0, '25')
        with patch('src.app.win_form.filedialog.asksaveasfilename', return_value=''):
            button(win, 'Guardar').invoke()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'perfil.txt'
            with patch('src.app.win_form.filedialog.asksaveasfilename', return_value=str(path)), patch('src.app.win_form.messagebox.showinfo'):
                button(win, 'Guardar').invoke()
            self.assertEqual(path.read_text(encoding='utf-8'), 'Nombre: Persona de prueba\nEdad: 25\n')

    def test_list_add_delete_clear(self):
        win = open_win_list(self.root)
        entry = widgets(win, ttk.Entry)[0]
        lb = widgets(win, tk.Listbox)[0]
        for value in ['Plomería', 'Electricidad']:
            entry.insert(0, value)
            button(win, 'Agregar').invoke()
        self.assertEqual(lb.get(0, 'end'), ('Plomería', 'Electricidad'))
        lb.selection_set(0)
        button(win, 'Eliminar seleccionado').invoke()
        self.assertEqual(lb.get(0, 'end'), ('Electricidad',))
        button(win, 'Limpiar').invoke()
        self.assertEqual(lb.size(), 0)

    def test_table_reads_csv(self):
        win = open_win_table(self.root)
        tree = widgets(win, ttk.Treeview)[0]
        self.assertEqual(len(tree.get_children()), 3)
        self.assertEqual(tree.item(tree.get_children()[0], 'values'), ('Plomería', '10', '20'))

    def test_canvas_has_four_objects(self):
        win = open_win_canvas(self.root)
        canvas = widgets(win, tk.Canvas)[0]
        self.assertEqual([canvas.type(i) for i in canvas.find_all()], ['rectangle', 'oval', 'line', 'text'])

    def test_main_navigation(self):
        from src.app.main import main
        with patch('src.app.main.tk.Tk', return_value=self.root), patch.object(self.root, 'mainloop'):
            main()
        buttons = widgets(self.root, ttk.Button)
        for control in buttons[:5]:
            control.invoke()
        windows = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertEqual(len(windows), 5)
        for win in windows:
            button(win, 'Cerrar').invoke()
            self.assertFalse(win.winfo_exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
