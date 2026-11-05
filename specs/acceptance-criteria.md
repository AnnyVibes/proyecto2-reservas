# Criterios de aceptación

Versión 1.0 · Responsable: Anllelina Varcasia. Cada criterio indica su requisito y sus pruebas.
Las pruebas de `reservas/tests/` se escribieron en los pasos 1 y 2; las de `tests/` las agregó
Eliel en el paso 3, con un caso por criterio en `tests/test_aceptacion.py` (`test_ac01_…` a `test_ac10_…`).

| ID | Requisito | Dado / cuando / entonces | Pruebas |
|---|---|---|---|
| AC-01 | RF-01, RF-03 | Dado un visitante sin sesión, cuando abre una cancha, entonces ve el mes con los días disponibles y, al elegir uno, sus horarios libres. | `reservas/tests/test_reservar.py`; `tests/test_aceptacion.py` |
| AC-02 | RF-04 | Dado un visitante sin sesión, cuando pulsa Confirmar, entonces va al inicio de sesión y después vuelve a la misma cancha. | `reservas/tests/test_reservar.py`, `reservas/tests/test_login.py`; `tests/test_aceptacion.py` |
| AC-03 | RF-02, BR-09 | Dados datos válidos, cuando se registra, entonces se crea la cuenta y queda con la sesión iniciada. | `reservas/tests/test_registro.py`; `tests/test_usuarios.py`, `tests/test_aceptacion.py` |
| AC-04 | RF-02, BR-09 | Dados un correo inválido, contraseñas distintas, una contraseña débil o un nombre vacío, cuando se registra, entonces ve el error y no se crea la cuenta. | `reservas/tests/test_registro.py`; `tests/test_usuarios.py`, `tests/test_aceptacion.py` |
| AC-05 | RF-02, BR-09 | Dado un usuario o un correo ya registrados, cuando se registra, entonces se rechaza. | `reservas/tests/test_registro.py`; `tests/test_usuarios.py`, `tests/test_aceptacion.py` |
| AC-06 | RF-06, BR-01 | Dada una reserva activa de 10:00 a 11:00, cuando otro usuario reserva esa cancha de 10:00 a 11:00, entonces recibe un error 409 y no se crea la reserva. | `reservas/tests/test_api_crear_reserva.py`, `reservas/tests/test_doble_reserva_admin.py`; `tests/test_doble_reserva.py` (prueba dedicada), `tests/test_aceptacion.py` |
| AC-07 | RF-06, BR-01 | Dada una reserva cancelada, cuando alguien reserva esa misma franja, entonces se permite. | `reservas/tests/test_mis_reservas.py`; `tests/test_doble_reserva.py`, `tests/test_aceptacion.py` |
| AC-08 | BR-02, BR-03 | Dada una franja fuera de 09:00–21:00 o en el pasado, cuando se intenta reservar, entonces se rechaza. | `reservas/tests/test_api_crear_reserva.py`; `tests/test_reglas.py`, `tests/test_aceptacion.py` |
| AC-09 | RF-07, BR-07 | Dada una reserva que empieza en menos de 2 horas, cuando el cliente intenta cancelarla, entonces se rechaza. | `reservas/tests/test_mis_reservas.py`; `tests/test_reglas.py`, `tests/test_aceptacion.py` |
| AC-10 | RF-08 | Dado un administrador, cuando abre el panel, entonces ve los KPIs con datos del rango elegido. | `reservas/tests/test_kpis.py` (paso 2); `tests/test_aceptacion.py` |

La matriz completa de criterio a prueba y la evidencia de la CI están en `docs/testing.md`.
