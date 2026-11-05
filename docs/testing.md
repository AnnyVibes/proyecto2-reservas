# Pruebas y verificación · Proyecto 2

## Cómo ejecutar

Desde la raíz, con el entorno virtual activado y dependencias instaladas:

```bash
python manage.py test
python manage.py test tests
python manage.py test tests.test_doble_reserva -v 2
```

El runner crea una base SQLite de prueba temporal, aplica las migraciones y la
destruye al terminar. No requiere usuarios demo, un servidor activo ni credenciales
externas. Los pagos de los tests son simulados. No hay dependencias adicionales.

## Última ejecución local

2026-11-05 · Python 3.14.3 · Django 5.2.18 · macOS:

```text
Línea base de main (6d25eb4): 138 pruebas, OK
Suite con el paso 3:        185 pruebas, OK
Pruebas nuevas de Eliel:     47
Fallos esperados:             0
Pruebas omitidas:             0
```

Los nuevos escenarios congelan el reloj en junio de 2030 y construyen sus propios
usuarios, canchas y pagos; no envejecen según la fecha de la máquina. El vencimiento
de tarjeta de prueba es posterior al reloj fijado. Los tests de registro no dependen
de ese reloj y no usan tarjetas. Las 138 pruebas existentes permanecen intactas.

## Cobertura por archivo

| Archivo | Pruebas | Cobertura |
|---|---|---|
| `tests/test_doble_reserva.py` | 12 | BR-01, AC-06/07: misma cancha/franja; solapes en ambos sentidos y contención; adyacencia; otra cancha; cancelada; bloqueo; recurrencia atómica en servicio y API. Sin pagos ni tarjetas parciales tras 409. |
| `tests/test_reglas.py` | 13 | BR-02 a BR-08: límites 09/21, minuto fuera, pasado por un segundo, fin y fecha, 12 repeticiones (13 reservas), tipos inválidos, 401/403, umbral exacto de cancelación, propiedad y rechazo de pago. |
| `tests/test_usuarios.py` | 12 | BR-09: alta válida, normalización, hash, sesión, correo inválido/duplicado, usuario repetido, contraseñas distintas/corta/común/numérica/similar, nombre vacío y `next` externo en registro/login. |
| `tests/test_aceptacion.py` | 10 | Un escenario identificado por cada AC-01 a AC-10, con integración HTTP, servicios y persistencia. |
| `tests/helpers.py` | — | Reloj, datos y mixin compartidos; no importa clases de tests heredadas ni duplica su descubrimiento. |
| `reservas/tests/` | 138 | Suite heredada: pagos, correo, modelos, disponibilidad, KPIs, demanda, front, registro, reservas y admin. |

Las funciones puras de KPIs (`resumir_kpis`, `variacion`, `limites`) ya están
cubiertas en `reservas/tests/test_kpis.py::CalculoPuroTests`: datos vacíos, cambios
porcentuales, rangos inválidos, recorte y filtrado sin consultas. La disponibilidad
usa ORM y reloj, por lo que se prueba como servicio en
`reservas/tests/test_disponibilidad.py`, incluyendo pasado, hoy, canceladas,
bloqueos y rangos. No se afirma que sea una función pura.

## Matriz criterio → prueba del paso 3

Todos los casos de esta tabla pertenecen a `tests/test_aceptacion.py`.

| Criterio | Método de prueba |
|---|---|
| AC-01 | `test_ac01_visitante_ve_cancha_y_disponibilidad` |
| AC-02 | `test_ac02_confirmacion_exige_sesion_y_login_vuelve_a_cancha` |
| AC-03 | `test_ac03_registro_valido_inicia_sesion` |
| AC-04 | `test_ac04_datos_invalidos_no_crean_cuenta` |
| AC-05 | `test_ac05_usuario_y_correo_duplicados_rechazados` |
| AC-06 | `test_ac06_doble_reserva_api_409` + pruebas dedicadas en `test_doble_reserva.py` |
| AC-07 | `test_ac07_cancelar_y_reservar_misma_franja` |
| AC-08 | `test_ac08_horario_y_pasado_rechazados` |
| AC-09 | `test_ac09_menos_dos_horas_no_cancela` |
| AC-10 | `test_ac10_panel_filtra_kpis_por_cancha_y_rango` |

Las especificaciones originales conservan las etiquetas de pendiente redactadas
por sus responsables; esta matriz aporta la evidencia del paso 3 sin editar sus archivos.

## Verificación adicional de navegador por el agente

Realizada el 2026-11-05, en una BD local creada para este proyecto:

1. Fixture de cuatro canchas y comando `crear_reservas_demo` (15 reservas).
2. Visitante abre pádel, elige el 6 de noviembre: aparecen nueve horas libres y
   se omiten las ocupadas de 09, 11 y 13 h (AC-01).
3. Elige 10–11 h y pulsa Confirmar: llega a `/login/?next=%2Freservar%2F3%2F`.
4. Inicia sesión con `demo_user`: vuelve a la misma cancha (AC-02).
5. Selecciona 10–11 h, completa la tarjeta de prueba aprobada y confirma:
   se muestra «¡Reserva confirmada!», importe $10.00 y referencia de pago.
6. Se verifica en BD una reserva confirmada y un pago de $10.00 para esa referencia.
   La consola del navegador no registró errores ni advertencias.

Captura guardada localmente fuera del repositorio como `reserva-confirmada.png`.
Esta fue una comprobación de Codex; no se presenta como una prueba manual hecha
por Eliel ni como una suite E2E repetida automáticamente en CI.

Para repetir: ejecutar `migrate`, `loaddata pistas`, `crear_reservas_demo`,
`runserver` y seguir el flujo anterior con una fecha futura que tenga espacio.
El comando demo reemplaza solo las reservas de `demo_user`; usar una BD local.

## CI

Workflow: `.github/workflows/tests.yml`, nombre **Pruebas Django**.
Se ejecuta en cada push y en cada pull request hacia `main`, Ubuntu y Python 3.12.
Instala exclusivamente `requirements.txt` y ejecuta `python manage.py test`.
Permiso del workflow: lectura de contenidos; timeout: 10 minutos.

Primera ejecución remota verificada: [run 42083284757](https://github.com/AnnyVibes/proyecto2-reservas/actions/runs/42083284757),
evento push, commit `b8f52b1`, Ubuntu/Python 3.12, **185 pruebas, OK**
(2026-11-05; 66.728 s de tests). El workflow terminó en `success`.
El PR de entrega es [#8](https://github.com/AnnyVibes/proyecto2-reservas/pull/8);
los checks de su última revisión se consultan allí.

La primera ejecución advirtió que checkout v4 y setup-python v5 usaban Node 20
obsoleto. Se actualizaron a las versiones oficiales checkout v7.0.1 y
setup-python v7.1.0; la comprobación de la revisión final se realiza antes de
entregar el PR. No se cambió la versión de Python ni las dependencias de la app.

## Alcance y fallos conocidos

La suite añadida no descubrió fallos nuevos: no hay `expectedFailure` ni skips.
Si apareciera un fallo real en la app, se mantendría como regresión documentada,
se reportaría en #3 con su BR/AC y lo corregiría el responsable del archivo.
Los tests no prueban carreras simultáneas ni exclusión de intervalos concurrentes
por SQLite; ese límite sigue documentado en `specs/architecture.md`.

## Cambio de requisito CR-01 (issue #10)

BR-07 pasó de 2 a 24 horas de anticipación para cancelar. Pruebas actualizadas antes del código:
`tests/test_reglas.py` (umbral exacto de 24 horas y 24 horas menos un segundo),
`tests/test_aceptacion.py::test_ac09_menos_de_24_horas_no_cancela`,
`reservas/tests/test_mis_reservas.py` y `reservas/tests/test_notificaciones.py`.

| Momento | Resultado |
|---|---|
| Pruebas actualizadas, código en 2 horas | 45 pruebas, **3 fallas esperadas** |
| Código en 24 horas | **185 pruebas, OK** |

El recorrido completo, con la salida en rojo y en verde, está en
[docs/cambio-requisito-cr01.md](cambio-requisito-cr01.md).
