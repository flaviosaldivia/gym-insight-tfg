# Gym Insight — Sistema de apoyo a decisiones gerenciales en gimnasios convencionales

Prototipo académico de Business Intelligence para integrar y analizar información operativa de un gimnasio convencional: socios, membresías, asistencias, renovaciones, bajas y pagos. Se implementa con **React, Python/FastAPI, PostgreSQL, Pandas y Recharts**.

> Los datos incluidos son sintéticos. Este prototipo no está preparado para almacenar datos personales reales ni para producción sin completar los controles de seguridad indicados en `docs/SEGURIDAD_Y_DESPLIEGUE.md`.

## 1. Funcionalidades

- Panel gerencial con socios activos, altas, bajas, asistencias, ingresos cobrados, renovaciones y membresías próximas a vencer.
- Filtros temporales de 7, 30, 90 y 180 días.
- Gráficos de actividad e ingresos con Recharts.
- Consulta y búsqueda de socios; consulta de membresías.
- Alertas de membresías con vencimiento próximo.
- Importación de socios desde CSV con Pandas: validación de columnas, normalización de correo, fechas y detección de duplicados.
- API REST con documentación interactiva.
- Carga de demostración reproducible (120 socios y registros relacionados).
- Ejecución local mediante Docker Compose y ejecución en GitHub Codespaces.
- Workflow de GitHub Actions para verificar sintaxis Python, pruebas ETL y compilación React.

## 2. Arquitectura

```text
React + Recharts (navegador)
          │ HTTP / JSON
          ▼
     FastAPI (Python)
          │
     Reglas de negocio
          │
  Pandas (ETL / series)
          │
          ▼
   PostgreSQL 16
```

- **React:** navegación, filtros, tarjetas KPI, tablas y presentación.
- **FastAPI:** endpoints REST, validación de parámetros y lógica de aplicación.
- **PostgreSQL:** persistencia relacional e integridad referencial.
- **Pandas:** limpieza, normalización y construcción de series temporales; también se usa en la importación CSV.
- **Recharts:** gráficos de área y barras en el frontend.

El modelo relacional contempla `socio`, `membresia`, `asistencia`, `pago` y `evento_membresia`, con relaciones 1:N y claves foráneas según el documento del proyecto.

## 3. Requisitos

### Opción recomendada (Docker)
- Git.
- Docker Desktop actualizado, con Docker Compose.

### Ejecución manual
- Python 3.11 o 3.12.
- Node.js 20 o 22 y npm.
- PostgreSQL 16.

## 4. Ejecución local con Docker (recomendada)

Desde la carpeta raíz del proyecto:

1. Copiar `.env.example` a `.env` (opcional para la configuración predeterminada).
2. Iniciar los servicios:

```bash
docker compose up --build -d
```

3. Esperar a que PostgreSQL esté saludable y el backend haya iniciado. Comprobar:

```text
http://localhost:8000/api/health
http://localhost:8000/docs
```

4. Cargar los datos sintéticos una sola vez:

```bash
docker compose --profile tools run --rm seed
```

5. Abrir el frontend:

```text
http://localhost:5173
```

El frontend usa el proxy de Vite para enviar `/api` al servicio FastAPI dentro de Docker. Para volver a iniciar el proyecto, normalmente basta con `docker compose up -d`.

### Detener y reiniciar

```bash
# Detener servicios sin borrar datos
docker compose down

# Iniciar nuevamente
docker compose up -d

# Eliminar también el volumen de PostgreSQL (BORRA los datos locales)
docker compose down -v
```

## 5. Ejecución local manual en Windows

Si no deseas ejecutar frontend y backend en Docker, puedes utilizar PostgreSQL local o mantener solamente PostgreSQL en Docker.

### 5.1 Base de datos

```powershell
docker compose up -d postgres
```

### 5.2 Backend

Abrir una terminal PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:DATABASE_URL="postgresql+psycopg://gym_user:gym_password@localhost:5432/gym_bi"
$env:FRONTEND_ORIGINS="http://localhost:5173"
uvicorn app.main:app --reload
```

Si PowerShell bloquea la activación del entorno virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

API: `http://localhost:8000`; documentación: `http://localhost:8000/docs`.

### 5.3 Datos sintéticos

En otra terminal, desde la raíz:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+psycopg://gym_user:gym_password@localhost:5432/gym_bi"
python scripts/seed.py
```

### 5.4 Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`. En ejecución manual Vite reenvía `/api` a `http://localhost:8000`.

## 6. Ejecutar en GitHub Codespaces

El repositorio incluye `.devcontainer/devcontainer.json` y Docker Compose para levantar PostgreSQL, FastAPI y React en Codespaces.

1. Crear una cuenta en [GitHub](https://github.com/) e iniciar sesión.
2. Crear un repositorio, por ejemplo `gym-insight-tfg`.
3. Subir el contenido completo de esta carpeta a la rama `main` (incluyendo `.devcontainer`, `.github`, Dockerfiles y `docker-compose.yml`). No subir `.env`, contraseñas ni datos reales.
4. Abrir el repositorio en GitHub.
5. Seleccionar **Code → Codespaces → Create codespace on main**.
6. Esperar que Codespaces construya el entorno según `.devcontainer/devcontainer.json`.
7. En la terminal de Codespaces, cargar los datos sintéticos desde el contenedor de desarrollo:

```bash
DATABASE_URL="postgresql+psycopg://gym_user:gym_password@postgres:5432/gym_bi" .venv/bin/python backend/scripts/seed.py
```

8. Abrir la pestaña **Ports**. El puerto `5173` corresponde al frontend y debe abrirse en el navegador; el puerto `8000` corresponde a la API.
9. Verificar `https://<tu-codespace>-8000.app.github.dev/api/health` o abrir el puerto 8000 desde **Ports** y agregar `/api/health`.

El contenedor `dev` incluye Node.js y Python; el contenedor `frontend` ejecuta Vite y el contenedor `backend` ejecuta FastAPI. La interfaz llama a `/api` en el mismo origen; el proxy de Vite dirige las solicitudes al servicio `backend` de Docker Compose. Esto evita tener que escribir manualmente la URL pública del puerto API.

> Codespaces es un entorno de desarrollo en la nube, no un alojamiento de producción permanente. Su disponibilidad, cuotas y facturación dependen de la cuenta y del uso. Para una publicación pública permanente se necesita desplegar frontend, backend y PostgreSQL en servicios de hosting independientes.

### Alternativa: GitHub Actions

El workflow `.github/workflows/ci.yml` se ejecuta al realizar `push` o abrir un `pull request` hacia `main`/`master`. Comprueba la compilación del frontend, la sintaxis del backend y las pruebas automatizadas de Pandas. Actions valida el código; no mantiene el sistema ejecutándose como servidor web.

## 7. Publicación pública desde GitHub

Para que cualquier persona pueda ingresar desde Internet, usar un hosting para cada capa:

- Frontend React: Vercel (raíz `frontend`, comando `npm run build`, salida `dist`). Variable `VITE_API_URL` con la URL pública del backend, sin `/api` al final.
- Backend FastAPI: Render (raíz `backend`, instalación `pip install -r requirements.txt`, inicio `uvicorn app.main:app --host 0.0.0.0 --port $PORT`). Variables `DATABASE_URL` y `FRONTEND_ORIGINS`.
- PostgreSQL: servicio administrado compatible con PostgreSQL 16. Configurar `DATABASE_URL` con el esquema `postgresql+psycopg://...` y SSL requerido por el proveedor.

Después de conocer el dominio de Vercel, establecerlo en `FRONTEND_ORIGINS` en el backend y volver a desplegar. Ejecutar la carga sintética una sola vez contra la base remota. Nunca incluir la cadena de conexión en el repositorio.

## 8. API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health` | Estado del servicio |
| GET | `/api/dashboard?start=AAAA-MM-DD&end=AAAA-MM-DD` | Indicadores y series del período |
| GET | `/api/socios?q=&estado=` | Búsqueda y listado de socios |
| GET | `/api/membresias?estado=` | Listado de membresías |
| GET | `/api/alertas` | Membresías próximas a vencer |
| POST | `/api/importar` | Importación CSV de socios |

## 9. Formato de importación CSV

Columnas obligatorias: `nombre,apellido,email,fecha_alta`. Columnas opcionales: `telefono,estado`.

```csv
nombre,apellido,email,fecha_alta,telefono,estado
Ana,Demo,ana.demo@gym.com,2026-01-10,+5492974000000,activo
```

La fecha debe expresarse preferentemente como `AAAA-MM-DD`. La API informa cantidad de registros válidos, duplicados e inválidos. La importación actual está enfocada en socios; no importa asistencias, pagos ni membresías.

## 10. Definición de indicadores y límites

- **Socios activos:** socios únicos con membresía en estado `vigente`, cuyo inicio es anterior o igual a la fecha final y cuyo vencimiento es posterior o igual a esa fecha.
- **Altas:** socios cuya fecha de alta está dentro del período seleccionado.
- **Bajas:** eventos `baja` registrados en `evento_membresia` cuya fecha corresponde al período seleccionado.
- **Asistencias:** cantidad de registros válidos dentro del período.
- **Renovaciones:** eventos `renovacion` registrados en `evento_membresia` dentro del período. El denominador de una tasa de renovación requiere identificar previamente las membresías vencidas susceptibles de renovación; no se presenta una tasa hasta contar con esa regla de negocio validada.
- **Membresías por vencer:** membresías vigentes con vencimiento entre la fecha final seleccionada y los 30 días posteriores.
- **Ingresos cobrados:** suma de pagos con estado `cobrado` dentro del período.
- **Variación de ingresos:** comparación porcentual contra el período inmediatamente anterior de igual duración.

Los valores de prueba son sintéticos. Los resultados no representan mediciones de un gimnasio real ni prueban mejoras en retención o rentabilidad.

## 11. Estructura

```text
.
├── .devcontainer/             # Configuración de GitHub Codespaces
├── .github/workflows/         # CI con GitHub Actions
├── backend/
│   ├── app/                   # API, modelos, acceso a datos e indicadores
│   ├── scripts/seed.py        # Carga de datos sintéticos
│   ├── tests/                 # Pruebas de transformaciones Pandas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/                   # React, Recharts y estilos
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js         # Proxy /api
├── docs/                      # Arquitectura, pruebas y despliegue
├── docker-compose.yml
└── README.md
```

## 12. Seguridad

Esta entrega es un prototipo académico. Antes de usar datos personales o exponerlo como sistema productivo se requiere, como mínimo: autenticación, autorización RBAC, gestión segura de secretos, HTTPS/TLS, protección de endpoints de importación, validación reforzada de archivos, auditoría, copias de seguridad, política de retención y pruebas de seguridad. Las credenciales predeterminadas de Docker son exclusivamente para desarrollo local.

## 13. Scripts de Windows heredados

Los archivos `.bat` permiten iniciar por separado PostgreSQL, backend, carga demo y frontend en Windows. Para una ejecución más simple y reproducible se recomienda Docker Compose, documentado en la sección 4.
