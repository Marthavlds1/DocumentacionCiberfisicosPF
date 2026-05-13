---
layout: default
title: Diseño Electrónico
nav_order: 9
---

# Diseño Electrónico

## Diagrama de cableado — Sistema de control mecatrónico

**PLC Allen Bradley Micro850 QWB · Driver TB6600 · Motor NEMA 17 · Sensores · Plancha 120 VAC**

![Diagrama de cableado — Sistema de control mecatrónico](assets/img/diagrama-cableado.png)

### Entradas del PLC (Inputs)

| Input | Componente | Tipo | Conexión |
| :---: | :--- | :--- | :--- |
| I0 | Sensor 1 — Cortina | Digital NPN | Señal (azul OUT) → I0 · Marrón (+) → +24 V · Negro → 0 V |
| I4 | Sensor 2 — Capacitivo | Digital NPN | Señal (azul OUT) → I4 · Marrón (+) → +24 V · Negro → 0 V |
| I5 | Sensor 3 — Capacitivo | Digital NPN | Señal (azul OUT) → I5 · Marrón (+) → +24 V · Negro → 0 V |
| COM | Tierra común entradas | — | Todas las COM de entradas → 0 V / GND |

### Salidas del PLC (Outputs)

| Output | Función | Destino | Observación |
| :---: | :--- | :--- | :--- |
| O0 | EN+ (Driver) | TB6600 — terminal EN+ | Habilita el driver del motor |
| O1 | PUL+ (Driver) | TB6600 — terminal PUL+ | Pulsos de paso del motor |
| O2 | DIR+ (Driver) | TB6600 — terminal DIR+ | Dirección de giro |
| O3 | Relevador (Plancha) | Bobina A1 del relevador 24 VDC | Activa la plancha 120 VAC al cerrar COM–NC |
| COM | Alimentación salidas | +24 VDC | Todas las COM de salidas → +24 V |

### Conexión Motor NEMA 17 → Driver TB6600

| Cable motor | Terminal driver | Color |
| :--- | :--- | :--- |
| B− | B− del TB6600 | Verde |
| B+ | B+ del TB6600 | Negro |
| A− | A− del TB6600 | Rojo |
| A+ | A+ del TB6600 | Azul |

### Conexión Driver TB6600 — Potencia y tierra

| Terminal driver | Conexión | Observación |
| :--- | :--- | :--- |
| VCC | +24 VDC | Alimentación del driver |
| GND | 0 V / GND | Retorno de potencia |
| EN− | Tierra común | Conectar a GND común del panel |
| DIR− | Tierra común | Conectar a GND común del panel |
| PUL− | Tierra común | Conectar a GND común del panel |

{: .note }
EN−, DIR− y PUL− deben conectarse a la misma barra de tierra común del panel de clemas.

### Relevador — Activación de la plancha 120 VAC

| Terminal | Conexión |
| :--- | :--- |
| A1 (bobina +) | Salida O3 del PLC |
| A2 (bobina −) | 0 V / GND |
| COM (contacto) | Fase 120 VAC (L) |
| NC (contacto) | Terminal de la plancha |

{: .warning }
La plancha opera a **120 VAC**. El relevador aísla el circuito de control (24 VDC) del circuito de potencia (120 VAC). El contacto NC se cierra cuando el relevador se energiza, activando la plancha.

### Notas generales del cableado

1. Todas las COM de entradas del PLC van a **0 V / GND**.
2. Todas las COM de salidas del PLC van a **+24 VDC**.
3. EN−, DIR− y PUL− del driver TB6600 conectados a **tierra común**.
4. El relevador energiza la plancha a vapor (120 VAC) al cerrar el contacto COM–NC.

---

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

## Recursos asociados

### motor_sensor.zip
Código del sistema embebido basado en ESP32 para el control de actuadores (pistón y torreta).

[Descargar motor_sensor.zip](assets/files/motor_sensor.zip){: .btn .btn-outline }

---

## Siguiente sección

[Control y Programación](09-control-programacion.md)