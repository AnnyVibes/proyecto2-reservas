"""Datos aislados y reloj fijo: sin depender del día de ejecución ni de los demo."""
from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.urls import reverse

from reservas.models import Booking, Resource

ZONA = ZoneInfo('America/Panama')
AHORA = datetime(2030, 6, 10, 8, tzinfo=ZONA)


def momento(hora=10, minuto=0, dias=1):
    return (AHORA + timedelta(days=dias)).replace(hour=hora, minute=minuto)


def registro_valido(**cambios):
    datos = {'username': 'nuevo_cliente', 'first_name': 'Eliel',
             'email': 'eliel@example.test', 'password1': 'Canchas!Robles-739',
             'password2': 'Canchas!Robles-739'}
    datos.update(cambios)
    return datos


class EscenarioReservas:
    """Mixin sin tests propios; cada TestCase construye su propia base de datos."""
    def setUp(self):
        super().setUp()
        reloj = patch('django.utils.timezone.now', return_value=AHORA)
        reloj.start()
        self.addCleanup(reloj.stop)
        self.usuario = User.objects.create_user('cliente_a', password='Cancha!Segura-738')
        self.otro = User.objects.create_user('cliente_b', password='Cancha!Segura-739')
        self.cancha = Resource.objects.create(name='Cancha de tenis', price_per_hour='10.00')
        self.otra_cancha = Resource.objects.create(name='Cancha de fútbol', price_per_hour='20.00')
        self.client.force_login(self.usuario)

    def reserva(self, inicio=None, fin=None, **cambios):
        inicio = inicio or momento()
        datos = {'user': self.otro, 'resource': self.cancha,
                 'start_time': inicio, 'end_time': fin or inicio + timedelta(hours=1)}
        datos.update(cambios)
        return Booking.objects.create(**datos)

    def post_reserva(self, inicio=None, fin=None, *, cancha=None, cliente=None, **cambios):
        inicio = inicio or momento()
        datos = {'resource_id': (cancha or self.cancha).pk,
                 'start_time': inicio.isoformat(),
                 'end_time': (fin or inicio + timedelta(hours=1)).isoformat(),
                 'repeat_weeks': 0,
                 'tarjeta': {'titular': 'Cliente Prueba', 'numero': '4242424242424242',
                             'mes': 12, 'anio': 2035, 'cvv': '987'}}
        datos.update(cambios)
        return (cliente or self.client).post(reverse('api_crear_reserva'), datos,
                                             content_type='application/json')
