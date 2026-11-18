# Personas ficticias para probar la lista. No son perfiles verificados.
TRABAJADORES = [
    {"id": 1, "nombre": "Ana López", "servicio_id": "plomeria", "zona": "León Centro", "disponible": True},
    {"id": 2, "nombre": "Carlos Pérez", "servicio_id": "plomeria", "zona": "León Norte", "disponible": True},
    {"id": 3, "nombre": "María Torres", "servicio_id": "electricidad", "zona": "León Centro", "disponible": True},
    {"id": 4, "nombre": "Luis Ramírez", "servicio_id": "electricidad", "zona": "León Sur", "disponible": False},
    {"id": 5, "nombre": "Sofía García", "servicio_id": "limpieza", "zona": "León Norte", "disponible": True},
    {"id": 6, "nombre": "Pedro Sánchez", "servicio_id": "reparaciones", "zona": "León Centro", "disponible": True},
    {"id": 7, "nombre": "Laura Díaz", "servicio_id": "pintura", "zona": "León Sur", "disponible": True},
    {"id": 8, "nombre": "Jorge Ruiz", "servicio_id": "carpinteria", "zona": "León Norte", "disponible": True},
    {"id": 9, "nombre": "Elena Flores", "servicio_id": "jardineria", "zona": "León Sur", "disponible": True},
    {"id": 10, "nombre": "Daniel Mora", "servicio_id": "cerrajeria", "zona": "León Centro", "disponible": True},
]


def obtener_trabajadores():
    # Devolvemos copias para no cambiar el catálogo desde la ventana.
    return [trabajador.copy() for trabajador in TRABAJADORES]
