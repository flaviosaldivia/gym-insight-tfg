from sqlalchemy import String, Date, DateTime, Time, ForeignKey, Numeric, BigInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Socio(Base):
    __tablename__ = "socio"
    id_socio: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    fecha_alta: Mapped[object] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="activo")
    membresias = relationship("Membresia", back_populates="socio", cascade="all, delete-orphan")
    asistencias = relationship("Asistencia", back_populates="socio", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="socio", cascade="all, delete-orphan")

class Membresia(Base):
    __tablename__ = "membresia"
    id_membresia: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_socio: Mapped[int] = mapped_column(ForeignKey("socio.id_socio", ondelete="CASCADE"), index=True)
    plan: Mapped[str] = mapped_column(String(80))
    fecha_inicio: Mapped[object] = mapped_column(Date)
    fecha_vencimiento: Mapped[object] = mapped_column(Date, index=True)
    estado: Mapped[str] = mapped_column(String(20), default="vigente")
    importe: Mapped[float] = mapped_column(Numeric(12,2))
    socio = relationship("Socio", back_populates="membresias")
    pagos = relationship("Pago", back_populates="membresia")

class Asistencia(Base):
    __tablename__ = "asistencia"
    id_asistencia: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_socio: Mapped[int] = mapped_column(ForeignKey("socio.id_socio", ondelete="CASCADE"), index=True)
    fecha: Mapped[object] = mapped_column(Date, index=True)
    hora: Mapped[object] = mapped_column(Time)
    actividad: Mapped[str] = mapped_column(String(80), default="Musculación")
    socio = relationship("Socio", back_populates="asistencias")

class Pago(Base):
    __tablename__ = "pago"
    id_pago: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_socio: Mapped[int] = mapped_column(ForeignKey("socio.id_socio", ondelete="CASCADE"), index=True)
    id_membresia: Mapped[int | None] = mapped_column(ForeignKey("membresia.id_membresia", ondelete="SET NULL"), nullable=True)
    fecha: Mapped[object] = mapped_column(Date, index=True)
    importe: Mapped[float] = mapped_column(Numeric(12,2))
    concepto: Mapped[str] = mapped_column(String(150))
    estado: Mapped[str] = mapped_column(String(20), default="cobrado")
    socio = relationship("Socio", back_populates="pagos")
    membresia = relationship("Membresia", back_populates="pagos")

class EventoMembresia(Base):
    __tablename__ = "evento_membresia"
    id_evento: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_membresia: Mapped[int] = mapped_column(ForeignKey("membresia.id_membresia", ondelete="CASCADE"), index=True)
    fecha: Mapped[object] = mapped_column(DateTime)
    tipo_evento: Mapped[str] = mapped_column(String(30))
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
