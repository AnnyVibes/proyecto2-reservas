// Reserva paso a paso: mes con días disponibles -> horarios libres del día -> Confirmar -> pago
document.addEventListener('DOMContentLoaded', function () {
    const datos = JSON.parse(document.getElementById('datos-reserva').textContent);
    const recurso = datos.recurso;
    const precioHora = parseFloat(datos.precio_hora);

    const dos = n => String(n).padStart(2, '0');
    const fechaDia = d => `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
    const hora = d => `${dos(d.getHours())}:${dos(d.getMinutes())}`;

    // Fecha en ISO con la zona horaria del navegador, p. ej. 2026-11-05T09:00:00-05:00
    function fechaISO(d) {
        const offset = -d.getTimezoneOffset();
        const signo = offset >= 0 ? '+' : '-';
        const abs = Math.abs(offset);
        return `${fechaDia(d)}T${hora(d)}:00${signo}${dos(Math.floor(abs / 60))}:${dos(abs % 60)}`;
    }

    function getCookie(nombre) {
        const cookie = document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith(nombre + '='));
        return cookie ? decodeURIComponent(cookie.slice(nombre.length + 1)) : null;
    }

    function textoFecha(d) {
        return d.toLocaleDateString('es', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    }

    // ---------- Paso 1: calendario del mes ----------
    const hoy = new Date(); hoy.setHours(0, 0, 0, 0);
    const primerMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    let mesVisible = new Date(primerMes);
    let diaElegido = null;
    let estadoPorDia = {};

    const contDias = document.getElementById('dias');
    const tituloMes = document.getElementById('titulo-mes');
    const btnAnterior = document.getElementById('mes-anterior');
    const errorCarga = document.getElementById('error-carga');
    const selector = document.getElementById('selector');
    const panelHoras = document.getElementById('panel-horas');

    function cargarMes() {
        const inicio = new Date(mesVisible);
        const fin = new Date(mesVisible.getFullYear(), mesVisible.getMonth() + 1, 1);
        tituloMes.textContent = mesVisible.toLocaleDateString('es', { month: 'long', year: 'numeric' });
        btnAnterior.disabled = mesVisible <= primerMes;
        errorCarga.classList.add('hidden');
        fetch(`/api/disponibilidad/${recurso}/?start=${fechaDia(inicio)}&end=${fechaDia(fin)}`)
            .then(r => r.ok ? r.json() : Promise.reject(r.status))
            .then(dias => {
                estadoPorDia = {};
                dias.forEach(d => { estadoPorDia[d.fecha] = d; });
                pintarMes();
            })
            .catch(() => { estadoPorDia = {}; pintarMes(); errorCarga.classList.remove('hidden'); });
    }

    function pintarMes() {
        contDias.innerHTML = '';
        const anio = mesVisible.getFullYear(), mes = mesVisible.getMonth();
        const huecos = (new Date(anio, mes, 1).getDay() + 6) % 7;   // la semana empieza en lunes
        for (let i = 0; i < huecos; i++) { contDias.appendChild(document.createElement('span')); }
        const total = new Date(anio, mes + 1, 0).getDate();
        for (let n = 1; n <= total; n++) {
            const fecha = new Date(anio, mes, n);
            const clave = fechaDia(fecha);
            const estado = estadoPorDia[clave];
            const disponible = !!estado && (estado.estado === 'libre' || estado.estado === 'parcial');
            const boton = document.createElement('button');
            boton.type = 'button';
            boton.className = 'dia';
            boton.textContent = n;
            boton.dataset.fecha = clave;
            if (fecha.getTime() === hoy.getTime()) { boton.classList.add('hoy'); }
            if (disponible) {
                boton.classList.add('disponible');
                boton.title = `${estado.libres} horario${estado.libres === 1 ? '' : 's'} libre${estado.libres === 1 ? '' : 's'}`;
                boton.addEventListener('click', () => elegirDia(fecha));
            } else {
                boton.disabled = true;
                boton.setAttribute('aria-disabled', 'true');
            }
            if (diaElegido && clave === fechaDia(diaElegido)) { boton.classList.add('seleccionado'); }
            contDias.appendChild(boton);
        }
    }

    btnAnterior.addEventListener('click', () => { mesVisible.setMonth(mesVisible.getMonth() - 1); cargarMes(); });
    document.getElementById('mes-siguiente').addEventListener('click', () => { mesVisible.setMonth(mesVisible.getMonth() + 1); cargarMes(); });

    // ---------- Paso 2: horarios libres del día ----------
    const listaHoras = document.getElementById('lista-horas');

    function elegirDia(fecha) {
        diaElegido = fecha;
        pintarMes();
        selector.classList.add('con-horas');
        panelHoras.classList.remove('hidden');
        const t = textoFecha(fecha);
        document.getElementById('fecha-elegida').textContent = t;
        listaHoras.innerHTML = '<p class="sin-horas">Cargando horarios…</p>';

        const siguiente = new Date(fecha); siguiente.setDate(siguiente.getDate() + 1);
        const rango = `?start=${fechaDia(fecha)}&end=${fechaDia(siguiente)}`;
        Promise.all([
            fetch(`/api/reservas/${recurso}/${rango}`).then(r => r.ok ? r.json() : Promise.reject()),
            fetch(`/api/bloqueos/${recurso}/${rango}`).then(r => r.ok ? r.json() : Promise.reject()),
        ]).then(([reservas, bloqueos]) => {
            const ocupados = reservas.concat(bloqueos).map(e => [new Date(e.start), new Date(e.end)]);
            const ahora = new Date();
            const libres = [];
            for (let h = datos.hora_inicio; h < datos.hora_fin; h++) {
                const inicio = new Date(fecha); inicio.setHours(h, 0, 0, 0);
                const fin = new Date(fecha); fin.setHours(h + 1, 0, 0, 0);
                if (inicio > ahora && !ocupados.some(([a, b]) => a < fin && b > inicio)) {
                    libres.push([inicio, fin]);
                }
            }
            mostrarHoras(libres);
        }).catch(() => {
            listaHoras.innerHTML = '<p class="sin-horas">No se pudieron cargar los horarios. Inténtalo de nuevo.</p>';
        });
    }

    // Una fila con su botón; al elegirla aparece "Confirmar" a su lado, como en una agenda en línea
    function filaOpcion(clase, texto, etiqueta, inicio, fin, todoElDia) {
        const fila = document.createElement('div');
        fila.className = 'fila-hora';
        const boton = document.createElement('button');
        boton.type = 'button';
        boton.className = clase;
        boton.textContent = texto;
        boton.setAttribute('aria-label', etiqueta);
        boton.addEventListener('click', () => {
            listaHoras.querySelectorAll('.fila-hora').forEach(f => {
                f.classList.remove('activa');
                const c = f.querySelector('.confirmar'); if (c) { c.remove(); }
            });
            fila.classList.add('activa');
            const confirmar = document.createElement('button');
            confirmar.type = 'button';
            confirmar.className = 'confirmar';
            confirmar.textContent = 'Confirmar';
            confirmar.addEventListener('click', () => confirmarHorario(inicio, fin, todoElDia));
            fila.appendChild(confirmar);
            confirmar.focus();
        });
        fila.appendChild(boton);
        return fila;
    }

    function mostrarHoras(libres) {
        listaHoras.innerHTML = '';
        if (!libres.length) {
            listaHoras.innerHTML = '<p class="sin-horas">Ya no quedan horarios libres este día. Elige otro.</p>';
            return;
        }
        // El día completo solo se ofrece si todas sus horas están libres
        if (libres.length === datos.hora_fin - datos.hora_inicio) {
            const inicio = libres[0][0], fin = libres[libres.length - 1][1];
            listaHoras.appendChild(filaOpcion('todo-el-dia', `Todo el día · ${hora(inicio)} a ${hora(fin)}`,
                `Todo el día, de ${hora(inicio)} a ${hora(fin)}`, inicio, fin, true));
            const separador = document.createElement('p');
            separador.className = 'separador-horas';
            separador.textContent = 'O una hora';
            listaHoras.appendChild(separador);
        }
        libres.forEach(([inicio, fin]) => {
            listaHoras.appendChild(filaOpcion('hora', hora(inicio), `${hora(inicio)} a ${hora(fin)}`, inicio, fin, false));
        });
    }

    // ---------- Paso 3: confirmar y pagar ----------
    const modal = document.getElementById('modal-pago');
    const formulario = document.getElementById('form-pago');
    const errorPago = document.getElementById('pago-error');
    const botonPagar = document.getElementById('pago-pagar');
    const repetir = document.getElementById('pago-repetir');
    const bloqueNueva = document.getElementById('pago-tarjeta-nueva');
    let pendiente = null;

    function confirmarHorario(inicio, fin, todoElDia) {
        if (!datos.autenticado) {
            // Sin sesión: primero entrar o crear cuenta, y volver a esta misma página
            window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
            return;
        }
        pendiente = { inicio, fin };
        const t = textoFecha(inicio);
        document.getElementById('pago-fecha').textContent = t.charAt(0).toUpperCase() + t.slice(1);
        document.getElementById('pago-horario').textContent =
            `de ${hora(inicio)} a ${hora(fin)}` + (todoElDia ? ' (todo el día)' : '');
        repetir.value = '0';
        errorPago.classList.add('hidden');
        actualizarTotal();
        actualizarMetodo();
        modal.classList.remove('hidden');
        botonPagar.focus();
    }

    function metodoElegido() {
        const marcado = formulario.querySelector('input[name="metodo"]:checked');
        return marcado ? marcado.value : 'nueva';
    }

    function actualizarTotal() {
        const reservas = parseInt(repetir.value, 10) + 1;
        const horas = (pendiente.fin - pendiente.inicio) / 3600000;
        document.getElementById('pago-total').textContent = `$${(precioHora * horas * reservas).toFixed(2)}`;
        document.getElementById('pago-detalle-total').textContent = `${reservas} reserva(s) × ${horas} h × $${precioHora.toFixed(2)}`;
    }

    function actualizarMetodo() {
        const nueva = metodoElegido() === 'nueva';
        bloqueNueva.classList.toggle('hidden', !nueva);
        bloqueNueva.querySelectorAll('input[data-requerido]').forEach(i => { i.required = nueva; });
    }

    function cerrarModal() {
        modal.classList.add('hidden');
        // Los datos de la tarjeta no se conservan en la página
        bloqueNueva.querySelectorAll('input').forEach(i => { if (i.type === 'checkbox') { i.checked = false; } else { i.value = ''; } });
        pendiente = null;
    }

    repetir.addEventListener('change', actualizarTotal);
    formulario.querySelectorAll('input[name="metodo"]').forEach(r => r.addEventListener('change', actualizarMetodo));
    document.getElementById('pago-cancelar').addEventListener('click', cerrarModal);
    modal.addEventListener('click', e => { if (e.target === modal) { cerrarModal(); } });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.classList.contains('hidden')) { cerrarModal(); } });

    formulario.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!pendiente) { return; }
        const cuerpo = {
            resource_id: recurso,
            start_time: fechaISO(pendiente.inicio),
            end_time: fechaISO(pendiente.fin),
            repeat_weeks: parseInt(repetir.value, 10),
        };
        const metodo = metodoElegido();
        if (metodo === 'nueva') {
            cuerpo.tarjeta = {
                titular: document.getElementById('pago-titular').value,
                numero: document.getElementById('pago-numero').value,
                mes: document.getElementById('pago-mes').value,
                anio: document.getElementById('pago-anio').value,
                cvv: document.getElementById('pago-cvv').value,
            };
            cuerpo.guardar = document.getElementById('pago-guardar').checked;
        } else {
            cuerpo.payment_method_id = parseInt(metodo, 10);
        }

        botonPagar.disabled = true;
        botonPagar.textContent = 'Procesando…';
        errorPago.classList.add('hidden');
        const inicio = pendiente.inicio, fin = pendiente.fin;

        fetch('/api/reservas/crear/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify(cuerpo),
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    cerrarModal();
                    const t = textoFecha(inicio);
                    document.getElementById('detalle-confirmacion').textContent =
                        `${t.charAt(0).toUpperCase() + t.slice(1)}, de ${hora(inicio)} a ${hora(fin)}`
                        + (data.reservas.length > 1 ? ` (${data.reservas.length} semanas)` : '')
                        + `. Importe: $${data.pago.importe} · Referencia: ${data.pago.referencia}`;
                    selector.classList.add('hidden');
                    document.getElementById('confirmacion').classList.remove('hidden');
                } else {
                    errorPago.textContent = data.error || 'No se pudo crear la reserva.';
                    errorPago.classList.remove('hidden');
                    document.getElementById('pago-cvv').value = '';
                }
            })
            .catch(() => {
                errorPago.textContent = 'No se pudo contactar con el servidor. Inténtalo de nuevo.';
                errorPago.classList.remove('hidden');
            })
            .finally(() => { botonPagar.disabled = false; botonPagar.textContent = 'Pagar y reservar'; });
    });

    document.getElementById('otra-reserva').addEventListener('click', () => {
        // Una tarjeta recién guardada aparece en la siguiente reserva tras recargar
        window.location.reload();
    });

    cargarMes();
});
