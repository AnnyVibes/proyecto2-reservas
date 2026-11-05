# Cambio de requisito CR-01 · Cancelar con al menos 24 horas de anticipación

**Issue:** #10 · **Rama:** `anllelina/10-cambio-24-horas` · **Fecha:** 2026-11-05

## 1. Cambio solicitado
A mitad del desarrollo, el complejo pide que una reserva solo se pueda cancelar hasta **24 horas**
antes de que empiece, en lugar de 2. Motivo: con 2 horas, las franjas canceladas a última hora
quedaban vacías porque ya no daba tiempo de que otro cliente las reservara (outcome O1/O2).

| | Antes (v1.0) | Después (v1.1) |
|---|---|---|
| BR-07 | Cancelar hasta 2 horas antes | Cancelar hasta 24 horas antes; con exactamente 24 horas se permite |
| AC-09 | Rechazo con menos de 2 horas | Rechazo con menos de 24 horas y mensaje con el plazo de 24 horas |

## Roles en este ciclo (rotados)
| Rol | Ciclo 1 | Ciclo 2 (CR-01) |
|---|---|---|
| Product / Spec Lead | Anllelina | **Eliel** |
| Architecture / Development Lead | Angélica | **Anllelina** |
| QA / DevOps Lead | Eliel | **Angélica** |

La ejecución la hizo Claude Code a pedido de Anllelina, dejando cada paso en un commit separado
para que se vea el orden. Eliel y Angélica revisan y aprueban el PR según su rol.

## 2. Recorrido, de la especificación al resultado
| Paso | Qué se hizo | Archivos | Commit |
|---|---|---|---|
| 1. Especificación | BR-07 a 24 horas (reglas v1.1 con historial), RF-07 y AC-09 | `specs/business-rules.md`, `specs/requirements.md`, `specs/acceptance-criteria.md` | `c69236d` |
| 2. Plan y tareas | Sección "Ciclo 2 · CR-01" con las 5 tareas | `specs/implementation-plan.md` | `e5e1b72` |
| 3. Pruebas en rojo | Umbral de 24 horas en las pruebas de cancelación | `tests/test_reglas.py`, `tests/test_aceptacion.py`, `reservas/tests/test_mis_reservas.py`, `reservas/tests/test_notificaciones.py` | `9902780` |
| 4. Código | `HORAS_MIN_CANCELACION = 24` y textos de la app | `reservas/services/reservas.py`, `mis_reservas.html`, `reservar.html` | `e589f88` |
| 5. Resultados | Pruebas en verde y documentación | este archivo, `docs/testing.md`, `README.md` | último commit del PR |

## 3. Pruebas antes de cambiar el código (rojo)
Con las pruebas ya actualizadas y el código todavía en 2 horas:

```text
> python manage.py test tests.test_reglas tests.test_aceptacion reservas.tests.test_mis_reservas reservas.tests.test_notificaciones

FAIL: test_br07_un_segundo_fuera_de_plazo (tests.test_reglas.ReglasTests)
AssertionError: CancelacionNoPermitida not raised
FAIL: test_ac09_menos_de_24_horas_no_cancela (tests.test_aceptacion.AceptacionTests)
AssertionError: False is not true : Couldn't find '24 horas' in the following response
FAIL: test_cancelacion_fuera_de_plazo (reservas.tests.test_mis_reservas.MisReservasTests)
AssertionError: 'cancelada' != Booking.Status.CONFIRMADA
Ran 45 tests in 104.590s
FAILED (failures=3)
```

Las tres fallas son las esperadas: el código aún dejaba cancelar con menos de 24 horas.

## 4. Pruebas después de cambiar el código (verde)
```text
> python manage.py test
Ran 185 tests in 282.879s
OK
```

## 5. Resultado para el usuario
- En **Mis reservas** y en la reserva paso a paso, la app indica que se puede cancelar hasta 24 horas antes.
- Si el cliente intenta cancelar con menos de 24 horas, la reserva sigue confirmada y ve el mensaje
  "Solo se puede cancelar con al menos 24 horas de anticipación."
- La regla se valida en el servidor (RNF-02), no solo en la pantalla.
