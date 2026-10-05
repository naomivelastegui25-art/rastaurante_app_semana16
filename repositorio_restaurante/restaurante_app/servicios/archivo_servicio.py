import json
import os

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta

# Carpeta base del proyecto (la que contiene main.py). Se calcula a partir de
# la ubicación de este archivo para que los datos se guarden siempre en
# <proyecto>/datos, sin importar desde dónde se ejecute el programa.
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS: str = os.path.join(BASE_DIR, "datos")


class ArchivoServicio:
    """Centraliza la lectura y escritura de productos, usuarios y ventas en JSON."""

    def __init__(self, carpeta_datos: str = CARPETA_DATOS) -> None:
        self.ruta_productos: str = os.path.join(carpeta_datos, "productos.json")
        self.ruta_usuarios: str = os.path.join(carpeta_datos, "usuarios.json")
        self.ruta_ventas: str = os.path.join(carpeta_datos, "ventas.json")

    # ------------------------------------------------------------------
    # Operaciones genéricas
    # ------------------------------------------------------------------
    def _guardar_datos(self, ruta_archivo: str, datos: list[dict]) -> bool:
        try:
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
            with open(ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"Error de permisos: no se puede escribir en {ruta_archivo}.")
        except OSError as error:
            print(f"Error al escribir {ruta_archivo}: {error}")
        return False

    def _cargar_datos(self, ruta_archivo: str) -> list[dict]:
        nombre = os.path.basename(ruta_archivo)
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            # Primera ejecución: el archivo aún no existe, se inicia vacío.
            return []
        except json.JSONDecodeError:
            print(f"Advertencia: {nombre} tiene contenido JSON inválido. "
                  "Se iniciará con una colección vacía.")
            return []
        except PermissionError:
            print(f"Error de permisos: no se puede leer {nombre}. "
                  "Se iniciará con una colección vacía.")
            return []

        if not isinstance(datos, list):
            print(f"Advertencia: {nombre} no contiene una lista de registros. "
                  "Se iniciará con una colección vacía.")
            return []
        return datos

    # ------------------------------------------------------------------
    # Productos
    # ------------------------------------------------------------------
    def guardar_productos(self, productos: list[Producto]) -> bool:
        datos = [producto.convertir_a_diccionario() for producto in productos]
        return self._guardar_datos(self.ruta_productos, datos)

    def cargar_productos(self) -> list[dict]:
        return self._cargar_datos(self.ruta_productos)

    # ------------------------------------------------------------------
    # Usuarios
    # ------------------------------------------------------------------
    def guardar_usuarios(self, usuarios: list[Usuario]) -> bool:
        datos = [usuario.convertir_a_diccionario() for usuario in usuarios]
        return self._guardar_datos(self.ruta_usuarios, datos)

    def cargar_usuarios(self) -> list[dict]:
        return self._cargar_datos(self.ruta_usuarios)

    # ------------------------------------------------------------------
    # Ventas
    # ------------------------------------------------------------------
    def guardar_ventas(self, ventas: list[Venta]) -> bool:
        datos = [venta.convertir_a_diccionario() for venta in ventas]
        return self._guardar_datos(self.ruta_ventas, datos)

    def cargar_ventas(self) -> list[dict]:
        return self._cargar_datos(self.ruta_ventas)
