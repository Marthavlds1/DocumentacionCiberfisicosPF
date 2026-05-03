---
layout: default
title: Descripción Funcional
nav_order: 5
---

# Descripción Funcional del Sistema

## Resumen del proceso

El sistema opera de forma **completamente autónoma** una vez que el usuario registra su prenda en la interfaz web y la coloca en la entrada de la banda transportadora. El proceso completo incluye 8 etapas secuenciales gestionadas por la rutina maestra en Raspberry Pi.

---

## Etapas del proceso

### Etapa 1 — Registro de prenda en la interfaz web
El cliente accede a la plataforma web ([luiscortesmunoz.github.io/Planchaduria](https://luiscortesmunoz.github.io/Planchaduria/)), crea su cuenta con autenticación Firebase, selecciona el tipo de prenda, material y cantidad. El sistema genera automáticamente un **código QR único** vinculado al pedido, almacenado en Firebase Realtime Database.

### Etapa 2 — Validación del QR en el HMI
El cliente presenta su código QR frente a la cámara integrada en el **HMI físico** (Raspberry Pi 3 con pantalla táctil). El sistema valida el ID del pedido contra la base de datos Firebase. Al confirmar la validación, el HMI muestra el estado del pedido y el proceso físico queda habilitado para iniciar.

### Etapa 3 — Detección de prenda (Sensor S1 — barrera infrarroja)
El cliente coloca la prenda en la entrada de la banda transportadora. El **sensor de barrera infrarroja (S1)** detecta la presencia de la prenda al interrumpir el haz de luz. La señal llega al PLC Micro850 (dirección `000004`), que activa el motor de la banda.

| Parámetro | Valor |
| :--- | :--- |
| Tipo de sensor | Barrera infrarroja |
| Dirección PLC | `000004` |
| Etapa interna | `ESPERA_SENSOR1` |

### Etapa 4 — Avance y captura fotográfica con IA
La banda avanza durante **45 segundos** hasta la estación de fotografía. Una **Raspberry Pi 3 con cámara** captura una imagen de la prenda y ejecuta el modelo `keras_model.h5` (clasificador binario: Camisa / Playera, entrenado con Google Teachable Machine). El resultado y la fotografía se suben al backend en Render y quedan registrados en Firebase Storage como evidencia de recepción.

| Parámetro | Valor |
| :--- | :--- |
| Tiempo de avance previo | 45 segundos |
| Modelo IA | `keras_model.h5` — Keras / TensorFlow |
| Clases detectadas | `Camisa` / `Playera` |
| Etapa interna | `FOTO` |

### Etapa 5 — Planchado automatizado con UR3 (Sensor S2)
La banda avanza hasta que el **sensor inductivo S2** (dirección `000005`) detecta la prenda en posición de planchado. El PLC envía la señal al UR3 vía **Modbus TCP**. El robot ejecuta la rutina correspondiente al tipo de prenda:

- `camisa.script` — 7 waypoints para camisa de vestir
- `playera.script` — 7 waypoints para playera / camiseta

La plancha está montada en el efector final del UR3 mediante un agarrador impreso en **PLA**.

| Parámetro | Valor |
| :--- | :--- |
| Sensor de posición | Inductivo S2 — `000005` |
| Comunicación robot | Modbus TCP · IP `192.168.3.71` · Puerto `30002` |
| Señales | `RX74` (recepción) / `TX71` (transmisión) |
| Waypoints por rutina | 7 |
| Tiempo de rutina | ~15 segundos |
| Etapa interna | `UR3` |

### Etapa 6 — Salida y pistón (Sensor S3)
Finalizado el planchado, la banda avanza hasta el **sensor inductivo S3** (dirección `000006`), que marca el fin del proceso. El motor se detiene. El **ESP32** (conectado por serial a `COM3 / 115200 baud`) activa el **pistón eléctrico** durante 9 segundos, empujando la prenda hacia el gancho de salida para que el cliente la recoja.

| Parámetro | Valor |
| :--- | :--- |
| Sensor de salida | Inductivo S3 — `000006` |
| Actuador | Pistón eléctrico — ESP32 |
| Tiempo pistón extendido | 9 segundos |
| Avance final | 60 segundos |
| Etapa interna | `PISTON` → `AVANCE_FINAL_60S` |

### Etapa 7 — Finalización y trazabilidad en Firebase
El sistema actualiza el estado del pedido en Firebase como **"Listo para entrega"**. El dashboard web y el HMI reflejan la finalización. La fotografía de evidencia queda almacenada en Firebase Storage. El ciclo termina y el sistema retorna al estado de espera (`STOP`).

---

## Resumen de tiempos del proceso

| Etapa | Duración |
| :--- | :--- |
| Avance hasta estación de foto | 45 segundos |
| Captura y clasificación IA | ~3 segundos |
| Avance hasta posición UR3 | Variable (sensor S2) |
| Rutina de planchado UR3 | ~15 segundos |
| Avance hasta sensor S3 | Variable (sensor S3) |
| Extensión del pistón | 9 segundos |
| Avance final y paro | 60 segundos |

---

## Siguiente sección

[Algoritmo de Funcionamiento](05-algoritmo.md)
