# Cartas 💌

App muy simple hecha con Flask para escribirle cartas a tu pareja.

## Base de datos: Turso

La app usa **Turso** (SQLite en la nube, capa gratuita sin fecha de expiración)
a través del SDK oficial `libsql`, que sigue la misma interfaz que el módulo
`sqlite3` de Python.

### 1. Crear la base de datos

```bash
curl -sSfL https://get.tur.so/install.sh | bash   # instala el CLI
turso auth login                                   # inicia sesión
turso db create cartas-db                           # crea la base de datos
turso db show cartas-db --url                        # copia esta URL
turso db tokens create cartas-db                      # copia este token
```

### 2. Configurar credenciales

Copia `.env.example` a `.env` y pega ahí la URL y el token que obtuviste:

```
TURSO_DATABASE_URL=libsql://tu-base-de-datos.turso.io
TURSO_AUTH_TOKEN=tu-token-aqui
```

El archivo `.env` **no debe subirse a GitHub** (ya está en `.gitignore`).

### 3. Instalar dependencias y correr en local

```bash
pip install -r requirements.txt
python app.py
```

Luego abre en el navegador:

- **Tú (subir cartas, privado):** `http://localhost:5000/escribir`
- **Ella (ver la lista de cartas):** `http://localhost:5000/cartas`

## Desplegar en Render (gratis)

1. Sube el código a GitHub y conecta el repo en Render.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn app:app`
4. En la sección **Environment** del servicio, agrega las mismas variables de
   `.env`: `TURSO_DATABASE_URL` y `TURSO_AUTH_TOKEN`.

Como los datos viven en Turso (no en el disco de Render), no necesitas un
Disk pagado — las cartas se conservan aunque el servicio se reinicie o se
redeploye, incluso en el plan gratuito de Render.

## Desplegar en PythonAnywhere

1. Sube el código y en la pestaña **Web** crea una app con "Manual configuration".
2. En el archivo WSGI:
   ```python
   import sys
   path = '/home/tu_usuario/cartas-app'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```
3. Pon la ruta de tu carpeta en **Source code** y **Working directory**.
4. En la pestaña **Files**, sube tu `.env` con las credenciales de Turso
   (o configúralas como variables de entorno del sistema, según prefieras).
5. Dale **Reload**.

## Notas

- No hay login: `/escribir` no está protegido por contraseña. Comparte solo el
  link de `/cartas` con ella, y mantén el de `/escribir` para ti. Si quieres,
  más adelante puedo agregarle una contraseña simple sin complicar el resto.
- La carta más reciente aparece abierta automáticamente en la lista; las demás
  se expanden al hacer clic.
- Puedes poner una fecha manual al escribir la carta (por ejemplo, si quieres
  que aparezca fechada como un aniversario); si la dejas vacía, se usa la
  fecha de hoy.