from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """Administra las colecciones y concentra las reglas de negocio del restaurante."""

    def __init__(self, archivo_servicio: ArchivoServicio | None = None) -> None:
        if archivo_servicio is None:
            archivo_servicio = ArchivoServicio()
        self.archivo_servicio: ArchivoServicio = archivo_servicio

        # --- Colecciones principales (almacenar, recorrer y persistir) ---
        self._productos: list[Producto] = self._cargar_productos()
        self._usuarios: list[Usuario] = self._cargar_usuarios()
        self._ventas: list[Venta] = self._cargar_ventas()

        # --- Índices auxiliares en memoria (búsquedas por clave) ---
        self._indice_usuarios: dict[str, Usuario] = {}
        self._indice_productos: dict[str, Producto] = {}
        self._ventas_por_usuario: dict[str, list[Venta]] = {}
        self._reconstruir_indices()

    # ------------------------------------------------------------------
    # Reconstrucción de objetos desde JSON
    # ------------------------------------------------------------------
    @staticmethod
    def _advertir_omitido(archivo: str, posicion: int, motivo: str) -> None:
        print(f"Advertencia: registro {posicion} de {archivo} omitido ({motivo}).")

    def _cargar_productos(self) -> list[Producto]:
        productos: list[Producto] = []
        codigos_vistos: set[str] = set()  # set: validar unicidad del código
        registros = self.archivo_servicio.cargar_productos()
        for posicion, registro in enumerate(registros, start=1):
            try:
                producto = Producto(
                    str(registro["id_producto"]),
                    registro["nombre"],
                    float(registro["precio"]),
                    registro["categoria"],
                    int(registro["stock"]),
                )
            except KeyError as error:
                self._advertir_omitido("productos.json", posicion, f"falta la clave {error}")
                continue
            except (ValueError, TypeError, AttributeError) as error:
                self._advertir_omitido("productos.json", posicion, f"dato inválido: {error}")
                continue

            if producto.id_producto in codigos_vistos:
                self._advertir_omitido("productos.json", posicion,
                                       f"código duplicado '{producto.id_producto}'")
                continue
            codigos_vistos.add(producto.id_producto)
            productos.append(producto)
        return productos

    def _cargar_usuarios(self) -> list[Usuario]:
        usuarios: list[Usuario] = []
        identificaciones_vistas: set[str] = set()  # set: validar unicidad
        registros = self.archivo_servicio.cargar_usuarios()
        for posicion, registro in enumerate(registros, start=1):
            try:
                usuario = Usuario(
                    str(registro["identificacion"]),
                    registro["nombre"],
                    registro["contrasena"],
                    registro.get("rol", "Cliente"),  # usuarios previos a la Semana 16
                )
            except KeyError as error:
                self._advertir_omitido("usuarios.json", posicion, f"falta la clave {error}")
                continue
            except (ValueError, TypeError, AttributeError) as error:
                self._advertir_omitido("usuarios.json", posicion, f"dato inválido: {error}")
                continue

            if usuario.identificacion in identificaciones_vistas:
                self._advertir_omitido("usuarios.json", posicion,
                                       f"identificación duplicada '{usuario.identificacion}'")
                continue
            identificaciones_vistas.add(usuario.identificacion)
            usuarios.append(usuario)
        return usuarios

    def _cargar_ventas(self) -> list[Venta]:
        ventas: list[Venta] = []
        registros = self.archivo_servicio.cargar_ventas()
        for posicion, registro in enumerate(registros, start=1):
            try:
                venta = Venta(
                    str(registro["usuario_id"]),
                    str(registro["producto_codigo"]),
                    int(registro["cantidad"]),
                    str(registro.get("fecha", "")),  # ventas antiguas: sin fecha
                )
            except KeyError as error:
                self._advertir_omitido("ventas.json", posicion, f"falta la clave {error}")
                continue
            except (ValueError, TypeError) as error:
                self._advertir_omitido("ventas.json", posicion, f"dato inválido: {error}")
                continue
            ventas.append(venta)
        return ventas

    # ------------------------------------------------------------------
    # Índices auxiliares
    # ------------------------------------------------------------------
    def _reconstruir_indices(self) -> None:
        """Arma los diccionarios auxiliares a partir de las listas principales.

        Se ejecuta al iniciar, con los objetos ya recuperados desde JSON.
        """
        self._indice_usuarios = {u.identificacion: u for u in self._usuarios}
        self._indice_productos = {p.id_producto: p for p in self._productos}

        self._ventas_por_usuario = {}
        for venta in self._ventas:
            self._ventas_por_usuario.setdefault(venta.usuario_id, []).append(venta)

    def indices_coherentes(self) -> bool:
        """Comprueba que cada índice represente exactamente lo que hay en su lista."""
        usuarios_ok = (
            len(self._indice_usuarios) == len(self._usuarios)
            and all(self._indice_usuarios.get(u.identificacion) is u for u in self._usuarios)
        )
        productos_ok = (
            len(self._indice_productos) == len(self._productos)
            and all(self._indice_productos.get(p.id_producto) is p for p in self._productos)
        )
        total_agrupadas = sum(len(v) for v in self._ventas_por_usuario.values())
        ventas_ok = (
            total_agrupadas == len(self._ventas)
            and all(v in self._ventas_por_usuario.get(v.usuario_id, []) for v in self._ventas)
        )
        return usuarios_ok and productos_ok and ventas_ok

    # ------------------------------------------------------------------
    # Acceso simulado
    # ------------------------------------------------------------------
    def validar_acceso(self, identificacion: str, contrasena: str) -> Usuario | None:
        """Devuelve el usuario si las credenciales son correctas; None si no lo son.

        Lanza ValueError si alguno de los campos está vacío.
        """
        if not identificacion.strip() or not contrasena:
            raise ValueError("Ingrese usuario y contraseña.")
        usuario = self.buscar_usuario(identificacion)
        if usuario is not None and usuario.contrasena == contrasena:
            return usuario
        return None

    # ------------------------------------------------------------------
    # Listados y búsquedas por clave (O(1) con los índices)
    # ------------------------------------------------------------------
    def listar_usuarios(self) -> list[Usuario]:
        return list(self._usuarios)  # copia: las vistas no modifican la colección

    def listar_productos(self) -> list[Producto]:
        return list(self._productos)

    def listar_ventas(self) -> list[Venta]:
        return list(self._ventas)

    def buscar_usuario(self, identificacion: str) -> Usuario | None:
        return self._indice_usuarios.get(identificacion.strip())

    def buscar_producto(self, codigo: str) -> Producto | None:
        return self._indice_productos.get(codigo.strip())

    def consultar_stock(self, codigo: str) -> int | None:
        producto = self.buscar_producto(codigo)
        return producto.stock if producto is not None else None

    # ------------------------------------------------------------------
    # Usuarios: registrar, consultar, actualizar y eliminar
    # ------------------------------------------------------------------
    def registrar_usuario(self, identificacion: str, nombre: str, contrasena: str,
                          rol: str = "Cliente") -> bool:
        """Devuelve False si ya existe. Lanza ValueError si los datos son inválidos."""
        nuevo_usuario = Usuario(identificacion, nombre, contrasena, rol)
        if self.buscar_usuario(nuevo_usuario.identificacion) is not None:
            return False
        self._usuarios.append(nuevo_usuario)
        self._indice_usuarios[nuevo_usuario.identificacion] = nuevo_usuario
        self.archivo_servicio.guardar_usuarios(self._usuarios)
        return True

    def actualizar_usuario(self, identificacion: str, nombre: str, contrasena: str,
                           rol: str) -> bool:
        """Devuelve False si el usuario no existe. Lanza ValueError si los datos son inválidos."""
        usuario = self.buscar_usuario(identificacion)
        if usuario is None:
            return False
        usuario.actualizar(nombre, contrasena, rol)
        self.archivo_servicio.guardar_usuarios(self._usuarios)
        return True

    def eliminar_usuario(self, identificacion: str) -> bool:
        """Devuelve False si el usuario no existe.

        No decide si la cuenta puede eliminarse por ser la sesión activa: eso
        depende de quién inició sesión, algo que conoce la interfaz, no esta
        capa de datos.
        """
        usuario = self.buscar_usuario(identificacion)
        if usuario is None:
            return False
        self._usuarios.remove(usuario)
        del self._indice_usuarios[usuario.identificacion]
        self.archivo_servicio.guardar_usuarios(self._usuarios)
        return True

    # ------------------------------------------------------------------
    # Productos: registrar, actualizar y eliminar
    # ------------------------------------------------------------------
    def registrar_producto(self, id_producto: str, nombre: str, precio: float,
                           categoria: str, stock: int) -> bool:
        """Devuelve False si ya existe. Lanza ValueError si los datos son inválidos."""
        nuevo_producto = Producto(id_producto, nombre, precio, categoria, stock)
        if self.buscar_producto(nuevo_producto.id_producto) is not None:
            return False
        self._productos.append(nuevo_producto)
        self._indice_productos[nuevo_producto.id_producto] = nuevo_producto
        self.archivo_servicio.guardar_productos(self._productos)
        return True

    def actualizar_producto(self, id_producto: str, nombre: str, precio: float,
                            categoria: str, stock: int) -> bool:
        """Devuelve False si el producto no existe. Lanza ValueError si los datos son inválidos."""
        producto = self.buscar_producto(id_producto)
        if producto is None:
            return False
        producto.actualizar(nombre, precio, categoria, stock)
        self.archivo_servicio.guardar_productos(self._productos)
        return True

    def eliminar_producto(self, id_producto: str) -> bool:
        """Devuelve False si el producto no existe."""
        producto = self.buscar_producto(id_producto)
        if producto is None:
            return False
        self._productos.remove(producto)
        del self._indice_productos[producto.id_producto]
        self.archivo_servicio.guardar_productos(self._productos)
        return True

    # ------------------------------------------------------------------
    # Ventas
    # ------------------------------------------------------------------
    def registrar_venta(self, identificacion_usuario: str, codigo_producto: str,
                        cantidad: int = 1) -> Venta:
        """Valida y registra una venta; es la operación que invoca la interfaz.

        Lanza ValueError con un mensaje claro si el usuario o el producto no
        existen, si la cantidad no es válida o si no hay stock suficiente. En
        ese caso no se modifica ningún dato ni ningún archivo.
        """
        usuario = self.buscar_usuario(identificacion_usuario)
        if usuario is None:
            raise ValueError("El usuario seleccionado no está registrado.")

        producto = self.buscar_producto(codigo_producto)
        if producto is None:
            raise ValueError("El producto seleccionado no existe.")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        if producto.stock < cantidad:
            raise ValueError(
                f"Stock insuficiente de '{producto.nombre}' (disponible: {producto.stock}).")

        venta = Venta(usuario.identificacion, producto.id_producto, cantidad)
        producto.vender(cantidad)
        self._ventas.append(venta)
        self._ventas_por_usuario.setdefault(venta.usuario_id, []).append(venta)

        # Persistencia: productos (stock actualizado) y ventas.
        self.archivo_servicio.guardar_productos(self._productos)
        self.archivo_servicio.guardar_ventas(self._ventas)
        return venta

    def vender_producto(self, codigo_producto: str, identificacion_usuario: str,
                        cantidad: int) -> bool:
        """Versión de consola (Semanas 11 y 12): delega en registrar_venta."""
        try:
            self.registrar_venta(identificacion_usuario, codigo_producto, cantidad)
        except ValueError as error:
            print(f"Error: {error}")
            return False
        return True

    def consultar_ventas_usuario(self, identificacion_usuario: str) -> list[Venta]:
        # Índice de ventas agrupadas por usuario: no recorre toda la colección.
        return list(self._ventas_por_usuario.get(identificacion_usuario.strip(), []))
