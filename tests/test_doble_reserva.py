"""BR-01, BR-05, AC-06/07: contrato de exclusión del servicio y de la API."""
from datetime import timedelta

from django.test import TestCase

from reservas.models import Availability, Booking, Payment, PaymentMethod
from reservas.services.reservas import ConflictoHorario, crear_reservas
from tests.helpers import EscenarioReservas, momento


class DobleReservaTests(EscenarioReservas, TestCase):
    def test_ac06_misma_cancha_y_franja_servicio(self):
        """BR-01 / AC-06: otro cliente no puede duplicar una reserva activa."""
        original = self.reserva()
        with self.assertRaises(ConflictoHorario):
            crear_reservas(self.usuario, self.cancha, momento(), momento(11))
        self.assertEqual(list(Booking.objects.values_list('pk', flat=True)), [original.pk])

    def test_ac06_api_409_sin_pago_ni_tarjeta(self):
        """AC-06: conflicto HTTP 409 sin efectos secundarios del pago o guardar tarjeta."""
        self.reserva()
        respuesta = self.post_reserva(guardar=True)
        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(respuesta.json()['success'])
        self.assertEqual(Booking.objects.count(), 1)
        self.assertFalse(Payment.objects.exists())
        self.assertFalse(PaymentMethod.objects.exists())

    def test_solapes_parciales_por_ambos_lados_y_contencion(self):
        """BR-01: rechaza intersección parcial, inclusión y cobertura del intervalo."""
        self.reserva()
        for a, b in [(momento(10, 30), momento(11, 30)),
                     (momento(9, 30), momento(10, 30)),
                     (momento(10, 15), momento(10, 45)), (momento(9), momento(12))]:
            with self.subTest(inicio=a, fin=b):
                with self.assertRaises(ConflictoHorario):
                    crear_reservas(self.usuario, self.cancha, a, b)
                self.assertEqual(self.post_reserva(a, b).status_code, 409)
                self.assertEqual(Booking.objects.count(), 1)
                self.assertFalse(Payment.objects.exists())

    def test_franjas_contiguas_servicio_y_api(self):
        """BR-01: tocar el inicio o el fin no es un solape."""
        self.reserva()
        anterior = crear_reservas(self.usuario, self.cancha, momento(9), momento(10))
        respuesta = self.post_reserva(momento(11), momento(12))
        self.assertEqual(len(anterior), 1)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Booking.objects.activas().count(), 3)
        self.assertEqual(Payment.objects.count(), 1)

    def test_mismo_horario_otra_cancha_servicio(self):
        """BR-01: el conflicto se limita a la cancha elegida."""
        self.reserva()
        creadas = crear_reservas(self.usuario, self.otra_cancha, momento(), momento(11))
        self.assertEqual(creadas[0].resource, self.otra_cancha)
        self.assertEqual(Booking.objects.activas().count(), 2)

    def test_mismo_horario_otra_cancha_api(self):
        """BR-01: una reserva ajena en otra cancha no bloquea el pago."""
        self.reserva()
        self.assertEqual(self.post_reserva(cancha=self.otra_cancha).status_code, 201)
        self.assertEqual(Booking.objects.activas().count(), 2)

    def test_ac07_cancelada_permite_servicio(self):
        """AC-07: la cancelada permanece como historial sin ocupar la franja."""
        cancelada = self.reserva(status=Booking.Status.CANCELADA)
        creadas = crear_reservas(self.usuario, self.cancha, momento(), momento(11))
        self.assertEqual(len(creadas), 1)
        cancelada.refresh_from_db()
        self.assertEqual(cancelada.status, Booking.Status.CANCELADA)
        self.assertEqual(Booking.objects.activas().count(), 1)

    def test_ac07_cancelada_permite_api(self):
        """AC-07: se puede pagar una franja exactamente igual a una cancelada."""
        self.reserva(status=Booking.Status.CANCELADA)
        self.assertEqual(self.post_reserva().status_code, 201)
        self.assertEqual(Booking.objects.count(), 2)
        self.assertEqual(Booking.objects.activas().count(), 1)

    def test_bloqueo_parcial_rechazado_servicio_y_api(self):
        """BR-01: los bloqueos del administrador también impiden solapes parciales."""
        Availability.objects.create(resource=self.cancha, start_time=momento(10, 30),
                                    end_time=momento(11, 30))
        with self.assertRaises(ConflictoHorario):
            crear_reservas(self.usuario, self.cancha, momento(), momento(11))
        self.assertEqual(self.post_reserva().status_code, 409)
        self.assertFalse(Booking.objects.exists())
        self.assertFalse(Payment.objects.exists())

    def test_recurrente_conflicto_tardio_revierte_servicio(self):
        """BR-05: conflicto en la tercera semana revierte también las dos primeras."""
        self.reserva(momento(dias=15))
        with self.assertRaises(ConflictoHorario):
            crear_reservas(self.usuario, self.cancha, momento(), momento(11), 2)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertFalse(Booking.objects.filter(user=self.usuario).exists())

    def test_recurrente_conflicto_tardio_revierte_api_y_pagos(self):
        """BR-05: API atómica, sin reservas, pagos ni tarjeta nueva parciales."""
        self.reserva(momento(dias=15))
        respuesta = self.post_reserva(repeat_weeks=2, guardar=True)
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertFalse(Payment.objects.exists())
        self.assertFalse(PaymentMethod.objects.exists())

    def test_bloqueo_otra_cancha_no_afecta(self):
        """BR-01: un bloqueo de otra cancha permite reservar la seleccionada."""
        Availability.objects.create(resource=self.otra_cancha, start_time=momento(9), end_time=momento(21))
        self.assertEqual(self.post_reserva().status_code, 201)
