---
layout: default
title: Arquitectura Ciberfísica
nav_order: 7
---

# Arquitectura Ciberfísica

{: .highlight }
Esta es la sección más importante del proyecto. La arquitectura ciberfísica define cómo cada componente físico y digital se comunica, qué protocolo utiliza y cuál es su rol dentro del sistema integrado.

---

## Visión general

El sistema **Planchado Express** es un sistema ciberfísico (CPS) compuesto por **cinco capas de comunicación** que operan de forma simultánea y coordinada:

| Capa | Componentes | Protocolo |
| :--- | :--- | :--- |
| **Nube / Internet** | Firebase, Render (Flask), GitHub Pages | HTTPS / REST / Firebase SDK |
| **Coordinación local** | Raspberry Pi 3 (`rutina_maestra.py`) | Python / HTTP / Modbus / Serial |
| **HMI** | Raspberry Pi 3 + pantalla táctil + cámara QR | HTTPS → Firebase |
| **Control industrial** | PLC Allen Bradley Micro850 | Modbus TCP |
| **Robótica y periféricos** | UR3, ESP32, sensores, motor, pistón | Modbus TCP, Serial USB |

---

## Diagrama de arquitectura

```
  ┌────────────────────────────────────────────────────────┐
  │                   ☁  NUBE / INTERNET                   │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
  │  │   Firebase   │  │  Flask API   │  │ GitHub Pages │ │
  │  │  Realtime DB │  │ (Render/     │  │ Interfaz Web │ │
  │  │  Firestore   │  │  Docker)     │  │  (cliente)   │ │
  │  │  Auth+Storage│  │              │  │              │ │
  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘ │
  └─────────┼────────────────┼──────────────────────────── ┘
            │   HTTPS/SDK    │   HTTPS/REST
            ▼                ▼
  ┌─────────────────────────────────────────────────────┐
  │          🧠  RASPBERRY PI 3  (Orquestador)          │
  │              rutina_maestra.py                       │
  │              IP: 192.168.3.162                       │
  │                                                      │
  │  • Polling Firebase → detecta pedidos nuevos         │
  │  • Control PLC vía pymodbus (Modbus TCP)             │
  │  • Envío de scripts URScript al UR3 por socket TCP   │
  │  • Comunicación serial con ESP32 (pistón/torreta)    │
  │  • Solicitud de foto a Raspberry cámara (HTTP)       │
  │  • Clasificación IA con keras_model.h5               │
  └──────┬──────────────┬──────────────────┬────────────┘
         │              │                  │
    Modbus TCP     Modbus TCP         Serial USB
    192.168.3.151  192.168.3.71       COM3 / 115200
         │              │                  │
         ▼              ▼                  ▼
  ┌──────────┐   ┌──────────────┐   ┌──────────────┐
  │  PLC     │   │   UR3        │   │   ESP32      │
  │ Micro850 │   │   Robot      │   │              │
  │          │   │ Colaborativo │   │ Torreta LED  │
  │ Motor    │   │              │   │ Pistón       │
  │ Sensores │   │ camisa/      │   │ eléctrico    │
  │ Plancha  │   │ playera      │   │              │
  └──────────┘   └──────────────┘   └──────────────┘
       │
  Entradas/Salidas digitales
       │
  ┌────┴──────────────────────────────────────────────┐
  │              CAMPO — SENSORES / ACTUADORES         │
  │  [S1 Barrera IR] [S2 Inductivo] [S3 Inductivo]    │
  │  [Motor banda]   [Plancha eléctrica 000007]        │
  └───────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────┐
  │                🖥️  HMI                            │
  │        Raspberry Pi 3 + Pantalla táctil           │
  │        Cámara lectora de QR                       │
  │        Muestra estado del pedido en tiempo real   │
  │        Se conecta a Firebase vía HTTPS            │
  └──────────────────────────────────────────────────┘
```

---

## Protocolos de comunicación

### Modbus TCP — PLC Micro850

El PLC Allen Bradley Micro850 se comunica con la Raspberry Pi mediante **Modbus TCP**, utilizando la librería `pymodbus` en Python.

```python
PLC_IP      = "192.168.3.151"
PLC_PORT    = 502
PLC_UNIT_ID = 1

# Coils de salida (control)
COIL_CMD_START    = 0   # 000001 — Arrancar motor
COIL_CMD_STOP     = 1   # 000002 — Parar motor
COIL_CMD_DIR_FWD  = 2   # 000003 — Dirección adelante
SALIDA_AUX_PLANCHA = 6  # 000007 — Activar plancha

# Entradas digitales (lectura de sensores)
SENSOR1_ADDRESS = 3     # 000004 — Barrera IR
SENSOR2_ADDRESS = 4     # 000005 — Inductivo UR3
SENSOR3_ADDRESS = 5     # 000006 — Inductivo salida
```

### Modbus TCP — Robot UR3

El UR3 también utiliza Modbus TCP para comunicarse con la Raspberry Pi. Adicionalmente, los scripts URScript se envían directamente al robot mediante un **socket TCP** al puerto `30002`.

```python
ROBOT_IP   = "192.168.3.71"
ROBOT_PORT = 30002

# Señales Modbus del UR3 (definidas dentro del script URScript)
modbus_add_signal("192.168.3.71", 255, 129, 3, "RX74", False)
modbus_add_signal("192.168.3.133", 255, 130, 3, "TX71", False)
```

### HTTP REST — Raspberry Pi cámara

La Raspberry Pi orquestadora solicita la fotografía a la Raspberry Pi de cámara mediante una API Flask local:

```python
RASPBERRY_IP   = "192.168.3.162"
RASPBERRY_PORT = 5000
BASE_RPI       = f"http://{RASPBERRY_IP}:{RASPBERRY_PORT}"
```

### Serial USB — ESP32

El ESP32 recibe comandos de la Raspberry Pi mediante comunicación serial para controlar la **torreta de señalización** y el **pistón eléctrico**:

```python
ESP32_SERIAL_PORT = "COM3"
ESP32_BAUDRATE    = 115200
ESP32_TIMEOUT     = 1
```

### HTTPS/REST — Backend en Render (nube)

La rutina maestra se comunica con el backend Flask desplegado en Render para sincronizar el estado con Firebase y subir las fotografías de evidencia:

```python
RENDER_BASE_URL = "https://docker-planchaduria.onrender.com"
```

---

## Tabla de IPs y puertos del sistema

| Componente | IP / Puerto | Protocolo | Rol |
| :--- | :--- | :--- | :--- |
| PLC Micro850 | `192.168.3.151:502` | Modbus TCP | Control de campo |
| UR3 Robot | `192.168.3.71:30002` | Modbus TCP + Socket | Planchado |
| Raspberry Pi cámara | `192.168.3.162:5000` | HTTP REST | Captura IA |
| Backend Render | `docker-planchaduria.onrender.com` | HTTPS REST | API nube |
| Firebase | Firebase Admin SDK | HTTPS | DB + Auth + Storage |
| ESP32 | COM3 / 115200 baud | Serial USB | Pistón + Torreta |

---

## Rol de cada componente en el CPS

### Raspberry Pi 3 — Orquestador central
Es el **cerebro del sistema**. Ejecuta `rutina_maestra.py`, que coordina todos los demás componentes. Hace polling a Firebase para detectar pedidos, controla el PLC por Modbus, envía scripts al UR3, comanda el ESP32 por serial, solicita fotos a la Raspberry cámara y ejecuta el modelo de IA localmente.

### PLC Allen Bradley Micro850 — Control de campo
Gestiona los **actuadores físicos y los sensores** del proceso: enciende/apaga el motor de la banda, lee el estado de los tres sensores (S1, S2, S3) y activa la plancha eléctrica (salida `000007`). Es la interfaz entre el mundo digital y el mundo físico de la línea de producción.

### UR3 — Robot colaborativo de planchado
Ejecuta las **trayectorias de planchado** sobre la prenda, con 7 waypoints calibrados por tipo de prenda. Recibe la instrucción de inicio vía señal Modbus y el script URScript por socket TCP. Es el actuador de mayor valor en el sistema.

### ESP32 — Control periférico
Controla la **torreta de señalización LED** (indica el estado del sistema visualmente en planta) y el **pistón eléctrico** que empuja la prenda planchada hacia el gancho de salida. Se comunica con la Raspberry Pi por serial USB.

### HMI — Interfaz local de operación
Panel táctil con Raspberry Pi 3 que muestra el estado del pedido en tiempo real (consultando Firebase) y lee el código QR del cliente mediante cámara integrada para validar el inicio del proceso.

### Firebase — Capa de datos y sincronización
Base de datos y plataforma de autenticación en la nube. Almacena pedidos (Firestore), estado del proceso en tiempo real (Realtime Database), fotografías de evidencia (Storage) y gestiona la autenticación de usuarios (Auth).

### Interfaz web — Punto de contacto con el cliente
Aplicación web en GitHub Pages que permite al cliente registrar su prenda, obtener el QR, consultar el estado del pedido y ver el historial. Se comunica directamente con Firebase mediante el SDK de JavaScript.

---

## Siguiente sección

[Diseño Mecánico](07-diseno-mecanico.md)
