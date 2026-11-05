"""BR-02 a BR-08: límites exactos, permisos, CSRF y transacciones."""
from datetime import timedelta
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from reservas.models import Booking, Payment
from reservas.services.reservas import (
    CancelacionNoPermitida, ReservaInvalida, cancelar_reserva, crear_reservas,
)
from tests.helpers import AHORA, EscenarioReservas, momento


class ReglasTests(EscenarioReservas, TestCase):
    def test_br02_dia_completo_en_limites_permitido(self):
        """BR-02: 09:00–21:00 se admite y cobra doce horas."""
        respuesta = self.post_reserva(momento(9), momento(21))
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()['pago']['importe'], '120.00')

    def test_br02_fuera_de_horario_por_un_minuto(self):
        """BR-02: un minuto fuera del horario basta para rechazar la franja."""
        for inicio, fin in [(momento(8, 59), momento(10)), (momento(20), momento(21, 1))]:
            with self.subTest(inicio=inicio, fin=fin):
                with self.assertRaises(ReservaInvalida):
                    crear_reservas(self.usuario, self.cancha, inicio, fin)
                self.assertEqual(self.post_reserva(inicio, fin).status_code, 400)
        self.assertFalse(Booking.objects.exists())

    def test_br03_pasado_por_un_segundo(self):
        """BR-03: rechaza una franja que ya empezó, aunque todavía no termine."""
        with patch('django.utils.timezone.now', return_value=momento() + timedelta(seconds=1)):
            self.assertEqual(self.post_reserva().status_code, 400)
        self.assertFalse(Booking.objects.exists())

    def test_br03_inicio_exactamente_ahora_permitido(self):
        """BR-03: igualdad con el reloj no es pasado."""
        with patch('django.utils.timezone.now', return_value=momento()):
            self.assertEqual(self.post_reserva().status_code, 201)

    def test_br04_fin_igual_anterior_o_en_otro_dia(self):
        """BR-04: orden estricto y ambos extremos en la misma fecha local."""
        for fin in [momento(), momento(9), momento(11, dias=2)]:
            with self.subTest(fin=fin):
                self.assertEqual(self.post_reserva(fin=fin).status_code, 400)
        self.assertFalse(Booking.objects.exists())

    def test_br05_limite_12_repeticiones_mas_original(self):
        """BR-05: doce semanas adicionales producen trece reservas y trece pagos."""
        respuesta = self.post_reserva(repeat_weeks=12)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Booking.objects.count(), 13)
        self.assertEqual(Payment.objects.count(), 13)
        self.assertEqual(respuesta.json()['pago']['importe'], '130.00')
        self.assertEqual(Booking.objects.latest('start_time').start_time, momento() + timedelta(weeks=12))

    def test_br05_fuera_de_limite_y_tipos_invalidos(self):
        """BR-05: rechaza >12, negativos y valores que no sean enteros reales."""
        for semanas in [13, -1, True, '2', 1.5]:
            with self.subTest(semanas=semanas):
                self.assertEqual(self.post_reserva(repeat_weeks=semanas).status_code, 400)
        self.assertFalse(Booking.objects.exists())

    def test_br06_sesion_obligatoria(self):
        """BR-06: el visitante recibe 401 y no produce pagos."""
        respuesta = self.post_reserva(cliente=Client())
        self.assertEqual(respuesta.status_code, 401)
        self.assertFalse(Booking.objects.exists())
        self.assertFalse(Payment.objects.exists())

    def test_br06_sesion_no_sustituye_csrf(self):
        """RNF-02: sesión válida sin CSRF no autoriza crear ni cancelar."""
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        self.assertEqual(self.post_reserva(cliente=cliente).status_code, 403)
        reserva = self.reserva(user=self.usuario)
        self.assertEqual(cliente.post(reverse('cancelar_reserva', args=[reserva.pk])).status_code, 403)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Booking.Status.CONFIRMADA)

    def test_br07_exactamente_dos_horas_permitido_y_libera(self):
        """BR-07: el umbral exacto de dos horas se admite y libera la franja."""
        reserva = self.reserva(AHORA + timedelta(hours=2), user=self.usuario)
        cancelar_reserva(reserva)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Booking.Status.CANCELADA)
        self.assertEqual(reserva.cancelled_at, AHORA)
        self.assertEqual(self.post_reserva(reserva.start_time, reserva.end_time).status_code, 201)

    def test_br07_un_segundo_fuera_de_plazo(self):
        """BR-07: dos horas menos un segundo se rechaza sin alterar estado."""
        reserva = self.reserva(AHORA + timedelta(hours=2, seconds=-1), user=self.usuario)
        with self.assertRaises(CancelacionNoPermitida):
            cancelar_reserva(reserva)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Booking.Status.CONFIRMADA)
        self.assertIsNone(reserva.cancelled_at)

    def test_br07_reserva_ajena_no_se_cancela(self):
        """RF-07: otro cliente recibe 404, aunque la reserva esté dentro de plazo."""
        ajena = self.reserva()
        self.assertEqual(self.client.post(reverse('cancelar_reserva', args=[ajena.pk])).status_code, 404)
        ajena.refresh_from_db()
        self.assertEqual(ajena.status, Booking.Status.CONFIRMADA)

    def test_br08_rechazo_revierte_todo(self):
        """BR-08: pago simulado rechazado no deja reservas ni tarjetas persistidas."""
        tarjeta = {'titular': 'Cliente Prueba', 'numero': '4000000000000002',
                   'mes': 12, 'anio': 2035, 'cvv': '987'}
        respuesta = self.post_reserva(tarjeta=tarjeta, repeat_weeks=2, guardar=True)
        self.assertEqual(respuesta.status_code, 402)
        self.assertFalse(Booking.objects.exists())
        self.assertFalse(Payment.objects.exists())
        self.assertFalse(self.usuario.payment_methods.exists())
