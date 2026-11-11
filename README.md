# CERTEO — Servicios con confianza

Proyecto integrador ODS 8: Trabajo Decente y Crecimiento Económico.
MVP educativo con una ventana principal y cinco subventanas tkinter.

## Ejecutar en Windows

Abre una terminal en la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m src.app.main
```

No requiere paquetes externos. Python debe incluir tkinter.
En VS Code instala Python, Pylance y Python Debugger de Microsoft, selecciona
el intérprete `.venv` y presiona F5 con «Ejecutar CERTEO (src.app.main)».
Se usa `debugpy`, el tipo actual del depurador de Python.

## Documentación

Consulta [la documentación y las evidencias](docs/04_skeleton_5_ventanas_tkinter_equipo.md).
Los datos del CSV son ejemplos ficticios para demostrar la tabla.
Este esqueleto no verifica identidades ni conecta usuarios reales.
