from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from reservas.models import Availability, Booking, Resource


class DobleReservaDesdeAdminTests(TestCase):
    """BR-01 también se cumple cuando un administrador crea o edita reservas en /admin/ (issue #6)."""

    def setUp(self):
        admin = User.objects.create_superuser('jefe', 'jefe@ejemplo.com', 'Clave-Admin-2026')
        self.client.force_login(admin)
        self.cliente = User.objects.create_user('ana', password='clave-segura-123')
        self.cancha = Resource.objects.create(name='Cancha de fútbol 5')
        self.dia = timezone.localdate() + timedelta(days=1)
        self.url = reverse('admin:reservas_booking_add')
        self.existente = Booking.objects.create(
            user=self.cliente, resource=self.cancha,
            start_time=self.momento(10), end_time=self.momento(11))

    def momento(self, hora, minuto=0):
        return timezone.make_aware(datetime.combine(self.dia, time(hora, minuto)))

    def datos(self, inicio='10:30:00', fin='11:30:00', **cambios):
        datos = {'user': self.cliente.id, 'resource': self.cancha.id,
                 'start_time_0': self.dia.isoformat(), 'start_time_1': inicio,
                 'end_time_0': self.dia.isoformat(), 'end_time_1': fin, 'status': 'confirmada'}
        datos.update(cambios)
        return datos

    def test_admin_rechaza_reserva_solapada(self):
        response = self.client.post(self.url, self.datos())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La franja horaria ya está reservada o bloqueada.')
        self.assertEqual(Booking.objects.count(), 1)

    def test_admin_rechaza_franja_bloqueada(self):
        Availability.objects.create(resource=self.cancha, start_time=self.momento(15), end_time=self.momento(17))
        response = self.client.post(self.url, self.datos(inicio='16:00:00', fin='17:00:00'))
        self.assertContains(response, 'La franja horaria ya está reservada o bloqueada.')
        self.assertEqual(Booking.objects.count(), 1)

    def test_admin_permite_franja_contigua_y_otra_cancha(self):
        self.client.post(self.url, self.datos(inicio='11:00:00', fin='12:00:00'))
        otra = Resource.objects.create(name='Pista de tenis')
        self.client.post(self.url, self.datos(resource=otra.id, inicio='10:00:00', fin='11:00:00'))
        self.assertEqual(Booking.objects.count(), 3)

    def test_admin_puede_cancelar_y_editar_sin_choque_consigo_misma(self):
        url = reverse('admin:reservas_booking_change', args=[self.existente.id])
        response = self.client.post(url, self.datos(inicio='10:00:00', fin='11:00:00', status='cancelada'))
        self.assertEqual(response.status_code, 302)
        self.existente.refresh_from_db()
        self.assertEqual(self.existente.status, Booking.Status.CANCELADA)

    def test_formulario_incompleto_muestra_error_sin_fallar(self):
        """Antes del issue #6, sin cancha o sin fecha el admin respondía con un error 500."""
        casos = {
            'sin cancha': self.datos(resource=''),
            'sin inicio': self.datos(start_time_0='', start_time_1=''),
            'sin fin': self.datos(end_time_0='', end_time_1=''),
        }
        for nombre, datos in casos.items():
            with self.subTest(nombre):
                response = self.client.post(self.url, datos)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Este campo es obligatorio')
        self.assertEqual(Booking.objects.count(), 1)
