# Ofivanta

Ofivanta es una aplicación escolar para buscar servicios para el hogar, como plomería, electricidad o limpieza. Permite elegir a un trabajador, explicar el problema y revisar una cotización antes de confirmar.

Está hecha con Python y tkinter. Por ahora funciona en una computadora, usa trabajadores ficticios y no realiza cobros.

Para abrirla necesitas Python 3.10 o posterior con tkinter. Abre la carpeta del proyecto en VS Code y ejecuta:

```text
python -m src.app.main
```

En Windows también puedes abrir iniciar_ofivanta.bat. No necesitas instalar paquetes adicionales.

Para probar el recorrido:

1. Entra a Buscar servicio y elige un oficio.
2. Selecciona a un trabajador y pulsa Solicitar servicio.
3. Llena el formulario y envíalo.
4. Revisa lo que guardaste en Mis solicitudes.
5. En Seguimiento, activa la simulación de prestador para crear una cotización de ejemplo.
6. Acéptala desde Ver detalles en Mis solicitudes.
7. Regresa a Seguimiento para simular el inicio y el final del trabajo.

Las pantallas se muestran dentro de la misma ventana. Puedes cambiar de sección desde el menú lateral o usar Volver. Los filtros y el formulario sin enviar se conservan al regresar.

Los datos se guardan automáticamente en data/ofivanta.sqlite3. Ese archivo es local y no se sube al repositorio. Si necesitas usar otra base, puedes indicar su ruta con OFIVANTA_DB_PATH.

Se conservan los cinco archivos del profesor en src/app: win_home.py, win_form.py, win_list.py, win_table.py y win_canvas.py. main.py los conecta, ui.py comparte el estilo y src/core maneja los datos.

La idea de ingresos es cobrar una comisión por los trabajos terminados. Básico usa el 10 % sin mensualidad. Pro usa el 7 % en nuevas cotizaciones y una cuota de ejemplo de $149 por 30 días. Incluye agenda y resumen por trabajador. Todo se simula; no hay pagos ni renovaciones automáticas.

Los cambios y las capturas están en [la documentación de la app](docs/07_interfaz_y_modelo_ingresos.md). Los documentos anteriores muestran cómo fue avanzando el proyecto.

Para ejecutar las pruebas:

```text
python -m unittest discover -s tests -v
```

Pasaron 53 pruebas de búsqueda, formularios, guardado, cotizaciones, planes y navegación. Usan datos temporales y necesitan una sesión de escritorio con tkinter.
