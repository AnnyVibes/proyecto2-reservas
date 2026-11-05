# Registro de IA · Eliel · Proyecto 2, paso 3

Fecha: 2026-11-05. Herramienta: Codex en la aplicación de escritorio. No se atribuye
un identificador de modelo que no se haya verificado.

Eliel pidió revisar exclusivamente el grupo de Tópicos y el chat de Anllelina y
completar lo solicitado para el nuevo proyecto usando su computadora. Codex leyó
ambos chats y el adjunto `prompt_codex_eliel.txt`; no revisó otros chats.
La aprobación del trabajo y el merge corresponden a Eliel.

| Actividad | IA utilizada | Solicitud | Resultado | Decisión |
|---|---|---|---|---|
| Identificar alcance | Codex | Revisar las instrucciones del nuevo proyecto como Eliel | Descargó el adjunto; identificó issue #3, pruebas/CI/docs y límites de archivos | Eliel autorizó realizar el trabajo; interpretación y ejecución técnica del agente |
| Preparación | Codex | Continuar después del paso 2 integrado | Verificó issue #2 cerrado y PR #5 en main; clonó main 6d25eb4 con PR #7; creó rama eliel/3-pruebas-ci y entorno; 138 pruebas base OK | Se respetó el orden indicado por el equipo |
| Pruebas dedicadas | Codex | Impedir doble reserva y cubrir reglas críticas | 12 tests de doble reserva y 13 de reglas: ambos lados del solape, contención, contiguas, otra cancha, cancelación, bloqueos, atomicidad y límites exactos | Diseño y redacción del agente; pendiente de revisión de Eliel |
| Usuarios y aceptación | Codex | Validaciones BR-09 y un escenario AC-01 a AC-10 | 12 tests de usuarios y 10 de aceptación; reloj fijo para escenarios temporales, sin modificar las 138 pruebas heredadas | Diseño del agente; pendiente de revisión de Eliel |
| Verificación local | Codex | Ejecutar python manage.py test y comprobar flujo real | 185 pruebas OK, sin skips ni expectedFailure. Navegador: visitante elige día/hora, Confirmar pide login, vuelve a la cancha, pago ficticio y reserva confirmados; BD con reserva y pago de $10.00; consola sin errores | Comprobación del agente; no se presenta como QA manual de Eliel |
| CI y documentación | Codex | Workflow Python 3.12, plan, matriz de tests y README | Workflow Ubuntu por push/PR a main; documentación ODD/SDD y trazabilidad, instalación PowerShell/Git Bash/macOS | Elaboración del agente dentro de archivos permitidos; revisión humana pendiente |
| Entrega | Codex | Push, PR con Closes #3 y CI verde | Rama y PR se publican al concluir, y se registra la evidencia remota en docs/testing.md | Eliel revisa y decide el merge; no se inventan aprobaciones humanas |

No se modifican `reservas/`, los tests existentes, requisitos ni especificaciones de
otros responsables. No se agregan dependencias. Los datos demo y la captura de
navegador son locales y no se incluyen en Git. La suite nueva no descubrió un fallo
nuevo de la aplicación, por lo que no se registran fallos esperados artificiales.
