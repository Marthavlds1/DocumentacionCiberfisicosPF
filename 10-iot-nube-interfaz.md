---
layout: default
title: IoT / Nube / Interfaz Web
nav_order: 11
---

# IoT / Nube / Interfaz Web

## Arquitectura de la capa de conectividad

La capa IoT del sistema integra tres servicios en la nube que operan de forma coordinada:

```
  Cliente (navegador)
       │
       ▼
  GitHub Pages ──────► Firebase (Auth + Firestore + Storage)
                              │
                         Render (Flask)
                              │
                         Raspberry Pi (rutina_maestra.py)
```

---

## Firebase — Base de datos y autenticación

Firebase es el **eje central de datos** del sistema. Gestiona cuatro servicios:

| Servicio Firebase | Uso en el proyecto |
| :--- | :--- |
| **Firebase Auth** | Autenticación de usuarios con email + verificación por código |
| **Firestore** | Almacenamiento de pedidos, clientes y estado del sistema |
| **Realtime Database** | Estado en tiempo real del pedido activo (para HMI y dashboard) |
| **Firebase Storage** | Fotografías de evidencia de cada prenda procesada |

### Estructura de datos en Realtime Database

```json
{
  "estado_actual": {
    "usuario_actual": "229",
    "cantidad": 1,
    "activo": true,
    "estado": "En proceso",
    "current_order_id": "abc123",
    "updated_at": "2026-04-27T17:20:33"
  }
}
```

---

## Backend Flask — Render (Docker)

El backend está construido con **Flask** y desplegado en **Render** como contenedor Docker. Actúa como intermediario entre la interfaz web, Firebase y la Raspberry Pi.

### Dependencias (`requirements.txt`)

```
Flask==3.0.3
flask-cors==4.0.1
firebase-admin==6.5.0
gunicorn==22.0.0
Werkzeug==3.0.3
requests==2.32.3
```

### Endpoints disponibles

| Endpoint | Método | Función |
| :--- | :--- | :--- |
| `GET /estado` | GET | Estado actual del sistema y pedido activo |
| `POST /activar_plc` | POST | Activa el proceso físico (inicio del ciclo) |
| `POST /desactivar_plc` | POST | Detiene el proceso físico |
| `POST /set_cantidad` | POST | Actualiza la cantidad de prendas del pedido |
| `POST /subir_foto` | POST | Sube fotografía de evidencia a Firebase Storage |
| `GET /fotos` | GET | Lista las fotografías del pedido actual |
| `GET /historial` | GET | Historial completo de pedidos procesados |

### URL del backend en producción

```
https://docker-planchaduria.onrender.com
```

{: .note }
El plan gratuito de Render suspende el contenedor tras 15 minutos de inactividad. La rutina maestra implementa reintentos automáticos para el arranque en frío.

---

## Interfaz Web — GitHub Pages

La interfaz web es una **Single Page Application** (SPA) hospedada en GitHub Pages, que se comunica directamente con Firebase mediante el SDK de JavaScript.

**URL:** [luiscortesmunoz.github.io/Planchaduria](https://luiscortesmunoz.github.io/Planchaduria/)

### Funcionalidades para el cliente

| Función | Descripción |
| :--- | :--- |
| Registro / Login | Autenticación Firebase con verificación por correo |
| Registrar prenda | Selección de tipo, material y cantidad |
| Generación de QR | QR único vinculado al ID del pedido |
| Estado en tiempo real | Consulta del estado actual del pedido |
| Historial | Listado de todas las prendas procesadas |
| Evidencia fotográfica | Foto de la prenda tomada durante el proceso |

### Panel de administrador

La interfaz incluye un **panel de administrador** protegido por autenticación que permite:

- Ver el dashboard general con totales (pendientes, en proceso, listos, entregados)
- Gestionar pedidos (crear, editar, actualizar estado, eliminar)
- Ver el directorio de clientes registrados
- Cambiar manualmente el estado de cualquier pedido

---

## Dashboard industrial local

El archivo `dashboard_server.py` sirve un **panel de monitoreo** accesible en la red local del laboratorio (puerto `5050`), que muestra en tiempo real:

- Etapa actual del proceso (`ESPERA_SENSOR1`, `UR3`, `PISTON`, etc.)
- Estado de los tres sensores (S1, S2, S3)
- Estado del motor y la plancha
- Tipo de prenda detectada por IA y nivel de confianza
- Logs de la rutina maestra en tiempo real (vía SSE)
- Información del pedido activo (ID, usuario, cantidad, tipo de prenda)

---

## Siguiente sección

[Simulación y Modelado](11-simulacion.md)
