# Arquitectura y diseño técnico

## Vista lógica

```mermaid
flowchart LR
  A[CSV / registros sintéticos] --> B[ETL Python + Pandas]
  B --> C[(PostgreSQL)]
  C --> D[FastAPI REST]
  D --> E[React]
  E --> F[Recharts / KPIs / tablas]
  F --> G[Análisis gerencial]
```

## Responsabilidades

- **Frontend React:** navegación, filtros, tarjetas KPI, tablas y gráficos responsive. No contiene fórmulas analíticas autoritativas.
- **FastAPI:** valida parámetros, coordina consultas y expone contratos JSON.
- **Pandas:** normaliza series temporales y procesa el archivo CSV de socios; informa duplicados y filas inválidas.
- **PostgreSQL:** persiste socios, membresías, asistencias, pagos y eventos de membresía con claves foráneas.

## Modelo relacional simplificado

```mermaid
erDiagram
  SOCIO ||--o{ MEMBRESIA : contrata
  SOCIO ||--o{ ASISTENCIA : registra
  SOCIO ||--o{ PAGO : realiza
  MEMBRESIA ||--o{ PAGO : relaciona
  MEMBRESIA ||--o{ EVENTO_MEMBRESIA : genera
  SOCIO {
    bigint id_socio PK
    varchar nombre
    varchar apellido
    varchar email UK
    date fecha_alta
    varchar estado
  }
  MEMBRESIA {
    bigint id_membresia PK
    bigint id_socio FK
    varchar plan
    date fecha_inicio
    date fecha_vencimiento
    numeric importe
    varchar estado
  }
  ASISTENCIA {
    bigint id_asistencia PK
    bigint id_socio FK
    date fecha
    time hora
    varchar actividad
  }
  PAGO {
    bigint id_pago PK
    bigint id_socio FK
    bigint id_membresia FK
    date fecha
    numeric importe
    varchar estado
  }
  EVENTO_MEMBRESIA {
    bigint id_evento PK
    bigint id_membresia FK
    timestamp fecha
    varchar tipo_evento
  }
```

## Flujo de consulta

1. Gerencia selecciona un período en el frontend.
2. React envía las fechas a `GET /api/dashboard`.
3. FastAPI valida que la fecha inicial no supere la final.
4. SQL calcula conteos y sumas sobre PostgreSQL; Pandas completa la serie temporal diaria.
5. La API devuelve un JSON único para tarjetas y gráficos.
6. React representa los resultados con Recharts.

## Seguridad pendiente para producción

El documento académico contempla RBAC, hash de credenciales Argon2id, HTTPS/TLS, variables de entorno y respaldos. Esta entrega ejecutable implementa la separación de capas y utiliza variables de entorno para la conexión, pero no incluye todavía un módulo de autenticación/RBAC ni despliegue TLS. No se debe considerar lista para producción.
