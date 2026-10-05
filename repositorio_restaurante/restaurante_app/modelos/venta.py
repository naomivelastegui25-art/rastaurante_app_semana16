from datetime import datetime

FORMATO_FECHA: str = "%Y-%m-%d %H:%M:%S"


class Venta:
    """Relación entre un usuario, un producto vendido y la fecha de la operación."""

    def __init__(self, usuario_id: str, producto_codigo: str, cantidad: int,
                 fecha: str | None = None) -> None:
        if not str(usuario_id).strip():
            raise ValueError("La venta debe tener un usuario asociado.")
        if not str(producto_codigo).strip():
            raise ValueError("La venta debe tener un producto asociado.")
        if cantidad <= 0:
            raise ValueError("La cantidad vendida debe ser mayor a cero.")

        self.usuario_id: str = str(usuario_id).strip()
        self.producto_codigo: str = str(producto_codigo).strip()
        self.cantidad: int = cantidad
        # Si no se indica (venta nueva) se toma la fecha y hora actuales.
        # Las ventas guardadas antes de la Semana 15 no tienen fecha.
        if fecha is None:
            fecha = datetime.now().strftime(FORMATO_FECHA)
        self.fecha: str = str(fecha).strip()

    def convertir_a_diccionario(self) -> dict:
        return {
            "usuario_id": self.usuario_id,
            "producto_codigo": self.producto_codigo,
            "cantidad": self.cantidad,
            "fecha": self.fecha,
        }
