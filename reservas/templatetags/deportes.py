"""Ícono del deporte de cada cancha, según su nombre."""
from django import template
from django.templatetags.static import static

register = template.Library()

# Palabra del nombre de la cancha -> imagen en reservas/static/reservas/img/
ICONOS = (
    ('tenis', 'deporte-tenis.svg'),
    ('padel', 'deporte-padel.svg'),
    ('pádel', 'deporte-padel.svg'),
    ('baloncesto', 'deporte-baloncesto.svg'),
    ('basket', 'deporte-baloncesto.svg'),
)
ICONO_POR_DEFECTO = 'balon.svg'   # fútbol y cualquier otra cancha


@register.simple_tag
def icono_deporte(nombre):
    nombre = (nombre or '').lower()
    archivo = next((img for palabra, img in ICONOS if palabra in nombre), ICONO_POR_DEFECTO)
    return static(f'reservas/img/{archivo}')
