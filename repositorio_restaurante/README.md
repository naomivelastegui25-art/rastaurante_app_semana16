# Restaurante App

Aplicación en Python para la gestión de un restaurante: usuarios, productos, ventas y control de stock, con persistencia en archivos JSON. El proyecto **evoluciona semana a semana**: cada semana incorpora nuevos requisitos sobre la misma base, sin reemplazarla.

## Estructura del repositorio

```
.
├── restaurante_app/
│   ├── assets/            (logo e íconos de la interfaz)
│   │   ├── logo.png
│   │   ├── logo_grande.png
│   │   └── icono_*.png
│   ├── datos/
│   │   ├── productos.json
│   │   ├── usuarios.json
│   │   └── ventas.json
│   ├── modelos/
│   │   ├── __init__.py
│   │   ├── producto.py
│   │   ├── usuario.py
│   │   └── venta.py
│   ├── servicios/
│   │   ├── __init__.py
│   │   ├── archivo_servicio.py
│   │   └── restaurante_servicio.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── login_view.py
│   │   ├── main_view.py
│   │   └── recursos.py
│   ├── main.py            (aplicación gráfica con Tkinter)
│   └── main_consola.py    (versión de consola de las Semanas 11 y 12)
└── README.md
```

| Capa | Responsabilidad |
|---|---|
| `assets/` | Logo e íconos PNG usados por la interfaz. |
| `datos/` | Solo almacena los archivos JSON. |
| `modelos/` | `Producto` (con stock), `Usuario` (con `rol`: Administrador, Empleado o Cliente) y `Venta` (usuario, producto, cantidad y fecha), con sus validaciones. |
| `servicios/archivo_servicio.py` | Lee y escribe los tres archivos JSON. |
| `servicios/restaurante_servicio.py` | `RestauranteServicio`: colecciones, índices, acceso, ventas y reglas de negocio. |
| `ui/` | Vistas de Tkinter (`recursos.py` carga las imágenes de `assets/`). Piden todo al servicio y no leen archivos JSON. |
| `main.py` | Crea la única ventana, prepara el servicio y controla el cambio entre vistas. |

## Ejecución

Requiere Python 3.10 o superior (Tkinter viene incluido con el instalador oficial de Python para Windows).

```
cd restaurante_app
python main.py            # aplicación gráfica
python main_consola.py    # versión de consola
```

**Acceso de prueba:** usuario `admin`, contraseña `admin123` (también `001` / `1234`).

## Evolución por semanas

### Semana 11: ventas, stock y persistencia
- Nueva clase `Venta`, que relaciona un usuario con un producto vendido.
- `vender_producto()`: valida que el usuario y el producto existan, que la cantidad sea mayor que cero y que haya stock suficiente. Si algo falla, no se modifica ningún dato.
- El stock nunca puede quedar negativo.
- Persistencia JSON de productos, usuarios y ventas, y reconstrucción de objetos al iniciar.

### Semana 12: colecciones para búsquedas más eficientes
Las listas `_productos`, `_usuarios` y `_ventas` se mantienen como colecciones principales (almacenar, recorrer y persistir). Se agregaron estructuras auxiliares:

| Colección | Clave → valor | Mejora |
|---|---|---|
| `dict` `_indice_usuarios` | identificación → `Usuario` | `buscar_usuario` deja de recorrer la lista. |
| `dict` `_indice_productos` | código → `Producto` | `buscar_producto` deja de recorrer la lista. |
| `dict` `_ventas_por_usuario` | identificación → lista de `Venta` | `consultar_ventas_usuario` no recorre todas las ventas. |
| `set` (al cargar JSON) | códigos / identificaciones ya vistos | Detecta duplicados con una comprobación de pertenencia. |

Los índices se **reconstruyen al iniciar** a partir de lo recuperado desde JSON y se **actualizan** al registrar, eliminar o vender. El método `indices_coherentes()` comprueba que cada índice coincida con su lista.

### Semana 13: base gráfica con Tkinter
- Carpeta `ui/` con `LoginView` y `MainView`; `main.py` mantiene una única ventana y un único ciclo de ejecución.
- Flujo: login → panel principal → cerrar sesión → login, todo en la misma ventana.
- `Usuario` incorpora `contrasena` para simular el acceso. `RestauranteServicio.validar_acceso()` valida las credenciales.
- Campos vacíos o credenciales incorrectas muestran un mensaje en la pantalla de acceso.
- El panel principal permite ver Productos y Usuarios; Ventas quedó como funcionalidad pendiente (se completó en la Semana 15).
- El servicio se renombró a `restaurante_servicio.py` (`RestauranteServicio`).

### Semana 14: componentes y contenedores
- Interfaz reorganizada con contenedores (`Frame`, `LabelFrame`) y los gestores `grid` y `pack`: encabezado, menú lateral y zona de contenido.
- Sección **Productos**: formulario (`Entry`, `Combobox`, `Spinbox`), botones con `command=` y tabla `Treeview` con barra de desplazamiento.
- Operaciones desde la interfaz: **Registrar**, **Consultar** (carga el producto al formulario por su código), **Actualizar** y **Eliminar** (con confirmación).
- Las validaciones y reglas de negocio están en el modelo y en `RestauranteServicio`; los botones solo coordinan.
- Después de cada operación se recarga la tabla y se muestra un mensaje de éxito o error.
- Sección **Usuarios**: consulta en tabla (no muestra contraseñas).

### Semana 15: eventos y callbacks (sección Ventas)
Se evolucionó el mismo proyecto sin reconstruirlo: login, navegación, gestión de productos y consulta de usuarios se conservan.

**Flujo de eventos de la venta**

```
Usuario elige usuario + producto y pulsa "Registrar venta"
        ↓
Botón ttk.Button(command=self._registrar_venta)
        ↓
Callback SeccionVentas._registrar_venta   (lee la interfaz, no tiene reglas de negocio)
        ↓
RestauranteServicio.registrar_venta       (valida y aplica la venta)
        ↓
Persistencia: ventas.json y productos.json (stock)
        ↓
Respuesta: tabla de ventas actualizada + mensaje de éxito o error
```

**Cambios**
- **Modelo `Venta`:** incorpora `fecha` (fecha y hora de la operación, generada al crear la venta). Las ventas guardadas sin fecha se siguen leyendo y se muestran como "Sin fecha".
- **`RestauranteServicio.registrar_venta(usuario, producto, cantidad)`:** valida que el usuario y el producto existan, que la cantidad sea mayor que cero y que haya stock suficiente; guarda en `ventas.json` y descuenta el stock. Ante un error lanza `ValueError` con el mensaje y no modifica nada. Se agregó `listar_ventas()`. `vender_producto()` (consola) ahora delega en `registrar_venta`.
- **Sección Ventas (`ui/main_view.py`):** dos `Combobox` de solo lectura (usuario y producto registrados), un `Spinbox` de cantidad, el botón **Registrar venta** y una tabla `Treeview` con fecha, usuario, producto y cantidad. La tabla y los selectores se recargan tras cada venta, y un mensaje indica el resultado.
- **Recursos visuales (`assets/`):** logo en el encabezado, en la pantalla de acceso y como ícono de la ventana; íconos en el menú lateral, en "Cerrar sesión" y en "Registrar venta". Si una imagen falta, la aplicación continúa sin ella.
- El menú ya no muestra "Ventas (pendiente)".

**Comprobación realizada:** venta válida (se guarda con fecha, baja el stock y aparece en la tabla); rechazo de usuario o producto no seleccionado, cantidad no numérica, cero o negativa y stock insuficiente, sin cambiar los archivos; las ventas se recuperan al cerrar y volver a ejecutar; no quedan referencias a libros o biblioteca.

### Semana 16: eventos sobre tabla y formulario (gestión de Usuarios)
Se conservan el login, la navegación, Productos y Ventas. La sección de Usuarios dejó de ser solo de consulta y ahora permite registrar, consultar, actualizar y eliminar, con acceso restringido por rol.

**Eventos que coordina la interfaz (`SeccionUsuarios`, en `ui/main_view.py`)**

```
TREEVIEW                    TECLADO              TECLADO               COMBOBOX                 BOTONES
<<TreeviewSelect>>           <Return>             <Escape>              <<ComboboxSelected>>      command=
     ↓                          ↓                    ↓                        ↓                      ↓
   bind()                     bind()               bind()                  bind()                 callback
     ↓                          ↓                    ↓                        ↓                      ↓
 _al_seleccionar_fila   _al_presionar_enter   _al_presionar_escape    _al_cambiar_rol      _registrar / _actualizar
     ↓                          ↓                    ↓                        ↓              _eliminar / _limpiar_formulario
 carga el usuario          reutiliza               reutiliza            muestra una                  ↓
 en el formulario          _registrar          _limpiar_formulario    descripción del rol    RestauranteServicio
```

**Cambios**
- **Modelo `Usuario`:** nuevo atributo `rol` (`Administrador`, `Empleado` o `Cliente`, en `Usuario.ROLES`), validado en el constructor. Se agregó `actualizar()`, con el mismo patrón que `Producto.actualizar()`. Los registros guardados antes de esta semana (sin `rol`) se cargan como `Cliente` por defecto.
- **`RestauranteServicio`:** `registrar_usuario(..., rol)` ahora recibe el rol; se agregaron `actualizar_usuario()` y `eliminar_usuario()`. Las tres operaciones validan, persisten en `usuarios.json` y devuelven `False` si el usuario no existe o ya existe, sin modificar nada en ese caso.
- **Sección Usuarios:**
  - Formulario con identificación, nombre, contraseña y un `Combobox` de rol; botones **Registrar**, **Actualizar**, **Eliminar** y **Limpiar** con `command=`.
  - Tabla `Treeview` con identificación, nombre y rol. Al seleccionar una fila (`<<TreeviewSelect>>` + `bind()`) se toma solo el identificador de la fila y se pide el resto de los datos a `RestauranteServicio`; la tabla nunca se lee como fuente de datos.
  - `<Return>` en los campos del formulario reutiliza `_registrar()` (no repite su lógica); `<Escape>` reutiliza `_limpiar_formulario()` y además quita la selección de la tabla.
  - El `Combobox` de rol responde a `<<ComboboxSelected>>` mostrando una breve descripción del rol elegido (sin reglas de negocio en la interfaz).
  - **Eliminar** pide confirmación con un diálogo y, además, la interfaz impide eliminar la cuenta con la que se inició sesión, comparando contra el usuario autenticado antes de llamar al servicio.
- **Acceso por rol:** el botón y la sección "Usuarios" solo se crean en `MainView` cuando quien inició sesión es `Administrador`; un Empleado o Cliente no los ve. `mostrar_seccion()` agrega una segunda verificación por si se intentara abrir la sección igualmente.
- **`datos/usuarios.json`:** cada registro ahora incluye `rol` (`admin` → Administrador). Se agregó un usuario de prueba `002 / Carlos Perez / 1234 / Empleado` para poder verificar el acceso restringido sin tener que registrarlo primero.
- **`assets/`:** se reutilizan el logo y los íconos ya incorporados en la Semana 15; el encabezado ahora muestra también el rol de la sesión activa ("Sesión: Administrador (Administrador)").

**Comprobación realizada:** registrar, consultar (vía selección), actualizar y eliminar un usuario; selección de fila carga el formulario; `Return` registra y `Escape` limpia formulario y selección; cambiar el rol en el combobox actualiza el mensaje informativo; no se puede eliminar la cuenta con sesión activa; un Empleado y un Cliente no ven la opción Usuarios en el menú; los usuarios se recuperan correctamente al reiniciar la aplicación.

## Manejo de excepciones

| Excepción | Comportamiento |
|---|---|
| `FileNotFoundError` | El programa inicia con una colección vacía. |
| `json.JSONDecodeError` | Advertencia y colección vacía. |
| `PermissionError` | Mensaje de error de permisos al leer o escribir. |
| `KeyError` | El registro al que le falta una clave se omite con una advertencia. |
| `ValueError` | Validaciones de `Producto`, `Usuario` y `Venta`. La interfaz muestra el mensaje. |

## Pruebas realizadas

- **Ventas y stock:** venta válida (el stock disminuye y se guarda en `ventas.json` y `productos.json`); rechazo de cantidad cero o negativa, stock insuficiente, usuario o producto inexistente, sin alterar los archivos.
- **Consultas:** búsqueda de producto por código, de usuario por identificación y ventas de un usuario.
- **Índices:** coherentes con las listas después de registrar, actualizar, eliminar y vender; reconstruidos al cerrar y volver a ejecutar.
- **Interfaz (Semanas 13 y 14):** login con campos vacíos, credenciales incorrectas y válidas; navegación entre secciones; registrar, consultar, actualizar y eliminar productos; cerrar sesión y volver al login; cambios conservados tras reiniciar.
- **Archivos dañados:** JSON inválido, archivo inexistente, registros sin clave y códigos duplicados.

## Notas
- El acceso es una **simulación** para fines del curso: las contraseñas se guardan en texto plano en `usuarios.json`.
- Eliminar un producto no borra las ventas ya registradas; en la consola esas ventas se muestran como "Producto desconocido".
