---
layout: default
title: Control y Programación
nav_order: 10
---

# Control y Programación

## Capas de software del sistema

El sistema distribuye el control en cuatro capas de software que operan coordinadamente:

| Capa | Archivo | Tecnología | Función |
| :--- | :--- | :--- | :--- |
| Orquestador | `rutina_maestra.py` | Python / Raspberry Pi | Coordina todo el proceso |
| Control de campo | Proyecto CCW | PLC Micro850 / Ladder | Motor, sensores, plancha |
| Robótica | `camisa.script` / `playera.script` | URScript | Trayectorias UR3 |
| Periféricos | Firmware ESP32 | C++ / Arduino | Pistón + Torreta |

---

## rutina_maestra.py — Orquestador central

El archivo `rutina_maestra.py` es el **cerebro del sistema**. Implementa una máquina de estados explícita que coordina todos los subsistemas.

### Librerías principales

```python
from pymodbus.client import ModbusTcpClient  # Comunicación PLC y UR3
import requests                               # API REST → Render/Firebase
import serial                                 # Comunicación ESP32
import socket                                 # Envío scripts al UR3
import tf_keras as keras                      # Modelo IA de clasificación
from PIL import Image                         # Procesamiento de imagen
```

### Gestión de etapas

```python
def cambiar_etapa(nueva_etapa: str):
    global etapa_actual
    etapa_actual = nueva_etapa
    print(f"[ESTADO] Etapa actual -> {etapa_actual}")

def configurar_mascaras_sensores(s1: bool, s2: bool, s3: bool):
    global sensor1_habilitado, sensor2_habilitado, sensor3_habilitado
    sensor1_habilitado = s1
    sensor2_habilitado = s2
    sensor3_habilitado = s3
    print(f"[MASCARAS] S1={'ON' if s1 else 'OFF'} | S2={'ON' if s2 else 'OFF'} | S3={'ON' if s3 else 'OFF'}")
```

### Clasificación IA de prendas

```python
def clasificar_prenda(imagen_path):
    img = Image.open(imagen_path).resize((224, 224))
    data = np.array(img, dtype=np.float32) / 127.5 - 1
    prediction = modelo_prendas.predict(data[np.newaxis, ...])
    clase_idx = np.argmax(prediction)
    confianza  = prediction[0][clase_idx]
    return labels_prendas[clase_idx], confianza
    # Retorna: ("Camisa", 0.97) o ("Playera", 0.94)
```

### Envío de script URScript al robot

```python
def enviar_script_ur3(ruta_script: str):
    with open(ruta_script, "r") as f:
        script = f.read()
    sock = socket.socket()
    sock.connect((ROBOT_IP, ROBOT_PORT))   # 192.168.3.71:30002
    sock.sendall(script.encode())
    sock.close()
```

### Control del motor (PLC Micro850 vía pymodbus)

```python
def motor_start():
    with ModbusTcpClient(PLC_IP, port=PLC_PORT) as client:
        client.write_coil(COIL_CMD_DIR_FWD, True, slave=PLC_UNIT_ID)
        client.write_coil(COIL_CMD_START,   True, slave=PLC_UNIT_ID)
    print("[PLC] Motor iniciado")

def motor_stop():
    with ModbusTcpClient(PLC_IP, port=PLC_PORT) as client:
        client.write_coil(COIL_CMD_STOP, True, slave=PLC_UNIT_ID)
    print("[PLC] Motor detenido")
```

---

## URScript — Trayectorias del UR3

### camisa.script (resumen)

Rutina de planchado para camisas de vestir. Define 7 waypoints con movimientos `movej` + cinemática inversa (`get_inverse_kin`).

```
def camisa():
  set_tcp(p[0.0, 0.0, 0.0777, 0.0, 0.0, 0.0])
  set_payload(0.1, [0.0, 0.0, 0.08])
  set_tool_voltage(24)
  modbus_add_signal("192.168.3.71", 255, 129, 3, "RX74", False)
  modbus_add_signal("192.168.3.133", 255, 130, 3, "TX71", False)

  while (True):
    movej(get_inverse_kin(p[.062, .299, .603, -1.834, -.149, -.019], ...), a=1.396, v=1.047)
    movej(get_inverse_kin(p[.023, .321, .271, -1.863, -.037, .140], ...), a=1.396, v=1.047)
    movej(get_inverse_kin(p[.092, .279, .548, -1.786, -.042, -.080], ...), a=1.396, v=1.047)
    movej(get_inverse_kin(p[.083, .283, .262, -1.995, -.014, -.012], ...), a=1.396, v=1.047)
    movej(get_inverse_kin(p[.167, .265, .509, -1.935,  .245, -.242], ...), a=1.396, v=1.047)
    movej(get_inverse_kin(p[.183, .239, .233, -2.204,  .277, -.134], ...), a=1.396, v=1.047)
    movej(get_inverse_kin(p[.015, .272, .692, -1.570,  .003,  .159], ...), a=1.396, v=1.047)
  end
end
```

### playera.script (resumen)

Rutina análoga para playeras con waypoints re-calibrados para la geometría diferente de este tipo de prenda.

### Parámetros de movimiento

| Parámetro | Valor | Descripción |
| :--- | :--- | :--- |
| `a` | `1.3962 rad/s²` | Aceleración articular |
| `v` | `1.0471 rad/s` | Velocidad articular |
| TCP offset Z | `0.0777 m` | Distancia de la herramienta al flange |
| Payload | `0.1 kg` | Masa de la plancha |

---

## PLC Micro850 — Connected Components Workbench

La lógica del PLC fue desarrollada en **Connected Components Workbench (CCW)** de Rockwell Automation, utilizando lenguaje Ladder. Las funciones principales son:

- Arranque y paro del motor de la banda (con dirección)
- Lectura de los tres sensores digitales (S1, S2, S3)
- Activación de la salida `000007` para la plancha eléctrica
- Respuesta a los comandos Modbus TCP desde la Raspberry Pi

---

## Dashboard de monitoreo — dashboard_server.py

El archivo `dashboard_server.py` implementa un **servidor Flask con Server-Sent Events (SSE)** que permite monitorear la rutina maestra en tiempo real sin modificarla:

- Ejecuta `rutina_maestra.py` como subproceso.
- Lee su salida estándar e interpreta los `[ESTADO]`, `[PLC]`, `[IA]`, `[MASCARAS]` y `[PC]` tags.
- Emite el estado actualizado a todos los clientes web conectados vía SSE.
- Expone endpoints REST (`/api/status`, `/api/start`, `/events`).

---

## Siguiente sección

[IoT / Nube / Interfaz Web](10-iot-nube-interfaz.md)
