# Paso 1: Librerías
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import os
import re
import time
import socket
from datetime import datetime
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageOps
import tf_keras as keras
from tf_keras.models import load_model

import requests
from pymodbus.client import ModbusTcpClient
import serial
import serial.tools.list_ports

# Paso 2: Configuración general
RENDER_BASE_URL = "https://docker-planchaduria.onrender.com"

# Raspberry con cámara
RASPBERRY_IP = "192.168.3.162"
RASPBERRY_PORT = 5000
BASE_RPI = f"http://{RASPBERRY_IP}:{RASPBERRY_PORT}"

# PLC
PLC_IP = "192.168.3.151"
PLC_PORT = 502
PLC_UNIT_ID = 1

# Direcciones PLC (offset base 0)
COIL_CMD_START = 0      # 000001
COIL_CMD_STOP = 1       # 000002
COIL_CMD_DIR_FWD = 2    # 000003

SENSOR1_ADDRESS = 3     # 000004
SENSOR2_ADDRESS = 4     # 000005
SENSOR3_ADDRESS = 5     # 000006
SALIDA_AUX_000007 = 6   # 000007 / Plancha

# Modelo IA
MODEL_PATH = "keras_model.h5"
LABELS_PATH = "labels.txt"
IMG_SIZE_MODELO = (224, 224)

# Robot UR3
ROBOT_IP = "192.168.3.71"
ROBOT_PORT = 30002

# ESP32 por serial
ESP32_SERIAL_PORT = "COM3"   # CAMBIA ESTO SI ES NECESARIO
ESP32_BAUDRATE = 115200
ESP32_TIMEOUT = 1

# Carpeta local para fotos
CARPETA_PC = "fotos_pc"
os.makedirs(CARPETA_PC, exist_ok=True)

# Paso 2.1: Tiempos principales de proceso
TIEMPO_PULSO = 0.2
TIEMPO_POLL = 2.0
TIEMPO_POLL_SENSOR = 0.1
TIEMPO_POLL_CONTINUO = 0.1

# Etapa 1: después de detectar Sensor 1, avanzar 45 segundos y detener para foto
TIEMPO_AVANCE_ANTES_FOTO = 45.0

# Etapa UR3
TIEMPO_RUTINA_UR3 = 15.0

# Cámara
TIEMPO_ESPERA_FOTO = 0.8

# Piston
TIEMPO_PISTON_ABIERTO = 9.0
TIEMPO_ESPERA_TRAS_CERRAR = 9.0

# Finalización: después del pistón, avanzar exactamente 1 minuto y terminar
TIEMPO_AVANCE_FINAL_STOP = 60.0

# Torreta
TIEMPO_PARPADEO_ESPERA_SENSOR1 = 0.3
TIEMPO_FLASH_FOTO = 0.25

# Debounce / filtro contra ruido eléctrico o rebotes mecánicos
LECTURAS_DEBOUNCE = 3
TIEMPO_DEBOUNCE = 0.05

# Reintentos
REINTENTOS_FOTO = 3
TIEMPO_ENTRE_REINTENTOS = 2.0

# Rutinas UR3
RUTA_SCRIPT_CAMISA = "camisa.script"
RUTA_SCRIPT_PLAYERA = "playera.script"

# Rutina vestido
Q_VESTIDO = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]
A_VESTIDO = 0.4
V_VESTIDO = 0.25


# Paso 3: Variables globales
procesando = False
motor_continuo_activo = False
pedido_actual_id = ""
usuario_actual = ""
cantidad_actual = 0
ur3_ya_ejecutado = False
estado_inicio_reportado = False
estado_planchado_reportado = False
tipo_prenda_actual = ""
esp32_serial = None
motor_encendido = False
senal_000007_activada = False
reinicio_despues_ur3 = False
modo_torreta = "rojo"
ultima_foto_local = ""
modelo_prendas = None
labels_prendas = []

# Máscaras de sensores por etapa
sensor1_habilitado = False
sensor2_habilitado = False
sensor3_habilitado = False
etapa_actual = "STOP"


# Paso 4: Utilidades
def limpiar_usuario(usuario: str) -> str:
    usuario = str(usuario).strip()
    usuario = re.sub(r"[^0-9]", "", usuario)

    if usuario == "":
        raise RuntimeError("El usuario no puede estar vacío")

    if len(usuario) > 5:
        raise RuntimeError("El usuario debe tener máximo 5 dígitos")

    return usuario


def imprimir_respuesta_http(resp: requests.Response, etiqueta: str):
    print(f"[HTTP] {etiqueta} status={resp.status_code}")
    try:
        print(f"[HTTP] {etiqueta} json={resp.json()}")
    except Exception:
        print(f"[HTTP] {etiqueta} text={resp.text[:1000]}")


def obtener_usuario_desde_order(order_data: dict) -> str:
    contador = order_data.get("Contador", "")
    folio = order_data.get("Folio", "")

    if contador not in [None, ""]:
        return limpiar_usuario(str(contador))

    digitos = re.sub(r"[^0-9]", "", str(folio))
    if digitos != "":
        return limpiar_usuario(digitos)

    raise RuntimeError("No se pudo obtener un usuario numérico válido del pedido")


def cambiar_etapa(nueva_etapa: str):
    global etapa_actual
    etapa_actual = nueva_etapa
    print(f"[ESTADO] Etapa actual -> {etapa_actual}")


def configurar_mascaras_sensores(s1: bool, s2: bool, s3: bool):
    global sensor1_habilitado, sensor2_habilitado, sensor3_habilitado
    sensor1_habilitado = s1
    sensor2_habilitado = s2
    sensor3_habilitado = s3
    print(
        "[MASCARAS] "
        f"S1={'ON' if s1 else 'OFF'} | "
        f"S2={'ON' if s2 else 'OFF'} | "
        f"S3={'ON' if s3 else 'OFF'}"
    )


def cargar_modelo_prendas():
    global modelo_prendas, labels_prendas

    if modelo_prendas is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"No existe el archivo del modelo: {MODEL_PATH}")

        if not os.path.exists(LABELS_PATH):
            raise RuntimeError(f"No existe el archivo de etiquetas: {LABELS_PATH}")

        print(f"[IA] Cargando modelo desde {MODEL_PATH} ...")
        modelo_prendas = load_model(MODEL_PATH, compile=False)
        print("[IA] Modelo cargado correctamente")

        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            labels_prendas = [line.strip() for line in f if line.strip()]

        print(f"[IA] Etiquetas cargadas: {labels_prendas}")

    return modelo_prendas, labels_prendas


def normalizar_etiqueta_modelo(texto: str) -> str:
    t = (texto or "").strip().lower()

    # Por si viene como "0 Camisa"
    t = re.sub(r"^\d+\s*", "", t)

    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
    for a, b in reemplazos.items():
        t = t.replace(a, b)

    if "playera" in t or "playeras" in t:
        return "playera"
    if "camisa" in t or "camisas" in t:
        return "camisa"
    if "vestido" in t or "vestidos" in t:
        return "vestido"

    return t


def clasificar_prenda_por_ia(ruta_imagen: str) -> Tuple[str, float]:
    if not os.path.exists(ruta_imagen):
        raise RuntimeError(f"No existe la imagen para clasificar: {ruta_imagen}")

    modelo, labels = cargar_modelo_prendas()

    image = Image.open(ruta_imagen).convert("RGB")
    image = ImageOps.fit(image, IMG_SIZE_MODELO, Image.Resampling.LANCZOS)

    image_array = np.asarray(image).astype(np.float32)
    image_array = (image_array / 127.5) - 1.0
    data = np.expand_dims(image_array, axis=0)

    prediction = modelo.predict(data, verbose=0)[0]
    idx = int(np.argmax(prediction))
    confianza = float(prediction[idx])

    if idx < 0 or idx >= len(labels):
        raise RuntimeError(f"Índice de clase fuera de rango: {idx}")

    clase = normalizar_etiqueta_modelo(labels[idx])
    return clase, confianza


# Paso 4.1: ESP32 serial
def listar_puertos_serial():
    puertos = serial.tools.list_ports.comports()
    print("[ESP32] Puertos seriales detectados:")
    for p in puertos:
        print(f" - {p.device} | {p.description}")


def conectar_esp32():
    global esp32_serial

    try:
        if esp32_serial is not None and esp32_serial.is_open:
            return True

        esp32_serial = serial.Serial(
            port=ESP32_SERIAL_PORT,
            baudrate=ESP32_BAUDRATE,
            timeout=ESP32_TIMEOUT
        )

        time.sleep(2)
        print(f"[ESP32] Conectada en {ESP32_SERIAL_PORT}")
        return True

    except Exception as e:
        print(f"[ESP32] No se pudo conectar: {e}")
        esp32_serial = None
        return False


def enviar_comando_esp32(comando: str) -> Tuple[bool, str]:
    global esp32_serial

    try:
        if esp32_serial is None or not esp32_serial.is_open:
            ok = conectar_esp32()
            if not ok:
                return False, "No se pudo abrir el puerto serial de la ESP32"

        cmd = comando.strip().lower() + "\n"
        esp32_serial.write(cmd.encode("utf-8"))
        esp32_serial.flush()

        time.sleep(0.15)

        respuestas = []
        while esp32_serial.in_waiting > 0:
            linea = esp32_serial.readline().decode("utf-8", errors="ignore").strip()
            if linea:
                respuestas.append(linea)

        respuesta = " | ".join(respuestas) if respuestas else "Comando enviado"
        print(f"[ESP32] comando='{comando}' respuesta='{respuesta}'")
        return True, respuesta

    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def torreta_roja():
    return enviar_comando_esp32("rojo")


def torreta_verde():
    return enviar_comando_esp32("verde")


def torreta_apagar():
    return enviar_comando_esp32("apagar")


def torreta_roja_parpadeo(estado_on: bool):
    if estado_on:
        return torreta_roja()
    else:
        return torreta_apagar()


def torreta_verde_flash_uno():
    global modo_torreta

    modo_previo = modo_torreta
    print("[TORRETA] Flash verde por captura de foto")

    torreta_verde()
    time.sleep(TIEMPO_FLASH_FOTO)
    torreta_apagar()
    time.sleep(TIEMPO_FLASH_FOTO)

    modo_torreta = modo_previo
    actualizar_torreta()


def actualizar_torreta():
    global modo_torreta

    # Requisito: usar solamente rojo y verde.
    if modo_torreta == "verde":
        return torreta_verde()
    elif modo_torreta == "apagado":
        return torreta_apagar()
    else:
        modo_torreta = "rojo"
        return torreta_roja()


def piston_extender():
    return enviar_comando_esp32("extender")


def piston_retraer():
    return enviar_comando_esp32("retraer")


def piston_parar():
    return enviar_comando_esp32("parar")


def desconectar_esp32():
    global esp32_serial
    try:
        if esp32_serial is not None and esp32_serial.is_open:
            esp32_serial.close()
            print("[ESP32] Puerto serial cerrado")
    except Exception as e:
        print("[ESP32] Error al cerrar puerto:", e)


# Paso 5: Funciones Render
def render_get_next_order() -> dict:
    print("[RENDER] Consultando siguiente pedido...")
    r = requests.get(f"{RENDER_BASE_URL}/api/worker/next-order", timeout=20)
    imprimir_respuesta_http(r, "next-order")
    r.raise_for_status()
    return r.json()


def render_order_start(order_id: str) -> dict:
    r = requests.post(f"{RENDER_BASE_URL}/api/worker/orders/{order_id}/start", timeout=20)
    imprimir_respuesta_http(r, "start")
    r.raise_for_status()
    return r.json()


def render_order_complete(order_id: str) -> dict:
    r = requests.post(f"{RENDER_BASE_URL}/api/worker/orders/{order_id}/complete", timeout=20)
    imprimir_respuesta_http(r, "complete")
    r.raise_for_status()
    return r.json()


def render_order_error(order_id: str, error_msg: str) -> dict:
    r = requests.post(
        f"{RENDER_BASE_URL}/api/worker/orders/{order_id}/error",
        json={"error": error_msg},
        timeout=20
    )
    imprimir_respuesta_http(r, "error")
    r.raise_for_status()
    return r.json()


def render_order_set_status(order_id: str, estado: str) -> dict:
    r = requests.post(
        f"{RENDER_BASE_URL}/api/worker/orders/{order_id}/status",
        json={"Estado": estado, "estado": estado},
        timeout=20
    )
    imprimir_respuesta_http(r, f"status-{estado}")
    r.raise_for_status()
    return r.json()


def render_marcar_en_proceso(order_id: str):
    global estado_inicio_reportado

    if estado_inicio_reportado:
        return

    try:
        render_order_set_status(order_id, "en_proceso")
    except Exception:
        render_order_start(order_id)

    estado_inicio_reportado = True


def render_marcar_planchado(order_id: str):
    global estado_planchado_reportado

    if estado_planchado_reportado:
        return

    render_order_set_status(order_id, "planchado")
    estado_planchado_reportado = True


def render_marcar_listo_para_entrega(order_id: str):
    render_order_set_status(order_id, "listo_para_entrega")


def render_subir_foto_pedido(order_id: str, ruta_foto: str) -> dict:
    if not os.path.exists(ruta_foto):
        raise RuntimeError(f"No existe la foto a subir: {ruta_foto}")

    peso = os.path.getsize(ruta_foto)
    print(f"[RENDER] Preparando subida de foto: {ruta_foto} | tamaño={peso} bytes")

    if peso == 0:
        raise RuntimeError(f"La foto está vacía: {ruta_foto}")

    ultimo_error = None

    for intento in range(1, REINTENTOS_FOTO + 1):
        print(f"[RENDER] Subiendo foto intento {intento}/{REINTENTOS_FOTO}")

        try:
            with open(ruta_foto, "rb") as f:
                files = {
                    "foto": (os.path.basename(ruta_foto), f, "image/jpeg")
                }

                r = requests.post(
                    f"{RENDER_BASE_URL}/api/worker/orders/{order_id}/photo",
                    files=files,
                    timeout=90
                )

            imprimir_respuesta_http(r, "upload-photo")
            r.raise_for_status()

            data = r.json()

            if not data.get("ok", False):
                raise RuntimeError(f"El backend respondió ok=false: {data}")

            foto_info = data.get("foto", {})
            print(f"[RENDER] Foto subida correctamente. URL={foto_info.get('url', '')}")
            return data

        except Exception as e:
            ultimo_error = e
            print("[RENDER] Error subiendo foto:", e)

            if intento < REINTENTOS_FOTO:
                time.sleep(TIEMPO_ENTRE_REINTENTOS)

    raise RuntimeError(f"No se pudo subir la foto: {ultimo_error}")


# Paso 6: Funciones Raspberry
def rasp_tomar_foto(usuario: str, indice: int):
    usuario_limpio = limpiar_usuario(usuario)
    url = f"{BASE_RPI}/tomar_foto/{usuario_limpio}/{indice}"

    print("[RPI] Solicitando toma de foto...")
    print("[RPI] URL:", url)

    try:
        r = requests.get(url, timeout=30)

        print("[RPI] Status:", r.status_code)
        print("[RPI] Respuesta servidor:", r.text)

        if r.status_code != 200:
            raise RuntimeError(
                f"Error al tomar foto. Status={r.status_code}. "
                f"Respuesta={r.text}"
            )

        data = r.json()
        print("[RPI] Respuesta tomar_foto:", data)
        return data

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"No se pudo conectar con la Raspberry: {e}")


def rasp_dame_foto():
    url = f"{BASE_RPI}/dame_foto"

    print("[RPI] Descargando foto...")
    print("[RPI] URL:", url)

    try:
        r = requests.get(url, timeout=30)

        print("[RPI] Status:", r.status_code)

        if r.status_code != 200:
            raise RuntimeError(
                f"Error al descargar foto. Status={r.status_code}. "
                f"Respuesta={r.text}"
            )

        if len(r.content) == 0:
            raise RuntimeError("La foto llegó vacía")

        return r.content

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"No se pudo descargar la foto desde la Raspberry: {e}")


def tomar_y_guardar_foto(usuario: str, indice: int) -> str:
    global modo_torreta

    usuario_limpio = limpiar_usuario(usuario)

    # Requisito: rojo cuando está detenido. No se usa amarillo.
    modo_torreta = "rojo"
    actualizar_torreta()

    print(f"[RPI] Solicitando foto usuario={usuario_limpio}, indice={indice}")
    rasp_tomar_foto(usuario_limpio, indice)

    time.sleep(TIEMPO_ESPERA_FOTO)

    imagen = rasp_dame_foto()

    nombre = datetime.now().strftime(f"usuario_{usuario_limpio}_foto_{indice}_%Y%m%d_%H%M%S.jpg")
    ruta = os.path.join(CARPETA_PC, nombre)

    with open(ruta, "wb") as f:
        f.write(imagen)

    if not os.path.exists(ruta):
        raise RuntimeError("No se pudo guardar la foto en la PC")

    peso = os.path.getsize(ruta)
    if peso == 0:
        raise RuntimeError("La foto se guardó vacía en la PC")

    print(f"[RPI] Foto guardada en: {ruta} | tamaño={peso} bytes")

    # Requisito: un flash verde cuando la foto fue capturada.
    torreta_verde_flash_uno()

    # Como la foto se toma con el carro detenido, regresamos a rojo.
    modo_torreta = "rojo"
    actualizar_torreta()

    return ruta


# Paso 7: Funciones PLC escritura
def write_coil_value(coil_address: int, value: bool) -> Tuple[bool, str]:
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

    try:
        if not client.connect():
            return False, "No se pudo conectar al PLC"

        result = client.write_coil(coil_address, value, device_id=PLC_UNIT_ID)

        if result.isError():
            return False, f"Error Modbus al escribir coil {coil_address}"

        print(f"[PLC] Coil {coil_address} = {value}")
        return True, f"Coil {coil_address} = {value}"

    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

    finally:
        client.close()


def pulse_coil(coil_address: int, pulse_time: float = TIEMPO_PULSO) -> Tuple[bool, str]:
    ok_on, msg_on = write_coil_value(coil_address, True)
    if not ok_on:
        return False, msg_on

    time.sleep(pulse_time)

    ok_off, msg_off = write_coil_value(coil_address, False)
    if not ok_off:
        return False, msg_off

    return True, "Pulso enviado correctamente"


def activar_salida_000007() -> Tuple[bool, str]:
    ok, msg = write_coil_value(SALIDA_AUX_000007, True)
    if ok:
        print("[PLC] Señal 000007 / PLANCHA ACTIVADA")
    else:
        print(f"[PLC] Error activando 000007: {msg}")
    return ok, msg


def desactivar_salida_000007() -> Tuple[bool, str]:
    ok, msg = write_coil_value(SALIDA_AUX_000007, False)
    if ok:
        print("[PLC] Señal 000007 / PLANCHA DESACTIVADA")
    else:
        print(f"[PLC] Error desactivando 000007: {msg}")
    return ok, msg


def activar_plancha_por_sensor1():
    global senal_000007_activada

    if senal_000007_activada:
        print("[PLC] La plancha ya estaba activada")
        return

    ok_aux, msg_aux = activar_salida_000007()
    if not ok_aux:
        raise RuntimeError(f"No se pudo activar la plancha / 000007: {msg_aux}")

    senal_000007_activada = True


def desactivar_plancha_despues_ur3():
    global senal_000007_activada

    if not senal_000007_activada:
        print("[PLC] La plancha ya estaba desactivada")
        return

    ok_aux, msg_aux = desactivar_salida_000007()
    if not ok_aux:
        raise RuntimeError(f"No se pudo desactivar la plancha / 000007: {msg_aux}")

    senal_000007_activada = False


def start_motor() -> Tuple[bool, str]:
    global motor_encendido, reinicio_despues_ur3, modo_torreta

    ok_dir, msg_dir = write_coil_value(COIL_CMD_DIR_FWD, True)
    if not ok_dir:
        modo_torreta = "rojo"
        actualizar_torreta()
        motor_encendido = False
        return False, msg_dir

    ok_clear_stop, msg_clear_stop = write_coil_value(COIL_CMD_STOP, False)
    if not ok_clear_stop:
        modo_torreta = "rojo"
        actualizar_torreta()
        motor_encendido = False
        return False, msg_clear_stop

    time.sleep(0.1)

    ok_start, msg_start = pulse_coil(COIL_CMD_START)
    if not ok_start:
        modo_torreta = "rojo"
        actualizar_torreta()
        motor_encendido = False
        return False, msg_start

    print("[PLC] Motor iniciado")
    motor_encendido = True
    modo_torreta = "verde"
    actualizar_torreta()

    # Después del UR3, al reiniciar el carro, se apaga la plancha.
    if reinicio_despues_ur3:
        try:
            desactivar_plancha_despues_ur3()
        finally:
            reinicio_despues_ur3 = False

    return True, "Motor iniciado"


def stop_motor() -> Tuple[bool, str]:
    global motor_encendido, modo_torreta

    ok_clear_start, msg_clear_start = write_coil_value(COIL_CMD_START, False)
    if not ok_clear_start:
        return False, msg_clear_start

    time.sleep(0.1)

    ok_stop, msg_stop = pulse_coil(COIL_CMD_STOP)
    if not ok_stop:
        return False, msg_stop

    print("[PLC] Motor detenido")
    motor_encendido = False
    modo_torreta = "rojo"
    actualizar_torreta()
    return True, "Motor detenido"


def mover_motor_por_tiempo(segundos: float, etiqueta: str):
    print(f"[PLC] {etiqueta}: avanzando motor por {segundos:.1f} segundos...")

    ok_start, msg_start = start_motor()
    if not ok_start:
        raise RuntimeError(f"No se pudo iniciar motor en {etiqueta}: {msg_start}")

    time.sleep(segundos)

    ok_stop, msg_stop = stop_motor()
    if not ok_stop:
        raise RuntimeError(f"No se pudo detener motor en {etiqueta}: {msg_stop}")


# Paso 8: Funciones PLC lectura
def read_sensor(sensor_address: int, sensor_name: str) -> Tuple[Optional[bool], str]:
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

    try:
        if not client.connect():
            return None, f"No se pudo conectar al PLC para leer {sensor_name}"

        result = client.read_coils(sensor_address, count=1, device_id=PLC_UNIT_ID)

        if result.isError():
            return None, f"Error al leer {sensor_name}"

        valor = bool(result.bits[0])
        return valor, "OK"

    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

    finally:
        client.close()


def leer_sensor1() -> Tuple[Optional[bool], str]:
    if not sensor1_habilitado:
        return False, "Sensor1 ignorado por máscara de etapa"
    return read_sensor(SENSOR1_ADDRESS, "sensor1")


def leer_sensor2() -> Tuple[Optional[bool], str]:
    if not sensor2_habilitado:
        return False, "Sensor2 ignorado por máscara de etapa"
    return read_sensor(SENSOR2_ADDRESS, "sensor2")


def leer_sensor3() -> Tuple[Optional[bool], str]:
    if not sensor3_habilitado:
        return False, "Sensor3 ignorado por máscara de etapa"
    return read_sensor(SENSOR3_ADDRESS, "sensor3")


def confirmar_sensor_estable(funcion_lectura, nombre_sensor: str, estado_esperado: bool) -> bool:
    """
    Filtro simple por lecturas consecutivas.
    Esto evita que un pico eléctrico o rebote mecánico dispare una etapa.
    """
    for i in range(LECTURAS_DEBOUNCE):
        valor, msg = funcion_lectura()

        if valor is None:
            raise RuntimeError(f"Error leyendo {nombre_sensor}: {msg}")

        if valor != estado_esperado:
            return False

        time.sleep(TIEMPO_DEBOUNCE)

    return True


def esperar_sensor1_y_activar_plancha(order_id: str):
    global modo_torreta

    cambiar_etapa("ESPERA_SENSOR1")
    configurar_mascaras_sensores(s1=True, s2=False, s3=False)

    print("[SENSOR1] Esperando primera detección de prenda...")

    ultimo_cambio = time.time()
    rojo_encendido = True
    modo_torreta = "rojo"
    actualizar_torreta()

    while True:
        valor_sensor, msg_sensor = leer_sensor1()

        if valor_sensor is None:
            raise RuntimeError(f"Error leyendo sensor1: {msg_sensor}")

        print(f"[SENSOR1] valor={valor_sensor}")

        # Parpadeo rojo a 0.3 s mientras se espera la prenda.
        ahora = time.time()
        if ahora - ultimo_cambio >= TIEMPO_PARPADEO_ESPERA_SENSOR1:
            rojo_encendido = not rojo_encendido
            torreta_roja_parpadeo(rojo_encendido)
            ultimo_cambio = ahora

        if valor_sensor:
            if confirmar_sensor_estable(leer_sensor1, "sensor1", True):
                print("[SENSOR1] Prenda detectada de forma estable")

                # Requisito: al detectar Sensor 1, activar inmediatamente la plancha.
                modo_torreta = "rojo"
                actualizar_torreta()
                activar_plancha_por_sensor1()

                render_marcar_en_proceso(order_id)

                # Cierre de etapa 1: Sensor 1 queda deshabilitado.
                configurar_mascaras_sensores(s1=False, s2=False, s3=False)
                return

        time.sleep(TIEMPO_POLL_SENSOR)


# Paso 9: Funciones UR3
def extraer_nombre_funcion_urscript(script_original: str) -> str:
    patron = r"(?m)^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*\)\s*:"
    match = re.search(patron, script_original)

    if not match:
        raise RuntimeError("No se pudo detectar el nombre de la función principal del URScript")

    return match.group(1)


def preparar_script_una_sola_vez(script_original: str) -> str:
    script = script_original.replace("\r\n", "\n")
    nombre_funcion = extraer_nombre_funcion_urscript(script)

    patron_llamada_final = rf"(?m)^\s*{re.escape(nombre_funcion)}\(\)\s*$"
    script = re.sub(patron_llamada_final, "", script).rstrip() + "\n"

    patron_while_principal = r"\n  while\s*\(\s*True\s*\)\s*:"
    matches = list(re.finditer(patron_while_principal, script))

    if matches:
        m = matches[-1]
        idx_while_ini = m.start()
        idx_while_fin = m.end()

        cierre = "\n  end\nend"
        idx_cierre = script.rfind(cierre)

        if idx_cierre != -1 and idx_cierre > idx_while_ini:
            prefix = script[:idx_while_ini]
            body = script[idx_while_fin:idx_cierre].lstrip("\n")
            body = re.sub(r"(?m)^ {2}", "", body)
            script = prefix.rstrip() + "\n" + body.rstrip() + "\nend\n"

    script = script.rstrip() + f"\n\n{nombre_funcion}()\n"

    if not script.endswith("\n"):
        script += "\n"

    return script


def construir_script_vestido() -> str:
    q = ", ".join(str(v) for v in Q_VESTIDO)
    return f"""def rutina_vestido():
  movej([{q}], a={A_VESTIDO}, v={V_VESTIDO})
end

rutina_vestido()
"""


def enviar_script_al_ur3(script: str) -> Tuple[bool, str]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((ROBOT_IP, ROBOT_PORT))
            s.sendall(script.encode("utf-8"))
        return True, "Script enviado al UR3 correctamente"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def normalizar_texto(texto: str) -> str:
    t = (texto or "").strip().lower()
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
    for a, b in reemplazos.items():
        t = t.replace(a, b)
    return t


def detectar_tipo_prenda(texto: str) -> str:
    t = normalizar_texto(texto)

    if "playera" in t or "playeras" in t:
        return "playera"
    if "camisa" in t or "camisas" in t:
        return "camisa"
    if "vestido" in t or "vestidos" in t:
        return "vestido"

    return "desconocido"


def ejecutar_tarea_ur3() -> Tuple[bool, str]:
    global tipo_prenda_actual

    tipo_detectado = detectar_tipo_prenda(tipo_prenda_actual)
    print(f"[UR3] tipo_prenda_actual='{tipo_prenda_actual}'")
    print(f"[UR3] tipo_detectado='{tipo_detectado}'")

    try:
        if tipo_detectado == "playera":
            ruta_script = os.path.join(os.path.dirname(__file__), RUTA_SCRIPT_PLAYERA)

            if not os.path.exists(ruta_script):
                return False, f"No existe el archivo URScript: {ruta_script}"

            with open(ruta_script, "r", encoding="utf-8") as f:
                script_original = f.read()

            script_preparado = preparar_script_una_sola_vez(script_original)
            return enviar_script_al_ur3(script_preparado)

        elif tipo_detectado == "camisa":
            ruta_script = os.path.join(os.path.dirname(__file__), RUTA_SCRIPT_CAMISA)

            if not os.path.exists(ruta_script):
                return False, f"No existe el archivo URScript: {ruta_script}"

            with open(ruta_script, "r", encoding="utf-8") as f:
                script_original = f.read()

            script_preparado = preparar_script_una_sola_vez(script_original)
            return enviar_script_al_ur3(script_preparado)

        elif tipo_detectado == "vestido":
            script_vestido = construir_script_vestido()
            return enviar_script_al_ur3(script_vestido)

        else:
            ruta_script = os.path.join(os.path.dirname(__file__), RUTA_SCRIPT_CAMISA)

            if not os.path.exists(ruta_script):
                return False, f"No existe el archivo URScript: {ruta_script}"

            with open(ruta_script, "r", encoding="utf-8") as f:
                script_original = f.read()

            script_preparado = preparar_script_una_sola_vez(script_original)
            return enviar_script_al_ur3(script_preparado)

    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# Paso 10: Etapas cerradas del proceso
def etapa_1_inspeccion_timer_y_foto(order_id: str, usuario: str, indice: int) -> str:
    global ultima_foto_local

    print("[ETAPA 1] Inicio: Sensor1 -> Plancha -> Avance 45s -> Stop -> Foto")

    esperar_sensor1_y_activar_plancha(order_id)

    cambiar_etapa("AVANCE_45S_ANTES_FOTO")
    configurar_mascaras_sensores(s1=False, s2=False, s3=False)

    mover_motor_por_tiempo(
        TIEMPO_AVANCE_ANTES_FOTO,
        "ETAPA 1 / avance antes de foto"
    )

    cambiar_etapa("FOTO")
    configurar_mascaras_sensores(s1=False, s2=False, s3=False)

    ruta_local = tomar_y_guardar_foto(usuario, indice)
    ultima_foto_local = ruta_local
    print(f"[IA] Última foto local actualizada: {ultima_foto_local}")

    print("[ETAPA 1] Subiendo foto a backend...")
    resp_subida = render_subir_foto_pedido(order_id, ruta_local)
    print("[RENDER] Foto subida:", resp_subida)

    foto_info = resp_subida.get("foto", {})
    print(f"[RENDER] URL final guardada en pedido: {foto_info.get('url', '')}")

    print("[ETAPA 1] Completada. Sensor1 permanece ignorado.")
    return ruta_local


def etapa_2_avance_sensor2_y_ur3(order_id: str, indice: int, total: int):
    global ur3_ya_ejecutado, motor_continuo_activo, reinicio_despues_ur3
    global tipo_prenda_actual, ultima_foto_local

    print("[ETAPA 2] Inicio: avanzar hasta Sensor2, ignorando Sensor1 y Sensor3")

    cambiar_etapa("AVANCE_A_SENSOR2")
    configurar_mascaras_sensores(s1=False, s2=True, s3=False)

    ur3_ya_ejecutado = False
    motor_continuo_activo = True

    ok_start, msg_start = start_motor()
    if not ok_start:
        raise RuntimeError(f"No se pudo iniciar motor hacia Sensor2: {msg_start}")

    while motor_continuo_activo:
        valor_sensor2, msg_sensor2 = leer_sensor2()

        if valor_sensor2 is None:
            raise RuntimeError(f"Error leyendo sensor2: {msg_sensor2}")

        print(f"[SENSOR2] valor={valor_sensor2}, ur3_ya_ejecutado={ur3_ya_ejecutado}")

        if valor_sensor2 and not ur3_ya_ejecutado:
            if confirmar_sensor_estable(leer_sensor2, "sensor2", True):
                print("[SENSOR2] Detectado de forma estable -> detener carro y ejecutar UR3")
                break

        time.sleep(TIEMPO_POLL_CONTINUO)

    ok_stop, msg_stop = stop_motor()
    if not ok_stop:
        raise RuntimeError(f"No se pudo detener el motor en Sensor2: {msg_stop}")

    motor_continuo_activo = False

    # Cierre de etapa 2: Sensor1 y Sensor2 quedan ignorados. Sensor3 aún no se lee.
    configurar_mascaras_sensores(s1=False, s2=False, s3=False)
    cambiar_etapa("UR3")

    if pedido_actual_id:
        render_marcar_planchado(pedido_actual_id)

    if not ultima_foto_local:
        raise RuntimeError("No hay una foto local disponible para clasificar")

    print(f"[IA] Clasificando foto: {ultima_foto_local}")
    clase_predicha, confianza = clasificar_prenda_por_ia(ultima_foto_local)

    tipo_prenda_actual = clase_predicha
    print(f"[IA] Prenda detectada: {tipo_prenda_actual} | confianza={confianza:.4f}")

    # Se conserva tu modificación previa: ejecutar la rutina UR3 dos veces.
    for repeticion in range(1, 3):
        print(f"[UR3] Ejecutando rutina {repeticion}/2")
        ok_robot, msg_robot = ejecutar_tarea_ur3()
        print("[UR3]", ok_robot, msg_robot)

        if not ok_robot:
            raise RuntimeError(f"No se pudo ejecutar UR3 en repetición {repeticion}: {msg_robot}")

        print(f"[UR3] Esperando {TIEMPO_RUTINA_UR3} segundos para terminar rutina {repeticion}/2")
        time.sleep(TIEMPO_RUTINA_UR3)

    ur3_ya_ejecutado = True

    if pedido_actual_id and indice == total:
        render_marcar_listo_para_entrega(pedido_actual_id)

    print("[ETAPA 2] UR3 terminado. Ahora puede reiniciar el carro.")

    # Al reiniciar después del UR3, se desactiva la plancha / 000007 dentro de start_motor().
    reinicio_despues_ur3 = True


def etapa_3_sensor3_piston_y_stop():
    global sensor3_habilitado, motor_continuo_activo

    print("[ETAPA 3] Inicio: avanzar hasta Sensor3, pistón y avance final de 60s")

    cambiar_etapa("AVANCE_A_SENSOR3")
    configurar_mascaras_sensores(s1=False, s2=False, s3=True)

    motor_continuo_activo = True

    ok_start, msg_start = start_motor()
    if not ok_start:
        raise RuntimeError(f"No se pudo iniciar motor hacia Sensor3: {msg_start}")

    while motor_continuo_activo:
        valor_sensor3, msg_sensor3 = leer_sensor3()

        if valor_sensor3 is None:
            raise RuntimeError(f"Error leyendo sensor3: {msg_sensor3}")

        print(f"[SENSOR3] valor={valor_sensor3}")

        if valor_sensor3:
            if confirmar_sensor_estable(leer_sensor3, "sensor3", True):
                print("[SENSOR3] Detectado de forma estable -> detener motor")
                break

        time.sleep(TIEMPO_POLL_CONTINUO)

    ok_stop, msg_stop = stop_motor()
    if not ok_stop:
        raise RuntimeError(f"No se pudo detener motor en Sensor3: {msg_stop}")

    motor_continuo_activo = False

    # Requisito: al detectar Sensor3, detener y deshabilitar lecturas de Sensor3.
    configurar_mascaras_sensores(s1=False, s2=False, s3=False)

    cambiar_etapa("PISTON")

    print("[PISTON] Extendiendo pistón...")
    ok_ext, msg_ext = piston_extender()
    print(f"[PISTON] piston_extender -> ok={ok_ext}, msg={msg_ext}")
    if not ok_ext:
        raise RuntimeError(f"No se pudo extender pistón: {msg_ext}")

    time.sleep(TIEMPO_PISTON_ABIERTO)

    print("[PISTON] Retrayendo pistón...")
    ok_ret, msg_ret = piston_retraer()
    print(f"[PISTON] piston_retraer -> ok={ok_ret}, msg={msg_ret}")
    if not ok_ret:
        raise RuntimeError(f"No se pudo retraer pistón: {msg_ret}")

    time.sleep(TIEMPO_ESPERA_TRAS_CERRAR)
    piston_parar()

    cambiar_etapa("AVANCE_FINAL_60S")
    configurar_mascaras_sensores(s1=False, s2=False, s3=False)

    mover_motor_por_tiempo(
        TIEMPO_AVANCE_FINAL_STOP,
        "ETAPA 3 / avance final antes de STOP"
    )

    cambiar_etapa("STOP")
    configurar_mascaras_sensores(s1=False, s2=False, s3=False)
    print("[ETAPA 3] Completada. Proceso terminado en STOP.")


# Paso 11: Proceso de una prenda
def procesar_prenda(order_id: str, usuario: str, indice: int, total: int):
    global ur3_ya_ejecutado

    print(f"[PC] ===== Procesando prenda {indice}/{total} =====")

    ur3_ya_ejecutado = False

    etapa_1_inspeccion_timer_y_foto(order_id, usuario, indice)
    etapa_2_avance_sensor2_y_ur3(order_id, indice, total)
    etapa_3_sensor3_piston_y_stop()

    print(f"[PC] ===== Fin prenda {indice}/{total} =====")


# Paso 12: Rutina completa del pedido
def ejecutar_pedido(order_data: dict):
    global procesando, motor_continuo_activo, ur3_ya_ejecutado
    global pedido_actual_id, usuario_actual, cantidad_actual
    global estado_inicio_reportado, estado_planchado_reportado
    global tipo_prenda_actual
    global senal_000007_activada, reinicio_despues_ur3, modo_torreta
    global ultima_foto_local

    order_id = str(order_data["id"])
    cantidad = int(order_data.get("cantidad", 1))
    tipo_prenda = str(order_data.get("tipoPrenda", "")).strip().lower()
    usuario = obtener_usuario_desde_order(order_data)

    procesando = True
    motor_continuo_activo = False
    ur3_ya_ejecutado = False
    estado_inicio_reportado = False
    estado_planchado_reportado = False
    senal_000007_activada = False
    reinicio_despues_ur3 = False
    pedido_actual_id = order_id
    usuario_actual = usuario
    cantidad_actual = cantidad
    tipo_prenda_actual = tipo_prenda
    ultima_foto_local = ""

    try:
        print(
            f"[PC] Iniciando pedido id={order_id} | "
            f"usuario={usuario} | cantidad={cantidad} | tipo_prenda={tipo_prenda_actual}"
        )

        configurar_mascaras_sensores(s1=False, s2=False, s3=False)
        cambiar_etapa("STOP")
        stop_motor()
        modo_torreta = "rojo"
        actualizar_torreta()

        for indice in range(1, cantidad + 1):
            procesar_prenda(order_id, usuario, indice, cantidad)

        print(render_order_complete(order_id))
        print("[PC] Pedido finalizado")

        cambiar_etapa("STOP")
        configurar_mascaras_sensores(s1=False, s2=False, s3=False)
        modo_torreta = "rojo"
        actualizar_torreta()

    except Exception as e:
        print("[PC] Error en pedido:", e)

        try:
            stop_motor()
            modo_torreta = "rojo"
            actualizar_torreta()
        except Exception:
            pass

        try:
            desactivar_salida_000007()
            senal_000007_activada = False
        except Exception:
            pass

        try:
            render_order_error(order_id, str(e))
        except Exception:
            pass

        motor_continuo_activo = False
        procesando = False
        cambiar_etapa("STOP")
        configurar_mascaras_sensores(s1=False, s2=False, s3=False)

    finally:
        procesando = False
        motor_continuo_activo = False
        configurar_mascaras_sensores(s1=False, s2=False, s3=False)


# Paso 13: Loop principal
def loop_principal():
    global procesando, motor_continuo_activo, modo_torreta

    print("[PC] Worker maestro iniciado.")

    while True:
        try:
            if not procesando and not motor_continuo_activo:
                resp = render_get_next_order()
                order_data = resp.get("order")

                if order_data:
                    print(
                        f"[PC] Nuevo pedido detectado: "
                        f"{order_data.get('Folio')} | "
                        f"cantidad={order_data.get('cantidad')} | "
                        f"tipoPrenda={order_data.get('tipoPrenda')}"
                    )
                    ejecutar_pedido(order_data)
                else:
                    print("[PC] Sin pedidos pendientes")

        except Exception as e:
            print("[PC] Error en loop principal:", e)
            try:
                cambiar_etapa("STOP")
                configurar_mascaras_sensores(s1=False, s2=False, s3=False)
                modo_torreta = "rojo"
                actualizar_torreta()
            except Exception:
                pass

        time.sleep(TIEMPO_POLL)


# Paso 14: Main
if __name__ == "__main__":
    try:
        listar_puertos_serial()
        conectar_esp32()
        torreta_roja()
        configurar_mascaras_sensores(s1=False, s2=False, s3=False)
        cambiar_etapa("STOP")
        loop_principal()
    finally:
        try:
            torreta_apagar()
            piston_parar()
            stop_motor()
            desactivar_salida_000007()
        except Exception:
            pass
        desconectar_esp32()
