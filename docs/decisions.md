# Registro de decisiones

Cada persona agrega sus decisiones al final, con número, fecha y autor. No se editan las de otros.

## D-01 · Partir del Proyecto 1 con su historial
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** el repositorio `proyecto2-reservas` se creó copiando `proyecto1-reservas` con todo su historial. La base de JStack-Dev que aparece en él se usó por indicación del profesor.
- **Motivo:** el Proyecto 2 continúa el mismo sistema de canchas, y el historial muestra de dónde parte cada cambio.

## D-02 · Tema: canchas deportivas
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** se mantiene el sistema de reservas de canchas deportivas, una de las opciones del enunciado.

## D-03 · Trabajo en cadena y archivos con dueño
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** se trabaja en orden: Anllelina (#1), luego Angélica (#2) y luego Eliel (#3). Cada persona empieza con `git pull` de `main` y solo modifica sus archivos, definidos en `.github/CODEOWNERS`.
- **Motivo:** cada persona sube su parte sin conflictos con las demás.

## D-04 · Reserva paso a paso inspirada en una agenda en línea
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** nueva página `/reservar/<id>/` con la información de la cancha a la izquierda y, a la derecha, el mes con los días disponibles, los horarios libres y un botón Confirmar junto al horario elegido. Se tomó como referencia el flujo de una página pública de Calendly, sin copiar su marca ni sus recursos.
- **Se conserva** el calendario completo del Proyecto 1 (`/calendario_full/<id>/`), enlazado desde la nueva página, para las vistas de semana y día.
- **Motivo:** el outcome O2 pide confirmar en 3 pasos sin ayuda del personal.

## D-05 · Imágenes propias en SVG
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** el balón, la cancha y los íconos de cada deporte se dibujaron como SVG propios en `reservas/static/reservas/img/`.
- **Motivo:** no hay que descargar imágenes de terceros ni preocuparse por licencias, y se ven nítidas en cualquier tamaño.

## D-06 · Registro de clientes en archivos nuevos
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** el registro y la reserva paso a paso viven en `views_front.py` y `forms_cuenta.py`, en lugar de ampliar `views.py`.
- **Motivo:** así Angélica puede trabajar en las vistas del panel sin tocar los mismos archivos.
