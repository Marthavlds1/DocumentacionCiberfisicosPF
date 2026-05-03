---
layout: default
title: Metodología de Desarrollo
nav_order: 14
---

# Metodología de Desarrollo

## Enfoque metodológico

El proyecto siguió una **metodología iterativa por capas**, desarrollando e integrando cada subsistema de forma incremental. En lugar de intentar construir el sistema completo de una vez, el equipo validó cada capa antes de integrarla con las demás.

---

## Etapas de desarrollo

### Etapa 1 — Definición del sistema (Enero 2026)
- Identificación del problema y selección del caso de uso (planchado industrial)
- Selección de componentes disponibles en el laboratorio
- Diseño de la arquitectura ciberfísica y definición del flujo de proceso
- Investigación de protocolos de comunicación (Modbus TCP, Serial USB, Firebase)

### Etapa 2 — Construcción de la estructura física (Febrero 2026)
- Ensamble de la banda transportadora
- Instalación de los tres sensores en posiciones calibradas
- Montaje del UR3 y fabricación del efector PLA mediante impresión 3D
- Conexión del tablero PLC Micro850 con sus entradas y salidas digitales

### Etapa 3 — Programación del PLC y calibración del UR3 (Feb–Mar 2026)
- Desarrollo de la lógica de control en Connected Components Workbench (CCW)
- Programación y calibración de los 7 waypoints de cada rutina URScript en PolyScope
- Validación de las trayectorias sin carga antes de montar la plancha

### Etapa 4 — Backend, Firebase e interfaz web (Marzo 2026)
- Configuración de Firebase (Auth, Firestore, Realtime Database, Storage)
- Implementación del backend Flask (Docker / Render)
- Desarrollo de la interfaz web en GitHub Pages con registro de pedidos, QR y panel de administrador

### Etapa 5 — Modelo IA y sistema de cámara (Mar–Abr 2026)
- Recopilación del dataset de prendas (camisas y playeras)
- Entrenamiento del clasificador con Google Teachable Machine
- Exportación a `keras_model.h5` e integración con la Raspberry Pi de cámara
- Validación de la clasificación con imágenes de prueba

### Etapa 6 — Integración completa y rutina maestra (Abril 2026)
- Desarrollo de `rutina_maestra.py` como orquestador central
- Integración de todos los subsistemas en el ciclo completo
- Implementación del dashboard de monitoreo (`dashboard_server.py`)
- Pruebas de ciclo completo con prendas reales

### Etapa 7 — Pruebas, ajustes y documentación (Abr–May 2026)
- Ajuste de tiempos del proceso (45 seg foto, 15 seg UR3, 9 seg pistón, 60 seg final)
- Implementación del filtro de debounce para sensores
- Elaboración de la documentación técnica en GitHub Pages

---

## División del trabajo

| Área | Responsabilidad |
| :--- | :--- |
| Robótica (UR3) | Programación y calibración de trayectorias URScript |
| Control (PLC) | Lógica de campo en CCW, Modbus TCP |
| Inteligencia Artificial | Entrenamiento de modelo, integración con Raspberry Pi |
| Backend / Nube | Flask API, Firebase, Docker, Render |
| Interfaz web | GitHub Pages, autenticación, QR, panel admin |
| Integración | `rutina_maestra.py`, arquitectura ciberfísica completa |

---

## Siguiente sección

[Resultados](14-resultados.md)
