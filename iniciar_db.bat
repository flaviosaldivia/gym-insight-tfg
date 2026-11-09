@echo off
cd /d "%~dp0"
docker compose up -d postgres
if errorlevel 1 (echo No se pudo iniciar PostgreSQL. Verifique Docker Desktop.) else (echo PostgreSQL iniciado en localhost:5432.)
pause
