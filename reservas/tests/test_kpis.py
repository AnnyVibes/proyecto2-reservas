"""RF-08 / AC-10: cifras conocidas, límites temporales, permisos y filtros."""
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from reservas.models import Availability, Booking, Payment, Resource
from reservas.services.kpis import calcular_kpis, limites, resumir_kpis, variacion

ZONA = ZoneInfo('America/Panama')
DIA = date(2026, 10, 1)


def momento(dia=DIA, hora=0, minuto=0):
    return datetime(dia.year, dia.month, dia.day, hora, minuto, tzinfo=ZONA)


class CalculoPuroTests(SimpleTestCase):
    def test_sin_datos_y_sin_canchas(self):
        datos = resumir_kpis(DIA, DIA, canchas=[], reservas=[], pagos=[], usuarios=[])
        for clave in ('ocupacion', 'ingresos', 'cancelaciones', 'porcentaje_cancelaciones',
                      'clientes_nuevos', 'reservas_totales', 'ticket_promedio'):
            self.assertEqual(datos[clave], 0)
        self.assertEqual(datos['horas_pico_top'], [])
        self.assertEqual(len(datos['ingresos_por_dia']), 1)

    def test_variacion(self):
        self.assertEqual(variacion(15, 10), 50)
        self.assertEqual(variacion(0, 10), -100)
        self.assertEqual(variacion(0, 0), 0)
        self.assertIsNone(variacion(10, 0))

    def test_rango_invertido_excesivo_y_extremo(self):
        for desde, hasta in [(DIA, DIA - timedelta(days=1)),
                             (DIA, DIA + timedelta(days=366)), (date.max, date.max)]:
            with self.subTest(desde=desde, hasta=hasta), self.assertRaises(ValueError):
                limites(desde, hasta)

    def test_nucleo_puro_filtra_cancha_y_no_muta_datos(self):
        canchas = [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}]
        reservas = [{'resource_id': 1, 'start_time': momento(hora=9),
                     'end_time': momento(hora=10, minuto=30), 'status': 'confirmada'},
                    {'resource_id': 2, 'start_time': momento(hora=9),
                     'end_time': momento(hora=12), 'status': 'confirmada'}]
        resultado = resumir_kpis(DIA, DIA, cancha=1, canchas=canchas,
                                reservas=reservas, pagos=[], usuarios=[])
        self.assertEqual(resultado['horas_reservadas'], 1.5)
        self.assertEqual(resultado['ocupacion'], 12.5)
        self.assertEqual(resultado['horas_pico_top'], [9, 10])
        self.assertEqual(len(reservas), 2)
        self.assertEqual(reservas[0]['end_time'], momento(hora=10, minuto=30))


class KpisTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user('cliente', date_joined=momento(hora=23))
        cls.staff = User.objects.create_user('staff', is_staff=True, date_joined=momento())
        cls.otro = User.objects.create_user('anterior', date_joined=momento(DIA - timedelta(days=1)))
        cls.a = Resource.objects.create(name='Cancha A')
        cls.b = Resource.objects.create(name='Cancha B')
        cls.r1 = Booking.objects.create(user=cls.usuario, resource=cls.a,
                                       start_time=momento(hora=9), end_time=momento(hora=11))
        cls.r2 = Booking.objects.create(user=cls.otro, resource=cls.b,
                                       start_time=momento(hora=10), end_time=momento(hora=11))
        cls.cancelada = Booking.objects.create(user=cls.usuario, resource=cls.a,
                                               start_time=momento(hora=12), end_time=momento(hora=13),
                                               status='cancelada')
        cls.rechazada = Booking.objects.create(user=cls.usuario, resource=cls.b,
                                               start_time=momento(hora=14), end_time=momento(hora=15),
                                               status='cancelada')
        for i, (reserva, importe, estado) in enumerate([
                (cls.r1, '40.00', 'aprobado'), (cls.r2, '20.00', 'aprobado'),
                (cls.cancelada, '10.00', 'aprobado'), (cls.rechazada, '99.00', 'rechazado')]):
            pago = Payment.objects.create(booking=reserva, amount=importe, status=estado,
                                          reference=f'KPIS-{i}')
            Payment.objects.filter(pk=pago.pk).update(created_at=momento(hora=23, minuto=59))
        # El bloqueo no resta capacidad teórica.
        Availability.objects.create(resource=cls.a, start_time=momento(hora=16),
                                    end_time=momento(hora=18))

    def test_ocupacion_y_capacidad(self):
        datos = calcular_kpis(DIA, DIA)
        self.assertEqual(datos['horas_reservadas'], 3)
        self.assertEqual(datos['horas_disponibles'], 24)
        self.assertEqual(datos['ocupacion'], 12.5)

    def test_ingresos_y_ticket_incluyen_pago_de_cancelada_no_rechazado(self):
        datos = calcular_kpis(DIA, DIA)
        self.assertEqual(datos['ingresos'], Decimal('70.00'))
        self.assertEqual(datos['ticket_promedio'], Decimal('23.33'))
        self.assertEqual(datos['ingresos_por_dia'], [{'fecha': DIA.isoformat(), 'importe': Decimal('70')}])

    def test_totales_y_cancelaciones(self):
        datos = calcular_kpis(DIA, DIA)
        self.assertEqual(datos['reservas_totales'], 4)
        self.assertEqual(datos['cancelaciones'], 2)
        self.assertEqual(datos['porcentaje_cancelaciones'], 50)

    def test_horas_pico_cuenta_cada_hora_de_reserva_larga(self):
        datos = calcular_kpis(DIA, DIA)
        self.assertEqual(datos['horas_pico_top'], [10])
        self.assertEqual(datos['horas_pico'][:3], [
            {'hora': 9, 'reservas': 1}, {'hora': 10, 'reservas': 2}, {'hora': 11, 'reservas': 0}])

    def test_ranking_por_horas(self):
        ranking = calcular_kpis(DIA, DIA)['canchas_mas_usadas']
        self.assertEqual([(r['nombre'], r['horas']) for r in ranking],
                         [('Cancha A', 2), ('Cancha B', 1)])

    def test_clientes_nuevos_excluye_staff_y_es_global(self):
        self.assertEqual(calcular_kpis(DIA, DIA)['clientes_nuevos'], 1)
        self.assertEqual(calcular_kpis(DIA, DIA, self.b)['clientes_nuevos'], 1)

    def test_filtro_cancha(self):
        datos = calcular_kpis(DIA, DIA, self.a)
        self.assertEqual(datos['horas_disponibles'], 12)
        self.assertEqual(datos['ocupacion'], 16.67)
        self.assertEqual(datos['ingresos'], Decimal('50'))
        self.assertEqual(datos['reservas_totales'], 2)
        self.assertEqual(len(datos['canchas_mas_usadas']), 1)

    def test_filtro_fechas_inclusivo_y_dias_vacios(self):
        siguiente = DIA + timedelta(days=1)
        self.assertEqual(calcular_kpis(siguiente, siguiente)['ingresos'], 0)
        datos = calcular_kpis(DIA, siguiente)
        self.assertEqual(datos['ocupacion'], 6.25)
        self.assertEqual(datos['ingresos_por_dia'][1]['importe'], 0)

    def test_ingresos_por_fecha_pago_no_fecha_reserva(self):
        Payment.objects.filter(booking=self.r1).update(created_at=momento(DIA + timedelta(days=1)))
        self.assertEqual(calcular_kpis(DIA, DIA)['ingresos'], Decimal('30'))
        self.assertEqual(calcular_kpis(DIA + timedelta(days=1), DIA + timedelta(days=1))['ingresos'], 40)

    def test_limites_de_medianoche_local_y_utc(self):
        # 04:59 UTC sigue perteneciendo al día anterior en Panamá.
        pago = Payment.objects.get(booking=self.r1)
        Payment.objects.filter(pk=pago.pk).update(
            created_at=datetime(2026, 10, 2, 4, 59, tzinfo=ZoneInfo('UTC')))
        self.assertEqual(calcular_kpis(DIA, DIA)['ingresos'], 70)
        Payment.objects.filter(pk=pago.pk).update(created_at=momento(DIA + timedelta(days=1)))
        self.assertEqual(calcular_kpis(DIA, DIA)['ingresos'], 30)

    def test_duracion_recortada_al_rango(self):
        # Dato histórico fuera del horario: demuestra recorte defensivo del cálculo.
        Booking.objects.create(user=self.usuario, resource=self.a,
                               start_time=momento(DIA - timedelta(days=1), 23),
                               end_time=momento(DIA, 1))
        datos = calcular_kpis(DIA, DIA, self.a)
        self.assertEqual(datos['horas_reservadas'], 3)
        self.assertEqual(datos['reservas_totales'], 2)

    def test_servicio_solo_lectura_y_numero_consultas_constante(self):
        with self.assertNumQueries(4):
            calcular_kpis(DIA, DIA)
        self.assertEqual(Booking.objects.count(), 4)
        self.assertEqual(Payment.objects.count(), 4)

    def test_acceso_visitante_y_no_staff(self):
        url = reverse('panel_kpis')
        self.assertRedirects(self.client.get(url), '/admin/login/?next=/panel/', fetch_redirect_response=False)
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_staff_inactivo_no_accede(self):
        self.staff.is_active = False
        self.staff.save(update_fields=['is_active'])
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('panel_kpis')).status_code, 302)

    def test_staff_ve_filtros_indicadores_y_graficos(self):
        self.client.force_login(self.staff)
        respuesta = self.client.get(reverse('panel_kpis'),
                                   {'desde': '2026-10-01', 'hasta': '2026-10-01', 'pista': self.a.pk})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'reservas/admin/panel.html')
        self.assertEqual(respuesta.context['kpis']['ingresos'], 50)
        self.assertEqual(respuesta.context['kpis']['reservas_totales'], 2)
        self.assertContains(respuesta, 'chart.js@4.4.1')
        self.assertContains(respuesta, 'datos-kpis')
        self.assertContains(respuesta, 'Sin base anterior')

    def test_ultimos_30_dias_por_defecto(self):
        self.client.force_login(self.staff)
        with patch('reservas.views_admin.timezone.localdate', return_value=DIA):
            respuesta = self.client.get(reverse('panel_kpis'))
        self.assertEqual(respuesta.context['desde'], '2026-09-02')
        self.assertEqual(respuesta.context['hasta'], '2026-10-01')
        self.assertEqual(respuesta.context['anterior_hasta'], date(2026, 9, 1))

    def test_filtros_invalidos(self):
        self.client.force_login(self.staff)
        for filtros in [{'desde': ''}, {'desde': '2026-02-30'},
                        {'desde': '20261001'}, {'desde': '2026-10-02', 'hasta': '2026-10-01'},
                        {'desde': '2020-01-01', 'hasta': '2026-10-01'},
                        {'desde': '0001-01-01', 'hasta': '0001-01-01'},
                        {'pista': 'abc'}, {'pista': '9' * 40}]:
            with self.subTest(filtros=filtros):
                respuesta = self.client.get(reverse('panel_kpis'), filtros)
                self.assertEqual(respuesta.status_code, 400)
                self.assertContains(respuesta, 'Filtros inválidos', status_code=400)
        self.assertEqual(self.client.get(reverse('panel_kpis'), {'pista': 99999}).status_code, 404)

    def test_demanda_sigue_accesible_y_enlace_solo_staff(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('panel_demanda')).status_code, 200)
        self.assertContains(self.client.get(reverse('home')), 'href="/panel/"')
        self.client.force_login(self.usuario)
        self.assertNotContains(self.client.get(reverse('home')), 'href="/panel/"')

    def test_nombres_de_cancha_se_serializan_sin_inyectar_script(self):
        self.a.name = '</script><script>alert(1)</script>'
        self.a.save(update_fields=['name'])
        self.client.force_login(self.staff)
        respuesta = self.client.get(reverse('panel_kpis'))
        self.assertNotContains(respuesta, self.a.name)
        self.assertContains(respuesta, '\\u003C/script\\u003E')
