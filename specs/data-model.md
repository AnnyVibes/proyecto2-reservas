# Modelo de datos

Descripción del esquema existente, sin migraciones nuevas. Todas las entidades
usan id BigAutoField como clave primaria; fechas con USE_TZ=True.

## Resource (cancha)
- name: CharField(100), único; description: TextField, admite vacío.
- price_per_hour: Decimal(8,2), valor predeterminado 10.00.
- Tiene muchas Booking y Availability. El deporte se deriva del nombre en la
  presentación; no existe campo deporte ni horario propio.

## Booking (reserva)
- user → auth.User, FK CASCADE, inversa bookings.
- resource → Resource, FK CASCADE, inversa bookings.
- start_time, end_time: DateTime obligatorios; created_at: auto_now_add.
- status: CharField(10), confirmada (predeterminado) o cancelada.
- cancelled_at: DateTime nullable/blank.
- Restricción BD reserva_confirmada_unica_por_franja: única combinación
  resource/start_time/end_time solo cuando status=confirmada.
- clean delega solapes a services/reservas.py; el servicio valida horario 09–21,
  mismo día, fin posterior, futuro y hasta 12 repeticiones. Son validaciones de
  aplicación, no CHECK SQL. La unicidad no impide por sí sola solapes parciales.

## Availability (bloqueo)
- resource → Resource, FK CASCADE, inversa availabilities.
- start_time, end_time: DateTime obligatorios.
- A pesar del nombre, representa indisponibilidad. Sin estado ni restricción SQL
  de solape o de orden de fechas. Sus intervalos impiden reservas vía hay_conflicto.

## PaymentMethod (tarjeta simulada)
- user → auth.User, FK CASCADE, inversa payment_methods.
- holder_name: CharField(100); brand: CharField(20), visa/mastercard/amex/otra.
- last4: CharField(4); exp_month y exp_year: PositiveSmallInteger.
- token: UUID único, no editable, generado con uuid4; created_at: auto_now_add.
- No almacena número completo ni CVV. Validación de tarjeta/vencimiento en pagos.py;
  no existe unicidad SQL de usuario/marca/last4/vencimiento.

## Payment (pago simulado)
- booking → Booking, OneToOne CASCADE, inversa payment.
- payment_method → PaymentMethod, FK SET_NULL, nullable/blank, inversa payments.
- amount: Decimal(10,2); status: CharField(10), aprobado o rechazado.
- reference: CharField(40), única; created_at: auto_now_add.
- Cada reserva tiene como máximo un pago. Al borrar una tarjeta se conserva el pago.
  El flujo actual revierte reserva y pago ante rechazo: rechazado existe en el modelo,
  pero reservar_y_pagar no persiste intentos rechazados. Cancelar no borra el pago.

## Relaciones
```text
User 1 ── N Booking N ── 1 Resource 1 ── N Availability
User 1 ── N PaymentMethod 1 ── N Payment 1 ── 1 Booking
```

Las opciones choices validan formularios/modelos explícitamente; no se debe asumir
que objects.create ejecuta full_clean ni que impone todas las reglas en la BD.
