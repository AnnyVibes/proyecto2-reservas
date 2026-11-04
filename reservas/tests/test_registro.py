from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistroTests(TestCase):
    """Validaciones de usuario al crear una cuenta (RF-02, AC-03 a AC-05)."""

    def datos(self, **cambios):
        datos = {'username': 'luis', 'first_name': 'Luis', 'email': 'luis@ejemplo.com',
                 'password1': 'Cancha-Futbol-2026', 'password2': 'Cancha-Futbol-2026'}
        datos.update(cambios)
        return datos

    def test_registro_valido_crea_cuenta_e_inicia_sesion(self):
        response = self.client.post(reverse('registro'), self.datos())
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        usuario = User.objects.get(username='luis')
        self.assertEqual(usuario.email, 'luis@ejemplo.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.id)

    def test_registro_respeta_next_interno_e_ignora_externo(self):
        url = f"{reverse('registro')}?next={reverse('reservar', args=[1])}"
        response = self.client.post(url, self.datos())
        self.assertRedirects(response, reverse('reservar', args=[1]), fetch_redirect_response=False)
        self.client.logout()
        response = self.client.post(f"{reverse('registro')}?next=https://sitio-malicioso.example/",
                                    self.datos(username='eva', email='eva@ejemplo.com'))
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_rechaza_datos_invalidos_sin_crear_cuenta(self):
        casos = {
            'usuario vacío': self.datos(username=''),
            'nombre vacío': self.datos(first_name='   '),
            'correo inválido': self.datos(email='no-es-correo'),
            'contraseñas distintas': self.datos(password2='Otra-Clave-2026'),
            'contraseña corta': self.datos(password1='Ab1', password2='Ab1'),
            'contraseña solo números': self.datos(password1='12345678901', password2='12345678901'),
        }
        for nombre, datos in casos.items():
            with self.subTest(nombre):
                response = self.client.post(reverse('registro'), datos)
                self.assertEqual(response.status_code, 200)
                self.assertFalse(User.objects.exists())

    def test_rechaza_usuario_o_correo_repetidos(self):
        User.objects.create_user(username='luis', email='luis@ejemplo.com', password='x-Clave-Segura-1')
        response = self.client.post(reverse('registro'), self.datos(email='otro@ejemplo.com'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('registro'), self.datos(username='otro', email='LUIS@ejemplo.com'))
        self.assertContains(response, 'Ya existe una cuenta con este correo.')
        self.assertEqual(User.objects.count(), 1)

    def test_con_sesion_redirige_al_inicio(self):
        self.client.force_login(User.objects.create_user(username='ana', password='clave-segura-123'))
        self.assertRedirects(self.client.get(reverse('registro')), reverse('home'), fetch_redirect_response=False)

    def test_login_y_registro_se_enlazan(self):
        self.assertContains(self.client.get(reverse('login')), f'href="{reverse("registro")}')
        self.assertContains(self.client.get(reverse('registro')), f'href="{reverse("login")}')
