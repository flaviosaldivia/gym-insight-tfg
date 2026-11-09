# Seguridad y despliegue

## Estado de la entrega

El proyecto es un prototipo académico con datos sintéticos. No incorpora autenticación ni autorización por roles, auditoría de operaciones, protección de carga con límites avanzados ni un proceso formal de backups. No debe publicarse con datos personales reales.

## Variables sensibles

- `DATABASE_URL`: solo en variables privadas del proveedor de hosting o `.env` local ignorado por Git.
- `POSTGRES_PASSWORD`: cambiarla fuera de entornos descartables.
- `FRONTEND_ORIGINS`: dominios exactos autorizados para CORS.
- `VITE_API_URL`: URL pública del backend; es visible en el bundle del navegador y no debe contener secretos.

## Publicación sugerida

1. PostgreSQL administrado en proveedor compatible, con SSL y backups.
2. FastAPI en servicio Python que ejecute `uvicorn app.main:app --host 0.0.0.0 --port $PORT` desde `backend`.
3. React en hosting estático desde `frontend`, con `npm run build` y salida `dist`.
4. Configurar `VITE_API_URL` durante la compilación del frontend y `FRONTEND_ORIGINS` en backend.
5. Ejecutar seed solo una vez en la base de datos de demostración.
6. Probar `/api/health`, `/docs`, consultas del dashboard e importación CSV.

## Pendientes para producción

- Implementar autenticación y RBAC en todos los endpoints.
- Aplicar hash robusto de contraseñas (Argon2id o bcrypt) y políticas de sesión/token.
- Limitar tamaño y tipo de archivo CSV; validar contenido, filas y campos.
- Añadir auditoría de importaciones y cambios.
- Activar HTTPS/TLS y restringir orígenes CORS.
- Establecer backups automáticos y pruebas de restauración.
- Añadir migraciones de esquema (por ejemplo, Alembic), monitoreo y alertas.
- Revisar definiciones de renovación y baja con responsables del negocio.
