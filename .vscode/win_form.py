"""
Ofivanta - Ventana 2: Solicitar servicio
Archivo: src/app/win_form.py

La ventana recibe el servicio y trabajador elegidos en el catálogo.
Para guardar, utiliza la función compartida guardar_solicitud() de src/core/datos.py.
"""

import re
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox


# Importación de la función compartida. Luis debe crearla en src/core/datos.py.
try:
    from src.core.datos import guardar_solicitud as _guardar_solicitud
except (ImportError, ModuleNotFoundError):
    _guardar_solicitud = None


class VentanaSolicitud:
    def __init__(self, parent, servicio=None, trabajador=None,
                 guardar_callback=None, on_close=None):
        self.parent = parent
        self.servicio = servicio
        self.trabajador = trabajador
        self.guardar_callback = guardar_callback or _guardar_solicitud
        self.on_close = on_close

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Ofivanta | Solicitar servicio")
        self.ventana.geometry("760x720")
        self.ventana.minsize(650, 650)
        self.ventana.configure(bg="#F4F7FB")

        self._crear_estilos()
        self._crear_interfaz()
        self.ventana.transient(parent)

    def _crear_estilos(self):
        estilo = ttk.Style(self.ventana)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Titulo.TLabel", background="#F4F7FB", foreground="#16324F",
            font=("Arial", 20, "bold")
        )
        estilo.configure(
            "Subtitulo.TLabel", background="#F4F7FB", foreground="#526579",
            font=("Arial", 10)
        )
        estilo.configure(
            "Campo.TLabel", background="#FFFFFF", foreground="#263746",
            font=("Arial", 10, "bold")
        )
        estilo.configure(
            "Accion.TButton", font=("Arial", 10, "bold"),
            padding=(14, 9)
        )

    @staticmethod
    def _texto_seleccion(valor, campo):
        """Acepta tanto texto como diccionarios provenientes del catálogo."""
        if valor is None:
            return "No seleccionado"
        if isinstance(valor, dict):
            posibles = ("nombre", "name", "titulo", "servicio", "especialidad")
            for clave in posibles:
                if valor.get(clave):
                    return str(valor[clave])
            return str(valor)
        return str(valor)

    def _crear_interfaz(self):
        contenedor = tk.Frame(self.ventana, bg="#F4F7FB")
        contenedor.pack(fill="both", expand=True, padx=24, pady=18)

        ttk.Label(contenedor, text="Solicitar un servicio",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            contenedor,
            text="Completa tus datos para enviar una solicitud al trabajador.",
            style="Subtitulo.TLabel"
        ).pack(anchor="w", pady=(4, 14))

        seleccion = tk.Frame(contenedor, bg="#E8F1FA", padx=14, pady=10)
        seleccion.pack(fill="x", pady=(0, 12))
        tk.Label(
            seleccion, text="SERVICIO SELECCIONADO",
            bg="#E8F1FA", fg="#526579", font=("Arial", 8, "bold")
        ).pack(anchor="w")
        self.lbl_servicio = tk.Label(
            seleccion, text=self._texto_seleccion(self.servicio, "servicio"),
            bg="#E8F1FA", fg="#16324F", font=("Arial", 10, "bold")
        )
        self.lbl_servicio.pack(anchor="w", pady=(2, 7))
        tk.Label(
            seleccion, text="TRABAJADOR SELECCIONADO",
            bg="#E8F1FA", fg="#526579", font=("Arial", 8, "bold")
        ).pack(anchor="w")
        self.lbl_trabajador = tk.Label(
            seleccion, text=self._texto_seleccion(self.trabajador, "trabajador"),
            bg="#E8F1FA", fg="#16324F", font=("Arial", 10, "bold")
        )
        self.lbl_trabajador.pack(anchor="w", pady=(2, 0))

        tarjeta = tk.Frame(contenedor, bg="white", padx=18, pady=15)
        tarjeta.pack(fill="both", expand=True)

        self.nombre = tk.StringVar()
        self.contacto = tk.StringVar()
        self.domicilio = tk.StringVar()
        self.fecha = tk.StringVar(value=date.today().isoformat())

        self._campo(tarjeta, "Nombre completo", self.nombre)
        self._campo(tarjeta, "Teléfono o correo de contacto", self.contacto)
        self._campo(tarjeta, "Domicilio donde se realizará el servicio", self.domicilio)
        self._campo(tarjeta, "Fecha deseada (AAAA-MM-DD)", self.fecha)

        ttk.Label(tarjeta, text="Descripción del problema",
                  style="Campo.TLabel").pack(anchor="w", pady=(10, 5))
        self.descripcion = tk.Text(
            tarjeta, height=5, wrap="word", font=("Arial", 10),
            relief="solid", bd=1, padx=8, pady=7
        )
        self.descripcion.pack(fill="x")

        tk.Label(
            tarjeta,
            text="El precio se definirá después mediante una cotización del trabajador.",
            bg="white", fg="#8A5A00", font=("Arial", 9, "italic"),
            wraplength=650, justify="left"
        ).pack(anchor="w", pady=(10, 0))

        botones = tk.Frame(contenedor, bg="#F4F7FB")
        botones.pack(fill="x", pady=(14, 0))
        ttk.Button(
            botones, text="Cancelar", command=self.ventana.destroy
        ).pack(side="right", padx=(8, 0))
        ttk.Button(
            botones, text="Revisar y enviar solicitud",
            style="Accion.TButton", command=self.validar_y_confirmar
        ).pack(side="right")

    def _campo(self, parent, etiqueta, variable):
        ttk.Label(parent, text=etiqueta, style="Campo.TLabel").pack(
            anchor="w", pady=(7, 4)
        )
        entrada = ttk.Entry(parent, textvariable=variable, font=("Arial", 10))
        entrada.pack(fill="x", ipady=5)

    def _validar(self):
        nombre = self.nombre.get().strip()
        contacto = self.contacto.get().strip()
        domicilio = self.domicilio.get().strip()
        descripcion = self.descripcion.get("1.0", "end").strip()
        fecha_texto = self.fecha.get().strip()

        if not all((nombre, contacto, domicilio, descripcion, fecha_texto)):
            messagebox.showwarning(
                "Datos incompletos",
                "Completa todos los campos antes de enviar la solicitud.",
                parent=self.ventana
            )
            return None

        # Se acepta un correo válido o un teléfono con al menos 10 dígitos.
        es_correo = re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            contacto
        ) is not None
        digitos = re.sub(r"\D", "", contacto)
        es_telefono = len(digitos) >= 10 and len(digitos) <= 15

        if not (es_correo or es_telefono):
            messagebox.showwarning(
                "Contacto no válido",
                "Escribe un correo válido o un teléfono de entre 10 y 15 dígitos.",
                parent=self.ventana
            )
            return None

        try:
            fecha_solicitada = date.fromisoformat(fecha_texto)
        except ValueError:
            messagebox.showwarning(
                "Fecha no válida",
                "Usa el formato AAAA-MM-DD, por ejemplo 2026-12-05.",
                parent=self.ventana
            )
            return None

        if fecha_solicitada < date.today():
            messagebox.showwarning(
                "Fecha anterior",
                "La fecha deseada no puede ser anterior al día de hoy.",
                parent=self.ventana
            )
            return None

        if self.servicio is None or self.trabajador is None:
            messagebox.showwarning(
                "Falta una selección",
                "Regresa al catálogo y selecciona un servicio y un trabajador.",
                parent=self.ventana
            )
            return None

        return {
            "cliente": nombre,
            "contacto": contacto,
            "domicilio": domicilio,
            "descripcion": descripcion,
            "fecha_deseada": fecha_texto,
            "servicio": self.servicio,
            "trabajador": self.trabajador,
            "estado": "Pendiente"
        }

    def validar_y_confirmar(self):
        datos = self._validar()
        if datos is None:
            return

        resumen = (
            f"Nombre: {datos['cliente']}\n"
            f"Contacto: {datos['contacto']}\n"
            f"Domicilio: {datos['domicilio']}\n"
            f"Servicio: {self._texto_seleccion(datos['servicio'], 'servicio')}\n"
            f"Trabajador: {self._texto_seleccion(datos['trabajador'], 'trabajador')}\n"
            f"Fecha deseada: {datos['fecha_deseada']}\n"
            f"Descripción: {datos['descripcion']}\n\n"
            "La solicitud se enviará con estado PENDIENTE.\n"
            "El envío no significa que el trabajador ya la aceptó.\n"
            "El precio se definirá mediante una cotización.\n\n"
            "¿Confirmas el envío?"
        )

        if messagebox.askyesno("Confirmar solicitud", resumen,
                               parent=self.ventana):
            self._guardar(datos)

    def _guardar(self, datos):
        if self.guardar_callback is None:
            messagebox.showerror(
                "Guardado no disponible",
                "Todavía no está conectada la función guardar_solicitud() "
                "de src/core/datos.py. Coordina con Luis para integrar el "
                "guardado compartido. No se guardó información.",
                parent=self.ventana
            )
            return

        try:
            # Contrato acordado para la integración: guardar_solicitud recibe
            # un diccionario con los campos de la solicitud y devuelve su ID.
            resultado = self.guardar_callback(datos)

            if isinstance(resultado, dict):
                numero = (resultado.get("numero_solicitud")
                          or resultado.get("id")
                          or resultado.get("numero"))
            else:
                numero = resultado

            if numero is None:
                numero = "registrada"

            messagebox.showinfo(
                "Solicitud enviada",
                f"Tu solicitud fue guardada correctamente.\n"
                f"Número de solicitud: {numero}\n"
                "Estado: Pendiente",
                parent=self.ventana
            )
            self.ventana.destroy()

        except Exception as error:
            messagebox.showerror(
                "No se pudo guardar",
                "Ocurrió un problema al guardar la solicitud.\n\n"
                f"Detalle: {error}\n\n"
                "Revisa con el equipo que guardar_solicitud() reciba "
                "el diccionario de datos.",
                parent=self.ventana
            )


def open_win_form(parent, servicio=None, trabajador=None,
                  guardar_callback=None, on_close=None):
    """
    Función de entrada para conectar esta ventana desde main.py.

    Ejemplo:
        open_win_form(root, servicio_seleccionado, trabajador_seleccionado)
    """
    return VentanaSolicitud(
        parent,
        servicio=servicio,
        trabajador=trabajador,
        guardar_callback=guardar_callback,
        on_close=on_close
    )


# Permite probar la ventana de manera independiente.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba Ofivanta")
    root.geometry("300x120")
    tk.Label(root, text="Prueba individual de win_form.py").pack(pady=15)
    tk.Button(
        root, text="Abrir formulario",
        command=lambda: open_win_form(
            root,
            servicio="Plomería",
            trabajador="Trabajador de prueba"
        )
    ).pack()
    root.mainloop()
