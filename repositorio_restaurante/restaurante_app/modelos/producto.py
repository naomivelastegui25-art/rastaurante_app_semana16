class Producto:
    """Producto del restaurante con control de stock."""

    def __init__(self, id_producto: str, nombre: str, precio: float,
                 categoria: str, stock: int = 0) -> None:
        if not str(id_producto).strip():
            raise ValueError("El código del producto no puede estar vacío.")
        if not nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        self.id_producto: str = str(id_producto).strip()
        self.nombre: str = nombre.strip()
        self.precio: float = precio
        self.categoria: str = categoria.strip()
        self.stock: int = stock

    def actualizar(self, nombre: str, precio: float, categoria: str, stock: int) -> None:
        """Actualiza los datos del producto (el código no cambia).

        Reutiliza las validaciones del constructor: si algún dato es inválido
        se lanza ValueError y el producto no sufre ningún cambio.
        """
        validado = Producto(self.id_producto, nombre, precio, categoria, stock)
        self.nombre = validado.nombre
        self.precio = validado.precio
        self.categoria = validado.categoria
        self.stock = validado.stock

    def vender(self, cantidad: int) -> None:
        """Disminuye el stock. Nunca permite que quede negativo."""
        if cantidad <= 0:
            raise ValueError("La cantidad a vender debe ser mayor a cero.")
        if self.stock < cantidad:
            raise ValueError("Stock insuficiente para realizar la venta.")
        self.stock -= cantidad

    def convertir_a_diccionario(self) -> dict:
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio": self.precio,
            "categoria": self.categoria,
            "stock": self.stock,
        }
