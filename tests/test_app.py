import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
from src.core import datos
from src.app.win_form import open_win_form
from src.app.win_table import open_win_table, abrir_detalles
from src.app.win_canvas import open_win_canvas
from src.app.ui import notificar_cambio


def widgets(parent,kind):
    resultado=[]
    for hijo in parent.winfo_children():
        if isinstance(hijo,kind):resultado.append(hijo)
        resultado.extend(widgets(hijo,kind))
    return resultado


def boton(parent,texto):
    return next(w for w in widgets(parent,(ttk.Button,tk.Button)) if w.cget("text")==texto)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.carpeta=tempfile.TemporaryDirectory()
        self.parche=patch.object(datos,"DB_path",Path(self.carpeta.name)/"ui.sqlite3");self.parche.start()
        datos.inicializar_base();self.root=tk.Tk();self.root.withdraw();self.root.update_idletasks()

    def tearDown(self):
        self.root.update_idletasks();self.root.destroy();self.parche.stop();self.carpeta.cleanup()

    def crear(self):
        return datos.guardar_solicitud("Cliente prueba","4771234567","Lugar de ejemplo","Fuga de agua", "serv-plomeria","1")

    def formulario(self,callback=None):
        servicio=next(s for s in datos.obtener_servicios() if s["id"]=="serv-plomeria")
        trabajador=next(t for t in datos.obtener_trabajadores() if t["id"]=="1")
        return open_win_form(self.root,servicio,trabajador,guardar_callback=callback)

    def llenar(self,form):
        form.nombre.set("Cliente prueba");form.contacto.set("4771234567");form.domicilio.set("Lugar de ejemplo")
        form.descripcion.insert("1.0","Reparar fuga de agua")

    def test_formulario_guarda_y_conserva_la_seleccion(self):
        form=self.formulario();self.llenar(form)
        with patch("src.app.win_form.messagebox.askyesno",return_value=True),patch("src.app.win_form.messagebox.showinfo"):
            form.validar_y_confirmar()
        solicitud=datos.obtener_solicitudes()[0]
        self.assertEqual(solicitud["servicio_id"],"serv-plomeria")
        self.assertEqual(solicitud["trabajador_id"],"1")
        self.assertEqual(solicitud["estado"],"pendiente")

    def test_cancelar_confirmacion_no_guarda(self):
        form=self.formulario();self.llenar(form)
        with patch("src.app.win_form.messagebox.askyesno",return_value=False):form.validar_y_confirmar()
        self.assertEqual(datos.obtener_solicitudes(),[])
        self.assertTrue(form.ventana.winfo_exists())

    def test_validacion_de_campos_y_seleccion(self):
        form=self.formulario()
        with patch("src.app.ui.messagebox.showerror") as aviso:self.assertIsNone(form._validar())
        aviso.assert_called_once()
        vacio=open_win_form(self.root)
        with patch("src.app.win_form.messagebox.showwarning") as aviso:self.assertIsNone(vacio._validar())
        aviso.assert_called_once()

    def test_fallo_de_guardado_no_anuncia_exito(self):
        def fallar(campos):raise ValueError("No se pudo guardar")
        form=self.formulario(fallar);self.llenar(form)
        with patch("src.app.win_form.messagebox.askyesno",return_value=True),patch("src.app.ui.messagebox.showerror"),patch("src.app.win_form.messagebox.showinfo") as info:
            form.validar_y_confirmar()
        info.assert_not_called();self.assertFalse(form.guardando)
        self.assertEqual(datos.obtener_solicitudes(),[])

    def test_historial_actualiza_sin_duplicar(self):
        win=open_win_table(self.root)
        self.assertEqual(len(win.tabla.get_children()),0)
        sid=self.crear();win.actualizar();win.actualizar()
        self.assertEqual(win.tabla.get_children(),(sid,))
        qid=datos.registrar_cotizacion(sid,500,True,"Condiciones de prueba")
        datos.aceptar_cotizacion(qid);notificar_cambio(self.root);self.root.update()
        self.assertEqual(win.tabla.item(sid,"values")[-1],"Confirmada")

    def test_detalles_aceptan_cotizacion_real(self):
        sid=self.crear();qid=datos.registrar_cotizacion(sid,500,True,"Incluye reparación menor")
        win=abrir_detalles(self.root,sid)
        cot=widgets(win,ttk.Treeview)[0];cot.selection_set(qid);self.root.update()
        with patch("src.app.win_table.messagebox.askyesno",return_value=True):boton(win,"Aceptar cotización").invoke()
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"cotizacion_aceptada")

    def test_cancelacion_desde_historial(self):
        sid=self.crear();win=open_win_table(self.root);win.tabla.selection_set(sid)
        with patch("src.app.win_table.messagebox.askyesno",return_value=True):boton(win,"Cancelar solicitud").invoke()
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"cancelada")

    def test_exportar_csv(self):
        self.crear();win=open_win_table(self.root);ruta=Path(self.carpeta.name)/"solicitudes.csv"
        with patch("src.app.win_table.filedialog.asksaveasfilename",return_value=str(ruta)),patch("src.app.win_table.messagebox.showinfo"):
            boton(win,"Exportar CSV").invoke()
        with ruta.open(encoding="utf-8-sig",newline="") as f:filas=list(csv.reader(f))
        self.assertEqual(len(filas),2);self.assertEqual(filas[1][1],"Plomería")

    def test_seguimiento_respeta_simulacion_y_estado(self):
        sid=self.crear();win=open_win_canvas(self.root,sid)
        self.assertIn("disabled",boton(win,"Crear cotización").state())
        widgets(win,ttk.Checkbutton)[0].invoke()
        self.assertNotIn("disabled",boton(win,"Crear cotización").state())
        self.assertIn("disabled",boton(win,"Iniciar servicio").state())
        qid=datos.registrar_cotizacion(sid,300,True,"Ejemplo");datos.aceptar_cotizacion(qid);win.actualizar()
        self.assertNotIn("disabled",boton(win,"Iniciar servicio").state())
        with patch("src.app.win_canvas.messagebox.askyesno",return_value=True):boton(win,"Iniciar servicio").invoke()
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"en_proceso")
        with patch("src.app.win_canvas.messagebox.askyesno",return_value=True):boton(win,"Finalizar servicio").invoke()
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"completada")

    def test_seguimiento_sin_solicitudes(self):
        win=open_win_canvas(self.root)
        self.assertIn("disabled",boton(win,"Iniciar servicio").state())
        self.assertTrue(win.canvas.find_all())

    def test_menu_abre_ventanas_sin_duplicarlas(self):
        from src.app.main import main
        with patch("src.app.main.tk.Tk",return_value=self.root),patch.object(self.root,"mainloop"):
            main()
        for texto in ["Buscar servicio","Mis solicitudes","Seguimiento"]:
            boton(self.root,texto).invoke();boton(self.root,texto).invoke()
        ventanas=[w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
        self.assertEqual(len(ventanas),0)
        self.assertEqual(set(self.root.navegador.paginas),{"Inicio","Buscar servicio","Mis solicitudes","Seguimiento"})


if __name__=="__main__":unittest.main()
