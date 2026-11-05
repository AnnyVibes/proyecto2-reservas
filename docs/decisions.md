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

## D-07 · Ajustes tras la primera revisión del front
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia
- **Decisión:** el calendario completo usa la misma tarjeta que la reserva paso a paso, con pasos y leyenda; los botones de volver y actualizar tienen un estilo común; la reserva paso a paso ofrece el día completo; se quitaron emojis de la portada y la zona horaria; Mis reservas pasa de tabla a tarjetas.
- **Datos demo:** `crear_reservas_demo` deja de crear la cancha "Pista Pádel 1" y usa la cancha de pádel del fixture `pistas`, para no mostrar una cancha repetida.

## D-08 · Conservar tecnología y la regla de solape existente
- **Fecha / responsable:** 2026-11-04 · Paso de Angélica; ejecución técnica por Codex, pendiente de revisión de Angélica.
- **Decisión de implementación del agente:** mantener Python/Django/SQLite y las dependencias existentes; documentar las capas y el modelo real antes de implementar el panel. No alterar hay_conflicto ni crear_reservas para preservar el contrato 409 y BR-01.
- **Límite:** los comandos demo y el guardado del admin no pasan por crear_reservas. Se dejó el hallazgo en el issue #2 porque modificar esos archivos no está autorizado. No se atribuye una garantía de exclusión concurrente a SQLite.

## D-09 · Fechas y denominadores explícitos para KPIs
- **Fecha / responsable:** 2026-11-04 · Paso de Angélica; propuesta implementada por Codex, pendiente de revisión de Angélica.
- **Decisión de implementación del agente:** fechas locales inclusivas, últimos 30 días incluido hoy, máximo 366 días; variación frente al período anterior de igual duración. Capacidad teórica de 12 horas por día y cancha sin restar bloqueos. Reservas/cancelaciones por fecha de inicio; ingresos por created_at del pago aprobado; ticket por pago aprobado. Clientes nuevos globales, excluyendo staff/superusuarios. Se muestran todos los empates en horas pico.
- **Motivo:** explicitar métricas que el enunciado no detalla y evitar mezclar cobros con fechas de juego. Las cancelaciones no implican reembolsos en el modelo existente.

## D-10 · Cálculo puro separado de lectura y panel sin archivos estáticos nuevos
- **Fecha / responsable:** 2026-11-04 · Paso de Angélica; propuesta implementada por Codex, pendiente de revisión de Angélica.
- **Decisión de implementación del agente:** núcleo resumir_kpis puro sobre datos explícitos; adaptador calcular_kpis de solo lectura con cuatro consultas por período. Vista staff separada, Chart.js 4.4.1, json_script y estilos dentro de la plantilla; solo adiciones autorizadas a navegación/rutas y CODEOWNERS.
- **Validación:** 23 pruebas nuevas para cálculos, filtros, zona horaria, permisos, datos vacíos y serialización segura. Inspección del navegador a 375 px sin desbordamiento horizontal y con tres gráficos renderizados.
- **Decisión reservada a Angélica:** revisión del PR y merge; no se afirma que haya aprobado las decisiones técnicas durante esta ejecución.

## D-11 · Validación de reservas en el admin (seguimiento de D-08)
- **Fecha / autor:** 2026-11-04 · Anllelina Varcasia (issue #6)
- **Hallazgo revisado:** el admin ya bloqueaba la doble reserva porque `Booking.clean()` usa `hay_conflicto`. El problema real era otro: con la cancha o una fecha vacías, `clean()` fallaba y el admin respondía con un error 500.
- **Decisión:** `Booking.clean()` solo compara franjas cuando hay cancha, inicio y fin, y solo para reservas confirmadas. Así el formulario marca el campo que falta, y una reserva cancelada se puede guardar sin chocar con otras.
- **Se mantiene:** los comandos de datos demo siguen con su propia comprobación de solapes, y la creación desde la app sigue pasando por `crear_reservas`.
- **Evidencia:** `reservas/tests/test_doble_reserva_admin.py`; la prueba del formulario incompleto falla sin el cambio y pasa con él.

## D-12 · Pruebas de contrato separadas por responsabilidad
- **Fecha / responsable:** 2026-11-05 · Paso de Eliel; ejecución técnica por Codex, pendiente de revisión de Eliel.
- **Decisión de implementación del agente:** agregar 47 pruebas en `tests/` sin tocar las 138 existentes ni la app. Cubrir BR-01 en servicio y API, ausencia de efectos de pago tras conflicto, límites exactos de horario/repetición/cancelación, BR-09 y AC-01 a AC-10. Usar reloj fijo y datos aislados para no depender del calendario real ni de los usuarios demo.
- **Evidencia:** línea base 138 OK; suite ampliada 185 OK. Las funciones puras de KPIs ya estaban cubiertas en el paso 2 y su evidencia se enlaza sin duplicarlas.

## D-13 · Distinguir CI, comprobación de navegador y decisión humana
- **Fecha / responsable:** 2026-11-05 · Paso de Eliel; propuesta ejecutada por Codex, pendiente de revisión de Eliel.
- **Decisión de implementación del agente:** CI Ubuntu/Python 3.12 por cada push y PR hacia main, usando solo dependencias fijadas y el runner de Django. Los tests HTTP se complementan con comprobación de navegador para AC-01/02, sin afirmar que CI ejecute JavaScript.
- **Validación del agente:** selección de día/hora como visitante, login con retorno a la misma cancha y reserva local con pago simulado de $10.00, confirmada también en BD. La captura queda fuera de Git.
- **Decisión reservada a Eliel:** revisión y merge del PR. El cambio de requisito del siguiente ciclo requiere un cambio concreto del equipo y no se inventa durante este paso.
