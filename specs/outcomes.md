# Outcomes (Fase 1 — ODD)

Responsable del ciclo 1: Anllelina Varcasia (Product / Spec Lead).

## Contexto
Complejo deportivo con canchas de fútbol, pádel, tenis y baloncesto que se alquilan por horas.
Partimos del gestor de reservas del Proyecto 1 (base indicada por el profesor).

## Problema
Los clientes piden la cancha por WhatsApp o por teléfono. El personal anota a mano, responde
tarde fuera de horario y a veces asigna el mismo horario a dos equipos. El cliente no sabe qué
horas quedan libres hasta que alguien le contesta, y el administrador no tiene datos para saber
qué horarios y canchas rinden más.

## Outcome buscado
Que un cliente encuentre y confirme un horario libre por su cuenta, en menos de un minuto y sin
cruces de horario, y que el administrador vea en un panel cómo se usan las canchas.

## Resultados medibles
| ID | Resultado para el usuario | Indicador | Meta |
|---|---|---|---|
| O1 | Cero cruces de horario | Reservas activas que se solapan en la misma cancha | 0 |
| O2 | Reservar sin ayuda del personal | Pasos desde elegir la cancha hasta confirmar | 3: día, hora y confirmar |
| O3 | Saber al instante qué hay libre | Días y horas libres visibles antes de iniciar sesión | Sí |
| O4 | Crear cuenta sin fricción | Errores de registro explicados campo por campo | Sí |
| O5 | Decidir con datos | KPIs de ocupación, ingresos y cancelaciones en el panel | Paso 2 (Angélica) |

## Preguntas de valor
- ¿Qué resultado quiere el cliente? Jugar en el horario que le conviene, con la seguridad de que nadie más tiene esa cancha.
- ¿Qué le cuesta hoy? Esperar respuesta, preguntar varias veces y llegar a una cancha ocupada.
- ¿Qué necesita ver para decidir? Los días con espacio, las horas libres y el precio, en una sola pantalla.
- ¿Qué no debe pasar nunca? Dos reservas activas en la misma cancha y a la misma hora.
- ¿Qué quiere el administrador? Saber qué horas y canchas se llenan, cuánto se ingresa y cuántas reservas se cancelan.
- ¿Cómo sabremos que funcionó? Por los indicadores O1 a O5 y las pruebas de `acceptance-criteria.md`.

## Fuera de alcance de este proyecto
Pagos reales, notificaciones por WhatsApp, aplicación móvil nativa y varias sedes.
