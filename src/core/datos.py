from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
import sqlite3 
from uuid import uuid4
#Para crear identificadores para los registros -->
DB_path = Path(__file__).resolve().parents[2] / "data" / "ofivanta.sqlite3"

@contextmanager
def conexion(db_path=DB_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conex = sqlite3.connect(db_path)
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
    

def inicializar_base(db_path=DB_path):
    """Crea las tablas y agrega datos de demostración sin duplicarlos."""
    with conexion(db_path) as conex:
        conex.executescript("""
            CREATE TABLE IF NOT EXISTS servicios (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trabajadores (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS trabajador_servicio (
                trabajador_id TEXT NOT NULL REFERENCES trabajadores(id),
                servicio_id TEXT NOT NULL REFERENCES servicios(id),
                PRIMARY KEY (trabajador_id, servicio_id)
            );

            CREATE TABLE IF NOT EXISTS solicitudes (
                id TEXT PRIMARY KEY,
                cliente TEXT NOT NULL,
                contacto TEXT NOT NULL,
                domicilio TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha TEXT NOT NULL,
                servicio_id TEXT NOT NULL REFERENCES servicios(id),
                trabajador_id TEXT NOT NULL REFERENCES trabajadores(id),
                estado TEXT NOT NULL CHECK (
                    estado IN (
                        'pendiente', 'cotizada', 'cotizacion_aceptada',
                        'en_proceso', 'completada', 'cancelada'
                    )
                ),
                creada_en TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cotizaciones (
                id TEXT PRIMARY KEY,
                solicitud_id TEXT NOT NULL REFERENCES solicitudes(id),
                importe REAL NOT NULL CHECK (importe >= 0),
                materiales_incluidos INTEGER NOT NULL
                    CHECK (materiales_incluidos IN (0, 1)),
                condiciones TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente' CHECK (
                    estado IN ('pendiente', 'aceptada', 'no_seleccionada')
                ),
                creada_en TEXT NOT NULL
            );
        """)

        conex.executemany(
            """INSERT OR IGNORE INTO servicios (id, nombre, descripcion)
               VALUES (?, ?, ?)""",
            [
                ("serv-plomeria", "Plomería", "Reparación e instalación de tuberías."),
                ("serv-electricidad", "Electricidad", "Instalaciones y reparaciones."),
                ("serv-carpinteria", "Carpintería", "Fabricación y reparación de muebles."),
            ],
        )
        conex.executemany(
            """INSERT OR IGNORE INTO trabajadores (id, nombre, descripcion)
               VALUES (?, ?, ?)""",
            [
                ("trab-plomeria-demo", "Profesional demo de plomería", "Perfil ficticio."),
                ("trab-electricidad-demo", "Profesional demo de electricidad", "Perfil ficticio."),
                ("trab-carpinteria-demo", "Profesional demo de carpintería", "Perfil ficticio."),
            ],
        )
        conex.executemany(
            """INSERT OR IGNORE INTO trabajador_servicio
               (trabajador_id, servicio_id) VALUES (?, ?)""",
            [
                ("trab-plomeria-demo", "serv-plomeria"),
                ("trab-electricidad-demo", "serv-electricidad"),
                ("trab-carpinteria-demo", "serv-carpinteria"),
            ],
        )


def obtener_servicios(db_path=DB_path):
    inicializar_base(db_path)
    with conexion(db_path) as conex:
        filas = conex.execute(
            "SELECT id, nombre, descripcion FROM servicios ORDER BY nombre"
        ).fetchall()
    return [dict(fila) for fila in filas]


def obtener_trabajadores(servicio_id=None, busqueda="", db_path=DB_path):
    """Busca perfiles activos, opcionalmente por servicio y texto."""
    inicializar_base(db_path)
    consulta = """
        SELECT DISTINCT t.id, t.nombre, t.descripcion
        FROM trabajadores AS t
        JOIN trabajador_servicio AS ts ON ts.trabajador_id = t.id
        JOIN servicios AS s ON s.id = ts.servicio_id
        WHERE t.activo = 1
    """
    parametros = []

    if servicio_id:
        consulta += " AND s.id = ?"
        parametros.append(servicio_id)

    if busqueda.strip():
        consulta += " AND (lower(t.nombre) LIKE ? OR lower(s.nombre) LIKE ?)"
        termino = f"%{busqueda.strip().lower()}%"
        parametros.extend([termino, termino])

    consulta += " ORDER BY t.nombre"

    with conexion(db_path) as conex:
        filas = conex.execute(consulta, parametros).fetchall()
    return [dict(fila) for fila in filas]


def guardar_solicitud(
    cliente,
    contacto,
    domicilio,
    descripcion,
    servicio_id,
    trabajador_id,
    fecha=None,
    db_path=DB_path,
):
    """Guarda la solicitud y devuelve su ID."""
    campos = {
        "cliente": cliente,
        "contacto": contacto,
        "domicilio": domicilio,
        "descripcion": descripcion,
        "servicio_id": servicio_id,
        "trabajador_id": trabajador_id,
    }
    for campo, valor in campos.items():
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El campo {campo} es obligatorio.")

    if fecha is None:
        fecha = date.today().isoformat()
    else:
        try:
            fecha = date.fromisoformat(fecha.strip()).isoformat()
        except (AttributeError, ValueError) as error:
            raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from error

    inicializar_base(db_path)
    solicitud_id = str(uuid4())
    creada_en = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with conexion(db_path) as conex:
        asignacion = conex.execute(
            """SELECT 1 FROM trabajador_servicio
               WHERE trabajador_id = ? AND servicio_id = ?""",
            (trabajador_id, servicio_id),
        ).fetchone()
        if asignacion is None:
            raise ValueError("El trabajador no ofrece ese servicio.")

        conex.execute(
            """INSERT INTO solicitudes
               (id, cliente, contacto, domicilio, descripcion, fecha,
                servicio_id, trabajador_id, estado, creada_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente', ?)""",
            (
                solicitud_id,
                cliente.strip(),
                contacto.strip(),
                domicilio.strip(),
                descripcion.strip(),
                fecha,
                servicio_id,
                trabajador_id,
                creada_en,
            ),
        )
    return solicitud_id


def obtener_solicitudes(db_path=DB_path):
    inicializar_base(db_path)
    with conexion(db_path) as conex:
        filas = conex.execute("""
            SELECT so.id, so.cliente, so.contacto, so.domicilio,
                   so.descripcion, so.fecha, so.estado,
                   s.nombre AS servicio, t.nombre AS trabajador
            FROM solicitudes AS so
            JOIN servicios AS s ON s.id = so.servicio_id
            JOIN trabajadores AS t ON t.id = so.trabajador_id
            ORDER BY so.creada_en DESC
        """).fetchall()
    return [dict(fila) for fila in filas]


def obtener_solicitud(solicitud_id, db_path=DB_path):
    inicializar_base(db_path)
    with conexion(db_path) as conex:
        fila = conex.execute(
            """SELECT so.*, s.nombre AS servicio, t.nombre AS trabajador
               FROM solicitudes AS so
               JOIN servicios AS s ON s.id = so.servicio_id
               JOIN trabajadores AS t ON t.id = so.trabajador_id
               WHERE so.id = ?""",
            (solicitud_id,),
        ).fetchone()
        if fila is None:
            return None

        solicitud = dict(fila)
        cotizaciones = conex.execute(
            """SELECT id, importe, materiales_incluidos, condiciones, estado
               FROM cotizaciones WHERE solicitud_id = ? ORDER BY creada_en""",
            (solicitud_id,),
        ).fetchall()

    solicitud["cotizaciones"] = [
        {
            **dict(cotizacion),
            "materiales_incluidos": bool(cotizacion["materiales_incluidos"]),
        }
        for cotizacion in cotizaciones
    ]
    return solicitud


def registrar_cotizacion(
    solicitud_id, importe, materiales_incluidos, condiciones, db_path=DB_path
):
    try:
        importe = float(importe)
    except (TypeError, ValueError) as error:
        raise ValueError("El importe debe ser numérico.") from error
    if not isfinite(importe) or importe < 0:
        raise ValueError("El importe debe ser mayor o igual a cero.")
    if not isinstance(materiales_incluidos, bool):
        raise ValueError("materiales_incluidos debe ser True o False.")
    if not isinstance(condiciones, str) or not condiciones.strip():
        raise ValueError("Las condiciones son obligatorias.")

    inicializar_base(db_path)
    cotizacion_id = str(uuid4())
    creada_en = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with conexion(db_path) as conex:
        solicitud = conex.execute(
            "SELECT estado FROM solicitudes WHERE id = ?", (solicitud_id,)
        ).fetchone()
        if solicitud is None:
            raise ValueError("No existe la solicitud.")
        if solicitud["estado"] not in ("pendiente", "cotizada"):
            raise ValueError("La solicitud ya no acepta cotizaciones.")

        conex.execute(
            """INSERT INTO cotizaciones
               (id, solicitud_id, importe, materiales_incluidos,
                condiciones, creada_en)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                cotizacion_id,
                solicitud_id,
                importe,
                int(materiales_incluidos),
                condiciones.strip(),
                creada_en,
            ),
        )
        conex.execute(
            "UPDATE solicitudes SET estado = 'cotizada' WHERE id = ?",
            (solicitud_id,),
        )
    return cotizacion_id


def aceptar_cotizacion(cotizacion_id, db_path=DB_path):
    """Acepta una cotización y marca las demás como no seleccionadas."""
    inicializar_base(db_path)
    with conexion(db_path) as conex:
        cotizacion = conex.execute(
            """SELECT c.solicitud_id, c.estado AS estado_cotizacion,
                      so.estado AS estado_solicitud
               FROM cotizaciones AS c
               JOIN solicitudes AS so ON so.id = c.solicitud_id
               WHERE c.id = ?""",
            (cotizacion_id,),
        ).fetchone()
        if cotizacion is None or cotizacion["estado_cotizacion"] != "pendiente":
            raise ValueError("La cotización no existe o ya fue resuelta.")
        if cotizacion["estado_solicitud"] != "cotizada":
            raise ValueError("La solicitud no está cotizada.")

        conex.execute(
            "UPDATE cotizaciones SET estado = 'aceptada' WHERE id = ?",
            (cotizacion_id,),
        )
        conex.execute(
            """UPDATE cotizaciones SET estado = 'no_seleccionada'
               WHERE solicitud_id = ? AND id != ? AND estado = 'pendiente'""",
            (cotizacion["solicitud_id"], cotizacion_id),
        )
        conex.execute(
            """UPDATE solicitudes SET estado = 'cotizacion_aceptada'
               WHERE id = ?""",
            (cotizacion["solicitud_id"],),
        )


def actualizar_estado(solicitud_id, nuevo_estado, db_path=DB_path):
    transiciones = {
        "pendiente": {"cancelada"},
        "cotizada": {"cancelada"},
        "cotizacion_aceptada": {"en_proceso", "cancelada"},
        "en_proceso": {"completada", "cancelada"},
        "completada": set(),
        "cancelada": set(),
    }
    if nuevo_estado not in transiciones:
        raise ValueError(f"Estado no válido: {nuevo_estado}.")

    inicializar_base(db_path)
    with conexion(db_path) as conex:
        solicitud = conex.execute(
            "SELECT estado FROM solicitudes WHERE id = ?", (solicitud_id,)
        ).fetchone()
        if solicitud is None:
            raise ValueError("No existe la solicitud.")
        if nuevo_estado not in transiciones[solicitud["estado"]]:
            raise ValueError(
                f"No se permite cambiar de '{solicitud['estado']}' "
                f"a '{nuevo_estado}'."
            )
        conex.execute(
            "UPDATE solicitudes SET estado = ? WHERE id = ?",
            (nuevo_estado, solicitud_id),
        )
