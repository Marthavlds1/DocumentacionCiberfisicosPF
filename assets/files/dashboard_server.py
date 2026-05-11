# Step 1: Dashboard server externo para observar tu rutina sin modificarla
# Ejecuta tu código original como subproceso y lee sus prints en consola.
# Requisito: guarda tu rutina original como "rutina_maestra.py" junto a este archivo
# o ejecuta con: ROUTINE_FILE="nombre_de_tu_codigo.py" python dashboard_server.py

import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, send_from_directory

# Step 2: Configuración
APP_DIR = Path(__file__).resolve().parent
WEB_DIR = APP_DIR / "web_dashboard"

ROUTINE_FILE = Path(os.getenv("ROUTINE_FILE", "rutina_maestra.py"))
if not ROUTINE_FILE.is_absolute():
    ROUTINE_FILE = APP_DIR / ROUTINE_FILE

HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
PORT = int(os.getenv("DASHBOARD_PORT", "5050"))
AUTO_START_ROUTINE = os.getenv("AUTO_START_ROUTINE", "1") == "1"
MAX_LOG_LINES = int(os.getenv("MAX_LOG_LINES", "120"))

# Step 3: Etapas reales detectadas en tu código original
STAGES: List[Dict[str, str]] = [
    {
        "key": "ESPERA_SENSOR1",
        "label": "Sensor 1",
        "description": "Espera detección inicial de prenda",
    },
    {
        "key": "AVANCE_45S_ANTES_FOTO",
        "label": "Avance foto",
        "description": "Motor avanza antes de captura",
    },
    {
        "key": "FOTO",
        "label": "Foto / IA",
        "description": "Captura, descarga y subida de foto",
    },
    {
        "key": "AVANCE_A_SENSOR2",
        "label": "Sensor 2",
        "description": "Avance hasta posición del UR3",
    },
    {
        "key": "UR3",
        "label": "UR3",
        "description": "Clasificación y rutina del robot",
    },
    {
        "key": "AVANCE_A_SENSOR3",
        "label": "Sensor 3",
        "description": "Avance hacia etapa de salida",
    },
    {
        "key": "PISTON",
        "label": "Pistón",
        "description": "Extensión, retracción y paro",
    },
    {
        "key": "AVANCE_FINAL_60S",
        "label": "Avance final",
        "description": "Salida final antes de STOP",
    },
]

STAGE_INDEX = {stage["key"]: i for i, stage in enumerate(STAGES)}
STAGE_LABEL = {stage["key"]: stage["label"] for stage in STAGES}

# Step 4: Estado compartido del dashboard
state_lock = threading.Lock()
subscribers_lock = threading.Lock()
subscribers: List[queue.Queue] = []
routine_process = None
reader_thread = None

state: Dict[str, Any] = {
    "dashboard_started_at": datetime.now().isoformat(timespec="seconds"),
    "last_update": datetime.now().isoformat(timespec="seconds"),
    "routine_file": str(ROUTINE_FILE),
    "routine_process_running": False,
    "routine_pid": None,
    "status": "idle",  # idle | running | success | error | stopped
    "current_stage": "STOP",
    "current_stage_label": "STOP / Reposo",
    "current_stage_index": -1,
    "last_non_stop_stage": "STOP",
    "last_non_stop_stage_label": "STOP / Reposo",
    "order_id": "",
    "usuario": "",
    "cantidad": "",
    "tipo_prenda": "",
    "confianza_ia": "",
    "ultima_foto_local": "",
    "motor_encendido": False,
    "senal_000007_activada": None,
    "sensor_masks": {"s1": False, "s2": False, "s3": False},
    "error": {
        "active": False,
        "stage": "",
        "stage_label": "",
        "message": "",
        "timestamp": "",
    },
    "logs": [],
    "stages": STAGES,
}

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_bool_from_on_off(value: str) -> bool:
    return value.strip().upper() == "ON"


def append_log(line: str) -> None:
    line = line.rstrip("\n")
    if not line:
        return

    record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "line": line,
    }

    state["logs"].append(record)
    if len(state["logs"]) > MAX_LOG_LINES:
        state["logs"] = state["logs"][-MAX_LOG_LINES:]


def set_stage(stage_key: str) -> None:
    stage_key = stage_key.strip()
    index = STAGE_INDEX.get(stage_key, -1)

    state["current_stage"] = stage_key
    state["current_stage_index"] = index

    if stage_key == "STOP":
        state["current_stage_label"] = "STOP / Reposo"
    else:
        state["current_stage_label"] = STAGE_LABEL.get(stage_key, stage_key)
        state["last_non_stop_stage"] = stage_key
        state["last_non_stop_stage_label"] = STAGE_LABEL.get(stage_key, stage_key)
        if not state["error"]["active"]:
            state["status"] = "running"


def clear_error() -> None:
    state["error"] = {
        "active": False,
        "stage": "",
        "stage_label": "",
        "message": "",
        "timestamp": "",
    }


def set_error(message: str) -> None:
    failed_stage = state.get("last_non_stop_stage") or state.get("current_stage") or "STOP"
    failed_label = STAGE_LABEL.get(failed_stage, failed_stage)

    state["status"] = "error"
    state["error"] = {
        "active": True,
        "stage": failed_stage,
        "stage_label": failed_label,
        "message": message.strip() or "Error no especificado",
        "timestamp": now_iso(),
    }


def snapshot_state() -> Dict[str, Any]:
    with state_lock:
        return json.loads(json.dumps(state, ensure_ascii=False))


def broadcast_state() -> None:
    payload = json.dumps(snapshot_state(), ensure_ascii=False)

    with subscribers_lock:
        dead_clients = []
        for client_queue in subscribers:
            try:
                client_queue.put_nowait(payload)
            except Exception:
                dead_clients.append(client_queue)

        for client_queue in dead_clients:
            if client_queue in subscribers:
                subscribers.remove(client_queue)


def parse_log_line(raw_line: str) -> None:
    line = raw_line.strip()
    if not line:
        return

    with state_lock:
        append_log(line)
        state["last_update"] = now_iso()

        # Etapa actual: ya existe en tu función cambiar_etapa()
        match_stage = re.search(r"\[ESTADO\]\s*Etapa actual\s*->\s*(.+)$", line)
        if match_stage:
            set_stage(match_stage.group(1))

        # Inicio de pedido
        match_order = re.search(
            r"\[PC\]\s*Iniciando pedido id=(.*?)\s*\|\s*usuario=(.*?)\s*\|\s*cantidad=(.*?)\s*\|\s*tipo_prenda=(.*)$",
            line,
        )
        if match_order:
            clear_error()
            state["status"] = "running"
            state["order_id"] = match_order.group(1).strip()
            state["usuario"] = match_order.group(2).strip()
            state["cantidad"] = match_order.group(3).strip()
            state["tipo_prenda"] = match_order.group(4).strip()
            state["confianza_ia"] = ""
            state["ultima_foto_local"] = ""
            state["last_non_stop_stage"] = "STOP"
            state["last_non_stop_stage_label"] = "STOP / Reposo"

        # Nuevo pedido detectado, útil cuando aún no entra a ejecutar_pedido()
        if "[PC] Nuevo pedido detectado:" in line and not state["error"]["active"]:
            state["status"] = "running"

        # Pedido terminado correctamente
        if "[PC] Pedido finalizado" in line:
            clear_error()
            state["status"] = "success"

        # Sin pedidos pendientes
        if "[PC] Sin pedidos pendientes" in line and not state["error"]["active"]:
            if not state["routine_process_running"]:
                state["status"] = "stopped"
            elif state["current_stage"] == "STOP":
                state["status"] = "idle"

        # Motor
        if "[PLC] Motor iniciado" in line:
            state["motor_encendido"] = True
        elif "[PLC] Motor detenido" in line:
            state["motor_encendido"] = False

        # Señal 000007 / plancha
        if "PLANCHA ACTIVADA" in line:
            state["senal_000007_activada"] = True
        elif "PLANCHA DESACTIVADA" in line:
            state["senal_000007_activada"] = False

        # Máscaras de sensores
        match_masks = re.search(
            r"\[MASCARAS\].*S1=(ON|OFF).*S2=(ON|OFF).*S3=(ON|OFF)",
            line,
        )
        if match_masks:
            state["sensor_masks"] = {
                "s1": safe_bool_from_on_off(match_masks.group(1)),
                "s2": safe_bool_from_on_off(match_masks.group(2)),
                "s3": safe_bool_from_on_off(match_masks.group(3)),
            }

        # Foto local
        match_photo = re.search(r"\[IA\]\s*Última foto local actualizada:\s*(.+)$", line)
        if match_photo:
            state["ultima_foto_local"] = match_photo.group(1).strip()

        # Clasificación IA
        match_ai = re.search(
            r"\[IA\]\s*Prenda detectada:\s*(.*?)\s*\|\s*confianza=([0-9.]+)",
            line,
        )
        if match_ai:
            state["tipo_prenda"] = match_ai.group(1).strip()
            state["confianza_ia"] = match_ai.group(2).strip()

        # Errores: se guarda la etapa en la que estaba antes de que tu código mande STOP
        match_error_order = re.search(r"\[PC\]\s*Error en pedido:\s*(.+)$", line)
        if match_error_order:
            set_error(match_error_order.group(1))

        match_error_loop = re.search(r"\[PC\]\s*Error en loop principal:\s*(.+)$", line)
        if match_error_loop:
            set_error(match_error_loop.group(1))

        # Errores no controlados del proceso Python
        if "Traceback (most recent call last):" in line:
            set_error("Traceback no controlado en la rutina. Revisa el log técnico.")

    broadcast_state()


def read_process_output(proc: subprocess.Popen) -> None:
    global routine_process

    try:
        assert proc.stdout is not None
        for raw_line in proc.stdout:
            parse_log_line(raw_line)
    except Exception as exc:
        parse_log_line(f"[DASHBOARD] Error leyendo salida de rutina: {exc}")
    finally:
        return_code = proc.poll()
        with state_lock:
            state["routine_process_running"] = False
            state["routine_pid"] = None
            state["last_update"] = now_iso()
            append_log(f"[DASHBOARD] Proceso de rutina terminado. return_code={return_code}")
            if state["status"] not in ["error", "success"]:
                state["status"] = "stopped"
        broadcast_state()


def start_routine_process() -> bool:
    global routine_process, reader_thread

    with state_lock:
        if routine_process is not None and routine_process.poll() is None:
            return True

        state["routine_file"] = str(ROUTINE_FILE)
        state["last_update"] = now_iso()

    if not ROUTINE_FILE.exists():
        with state_lock:
            set_error(
                f"No encontré la rutina original en: {ROUTINE_FILE}. "
                "Guarda tu código como rutina_maestra.py o define ROUTINE_FILE."
            )
            append_log(f"[DASHBOARD] Archivo no encontrado: {ROUTINE_FILE}")
        broadcast_state()
        return False

    routine_process = subprocess.Popen(
        [sys.executable, "-u", str(ROUTINE_FILE)],
        cwd=str(ROUTINE_FILE.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    with state_lock:
        clear_error()
        state["status"] = "running"
        state["routine_process_running"] = True
        state["routine_pid"] = routine_process.pid
        state["last_update"] = now_iso()
        append_log(f"[DASHBOARD] Rutina iniciada como subproceso PID={routine_process.pid}")

    reader_thread = threading.Thread(target=read_process_output, args=(routine_process,), daemon=True)
    reader_thread.start()
    broadcast_state()
    return True


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path: str):
    return send_from_directory(WEB_DIR, path)


@app.route("/api/status")
def api_status():
    return jsonify(snapshot_state())


@app.route("/api/start", methods=["POST"])
def api_start():
    ok = start_routine_process()
    return jsonify({"ok": ok, "state": snapshot_state()})


@app.route("/events")
def events():
    client_queue: queue.Queue = queue.Queue(maxsize=20)
    with subscribers_lock:
        subscribers.append(client_queue)

    def stream():
        try:
            yield f"data: {json.dumps(snapshot_state(), ensure_ascii=False)}\n\n"
            while True:
                try:
                    payload = client_queue.get(timeout=20)
                    yield f"data: {payload}\n\n"
                except queue.Empty:
                    yield ": keep-alive\n\n"
        finally:
            with subscribers_lock:
                if client_queue in subscribers:
                    subscribers.remove(client_queue)

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    if AUTO_START_ROUTINE:
        start_routine_process()

    print(f"[DASHBOARD] Abre el tablero en http://localhost:{PORT}")
    print(f"[DASHBOARD] Rutina observada: {ROUTINE_FILE}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
