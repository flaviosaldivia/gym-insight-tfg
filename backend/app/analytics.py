from datetime import date, timedelta
from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session
from .models import Socio, Membresia, Asistencia, Pago, EventoMembresia
import pandas as pd


def dashboard(db: Session, start: date, end: date):
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - (end - start)
    active = db.query(func.count(distinct(Membresia.id_socio))).filter(Membresia.estado == "vigente", Membresia.fecha_inicio <= end, Membresia.fecha_vencimiento >= end).scalar() or 0
    prev_active = db.query(func.count(distinct(Membresia.id_socio))).filter(Membresia.estado == "vigente", Membresia.fecha_inicio <= prev_end, Membresia.fecha_vencimiento >= prev_end).scalar() or 0
    new_members = db.query(func.count(Socio.id_socio)).filter(Socio.fecha_alta.between(start,end)).scalar() or 0
    cancellations = db.query(func.count(EventoMembresia.id_evento)).filter(EventoMembresia.tipo_evento == "baja", func.date(EventoMembresia.fecha).between(start, end)).scalar() or 0
    attendance = db.query(func.count(Asistencia.id_asistencia)).filter(Asistencia.fecha.between(start,end)).scalar() or 0
    revenue = db.query(func.coalesce(func.sum(Pago.importe),0)).filter(Pago.fecha.between(start,end), Pago.estado == "cobrado").scalar() or 0
    renewals = db.query(func.count(EventoMembresia.id_evento)).filter(EventoMembresia.tipo_evento == "renovacion", func.date(EventoMembresia.fecha).between(start, end)).scalar() or 0
    expiring = db.query(func.count(Membresia.id_membresia)).filter(Membresia.estado == "vigente", Membresia.fecha_vencimiento.between(end, end + timedelta(days=30))).scalar() or 0
    prev_revenue = db.query(func.coalesce(func.sum(Pago.importe),0)).filter(Pago.fecha.between(prev_start,prev_end), Pago.estado == "cobrado").scalar() or 0
    # Aggregate in SQL; Pandas is used to normalize the daily series before returning it.
    rows = db.query(Asistencia.fecha, func.count(Asistencia.id_asistencia)).filter(Asistencia.fecha.between(start,end)).group_by(Asistencia.fecha).order_by(Asistencia.fecha).all()
    daily = pd.DataFrame(rows, columns=["fecha", "asistencias"])
    if not daily.empty:
        daily["fecha"] = pd.to_datetime(daily["fecha"])
        daily = daily.set_index("fecha").asfreq("D", fill_value=0).rename_axis("fecha").reset_index()
        attendance_series = [{"date": x.strftime("%d/%m"), "value": int(y)} for x,y in zip(daily.fecha, daily.asistencias)]
    else:
        attendance_series = []
    rev_rows = db.query(Pago.fecha, func.sum(Pago.importe)).filter(Pago.fecha.between(start,end), Pago.estado == "cobrado").group_by(Pago.fecha).order_by(Pago.fecha).all()
    rev = pd.DataFrame(rev_rows, columns=["fecha", "importe"])
    if not rev.empty:
        rev["fecha"] = pd.to_datetime(rev["fecha"])
        rev = rev.set_index("fecha").asfreq("D", fill_value=0).rename_axis("fecha").reset_index()
        revenue_series = [{"date": x.strftime("%d/%m"), "value": float(y)} for x,y in zip(rev.fecha, rev.importe)]
    else: revenue_series=[]
    monthly = db.query(func.to_char(Pago.fecha, 'YYYY-MM'), func.sum(Pago.importe)).filter(Pago.fecha >= start - timedelta(days=180), Pago.fecha <= end, Pago.estado == "cobrado").group_by(func.to_char(Pago.fecha, 'YYYY-MM')).order_by(func.to_char(Pago.fecha, 'YYYY-MM')).all()
    return {
      "period":{"from":start.isoformat(),"to":end.isoformat()},
      "kpis":{"active_members":active,"active_change":active-prev_active,"new_members":new_members,"cancellations":cancellations,"attendance":attendance,"revenue":float(revenue),"revenue_change": round(((float(revenue)-float(prev_revenue))/float(prev_revenue))*100,1) if float(prev_revenue) else 0,"renewals":renewals,"expiring_30d":expiring},
      "attendance_series":attendance_series,"revenue_series":revenue_series,
      "monthly_revenue":[{"month":m,"value":float(v or 0)} for m,v in monthly]
    }
