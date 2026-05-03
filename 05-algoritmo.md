---
layout: default
title: Algoritmo de Funcionamiento
nav_order: 6
---

# Algoritmo de Funcionamiento

## Lógica de control por etapas

El sistema utiliza una **máquina de estados explícita** implementada en `rutina_maestra.py`. Cada etapa se nombra con una clave única y el estado se actualiza mediante la función `cambiar_etapa()`, que imprime el estado para que el dashboard pueda interpretarlo en tiempo real.

```python
def cambiar_etapa(nueva_etapa: str):
    global etapa_actual
    etapa_actual = nueva_etapa
    print(f"[ESTADO] Etapa actual -> {etapa_actual}")
```

---

## Estados del sistema

| Clave de etapa | Descripción |
| :--- | :--- |
| `STOP` | Sistema en reposo, esperando pedido |
| `ESPERA_SENSOR1` | Esperando detección de prenda en entrada (barrera IR) |
| `AVANCE_45S_ANTES_FOTO` | Banda avanzando 45 seg hacia estación de fotografía |
| `FOTO` | Captura fotográfica y clasificación IA en curso |
| `AVANCE_A_SENSOR2` | Banda avanzando hacia posición de planchado (UR3) |
| `UR3` | Robot ejecutando rutina de planchado |
| `AVANCE_A_SENSOR3` | Banda avanzando hacia estación de salida |
| `PISTON` | Pistón eléctrico activo — empujando prenda al gancho |
| `AVANCE_FINAL_60S` | Avance final de 60 segundos antes del STOP |

---

## Diagrama de flujo

```
         ┌──────────────┐
         │    INICIO    │
         └──────┬───────┘
                │
         ┌──────▼───────────────────────┐
         │  Registro pedido en web      │
         │  Generación de QR (Firebase) │
         └──────┬───────────────────────┘
                │
         ┌──────▼──────────────┐
         │  ¿QR válido en HMI? │◄─── NO ──┐
         └──────┬──────────────┘          │
               SÍ                         │
                │                   (reintentar)
         ┌──────▼───────────────────────┐
         │  Cliente coloca prenda       │
         │  en entrada de banda         │
         └──────┬───────────────────────┘
                │
         ┌──────▼─────────────────────┐
         │  ¿Sensor S1 detecta        │◄─── NO ──┐
         │  prenda? (barrera IR)      │          │
         └──────┬─────────────────────┘    (esperar)
               SÍ
                │
         ┌──────▼──────────────────────────────────┐
         │  Motor ON — Banda avanza 45 segundos     │
         │  hacia estación de fotografía            │
         └──────┬──────────────────────────────────┘
                │
         ┌──────▼────────────────────────────────────┐
         │  Raspberry Pi toma foto de prenda          │
         │  Modelo IA clasifica: ¿Camisa o Playera?   │
         └──────┬────────────────────────────────────┘
                │
         ┌──────▼────────┐
         │  ¿Tipo prenda? │
         └──┬─────────┬──┘
          CAMISA    PLAYERA
            │           │
      camisa.script  playera.script
            └─────┬─────┘
                  │
         ┌────────▼──────────────────────┐
         │  ¿Sensor S2 activo?           │◄─── NO ──┐
         │  (inductivo, posición UR3)    │          │
         └────────┬──────────────────────┘    (esperar)
                 SÍ
                  │
         ┌────────▼──────────────────────────────┐
         │  Motor OFF — UR3 ejecuta rutina        │
         │  de planchado (7 waypoints, ~15 seg)   │
         └────────┬──────────────────────────────┘
                  │
         ┌────────▼──────────────────────┐
         │  Motor ON — Banda avanza       │
         │  hacia estación de salida      │
         └────────┬──────────────────────┘
                  │
         ┌────────▼──────────────────────┐
         │  ¿Sensor S3 activo?           │◄─── NO ──┐
         │  (inductivo, posición salida) │          │
         └────────┬──────────────────────┘    (esperar)
                 SÍ
                  │
         ┌────────▼────────────────────────────────────┐
         │  Motor OFF                                   │
         │  ESP32 activa pistón eléctrico (9 seg)       │
         │  Prenda empujada al gancho de salida         │
         └────────┬────────────────────────────────────┘
                  │
         ┌────────▼─────────────────────────────────┐
         │  Motor ON — Avance final 60 segundos      │
         │  Motor OFF — STOP                        │
         └────────┬─────────────────────────────────┘
                  │
         ┌────────▼──────────────────────────────────┐
         │  Firebase actualiza estado del pedido     │
         │  "Listo para entrega" + foto guardada     │
         └────────┬──────────────────────────────────┘
                  │
         ┌────────▼───────────┐
         │   FIN DEL CICLO    │
         └────────────────────┘
```

---

## Manejo de errores

El sistema implementa mecanismos de robustez ante fallas:

- **Debounce de sensores:** se requieren 3 lecturas consecutivas en 50 ms para validar el estado de un sensor, filtrando ruido eléctrico y rebotes mecánicos.
- **Reintentos de fotografía:** hasta 3 intentos con 2 segundos de espera entre reintentos si la cámara Raspberry no responde.
- **Watchdog del UR3:** `rtde_set_watchdog("speed_slider_mask", 10.0, "ignore")` evita bloqueos por pérdida de conexión.
- **Gestión de errores en loop:** cualquier excepción en el loop principal es capturada, registrada y reportada al dashboard sin detener el sistema.

---

## Siguiente sección

[Arquitectura Ciberfísica](06-arquitectura.md)
