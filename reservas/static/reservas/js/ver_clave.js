// Botón "Mostrar / Ocultar" de los campos de contraseña
document.querySelectorAll('[data-ver-clave]').forEach(function (boton) {
    boton.addEventListener('click', function () {
        const campo = document.getElementById(boton.dataset.verClave);
        const oculto = campo.type === 'password';
        campo.type = oculto ? 'text' : 'password';
        boton.textContent = oculto ? 'Ocultar' : 'Mostrar';
        boton.setAttribute('aria-label', oculto ? 'Ocultar contraseña' : 'Mostrar contraseña');
    });
});
