from flask import Flask, request, redirect, url_for, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'cartas.json')


def cargar_cartas():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def guardar_cartas(cartas):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(cartas, f, ensure_ascii=False, indent=2)


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

            cartas = cargar_cartas()
            nuevo_id = 1 if not cartas else max(c['id'] for c in cartas) + 1
            nueva_carta = {
                'id': nuevo_id,
                'titulo': titulo if titulo else 'Sin título',
                'contenido': contenido,
                'fecha': fecha,
                'creada_en': datetime.now().isoformat()
            }
            cartas.append(nueva_carta)
            guardar_cartas(cartas)
            enviado = True

    return render_template('escribir.html', enviado=enviado, error=error)


# ------------------------------------------------------------------
# Endpoint PÚBLICO: aquí ella consulta la lista de cartas
# Compártele el link. Ej: http://tu-servidor/cartas
# ------------------------------------------------------------------
@app.route('/cartas')
def ver_cartas():
    cartas = cargar_cartas()
    cartas_ordenadas = sorted(cartas, key=lambda c: c['fecha'], reverse=True)
    return render_template('cartas.html', cartas=cartas_ordenadas)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
