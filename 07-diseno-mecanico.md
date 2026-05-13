---
layout: default
title: Diseño Mecánico
nav_order: 8
---

# Diseño Mecánico

## Estructura general del sistema

La estructura física de **Planchado Express** está compuesta por una **banda transportadora lineal** con tres estaciones de sensado y una plataforma de montaje para el robot UR3. El recorrido de la prenda va desde la entrada (sensor S1) hasta la salida por gancho (sensor S3).

![Estructura general del sistema](assets/img/diseno-mecanico.png)
![Medidas de estacion](assets/img/Estacion.jpeg)

---

## Robot UR3 — Especificaciones físicas

| Parámetro | Valor |
| :--- | :--- |
| Modelo | Universal Robots UR3 |
| Tipo | Robot colaborativo (Cobot) |
| Grados de libertad | 6 DOF |
| TCP configurado | `p[0.0, 0.0, 0.0777, 0.0, 0.0, 0.0]` |
| Payload configurado | 0.1 kg |
| Voltaje de herramienta | 24 V |
| Gravedad configurada | `[0.0, 0.0, 9.82]` m/s² |
| Efector final | Agarrador impreso en PLA (fabricación propia) |
| Herramienta montada | Plancha eléctrica comercial |
| Waypoints por rutina | 7 puntos calibrados |

---

## Efector final — Agarrador PLA

El agarrador del efector final fue **diseñado y fabricado mediante impresión 3D** en filamento PLA. Está dimensionado para:

- Sostener con seguridad la plancha comercial utilizada.
- Garantizar la geometría de contacto correcta con la superficie de la prenda durante las trayectorias de planchado.
- Resistir el peso y el calor transmitido por la plancha durante la operación continua.

---

## Banda transportadora

| Parámetro | Descripción |
| :--- | :--- |
| Tipo | Banda lineal motorizada |
| Dirección | Unidireccional (adelante) |
| Control | PLC Micro850 (coils `000001`, `000002`, `000003`) |
| Estaciones | Entrada → Foto → UR3 → Salida |
| Mecanismo de salida | Pistón eléctrico + gancho lateral |

---

## Actuador de salida — Pistón eléctrico

El pistón eléctrico está controlado por el **ESP32** mediante comandos seriales desde la Raspberry Pi. Al activarse, empuja lateralmente la prenda planchada hacia el gancho de salida donde el cliente la recoge.

| Parámetro | Valor |
| :--- | :--- |
| Tipo | Actuador lineal eléctrico |
| Control | ESP32 vía serial USB |
| Tiempo extendido | 9 segundos |
| Tiempo de espera tras cerrar | 9 segundos |
| Función | Expulsar prenda al gancho de salida |

---

## Piezas diseñadas e impresas en 3D

Todas las piezas fueron diseñadas en CAD y fabricadas mediante impresión 3D en filamento PLA. Los archivos `.stl` están disponibles en la carpeta `0_IMPRIMIR/` del repositorio.

[Descargar archivos STL](assets/0_IMPRIMIR){: .btn .btn-outline }

| Pieza | Vista previa | Función |
| :--- | :---: | :--- |
| Agarre de Plancha 1 | ![Agarre Plancha 1](assets/img/AgarrePlacha1.jpeg) | Sujeción principal de la plancha al efector del UR3 |
| Agarre de Plancha 2 | ![Agarre Plancha 2](assets/img/AgarrePlancha2.jpeg) | Pieza complementaria del agarre de plancha |
| Agarre Motor a Pasos | ![Agarre Motor](assets/img/AgarreMotor.jpeg) | Montaje del motor Nema 17 en la estructura |
| Gancho | ![Gancho](assets/img/Gancho.jpeg) | Gancho de salida para entrega de prenda |
| Cadena Ganchito | ![Cadena Ganchito](assets/img/Cadena_carrito.jpeg) | Eslabón de cadena para sistema de transporte |
| Carrito Base | ![Carrito Base](assets/img/BaseCarrito.jpeg) | Base del carrito sobre la banda |
| Carrito Agarre | ![Carrito Agarre](assets/img/CarritoAgarre.jpeg) | Agarre superior del carrito |
| Engranaje Plato | ![Engranaje Plato](assets/img/Engranaje_plato.jpeg) | Engranaje de transmisión principal |
| Engranaje Final | ![Engranaje Final](assets/img/EngranajeFinal.jpeg) | Engranaje de salida del sistema |
| Soporte Tensor | ![Soporte Tensor](assets/img/SoporteTensor.jpeg) | Soporte para sistema de tensado de banda |
| Tuerca Tensor | ![Tuerca Tensor](assets/img/tuercsTensor.jpeg) | Elemento de ajuste del tensor |
| Tensores | ![Tensores](assets/img/Tensores.jpeg) | Componentes de tensado de la banda |
| Sensores | ![Sensores](assets/img/Sensor.jpeg) | Soporte/montaje para sensores inductivos |
| Soporte acetato sup. | ![Soporte acetato superior](assets/img/arriba.jpeg) | Soporte superior lateral de acetato |
| Soporte acetato | ![Soporte acetato](assets/img/soporte-acetato.jpeg) | Soporte lateral de acetato |

---

## Siguiente sección

[Diseño Electrónico](08-diseno-electronico.md)