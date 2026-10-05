"""Versión de consola (Semanas 11 y 12). Conserva el registro de usuarios,
productos, ventas y la consulta de ventas por usuario."""
from servicios.restaurante_servicio import RestauranteServicio


def mostrar_menu() -> str:
    print("\n--- SISTEMA DE RESTAURANTE (CONSOLA) ---")
    print("1. Registrar Usuario")
    print("2. Registrar Producto")
    print("3. Realizar Venta")
    print("4. Consultar Ventas por Usuario")
    print("5. Salir")
    return input("Seleccione una opción: ").strip()


def registrar_usuario(servicio: RestauranteServicio) -> None:
    print("\n--- REGISTRAR USUARIO ---")
    identificacion = input("Ingrese identificación: ")
    nombre = input("Ingrese nombre: ")
    contrasena = input("Ingrese contraseña: ")
    try:
        if servicio.registrar_usuario(identificacion, nombre, contrasena):
            print("Usuario registrado exitosamente.")
        else:
            print("Error: El usuario ya se encuentra registrado.")
    except ValueError as error:
        print(f"Error: {error}")


def registrar_producto(servicio: RestauranteServicio) -> None:
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = input("Ingrese código del producto: ")
    nombre = input("Ingrese nombre del producto: ")
    precio_texto = input("Ingrese precio: ")
    categoria = input("Ingrese categoría: ")
    stock_texto = input("Ingrese stock inicial: ")

    try:
        precio = float(precio_texto)
        stock = int(stock_texto)
    except ValueError:
        print("Error: El precio debe ser un decimal y el stock un entero.")
        return

    try:
        if servicio.registrar_producto(codigo, nombre, precio, categoria, stock):
            print("Producto registrado exitosamente.")
        else:
            print("Error: El producto ya se encuentra registrado.")
    except ValueError as error:
        print(f"Error: {error}")


def realizar_venta(servicio: RestauranteServicio) -> None:
    print("\n--- REALIZAR VENTA ---")
    identificacion = input("Ingrese identificación del usuario: ")
    codigo_producto = input("Ingrese código del producto: ")
    try:
        cantidad = int(input("Ingrese la cantidad a comprar: "))
    except ValueError:
        print("Error: La cantidad debe ser un valor numérico entero.")
        return

    if servicio.vender_producto(codigo_producto, identificacion, cantidad):
        print("Venta procesada y registrada correctamente.")
    else:
        print("La operación fue rechazada. No se modificó ningún dato.")


def consultar_ventas(servicio: RestauranteServicio) -> None:
    print("\n--- CONSULTAR VENTAS POR USUARIO ---")
    identificacion = input("Ingrese identificación del usuario: ")
    ventas = servicio.consultar_ventas_usuario(identificacion)

    if not ventas:
        print("No se encontraron ventas asociadas a esta identificación.")
        return

    print(f"\n--- Historial de Ventas (Usuario: {identificacion.strip()}) ---")
    for venta in ventas:
        producto = servicio.buscar_producto(venta.producto_codigo)
        nombre = producto.nombre if producto else "Producto desconocido"
        print(f"* Cód: {venta.producto_codigo} | Producto: {nombre} | Cantidad: {venta.cantidad}")


def main() -> None:
    servicio = RestauranteServicio()

    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            registrar_usuario(servicio)
        elif opcion == "2":
            registrar_producto(servicio)
        elif opcion == "3":
            realizar_venta(servicio)
        elif opcion == "4":
            consultar_ventas(servicio)
        elif opcion == "5":
            print("Cerrando el sistema. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    main()
