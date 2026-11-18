"""Catálogo  de servicios ofrecidos en la aplicación."""

SERVICIOS: list[dict[str, str]] = [
    {"id": "plomeria", "nombre": "Servicios de Plomería"},
    {"id": "electricidad", "nombre": "Servicios de Electricidad"},
    {"id": "limpieza", "nombre": "Servicios de Limpieza"},
    {"id": "reparaciones", "nombre": "Servicios de Reparaciones generales"},
    {"id": "pintura", "nombre": "Servicios de Pintura"},
    {"id": "carpinteria", "nombre": "Servicios de Carpintería"},
    {"id": "jardineria", "nombre": "Servicios de Jardinería"},
    {"id": "cerrajeria", "nombre": "Servicios de Cerrajería"},
]


def obtener_servicios() -> list[dict[str, str]]:
    """Devuelve los servicios disponibles para que la interfaz los consulte."""
    return [servicio.copy() for servicio in SERVICIOS]
