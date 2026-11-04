# Criterios de aceptación

Versión 1.0 · Responsable: Anllelina Varcasia. Cada criterio indica su requisito y su prueba;
Eliel completa en el paso 3 las pruebas marcadas como pendientes.

| ID | Requisito | Dado / cuando / entonces | Prueba |
|---|---|---|---|
| AC-01 | RF-01, RF-03 | Dado un visitante sin sesión, cuando abre una cancha, entonces ve el mes con los días disponibles y, al elegir uno, sus horarios libres. | `test_reservar.py` |
| AC-02 | RF-04 | Dado un visitante sin sesión, cuando pulsa Confirmar, entonces va al inicio de sesión y después vuelve a la misma cancha. | `test_reservar.py`, `test_login.py` |
| AC-03 | RF-02, BR-09 | Dados datos válidos, cuando se registra, entonces se crea la cuenta y queda con la sesión iniciada. | `test_registro.py` |
| AC-04 | RF-02, BR-09 | Dados un correo inválido, contraseñas distintas, una contraseña débil o un nombre vacío, cuando se registra, entonces ve el error y no se crea la cuenta. | `test_registro.py` |
| AC-05 | RF-02, BR-09 | Dado un usuario o un correo ya registrados, cuando se registra, entonces se rechaza. | `test_registro.py` |
| AC-06 | RF-06, BR-01 | Dada una reserva activa de 10:00 a 11:00, cuando otro usuario reserva esa cancha de 10:00 a 11:00, entonces recibe un error 409 y no se crea la reserva. | `test_api_crear_reserva.py`; prueba dedicada pendiente (Eliel) |
| AC-07 | RF-06, BR-01 | Dada una reserva cancelada, cuando alguien reserva esa misma franja, entonces se permite. | `test_mis_reservas.py` |
| AC-08 | BR-02, BR-03 | Dada una franja fuera de 09:00–21:00 o en el pasado, cuando se intenta reservar, entonces se rechaza. | `test_api_crear_reserva.py` |
| AC-09 | RF-07, BR-07 | Dada una reserva que empieza en menos de 2 horas, cuando el cliente intenta cancelarla, entonces se rechaza. | `test_mis_reservas.py` |
| AC-10 | RF-08 | Dado un administrador, cuando abre el panel, entonces ve los KPIs con datos del rango elegido. | Pendiente (Angélica) |
