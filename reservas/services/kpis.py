"""KPIs de solo lectura: adaptador ORM y núcleo de cálculo puro separado."""
from datetime import datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.utils import timezone

from reservas.models import Booking, Payment, Resource
from reservas.services.reservas import FRANJA_FIN, FRANJA_INICIO

ZONA = ZoneInfo('America/Panama')
CERO = Decimal('0.00')
MAX_DIAS = 366


def limites(desde, hasta):
    """Fechas inclusivas a intervalo consciente [inicio, fin), sin usar el reloj."""
    dias = (hasta - desde).days + 1
    if not 1 <= dias <= MAX_DIAS:
        raise ValueError(f'El rango debe tener entre 1 y {MAX_DIAS} días.')
    try:
        fin = hasta + timedelta(days=1)
    except OverflowError as exc:
        raise ValueError('La fecha final está fuera del rango admitido.') from exc
    return (datetime.combine(desde, time.min, ZONA),
            datetime.combine(fin, time.min, ZONA))


def variacion(actual, anterior):
    """Cambio relativo; None expresa falta de base, nunca división por cero."""
    if not anterior:
        return 0.0 if not actual else None
    return round(float((actual - anterior) / anterior * 100), 2)


def resumir_kpis(desde, hasta, *, canchas, reservas, pagos, usuarios, cancha=None):
    """Función pura sobre listas de diccionarios (contratos de values del adaptador).

    No consulta BD, no modifica entradas y no lee reloj ni zona horaria global.
    Usuarios nuevos es global; pagos y reservas sí se filtran por cancha.
    """
    inicio, fin = limites(desde, hasta)
    dias = (hasta - desde).days + 1
    seleccion = [c for c in canchas if cancha is None or c['id'] == cancha]
    ids = {c['id'] for c in seleccion}
    horas_cancha = {c['id']: 0.0 for c in seleccion}
    conteos = dict.fromkeys(range(FRANJA_INICIO, FRANJA_FIN), 0)
    total = canceladas = 0
    for r in reservas:
        if r['resource_id'] not in ids:
            continue
        if inicio <= r['start_time'] < fin:
            total += 1
            canceladas += r['status'] == Booking.Status.CANCELADA
        if r['status'] != Booking.Status.CONFIRMADA:
            continue
        a, b = max(inicio, r['start_time']), min(fin, r['end_time'])
        if a >= b:
            continue
        horas_cancha[r['resource_id']] += (b - a).total_seconds() / 3600
        franja = a.astimezone(ZONA).replace(minute=0, second=0, microsecond=0)
        while franja < b:
            if franja.hour in conteos:
                conteos[franja.hour] += 1
            franja += timedelta(hours=1)

    diarios = {desde + timedelta(days=i): CERO for i in range(dias)}
    ingresos = CERO
    aprobados = 0
    for p in pagos:
        if (p['booking__resource_id'] in ids and p['status'] == Payment.Status.APROBADO
                and inicio <= p['created_at'] < fin):
            ingresos += p['amount']
            aprobados += 1
            diarios[p['created_at'].astimezone(ZONA).date()] += p['amount']
    capacidad_cancha = dias * (FRANJA_FIN - FRANJA_INICIO)
    capacidad = capacidad_cancha * len(seleccion)
    horas = sum(horas_cancha.values())
    ranking = sorted([
        {'id': c['id'], 'nombre': c['name'], 'horas': round(horas_cancha[c['id']], 2),
         'ocupacion': round(horas_cancha[c['id']] / capacidad_cancha * 100, 2)}
        for c in seleccion
    ], key=lambda c: (-c['horas'], c['nombre'], c['id']))
    maximo = max(conteos.values(), default=0)
    return {
        'ocupacion': round(horas / capacidad * 100, 2) if capacidad else 0.0,
        'horas_reservadas': round(horas, 2), 'horas_disponibles': capacidad,
        'ingresos': ingresos, 'cancelaciones': canceladas,
        'porcentaje_cancelaciones': round(canceladas / total * 100, 2) if total else 0.0,
        'reservas_totales': total,
        'ticket_promedio': (ingresos / aprobados).quantize(Decimal('0.01')) if aprobados else CERO,
        'clientes_nuevos': sum(inicio <= u['date_joined'] < fin for u in usuarios
                              if not u['is_staff'] and not u['is_superuser']),
        'horas_pico': [{'hora': h, 'reservas': n} for h, n in conteos.items()],
        'horas_pico_top': [h for h, n in conteos.items() if n == maximo and maximo > 0],
        'canchas_mas_usadas': ranking,
        'ingresos_por_dia': [{'fecha': d.isoformat(), 'importe': v} for d, v in diarios.items()],
    }


def calcular_kpis(desde, hasta, cancha=None):
    """Carga un rango explícito, opcionalmente una Resource; nunca escribe datos."""
    inicio, fin = limites(desde, hasta)
    reservas = Booking.objects.filter(start_time__lt=fin, end_time__gt=inicio)
    pagos = Payment.objects.filter(created_at__gte=inicio, created_at__lt=fin,
                                   status=Payment.Status.APROBADO)
    canchas = Resource.objects.all()
    if cancha is not None:
        canchas = canchas.filter(pk=cancha.pk)
        reservas = reservas.filter(resource=cancha)
        pagos = pagos.filter(booking__resource=cancha)
    usuarios = get_user_model().objects.filter(date_joined__gte=inicio, date_joined__lt=fin,
                                               is_staff=False, is_superuser=False)
    return resumir_kpis(
        desde, hasta, cancha=cancha.pk if cancha is not None else None,
        canchas=list(canchas.values('id', 'name')),
        reservas=list(reservas.values('resource_id', 'start_time', 'end_time', 'status')),
        pagos=list(pagos.values('booking__resource_id', 'created_at', 'amount', 'status')),
        usuarios=list(usuarios.values('date_joined', 'is_staff', 'is_superuser')),
    )
