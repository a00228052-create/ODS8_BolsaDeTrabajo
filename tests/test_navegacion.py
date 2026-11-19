import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk
from unittest.mock import patch
from src.core import datos
from src.app.main import main
from src.app.win_list import open_win_list
from src.app.win_form import open_win_form
from src.app.win_table import abrir_detalles
from src.app.ui import notificar_cambio, cerrar_vista


def widgets(parent, clase):
    encontrados = []
    for hijo in parent.winfo_children():
        if isinstance(hijo, clase):
            encontrados.append(hijo)
        encontrados.extend(widgets(hijo, clase))
    return encontrados


def boton(parent, texto):
    return next(w for w in widgets(parent, (ttk.Button, tk.Button)) if w.cget('text') == texto)


class NavegacionTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.parche = patch.object(datos, 'DB_path', Path(self.temporal.name) / 'navegacion.sqlite3')
        self.parche.start()
        self.root = tk.Tk()
        self.root.withdraw()
        self.errores = []
        self.root.report_callback_exception = lambda tipo, error, traza: self.errores.append(str(error))
        with patch('src.app.main.tk.Tk', return_value=self.root), patch.object(self.root, 'mainloop'):
            main()
        self.nav = self.root.navegador

    def tearDown(self):
        self.root.update()
        self.root.destroy()
        self.parche.stop()
        self.temporal.cleanup()
        self.assertEqual(self.errores, [])

    def crear_solicitud(self):
        return datos.guardar_solicitud('Persona prueba', 'demo@example.test', 'Lugar de ejemplo',
                                      'Revisión de una fuga', 'serv-plomeria', '1')

    def formulario(self, trabajador='1'):
        servicio = next(s for s in datos.obtener_servicios() if s['id'] == 'serv-plomeria')
        perfil = next(t for t in datos.obtener_trabajadores() if t['id'] == trabajador)
        return open_win_form(self.root, servicio, perfil)

    def test_cambiar_seccion_no_abre_ventanas_del_sistema(self):
        for texto in ['Buscar servicio', 'Mis solicitudes', 'Seguimiento', 'Inicio', 'Planes e ingresos']:
            self.root.botones_menu[texto].invoke()
            self.root.update()
        self.assertEqual(widgets(self.root, tk.Toplevel), [])
        self.assertEqual(self.nav.actual.titulo, 'Inicio')
        self.assertLessEqual(len(self.nav.paginas), 4)

    def test_volver_conserva_el_filtro_del_catalogo(self):
        self.root.botones_menu['Buscar servicio'].invoke()
        catalogo = self.nav.actual
        catalogo.buscar('plomeria')
        self.root.botones_menu['Mis solicitudes'].invoke()
        boton(self.root, 'Volver').invoke()
        self.assertIs(self.nav.actual, catalogo)
        self.assertEqual(len(catalogo.tabla.get_children()), 2)
        self.root.botones_menu['Buscar servicio'].invoke()
        self.assertIs(self.nav.actual, catalogo)

    def test_volver_conserva_un_formulario_sin_enviar(self):
        self.root.botones_menu['Buscar servicio'].invoke()
        form = self.formulario()
        form.nombre.set('Mi borrador')
        self.nav.volver()
        self.assertEqual(self.nav.actual.titulo, 'Buscar servicio')
        misma = self.formulario()
        self.assertIs(misma, form)
        self.assertEqual(misma.nombre.get(), 'Mi borrador')
        self.assertEqual(datos.obtener_solicitudes(), [])

    def test_no_descarta_borrador_al_elegir_otra_persona_sin_confirmar(self):
        original = self.formulario()
        original.nombre.set('Borrador a conservar')
        with patch('src.app.win_form.messagebox.askyesno', return_value=False):
            resultado = self.formulario('2')
        self.assertIs(resultado, original)
        self.assertEqual(resultado.trabajador['id'], '1')
        self.assertEqual(resultado.nombre.get(), 'Borrador a conservar')

    def test_un_cambio_en_favoritos_no_reemplaza_el_borrador(self):
        original=self.formulario()
        original.nombre.set('Borrador a conservar')
        datos.alternar_favorito('1')
        with patch('src.app.win_form.messagebox.askyesno') as aviso:
            resultado=self.formulario()
        aviso.assert_not_called()
        self.assertIs(resultado,original)

    def test_cerrar_detalle_regresa_al_historial(self):
        sid = self.crear_solicitud()
        self.root.botones_menu['Mis solicitudes'].invoke()
        historial = self.nav.actual
        detalle = abrir_detalles(historial, sid)
        self.assertEqual(self.nav.actual.titulo, 'Detalle de solicitud')
        cerrar_vista(detalle)
        self.assertIs(self.nav.actual, historial)
        self.assertFalse(detalle.winfo_exists())

    def test_eventos_actualizan_paginas_ocultas(self):
        self.root.botones_menu['Mis solicitudes'].invoke()
        historial = self.nav.actual
        self.root.botones_menu['Inicio'].invoke()
        sid = self.crear_solicitud()
        notificar_cambio(self.root)
        self.root.update()
        self.assertEqual(historial.tabla.get_children(), (sid,))

    def test_cotizacion_permanece_dentro_de_la_app(self):
        sid = self.crear_solicitud()
        self.root.botones_menu['Seguimiento'].invoke()
        seguimiento = self.nav.actual
        widgets(seguimiento, ttk.Checkbutton)[0].invoke()
        boton(seguimiento, 'Crear cotización').invoke()
        cotizacion = self.nav.actual
        self.assertEqual(cotizacion.titulo, 'Cotización de ejemplo')
        self.assertEqual(widgets(self.root, tk.Toplevel), [])
        importe = widgets(cotizacion, ttk.Entry)[0]
        importe.insert(0, '500')
        widgets(cotizacion, tk.Text)[0].insert('1.0', 'Revisión y reparación de ejemplo')
        boton(cotizacion, 'Guardar cotización').invoke()
        self.root.update()
        self.assertIs(self.nav.actual, seguimiento)
        self.assertEqual(datos.obtener_solicitud(sid)['estado'], 'cotizada')


if __name__ == '__main__':
    unittest.main()
