# Adaptación de ventana – Ofivanta

**Integrante:** Irma Gloria Núñez Romo  
**Ventana asignada:** Ventana 2 – Formulario, validación y guardado  
**Archivo:** `src/app/win_form.py`  
**Proyecto:** Ofivanta

## 1. Objetivo de la ventana

La ventana permite que un cliente envíe una solicitud para contratar un servicio del hogar. Recibe el servicio y el trabajador que el cliente seleccionó previamente en el catálogo, solicita sus datos de contacto y la información del problema, valida los datos y confirma el envío.

## 2. Cambios realizados

- Se cambió el formulario de ejemplo de nombre y edad por un formulario para solicitar un servicio.
- Se agregaron los campos nombre completo, contacto, domicilio, descripción del problema y fecha deseada.
- Se muestran el servicio y el trabajador seleccionados desde el catálogo.
- Se valida que no existan campos vacíos.
- Se valida que el contacto sea un correo electrónico o un teléfono de 10 a 15 dígitos.
- Se valida que la fecha tenga formato `AAAA-MM-DD` y no sea anterior al día actual.
- Se agregó una pantalla de resumen para que el cliente confirme los datos antes de enviar.
- La solicitud se envía con estado **Pendiente**.
- Se aclara que el precio se determina después mediante una cotización.
- Se sustituyó el guardado directo en TXT por una llamada a `guardar_solicitud()`.

## 3. Diseño propuesto

La ventana tiene un encabezado con el título “Solicitar un servicio”, un recuadro que muestra el servicio y el trabajador seleccionados, un formulario con los datos del cliente y dos acciones: cancelar o revisar y enviar la solicitud. Se utiliza una distribución sencilla para que el proceso sea fácil de entender.

## 4. Reflexión

Estos cambios apoyan la idea de Ofivanta porque permiten que una persona solicite desde la aplicación un servicio que necesita en su casa. La validación ayuda a evitar solicitudes incompletas o con datos incorrectos. Además, mostrar un resumen antes de enviar permite revisar la información y el estado Pendiente deja claro que el trabajador todavía debe confirmar la solicitud y enviar una cotización.

## 5. Pruebas que deben realizarse

1. Enviar una solicitud con todos los campos correctos.
2. Intentar enviar el formulario dejando un campo vacío.
3. Escribir un contacto con formato incorrecto.
4. Escribir una fecha con formato incorrecto.
5. Intentar seleccionar una fecha anterior al día actual.
6. Confirmar que la solicitud se guarda con estado Pendiente.
7. Confirmar que el número de solicitud se muestra después de guardar.
8. Comprobar que la solicitud aparece en “Mis solicitudes”.

## 6. Evidencias

**Captura de la ventana original:** insertar aquí una captura de `win_form.py` antes de los cambios.

**Captura del diseño propuesto o ventana modificada:** insertar aquí una captura de la ventana ejecutándose.

## 7. Nota de integración

La ventana importa `guardar_solicitud` desde `src/core/datos.py` y espera que la función reciba un diccionario con los datos de la solicitud y devuelva el identificador o número generado. Este contrato debe confirmarse con Luis, responsable de la lógica compartida y del guardado. También se debe comprobar que `main.py` y la ventana de catálogo llamen a `open_win_form(parent, servicio, trabajador)` con los datos seleccionados.

La ventana puede abrirse por separado para revisar su interfaz. Para guardar de forma integrada se necesita que exista la función compartida del equipo.
