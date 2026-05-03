---
layout: default
title: Objetivos
nav_order: 4
---

# Objetivos del Proyecto

## Objetivo General

Diseñar e implementar un sistema ciberfísico capaz de **automatizar el proceso de planchado de prendas textiles** en un entorno industrial, integrando robótica colaborativa (UR3), control PLC (Micro850), visión artificial por inteligencia artificial (Keras/TensorFlow) e infraestructura IoT en la nube (Firebase/Render), aplicando los conocimientos y herramientas adquiridos a lo largo de la carrera de Ingeniería Mecatrónica.

---

## Objetivos Específicos

### 1. Automatización robótica con UR3
Programar el robot colaborativo UR3 para ejecutar trayectorias de planchado diferenciadas según el tipo de prenda detectada (camisa o playera), utilizando URScript con 7 waypoints calibrados por rutina y comunicación Modbus TCP con el sistema de control.

### 2. Clasificación automática de prendas por IA
Implementar un modelo de visión artificial entrenado con Keras/TensorFlow (`keras_model.h5`) capaz de clasificar automáticamente el tipo de prenda mediante fotografía capturada por Raspberry Pi, con retroalimentación al sistema para seleccionar la rutina correcta del robot.

### 3. Control industrial mediante PLC Micro850
Programar el PLC Allen Bradley Micro850 para gestionar la lógica de control del motor de la banda transportadora, los tres sensores del proceso (barrera IR + 2 inductivos) y los actuadores de campo (motor, plancha), comunicándose vía Modbus TCP con la Raspberry Pi orquestadora.

### 4. Interfaz web con trazabilidad completa
Desarrollar una plataforma web responsive hospedada en GitHub Pages que permita al usuario registrar su prenda, obtener un código QR de seguimiento y monitorear el estado del proceso en tiempo real, con historial almacenado en Firebase y fotografía de evidencia de cada prenda procesada.

### 5. HMI de monitoreo industrial
Implementar un panel HMI físico sobre Raspberry Pi 3 con pantalla táctil que muestre el estado operativo del sistema, lea el código QR del cliente mediante cámara integrada y permita la supervisión local del proceso de planchado en tiempo real.

### 6. Arquitectura ciberfísica completa e integrada
Integrar todos los componentes del sistema (UR3, PLC Micro850, Raspberry Pi, ESP32, Firebase, HMI, interfaz web) en una arquitectura ciberfísica coherente con comunicación bidireccional, gestión de estados por etapas y manejo de errores robusto.

---

## Siguiente sección

[Descripción Funcional del Sistema](04-descripcion-funcional.md)
