# Contrato HTTP existente y panel nuevo

API de mismo origen, sesión Django y protección CSRF en POST. Errores de las APIs:
`{"success": false, "error": "mensaje"}` salvo 403 CSRF y 405 de método (Django).
Fechas ISO sin offset se interpretan en America/Panama. Los endpoints GET de eventos
son públicos; no exponen identidad de otros clientes.

## GET /api/reservas/<id>/ (api_reservas)
ID de Resource. Parámetros opcionales start y end, ambos requeridos si se envía uno;
fecha YYYY-MM-DD o ISO con hora (se usa su fecha), end exclusivo y posterior a start.
Sin rango devuelve todas las reservas activas. 200: lista de eventos con title
(«Tu reserva» o «Reservado»), start/end ISO y color. 400: rango inválido.
Una cancha inexistente devuelve lista vacía, no 404 (comportamiento existente).

## POST /api/reservas/crear/ (api_crear_reserva)
Requiere sesión y CSRF. Cuerpo JSON objeto:
- resource_id: identificador de cancha; start_time y end_time: datetime ISO.
- repeat_weeks: entero 0–12, opcional (0); guardar: booleano opcional.
- payment_method_id: tarjeta propia guardada; alternativamente tarjeta con
  titular, numero, mes, anio y cvv. Los datos sensibles solo se usan transitoriamente.

201: success=true, reservas=[{start,end}], pago={importe (cadena decimal),
referencia, tarjeta (descripción segura)}. Repeticiones y pago son atómicos.
400: JSON/fechas/repetición/reglas horarias o tarjeta inválidos.
401: sin sesión. 402: pago rechazado. 404: cancha o tarjeta propia inexistentes.
409: solape de cualquier repetición con reserva activa o bloqueo (BR-01).
405: método distinto de POST. 403: CSRF faltante o inválido.

## GET /api/bloqueos/<id>/ (api_bloqueos)
Mismo rango opcional start/end exclusivo que reservas. 200: lista de eventos
{title: «Bloqueado», start, end, color}. 400: rango inválido. ID inexistente: [].

## GET /api/disponibilidad/<id>/ (api_disponibilidad)
start/end obligatorios, end exclusivo; máximo 62 días. 200: lista
{fecha: YYYY-MM-DD, estado: libre|parcial|completo|pasado, libres: entero, total: 12}.
400: rango faltante, inválido o demasiado largo. 404: cancha inexistente.

## GET /panel/ (panel_kpis)
HTML, solo staff activo mediante staff_member_required. Parámetros opcionales:
desde/hasta: YYYY-MM-DD inclusivos (por defecto hoy−29 y hoy); pista: ID de Resource.
200: tarjetas, variaciones, gráficos y ranking para el filtro. 400: fecha inválida,
rango invertido o superior a 366 días, ID de pista mal formado. 404: pista inexistente.
302 a /admin/login/?next=/panel/ para visitante, no staff o usuario inactivo.
No crea reservas ni pagos. Definiciones y denominadores en architecture.md.

## GET /panel/demanda/ (panel_demanda, existente)
HTML, solo staff; pista opcional. 200: histórico semanal, previsión y mapa de calor;
404: pista inválida o inexistente; 302 al login de admin si no tiene acceso.
Se conserva la ruta y su comportamiento.
