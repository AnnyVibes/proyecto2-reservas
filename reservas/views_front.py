"""
Vistas del front nuevo del Proyecto 2: registro de clientes y reserva paso a paso
(día disponible -> horario -> confirmar). Las reglas de negocio siguen en reservas.services.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms_cuenta import RegistroForm
from .models import Resource
from .services.reservas import FRANJA_FIN, FRANJA_INICIO, MAX_SEMANAS_REPETICION


def _destino_seguro(request):
    """El ?next= solo se respeta si apunta a este mismo sitio."""
    next_url = request.GET.get('next', '')
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()},
                                       require_https=request.is_secure()):
        return next_url
    return '/'


def registro(request):
    """Alta de un cliente: valida los datos, crea la cuenta e inicia sesión."""
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, f'¡Bienvenido, {usuario.first_name}! Tu cuenta está lista.')
        return redirect(_destino_seguro(request))
    return render(request, 'reservas/registro.html', {'form': form})


def reservar(request, resource_id):
    """Reserva paso a paso: calendario del mes, horarios libres del día y confirmación con pago."""
    resource = get_object_or_404(Resource, id=resource_id)
    tarjetas = []
    if request.user.is_authenticated:
        tarjetas = [
            {'id': t.id, 'marca': t.get_brand_display(), 'last4': t.last4,
             'vence': f'{t.exp_month:02d}/{t.exp_year % 100:02d}'}
            for t in request.user.payment_methods.order_by('-created_at')
        ]
    return render(request, 'reservas/reservar.html', {
        'resource': resource,
        'tarjetas': tarjetas,
        'semanas_repeticion': range(1, MAX_SEMANAS_REPETICION + 1),
        'datos_reserva': {
            'recurso': resource.id,
            'precio_hora': str(resource.price_per_hour),
            'hora_inicio': FRANJA_INICIO,
            'hora_fin': FRANJA_FIN,
            'autenticado': request.user.is_authenticated,
        },
    })
