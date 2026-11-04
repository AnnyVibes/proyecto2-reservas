# Reglas de negocio

Versión 1.0 · Responsable: Anllelina Varcasia. Las reglas BR-01 a BR-08 ya existían en el
Proyecto 1 (`reservas/services/`) y aquí quedan especificadas; BR-09 es nueva.

| ID | Regla | Dónde se valida |
|---|---|---|
| BR-01 | **No se permite doble reserva:** una cancha no puede tener dos reservas activas que se solapen, ni una reserva que se solape con un bloqueo. Dos franjas se solapan si `inicio_a < fin_b` y `fin_a > inicio_b`. | `services/reservas.py` (servidor) |
| BR-02 | Una reserva va de las 09:00 a las 21:00 como máximo. La reserva paso a paso ofrece turnos de 1 hora o el día completo (09:00–21:00) cuando todas sus horas están libres; el calendario completo permite cualquier franja dentro de ese horario. | `services/reservas.py` |
| BR-03 | No se puede reservar una franja que empieza en el pasado. | `services/reservas.py` |
| BR-04 | El fin de la reserva debe ser posterior al inicio y caer en el mismo día. | `services/reservas.py` |
| BR-05 | Una reserva puede repetirse cada semana hasta 12 semanas más; si una semana choca, no se crea ninguna. | `services/reservas.py` |
| BR-06 | Solo un usuario con sesión iniciada puede crear una reserva. | `views.api_crear_reserva` |
| BR-07 | El cliente puede cancelar su reserva hasta 2 horas antes de que empiece; la franja vuelve a quedar libre. | `services/reservas.py` |
| BR-08 | El pago es simulado: la tarjeta 4242 4242 4242 4242 se aprueba y la 4000 0000 0000 0002 se rechaza. | `services/pagos.py` |
| BR-09 | **Registro:** usuario único; nombre obligatorio; correo válido y único sin distinguir mayúsculas; contraseña de al menos 8 caracteres, que no sea común, solo números ni parecida al usuario, escrita dos veces igual. | `forms_cuenta.RegistroForm` |

## Disponibilidad que se muestra al cliente
- Un día está **disponible** si le queda al menos una franja libre y no es pasado.
- Una franja está **libre** si no la solapa una reserva activa ni un bloqueo, y no ha empezado.
- El front solo muestra lo libre, pero la decisión final es siempre del servidor (BR-01).
