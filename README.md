# Planchado Express — Documentación Técnica

Documentación técnica del proyecto **Planchado Express**, desarrollado como parte de la asignatura de **Sistemas Ciberfísicos** en la **Universidad Iberoamericana (IBERO)**, Primavera 2026.

---

## Documentación en línea

La documentación completa del proyecto está disponible en:

**[marthavlds1.github.io/DocumentacionCiberfisicosPF](https://marthavlds1.github.io/DocumentacionCiberfisicosPF)**

---

## Descripción del proyecto

Planchado Express es un sistema ciberfísico integrado que automatiza el proceso de planchado de prendas textiles en un entorno industrial. El usuario registra su prenda en la interfaz web y obtiene un código QR de seguimiento; a partir de ese momento el sistema opera de forma completamente autónoma: clasifica la prenda mediante inteligencia artificial, ejecuta la rutina de planchado con un robot colaborativo UR3 y entrega la prenda mediante una banda transportadora con actuadores de salida.

### Componentes principales del sistema

| Componente | Tecnología |
| :--- | :--- |
| Robot colaborativo | Universal Robots UR3 |
| Control industrial | PLC Allen Bradley Micro850 |
| Orquestador del sistema | Raspberry Pi 3 — `rutina_maestra.py` |
| Clasificación por IA | Keras / TensorFlow — `keras_model.h5` |
| Control de periféricos | ESP32 (pistón eléctrico + torreta de señalización) |
| Base de datos y autenticación | Firebase (Auth, Firestore, Realtime DB, Storage) |
| Backend API | Flask — Docker — Render |
| Interfaz web del cliente | GitHub Pages |

---

## Estructura del repositorio

```
DocumentacionCiberfisicosPF/
├── _config.yml
├── _includes/
│   ├── head_custom.html
│   └── footer_custom.html
├── assets/
│   └── css/custom.css
├── index.md
├── 01-contexto.md
├── 02-problema.md
├── 03-objetivos.md
├── 04-descripcion-funcional.md
├── 05-algoritmo.md
├── 06-arquitectura.md
├── 07-diseno-mecanico.md
├── 08-diseno-electronico.md
├── 09-control-programacion.md
├── 10-iot-nube-interfaz.md
├── 11-simulacion.md
├── 12-materiales-costos.md
├── 13-metodologia.md
├── 14-resultados.md
├── 15-problemas.md
├── 16-evidencia.md
├── 17-referencias.md
└── uso-ia.md
```
---

## Equipo de desarrollo

| Integrante | Programa |
| :--- | :--- |
| Luis Cortés Muñoz | Ingeniería Mecatrónica — IBERO |
| Emmanuel Iturbide Rebolledo | Ingeniería Mecatrónica — IBERO |
| Alexander Moncada Rivas | Ingeniería Mecatrónica — IBERO |
| Martha Valdés Cruz | Ingeniería Mecatrónica — IBERO |
| Renata Badillo Cabrera | Ingeniería Mecatrónica — IBERO |
| Camila Sánchez Guevara | Ingeniería Mecatrónica — IBERO |

**Cuerpo docente:** Mr. Joel Arango Ramírez · Dr. Huber Girón Nieto

---

## Referencias del proyecto

| Recurso | URL |
| :--- | :--- |
| Documentación técnica | [marthavlds1.github.io/DocumentacionCiberfisicosPF](https://marthavlds1.github.io/DocumentacionCiberfisicosPF) |
| Interfaz web del cliente | [luiscortesmunoz.github.io/Planchaduria](https://luiscortesmunoz.github.io/Planchaduria/) |
| Backend API (Render) | [docker-planchaduria.onrender.com](https://docker-planchaduria.onrender.com) |
| Diagrama de arquitectura | [Miro — Arquitectura Ciberfísica](https://miro.com/app/live-embed/uXjVGEpRJUk=/) |

---

## Tecnologías utilizadas

`Python` `URScript` `Flask` `Firebase` `Docker` `Keras` `TensorFlow` `Modbus TCP` `Raspberry Pi` `ESP32` `PLC Micro850` `Jekyll` `Just the Docs`

---

Universidad Iberoamericana · Ingeniería Mecatrónica · Sistemas Ciberfísicos · Primavera 2026
