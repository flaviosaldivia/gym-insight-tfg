from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import date, timedelta
from pathlib import Path
import os
import pandas as pd, io
from .database import Base, engine, get_db
from .models import Socio, Membresia, Asistencia, Pago
from .schemas import SocioOut, MembresiaOut
from .analytics import dashboard

app = FastAPI(title="Gym Insight API", version="1.0.0", description="API de indicadores gerenciales para gimnasios convencionales")
allowed_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/api/health")
def health(): return {"status":"ok", "service":"Gym Insight API"}

@app.get("/api/dashboard")
def get_dashboard(start: date | None = None, end: date | None = None, db: Session = Depends(get_db)):
    end = end or date.today(); start = start or (end - timedelta(days=29))
    if start > end: raise HTTPException(400, "La fecha inicial no puede ser posterior a la fecha final")
    return dashboard(db,start,end)

@app.get("/api/socios", response_model=list[SocioOut])
def socios(q: str = "", estado: str = "todos", limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Socio)
    if q: query=query.filter(or_(Socio.nombre.ilike(f"%{q}%"),Socio.apellido.ilike(f"%{q}%"),Socio.email.ilike(f"%{q}%")))
    if estado != "todos": query=query.filter(Socio.estado==estado)
    return query.order_by(Socio.apellido, Socio.nombre).limit(min(limit,500)).all()

@app.get("/api/membresias", response_model=list[MembresiaOut])
def membresias(estado: str = "todas", db: Session = Depends(get_db)):
    query=db.query(Membresia)
    if estado != "todas": query=query.filter(Membresia.estado==estado)
    return query.order_by(Membresia.fecha_vencimiento).limit(300).all()

@app.get("/api/alertas")
def alertas(db: Session = Depends(get_db)):
    today=date.today(); limit=today+timedelta(days=30)
    exp=db.query(Membresia,Socio).join(Socio).filter(Membresia.estado=="vigente",Membresia.fecha_vencimiento.between(today,limit)).order_by(Membresia.fecha_vencimiento).all()
    return [{"id":m.id_membresia,"socio":f"{s.nombre} {s.apellido}","plan":m.plan,"vence":m.fecha_vencimiento.isoformat(),"dias":(m.fecha_vencimiento-today).days} for m,s in exp]

@app.post("/api/importar")
async def importar(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Solo se admiten archivos CSV")
    try: df=pd.read_csv(io.BytesIO(await file.read()))
    except Exception as exc: raise HTTPException(400,f"No se pudo leer el CSV: {exc}")
    required={"nombre","apellido","email","fecha_alta"}
    missing=sorted(required-set(df.columns))
    if missing: raise HTTPException(400,"Faltan columnas obligatorias: "+", ".join(missing))
    report={"total":len(df),"validos":0,"duplicados":0,"invalidos":0,"errores":[]}
    seen=set()
    existing_emails={email for (email,) in db.query(Socio.email).all()}
    for idx,row in df.iterrows():
        nombre = "" if pd.isna(row.get("nombre")) else str(row.get("nombre")).strip()
        apellido = "" if pd.isna(row.get("apellido")) else str(row.get("apellido")).strip()
        email = "" if pd.isna(row.get("email")) else str(row.get("email")).strip().lower()
        if not nombre or not apellido or not email or "@" not in email:
            report["invalidos"]+=1
            report["errores"].append({"fila":int(idx)+2,"motivo":"Nombre, apellido o email inválido/incompleto"})
            continue
        if email in seen or email in existing_emails:
            report["duplicados"]+=1
            continue
        fecha=pd.to_datetime(row.get("fecha_alta"),errors="coerce")
        if pd.isna(fecha):
            report["invalidos"]+=1
            report["errores"].append({"fila":int(idx)+2,"motivo":"Fecha de alta inválida"})
            continue
        telefono = None if pd.isna(row.get("telefono")) else str(row.get("telefono")).strip()[:30]
        estado = "activo" if pd.isna(row.get("estado")) else str(row.get("estado")).strip().lower()
        if estado not in {"activo", "inactivo"}:
            estado = "activo"
        db.add(Socio(nombre=nombre[:80],apellido=apellido[:80],email=email[:160],telefono=telefono,fecha_alta=fecha.date(),estado=estado))
        seen.add(email)
        report["validos"]+=1
    db.commit()
    return report
