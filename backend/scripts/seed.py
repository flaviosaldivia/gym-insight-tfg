import os, sys, random
from datetime import date, datetime, timedelta, time
from decimal import Decimal
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import Base, engine, SessionLocal
from app.models import Socio, Membresia, Asistencia, Pago, EventoMembresia

Base.metadata.create_all(bind=engine)
db=SessionLocal()
if db.query(Socio).count():
    print("La base ya contiene datos. No se duplicó la carga inicial."); db.close(); raise SystemExit
random.seed(42)
today=date.today(); plans=[("Plan mensual",28000), ("Plan trimestral",72000), ("Plan libre",35000)]
for i in range(1,121):
    joined=today-timedelta(days=random.randint(30,540))
    s=Socio(nombre=random.choice(["Lucía","Mateo","Sofía","Benjamín","Valentina","Joaquín","Camila","Tomás","Martina","Santiago","Agustina","Nicolás"]),apellido=random.choice(["Gómez","Pérez","Rodríguez","López","Fernández","Martínez","Díaz","Romero","Torres","Álvarez"]),email=f"socio{i:03d}@demo.gym",telefono=f"+54 9 297 {random.randint(1000000,9999999)}",fecha_alta=joined,estado="activo")
    db.add(s); db.flush()
    plan,price=random.choice(plans); duration=30 if plan=="Plan mensual" else 90
    start=joined; end=start+timedelta(days=duration)
    if end < today and random.random()<.20: status="vencida"
    elif random.random()<.06: status="cancelada"
    else: status="vigente"; end=max(end,today+timedelta(days=random.randint(1,90)))
    m=Membresia(id_socio=s.id_socio,plan=plan,fecha_inicio=start,fecha_vencimiento=end,estado=status,importe=Decimal(price)); db.add(m); db.flush()
    if random.random()<.78:
        db.add(Pago(id_socio=s.id_socio,id_membresia=m.id_membresia,fecha=max(start,today-timedelta(days=random.randint(0,180))),importe=Decimal(price),concepto=f"Abono {plan}",estado="cobrado"))
    if status == "cancelada":
        event_day = today - timedelta(days=random.randint(1, 89))
        db.add(EventoMembresia(id_membresia=m.id_membresia, fecha=datetime.combine(event_day, time(12, 0)), tipo_evento="baja", motivo="Baja voluntaria"))
    elif random.random() < 0.22:
        event_day = today - timedelta(days=random.randint(1, 180))
        db.add(EventoMembresia(id_membresia=m.id_membresia, fecha=datetime.combine(event_day, time(12, 0)), tipo_evento="renovacion", motivo="Renovación de membresía"))
    # Attendance history: distributed over the last 90 days, weighted toward recent days.
    count=random.randint(3,26)
    for j in range(count):
        d=today-timedelta(days=random.randint(0,89))
        db.add(Asistencia(id_socio=s.id_socio,fecha=d,hora=time(random.randint(7,21),random.choice([0,15,30,45])),actividad=random.choice(["Musculación","Funcional","Spinning","GAP"])))
db.commit(); print("Datos sintéticos cargados: 120 socios y registros relacionados."); db.close()
