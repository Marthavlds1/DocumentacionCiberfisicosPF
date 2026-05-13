---
layout: default
title: Mejoras Futuras
nav_order: 18
---

# Mejoras Futuras

A partir del desarrollo e integración del sistema de **Planchado Express**, se identificaron diferentes áreas de oportunidad que pueden mejorar el desempeño, la estabilidad y la escalabilidad del proyecto. Estas mejoras abarcan la parte de control, sensores, planchado, mecánica, estructura, electrónica y visión artificial.

---

## Programador lógico / PLC

Durante el desarrollo del sistema se utilizó el PLC disponible de acuerdo con los recursos del proyecto. Sin embargo, las salidas utilizadas (relevador) no fueron las más adecuadas para generar pulsos rápidos y precisos para el control del motor a pasos. Esto provocó que el movimiento del motor fuera más lento y que el control de velocidad tuviera ciertas limitaciones.

Como mejora futura, se propone utilizar un PLC con **salidas transistor de alta velocidad** o salidas especiales para control de pulsos. Esto permitiría generar señales más rápidas, mejorar la respuesta del motor a pasos y tener un control más preciso del movimiento.

También se debe considerar la ubicación y protección de los sensores, ya que algunos pueden verse afectados por la luz del medio ambiente. Para evitar lecturas falsas, se recomienda mejorar el montaje físico de los sensores, calibrarlos correctamente y, si es necesario, utilizar sensores con mayor inmunidad a la luz externa.

---

## Sistema de planchado

En la parte de planchado, una mejora importante sería utilizar una superficie más estable para sostener la playera o prenda durante el proceso. Actualmente, si la prenda no queda completamente fija, puede moverse o quedar suspendida, lo que afecta la calidad del planchado.

Como mejora futura, se propone diseñar una base donde la prenda permanezca bien extendida y fija durante todo el proceso. Además, se podrían agregar más pasadas de la plancha para mejorar el acabado final y asegurar que la prenda quede mejor planchada.

---

## Sistema mecánico

En la parte mecánica, se identificó que el movimiento podría mejorar utilizando componentes de mayor calidad. Una propuesta es invertir en una **cadena tipo bicicleta** y en **engranes nuevos**, ya que esto permitiría obtener un movimiento más uniforme, estable y confiable.

También se recomienda comprar más perfil estructural para completar y mejorar el rack de entrega. Esto permitiría tener una salida más ordenada de las prendas y facilitaría el proceso final después del planchado.

---

## Estructura del sistema

Para mejorar la firmeza de la estructura, se propone agregar perfiles en diagonal en zonas estratégicas. Esto ayudaría a reducir vibraciones, aumentar la rigidez del sistema y mejorar la estabilidad general durante el movimiento del motor, la plancha y los mecanismos de transporte.

Una estructura más rígida también permitiría que los sensores, el motor y los actuadores trabajen con mayor precisión, reduciendo errores causados por movimientos no deseados.

---

## PCB y torreta

En la parte electrónica, específicamente en la PCB y la torreta, se identificaron oportunidades de mejora en el diseño y armado del circuito. Debido al proceso de fabricación utilizado, se presentaron algunos problemas con la PCB, lo que dificultó alcanzar el funcionamiento deseado.

Como mejora futura, se propone rediseñar la PCB, revisar correctamente las conexiones y validar el circuito antes de fabricarlo. Además, se recomienda mandar a fabricar la PCB de manera profesional, por ejemplo, con un proveedor especializado, para obtener una placa con mejor calidad, mayor confiabilidad y menor probabilidad de fallas.

Esto permitiría que la torreta funcione correctamente y que las señales visuales del sistema, como los colores de estado, sean más claras y estables.

---

## Escalabilidad del sistema

Finalmente, una mejora importante sería implementar más carritos dentro del sistema para poder procesar más de una prenda al mismo tiempo. Esto permitiría aumentar la capacidad del sistema y hacerlo más eficiente en un entorno de producción.

Además, se podría ampliar la red neuronal utilizada para la clasificación de prendas, agregando más tipos de ropa como sacos, pantalones u otras prendas. Con un modelo más completo, el sistema podría tomar mejores decisiones y adaptarse a una mayor variedad de casos reales.

---

## Conclusión

Las mejoras futuras propuestas permitirían que el sistema de Planchado Express sea más rápido, estable y confiable. Al optimizar el PLC, mejorar la estructura mecánica, rediseñar la PCB, fijar mejor la prenda durante el planchado y ampliar la capacidad del sistema, el proyecto podría evolucionar hacia una versión más robusta y cercana a una aplicación industrial real.