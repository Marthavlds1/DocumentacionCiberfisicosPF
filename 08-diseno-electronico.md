---
layout: default
title: Diseño Electrónico
nav_order: 9
---

# Diseño Electrónico

## Arquitectura electrónica general

El sistema electrónico se organiza en tres capas:

1. **Sensado** — detección del estado físico de la prenda en la línea
2. **Control industrial** — PLC Micro850 gestiona motor, sensores y actuadores
3. **Actuación periférica** — ESP32 controla pistón y torreta; UR3 plancha

---

## Sensores

| Sensor | Tipo | Posición | Función | Dirección PLC |
| :--- | :--- | :--- | :--- | :--- |
| **S1** | Barrera infrarroja | Entrada de banda | Detecta presencia de prenda al iniciar el proceso | `000004` |
| **S2** | Inductivo | Estación UR3 | Confirma posición de la prenda bajo el robot | `000005` |
| **S3** | Inductivo | Estación de salida | Marca fin del proceso — activa pistón | `000006` |

### S1 — Sensor de barrera infrarroja
Sensor fotoeléctrico de barrera (emisor/receptor) ubicado en la entrada de la banda transportadora. Cuando la prenda interrumpe el haz de luz infrarroja, el PLC recibe la señal en la dirección `000004` y activa el motor de la banda.

### S2 y S3 — Sensores inductivos
Sensores de proximidad inductivos que detectan la presencia de material metálico (estructura de la banda o porta-prenda). Se utilizan para posicionar la prenda en la estación de planchado (S2) y en la estación de salida (S3).

{: .note }
El sistema implementa un **filtro de debounce** con 3 lecturas consecutivas en 50 ms para cada sensor, eliminando falsas detecciones por ruido eléctrico o rebotes mecánicos.

---

## PLC Allen Bradley Micro850

| Parámetro | Valor |
| :--- | :--- |
| Modelo | Allen Bradley Micro850 |
| Software de programación | Connected Components Workbench (CCW) |
| Protocolo de comunicación | Modbus TCP |
| IP en red local | `192.168.3.151` |
| Puerto Modbus | `502` |
| Unit ID | `1` |
| Entradas digitales | S1 (`000004`), S2 (`000005`), S3 (`000006`) |
| Salidas digitales | Motor START (`000001`), Motor STOP (`000002`), Dirección FWD (`000003`), Plancha (`000007`) |

### Mapa de direcciones Modbus (offset base 0)

```python
COIL_CMD_START      = 0   # 000001 — Arrancar motor
COIL_CMD_STOP       = 1   # 000002 — Parar motor
COIL_CMD_DIR_FWD    = 2   # 000003 — Dirección hacia adelante
SENSOR1_ADDRESS     = 3   # 000004 — Sensor barrera IR (entrada)
SENSOR2_ADDRESS     = 4   # 000005 — Sensor inductivo (posición UR3)
SENSOR3_ADDRESS     = 5   # 000006 — Sensor inductivo (salida)
SALIDA_AUX_PLANCHA  = 6   # 000007 — Activar/desactivar plancha
```

---

## Actuadores

| Actuador | Control | Dirección | Función |
| :--- | :--- | :--- | :--- |
| Motor de banda | PLC Micro850 | `000001/002/003` | Arranque, paro y dirección de la banda transportadora |
| Plancha eléctrica | PLC Micro850 | `000007` | Activación de la resistencia calefactora |
| Robot UR3 | URScript + Modbus | `192.168.3.71:30002` | Ejecución de trayectorias de planchado |
| Pistón eléctrico | ESP32 vía serial | `COM3` | Empuja la prenda hacia el gancho de salida |
| Torreta luminosa | ESP32 vía serial | `COM3` | Señalización visual del estado del sistema |

---

## ESP32 — Periféricos de salida

| Parámetro | Valor |
| :--- | :--- |
| Microcontrolador | ESP32 |
| Comunicación | Serial USB / 115200 baud |
| Puerto serial | `COM3` |
| Controla | Pistón eléctrico + Torreta LED |
| Tiempo de activación del pistón | 9 segundos extendido |
| Timeout serial | 1 segundo |

---

## Raspberry Pi 3 — Nodo de cámara e IA

Una segunda Raspberry Pi 3 opera como **nodo independiente de cámara e inteligencia artificial**:

| Parámetro | Valor |
| :--- | :--- |
| IP en red local | `192.168.3.162` |
| Puerto Flask | `5000` |
| Función | Captura fotográfica + clasificación IA |
| Modelo IA | `keras_model.h5` (Keras/TensorFlow) |
| Tamaño de imagen al modelo | 224 × 224 px |
| Clases | `0 Camisa` / `1 Playera` |

---

## Siguiente sección

[Control y Programación](09-control-programacion.md)
