---
layout: default
title: Evidencia Visual
nav_order: 17
---

# Evidencia Visual

## Fotografías del sistema

{: .note }
Agrega aquí las fotografías del sistema físico. Coloca tus imágenes en la carpeta `assets/img/evidencia/` y reemplaza los nombres de archivo en los ejemplos de abajo.

### Sistema completo — Vista general

```markdown
![Vista general del sistema](../assets/img/evidencia/sistema-general.jpg)
```

### Robot UR3 con efector y plancha

```markdown
![UR3 con efector PLA y plancha](../assets/img/evidencia/ur3-efector.jpg)
```

### Tablero PLC Micro850

```markdown
![Tablero PLC Allen Bradley Micro850](../assets/img/evidencia/plc-tablero.jpg)
```

### HMI con lector QR

```markdown
![HMI - Pantalla táctil con lector QR](../assets/img/evidencia/hmi.jpg)
```

### Banda transportadora y sensores

```markdown
![Banda transportadora con sensores S1, S2, S3](../assets/img/evidencia/banda-sensores.jpg)
```

---

## Interfaz web — Capturas de pantalla

La interfaz web está disponible en vivo en:

[luiscortesmunoz.github.io/Planchaduria](https://luiscortesmunoz.github.io/Planchaduria/){: .btn .btn-red }

### Pantalla principal — Inicio de sesión
```markdown
![Pantalla de inicio de sesión](../assets/img/evidencia/web-login.jpg)
```

### Registro de prenda y generación de QR
```markdown
![Registro de prenda y QR generado](../assets/img/evidencia/web-registro-qr.jpg)
```

### Panel de administrador
```markdown
![Panel de administrador](../assets/img/evidencia/web-admin.jpg)
```

---

## Dashboard industrial — Monitoreo en tiempo real

```markdown
![Dashboard de monitoreo industrial](../assets/img/evidencia/dashboard-local.jpg)
```

---

## Prendas procesadas — Evidencia fotográfica IA

Las siguientes fotografías fueron capturadas automáticamente durante las pruebas del 27–28 de abril de 2026 y almacenadas en Firebase Storage:

| Archivo | Usuario | Fecha | Clasificación IA |
| :--- | :--- | :--- | :--- |
| `usuario_229_foto_1_20260427_172033.jpg` | 229 | 27 Abr · 17:20 | — |
| `usuario_230_foto_1_20260427_190505.jpg` | 230 | 27 Abr · 19:05 | — |
| `usuario_231_foto_1_20260427_191223.jpg` | 231 | 27 Abr · 19:12 | — |
| `usuario_233_foto_1_20260427_203505.jpg` | 233 | 27 Abr · 20:35 | — |
| `usuario_234_foto_1_20260427_203911.jpg` | 234 | 27 Abr · 20:39 | — |
| `usuario_235_foto_1_20260427_204239.jpg` | 235 | 27 Abr · 20:42 | — |
| `usuario_236_foto_1_20260427_205636.jpg` | 236 | 27 Abr · 20:56 | — |
| `usuario_237_foto_1_20260427_211726.jpg` | 237 | 28 Abr · 21:17 | — |
| `usuario_238_foto_1_20260427_212537.jpg` | 238 | 28 Abr · 21:25 | — |
| `usuario_239_foto_1_20260427_213958.jpg` | 239 | 28 Abr · 21:39 | — |

{: .note }
Para mostrar estas fotos en la página, cópialas de la carpeta `fotos_pc/` del repositorio `industrial_dashboard_planchado_express` a `assets/img/evidencia/` y agrega las etiquetas `![descripción](../assets/img/evidencia/nombre.jpg)` en esta sección.

---

## Video de demostración

Si tienes un video del sistema funcionando, puedes incrustarlo así:

```html
<div class="responsive-embed">
  <iframe src="https://www.youtube.com/embed/TU_VIDEO_ID"
          allowfullscreen></iframe>
</div>
```

O si el video está en el repositorio (como `assets/videos/demo.mp4`):

```html
<video controls>
  <source src="../assets/videos/demo.mp4" type="video/mp4">
</video>
```

---

## Siguiente sección

[Referencias](17-referencias.md)
