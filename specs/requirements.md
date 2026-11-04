# Requisitos (Fase 2 — SDD)

Versión 1.0 · Responsable: Anllelina Varcasia · Deriva de `outcomes.md`.

## Funcionales
| ID | Requisito | Outcome | Responsable |
|---|---|---|---|
| RF-01 | Ver las canchas con su deporte, descripción y precio por hora, sin iniciar sesión. | O3 | Anllelina |
| RF-02 | Crear una cuenta con usuario, nombre, correo y contraseña, con validaciones (BR-09). | O4 | Anllelina |
| RF-03 | Reservar paso a paso: elegir un día disponible del mes, ver sus horarios libres y confirmar uno. | O2, O3 | Anllelina |
| RF-04 | Pedir inicio de sesión solo al confirmar, y volver a la misma cancha después. | O2 | Anllelina |
| RF-05 | Pagar la reserva con el pago simulado, con tarjeta nueva o guardada. | O2 | Base Proyecto 1 |
| RF-06 | Impedir reservas que se solapen con otra reserva activa o con un bloqueo (BR-01). | O1 | Angélica |
| RF-07 | Ver y cancelar las propias reservas según BR-07. | O2 | Base Proyecto 1 |
| RF-08 | Panel de administración con KPIs de ocupación, ingresos, cancelaciones, horas pico, canchas más usadas y clientes nuevos. | O5 | Angélica |
| RF-09 | Pruebas automatizadas de reglas críticas, validaciones de usuario y criterios de aceptación, con CI. | O1–O4 | Eliel |

## No funcionales
| ID | Requisito |
|---|---|
| RNF-01 | El diseño se adapta a celular (desde 375 px) y a escritorio. |
| RNF-02 | Toda regla de negocio se valida en el servidor, aunque el front ya la muestre. |
| RNF-03 | Nunca se guarda el número completo de la tarjeta ni el CVV. |
| RNF-04 | Las imágenes del sitio son propias (SVG), sin derechos de terceros. |
| RNF-05 | Las fechas se manejan con la zona horaria del sistema (America/Panama). |
