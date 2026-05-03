---
layout: default
title: Inicio
nav_order: 1
---

# Planchado Express — Sistemas Ciberfísicos

Bienvenido a la documentación técnica del proyecto **Planchado Express**, desarrollado como parte de la asignatura de **Sistemas Ciberfísicos** en la Universidad Iberoamericana, Primavera 2026.

---

## Identidad del Proyecto

| Campo | Descripción |
| :--- | :--- |
| **Proyecto** | Planchado Express |
| **Materia** | Sistemas Ciberfísicos |
| **Institución** | Universidad Iberoamericana (IBERO) |
| **Programa** | Ingeniería Mecatrónica y Sistemas Ciberfísicos |
| **Semestre** | Noveno semestre |
| **Periodo** | Primavera 2026 |

## Cuerpo Docente

- **Mr. Joel Arango Ramírez**
- **Dr. Huber Girón Nieto**

## Integrantes del Equipo

| Integrante | Programa |
| :--- | :--- |
| Luis Cortés Muñoz | Ingeniería Mecatrónica |
| Emmanuel Iturbide Rebolledo | Ingeniería Mecatrónica |
| Alexander Moncada Rivas | Ingeniería Mecatrónica |
| Martha Valdés Cruz | Ingeniería Mecatrónica |
| Renata Badillo Cabrera | Ingeniería Mecatrónica |
| Camila Sánchez Guevara | Ingeniería Mecatrónica |

---

## Descripción General del Sistema

**Planchado Express** es un sistema ciberfísico integrado que automatiza el proceso de planchado de prendas textiles en un entorno industrial. El usuario únicamente registra su prenda en la interfaz web y la coloca en la entrada de la banda transportadora; a partir de ese momento, el sistema opera de forma completamente autónoma.

El sistema integra:

- **Robot colaborativo UR3** — ejecuta las trayectorias de planchado
- **PLC Allen Bradley Micro850** — controla la banda, sensores y actuadores
- **Raspberry Pi 3** — orquesta el proceso completo y clasifica prendas con IA
- **ESP32** — controla la torreta de señalización y el pistón de salida
- **HMI** — panel táctil con lector QR para validación de pedidos
- **Firebase + Render** — nube para trazabilidad y gestión de pedidos
- **Interfaz web** — registro y monitoreo desde cualquier dispositivo

---

## Contenido de la Documentación

- [01. Contexto General](01-contexto.md)
- [02. Problema de Ingeniería](02-problema.md)
- [03. Objetivos](03-objetivos.md)
- [04. Descripción Funcional](04-descripcion-funcional.md)
- [05. Algoritmo de Funcionamiento](05-algoritmo.md)
- [06. Arquitectura Ciberfísica](06-arquitectura.md)
- [07. Diseño Mecánico](07-diseno-mecanico.md)
- [08. Diseño Electrónico](08-diseno-electronico.md)
- [09. Control y Programación](09-control-programacion.md)
- [10. IoT / Nube / Interfaz Web](10-iot-nube-interfaz.md)
- [11. Simulación y Modelado](11-simulacion.md)
- [12. Materiales y Costos](12-materiales-costos.md)
- [13. Metodología de Desarrollo](13-metodologia.md)
- [14. Resultados](14-resultados.md)
- [15. Problemas Encontrados](15-problemas.md)
- [16. Evidencia Visual](16-evidencia.md)
- [17. Referencias](17-referencias.md)

---

© 2026 — Universidad Iberoamericana · Sistemas Ciberfísicos
