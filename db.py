"""
Conexión a Turso usando su API HTTP (Hrana over HTTP) en vez de los
bindings nativos de libsql. Esto evita un bug conocido y sin resolver
en las librerías de Python de Turso, que provoca deadlocks de hilos
dentro de apps Flask/gunicorn:
https://github.com/tursodatabase/libsql-client-py/issues/30

Al usar HTTP puro con `requests`, además le podemos poner un timeout
explícito a cada consulta: si algo falla, falla rápido y con un error
claro, en vez de colgar el worker hasta que gunicorn lo mate.
"""
import os
import requests

TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN', '')

TIMEOUT_SEGUNDOS = 10


def _url_pipeline():
    url = TURSO_DATABASE_URL.strip()
    if url.startswith('libsql://'):
        url = 'https://' + url[len('libsql://'):]
    return url.rstrip('/') + '/v2/pipeline'


def _valor_a_arg(valor):
    if valor is None:
        return {'type': 'null'}
    if isinstance(valor, bool):
        return {'type': 'integer', 'value': str(int(valor))}
    if isinstance(valor, int):
        return {'type': 'integer', 'value': str(valor)}
    if isinstance(valor, float):
        return {'type': 'float', 'value': valor}
    return {'type': 'text', 'value': str(valor)}


def _celda_a_python(celda):
    tipo = celda.get('type')
    valor = celda.get('value')
    if tipo == 'null' or valor is None:
        return None
    if tipo == 'integer':
        return int(valor)
    if tipo == 'float':
        return float(valor)
    return valor


def ejecutar(sql, params=()):
    """Ejecuta una sentencia SQL contra Turso vía HTTP.
    Devuelve una lista de filas (cada fila, una lista de valores en Python)."""
    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        raise RuntimeError('Faltan TURSO_DATABASE_URL o TURSO_AUTH_TOKEN en las variables de entorno.')

    payload = {
        'requests': [
            {
                'type': 'execute',
                'stmt': {
                    'sql': sql,
                    'args': [_valor_a_arg(p) for p in params]
                }
            },
            {'type': 'close'}
        ]
    }
    headers = {
        'Authorization': f'Bearer {TURSO_AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }

    respuesta = requests.post(
        _url_pipeline(), json=payload, headers=headers, timeout=TIMEOUT_SEGUNDOS
    )
    respuesta.raise_for_status()
    datos = respuesta.json()

    primer_resultado = datos['results'][0]
    if primer_resultado['type'] == 'error':
        mensaje = primer_resultado.get('error', {}).get('message', 'Error en la consulta a Turso')
        raise RuntimeError(mensaje)

    resultado = primer_resultado['response']['result']
    filas = [
        [_celda_a_python(celda) for celda in fila]
        for fila in resultado.get('rows', [])
    ]
    return filas