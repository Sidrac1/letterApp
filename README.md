# Cartas 💌

App muy simple hecha con Flask para escribirle cartas a tu pareja.

## Cómo correrla

```bash
pip install -r requirements.txt
python app.py
```

Luego abre en el navegador:

- **Tú (subir cartas, privado):** `http://localhost:5000/escribir`
- **Ella (ver la lista de cartas):** `http://localhost:5000/cartas`

## Notas

- Las cartas se guardan en `cartas.json` (se crea automáticamente). No hay base de datos, así que es fácil de leer o respaldar.
- No hay login: `/escribir` no está protegido por contraseña. Si vas a exponer la app en internet (por ejemplo con ngrok o en un hosting), comparte solo el link de `/cartas` con ella, y mantén el de `/escribir` para ti. Si quieres, más adelante puedo agregarle una contraseña simple a `/escribir` sin complicar el resto.
- La carta más reciente aparece abierta automáticamente en la lista; las demás se expanden al hacer clic.
- Puedes poner una fecha manual al escribir la carta (por ejemplo, si quieres que aparezca fechada como un aniversario); si la dejas vacía, se usa la fecha de hoy.
