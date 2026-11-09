@echo off
cd /d "%~dp0backend"
if not exist .venv (echo Primero ejecute iniciar_backend.bat para crear el entorno. & pause & exit /b 1)
call .venv\Scripts\activate.bat
set DATABASE_URL=postgresql+psycopg://gym_user:gym_password@localhost:5432/gym_bi
python scripts\seed.py
pause
