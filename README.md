# 🚗 UrbanGo

Aplicación de transporte tipo ride-hailing desarrollada para el mercado venezolano. Construida con **FastAPI + PostgreSQL** en el backend y **Capacitor + Vanilla JS** en el frontend, compilada como APK nativo para Android.

---

## 🧱 Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + PostgreSQL |
| Frontend | Vanilla JS + HTML/CSS |
| Mobile | Capacitor (Android APK) |
| Mapas | Google Maps Platform |
| Tiempo real | WebSockets |
| Despliegue | DigitalOcean (Ubuntu) |
| Proceso | Systemd |

---

## 📁 Estructura del proyecto

```
urbango-app/
├── src/
│   ├── index.html              ← Entry point (Capacitor)
│   ├── shared/                 ← Recursos compartidos
│   ├── passenger/              ← Vistas del pasajero
│   │   ├── home.html
│   │   ├── login.html
│   │   └── register.html
│   └── driver/                 ← Vistas del conductor
│       └── home.html
├── urbango-api/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── auth.py
│       ├── dependencies.py
│       ├── models/
│       │   ├── user.py
│       │   ├── driver.py
│       │   └── trip.py
│       ├── routes/
│       │   ├── auth.py
│       │   ├── drivers.py
│       │   └── trips.py
│       └── websocket/
└── android/                    ← Proyecto Android (Capacitor)
```

---

## ⚙️ Requisitos previos

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Java 21 (para compilar APK)
- Android SDK
- Cuenta de Google Maps Platform (API Key)

---

## 🚀 Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone git@github.com:jldgrafico/urbango-app.git
cd urbango-app
```

### 2. Configurar el backend

```bash
cd urbango-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crear el archivo `.env` en `urbango-api/`:

```env
DATABASE_URL=postgresql://usuario:password@localhost/urbango_db
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. Crear la base de datos

```bash
sudo -u postgres psql
CREATE DATABASE urbango_db;
CREATE USER appuser WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE urbango_db TO appuser;
\q
```

Inicializar las tablas:

```bash
cd urbango-api
python3 -c "from app.database import Base, engine; from app.models import user, driver, trip; Base.metadata.create_all(bind=engine)"
```

### 4. Levantar el backend

```bash
cd urbango-api
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

La API estará disponible en `http://localhost:8001`  
Documentación automática: `http://localhost:8001/docs`

### 5. Configurar Google Maps API Key

En `src/passenger/home.html` y `src/driver/home.html`, reemplaza:

```javascript
key=TU_API_KEY_AQUI
```

con tu API Key de Google Maps Platform.

### 6. Compilar el APK Android

```bash
npm install
npx cap sync android
cd android
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
./gradlew assembleDebug --max-workers=2
```

El APK estará en:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

### 7. Instalar en dispositivo Android

```bash
adb devices                          # Ver dispositivos conectados
adb -s <DEVICE_ID> install app/build/outputs/apk/debug/app-debug.apk
```

---

## 🌐 Despliegue en producción (DigitalOcean)

### Configurar Nginx

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Configurar Systemd

```ini
# /etc/systemd/system/urbango.service
[Unit]
Description=UrbanGo API
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/urbango-app/urbango-api
ExecStart=/var/www/urbango-app/urbango-api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable urbango
systemctl start urbango
```

---

## 👥 Roles de usuario

| Rol | Descripción |
|---|---|
| `passenger` | Solicita viajes, ve conductor en tiempo real |
| `driver` | Acepta viajes, comparte ubicación en tiempo real |

---

## 📡 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` | Registro de usuario |
| POST | `/auth/login` | Login, retorna JWT |
| GET | `/drivers/available` | Conductores disponibles |
| POST | `/trips/` | Solicitar viaje |
| PATCH | `/trips/{id}/status` | Actualizar estado del viaje |
| WS | `/ws/driver/{id}` | WebSocket del conductor |
| WS | `/ws/passenger/{id}` | WebSocket del pasajero |

---

## 📱 Dispositivos probados

| Dispositivo | Chipset | Estado |
|---|---|---|
| Motorola Edge 60 Fusion | MediaTek | ✅ |
| Yezz Art 3 | MediaTek | ✅ |
| Redmi 15C | MediaTek | ✅ |
| Samsung Galaxy A32 | MediaTek | ✅ |

---

## 🔑 Variables de entorno requeridas

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL de conexión PostgreSQL |
| `SECRET_KEY` | Clave para firmar JWT |
| `ALGORITHM` | Algoritmo JWT (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token |

---

## 📝 Notas importantes

- El proyecto usa **WebSockets** para ubicación en tiempo real — asegúrate de que Nginx tenga el proxy WebSocket configurado correctamente.
- En dispositivos **MediaTek**, el GPS puede tener restricciones de `stationary throttling`. El proyecto usa `watchPosition` para el conductor que funciona correctamente.
- Para HTTPS en producción se recomienda **Let's Encrypt** con Certbot.

---

## 👨‍💻 Desarrollado por

José León — [@jldgrafico](https://github.com/jldgrafico)
