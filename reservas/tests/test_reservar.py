from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from reservas.models import Resource


class ReservarPasoAPasoTests(TestCase):
    """Página de reserva paso a paso (RF-03, AC-01 y AC-02)."""

    def setUp(self):
        self.resource = Resource.objects.create(name='Cancha de fútbol 5')
        self.url = reverse('reservar', args=[self.resource.id])

    def test_muestra_calendario_horarios_y_modal_de_pago(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        for fragmento in ('id="dias"', 'id="lista-horas"', 'id="modal-pago"', 'reservar.js', 'Cancha de fútbol 5'):
            with self.subTest(fragmento=fragmento):
                self.assertContains(response, fragmento)

    def test_indica_si_hay_sesion_para_pedir_login_al_confirmar(self):
        self.assertContains(self.client.get(self.url), '"autenticado": false')
        self.client.force_login(User.objects.create_user(username='ana', password='clave-segura-123'))
        self.assertContains(self.client.get(self.url), '"autenticado": true')

    def test_cancha_inexistente_devuelve_404(self):
        self.assertEqual(self.client.get(reverse('reservar', args=[99999])).status_code, 404)

    def test_inicio_enlaza_a_reservar_con_icono_del_deporte(self):
        Resource.objects.create(name='Pista de tenis')
        response = self.client.get(reverse('home'))
        self.assertContains(response, f'href="{self.url}"')
        self.assertContains(response, 'reservas/img/balon.svg')
        self.assertContains(response, 'reservas/img/deporte-tenis.svg')
