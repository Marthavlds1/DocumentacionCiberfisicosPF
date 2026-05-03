---
layout: default
title: Problemas Encontrados
nav_order: 16
---

# Problemas Encontrados

## Retos técnicos durante el desarrollo

A lo largo del proyecto se identificaron y resolvieron múltiples retos de integración, comunicación y sincronización entre subsistemas.

---

## 1. Sincronización Modbus TCP multi-dispositivo

**Problema:** La comunicación simultánea con el PLC (`192.168.3.151`) y el UR3 (`192.168.3.71`) por Modbus TCP generaba conflictos de timing. Peticiones concurrentes causaban timeouts o lecturas incorrectas de sensores.

**Solución:** Se implementó un sistema de **máscaras de sensores por etapa** (`configurar_mascaras_sensores`). Solo el sensor relevante para la etapa actual está habilitado, reduciendo el número de peticiones Modbus simultáneas y el riesgo de conflictos. El polling de sensores se fijó en 100 ms.

---

## 2. Ruido eléctrico en sensores inductivos

**Problema:** Los sensores inductivos S2 y S3 presentaron lecturas inestables debido a rebotes mecánicos de la banda y ruido eléctrico del motor. Esto provocaba falsas activaciones que podían iniciar el UR3 en el momento incorrecto.

**Solución:** Implementación de un **filtro de debounce** que requiere 3 lecturas consecutivas positivas en 50 ms para validar el estado de un sensor:

```python
LECTURAS_DEBOUNCE = 3
TIEMPO_DEBOUNCE   = 0.05  # segundos
```

---

## 3. Clasificación IA con iluminación variable

**Problema:** El modelo `keras_model.h5` presentó variabilidad en el nivel de confianza de clasificación cuando la iluminación del laboratorio cambiaba (luz natural vs. artificial).

**Solución:** Se implementaron **reintentos automáticos** (hasta 3 intentos con 2 segundos de espera) para la captura de fotografía, y se mejoró la iluminación fija de la estación de foto con luz artificial constante.

```python
REINTENTOS_FOTO       = 3
TIEMPO_ENTRE_REINTENTOS = 2.0  # segundos
```

---

## 4. Latencia del backend en Render (arranque en frío)

**Problema:** El plan gratuito de Render suspende el contenedor Docker tras 15 minutos de inactividad. La primera petición tras la suspensión tiene una latencia de 30–60 segundos, lo que podía bloquear la rutina maestra.

**Solución (mitigada):** Se implementó un mecanismo de reintentos en la rutina maestra para las peticiones al backend, permitiendo hasta 3 intentos antes de reportar el error. No se eliminó el problema de fondo, pero se evita que el sistema falle por un solo timeout.

---

## 5. Calibración de waypoints del UR3

**Problema:** La calibración manual de los 7 waypoints para cada tipo de prenda requirió múltiples iteraciones. Las diferencias en la posición de la prenda sobre la banda generaban cobertura incompleta de la superficie en algunos puntos.

**Solución:** Proceso iterativo de calibración en PolyScope: posicionar el robot manualmente → guardar waypoint → ejecutar trayectoria completa → evaluar cobertura → ajustar. Se realizaron aproximadamente 8 iteraciones por rutina hasta lograr cobertura completa sin colisiones.

---

## 6. Gestión de estados concurrentes

**Problema:** La rutina maestra debía manejar simultáneamente el estado del PLC, el robot, la cámara y Firebase, además de responder a errores en cualquiera de estas capas sin bloquear el proceso principal.

**Solución:** Arquitectura de **etapas explícitas** con la función `cambiar_etapa()`, que garantiza que cada subsistema solo está activo durante su etapa correspondiente. El uso de threading controlado (`dashboard_server.py`) permite monitorear el proceso sin interferir con él.

---

## Mejoras futuras identificadas

- Visión por computadora para **detección de arrugas** post-planchado (verificación de calidad)
- **Control PID de temperatura** de la plancha en tiempo real
- Soporte para más tipos de prendas (pantalones, vestidos)
- **Notificaciones push** al cliente cuando la prenda está lista
- Optimización de trayectorias del UR3 con algoritmos de motion planning
- Redundancia en la comunicación Modbus con reconexión automática

---

## Siguiente sección

[Evidencia Visual](16-evidencia.md)
