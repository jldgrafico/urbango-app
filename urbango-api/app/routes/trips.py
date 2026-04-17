from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models.user import User
from app.models.trip import Trip, TripStatus
from app.models.driver import DriverProfile
from app.schemas.trip import TripCreate, TripResponse, TripStatusUpdate
from app.dependencies import get_current_user
from app.websocket.manager import manager
from datetime import datetime
from typing import List
import math

router = APIRouter(prefix="/trips", tags=["Viajes"])

def calculate_fare(distance_km: float) -> float:
    base_fare = 2.0
    per_km = 1.5
    return round(base_fare + (distance_km * per_km), 2)

def calculate_distance(lat1, lng1, lat2, lng2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 2)

@router.post("/request", response_model=TripResponse, status_code=201)
async def request_trip(
    trip_data: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que no tenga viaje activo
    active_trip = db.query(Trip).filter(
        and_(
            Trip.passenger_id == current_user.id,
            Trip.status.in_([
                TripStatus.searching,
                TripStatus.offered,
                TripStatus.accepted,
                TripStatus.driver_en_route,
                TripStatus.arrived,
                TripStatus.onboard,
                TripStatus.in_progress
            ])
        )
    ).first()

    if active_trip:
        raise HTTPException(status_code=400, detail="Ya tienes un viaje activo")

    # Calcular distancia y tarifa
    distance = calculate_distance(
        trip_data.origin_lat, trip_data.origin_lng,
        trip_data.dest_lat, trip_data.dest_lng
    )
    fare = calculate_fare(distance)

    # Crear viaje
    trip = Trip(
        passenger_id=current_user.id,
        origin_lat=trip_data.origin_lat,
        origin_lng=trip_data.origin_lng,
        origin_address=trip_data.origin_address,
        dest_lat=trip_data.dest_lat,
        dest_lng=trip_data.dest_lng,
        dest_address=trip_data.dest_address,
        payment_method=trip_data.payment_method,
        fare=fare,
        distance_km=distance,
        status=TripStatus.searching
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # Notificar conductores online via WebSocket
    await manager.notify_drivers({
        "type": "trip_request",
        "trip_id": trip.id,
        "passenger_id": current_user.id,
        "origin": trip_data.origin_address,
        "destination": trip_data.dest_address,
        "fare": fare,
        "distance_km": distance,
        "payment_method": trip_data.payment_method
    })

    return trip

@router.patch("/{trip_id}/status", response_model=TripResponse)
async def update_trip_status(
    trip_id: int,
    status_data: TripStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    # Actualizar estado
    trip.status = status_data.status

    if status_data.status == TripStatus.accepted:
        trip.driver_id = current_user.id
        trip.accepted_at = datetime.utcnow()

    elif status_data.status == TripStatus.completed:
        trip.completed_at = datetime.utcnow()

    elif status_data.status == TripStatus.cancelled:
        trip.cancelled_at = datetime.utcnow()
        trip.cancel_reason = status_data.cancel_reason

    db.commit()
    db.refresh(trip)

    # Notificar al pasajero el cambio de estado
    await manager.send_to_passenger(trip.passenger_id, {
        "type": "trip_status_update",
        "trip_id": trip.id,
        "status": status_data.status,
        "driver_id": trip.driver_id
    })

    return trip

@router.get("/my-trips", response_model=List[TripResponse])
def get_my_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trips = db.query(Trip).filter(
        Trip.passenger_id == current_user.id
    ).order_by(Trip.created_at.desc()).limit(20).all()
    return trips

@router.get("/active", response_model=TripResponse)
def get_active_trip(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(
        and_(
            Trip.passenger_id == current_user.id,
            Trip.status.notin_([TripStatus.completed, TripStatus.cancelled])
        )
    ).first()

    if not trip:
        raise HTTPException(status_code=404, detail="No tienes viaje activo")
    return trip