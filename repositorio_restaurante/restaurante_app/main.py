import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView
from ui.recursos import cargar_imagen


class Aplicacion:
    """Crea la única ventana, prepara el servicio y controla el cambio entre vistas."""

    def __init__(self) -> None:
        self.ventana: tk.Tk = tk.Tk()
        self.ventana.title("Restaurante App")
        self.ventana.geometry("980x640")
        self.ventana.minsize(860, 580)

        # Ícono de la ventana (se conserva la referencia para que no se libere).
        self.icono_ventana: tk.PhotoImage | None = cargar_imagen("logo.png")
        if self.icono_ventana is not None:
            self.ventana.iconphoto(True, self.icono_ventana)

        self._configurar_estilos()
        self.servicio: RestauranteServicio = RestauranteServicio()
        self.vista_actual: ttk.Frame | None = None

        self.mostrar_login()

    def _crear_fuente(self, tamano: int) -> tkfont.Font:
        """Fuente en negrita derivada de la fuente por defecto del sistema."""
        fuente = tkfont.nametofont("TkDefaultFont").copy()
        fuente.configure(size=tamano, weight="bold")
        self._fuentes.append(fuente)  # se conserva la referencia para que no se libere
        return fuente

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.ventana)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")

        self._fuentes: list[tkfont.Font] = []
        estilo.configure("Titulo.TLabel", font=self._crear_fuente(20))
        estilo.configure("Subtitulo.TLabel", foreground="#666666")
        estilo.configure("Seccion.TLabel", font=self._crear_fuente(14))
        estilo.configure("Encabezado.TFrame", background="#2f3e46")
        estilo.configure("Encabezado.TLabel", background="#2f3e46", foreground="#ffffff")
        estilo.configure("EncabezadoTitulo.TLabel", background="#2f3e46", foreground="#ffffff",
                         font=self._crear_fuente(14))
        estilo.configure("Exito.TButton", font=self._crear_fuente(10))
        estilo.configure("Treeview", rowheight=26)
        estilo.configure("Treeview.Heading", font=self._crear_fuente(10))

    def _cambiar_vista(self, nueva_vista: ttk.Frame) -> None:
        if self.vista_actual is not None:
            self.vista_actual.destroy()
        self.vista_actual = nueva_vista
        nueva_vista.pack(fill="both", expand=True)

    def mostrar_login(self) -> None:
        self._cambiar_vista(LoginView(self.ventana, self.servicio, self.mostrar_principal))

    def mostrar_principal(self, usuario: Usuario) -> None:
        self._cambiar_vista(MainView(self.ventana, self.servicio, usuario, self.mostrar_login))

    def ejecutar(self) -> None:
        self.ventana.mainloop()


def main() -> None:
    Aplicacion().ejecutar()


if __name__ == "__main__":
    main()
