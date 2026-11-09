@echo off
cd /d "%~dp0backend"
if not exist .venv (py -3 -m venv .venv)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://gym_user:gym_password@localhost:5432/gym_bi
uvicorn app.main:app --reload
