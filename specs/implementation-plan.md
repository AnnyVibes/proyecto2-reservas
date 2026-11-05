# Plan de implementación · Proyecto 2

Fecha de actualización: 2026-11-05. Método: outcomes (ODD) → especificaciones
(SDD) → implementación → pruebas → revisión. Este documento describe la cadena
ejecutada; no reemplaza las especificaciones funcionales ni técnicas de sus autores.

## Cadena, responsables y dependencias

| Paso | Persona / rol | Trabajo y archivos | Dependencia | Evidencia |
|---|---|---|---|---|
| #1 | Anllelina · Product / Spec Lead | Outcomes, requisitos, reglas, criterios, front público y registro | Base Proyecto 1 | PR #4 integrado; issue #1 cerrado |
| #2 | Angélica · Architecture / Development Lead | Arquitectura, datos, API, regla de solapes y KPIs staff | #1 integrado | PR #5 integrado; issue #2 cerrado |
| #3 | Eliel · QA / DevOps Lead | `tests/`, workflow, plan, guía de pruebas, README y registro de IA | #2 integrado | PR #8 integrado; issue #3 cerrado |

La rama del paso 3 parte de `main` en `6d25eb4`, que también contiene el PR #7
(validación del admin, issue #6). El código de la app y las 138 pruebas heredadas
se mantienen sin modificaciones. El paso 3 aporta 47 pruebas, para 185 en total.

## Tareas trazables

| Tarea | Outcome / requisito / regla | Validación |
|---|---|---|
| Mostrar canchas, mes y horas libres | O3 · RF-01, RF-03 · AC-01 | `tests/test_aceptacion.py::test_ac01_visitante_ve_cancha_y_disponibilidad`; navegador con datos demo |
| Pedir sesión al confirmar y volver a la cancha | O2 · RF-04 · BR-06 · AC-02 | `test_ac02_confirmacion_exige_sesion_y_login_vuelve_a_cancha`; navegador |
| Crear cuenta y rechazar entradas inválidas o duplicadas | O4 · RF-02 · BR-09 · AC-03/04/05 | `tests/test_usuarios.py` y casos AC-03/04/05 |
| Impedir cruces; permitir contigüidad y canchas distintas | O1 · RF-06 · BR-01 · AC-06 | `tests/test_doble_reserva.py`, servicio y API |
| Liberar una reserva cancelada | O1/O2 · RF-06/07 · BR-01/07 · AC-07/09 | Doble reserva, reglas y casos AC-07/09 |
| Validar horario, futuro, orden y repetición atómica | O1 · BR-02/03/04/05 · AC-08 | `tests/test_reglas.py` y recurrencia con conflicto en semana 3 |
| Pago simulado consistente y sin efectos tras rechazo | O2 · RF-05 · BR-08 | `test_br08_rechazo_revierte_todo`; suite heredada de pagos |
| Mostrar KPIs del rango y cancha solo a staff | O5 · RF-08 · AC-10 | `test_ac10_panel_filtra_kpis_por_cancha_y_rango`; `reservas/tests/test_kpis.py` |
| Automatizar la validación y documentar el proceso | RF-09 · RNF-02 | `.github/workflows/tests.yml`, `docs/testing.md`, logs y decisiones |

## Orden de cierre

1. Confirmar prerrequisito #2 y ejecutar línea base.
2. Agregar las pruebas de Eliel sin cambiar código ni tests de otros responsables.
3. Ante un error real nuevo: conservar una regresión con `expectedFailure`,
   explicar BR/AC afectado y reportarlo en #3; la corrección corresponde al dueño.
4. Ejecutar suite completa antes de cada commit, publicar la rama y abrir PR con `Closes #3`.
5. Verificar CI en Python 3.12, adjuntar evidencia y pedir revisión a Eliel.
6. Eliel revisa y decide el merge; al integrarse se cierra #3.
7. El siguiente ciclo empieza con `.github/ISSUE_TEMPLATE/cambio-de-requisito.md`,
   actualización previa de `specs/` y roles rotados. Hace falta definir el cambio
   concreto con el equipo; no se inventa un requisito para anticipar ese ciclo.

## Límites de la evidencia

Las pruebas HTTP no ejecutan JavaScript; la comprobación de navegador de AC-01/02
se informa por separado. Los tests secuenciales no demuestran exclusión concurrente
de intervalos en SQLite: se conserva el límite ya descrito en `architecture.md`.
La decisión humana de aceptar el trabajo y la revisión del PR no se atribuyen al agente.
