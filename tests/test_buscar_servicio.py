"""Pruebas del catálogo y su conexión con el formulario actual."""
import unittest
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
from src.app.win_list import open_win_list
from src.core.servicios import obtener_servicios
from src.core.trabajadores import obtener_trabajadores


def widgets(parent, kind):
    result = []
    for child in parent.winfo_children():
        if isinstance(child, kind):
            result.append(child)
        result.extend(widgets(child, kind))
    return result


def button(win, name):
    return next(w for w in widgets(win, ttk.Button) if w.cget('text') == name)


class BuscarServicioTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.update_idletasks()

    def tearDown(self):
        self.root.update_idletasks()
        self.root.destroy()

    def test_catalogos_compartidos(self):
        services = {s['id'] for s in obtener_servicios()}
        workers = obtener_trabajadores()
        self.assertEqual(len({w['id'] for w in workers}), len(workers))
        self.assertTrue(all(w['servicio_id'] in services for w in workers))
        workers[0]['nombre'] = 'Cambio'
        self.assertNotEqual(obtener_trabajadores()[0]['nombre'], 'Cambio')

    def test_filtro_y_cambio_de_seleccion(self):
        win = open_win_list(self.root, categoria='plomeria')
        tree = widgets(win, ttk.Treeview)[0]
        self.assertEqual(tree.get_children(), ('1', '2'))
        tree.selection_set('1')
        combo = widgets(win, ttk.Combobox)[0]
        combo.set('Servicios de Electricidad')
        combo.event_generate('<<ComboboxSelected>>')
        self.root.update()
        self.assertEqual(tree.get_children(), ('3', '4'))
        self.assertEqual(tree.selection(), ())
        combo.current(0)
        combo.event_generate('<<ComboboxSelected>>')
        self.root.update()
        self.assertEqual(len(tree.get_children()), 10)

    def test_avisos_sin_seleccion(self):
        win = open_win_list(self.root)
        with patch('src.app.win_list.messagebox.showwarning') as warning, patch('src.app.win_list.open_win_form') as form:
            button(win, 'Seleccionar trabajador').invoke()
            button(win, 'Solicitar servicio').invoke()
            self.assertEqual(warning.call_count, 2)
            form.assert_not_called()

    def test_no_disponible(self):
        win = open_win_list(self.root)
        widgets(win, ttk.Treeview)[0].selection_set('4')
        with patch('src.app.win_list.messagebox.showwarning') as warning, patch('src.app.win_list.open_win_form') as form:
            button(win, 'Solicitar servicio').invoke()
            warning.assert_called_once()
            form.assert_not_called()

    def test_seleccion_llega_al_formulario_y_al_guardado(self):
        win = open_win_list(self.root)
        widgets(win, ttk.Treeview)[0].selection_set('2')
        with patch('src.app.win_form._guardar_solicitud', return_value=123) as guardar:
            button(win, 'Solicitar servicio').invoke()
        form = next(w for w in win.winfo_children() if isinstance(w, tk.Toplevel))
        labels = ' '.join(w.cget('text') for w in widgets(form, tk.Label))
        self.assertIn('Carlos Pérez', labels)
        self.assertIn('Servicios de Plomería', labels)
        fields = widgets(form, ttk.Entry)
        for entry, value in zip(fields[:3], ['Cliente de prueba', '4771234567', 'Domicilio de prueba']):
            entry.insert(0, value)
        widgets(form, tk.Text)[0].insert('1.0', 'Fuga de agua de ejemplo')
        with patch('src.app.win_form.messagebox.askyesno', return_value=True), patch('src.app.win_form.messagebox.showinfo'):
            button(form, 'Revisar y enviar solicitud').invoke()
        guardar.assert_called_once()
        datos = guardar.call_args.args[0]
        self.assertEqual(datos['servicio']['id'], 'plomeria')
        self.assertEqual(datos['trabajador']['id'], 2)
        self.assertEqual(datos['estado'], 'Pendiente')

    def test_catalogo_vacio(self):
        with patch('src.app.win_list.obtener_trabajadores', return_value=[]):
            win = open_win_list(self.root)
        self.assertEqual(widgets(win, ttk.Treeview)[0].get_children(), ())
        self.assertTrue(any(w.cget('text') == 'No hay trabajadores para este oficio.' for w in widgets(win, ttk.Label)))

    def test_cliente_no_modifica_catalogo(self):
        win = open_win_list(self.root)
        names = [w.cget('text') for w in widgets(win, ttk.Button)]
        for forbidden in ['Agregar', 'Eliminar seleccionado', 'Limpiar']:
            self.assertNotIn(forbidden, names)
        button(win, 'Cerrar').invoke()
        self.assertFalse(win.winfo_exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
