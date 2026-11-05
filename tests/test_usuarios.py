"""BR-09 / RF-02: registro HTTP y redirecciones seguras de login y registro."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tests.helpers import registro_valido


class UsuariosTests(TestCase):
    def test_registro_valido_normaliza_correo_y_guarda_hash(self):
        """BR-09: nombre y correo limpios, clave hasheada y sesión iniciada."""
        datos = registro_valido(email='  ELIEL@EXAMPLE.TEST ', first_name=' Eliel ')
        respuesta = self.client.post(reverse('registro'), datos)
        self.assertRedirects(respuesta, '/', fetch_redirect_response=False)
        usuario = User.objects.get()
        self.assertEqual(usuario.email, 'eliel@example.test')
        self.assertEqual(usuario.first_name, 'Eliel')
        self.assertTrue(usuario.check_password(datos['password1']))
        self.assertNotEqual(usuario.password, datos['password1'])
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def assert_rechazado(self, cambios, campo):
        antes = User.objects.count()
        respuesta = self.client.post(reverse('registro'), registro_valido(**cambios))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(campo, respuesta.context['form'].errors)
        self.assertEqual(User.objects.count(), antes)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_correo_invalido(self):
        """BR-09: un correo sin dominio válido se rechaza en su campo."""
        self.assert_rechazado({'email': 'sin-arroba'}, 'email')

    def test_correo_repetido_sin_distinguir_mayusculas(self):
        """BR-09: el mismo correo con mayúsculas no crea otra cuenta."""
        User.objects.create_user('existente', email='ELIEL@example.test')
        self.assert_rechazado({'email': 'eliel@EXAMPLE.TEST'}, 'email')

    def test_usuario_repetido(self):
        """BR-09: username debe ser único aunque cambie el correo."""
        User.objects.create_user('nuevo_cliente', email='otro@example.test')
        self.assert_rechazado({}, 'username')

    def test_contrasenas_distintas(self):
        """BR-09: confirmar otra contraseña produce error sin guardar usuario."""
        self.assert_rechazado({'password2': 'Distinta!Robles-739'}, 'password2')

    def test_contrasena_corta(self):
        """BR-09: siete caracteres no cumplen el mínimo de ocho."""
        self.assert_rechazado({'password1': 'M!7aQ2x', 'password2': 'M!7aQ2x'}, 'password2')

    def test_contrasena_comun(self):
        """BR-09: una contraseña común se rechaza aun con longitud suficiente."""
        self.assert_rechazado({'password1': 'password', 'password2': 'password'}, 'password2')

    def test_contrasena_numerica(self):
        """BR-09: longitud suficiente no autoriza claves solo numéricas."""
        self.assert_rechazado({'password1': '83649172508', 'password2': '83649172508'}, 'password2')

    def test_contrasena_parecida_al_usuario(self):
        """BR-09: impide usar el nombre de usuario como contraseña."""
        self.assert_rechazado({'password1': 'nuevo_cliente', 'password2': 'nuevo_cliente'}, 'password2')

    def test_nombre_vacio_o_espacios(self):
        """BR-09: el nombre debe contener algo además de espacios."""
        for nombre in ['', '   ']:
            with self.subTest(nombre=nombre):
                self.assert_rechazado({'first_name': nombre}, 'first_name')

    def test_registro_ignora_next_externo_y_relativo_a_protocolo(self):
        """RF-04: ni una URL absoluta ajena ni //otro.host recibe la sesión."""
        for i, destino in enumerate(['https://externo.example/', '//externo.example/']):
            with self.subTest(destino=destino):
                self.client.logout()
                url = reverse('registro') + '?next=' + destino
                respuesta = self.client.post(url, registro_valido(username=f'cliente_{i}', email=f'c{i}@example.test'))
                self.assertRedirects(respuesta, '/', fetch_redirect_response=False)
                self.assertIn('_auth_user_id', self.client.session)

    def test_login_ignora_next_externo(self):
        """RF-04: login tampoco permite una redirección abierta."""
        datos = registro_valido()
        User.objects.create_user(datos['username'], password=datos['password1'])
        for destino in ['https://externo.example/', '//externo.example/']:
            with self.subTest(destino=destino):
                self.client.logout()
                respuesta = self.client.post(reverse('login') + '?next=' + destino,
                    {'username': datos['username'], 'password': datos['password1']})
                self.assertRedirects(respuesta, '/', fetch_redirect_response=False)
