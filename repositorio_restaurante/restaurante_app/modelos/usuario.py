class Usuario:
    """Persona registrada. Puede comprar y acceder a la aplicación (acceso simulado)."""

    ROLES: tuple[str, ...] = ("Administrador", "Empleado", "Cliente")

    def __init__(self, identificacion: str, nombre: str, contrasena: str,
                 rol: str = "Cliente") -> None:
        if not str(identificacion).strip():
            raise ValueError("La identificación no puede estar vacía.")
        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not contrasena:
            raise ValueError("La contraseña no puede estar vacía.")
        rol = rol.strip() if isinstance(rol, str) else rol
        if rol not in self.ROLES:
            raise ValueError(f"El rol debe ser uno de: {', '.join(self.ROLES)}.")

        self.identificacion: str = str(identificacion).strip()
        self.nombre: str = nombre.strip()
        self.contrasena: str = contrasena
        self.rol: str = rol

    def actualizar(self, nombre: str, contrasena: str, rol: str) -> None:
        """Actualiza los datos del usuario (la identificación no cambia).

        Reutiliza las validaciones del constructor: si algún dato es inválido
        se lanza ValueError y el usuario no sufre ningún cambio.
        """
        validado = Usuario(self.identificacion, nombre, contrasena, rol)
        self.nombre = validado.nombre
        self.contrasena = validado.contrasena
        self.rol = validado.rol

    def es_administrador(self) -> bool:
        return self.rol == "Administrador"

    def convertir_a_diccionario(self) -> dict:
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "contrasena": self.contrasena,
            "rol": self.rol,
        }
