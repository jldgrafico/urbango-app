from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.driver import DriverProfile
from app.websocket.manager import manager
from app.auth import decode_token
import json

router = APIRouter()

@router.websocket("/ws/driver/{driver_id}")
async def driver_websocket(
    websocket: WebSocket,
    driver_id: int,
    db: Session = Depends(get_db)
):
    await manager.connect_driver(driver_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Actualizar ubicación del conductor en BD
            if payload.get("type") == "location_update":
                lat = payload.get("lat")
                lng = payload.get("lng")

                profile = db.query(DriverProfile).filter(
                    DriverProfile.user_id == driver_id
                ).first()

                if profile:
                    profile.current_lat = lat
                    profile.current_lng = lng
                    profile.is_online = True
                    db.commit()

                # Transmitir ubicación a pasajeros
                await manager.broadcast_driver_location(driver_id, lat, lng)

                # Confirmar al conductor
                await manager.send_to_driver(driver_id, {
                    "type": "location_confirmed",
                    "lat": lat,
                    "lng": lng
                })

    except WebSocketDisconnect:
        manager.disconnect_driver(driver_id)
        # Marcar conductor como offline
        profile = db.query(DriverProfile).filter(
            DriverProfile.user_id == driver_id
        ).first()
        if profile:
            profile.is_online = False
            db.commit()

@router.websocket("/ws/passenger/{passenger_id}")
async def passenger_websocket(
    websocket: WebSocket,
    passenger_id: int
):
    await manager.connect_passenger(passenger_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # El pasajero puede enviar mensajes al conductor
            if payload.get("type") == "message_to_driver":
                driver_id = payload.get("driver_id")
                await manager.send_to_driver(driver_id, {
                    "type": "passenger_message",
                    "passenger_id": passenger_id,
                    "message": payload.get("message")
                })

    except WebSocketDisconnect:
        manager.disconnect_passenger(passenger_id)