---
layout: default
title: Contexto General
nav_order: 2
---

# Contexto General del Proyecto

## Entorno de aplicación

**Planchado Express** se ubica en el contexto de la industria de **planchadurías comerciales**, donde el proceso de planchado de prendas representa una actividad central del negocio. Este tipo de establecimientos atiende volúmenes altos de prendas diariamente, lo que convierte la automatización en una palanca de mejora operativa significativa.

El proyecto busca demostrar que los principios de los **sistemas ciberfísicos** — la integración coherente de componentes físicos con capas de software, control y conectividad — pueden aplicarse con éxito a procesos industriales de uso cotidiano.

---

## ¿Qué es Planchado Express?

Planchado Express es un **sistema ciberfísico integrado** que automatiza el proceso completo de planchado de prendas textiles. El cliente únicamente:

1. Registra su prenda en la interfaz web y obtiene un código QR.
2. Presenta su QR en el HMI y coloca la prenda en la entrada de la banda.

A partir de ese momento, el sistema opera de forma **completamente autónoma**: la prenda es transportada, fotografiada, clasificada por inteligencia artificial, planchada por el robot UR3 y entregada mediante un pistón de salida, sin intervención humana adicional.

---

## Origen del proyecto

La idea surgió en el aula durante la asignatura de Sistemas Ciberfísicos, como respuesta al reto de **automatizar un proceso de la vida diaria** utilizando las herramientas aprendidas a lo largo de la carrera de Ingeniería Mecatrónica.

El planchado fue elegido por su viabilidad técnica dentro del laboratorio y por representar un proceso con pasos secuenciales claros, susceptible de ser orquestado mediante un sistema de control y comunicación distribuida.

---

## Tipo de prendas

El prototipo está enfocado en el tratamiento de **prendas de tela plana**:

- Camisas de vestir
- Playeras / camisetas

La clasificación entre ambos tipos se realiza automáticamente mediante un modelo de **inteligencia artificial** (Keras/TensorFlow) que analiza la fotografía de la prenda antes de seleccionar la trayectoria de planchado del robot.

---

## Alcance del proyecto

El desarrollo corresponde a un **prototipo funcional** orientado a:

- Demostrar la viabilidad técnica de la integración ciberfísica completa.
- Validar la comunicación entre todos los subsistemas (PLC, robot, IA, nube, HMI).
- Evidenciar el uso de protocolos industriales (Modbus TCP) y de IoT (Firebase, REST).

No se busca aún un producto comercial terminado, sino una solución experimental capaz de validar el concepto de automatización del planchado en entorno académico-industrial.

---

## Siguiente sección

[Problema de Ingeniería](02-problema.md)
