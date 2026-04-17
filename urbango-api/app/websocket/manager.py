from fastapi import WebSocket
from typing import Dict
import json

class ConnectionManager:
    def __init__(self):
        # Conductores conectados: {driver_id: websocket}
        self.drivers: Dict[int, WebSocket] = {}
        # Pasajeros conectados: {passenger_id: websocket}
        self.passengers: Dict[int, WebSocket] = {}

    async def connect_driver(self, driver_id: int, websocket: WebSocket):
        await websocket.accept()
        self.drivers[driver_id] = websocket
        print(f"Conductor {driver_id} conectado")

    async def connect_passenger(self, passenger_id: int, websocket: WebSocket):
        await websocket.accept()
        self.passengers[passenger_id] = websocket
        print(f"Pasajero {passenger_id} conectado")

    def disconnect_driver(self, driver_id: int):
        if driver_id in self.drivers:
            del self.drivers[driver_id]
            print(f"Conductor {driver_id} desconectado")

    def disconnect_passenger(self, passenger_id: int):
        if passenger_id in self.passengers:
            del self.passengers[passenger_id]
            print(f"Pasajero {passenger_id} desconectado")

    async def send_to_passenger(self, passenger_id: int, data: dict):
        if passenger_id in self.passengers:
            websocket = self.passengers[passenger_id]
            await websocket.send_text(json.dumps(data))

    async def send_to_driver(self, driver_id: int, data: dict):
        if driver_id in self.drivers:
            websocket = self.drivers[driver_id]
            await websocket.send_text(json.dumps(data))

    async def broadcast_driver_location(self, driver_id: int, lat: float, lng: float):
        data = {
            "type": "driver_location",
            "driver_id": driver_id,
            "lat": lat,
            "lng": lng
        }
        # Enviar a todos los pasajeros conectados
        for passenger_id, websocket in self.passengers.items():
            try:
                await websocket.send_text(json.dumps(data))
            except:
                pass

# Instancia global
manager = ConnectionManager()