"""Panel de KPIs: validación de filtros, autorización y presentación."""
from datetime import date, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from reservas.models import Resource
from reservas.services.kpis import calcular_kpis, limites, variacion


@staff_member_required
@require_GET
def panel_kpis(request):
    hoy = timezone.localdate()
    desde_texto = request.GET.get('desde', (hoy - timedelta(days=29)).isoformat())
    hasta_texto = request.GET.get('hasta', hoy.isoformat())
    pista_texto = request.GET.get('pista', '')
    contexto = {'desde': desde_texto, 'hasta': hasta_texto, 'pista_id': pista_texto,
                'pistas': Resource.objects.order_by('name')}
    try:
        desde, hasta = date.fromisoformat(desde_texto), date.fromisoformat(hasta_texto)
        if desde.isoformat() != desde_texto or hasta.isoformat() != hasta_texto:
            raise ValueError('Usa fechas con formato YYYY-MM-DD.')
        limites(desde, hasta)
        dias = (hasta - desde).days + 1
        anterior_hasta = desde - timedelta(days=1)
        anterior_desde = desde - timedelta(days=dias)
        if pista_texto and (not pista_texto.isascii() or not pista_texto.isdigit()
                            or len(pista_texto) > 18):
            raise ValueError('La cancha debe ser un identificador numérico válido.')
    except (ValueError, OverflowError) as exc:
        contexto['error'] = f'Filtros inválidos. {exc}'
        return render(request, 'reservas/admin/panel.html', contexto, status=400)
    pista = get_object_or_404(Resource, pk=int(pista_texto)) if pista_texto else None
    actual = calcular_kpis(desde, hasta, pista)
    anterior = calcular_kpis(anterior_desde, anterior_hasta, pista)
    definiciones = [
        ('ocupacion', 'Ocupación', '%'), ('ingresos', 'Ingresos', '$'),
        ('cancelaciones', 'Cancelaciones', ''),
        ('porcentaje_cancelaciones', 'Tasa de cancelación', '%'),
        ('clientes_nuevos', 'Clientes nuevos · global', ''),
        ('reservas_totales', 'Reservas totales', ''),
        ('ticket_promedio', 'Ticket promedio', '$'),
        ('horas_reservadas', 'Horas reservadas', 'h'),
    ]
    contexto.update({
        'kpis': actual, 'anterior_desde': anterior_desde, 'anterior_hasta': anterior_hasta,
        'tarjetas': [{'nombre': nombre, 'valor': actual[clave], 'unidad': unidad,
                     'decimales': 0 if clave in ('cancelaciones', 'clientes_nuevos', 'reservas_totales') else 2,
                     'variacion': variacion(actual[clave], anterior[clave])}
                    for clave, nombre, unidad in definiciones],
        'graficos': {
            'dias': [v['fecha'] for v in actual['ingresos_por_dia']],
            'ingresos': [float(v['importe']) for v in actual['ingresos_por_dia']],
            'canchas': [v['nombre'] for v in actual['canchas_mas_usadas']],
            'ocupacion': [v['ocupacion'] for v in actual['canchas_mas_usadas']],
            'horas': [f"{v['hora']:02d}:00" for v in actual['horas_pico']],
            'reservas': [v['reservas'] for v in actual['horas_pico']],
        },
    })
    return render(request, 'reservas/admin/panel.html', contexto)
