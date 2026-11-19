import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
from src.core import datos
from src.app.main import main
from src.app.win_list import open_win_list
from src.app.win_form import open_win_form


def widgets(parent, clase):
    resultado = []
    for hijo in parent.winfo_children():
        if isinstance(hijo, clase):
            resultado.append(hijo)
        resultado.extend(widgets(hijo, clase))
    return resultado


def boton(parent, texto):
    return next(w for w in widgets(parent, (tk.Button, ttk.Button)) if w.cget('text') == texto)


class DatosDemoFixture(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.parche = patch.object(datos, 'DB_path', Path(self.carpeta.name) / 'demo.sqlite3')
        self.parche.start()
        datos.inicializar_base()

    def tearDown(self):
        self.parche.stop()
        self.carpeta.cleanup()

    def crear(self, trabajador='1', **campos):
        return datos.guardar_solicitud('Cliente de ejemplo', 'demo@example.test', 'Lugar ficticio',
                                      'Reparar una fuga', 'serv-plomeria', trabajador, **campos)

    def finalizar(self, solicitud, importe):
        cotizacion = datos.registrar_cotizacion(solicitud, importe, True, 'Condiciones de ejemplo')
        datos.aceptar_cotizacion(cotizacion)
        datos.actualizar_estado(solicitud, 'en_proceso')
        datos.actualizar_estado(solicitud, 'completada')


class FuncionesNuevasTests(DatosDemoFixture):
    def test_favorito_persiste_y_se_puede_quitar(self):
        self.assertTrue(datos.alternar_favorito('2'))
        datos.inicializar_base()
        self.assertEqual([t['id'] for t in datos.obtener_trabajadores(solo_favoritos=True)], ['2'])
        self.assertFalse(datos.alternar_favorito('2'))
        self.assertEqual(datos.obtener_trabajadores(solo_favoritos=True), [])
        with self.assertRaises(ValueError):
            datos.alternar_favorito('inexistente')

    def test_favoritos_respetan_el_oficio_y_la_disponibilidad(self):
        datos.alternar_favorito('4')
        self.assertEqual(len(datos.obtener_trabajadores('serv-electricidad', solo_favoritos=True)), 1)
        self.assertEqual(datos.obtener_trabajadores('serv-plomeria', solo_favoritos=True), [])
        self.assertEqual(datos.obtener_trabajadores(solo_favoritos=True, solo_disponibles=True), [])

    def test_disponibles_aparecen_primero(self):
        trabajadores = datos.obtener_trabajadores(orden='disponibilidad')
        self.assertEqual(trabajadores[-1]['id'], '4')
        self.assertTrue(all(t['disponible'] for t in trabajadores[:-1]))

    def test_reparto_suma_el_total_y_redondea_centavos(self):
        self.assertEqual(datos.desglosar_importe(500), {'total': 500, 'comision': 50, 'neto': 450, 'porcentaje': 10})
        for importe in ['0.01', '0.05', '0.15', '19.99', '200.35', '999999.99', '10.005']:
            reparto = datos.desglosar_importe(importe)
            self.assertEqual(Decimal(str(reparto['comision'])) + Decimal(str(reparto['neto'])),
                             Decimal(str(reparto['total'])))
        self.assertEqual(datos.desglosar_importe('10.005')['total'], 10.01)
        for importe in ['nan', 'inf', '-1', 'invalido', '1000001']:
            with self.subTest(importe=importe), self.assertRaises(ValueError):
                datos.desglosar_importe(importe)

    def test_solo_finalizados_generan_comision_simulada(self):
        finalizada, pendiente, cancelada = self.crear(), self.crear(), self.crear()
        self.finalizar(finalizada, 500)
        qid = datos.registrar_cotizacion(pendiente, 900, False, 'Ejemplo')
        datos.aceptar_cotizacion(qid)
        qid = datos.registrar_cotizacion(cancelada, 1000, True, 'Ejemplo')
        datos.aceptar_cotizacion(qid)
        datos.cancelar_solicitud(cancelada)
        resumen = datos.resumen_negocio()
        self.assertEqual(resumen['comisiones'], 50)
        self.assertEqual(resumen['neto_trabajadores'], 450)
        self.assertEqual(resumen['servicios_finalizados'], 1)

    def test_porcentaje_de_la_cotizacion_no_cambia_despues(self):
        sid = self.crear()
        qid = datos.registrar_cotizacion(sid, 500, True, 'Ejemplo')
        with patch.object(datos, 'COMISION_PORCENTAJE', 20):
            datos.aceptar_cotizacion(qid)
            datos.actualizar_estado(sid, 'en_proceso')
            datos.actualizar_estado(sid, 'completada')
            self.assertEqual(datos.resumen_negocio()['comisiones'], 50)
        self.assertEqual(datos.obtener_solicitudes()[0]['importe'], 500)

    def test_plan_no_duplica_periodo_y_no_borra_historial(self):
        primero = datos.activar_plan_pro('1')
        self.assertEqual(datos.activar_plan_pro('1'), primero)
        self.assertEqual(datos.obtener_plan('1')['plan'], 'pro')
        datos.cancelar_plan_pro('1')
        self.assertEqual(datos.obtener_plan('1')['plan'], 'basico')
        self.assertEqual(datos.activar_plan_pro('1'), primero)
        self.assertEqual(datos.resumen_negocio()['suscripciones'], 149)
        datos.inicializar_base()
        self.assertEqual(datos.obtener_plan('1')['plan'], 'pro')

    def test_plan_vencido_no_se_renueva_solo(self):
        datos.activar_plan_pro('1')
        with datos.conexion() as con:
            con.execute('UPDATE suscripciones_demo SET vence=?', ((date.today() - timedelta(days=1)).isoformat(),))
        self.assertEqual(datos.obtener_plan('1')['plan'], 'basico')
        self.assertEqual(datos.resumen_negocio()['suscripciones'], 149)
        self.assertEqual(datos.resumen_negocio()['planes_activos'], 0)
        datos.activar_plan_pro('1')
        self.assertEqual(datos.resumen_negocio()['suscripciones'], 298)

    def test_agenda_filtra_por_trabajador_y_excluye_cerrados(self):
        abierta = self.crear(horario='Tarde (12 a 18)', urgencia='Lo antes posible')
        finalizada = self.crear()
        self.finalizar(finalizada, 400)
        self.crear(trabajador='2')
        with self.assertRaises(ValueError):
            datos.obtener_agenda('1')
        datos.activar_plan_pro('1')
        self.assertEqual([s['id'] for s in datos.obtener_agenda('1')], [abierta])
        self.assertEqual(datos.obtener_solicitud(abierta)['horario'], 'Tarde (12 a 18)')
        self.assertEqual(datos.resumen_negocio('2')['total_ofivanta'], 0)
        with self.assertRaises(ValueError):
            self.crear(horario='invalido')

    def test_resumen_combina_comision_y_planes_sin_duplicar_servicios(self):
        sid = self.crear()
        self.finalizar(sid, 500)
        datos.activar_plan_pro('1')
        datos.activar_plan_pro('1')
        datos.activar_plan_pro('2')
        resumen = datos.resumen_negocio()
        self.assertEqual(resumen['total_ofivanta'], 348)
        self.assertEqual(resumen['planes_activos'], 2)
        self.assertEqual(datos.resumen_negocio('1')['total_ofivanta'], 199)

    def test_actualiza_base_anterior_sin_perder_solicitudes(self):
        import sqlite3
        ruta=Path(self.carpeta.name)/'base_anterior.sqlite3'
        con=sqlite3.connect(ruta)
        try:
            con.execute('''CREATE TABLE solicitudes (
                id TEXT PRIMARY KEY, cliente TEXT, contacto TEXT, domicilio TEXT,
                descripcion TEXT, fecha TEXT, servicio_id TEXT, trabajador_id TEXT,
                estado TEXT, creada_en TEXT)''')
            con.execute('INSERT INTO solicitudes VALUES (?,?,?,?,?,?,?,?,?,?)',
                ('anterior','Cliente ejemplo','demo@example.test','Lugar ficticio','Fuga',
                 date.today().isoformat(),'serv-plomeria','1','pendiente',datos.ahora()))
            con.commit()
        finally:
            con.close()
        datos.inicializar_base(ruta)
        datos.inicializar_base(ruta)
        solicitud=datos.obtener_solicitud('anterior',ruta)
        self.assertEqual(solicitud['cliente'],'Cliente ejemplo')
        self.assertEqual(solicitud['horario'],'Por acordar')
        self.assertEqual(solicitud['urgencia'],'Normal')
        self.assertEqual(len(datos.obtener_solicitudes(ruta)),1)

    def test_pro_reduce_comision_y_conserva_cotizaciones_anteriores(self):
        sid=self.crear()
        anterior=datos.registrar_cotizacion(sid,500,True,'Propuesta anterior')
        datos.activar_plan_pro('1')
        nueva=datos.registrar_cotizacion(sid,500,True,'Propuesta con Pro')
        cuotas={q['id']:q for q in datos.obtener_solicitud(sid)['cotizaciones']}
        self.assertEqual(cuotas[anterior]['desglose']['comision'],50)
        self.assertEqual(cuotas[nueva]['desglose']['comision'],35)
        datos.cancelar_plan_pro('1')
        datos.aceptar_cotizacion(nueva)
        datos.actualizar_estado(sid,'en_proceso')
        datos.actualizar_estado(sid,'completada')
        self.assertEqual(datos.resumen_negocio()['comisiones'],35)

    def test_comparador_incluye_mensualidad_y_casos_sin_trabajo(self):
        resultado=datos.comparar_planes(500,20)
        self.assertEqual(resultado['volumen'],10000)
        self.assertEqual(resultado['neto_basico'],9000)
        self.assertEqual(resultado['neto_pro'],9151)
        self.assertEqual(resultado['diferencia'],151)
        resultado=datos.comparar_planes(500,0)
        self.assertEqual(resultado['neto_basico'],0)
        self.assertEqual(resultado['neto_pro'],-149)
        for cantidad in [-1,'1.5','a',True,10001]:
            with self.subTest(cantidad=cantidad),self.assertRaises(ValueError):
                datos.comparar_planes(500,cantidad)


class VentanasNuevasTests(DatosDemoFixture):
    def setUp(self):
        super().setUp()
        self.root = tk.Tk()
        self.root.withdraw()
        self.errores = []
        self.root.report_callback_exception = lambda tipo, error, traza: self.errores.append(str(error))

    def tearDown(self):
        self.root.update()
        errores = self.errores[:]
        self.root.destroy()
        super().tearDown()
        self.assertEqual(errores, [])

    def abrir_menu(self):
        with patch('src.app.main.tk.Tk', return_value=self.root), patch.object(self.root, 'mainloop'):
            main()
        return self.root.inicio

    def test_pro_se_activa_desde_la_interfaz_y_habilita_agenda(self):
        sid = self.crear()
        home = self.abrir_menu()
        boton(self.root, 'Planes e ingresos').invoke()
        self.assertEqual(home.agenda.get_children(), ())
        with patch('src.app.win_home.messagebox.askyesno', return_value=True):
            boton(self.root, 'Simular Pro').invoke()
        self.root.update()
        self.assertEqual(datos.obtener_plan('1')['plan'], 'pro')
        self.assertEqual(home.agenda.get_children(), (sid,))
        with patch('src.app.win_home.messagebox.askyesno', return_value=True):
            boton(self.root, 'Volver a Básico').invoke()
        self.root.update()
        self.assertEqual(home.agenda.get_children(), ())

    def test_favoritos_y_restablecer_desde_catalogo(self):
        win = open_win_list(self.root)
        win.tabla.selection_set('2|serv-plomeria')
        self.root.update()
        boton(win, 'Guardar favorito').invoke()
        self.root.update()
        next(w for w in widgets(win, ttk.Checkbutton) if w.cget('text') == 'Mis favoritos').invoke()
        self.assertEqual(win.tabla.get_children(), ('2|serv-plomeria',))
        boton(win, 'Restablecer filtros').invoke()
        self.assertEqual(len(win.tabla.get_children()), 10)

    def test_formulario_conserva_preferencias(self):
        servicio = next(s for s in datos.obtener_servicios() if s['id'] == 'serv-plomeria')
        trabajador = next(t for t in datos.obtener_trabajadores() if t['id'] == '1')
        form = open_win_form(self.root, servicio, trabajador)
        form.nombre.set('Cliente ejemplo')
        form.contacto.set('demo@example.test')
        form.domicilio.set('Lugar ficticio')
        form.horario.set('Tarde (12 a 18)')
        form.urgencia.set('Lo antes posible')
        boton(form.ventana, 'Usar descripción de ejemplo').invoke()
        with patch('src.app.win_form.messagebox.askyesno', return_value=True), patch('src.app.win_form.messagebox.showinfo'):
            form.validar_y_confirmar()
        guardada = datos.obtener_solicitudes()[0]
        self.assertEqual(guardada['horario'], 'Tarde (12 a 18)')
        self.assertEqual(guardada['urgencia'], 'Lo antes posible')

    def test_menu_conserva_acceso_a_las_cinco_ventanas(self):
        self.abrir_menu()
        for indice in range(5):
            self.root.menu_ventanas.invoke(indice)
        ventanas=[w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
        self.assertEqual(len(ventanas),5)

    def test_enviar_desde_busqueda_abre_historial_con_seleccion(self):
        self.abrir_menu()
        boton(self.root,'Buscar servicio').invoke()
        lista=next(w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel))
        lista.tabla.selection_set('1|serv-plomeria')
        boton(lista,'Solicitar servicio').invoke()
        form=next(w for w in lista.winfo_children() if isinstance(w,tk.Toplevel))
        entradas=[w for w in widgets(form,ttk.Entry) if not isinstance(w,ttk.Combobox)]
        for entrada,texto in zip(entradas[:3],['Cliente ejemplo','demo@example.test','Lugar ficticio']):
            entrada.insert(0,texto)
        boton(form,'Usar descripción de ejemplo').invoke()
        with patch('src.app.win_form.messagebox.askyesno',return_value=True),patch('src.app.win_form.messagebox.showinfo'):
            boton(form,'Revisar y enviar solicitud').invoke()
        self.root.update()
        historial=next(w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel) and 'Mis solicitudes' in w.title())
        self.assertEqual(historial.tabla.selection(),(datos.obtener_solicitudes()[0]['id'],))


if __name__ == '__main__':
    unittest.main()
