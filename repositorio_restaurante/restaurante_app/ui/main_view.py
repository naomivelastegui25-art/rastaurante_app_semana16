import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.recursos import cargar_imagen

COLOR_OK: str = "#1b6e2d"
COLOR_ERROR: str = "#b00020"


class SeccionUsuarios(ttk.Frame):
    """Gestión de usuarios: formulario + Treeview, solo para el rol Administrador.

    Eventos que coordina (ninguno contiene reglas de negocio, solo las delega
    a RestauranteServicio):
        Treeview  -> <<TreeviewSelect>> -> bind()      -> _al_seleccionar_fila -> cargar formulario
        Combobox  -> <<ComboboxSelected>> -> bind()     -> _al_cambiar_rol      -> mensaje informativo
        Entry/frm -> <Return>            -> bind()      -> _registrar (reutilizado)
        Entry/frm -> <Escape>            -> bind()      -> _limpiar_formulario (reutilizado)
        Botones   -> command=            -> _registrar / _actualizar / _eliminar / _limpiar_formulario
    """

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio,
                 usuario_actual: Usuario) -> None:
        super().__init__(master, padding=12)
        self.servicio: RestauranteServicio = servicio
        self.usuario_actual: Usuario = usuario_actual

        self.var_identificacion: tk.StringVar = tk.StringVar()
        self.var_nombre: tk.StringVar = tk.StringVar()
        self.var_contrasena: tk.StringVar = tk.StringVar()
        self.var_rol: tk.StringVar = tk.StringVar(value=Usuario.ROLES[-1])

        # Identificación del usuario seleccionado en la tabla (None = alta nueva).
        self._identificacion_seleccionada: str | None = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Gestión de usuarios", style="Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self._crear_formulario()
        self._crear_estado()
        self._crear_tabla()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_formulario(self) -> None:
        marco = ttk.LabelFrame(self, text="Datos del usuario", padding=12)
        marco.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(1, weight=1)
        marco.columnconfigure(3, weight=1)

        ttk.Label(marco, text="Identificación:").grid(
            row=0, column=0, sticky="e", padx=(0, 6), pady=5)
        self.ent_identificacion: ttk.Entry = ttk.Entry(marco, textvariable=self.var_identificacion)
        self.ent_identificacion.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Nombre:").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=5)
        self.ent_nombre: ttk.Entry = ttk.Entry(marco, textvariable=self.var_nombre)
        self.ent_nombre.grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Contraseña:").grid(
            row=1, column=0, sticky="e", padx=(0, 6), pady=5)
        self.ent_contrasena: ttk.Entry = ttk.Entry(
            marco, textvariable=self.var_contrasena, show="*")
        self.ent_contrasena.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Rol:").grid(row=1, column=2, sticky="e", padx=(0, 6), pady=5)
        self.cmb_rol: ttk.Combobox = ttk.Combobox(
            marco, textvariable=self.var_rol, values=Usuario.ROLES, state="readonly")
        self.cmb_rol.grid(row=1, column=3, sticky="ew", pady=5)
        # <<ComboboxSelected>>: evento propio de ttk.Combobox, se asocia con bind().
        self.cmb_rol.bind("<<ComboboxSelected>>", self._al_cambiar_rol)

        self.lbl_rol_info: ttk.Label = ttk.Label(marco, text="", style="Subtitulo.TLabel")
        self.lbl_rol_info.grid(row=2, column=0, columnspan=4, sticky="w", pady=(2, 0))

        botones = ttk.Frame(marco)
        botones.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(botones, text="Registrar", command=self._registrar).grid(row=0, column=0, padx=4)
        ttk.Button(botones, text="Actualizar", command=self._actualizar).grid(row=0, column=1, padx=4)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).grid(row=0, column=2, padx=4)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_formulario).grid(
            row=0, column=3, padx=4)

        # <Return> y <Escape>: eventos de teclado, se asocian con bind() sobre
        # los campos de entrada (no duplican lógica: reutilizan _registrar y
        # _limpiar_formulario, los mismos métodos que usan los botones).
        for entrada in (self.ent_identificacion, self.ent_nombre, self.ent_contrasena):
            entrada.bind("<Return>", self._al_presionar_enter)
            entrada.bind("<Escape>", self._al_presionar_escape)
        self.cmb_rol.bind("<Escape>", self._al_presionar_escape)

    def _crear_estado(self) -> None:
        self.lbl_estado: ttk.Label = ttk.Label(self, text="", foreground=COLOR_OK)
        self.lbl_estado.grid(row=2, column=0, sticky="w", pady=8)

    def _crear_tabla(self) -> None:
        marco = ttk.LabelFrame(self, text="Usuarios registrados", padding=8)
        marco.grid(row=3, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = ("identificacion", "nombre", "rol")
        self.tabla: ttk.Treeview = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = {"identificacion": "Usuario (identificación)", "nombre": "Nombre",
                       "rol": "Rol"}
        anchos = {"identificacion": 180, "nombre": 260, "rol": 130}
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

        # <<TreeviewSelect>>: evento propio de ttk.Treeview, se asocia con bind().
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    # ------------------------------------------------------------------
    # Utilidades de la vista
    # ------------------------------------------------------------------
    def _mostrar_estado(self, mensaje: str, error: bool = False) -> None:
        self.lbl_estado.configure(text=mensaje, foreground=COLOR_ERROR if error else COLOR_OK)

    def _limpiar_campos(self) -> None:
        self.var_identificacion.set("")
        self.var_nombre.set("")
        self.var_contrasena.set("")
        self.var_rol.set(Usuario.ROLES[-1])
        self.lbl_rol_info.configure(text="")
        self._identificacion_seleccionada = None

    def _limpiar_formulario(self) -> None:
        self._limpiar_campos()
        self.tabla.selection_remove(self.tabla.selection())
        self._mostrar_estado("")

    def actualizar(self) -> None:
        """Vuelve a cargar la tabla con lo que informa el servicio."""
        self.tabla.delete(*self.tabla.get_children())
        for usuario in self.servicio.listar_usuarios():
            self.tabla.insert("", "end", iid=usuario.identificacion,
                              values=(usuario.identificacion, usuario.nombre, usuario.rol))

    # ------------------------------------------------------------------
    # Eventos asociados con bind()
    # ------------------------------------------------------------------
    def _al_seleccionar_fila(self, event: "tk.Event") -> None:
        """<<TreeviewSelect>>: carga en el formulario el usuario de la fila elegida.

        Solo toma la identificación de la tabla; los demás datos los pide a
        RestauranteServicio, sin leer el resto de la información directamente
        de la fila ni del archivo.
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        identificacion = seleccion[0]
        usuario = self.servicio.buscar_usuario(identificacion)
        if usuario is None:
            return

        self._identificacion_seleccionada = usuario.identificacion
        self.var_identificacion.set(usuario.identificacion)
        self.var_nombre.set(usuario.nombre)
        self.var_contrasena.set(usuario.contrasena)
        self.var_rol.set(usuario.rol)
        self._mostrar_info_rol(usuario.rol)
        self._mostrar_estado(f"Usuario '{usuario.identificacion}' cargado en el formulario.")

    def _al_cambiar_rol(self, event: "tk.Event") -> None:
        """<<ComboboxSelected>>: solo informa lo que implica el rol elegido."""
        self._mostrar_info_rol(self.var_rol.get())

    def _mostrar_info_rol(self, rol: str) -> None:
        descripciones = {
            "Administrador": "Acceso administrativo: gestiona usuarios, productos y ventas.",
            "Empleado": "Puede operar productos y ventas, sin gestión de usuarios.",
            "Cliente": "Usuario del restaurante; puede figurar como comprador en una venta.",
        }
        self.lbl_rol_info.configure(text=descripciones.get(rol, ""))

    def _al_presionar_enter(self, event: "tk.Event") -> None:
        """<Return>: atajo de teclado que reutiliza el registro, sin duplicar lógica."""
        self._registrar()

    def _al_presionar_escape(self, event: "tk.Event") -> None:
        """<Escape>: atajo de teclado que reutiliza la limpieza del formulario."""
        self._limpiar_formulario()

    # ------------------------------------------------------------------
    # Acciones (command=): coordinan la interfaz y delegan en el servicio
    # ------------------------------------------------------------------
    def _registrar(self) -> None:
        try:
            registrado = self.servicio.registrar_usuario(
                self.var_identificacion.get(), self.var_nombre.get(),
                self.var_contrasena.get(), self.var_rol.get())
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        if not registrado:
            self._mostrar_estado("Ya existe un usuario con esa identificación.", error=True)
            return
        self.actualizar()
        self._limpiar_formulario()
        self._mostrar_estado("Usuario registrado correctamente.")

    def _actualizar(self) -> None:
        identificacion = self.var_identificacion.get().strip()
        if not identificacion:
            self._mostrar_estado("Seleccione o escriba la identificación del usuario.",
                                 error=True)
            return
        try:
            actualizado = self.servicio.actualizar_usuario(
                identificacion, self.var_nombre.get(),
                self.var_contrasena.get(), self.var_rol.get())
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        if not actualizado:
            self._mostrar_estado("No existe un usuario con esa identificación.", error=True)
            return
        self.actualizar()
        self._mostrar_estado("Usuario actualizado correctamente.")

    def _eliminar(self) -> None:
        identificacion = self.var_identificacion.get().strip()
        if not identificacion:
            self._mostrar_estado("Seleccione el usuario a eliminar.", error=True)
            return

        # La sesión activa es información de la interfaz: se evita aquí, antes
        # de llegar al servicio, para no depender de que la capa de datos
        # conozca quién inició sesión.
        if identificacion == self.usuario_actual.identificacion:
            self._mostrar_estado(
                "No puede eliminar la cuenta con la que inició sesión.", error=True)
            return

        usuario = self.servicio.buscar_usuario(identificacion)
        if usuario is None:
            self._mostrar_estado("No existe un usuario con esa identificación.", error=True)
            return
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Eliminar al usuario '{usuario.nombre}'?"):
            self._mostrar_estado("Eliminación cancelada.")
            return

        self.servicio.eliminar_usuario(identificacion)
        self.actualizar()
        self._limpiar_formulario()
        self._mostrar_estado("Usuario eliminado correctamente.")


class SeccionProductos(ttk.Frame):
    """Formulario + acciones + tabla para registrar, consultar, actualizar y eliminar productos."""

    CATEGORIAS: tuple[str, ...] = ("Plato", "Bebida", "Postre", "Otro")

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio) -> None:
        super().__init__(master, padding=12)
        self.servicio: RestauranteServicio = servicio

        self.var_codigo: tk.StringVar = tk.StringVar()
        self.var_nombre: tk.StringVar = tk.StringVar()
        self.var_precio: tk.StringVar = tk.StringVar()
        self.var_categoria: tk.StringVar = tk.StringVar(value=self.CATEGORIAS[0])
        self.var_stock: tk.StringVar = tk.StringVar(value="0")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Gestión de productos", style="Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self._crear_formulario()
        self._crear_estado()
        self._crear_tabla()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_formulario(self) -> None:
        marco = ttk.LabelFrame(self, text="Datos del producto", padding=12)
        marco.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(1, weight=1)
        marco.columnconfigure(3, weight=1)

        ttk.Label(marco, text="Código:").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Entry(marco, textvariable=self.var_codigo).grid(
            row=0, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Nombre:").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=5)
        ttk.Entry(marco, textvariable=self.var_nombre).grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Precio:").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Entry(marco, textvariable=self.var_precio).grid(
            row=1, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Categoría:").grid(row=1, column=2, sticky="e", padx=(0, 6), pady=5)
        ttk.Combobox(marco, textvariable=self.var_categoria, values=self.CATEGORIAS).grid(
            row=1, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Stock:").grid(row=2, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Spinbox(marco, textvariable=self.var_stock, from_=0, to=9999, width=8).grid(
            row=2, column=1, sticky="w", padx=(0, 16), pady=5)

        botones = ttk.Frame(marco)
        botones.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(botones, text="Registrar", command=self._registrar).grid(row=0, column=0, padx=4)
        ttk.Button(botones, text="Consultar", command=self._consultar).grid(row=0, column=1, padx=4)
        ttk.Button(botones, text="Actualizar", command=self._actualizar).grid(row=0, column=2, padx=4)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).grid(row=0, column=3, padx=4)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_formulario).grid(
            row=0, column=4, padx=4)

    def _crear_estado(self) -> None:
        self.lbl_estado: ttk.Label = ttk.Label(self, text="", foreground=COLOR_OK)
        self.lbl_estado.grid(row=2, column=0, sticky="w", pady=8)

    def _crear_tabla(self) -> None:
        marco = ttk.LabelFrame(self, text="Productos registrados", padding=8)
        marco.grid(row=3, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "precio", "categoria", "stock")
        self.tabla: ttk.Treeview = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = {"codigo": "Código", "nombre": "Nombre", "precio": "Precio",
                       "categoria": "Categoría", "stock": "Stock"}
        anchos = {"codigo": 80, "nombre": 240, "precio": 80, "categoria": 110, "stock": 70}
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

    # ------------------------------------------------------------------
    # Utilidades de la vista
    # ------------------------------------------------------------------
    def _mostrar_estado(self, mensaje: str, error: bool = False) -> None:
        self.lbl_estado.configure(text=mensaje, foreground=COLOR_ERROR if error else COLOR_OK)

    def _leer_precio_y_stock(self) -> tuple[float, int] | None:
        """Convierte los textos del formulario a números. Las reglas de negocio las valida el servicio."""
        try:
            precio = float(self.var_precio.get().strip().replace(",", "."))
        except ValueError:
            self._mostrar_estado("El precio debe ser un número.", error=True)
            return None
        try:
            stock = int(self.var_stock.get().strip())
        except ValueError:
            self._mostrar_estado("El stock debe ser un número entero.", error=True)
            return None
        return precio, stock

    def _limpiar_campos(self) -> None:
        self.var_codigo.set("")
        self.var_nombre.set("")
        self.var_precio.set("")
        self.var_categoria.set(self.CATEGORIAS[0])
        self.var_stock.set("0")

    def _limpiar_formulario(self) -> None:
        self._limpiar_campos()
        self._mostrar_estado("")

    def actualizar(self) -> None:
        """Vuelve a cargar la tabla con lo que informa el servicio."""
        self.tabla.delete(*self.tabla.get_children())
        for producto in self.servicio.listar_productos():
            self.tabla.insert("", "end", values=(
                producto.id_producto, producto.nombre, f"{producto.precio:.2f}",
                producto.categoria, producto.stock))

    # ------------------------------------------------------------------
    # Acciones (command=): coordinan la interfaz y delegan en el servicio
    # ------------------------------------------------------------------
    def _registrar(self) -> None:
        numeros = self._leer_precio_y_stock()
        if numeros is None:
            return
        precio, stock = numeros
        try:
            registrado = self.servicio.registrar_producto(
                self.var_codigo.get(), self.var_nombre.get(), precio,
                self.var_categoria.get(), stock)
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        if not registrado:
            self._mostrar_estado("Ya existe un producto con ese código.", error=True)
            return
        self.actualizar()
        self._limpiar_campos()
        self._mostrar_estado("Producto registrado correctamente.")

    def _consultar(self) -> None:
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self._mostrar_estado("Ingrese el código del producto a consultar.", error=True)
            return
        producto = self.servicio.buscar_producto(codigo)
        if producto is None:
            self._mostrar_estado("No existe un producto con ese código.", error=True)
            return
        self.var_nombre.set(producto.nombre)
        self.var_precio.set(str(producto.precio))
        self.var_categoria.set(producto.categoria)
        self.var_stock.set(str(producto.stock))
        self._mostrar_estado("Producto cargado en el formulario.")

    def _actualizar(self) -> None:
        numeros = self._leer_precio_y_stock()
        if numeros is None:
            return
        precio, stock = numeros
        try:
            actualizado = self.servicio.actualizar_producto(
                self.var_codigo.get(), self.var_nombre.get(), precio,
                self.var_categoria.get(), stock)
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        if not actualizado:
            self._mostrar_estado("No existe un producto con ese código.", error=True)
            return
        self.actualizar()
        self._mostrar_estado("Producto actualizado correctamente.")

    def _eliminar(self) -> None:
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self._mostrar_estado("Ingrese el código del producto a eliminar.", error=True)
            return
        producto = self.servicio.buscar_producto(codigo)
        if producto is None:
            self._mostrar_estado("No existe un producto con ese código.", error=True)
            return
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Eliminar el producto '{producto.nombre}'?"):
            self._mostrar_estado("Eliminación cancelada.")
            return

        self.servicio.eliminar_producto(codigo)
        self.actualizar()
        self._limpiar_campos()
        self._mostrar_estado("Producto eliminado correctamente.")


class SeccionVentas(ttk.Frame):
    """Registro de ventas: elegir usuario y producto, pulsar el botón y ver la tabla.

    Flujo de eventos:
        clic en "Registrar venta" -> command= -> _registrar_venta (callback)
        -> RestauranteServicio.registrar_venta -> ventas.json -> tabla y mensaje.
    """

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio) -> None:
        super().__init__(master, padding=12)
        self.servicio: RestauranteServicio = servicio

        self.var_usuario: tk.StringVar = tk.StringVar()
        self.var_producto: tk.StringVar = tk.StringVar()
        self.var_cantidad: tk.StringVar = tk.StringVar(value="1")

        # Texto que ve la persona en el Combobox -> valor real (identificación / código).
        self._usuarios_por_texto: dict[str, str] = {}
        self._productos_por_texto: dict[str, str] = {}

        self.img_registrar: tk.PhotoImage | None = cargar_imagen("icono_registrar.png")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Registro de ventas", style="Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self._crear_formulario()
        self._crear_estado()
        self._crear_tabla()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_formulario(self) -> None:
        marco = ttk.LabelFrame(self, text="Nueva venta", padding=12)
        marco.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(1, weight=1)
        marco.columnconfigure(3, weight=1)

        ttk.Label(marco, text="Usuario:").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=5)
        self.cmb_usuario: ttk.Combobox = ttk.Combobox(
            marco, textvariable=self.var_usuario, state="readonly")
        self.cmb_usuario.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Producto:").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=5)
        self.cmb_producto: ttk.Combobox = ttk.Combobox(
            marco, textvariable=self.var_producto, state="readonly")
        self.cmb_producto.grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Cantidad:").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Spinbox(marco, textvariable=self.var_cantidad, from_=1, to=999, width=8).grid(
            row=1, column=1, sticky="w", padx=(0, 16), pady=5)

        # command= asocia el clic del botón con el callback _registrar_venta.
        kwargs_boton = {"image": self.img_registrar, "compound": "left"} \
            if self.img_registrar is not None else {}
        ttk.Button(marco, text="Registrar venta", command=self._registrar_venta,
                   style="Exito.TButton", **kwargs_boton).grid(
            row=2, column=0, columnspan=4, pady=(10, 0))

    def _crear_estado(self) -> None:
        self.lbl_estado: ttk.Label = ttk.Label(self, text="", foreground=COLOR_OK)
        self.lbl_estado.grid(row=2, column=0, sticky="w", pady=8)

    def _crear_tabla(self) -> None:
        marco = ttk.LabelFrame(self, text="Ventas registradas", padding=8)
        marco.grid(row=3, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = ("fecha", "usuario", "producto", "cantidad")
        self.tabla: ttk.Treeview = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = {"fecha": "Fecha", "usuario": "Usuario",
                       "producto": "Producto", "cantidad": "Cantidad"}
        anchos = {"fecha": 150, "usuario": 200, "producto": 240, "cantidad": 80}
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

    # ------------------------------------------------------------------
    # Utilidades de la vista
    # ------------------------------------------------------------------
    def _mostrar_estado(self, mensaje: str, error: bool = False) -> None:
        self.lbl_estado.configure(text=mensaje, foreground=COLOR_ERROR if error else COLOR_OK)

    def _cargar_selectores(self) -> None:
        """Llena los Combobox con los usuarios y productos que informa el servicio."""
        self._usuarios_por_texto = {
            f"{u.identificacion} - {u.nombre}": u.identificacion
            for u in self.servicio.listar_usuarios()}
        self._productos_por_texto = {
            f"{p.id_producto} - {p.nombre} (stock: {p.stock})": p.id_producto
            for p in self.servicio.listar_productos()}

        self.cmb_usuario.configure(values=list(self._usuarios_por_texto))
        self.cmb_producto.configure(values=list(self._productos_por_texto))

        # Si lo que estaba seleccionado ya no existe (o el stock cambió), se limpia.
        if self.var_usuario.get() not in self._usuarios_por_texto:
            self.var_usuario.set("")
        if self.var_producto.get() not in self._productos_por_texto:
            self.var_producto.set("")

    def _cargar_tabla(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for venta in self.servicio.listar_ventas():
            usuario = self.servicio.buscar_usuario(venta.usuario_id)
            producto = self.servicio.buscar_producto(venta.producto_codigo)
            self.tabla.insert("", "end", values=(
                venta.fecha or "Sin fecha",
                usuario.nombre if usuario else f"{venta.usuario_id} (eliminado)",
                producto.nombre if producto else f"{venta.producto_codigo} (eliminado)",
                venta.cantidad))
        # Muestra la venta más reciente al final de la lista.
        hijos = self.tabla.get_children()
        if hijos:
            self.tabla.see(hijos[-1])

    def actualizar(self) -> None:
        """Vuelve a cargar selectores y tabla con lo que informa el servicio."""
        self._cargar_selectores()
        self._cargar_tabla()

    # ------------------------------------------------------------------
    # Callback (command=): coordina la interfaz y delega en el servicio
    # ------------------------------------------------------------------
    def _registrar_venta(self) -> None:
        identificacion = self._usuarios_por_texto.get(self.var_usuario.get())
        codigo = self._productos_por_texto.get(self.var_producto.get())
        if identificacion is None:
            self._mostrar_estado("Seleccione un usuario.", error=True)
            return
        if codigo is None:
            self._mostrar_estado("Seleccione un producto.", error=True)
            return
        try:
            cantidad = int(self.var_cantidad.get().strip())
        except ValueError:
            self._mostrar_estado("La cantidad debe ser un número entero.", error=True)
            return

        # Las reglas de la venta (existencia, cantidad, stock) las valida el servicio.
        try:
            venta = self.servicio.registrar_venta(identificacion, codigo, cantidad)
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        self.actualizar()
        self.var_cantidad.set("1")
        self._mostrar_estado(
            f"Venta registrada: {venta.cantidad} x {self._nombre_producto(codigo)} "
            f"para {self._nombre_usuario(identificacion)}.")

    def _nombre_producto(self, codigo: str) -> str:
        producto = self.servicio.buscar_producto(codigo)
        return producto.nombre if producto else codigo

    def _nombre_usuario(self, identificacion: str) -> str:
        usuario = self.servicio.buscar_usuario(identificacion)
        return usuario.nombre if usuario else identificacion


class MainView(ttk.Frame):
    """Panel principal: encabezado, menú de navegación y zona de contenido."""

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio, usuario: Usuario,
                 al_cerrar_sesion: Callable[[], None]) -> None:
        super().__init__(master)
        self.servicio: RestauranteServicio = servicio
        self.usuario: Usuario = usuario
        self.al_cerrar_sesion: Callable[[], None] = al_cerrar_sesion

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Imágenes de assets/ (se guardan como atributos para que no se liberen).
        self.img_logo: tk.PhotoImage | None = cargar_imagen("logo.png")
        self.iconos: dict[str, tk.PhotoImage | None] = {
            nombre: cargar_imagen(f"icono_{nombre}.png")
            for nombre in ("productos", "usuarios", "ventas", "salir")}

        self._crear_encabezado()
        self._crear_menu()
        self._crear_contenido()
        self.mostrar_seccion("productos")

    def _crear_encabezado(self) -> None:
        encabezado = ttk.Frame(self, style="Encabezado.TFrame", padding=(16, 10))
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
        encabezado.columnconfigure(1, weight=1)

        if self.img_logo is not None:
            ttk.Label(encabezado, image=self.img_logo, style="Encabezado.TLabel").grid(
                row=0, column=0, padx=(0, 12))
        ttk.Label(encabezado, text="Panel principal del restaurante",
                  style="EncabezadoTitulo.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(encabezado, text=f"Sesión: {self.usuario.nombre} ({self.usuario.rol})",
                  style="Encabezado.TLabel").grid(row=0, column=2, padx=16)
        ttk.Button(encabezado, text="Cerrar sesión", command=self.al_cerrar_sesion,
                   **self._opciones_icono("salir")).grid(row=0, column=3)

    def _opciones_icono(self, nombre: str) -> dict:
        """Opciones de ttk.Button para mostrar un ícono a la izquierda del texto."""
        icono = self.iconos.get(nombre)
        return {"image": icono, "compound": "left"} if icono is not None else {}

    def _crear_menu(self) -> None:
        menu = ttk.LabelFrame(self, text="Menú", padding=10)
        menu.grid(row=1, column=0, sticky="ns", padx=(12, 6), pady=12)

        opciones = [("Productos", "productos"), ("Ventas", "ventas")]
        # La gestión de usuarios es administrativa: solo se ofrece en el menú
        # a quien inició sesión con rol Administrador.
        if self.usuario.es_administrador():
            opciones.insert(1, ("Usuarios", "usuarios"))
        for fila, (texto, clave) in enumerate(opciones):
            ttk.Button(menu, text=texto, width=20, command=lambda c=clave: self.mostrar_seccion(c),
                       **self._opciones_icono(clave)).grid(row=fila, column=0, pady=4)

    def _crear_contenido(self) -> None:
        contenido = ttk.Frame(self)
        contenido.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=12)
        contenido.columnconfigure(0, weight=1)
        contenido.rowconfigure(0, weight=1)

        self.secciones: dict[str, ttk.Frame] = {
            "productos": SeccionProductos(contenido, self.servicio),
            "ventas": SeccionVentas(contenido, self.servicio),
        }
        # Igual que en el menú, la sección de Usuarios solo se crea para un
        # Administrador: un Empleado o Cliente no cuenta con esa gestión.
        if self.usuario.es_administrador():
            self.secciones["usuarios"] = SeccionUsuarios(contenido, self.servicio, self.usuario)
        for seccion in self.secciones.values():
            seccion.grid(row=0, column=0, sticky="nsew")

    def mostrar_seccion(self, clave: str) -> None:
        # Segunda barrera (la primera es que el botón ni siquiera se crea):
        # nunca se abre Usuarios si la sesión activa no es de Administrador.
        seccion = self.secciones.get(clave)
        if seccion is None:
            return
        seccion.actualizar()
        seccion.tkraise()
