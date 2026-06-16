# TaskFlow — Gestión de Proyectos y Tareas

Aplicación web Full Stack desarrollada con **Django** (backend) y **React** (frontend parcial).  
Proyecto Final del Máster en Desarrollo Full Stack — ConquerX / ConquerBlocks.

🌐 **Aplicación desplegada:** https://taskflow-production-96f8.up.railway.app

---

## Descripción

TaskFlow es una plataforma de gestión de proyectos y tareas colaborativa. Permite a equipos
organizar su trabajo, crear proyectos, asignar tareas a miembros y hacer seguimiento del
progreso en tiempo real.

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Django 4.2, Python 3.10+ |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Frontend | Django Templates + React 18 (CDN) |
| Estilos | Bootstrap 5.3 |
| Autenticación | Django Auth (sesiones) |

## Roles de usuario

- **Administrador** — Acceso total al panel de administración y todos los proyectos
- **Project Lead** — Crea y gestiona proyectos propios, asigna tareas
- **Miembro** — Trabaja en tareas asignadas, añade comentarios
- **Visitante** — Solo puede ver proyectos públicos

---

## Instalación y puesta en marcha

### Requisitos previos
- Python 3.10 o superior instalado
- pip actualizado

### Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/RubenMC-44/Taskflow.git
cd taskflow

# 2. Crea y activa el entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Aplica las migraciones
python manage.py migrate

# 5. Crea un superusuario (administrador)
python manage.py createsuperuser

# 6. Arranca el servidor de desarrollo
python manage.py runserver
```

---

## Estructura del proyecto

```
taskflow/
├── manage.py
├── requirements.txt
├── taskflow/           # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/           # App de autenticación y perfiles
│   ├── models.py       # UserProfile
│   ├── views.py        # Login, registro, perfil
│   └── forms.py
├── core/               # App principal
│   ├── models.py       # Project, ProjectMember, Task, Comment
│   ├── views.py        # CRUD de proyectos y tareas
│   ├── api.py          # Endpoints JSON para React
│   └── forms.py
├── templates/          # Plantillas HTML
│   ├── base.html
│   ├── accounts/
│   └── core/           # Incluye vistas con componentes React
└── static/
    └── css/style.css
```

---

## Vistas con React

La aplicación incluye dos vistas con componentes React que consumen datos del backend:

1. **Dashboard** (`/dashboard/`) — Estadísticas de tareas en tiempo real con filtros dinámicos
2. **Listado de Proyectos** (`/projects/`) — Búsqueda y filtrado de proyectos en tiempo real

Ambos componentes se comunican con los endpoints `/api/dashboard/` y `/api/projects/`
mediante `fetch()` con el token CSRF de Django.

---

## Seguridad

- Autenticación por sesión con Django Auth
- Protección CSRF en todos los formularios y llamadas AJAX
- Contraseñas hasheadas con PBKDF2 (por defecto en Django)
- Control de acceso por decoradores (`@login_required`, comprobación de roles)
- Validación de formularios en servidor

---

## Endpoints API (React)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/dashboard/` | Estadísticas y tareas recientes del usuario |
| GET | `/api/projects/` | Proyectos del usuario (`?search=` / `?status=`) |
| GET | `/api/projects/<id>/tasks/` | Tareas de un proyecto (`?status=` / `?priority=`) |

---

## Panel de administración

Accesible en `/admin/` con un superusuario. Permite gestionar usuarios, proyectos y tareas directamente desde la interfaz de Django Admin.

---

## Despliegue

La aplicación está desplegada y accesible públicamente en:

**https://taskflow-production-96f8.up.railway.app**

Desplegada en **Railway** con PostgreSQL como base de datos de producción.

### Variables de entorno necesarias en producción

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `False` en producción |
| `ALLOWED_HOSTS` | Dominio de la aplicación |
| `DATABASE_URL` | URL de conexión a PostgreSQL |

### Pasos para redesplegar

```bash
# 1. Configura las variables de entorno en Railway
# 2. Conecta el repositorio GitHub
# 3. Railway detecta automáticamente Python y ejecuta:
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn taskflow.wsgi
```
