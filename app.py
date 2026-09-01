from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime
from dotenv import load_dotenv
import db

load_dotenv()

app = Flask(__name__)


def inicializar_db():
    try:
        db.ejecutar('''
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
                db.ejecutar(
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
    error = None
    cartas = []
    try:
        filas = db.ejecutar(
            'SELECT id, titulo, contenido, fecha, creada_en FROM cartas ORDER BY fecha DESC, id DESC'
        )
        cartas = [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        error = f'No se pudieron cargar las cartas en este momento ({e})'

    return render_template('cartas.html', cartas=cartas, error=error)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)