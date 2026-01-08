#-*- coding: utf-8 -*-
from flask import Flask, render_template, Response, stream_with_context
import os
import json
import time
import subprocess
import sys

app = Flask(__name__)
LOG_FILE = "config/commands.json"
STATUS_LOG_FILE = "config/status_logs.json"
VEHICLE_STATUS_FILE = "config/vehicle_status.json"
SPEECH_OUTPUT_FILE = "config/speech_output.json"
TASK_HISTORY_FILE = "config/task_history.json"

def yorumla_komut(komut_dict):
    if "komut" not in komut_dict:
        if "uyari" in komut_dict:
            return f"⚠️ Söylediklerini tam anlayamadım: \"{komut_dict['uyari']}\""
        elif "hata" in komut_dict:
            return f"❌ Hata: {komut_dict['hata']}"
        return json.dumps(komut_dict, ensure_ascii=False)

    komut = komut_dict["komut"]
    hiz = komut_dict.get("hiz", 100)
    kosul = komut_dict.get("kosul", "")
    aci = komut_dict.get("aci", 90)

    if komut == "ileri_git":
        if kosul == "engel_algilayana_kadar":
            return f"⬆️ Engel algılanana kadar {hiz} hızla ileri gidiliyor."
        else:
            return f"⬆️ {kosul} boyunca {hiz} hızla ileri gidiliyor."
    elif komut == "geri_git":
        if kosul == "engel_algilayana_kadar":
            return f"⬇️ Engel algılanana kadar {hiz} hızla geri gidiliyor."
        else:
            return f"⬇️ {kosul} boyunca {hiz} hızla geri gidiliyor."
    elif komut == "sola_don":
        return f"↩️ Sola doğru {aci}° dönülüyor."
    elif komut == "saga_don":
        return f"↪️ Sağa doğru {aci}° dönülüyor."
    elif komut == "tank_donus_sola":
        return f"🔄 Tank modu ile sola {aci}° dönülüyor."
    elif komut == "tank_donus_saga":
        return f"🔄 Tank modu ile sağa {aci}° dönülüyor."
    elif komut == "dur":
        return "⏹️ Duruluyor."

    return f"Bilinmeyen komut: {komut_dict}"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/stream')
def stream():
    def event_stream():
        last_mtime = 0
        cumulative_commands = []
        while True:
            try:
                mtime = os.path.getmtime(LOG_FILE)
                if mtime != last_mtime:
                    last_mtime = mtime
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        komutlar = json.load(f)

                    for komut in komutlar:
                        if komut not in cumulative_commands:
                            mesaj = yorumla_komut(komut)
                            yield f"data: {mesaj}\n\n"
                            cumulative_commands.append(komut)
            except Exception as e:
                yield f"data: ❌ Hata: {str(e)}\n\n"
            time.sleep(1)
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

@app.route('/status-stream')
def status_stream():
    def status_event_stream():
        last_mtime = 0
        last_size = 0
        startup_complete = False
        
        while True:
            try:
                if os.path.exists(STATUS_LOG_FILE):
                    mtime = os.path.getmtime(STATUS_LOG_FILE)
                    file_size = os.path.getsize(STATUS_LOG_FILE)
                    
                    if not startup_complete:
                        #On first load, just record current state without sending data
                        last_mtime = mtime
                        last_size = file_size
                        startup_complete = True
                    elif mtime != last_mtime or file_size != last_size:
                        #Only send new data after startup
                        last_mtime = mtime
                        last_size = file_size
                        
                        with open(STATUS_LOG_FILE, "r", encoding="utf-8") as f:
                            logs = json.load(f)
                        
                        #Send only the latest message
                        if logs:
                            log = logs[-1]
                            timestamp = log.get('timestamp', '')
                            message = log.get('message', '')
                            if message:
                                yield f"data: [{timestamp}] {message}\n\n"
            except Exception as e:
                yield f"data: [ERROR] Status log okuma hatası: {str(e)}\n\n"
            time.sleep(1)
    return Response(stream_with_context(status_event_stream()), mimetype="text/event-stream")

@app.route('/vehicle-status-stream')
def vehicle_status_stream():
    def vehicle_status_event_stream():
        last_mtime = 0
        while True:
            try:
                if os.path.exists(VEHICLE_STATUS_FILE):
                    mtime = os.path.getmtime(VEHICLE_STATUS_FILE)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        with open(VEHICLE_STATUS_FILE, "r", encoding="utf-8") as f:
                            status_data = json.load(f)
                        
                        recent_status = status_data[-3:] if len(status_data) > 3 else status_data
                        for status in recent_status:
                            timestamp = status.get('timestamp', '')
                            state = status.get('state', '')
                            if state:
                                yield f"data: [{timestamp}] Araç durumu: {state}\n\n"
            except Exception as e:
                yield f"data: [ERROR] Araç durum okuma hatası: {str(e)}\n\n"
            time.sleep(1)
    return Response(stream_with_context(vehicle_status_event_stream()), mimetype="text/event-stream")

@app.route('/speech-output-stream')
def speech_output_stream():
    def speech_event_stream():
        last_mtime = 0
        while True:
            try:
                if os.path.exists(SPEECH_OUTPUT_FILE):
                    mtime = os.path.getmtime(SPEECH_OUTPUT_FILE)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        with open(SPEECH_OUTPUT_FILE, "r", encoding="utf-8") as f:
                            speech_data = json.load(f)
                        
                        recent_speech = speech_data[-3:] if len(speech_data) > 3 else speech_data
                        for speech in recent_speech:
                            timestamp = speech.get('timestamp', '')
                            text = speech.get('text', '')
                            confidence = speech.get('confidence', 0)
                            if text:
                                if confidence is not None:
                                    yield f"data: [{timestamp}] \"{text}\" (güven: {confidence:.2f})\n\n"
                                else:
                                    yield f"data: [{timestamp}] \"{text}\"\n\n"
            except Exception as e:
                yield f"data: [ERROR] Ses tanıma okuma hatası: {str(e)}\n\n"
            time.sleep(1)
    return Response(stream_with_context(speech_event_stream()), mimetype="text/event-stream")

@app.route('/task-history-stream')
def task_history_stream():
    def task_history_event_stream():
        last_mtime = 0
        while True:
            try:
                if os.path.exists(TASK_HISTORY_FILE):
                    mtime = os.path.getmtime(TASK_HISTORY_FILE)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        with open(TASK_HISTORY_FILE, "r", encoding="utf-8") as f:
                            history_data = json.load(f)
                        
                        recent_tasks = history_data[-5:] if len(history_data) > 5 else history_data
                        for task in recent_tasks:
                            timestamp = task.get('timestamp', '')
                            task_type = task.get('task_type', '')
                            success = task.get('success', True)
                            duration = task.get('duration', 0)
                            status_icon = "✅" if success else "❌"
                            if task_type:
                                yield f"data: [{timestamp}] {status_icon} {task_type} ({duration:.1f}s)\n\n"
            except Exception as e:
                yield f"data: [ERROR] Görev geçmişi okuma hatası: {str(e)}\n\n"
            time.sleep(1)
    return Response(stream_with_context(task_history_event_stream()), mimetype="text/event-stream")

@app.route('/start-main')
def start_main():
    try:
        #Get project root directory (2 levels up from web/app.py)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        main_py_path = os.path.join(project_root, "src", "main.py")
        
        #Debug info
        current_dir = os.getcwd()
        app_file_path = os.path.abspath(__file__)
        
        #Check if files exist
        if not os.path.exists(main_py_path):
            return f"❌ main.py bulunamadı: {main_py_path} (current dir: {current_dir}, app: {app_file_path})"
        
        #Use virtual environment's Python (Raspberry Pi)
        venv_python = os.path.join(project_root, "venv", "bin", "python3")
        if not os.path.exists(venv_python):
            venv_python = "python3"  # fallback to system python
        
        process = subprocess.Popen([venv_python, main_py_path], cwd=project_root)
        
        return f"✅ Ses tanıma sistemi (sadece takım üyeleri) başarıyla başlatıldı! PID: {process.pid}"
    except Exception as e:
        return f"❌ Hata oluştu: {str(e)} (cwd: {os.getcwd()})"

@app.route('/start-main2')
def start_main2():
    try:
        #Get project root directory (2 levels up from web/app.py)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        main2_py_path = os.path.join(project_root, "src", "main2.py")
        
        #Debug info
        current_dir = os.getcwd()
        app_file_path = os.path.abspath(__file__)
        
        #Check if files exist
        if not os.path.exists(main2_py_path):
            return f"❌ main2.py bulunamadı: {main2_py_path} (current dir: {current_dir}, app: {app_file_path})"
        
        #Use virtual environment's Python (Raspberry Pi)
        venv_python = os.path.join(project_root, "venv", "bin", "python3")
        if not os.path.exists(venv_python):
            venv_python = "python3"  # fallback to system python
        
        process = subprocess.Popen([venv_python, main2_py_path], cwd=project_root)
        
        return f"✅ Ses tanıma sistemi (herkes için) başarıyla başlatıldı! PID: {process.pid}"
    except Exception as e:
        return f"❌ Hata oluştu: {str(e)} (cwd: {os.getcwd()})"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)