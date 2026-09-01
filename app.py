from flask import Flask, request, redirect, url_for, render_template
import libsql
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')

# ------------------------------------------------------------------
# Usamos UNA sola conexión reutilizada durante toda la vida del proceso,
# en vez de abrir y cerrar una conexión por cada request. Abrir/cerrar
# conexiones de libsql repetidamente dentro de Flask provoca un deadlock
# conocido en las librerías de Python de Turso:
# https://github.com/tursodatabase/libsql-client-py/issues/30
# ------------------------------------------------------------------
_db_connection = None


def _nueva_conexion():
    return libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)


def get_db():
    global _db_connection
    if _db_connection is None:
        _db_connection = _nueva_conexion()
    return _db_connection


def ejecutar(sql, params=()):
    """Ejecuta una consulta y, si la conexión se cayó (por inactividad u
    otro motivo), reconecta una vez y reintenta antes de fallar."""
    global _db_connection
    try:
        db = get_db()
        resultado = db.execute(sql, params)
        db.commit()
        return resultado
    except Exception:
        _db_connection = _nueva_conexion()
        resultado = _db_connection.execute(sql, params)
        _db_connection.commit()
        return resultado


def inicializar_db():
    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        print('AVISO: faltan TURSO_DATABASE_URL o TURSO_AUTH_TOKEN en las variables de entorno.')
        return
    try:
        ejecutar('''
            CREATE TABLE IF NOT EXISTS cartas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                fecha TEXT NOT NULL,
                creada_en TEXT NOT NULL
            )
        ''')
    except Exception as e:
        # No tumbamos el arranque del worker si Turso no responde a tiempo;
        # cada request intentará conectar de nuevo por su cuenta.
        print(f'AVISO: no se pudo inicializar la base de datos al arrancar: {e}')


inicializar_db()


@app.route('/')
def inicio():
    return redirect(url_for('ver_cartas'))


# ------------------------------------------------------------------
# Endpoint PRIVADO: aquí subes tú las cartas
# Compártelo solo contigo. Ej: http://tu-servidor/escribir
# ------------------------------------------------------------------
@app.route('/escribir', methods=['GET', 'POST'])
def escribir_carta():
    enviado = False
    error = None

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        contenido = request.form.get('contenido', '').strip()
        fecha_form = request.form.get('fecha', '').strip()

        if not contenido:
            error = 'Escribe algo antes de enviar la carta 💌'
        else:
            fecha = fecha_form if fecha_form else datetime.now().strftime('%Y-%m-%d')
            titulo_final = titulo if titulo else 'Sin título'
            creada_en = datetime.now().isoformat()

            try:
                ejecutar(
                    'INSERT INTO cartas (titulo, contenido, fecha, creada_en) VALUES (?, ?, ?, ?)',
                    (titulo_final, contenido, fecha, creada_en)
                )
                enviado = True
            except Exception as e:
                error = f'No se pudo guardar la carta, intenta de nuevo ({e})'

    return render_template('escribir.html', enviado=enviado, error=error)


# ------------------------------------------------------------------
# Endpoint PÚBLICO: aquí ella consulta la lista de cartas
# Compártele el link. Ej: http://tu-servidor/cartas
# ------------------------------------------------------------------
@app.route('/cartas')
def ver_cartas():
    columnas = ['id', 'titulo', 'contenido', 'fecha', 'creada_en']
    filas = ejecutar(
        'SELECT id, titulo, contenido, fecha, creada_en FROM cartas ORDER BY fecha DESC, id DESC'
    ).fetchall()
    cartas = [dict(zip(columnas, fila)) for fila in filas]
    return render_template('cartas.html', cartas=cartas)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)