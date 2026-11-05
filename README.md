# Proyecto 2 · Golazo Reservas

Sistema de reservas de canchas de fútbol, pádel, tenis y baloncesto, continuación
del Proyecto 1 indicado por el profesor. El cliente consulta disponibilidad sin
sesión, elige día y hora y confirma con pago simulado. El administrador consulta
ocupación, ingresos, cancelaciones, horas pico, ranking y clientes nuevos.

## Método y equipo

El proceso sigue **ODD → SDD → código → pruebas**: primero se definen los outcomes,
luego requisitos, reglas y criterios, y después arquitectura, implementación y validación.

| Paso | Persona | Rol / responsabilidad |
|---|---|---|
| #1 | Anllelina Varcasia · `AnnyVibes` | Product / Spec Lead: outcomes, especificación funcional y front |
| #2 | Angélica Rodríguez · `rodriguezac` | Architecture / Development Lead: arquitectura, reservas y KPIs |
| #3 | Eliel Garcia · `notSoEliel` | QA / DevOps Lead: pruebas, CI y documentación de entrega |

Cada paso parte del anterior integrado en `main`; los archivos tienen responsables
en [CODEOWNERS](.github/CODEOWNERS). La integración del paso 3 requiere revisión
de Eliel. El siguiente ciclo usa la [plantilla de cambio de requisito](.github/ISSUE_TEMPLATE/cambio-de-requisito.md)
y roles rotados.

## Tecnología y funcionalidades

Python 3.12 o superior, Django 5.2.18, SQLite, plantillas Django, Tailwind por CDN,
FullCalendar 6.1.11 y Chart.js 4.4.1. Dependencias fijadas en `requirements.txt`.

- Registro con validaciones, inicio de sesión y retorno a la cancha.
- Reserva en tres pasos, calendario mensual y horas libres; día completo si está libre.
- Horario 09:00–21:00, bloqueos, cancelación con al menos 24 horas (cambio de requisito CR-01, ver [docs/cambio-requisito-cr01.md](docs/cambio-requisito-cr01.md)) y hasta 12 semanas adicionales.
- Reserva/pago y repeticiones atómicos. Tarjetas simuladas: solo se guardan titular,
  marca, últimos cuatro dígitos, vencimiento y token, nunca PAN completo ni CVV.
- Mis reservas, Mis tarjetas, correos en consola y panel histórico de demanda.
- KPIs filtrados por fecha y cancha en `/panel/`, solo para staff activo.
- 185 pruebas, incluidas 47 del paso 3; CI en Ubuntu con Python 3.12.

## Instalación local

Requisitos: Git, Python 3.12+ y acceso al repositorio. Cada persona utiliza su propia
cuenta e identidad de Git. La BD y `venv/` no se versionan.

### Windows · PowerShell

```powershell
git clone https://github.com/AnnyVibes/proyecto2-reservas.git
cd proyecto2-reservas
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata pistas
python manage.py crear_reservas_demo
python manage.py createsuperuser
python manage.py runserver
```

Si la política local impide activar el entorno, se puede usar directamente
`.\venv\Scripts\python.exe` en lugar de `python` en los comandos siguientes a `venv`.

### Windows · Git Bash

```bash
git clone https://github.com/AnnyVibes/proyecto2-reservas.git
cd proyecto2-reservas
py -3.12 -m venv venv
source venv/Scripts/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata pistas
python manage.py crear_reservas_demo
python manage.py createsuperuser
python manage.py runserver
```

### macOS / Linux

```bash
git clone https://github.com/AnnyVibes/proyecto2-reservas.git
cd proyecto2-reservas
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata pistas
python manage.py crear_reservas_demo
python manage.py createsuperuser
python manage.py runserver
```

Abrir [la aplicación local](http://127.0.0.1:8000/). Para otro puerto:
`python manage.py runserver 8002` y abrir `http://127.0.0.1:8002/`.

## Datos de demostración y pago

`python manage.py crear_reservas_demo` crea `demo_user`, contraseña inicial
`demo1234`, y hasta 15 reservas futuras en pádel. Si el usuario ya existe no cambia
su contraseña; reemplaza solo sus reservas. No ejecutarlo contra datos que quieras
conservar de esa cuenta. Los tests generan datos separados y no necesitan este comando.

El administrador local se crea con `createsuperuser`; no hay credenciales de admin
universales ni incluidas en los fixtures.

| Tarjeta ficticia | Resultado |
|---|---|
| `4242 4242 4242 4242` | Aprobada |
| `4000 0000 0000 0002` | Rechazada; no persiste reserva ni pago |

Usar vencimiento futuro, titular no vacío y CVV ficticio de 3–4 dígitos.
El backend de correo predeterminado imprime en consola; no requiere SMTP real.
Para el panel de demanda se puede generar histórico local reproducible:

```bash
python manage.py generar_historico --semanas 26 --seed 42
```

## Pruebas y CI

```bash
python manage.py test
python manage.py test tests
python manage.py test tests.test_doble_reserva -v 2
```

El runner crea y destruye su BD temporal. El workflow
[Pruebas Django](.github/workflows/tests.yml) ejecuta la suite en cada push y PR a `main`.
Los resultados, evidencia de CI, matriz AC→test y comprobación de navegador se detallan
en [la guía de pruebas](docs/testing.md). La suite HTTP no ejecuta JavaScript.

## Estructura

```text
gestor_reservas/       Configuración Django
reservas/             Modelos, vistas, servicios, plantillas y recursos propios
reservas/tests/       Pruebas heredadas de los pasos anteriores
tests/                Pruebas de contrato y aceptación de Eliel
specs/                Outcomes, requisitos, reglas, aceptación, arquitectura y plan
docs/                 Pruebas, decisiones y registros de IA
.github/workflows/    Integración continua
.github/CODEOWNERS    Responsables por archivo
```

## Documentación

- [Outcomes](specs/outcomes.md), [requisitos](specs/requirements.md),
  [reglas de negocio](specs/business-rules.md) y [criterios de aceptación](specs/acceptance-criteria.md).
- [Arquitectura](specs/architecture.md), [modelo de datos](specs/data-model.md)
  y [contrato HTTP](specs/api.md).
- [Plan por persona y dependencias](specs/implementation-plan.md).
- [Pruebas, trazabilidad y CI](docs/testing.md).
- [Decisiones](docs/decisions.md) y registros de IA:
  [Anllelina](docs/ai-log/anllelina.md), [Angélica](docs/ai-log/angelica.md),
  [Eliel](docs/ai-log/eliel.md).

La base SQLite y las comprobaciones secuenciales no garantizan por sí solas exclusión
de intervalos ante peticiones concurrentes; el límite está explicado en arquitectura.
