"""Trazabilidad explícita AC-01 a AC-10: integración HTTP, servicios y persistencia.

AC-01/02 verifican el contrato de servidor. La interacción JavaScript necesita
la comprobación adicional de navegador descrita en docs/testing.md.
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from reservas.models import Booking, Payment
from tests.helpers import AHORA, EscenarioReservas, momento, registro_valido


class AceptacionTests(EscenarioReservas, TestCase):
    def test_ac01_visitante_ve_cancha_y_disponibilidad(self):
        """AC-01 / RF-01,03: calendario y API públicos distinguen horas ocupadas."""
        self.client.logout()
        self.reserva()
        respuesta = self.client.get(reverse('reservar', args=[self.cancha.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['resource'], self.cancha)
        self.assertFalse(respuesta.context['datos_reserva']['autenticado'])
        dias = self.client.get(reverse('api_disponibilidad', args=[self.cancha.pk]),
            {'start': momento().date().isoformat(), 'end': momento(dias=2).date().isoformat()})
        self.assertEqual(dias.status_code, 200)
        self.assertEqual(dias.json()[0]['libres'], 11)
        eventos = self.client.get(reverse('api_reservas', args=[self.cancha.pk]))
        self.assertEqual(eventos.status_code, 200)
        self.assertEqual(len(eventos.json()), 1)
        self.assertEqual(eventos.json()[0]['title'], 'Reservado')

    def test_ac02_confirmacion_exige_sesion_y_login_vuelve_a_cancha(self):
        """AC-02 / RF-04: API deniega visitante; next interno conserva la cancha."""
        self.client.logout()
        self.assertEqual(self.post_reserva().status_code, 401)
        destino = reverse('reservar', args=[self.cancha.pk])
        respuesta = self.client.post(reverse('login') + '?next=' + destino,
            {'username': 'cliente_a', 'password': 'Cancha!Segura-738'}, follow=True)
        self.assertRedirects(respuesta, destino)
        self.assertTrue(respuesta.context['datos_reserva']['autenticado'])
        self.assertEqual(self.post_reserva().status_code, 201)

    def test_ac03_registro_valido_inicia_sesion(self):
        """AC-03 / BR-09: alta válida crea cuenta y deja autenticado al cliente."""
        self.client.logout()
        respuesta = self.client.post(reverse('registro'), registro_valido())
        self.assertEqual(respuesta.status_code, 302)
        usuario = User.objects.get(username='nuevo_cliente')
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_ac04_datos_invalidos_no_crean_cuenta(self):
        """AC-04: correo, nombre, claves distintas y débiles muestran error."""
        self.client.logout()
        for cambios, campo in [({'email': 'mal'}, 'email'), ({'first_name': ''}, 'first_name'),
            ({'password2': 'Otra!Clave-739'}, 'password2'),
            ({'password1': 'Ab1', 'password2': 'Ab1'}, 'password2')]:
            with self.subTest(cambios=cambios):
                respuesta = self.client.post(reverse('registro'), registro_valido(**cambios))
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(campo, respuesta.context['form'].errors)
                self.assertFalse(User.objects.filter(username='nuevo_cliente').exists())

    def test_ac05_usuario_y_correo_duplicados_rechazados(self):
        """AC-05: se prueban por separado las dos restricciones de unicidad."""
        self.client.logout()
        User.objects.create_user('nuevo_cliente', email='eliel@example.test')
        antes = User.objects.count()
        for cambios, campo in [({'email': 'distinto@example.test'}, 'username'),
                               ({'username': 'distinto', 'email': 'ELIEL@EXAMPLE.TEST'}, 'email')]:
            with self.subTest(campo=campo):
                respuesta = self.client.post(reverse('registro'), registro_valido(**cambios))
                self.assertIn(campo, respuesta.context['form'].errors)
                self.assertEqual(User.objects.count(), antes)

    def test_ac06_doble_reserva_api_409(self):
        """AC-06: reserva de otro cliente produce 409 y conserva solo la original."""
        original = self.reserva()
        self.assertEqual(self.post_reserva().status_code, 409)
        self.assertEqual(list(Booking.objects.values_list('pk', flat=True)), [original.pk])

    def test_ac07_cancelar_y_reservar_misma_franja(self):
        """AC-07: cancelación real, nuevo cliente y nuevo pago en la misma franja."""
        original = self.reserva(user=self.usuario)
        respuesta = self.client.post(reverse('cancelar_reserva', args=[original.pk]))
        self.assertEqual(respuesta.status_code, 302)
        self.client.force_login(self.otro)
        self.assertEqual(self.post_reserva().status_code, 201)
        original.refresh_from_db()
        self.assertEqual(original.status, Booking.Status.CANCELADA)
        self.assertEqual(Booking.objects.activas().get().user, self.otro)

    def test_ac08_horario_y_pasado_rechazados(self):
        """AC-08: ambos errores se validan directamente en el servidor."""
        for inicio, fin in [(momento(8), momento(9)), (momento(dias=-1), momento(11, dias=-1))]:
            with self.subTest(inicio=inicio):
                self.assertEqual(self.post_reserva(inicio, fin).status_code, 400)
        self.assertFalse(Booking.objects.exists())

    def test_ac09_menos_de_24_horas_no_cancela(self):
        """AC-09: el POST informa error y mantiene confirmada la reserva."""
        reserva = self.reserva(AHORA + timedelta(hours=23), user=self.usuario)
        respuesta = self.client.post(reverse('cancelar_reserva', args=[reserva.pk]), follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '24 horas')
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Booking.Status.CONFIRMADA)
        self.assertIsNone(reserva.cancelled_at)

    def test_ac10_panel_filtra_kpis_por_cancha_y_rango(self):
        """AC-10 / RF-08: staff ve cifras calculadas, visitante y cliente no acceden."""
        url = reverse('panel_kpis')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)
        staff = User.objects.create_user('administrador', is_staff=True)
        reserva = self.reserva(momento(9), momento(12))
        self.reserva(momento(9), momento(21), resource=self.otra_cancha)
        pago = Payment.objects.create(booking=reserva, amount='30.00', status='aprobado', reference='AC10-1')
        Payment.objects.filter(pk=pago.pk).update(created_at=momento(12))
        self.client.force_login(staff)
        dia = momento().date().isoformat()
        respuesta = self.client.get(url, {'desde': dia, 'hasta': dia, 'pista': self.cancha.pk})
        self.assertEqual(respuesta.status_code, 200)
        kpis = respuesta.context['kpis']
        self.assertEqual(kpis['reservas_totales'], 1)
        self.assertEqual(kpis['horas_reservadas'], 3)
        self.assertEqual(kpis['ocupacion'], 25)
        self.assertEqual(kpis['ingresos'], Decimal('30.00'))
        self.assertEqual(kpis['cancelaciones'], 0)
        otro_dia = momento(dias=2).date().isoformat()
        vacio = self.client.get(url, {'desde': otro_dia, 'hasta': otro_dia, 'pista': self.cancha.pk})
        self.assertEqual(vacio.context['kpis']['reservas_totales'], 0)
        self.assertEqual(vacio.context['kpis']['ingresos'], 0)
