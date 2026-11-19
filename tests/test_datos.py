import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch
from src.core import datos


class DatosTests(unittest.TestCase):
    def setUp(self):
        self.carpeta=tempfile.TemporaryDirectory()
        self.ruta=Path(self.carpeta.name)/"pruebas.sqlite3"
        self.parche=patch.object(datos,"DB_path",self.ruta);self.parche.start()
        datos.inicializar_base()

    def tearDown(self):
        self.parche.stop();self.carpeta.cleanup()

    def crear(self,**cambios):
        campos=dict(cliente="Cliente de prueba",contacto="4771234567",domicilio="Domicilio ficticio",
            descripcion="Revisar fuga de agua",servicio_id="serv-plomeria",trabajador_id="1",
            fecha=(date.today()+timedelta(days=1)).isoformat())
        campos.update(cambios)
        return datos.guardar_solicitud(**campos)

    def test_catalogo_no_se_duplica(self):
        for _ in range(3):datos.inicializar_base()
        self.assertEqual(len(datos.obtener_servicios()),8)
        self.assertEqual(len(datos.obtener_trabajadores()),10)

    def test_busqueda_sin_acentos_y_disponibilidad(self):
        self.assertEqual(len(datos.obtener_trabajadores(busqueda="PLOMERIA")),2)
        trabajadores=datos.obtener_trabajadores("serv-electricidad",solo_disponibles=True)
        self.assertEqual([t["id"] for t in trabajadores],["3"])
        self.assertTrue(all("Norte" in t["zona"] for t in datos.obtener_trabajadores(busqueda="norte")))

    def test_guarda_diccionario_del_formulario(self):
        identificador=datos.guardar_solicitud({"cliente":" Persona ","contacto":"persona@example.test",
            "domicilio":" Lugar de ejemplo ","descripcion":" Trabajo de ejemplo ",
            "fecha_deseada":date.today().isoformat(),"servicio":{"id":"serv-plomeria"},"trabajador":{"id":"1"}})
        guardada=datos.obtener_solicitud(identificador)
        self.assertEqual(guardada["cliente"],"Persona")
        self.assertEqual(guardada["estado"],"pendiente")
        self.assertEqual(len(guardada["movimientos"]),1)

    def test_persistencia_y_ids_unicos(self):
        a,b=self.crear(),self.crear()
        self.assertNotEqual(a,b)
        datos.inicializar_base()
        with sqlite3.connect(self.ruta) as con:
            self.assertEqual(con.execute("SELECT count(*) FROM solicitudes").fetchone()[0],2)
        con.close()
        self.assertIsNotNone(datos.obtener_solicitud(a))

    def test_no_guarda_campos_invalidos(self):
        errores=[{"cliente":" "},{"contacto":"abc4771234567"},{"contacto":"xx@"},
            {"domicilio":""},{"descripcion":""},{"fecha":"19/11/2026"},
            {"fecha":(date.today()-timedelta(days=1)).isoformat()},
            {"servicio_id":"serv-electricidad"},{"trabajador_id":"no-existe"},
            {"servicio_id":"serv-electricidad","trabajador_id":"4"}]
        for cambios in errores:
            with self.subTest(cambios=cambios),self.assertRaises(ValueError):self.crear(**cambios)
        self.assertEqual(datos.obtener_solicitudes(),[])

    def test_cotizaciones_invalidas_no_modifican_solicitud(self):
        sid=self.crear()
        for importe in ["abc",float("nan"),float("inf"),-10,0,0.001,1000001]:
            with self.subTest(importe=importe),self.assertRaises(ValueError):
                datos.registrar_cotizacion(sid,importe,True,"Incluye revisión")
        with self.assertRaises(ValueError):datos.registrar_cotizacion(sid,100,True," ")
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"pendiente")
        self.assertEqual(datos.obtener_solicitud(sid)["cotizaciones"],[])

    def test_recorrido_completo(self):
        sid=self.crear()
        primero=datos.registrar_cotizacion(sid,450,True,"Revisión y reparación menor.")
        segundo=datos.registrar_cotizacion(sid,700,False,"Cambio de pieza. Materiales aparte.")
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"cotizada")
        datos.aceptar_cotizacion(primero)
        solicitud=datos.obtener_solicitud(sid)
        self.assertEqual(solicitud["estado_texto"],"Confirmada")
        estados={c["id"]:c["estado"] for c in solicitud["cotizaciones"]}
        self.assertEqual(estados,{primero:"aceptada",segundo:"no_seleccionada"})
        with self.assertRaises(ValueError):datos.aceptar_cotizacion(segundo)
        datos.actualizar_estado(sid,"En proceso")
        with self.assertRaises(ValueError):datos.cancelar_solicitud(sid)
        datos.actualizar_estado(sid,"Finalizada")
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"completada")
        self.assertEqual(len(datos.obtener_solicitud(sid)["movimientos"]),6)

    def test_no_se_pueden_saltar_etapas(self):
        sid=self.crear()
        for estado in ["cotizacion_aceptada","en_proceso","completada","inexistente"]:
            with self.subTest(estado=estado),self.assertRaises(ValueError):datos.actualizar_estado(sid,estado)
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"pendiente")

    def test_cancelacion_no_se_reabre(self):
        sid=self.crear();datos.cancelar_solicitud(sid)
        with self.assertRaises(ValueError):datos.registrar_cotizacion(sid,500,True,"Ejemplo")
        with self.assertRaises(ValueError):datos.actualizar_estado(sid,"pendiente")
        self.assertEqual(datos.obtener_solicitud(sid)["estado_texto"],"Cancelada")

    def test_cancelacion_antes_de_iniciar(self):
        sid=self.crear();qid=datos.registrar_cotizacion(sid,250,True,"Ejemplo")
        datos.aceptar_cotizacion(qid);datos.cancelar_solicitud(sid)
        self.assertEqual(datos.obtener_solicitud(sid)["estado"],"cancelada")

    def test_consultas_con_apostrofes(self):
        sid=self.crear(cliente="Persona D'Ávila",descripcion="Revisar llave 'principal'; SELECT 1")
        self.assertEqual(datos.obtener_solicitud(sid)["cliente"],"Persona D'Ávila")
        self.assertEqual(len(datos.obtener_servicios()),8)

    def test_migracion_de_trabajadores_anteriores(self):
        ruta=Path(self.carpeta.name)/"anterior.sqlite3"
        with sqlite3.connect(ruta) as con:
            con.execute("CREATE TABLE trabajadores(id TEXT PRIMARY KEY,nombre TEXT NOT NULL,descripcion TEXT NOT NULL,activo INTEGER NOT NULL DEFAULT 1)")
            con.execute("INSERT INTO trabajadores VALUES ('anterior','Perfil anterior','Conservar registro',1)")
        con.close()
        datos.inicializar_base(ruta)
        with sqlite3.connect(ruta) as con:
            fila=con.execute("SELECT nombre,zona,disponible FROM trabajadores WHERE id='anterior'").fetchone()
        con.close()
        self.assertEqual(fila,("Perfil anterior","León",1))


if __name__=="__main__":unittest.main()
