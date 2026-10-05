import os
import tkinter as tk

from servicios.archivo_servicio import BASE_DIR

CARPETA_ASSETS: str = os.path.join(BASE_DIR, "assets")


def cargar_imagen(nombre_archivo: str) -> tk.PhotoImage | None:
    """Carga una imagen PNG de la carpeta assets/.

    Devuelve None si el archivo no existe o no se puede leer, para que la
    aplicación siga funcionando (sin ícono) en lugar de cerrarse.
    Quien la use debe conservar la referencia, o Tkinter la libera.
    """
    ruta = os.path.join(CARPETA_ASSETS, nombre_archivo)
    try:
        return tk.PhotoImage(file=ruta)
    except tk.TclError:
        print(f"Advertencia: no se pudo cargar la imagen {nombre_archivo}.")
        return None
