from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TripStatus(str, enum.Enum):
    searching    = "searching"
    offered      = "offered"
    accepted     = "accepted"
    driver_en_route = "driver_en_route"
    arrived      = "arrived"
    onboard      = "onboard"
    in_progress  = "in_progress"
    completed    = "completed"
    cancelled    = "cancelled"

class PaymentMethod(str, enum.Enum):
    cash         = "cash"
    transfer     = "transfer"
    pago_movil   = "pago_movil"

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Origen
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    origin_address = Column(String(255), nullable=False)

    # Destino
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    dest_address = Column(String(255), nullable=False)

    # Estado y pago
    status = Column(Enum(TripStatus), default=TripStatus.searching, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.cash)
    fare = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    duration_min = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancel_reason = Column(Text, nullable=True)

    # Relaciones
    passenger = relationship("User", foreign_keys=[passenger_id])
    driver = relationship("User", foreign_keys=[driver_id])

    def __repr__(self):
        return f"<Trip {self.id} - {self.status}>"