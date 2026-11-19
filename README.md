# Ofivanta

Ofivanta es un proyecto escolar para buscar trabajadores de oficios y solicitar servicios para el hogar. La idea es encontrar a un plomero, electricista u otro trabajador, explicar qué se necesita y revisar una cotización antes de confirmar.

La aplicación está hecha con Python y tkinter. Los perfiles son ficticios y las solicitudes se guardan en la computadora. Esta versión no conecta usuarios reales ni realiza pagos.

## Cómo abrirla

Necesitas Python 3.10 o posterior con tkinter. Abre la carpeta del proyecto en VS Code y ejecuta en su terminal:

```text
python -m src.app.main
```

También puedes presionar F5 usando la configuración incluida o abrir `iniciar_ofivanta.bat` en Windows. No hay paquetes externos que instalar.

## Qué puedes hacer

1. Entrar a Buscar servicio desde el inicio.
2. Filtrar por oficio, buscar por nombre o zona y consultar la disponibilidad.
3. Elegir a un trabajador y llenar el formulario de solicitud.
4. Revisar la solicitud en Mis solicitudes.
5. Crear una cotización de ejemplo desde Seguimiento, activando la simulación de prestador.
6. Volver a Mis solicitudes, abrir Ver detalles y aceptar la cotización.
7. Simular el inicio y la finalización desde Seguimiento.

La solicitud pasa por Pendiente, Cotizada, Confirmada, En proceso y Finalizada. Se puede cancelar antes de iniciar el trabajo. Los botones de simulación solo permiten los cambios que corresponden al estado actual.

Los datos se guardan automáticamente en `data/ofivanta.sqlite3`. Ese archivo se crea al abrir la app y no se debe subir a GitHub con datos personales. Para usar otra base local se puede definir la variable `OFIVANTA_DB_PATH` antes de iniciar.

## Archivos del proyecto

Las cinco ventanas siguen en `src/app`: `win_home.py`, `win_form.py`, `win_list.py`, `win_table.py` y `win_canvas.py`. El menú está en `main.py`, el estilo compartido en `ui.py` y el catálogo y guardado local en `src/core`.

La [documentación de la interfaz y el modelo de ingresos](docs/07_interfaz_y_modelo_ingresos.md) explica los cambios y contiene las capturas finales. Incluye el logo azul, el inicio con degradado, botones redondos, favoritos y los planes de ejemplo. El menú «Ir a» conserva el acceso a las cinco ventanas originales del profesor. Los documentos de sesiones anteriores se conservan como evidencia del avance.

## Planes de ejemplo

El plan Básico no tiene mensualidad y usa una comisión del 10 %. El plan Pro registra $149 simulados por 30 días y aplica el 7 % a nuevas cotizaciones. Pro incluye una agenda por trabajador y un resumen de ganancias. El porcentaje queda guardado en cada cotización; cambiar de plan no cambia propuestas anteriores.

En «Planes e ingresos» puedes comparar ambos planes con el importe de un trabajo y la cantidad de trabajos en 30 días. La comparación incluye la cuota de Pro. El apartado «Ingresos» muestra las comisiones de trabajos finalizados y los periodos Pro activados en la demostración. Todos estos importes son ejemplos: no hay pagos, tarjetas ni renovaciones automáticas.

## Pruebas

Desde la carpeta del proyecto:

```text
python -m unittest discover -s tests -v
```

Las pruebas usan bases temporales. Comprueban filtros, formularios, guardado, cotizaciones, cambios de estado y apertura desde el menú. Las pruebas de ventanas necesitan una sesión de escritorio con tkinter.
