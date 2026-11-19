"""Guardado local compartido por las cinco ventanas de Ofivanta."""
from contextlib import contextmanager
from datetime import date, datetime, timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import isfinite
from pathlib import Path
from uuid import uuid4
import os
import re
import sqlite3
import unicodedata

from .catalogo import SERVICIOS, TRABAJADORES

DB_path = Path(os.environ.get("OFIVANTA_DB_PATH", Path(__file__).resolve().parents[2] / "data" / "ofivanta.sqlite3"))
ESTADOS = {
    "pendiente": "Pendiente", "cotizada": "Cotizada",
    "cotizacion_aceptada": "Confirmada", "en_proceso": "En proceso",
    "completada": "Finalizada", "cancelada": "Cancelada",
}
ORDEN_ESTADOS = list(ESTADOS)[:-1]
# Propuesta para el prototipo. No se procesa ningún cobro.
COMISION_PORCENTAJE = 10
COMISION_PRO_PORCENTAJE = 7
PRECIO_PRO_CENTAVOS = 14900
HORARIOS = ("Por acordar", "Mañana (8 a 12)", "Tarde (12 a 18)", "Después de las 18")
URGENCIAS = ("Normal", "Lo antes posible")


def ahora():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def texto_busqueda(valor):
    return "".join(c for c in unicodedata.normalize("NFD", str(valor).casefold()) if unicodedata.category(c) != "Mn")


@contextmanager
def conexion(db_path=None):
    ruta = Path(db_path or DB_path)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conex = sqlite3.connect(ruta, timeout=10)
    conex.row_factory = sqlite3.Row
    conex.execute("PRAGMA foreign_keys = ON")
    try:
        yield conex
        conex.commit()
    except Exception:
        conex.rollback()
        raise
    finally:
        conex.close()


def inicializar_base(db_path=None):
    """Crea o actualiza las tablas sin borrar solicitudes anteriores."""
    with conexion(db_path) as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS servicios (
                id TEXT PRIMARY KEY, nombre TEXT NOT NULL UNIQUE, descripcion TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS trabajadores (
                id TEXT PRIMARY KEY, nombre TEXT NOT NULL, descripcion TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
                zona TEXT NOT NULL DEFAULT 'León',
                disponible INTEGER NOT NULL DEFAULT 1 CHECK (disponible IN (0,1)));
            CREATE TABLE IF NOT EXISTS trabajador_servicio (
                trabajador_id TEXT NOT NULL REFERENCES trabajadores(id),
                servicio_id TEXT NOT NULL REFERENCES servicios(id),
                PRIMARY KEY (trabajador_id, servicio_id));
            CREATE TABLE IF NOT EXISTS solicitudes (
                id TEXT PRIMARY KEY, cliente TEXT NOT NULL, contacto TEXT NOT NULL,
                domicilio TEXT NOT NULL, descripcion TEXT NOT NULL, fecha TEXT NOT NULL,
                servicio_id TEXT NOT NULL REFERENCES servicios(id),
                trabajador_id TEXT NOT NULL REFERENCES trabajadores(id),
                estado TEXT NOT NULL CHECK (estado IN ('pendiente','cotizada',
                    'cotizacion_aceptada','en_proceso','completada','cancelada')),
                creada_en TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id TEXT PRIMARY KEY, solicitud_id TEXT NOT NULL REFERENCES solicitudes(id),
                importe REAL NOT NULL CHECK (importe >= 0),
                materiales_incluidos INTEGER NOT NULL CHECK (materiales_incluidos IN (0,1)),
                condiciones TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','aceptada','no_seleccionada')),
                creada_en TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solicitud_id TEXT NOT NULL REFERENCES solicitudes(id),
                estado TEXT NOT NULL, detalle TEXT NOT NULL, fecha TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS favoritos (
                trabajador_id TEXT PRIMARY KEY REFERENCES trabajadores(id));
            CREATE TABLE IF NOT EXISTS suscripciones_demo (
                id TEXT PRIMARY KEY, trabajador_id TEXT NOT NULL REFERENCES trabajadores(id),
                inicio TEXT NOT NULL, vence TEXT NOT NULL,
                precio_centavos INTEGER NOT NULL, activa INTEGER NOT NULL DEFAULT 1);
            CREATE INDEX IF NOT EXISTS idx_solicitudes_fecha ON solicitudes(creada_en);
            CREATE INDEX IF NOT EXISTS idx_cotizaciones_solicitud ON cotizaciones(solicitud_id);
        """)
        columnas = {fila["name"] for fila in con.execute("PRAGMA table_info(trabajadores)")}
        if "zona" not in columnas:
            con.execute("ALTER TABLE trabajadores ADD COLUMN zona TEXT NOT NULL DEFAULT 'León'")
        if "disponible" not in columnas:
            con.execute("ALTER TABLE trabajadores ADD COLUMN disponible INTEGER NOT NULL DEFAULT 1")
        columnas_solicitud = {f["name"] for f in con.execute("PRAGMA table_info(solicitudes)")}
        for campo, valor in (("horario", "Por acordar"), ("urgencia", "Normal")):
            if campo not in columnas_solicitud:
                con.execute(f"ALTER TABLE solicitudes ADD COLUMN {campo} TEXT NOT NULL DEFAULT '{valor}'")
        columnas_cotizacion = {f["name"] for f in con.execute("PRAGMA table_info(cotizaciones)")}
        if "comision_porcentaje" not in columnas_cotizacion:
            con.execute("ALTER TABLE cotizaciones ADD COLUMN comision_porcentaje INTEGER NOT NULL DEFAULT 10")
        con.executemany("INSERT OR IGNORE INTO servicios VALUES (?, ?, ?)", SERVICIOS)
        for identificador, nombre, descripcion, zona, disponible, oficio in TRABAJADORES:
            con.execute("""INSERT OR IGNORE INTO trabajadores
                (id,nombre,descripcion,zona,disponible) VALUES (?,?,?,?,?)""",
                (identificador, nombre, descripcion, zona, int(disponible)))
            con.execute("INSERT OR IGNORE INTO trabajador_servicio VALUES (?,?)", (identificador, oficio))


def obtener_servicios(db_path=None):
    inicializar_base(db_path)
    with conexion(db_path) as con:
        return [dict(f) for f in con.execute("SELECT * FROM servicios ORDER BY nombre")]


def obtener_trabajadores(servicio_id=None, busqueda="", db_path=None, solo_disponibles=False,
                         solo_favoritos=False, orden="nombre"):
    inicializar_base(db_path)
    consulta = """SELECT t.id,t.nombre,t.descripcion,t.zona,t.disponible,
        ts.servicio_id,s.nombre AS servicio, f.trabajador_id IS NOT NULL AS favorito FROM trabajadores t
        JOIN trabajador_servicio ts ON ts.trabajador_id=t.id
        JOIN servicios s ON s.id=ts.servicio_id
        LEFT JOIN favoritos f ON f.trabajador_id=t.id WHERE t.activo=1"""
    parametros = []
    if servicio_id:
        consulta += " AND ts.servicio_id=?"
        parametros.append(servicio_id)
    if solo_disponibles:
        consulta += " AND t.disponible=1"
    if solo_favoritos:
        consulta += " AND f.trabajador_id IS NOT NULL"
    with conexion(db_path) as con:
        filas = [dict(f) for f in con.execute(consulta + " ORDER BY t.nombre,s.nombre", parametros)]
    termino = texto_busqueda(busqueda.strip())
    resultado = [dict(f, disponible=bool(f["disponible"]), favorito=bool(f["favorito"])) for f in filas
                 if termino in texto_busqueda(f["nombre"] + " " + f["servicio"] + " " + f["zona"])]
    if orden == "disponibilidad":
        resultado.sort(key=lambda f: (not f["disponible"], texto_busqueda(f["nombre"])))
    return resultado


def validar_campos(cliente, contacto, domicilio, descripcion, fecha):
    campos = {"nombre": (cliente,100), "contacto": (contacto,150),
              "domicilio": (domicilio,250), "descripción": (descripcion,3000)}
    for nombre, (valor, limite) in campos.items():
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"Completa el campo {nombre}.")
        if len(valor.strip()) > limite:
            raise ValueError(f"El campo {nombre} permite hasta {limite} caracteres.")
    contacto = contacto.strip()
    correo = re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contacto)
    telefono = re.fullmatch(r"[+()\d\s-]+", contacto)
    digitos = re.sub(r"\D", "", contacto)
    if not correo and not (telefono and 10 <= len(digitos) <= 15):
        raise ValueError("Escribe un correo válido o un teléfono de 10 a 15 dígitos.")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fecha)):
            raise ValueError
        dia = date.fromisoformat(fecha)
    except (TypeError, ValueError):
        raise ValueError("Escribe la fecha como AAAA-MM-DD.") from None
    if dia < date.today():
        raise ValueError("La fecha no puede ser anterior a hoy.")


def guardar_solicitud(cliente=None, contacto=None, domicilio=None, descripcion=None,
                      servicio_id=None, trabajador_id=None, fecha=None, db_path=None,
                      horario="Por acordar", urgencia="Normal"):
    """Acepta un diccionario del formulario o los parámetros por separado."""
    if isinstance(cliente, dict):
        datos = cliente
        cliente, contacto = datos.get("cliente"), datos.get("contacto")
        domicilio, descripcion = datos.get("domicilio"), datos.get("descripcion")
        servicio, trabajador = datos.get("servicio"), datos.get("trabajador")
        servicio_id = datos.get("servicio_id") or (servicio.get("id") if isinstance(servicio, dict) else servicio)
        trabajador_id = datos.get("trabajador_id") or (trabajador.get("id") if isinstance(trabajador, dict) else trabajador)
        fecha = datos.get("fecha_deseada") or datos.get("fecha")
        horario = datos.get("horario", horario)
        urgencia = datos.get("urgencia", urgencia)
    fecha = date.today().isoformat() if fecha is None else str(fecha).strip()
    validar_campos(cliente, contacto, domicilio, descripcion, fecha)
    if horario not in HORARIOS or urgencia not in URGENCIAS:
        raise ValueError("Elige un horario y una prioridad de las opciones disponibles.")
    if servicio_id is None or trabajador_id is None:
        raise ValueError("Selecciona un servicio y un trabajador en el catálogo.")
    inicializar_base(db_path)
    identificador = str(uuid4())
    with conexion(db_path) as con:
        trabajador = con.execute("""SELECT t.activo,t.disponible FROM trabajadores t
            JOIN trabajador_servicio ts ON ts.trabajador_id=t.id
            WHERE t.id=? AND ts.servicio_id=?""", (str(trabajador_id), str(servicio_id))).fetchone()
        if trabajador is None:
            raise ValueError("El trabajador no ofrece el servicio seleccionado.")
        if not trabajador["activo"] or not trabajador["disponible"]:
            raise ValueError("Este trabajador ya no está disponible. Elige otro.")
        con.execute("""INSERT INTO solicitudes
            (id,cliente,contacto,domicilio,descripcion,fecha,servicio_id,trabajador_id,estado,creada_en,horario,urgencia)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (identificador, cliente.strip(), contacto.strip(), domicilio.strip(), descripcion.strip(),
             fecha, str(servicio_id), str(trabajador_id), "pendiente", ahora(), horario, urgencia))
        con.execute("INSERT INTO movimientos(solicitud_id,estado,detalle,fecha) VALUES (?,?,?,?)",
            (identificador, "pendiente", "Solicitud creada. En espera de cotización.", ahora()))
    return identificador


def obtener_solicitudes(db_path=None):
    inicializar_base(db_path)
    with conexion(db_path) as con:
        return [dict(f, numero=f["id"][:8].upper(), estado_texto=ESTADOS[f["estado"]]) for f in con.execute("""
            SELECT so.*,s.nombre AS servicio,t.nombre AS trabajador,t.zona,
            (SELECT importe FROM cotizaciones WHERE solicitud_id=so.id AND estado='aceptada') AS importe
            FROM solicitudes so
            JOIN servicios s ON s.id=so.servicio_id JOIN trabajadores t ON t.id=so.trabajador_id
            ORDER BY so.creada_en DESC, so.id DESC""")]


def obtener_solicitud(solicitud_id, db_path=None):
    inicializar_base(db_path)
    with conexion(db_path) as con:
        fila = con.execute("""SELECT so.*,s.nombre AS servicio,t.nombre AS trabajador,t.zona
            FROM solicitudes so JOIN servicios s ON s.id=so.servicio_id
            JOIN trabajadores t ON t.id=so.trabajador_id WHERE so.id=?""", (solicitud_id,)).fetchone()
        if fila is None:
            return None
        datos = dict(fila, numero=fila["id"][:8].upper(), estado_texto=ESTADOS[fila["estado"]])
        datos["cotizaciones"] = [dict(f, materiales_incluidos=bool(f["materiales_incluidos"]),
                                      desglose=desglosar_importe(f["importe"], f["comision_porcentaje"]))
            for f in con.execute("SELECT * FROM cotizaciones WHERE solicitud_id=? ORDER BY creada_en DESC", (solicitud_id,))]
        datos["movimientos"] = [dict(f) for f in con.execute(
            "SELECT * FROM movimientos WHERE solicitud_id=? ORDER BY id", (solicitud_id,))]
    return datos


def registrar_cotizacion(solicitud_id, importe, materiales_incluidos, condiciones, db_path=None):
    try:
        importe = float(importe)
    except (TypeError, ValueError):
        raise ValueError("Escribe un importe válido.") from None
    if not isfinite(importe) or importe < 0.01 or importe > 1000000:
        raise ValueError("El importe debe estar entre $0.01 y $1,000,000.")
    if not isinstance(materiales_incluidos, bool):
        raise ValueError("Indica si incluye materiales.")
    if not isinstance(condiciones, str) or not condiciones.strip() or len(condiciones) > 2000:
        raise ValueError("Escribe las condiciones de la cotización (hasta 2000 caracteres).")
    inicializar_base(db_path)
    identificador = str(uuid4())
    with conexion(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        fila = con.execute("SELECT estado,trabajador_id FROM solicitudes WHERE id=?", (solicitud_id,)).fetchone()
        if fila is None or fila["estado"] not in ("pendiente", "cotizada"):
            raise ValueError("Esta solicitud ya no acepta cotizaciones.")
        pro = con.execute("""SELECT 1 FROM suscripciones_demo WHERE trabajador_id=? AND activa=1 AND vence>?""",
                          (fila["trabajador_id"],date.today().isoformat())).fetchone()
        porcentaje = COMISION_PRO_PORCENTAJE if pro else COMISION_PORCENTAJE
        con.execute("""INSERT INTO cotizaciones(id,solicitud_id,importe,materiales_incluidos,
            condiciones,estado,creada_en,comision_porcentaje) VALUES (?,?,?,?,?,'pendiente',?,?)""",
            (identificador, solicitud_id, desglosar_importe(importe)["total"], int(materiales_incluidos),
             condiciones.strip(), ahora(), porcentaje))
        con.execute("UPDATE solicitudes SET estado='cotizada' WHERE id=?", (solicitud_id,))
        con.execute("INSERT INTO movimientos(solicitud_id,estado,detalle,fecha) VALUES (?,?,?,?)",
            (solicitud_id, "cotizada", f"Cotización de ejemplo recibida por ${importe:,.2f}.", ahora()))
    return identificador


def aceptar_cotizacion(cotizacion_id, db_path=None):
    inicializar_base(db_path)
    with conexion(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        fila = con.execute("""SELECT c.solicitud_id,c.estado,so.estado AS estado_solicitud
            FROM cotizaciones c JOIN solicitudes so ON so.id=c.solicitud_id WHERE c.id=?""", (cotizacion_id,)).fetchone()
        if fila is None or fila["estado"] != "pendiente" or fila["estado_solicitud"] != "cotizada":
            raise ValueError("La cotización ya fue resuelta o no puede aceptarse.")
        con.execute("UPDATE cotizaciones SET estado='aceptada' WHERE id=?", (cotizacion_id,))
        con.execute("UPDATE cotizaciones SET estado='no_seleccionada' WHERE solicitud_id=? AND id!=? AND estado='pendiente'",
            (fila["solicitud_id"], cotizacion_id))
        con.execute("UPDATE solicitudes SET estado='cotizacion_aceptada' WHERE id=?", (fila["solicitud_id"],))
        con.execute("INSERT INTO movimientos(solicitud_id,estado,detalle,fecha) VALUES (?,?,?,?)",
            (fila["solicitud_id"], "cotizacion_aceptada", "El cliente aceptó la cotización.", ahora()))


def actualizar_estado(solicitud_id, nuevo_estado, db_path=None):
    alias = {v: k for k,v in ESTADOS.items()}
    nuevo_estado = alias.get(nuevo_estado, nuevo_estado)
    permitidos = {"pendiente": {"cancelada"}, "cotizada": {"cancelada"},
        "cotizacion_aceptada": {"en_proceso","cancelada"}, "en_proceso": {"completada"},
        "completada": set(), "cancelada": set()}
    if nuevo_estado not in permitidos:
        raise ValueError("Estado no válido.")
    inicializar_base(db_path)
    with conexion(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        fila = con.execute("SELECT estado FROM solicitudes WHERE id=?", (solicitud_id,)).fetchone()
        if fila is None:
            raise ValueError("No se encontró la solicitud.")
        if nuevo_estado not in permitidos[fila["estado"]]:
            raise ValueError(f"No se puede pasar de {ESTADOS[fila['estado']]} a {ESTADOS[nuevo_estado]}.")
        con.execute("UPDATE solicitudes SET estado=? WHERE id=?", (nuevo_estado, solicitud_id))
        con.execute("INSERT INTO movimientos(solicitud_id,estado,detalle,fecha) VALUES (?,?,?,?)",
            (solicitud_id, nuevo_estado, f"Estado actualizado a {ESTADOS[nuevo_estado]}.", ahora()))


def cancelar_solicitud(solicitud_id, db_path=None):
    actualizar_estado(solicitud_id, "cancelada", db_path)


def alternar_favorito(trabajador_id, db_path=None):
    """Los favoritos pertenecen a esta computadora, no a una cuenta en línea."""
    inicializar_base(db_path)
    with conexion(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        if not con.execute("SELECT id FROM trabajadores WHERE id=? AND activo=1", (str(trabajador_id),)).fetchone():
            raise ValueError("No se encontró al trabajador.")
        existe = con.execute("SELECT 1 FROM favoritos WHERE trabajador_id=?", (str(trabajador_id),)).fetchone()
        if existe:
            con.execute("DELETE FROM favoritos WHERE trabajador_id=?", (str(trabajador_id),))
        else:
            con.execute("INSERT INTO favoritos VALUES (?)", (str(trabajador_id),))
    return not bool(existe)


def desglosar_importe(importe, porcentaje=COMISION_PORCENTAJE):
    """Calcula en centavos para que el total coincida con sus dos partes."""
    try:
        monto = Decimal(str(importe))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Escribe un importe válido.") from None
    if not monto.is_finite() or monto < 0 or monto > 1000000:
        raise ValueError("El importe debe estar entre $0 y $1,000,000.")
    if type(porcentaje) is not int or not 0 <= porcentaje <= 100:
        raise ValueError("El porcentaje debe ser un entero entre 0 y 100.")
    total = int((monto * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    comision = int((Decimal(total) * porcentaje / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return {"total": total / 100, "comision": comision / 100,
            "neto": (total - comision) / 100, "porcentaje": porcentaje}


def obtener_plan(trabajador_id, db_path=None):
    inicializar_base(db_path)
    with conexion(db_path) as con:
        trabajador = con.execute("SELECT nombre FROM trabajadores WHERE id=?", (str(trabajador_id),)).fetchone()
        if trabajador is None:
            raise ValueError("No se encontró al trabajador.")
        fila = con.execute("""SELECT * FROM suscripciones_demo
            WHERE trabajador_id=? AND activa=1 AND vence>? ORDER BY inicio DESC, id DESC LIMIT 1""",
            (str(trabajador_id), date.today().isoformat())).fetchone()
    return {"plan": "pro" if fila else "basico", "nombre": trabajador["nombre"],
            "vence": fila["vence"] if fila else None,
            "precio": fila["precio_centavos"] / 100 if fila else 0}


def activar_plan_pro(trabajador_id, db_path=None):
    """Registra 30 días de ejemplo. Repetir la activación no duplica el cargo."""
    inicializar_base(db_path)
    with conexion(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        if not con.execute("SELECT id FROM trabajadores WHERE id=? AND activo=1", (str(trabajador_id),)).fetchone():
            raise ValueError("No se encontró al trabajador.")
        hoy = date.today().isoformat()
        periodo = con.execute("""SELECT id FROM suscripciones_demo WHERE trabajador_id=? AND vence>?
            ORDER BY inicio DESC, id DESC LIMIT 1""", (str(trabajador_id), hoy)).fetchone()
        if periodo:
            con.execute("UPDATE suscripciones_demo SET activa=1 WHERE id=?", (periodo["id"],))
            return periodo["id"]
        identificador = str(uuid4())
        vence = (date.today() + timedelta(days=30)).isoformat()
        con.execute("INSERT INTO suscripciones_demo VALUES (?,?,?,?,?,1)",
                    (identificador, str(trabajador_id), hoy, vence, PRECIO_PRO_CENTAVOS))
    return identificador


def cancelar_plan_pro(trabajador_id, db_path=None):
    obtener_plan(trabajador_id, db_path)
    with conexion(db_path) as con:
        con.execute("UPDATE suscripciones_demo SET activa=0 WHERE trabajador_id=?", (str(trabajador_id),))


def obtener_agenda(trabajador_id, db_path=None):
    if obtener_plan(trabajador_id, db_path)["plan"] != "pro":
        raise ValueError("Activa el plan Pro de ejemplo para usar la agenda del prestador.")
    agenda = [s for s in obtener_solicitudes(db_path) if s["trabajador_id"] == str(trabajador_id)
              and s["estado"] not in ("cancelada", "completada")]
    return sorted(agenda, key=lambda s: (s["fecha"], s["creada_en"]))


def resumen_negocio(trabajador_id=None, db_path=None):
    """Acumulado simulado: cuenta comisiones únicamente de trabajos finalizados."""
    inicializar_base(db_path)
    filtro = " AND so.trabajador_id=?" if trabajador_id is not None else ""
    parametros = (str(trabajador_id),) if trabajador_id is not None else ()
    with conexion(db_path) as con:
        terminadas = con.execute("""SELECT c.importe,c.comision_porcentaje FROM cotizaciones c
            JOIN solicitudes so ON so.id=c.solicitud_id
            WHERE c.estado='aceptada' AND so.estado='completada'""" + filtro, parametros).fetchall()
        filtro_plan = " WHERE trabajador_id=?" if trabajador_id is not None else ""
        periodos = con.execute("SELECT precio_centavos,activa,vence FROM suscripciones_demo" + filtro_plan,
                              parametros).fetchall()
    total = comision = neto = 0
    for fila in terminadas:
        desglose = desglosar_importe(fila["importe"], fila["comision_porcentaje"])
        total += round(desglose["total"] * 100)
        comision += round(desglose["comision"] * 100)
        neto += round(desglose["neto"] * 100)
    suscripciones = sum(p["precio_centavos"] for p in periodos)
    return {"servicios_finalizados": len(terminadas), "total_servicios": total / 100,
            "comisiones": comision / 100, "neto_trabajadores": neto / 100,
            "suscripciones": suscripciones / 100, "total_ofivanta": (comision + suscripciones) / 100,
            "planes_activos": sum(bool(p["activa"] and p["vence"] > date.today().isoformat()) for p in periodos)}


def comparar_planes(importe, cantidad):
    """Proyección sencilla de 30 días; no crea cobros ni registros."""
    if isinstance(cantidad,bool):
        raise ValueError("Escribe una cantidad entera de trabajos entre 0 y 10000.")
    try:
        cantidad_entera=int(str(cantidad))
    except (ValueError,TypeError):
        raise ValueError("Escribe una cantidad entera de trabajos entre 0 y 10000.") from None
    if not 0<=cantidad_entera<=10000:
        raise ValueError("Escribe una cantidad entera de trabajos entre 0 y 10000.")
    basico=desglosar_importe(importe,COMISION_PORCENTAJE)
    pro=desglosar_importe(importe,COMISION_PRO_PORCENTAJE)
    volumen=round(basico['total']*100)*cantidad_entera
    comision_basica=round(basico['comision']*100)*cantidad_entera
    comision_pro=round(pro['comision']*100)*cantidad_entera
    return {"cantidad":cantidad_entera,"volumen":volumen/100,
        "comision_basica":comision_basica/100,"comision_pro":comision_pro/100,
        "cuota_pro":PRECIO_PRO_CENTAVOS/100,
        "neto_basico":(volumen-comision_basica)/100,
        "neto_pro":(volumen-comision_pro-PRECIO_PRO_CENTAVOS)/100,
        "diferencia":(comision_basica-comision_pro-PRECIO_PRO_CENTAVOS)/100}
