Ofivanta. Entrega de la sesión 12

Equipo Ofivanta
20 de noviembre de 2026

Ofivanta es un prototipo para buscar servicios para el hogar, revisar un perfil y pedir una cotización antes de confirmar el trabajo. Está hecho con Python y tkinter y conserva las cinco ventanas del profesor dentro de la navegación de la app.

Archivos de la entrega:

- [01_presentacion_Ofivanta.pptx](01_presentacion_Ofivanta.pptx): presentación de hasta 10 diapositivas. Está pensada para una exposición de 5 minutos y 5 minutos adicionales de retroalimentación.
- [02_prototipo.zip](02_prototipo.zip): código y recursos del prototipo del 20 de noviembre. Se entrega una sola copia comprimida en esta carpeta; no se repite aquí el árbol de código sin comprimir.
- [03_observaciones_y_plan_de_mejora.md](03_observaciones_y_plan_de_mejora.md): espacio para registrar los comentarios reales y propuesta de trabajo del equipo.
- [04_video_demostracion.mp4](04_video_demostracion.mp4): demostración anterior, del 19 de noviembre. Sirve como apoyo; el prototipo del día 20 tiene mejoras posteriores de interfaz y cuentas que no aparecen en ese video.

Cómo abrir el prototipo en VS Code

Descomprime 02_prototipo.zip y abre la carpeta que contiene src. Necesitas Python 3.10 o posterior con tkinter. En la terminal de VS Code, crea el entorno virtual:

```powershell
python -m venv .venv
```

En VS Code, usa Python: Select Interpreter y elige .venv\Scripts\python.exe. Después ejecuta desde la misma carpeta:

```powershell
.\.venv\Scripts\python.exe -m src.app.main
```

El ZIP no incluye .venv, bases personales, respaldos ni contraseñas personales. El entorno y las bases locales se crean al usar la app. Para la demostración conviene crear una cuenta con datos ficticios o entrar como invitado. Google y Apple todavía no conectan cuentas; los perfiles de trabajadores y los precios de referencia son ejemplos.

El recorrido para mostrar en clase es: elegir un oficio y una dirección, revisar un perfil, enviar una solicitud, consultar una cotización y ver el seguimiento. La presentación debe distinguir lo que ya funciona localmente de lo que falta para prestar servicios reales.

Integrantes: Laira Fernanda Barroso Villa, Irma Gloria Núñez Romo, Gonzalo Martínez Zermeño, Leonardo Alfaro García, Jorge Fernando Villalobos García y Luis Ernesto Guerrero García.
