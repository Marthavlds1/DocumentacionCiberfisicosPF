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
