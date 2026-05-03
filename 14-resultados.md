---
layout: default
title: Resultados
nav_order: 15
---

# Resultados

## Logros del proyecto

El sistema fue implementado y probado de forma exitosa, logrando la **automatización completa del ciclo de planchado** con integración de todos los subsistemas definidos en los objetivos.

---

## Métricas del sistema

| Indicador | Resultado |
| :--- | :--- |
| Objetivos cumplidos | 6 de 6 (100%) |
| Tipos de prenda clasificados por IA | 2 (Camisa / Playera) |
| Waypoints calibrados por rutina | 7 |
| Etapas del proceso automatizado | 8 |
| Intervención humana en el planchado | Ninguna (0%) |
| Prendas procesadas en pruebas (27-28 Abr 2026) | 10 prendas (usuarios 229–239) |
| Subsistemas integrados | 7 (UR3, PLC, Raspberry Pi x2, ESP32, Firebase, HMI) |

---

## Resultados por subsistema

### Robot UR3 — Planchado autónomo
El UR3 ejecuta con éxito las rutinas de planchado diferenciadas para camisa y playera. Los 7 waypoints cubren la superficie completa de la prenda con la presión y velocidad calibradas.

### Clasificación IA — keras_model.h5
El modelo clasificó correctamente las prendas durante todas las pruebas, con niveles de confianza consistentes para seleccionar la rutina correcta del robot. Los resultados fueron registrados en el dashboard en tiempo real.

### PLC Micro850 — Control de campo
El PLC gestionó correctamente el encendido/apagado del motor, la lectura de los tres sensores y la activación de la plancha eléctrica durante todos los ciclos de prueba, sin errores de comunicación Modbus.

### Interfaz web — En producción
La plataforma está desplegada y funcional en [luiscortesmunoz.github.io/Planchaduria](https://luiscortesmunoz.github.io/Planchaduria/). Usuarios reales utilizaron el sistema durante las pruebas finales (usuarios 229–239), registrando sus prendas, obteniendo QR y monitoreando el estado en tiempo real.

### Firebase — Trazabilidad completa
Cada prenda procesada quedó registrada en Firebase con: ID de pedido, datos del usuario, tipo de prenda detectado por IA, nivel de confianza, fotografía de evidencia y estado final del pedido.

### HMI — Validación por QR
El HMI leyó correctamente los códigos QR presentados por los usuarios y habilitó el inicio del proceso físico tras validar el ID contra Firebase.

---

## Evidencia de prendas procesadas

Las siguientes fotografías fueron capturadas automáticamente por la cámara Raspberry Pi durante las pruebas del 27–28 de abril de 2026 y almacenadas en Firebase Storage:

| ID Usuario | Fecha y hora | Almacenamiento |
| :--- | :--- | :--- |
| 229 | 27 Abr 2026 · 17:20 | Firebase Storage |
| 230 | 27 Abr 2026 · 19:05 | Firebase Storage |
| 231 | 27 Abr 2026 · 19:12 | Firebase Storage |
| 233 | 27 Abr 2026 · 20:35 | Firebase Storage |
| 234 | 27 Abr 2026 · 20:39 | Firebase Storage |
| 235 | 27 Abr 2026 · 20:42 | Firebase Storage |
| 236 | 27 Abr 2026 · 20:56 | Firebase Storage |
| 237 | 28 Abr 2026 · 21:17 | Firebase Storage |
| 238 | 28 Abr 2026 · 21:25 | Firebase Storage |
| 239 | 28 Abr 2026 · 21:39 | Firebase Storage |

---

## Siguiente sección

[Problemas Encontrados](15-problemas.md)
