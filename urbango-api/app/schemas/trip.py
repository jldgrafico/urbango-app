from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.trip import TripStatus, PaymentMethod

class TripCreate(BaseModel):
    origin_lat: float
    origin_lng: float
    origin_address: str
    dest_lat: float
    dest_lng: float
    dest_address: str
    payment_method: PaymentMethod = PaymentMethod.cash

class TripResponse(BaseModel):
    id: int
    passenger_id: int
    driver_id: Optional[int] = None
    origin_lat: float
    origin_lng: float
    origin_address: str
    dest_lat: float
    dest_lng: float
    dest_address: str
    status: TripStatus
    payment_method: PaymentMethod
    fare: Optional[float] = None
    distance_km: Optional[float] = None
    duration_min: Optional[int] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TripStatusUpdate(BaseModel):
    status: TripStatus
    cancel_reason: Optional[str] = None