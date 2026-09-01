from flask import Flask, request, redirect, url_for, render_template, g
import libsql
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')


def get_db():
    if 'db' not in g:
        g.db = libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
    return g.db


@app.teardown_appcontext
def cerrar_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def inicializar_db():
    conn = libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cartas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha TEXT NOT NULL,
            creada_en TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


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

            db = get_db()
            db.execute(
                'INSERT INTO cartas (titulo, contenido, fecha, creada_en) VALUES (?, ?, ?, ?)',
                (titulo_final, contenido, fecha, creada_en)
            )
            db.commit()
            enviado = True

    return render_template('escribir.html', enviado=enviado, error=error)


# ------------------------------------------------------------------
# Endpoint PÚBLICO: aquí ella consulta la lista de cartas
# Compártele el link. Ej: http://tu-servidor/cartas
# ------------------------------------------------------------------
@app.route('/cartas')
def ver_cartas():
    db = get_db()
    columnas = ['id', 'titulo', 'contenido', 'fecha', 'creada_en']
    filas = db.execute(
        'SELECT id, titulo, contenido, fecha, creada_en FROM cartas ORDER BY fecha DESC, id DESC'
    ).fetchall()
    cartas = [dict(zip(columnas, fila)) for fila in filas]
    return render_template('cartas.html', cartas=cartas)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)