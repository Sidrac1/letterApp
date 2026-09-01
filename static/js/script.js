// ---------- Corazones flotantes de fondo ----------
function crearCorazonesFlotantes() {
    const contenedor = document.getElementById('corazones-flotantes');
    if (!contenedor) return;

    const simbolos = ['💗', '💕', '💖', '♡'];
    const cantidad = 14;

    for (let i = 0; i < cantidad; i++) {
        const corazon = document.createElement('span');
        corazon.classList.add('corazon-flotante');
        corazon.textContent = simbolos[Math.floor(Math.random() * simbolos.length)];

        const left = Math.random() * 100;
        const duracion = 10 + Math.random() * 12;
        const retraso = Math.random() * 10;
        const tamano = 0.9 + Math.random() * 1.3;

        corazon.style.left = left + 'vw';
        corazon.style.animationDuration = duracion + 's';
        corazon.style.animationDelay = retraso + 's';
        corazon.style.fontSize = tamano + 'rem';

        contenedor.appendChild(corazon);
    }
}

// ---------- Acordeón de cartas ----------
function activarAcordeonCartas() {
    const tarjetas = document.querySelectorAll('.tarjeta-carta');

    tarjetas.forEach((tarjeta) => {
        const encabezado = tarjeta.querySelector('.encabezado-carta');
        if (!encabezado) return;

        encabezado.addEventListener('click', () => {
            tarjeta.classList.toggle('abierta');
        });
    });

    // Abre automáticamente la carta más reciente (la primera de la lista)
    if (tarjetas.length > 0) {
        tarjetas[0].classList.add('abierta');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    crearCorazonesFlotantes();
    activarAcordeonCartas();
});
