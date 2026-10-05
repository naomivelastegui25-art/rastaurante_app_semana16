import tkinter as tk
from tkinter import ttk
from typing import Callable

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.recursos import cargar_imagen


class LoginView(ttk.Frame):
    """Pantalla de acceso simulada: usuario, contraseña, mensajes y botón de ingreso."""

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio,
                 al_ingresar: Callable[[Usuario], None]) -> None:
        super().__init__(master, padding=30)
        self.servicio: RestauranteServicio = servicio
        self.al_ingresar: Callable[[Usuario], None] = al_ingresar

        self.var_usuario: tk.StringVar = tk.StringVar()
        self.var_contrasena: tk.StringVar = tk.StringVar()

        self.img_logo: tk.PhotoImage | None = cargar_imagen("logo_grande.png")
        self._crear_componentes()

    def _crear_componentes(self) -> None:
        # La caja de acceso queda centrada porque el contenedor tiene una
        # sola celda que se expande y la caja no usa "sticky".
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        caja = ttk.LabelFrame(self, text="Acceso al sistema", padding=25)
        caja.grid(row=0, column=0)

        if self.img_logo is not None:
            ttk.Label(caja, image=self.img_logo).grid(
                row=0, column=0, columnspan=2, pady=(0, 8))
        ttk.Label(caja, text="Restaurante", style="Titulo.TLabel").grid(
            row=1, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(caja, text="Ingrese sus credenciales para continuar",
                  style="Subtitulo.TLabel").grid(row=2, column=0, columnspan=2, pady=(0, 18))

        ttk.Label(caja, text="Usuario:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
        ttk.Entry(caja, textvariable=self.var_usuario, width=28).grid(row=3, column=1, pady=6)

        ttk.Label(caja, text="Contraseña:").grid(row=4, column=0, sticky="e", padx=(0, 8), pady=6)
        ttk.Entry(caja, textvariable=self.var_contrasena, show="*", width=28).grid(
            row=4, column=1, pady=6)

        ttk.Button(caja, text="Ingresar", command=self._ingresar).grid(
            row=5, column=0, columnspan=2, pady=(16, 8), ipadx=20)

        self.lbl_mensaje: ttk.Label = ttk.Label(caja, text="", foreground="#b00020")
        self.lbl_mensaje.grid(row=6, column=0, columnspan=2, pady=(4, 0))

        ttk.Label(caja, text="Acceso de prueba: admin / admin123",
                  style="Subtitulo.TLabel").grid(row=7, column=0, columnspan=2, pady=(14, 0))

    def _ingresar(self) -> None:
        try:
            usuario = self.servicio.validar_acceso(
                self.var_usuario.get(), self.var_contrasena.get())
        except ValueError as error:
            self.lbl_mensaje.configure(text=str(error))
            return

        if usuario is None:
            self.lbl_mensaje.configure(text="Usuario o contraseña incorrectos.")
            self.var_contrasena.set("")
            return

        self.al_ingresar(usuario)
