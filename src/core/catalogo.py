"""Datos ficticios para demostrar Ofivanta sin conexión a Internet."""

SERVICIOS = [
    ("serv-plomeria", "Plomería", "Fugas, llaves, tuberías y mantenimiento."),
    ("serv-electricidad", "Electricidad", "Contactos, iluminación e instalaciones."),
    ("serv-limpieza", "Limpieza", "Limpieza de espacios y mantenimiento del hogar."),
    ("serv-reparaciones", "Reparaciones", "Arreglos y mantenimiento general."),
    ("serv-pintura", "Pintura", "Pintura de interiores y exteriores."),
    ("serv-carpinteria", "Carpintería", "Muebles, puertas y reparaciones de madera."),
    ("serv-jardineria", "Jardinería", "Cuidado de jardines y plantas."),
    ("serv-cerrajeria", "Cerrajería", "Mantenimiento e instalación de cerraduras."),
]

# ID, nombre, presentación, zona, disponible, oficio.
TRABAJADORES = [
    ("1", "Ana López", "Reparación de fugas y mantenimiento de llaves.", "León Centro", True, "serv-plomeria"),
    ("2", "Carlos Pérez", "Instalación de tuberías y revisión de fugas.", "León Norte", True, "serv-plomeria"),
    ("3", "María Torres", "Revisión de contactos e iluminación del hogar.", "León Centro", True, "serv-electricidad"),
    ("4", "Luis Ramírez", "Mantenimiento de instalaciones eléctricas.", "León Sur", False, "serv-electricidad"),
    ("5", "Sofía García", "Limpieza y cuidado de espacios interiores.", "León Norte", True, "serv-limpieza"),
    ("6", "Pedro Sánchez", "Reparaciones pequeñas y mantenimiento general.", "León Centro", True, "serv-reparaciones"),
    ("7", "Laura Díaz", "Preparación y pintura de muros.", "León Sur", True, "serv-pintura"),
    ("8", "Jorge Ruiz", "Reparación de puertas y muebles de madera.", "León Norte", True, "serv-carpinteria"),
    ("9", "Elena Flores", "Mantenimiento de jardines y áreas verdes.", "León Sur", True, "serv-jardineria"),
    ("10", "Daniel Mora", "Instalación y mantenimiento de cerraduras.", "León Centro", True, "serv-cerrajeria"),
]
