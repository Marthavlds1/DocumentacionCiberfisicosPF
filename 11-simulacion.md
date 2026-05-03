---
layout: default
title: Simulación y Modelado
nav_order: 12
---

# Simulación y Modelado

## Estrategia de validación digital

El proyecto utilizó cuatro herramientas de simulación y validación antes de la implementación física:

---

## 1. Programación del UR3 en PolyScope

Las trayectorias de planchado fueron programadas y validadas en el **entorno de programación PolyScope** del propio UR3. Este entorno permite:

- Definir waypoints de forma interactiva moviendo el robot manualmente.
- Verificar alcance articular y detectar singularidades.
- Simular la trayectoria completa en modo "fantasma" antes de ejecutarla físicamente.
- Exportar el programa como script URScript (`camisa.script` / `playera.script`).

Las rutinas fueron validadas con la plancha montada en el efector para verificar que no había colisiones con la estructura de la banda.

---

## 2. Entrenamiento del modelo IA — Google Teachable Machine

El clasificador de prendas fue entrenado con **Google Teachable Machine**:

1. Se recolectaron imágenes de camisas y playeras en condiciones similares a las del sistema real (iluminación del laboratorio, ángulo de la cámara).
2. Se entrenó el modelo con las dos clases: `Camisa` y `Playera`.
3. El modelo exportado en formato Keras (`.h5`) fue validado con un conjunto de imágenes de prueba antes de su integración.

| Parámetro del modelo | Valor |
| :--- | :--- |
| Archivo | `keras_model.h5` |
| Etiquetas | `labels.txt` → `0 Camisa`, `1 Playera` |
| Tamaño de entrada | 224 × 224 px |
| Normalización | `/127.5 - 1` (rango [-1, 1]) |
| Framework | TF-Keras / TensorFlow |

---

## 3. Lógica PLC en Connected Components Workbench

La lógica de control del PLC Micro850 fue desarrollada y simulada en **Connected Components Workbench (CCW)** antes de descargarse al hardware. CCW permite:

- Simular el comportamiento de las entradas y salidas digitales.
- Verificar la secuencia de activación del motor y respuesta a sensores.
- Depurar la lógica Ladder antes de la integración con Modbus.

---

## 4. Pruebas de integración con dashboard_server.py

El `dashboard_server.py` permitió realizar pruebas de la `rutina_maestra.py` monitoreando el flujo completo de estados sin necesidad de tener todo el hardware conectado simultáneamente. El sistema de SSE y parseo de logs facilitó la detección temprana de errores de integración.

---

## Siguiente sección

[Materiales y Costos](12-materiales-costos.md)
