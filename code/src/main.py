import re 
import os
import sys
import json
from datetime import datetime
import socket
import threading

#Add both src directory and project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)

try:
    from audio.recorder import sound_record_advanced
    from audio.recorder import sound_record
    from audio.speech_to_text import speech_to_text
    from audio.text_to_speech import text_to_speech
    from llm.gemini_client import process_command_with_llm
    from ml.speaker_recognition import predict_speaker, predict_one_class
    from ml.command_classifier import predict_class, predict_multi_class
    from vehicle.navigation import execute_commands
except ImportError:
    from audio.recorder import sound_record_advanced
    from src.audio.recorder import sound_record
    from src.audio.speech_to_text import speech_to_text
    from src.audio.text_to_speech import text_to_speech
    from src.llm.gemini_client import process_command_with_llm
    from src.ml.speaker_recognition import predict_speaker, predict_one_class
    from src.ml.command_classifier import predict_class, predict_multi_class
    from src.vehicle.navigation import execute_commands

class CarStatusServer:
    def __init__(self, port=9999):
        self.port = port
        self.current_status = {
            "command": "idle",
            "timestamp": datetime.now().isoformat(),
            "details": {},
            "speech_text": "",
            "vehicle_state": "idle"
        }
        self.clients = []
        self.server_socket = None
        self.vehicle_status_file = "config/vehicle_status.json"
        self.speech_output_file = "config/speech_output.json"
        self.task_history_file = "config/task_history.json"
        self.ensure_status_files()

    def ensure_status_files(self):
        for file_path in [self.vehicle_status_file, self.speech_output_file, self.task_history_file]:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)

    def update_vehicle_state(self, state):
        self.current_status["vehicle_state"] = state
        self.current_status["timestamp"] = datetime.now().isoformat()
        
        status_entry = {
            "timestamp": self.current_status["timestamp"],
            "state": state
        }
        
        try:
            with open(self.vehicle_status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            status_data.append(status_entry)
            
            if len(status_data) > 100:
                status_data = status_data[-100:]
                
            with open(self.vehicle_status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def log_speech_output(self, speech_text, confidence=None):
        speech_entry = {
            "timestamp": datetime.now().isoformat(),
            "text": speech_text,
            "confidence": confidence
        }
        
        try:
            with open(self.speech_output_file, 'r', encoding='utf-8') as f:
                speech_data = json.load(f)
            speech_data.append(speech_entry)
            
            if len(speech_data) > 50:
                speech_data = speech_data[-50:]
                
            with open(self.speech_output_file, 'w', encoding='utf-8') as f:
                json.dump(speech_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def log_task_completion(self, task_type, command_details, success=True, duration=None):
        task_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "command": command_details,
            "success": success,
            "duration": duration
        }
        
        try:
            with open(self.task_history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            history_data.append(task_entry)
            
            if len(history_data) > 100:
                history_data = history_data[-100:]
                
            with open(self.task_history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def update_status(self, command, details=None, speech_text=""):
        self.current_status = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
            "speech_text": speech_text,
            "vehicle_state": self.current_status["vehicle_state"]
        }
        self.broadcast_status()

    def broadcast_status(self):
        message = json.dumps(self.current_status, ensure_ascii=False) + "\n"
        for client in self.clients[:]:
            try:
                client.send(message.encode('utf-8'))
            except:
                self.clients.remove(client)

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            print(f"Car status server started on port {self.port}")

            while True:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.clients.append(client_socket)
                    self.broadcast_status()
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    break
        except Exception as e:
            print(f"Failed to start status server: {e}")

#Global status server instance
status_server = CarStatusServer()

def start_command_server(status_server_instance):
    def handle_command_client(client_socket, address):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                try:
                    command = json.loads(data)
                    status_server_instance.update_status(
                        command.get('komut', 'received'),
                        command
                    )

                    response = {"status": "success", "message": "Command received"}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                
                except:
                    pass
        except:
            pass
class StdoutCapture:
    def __init__(self, log_file="config/status_logs.json"):
        self.log_file = log_file
        self.original_stdout = sys.stdout
        self.ensure_log_file()
    
    def ensure_log_file(self):
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def write(self, text):
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        if text.strip():
            self.log_to_file(text.strip())
    
    def log_to_file(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": message
        }
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            logs.append(log_entry)
            logs = logs[-100:]  # Keep only last 100 entries
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass  # Ignore logging errors
    
    def flush(self):
        self.original_stdout.flush()

def main():
    #Adjust paths based on where we're running from
    if os.path.basename(os.getcwd()) == 'src':
        # Running from src directory
        json_key_file = '../config/google_credentials.json'
        data_dir = '../data'
        models_dir = '../models'
    else:
        #Running from project root
        json_key_file = 'config/google_credentials.json'
        data_dir = 'data'
        models_dir = 'models'
    
    llm_api_key = "AIzaSyDAm4K_iBS-ptTHW8_YyW3kLWgjnMpzskA"
    
    #Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)

    audio_file = os.path.join(data_dir, 'recorded_sound.wav')


    try:
        command = sound_record_advanced(audio_file, status_server)
    except:
        print('Kullanıcın sesi kaydedilemedi.')

    predict_result = predict_one_class(audio_file, os.path.join(models_dir, 'modelV3/one_class_svm_model.joblib'))
    print(predict_result)

    if int(predict_result) == 1:
        #predict_result2 = predict_multi_class(audio_file, os.path.join(models_dir, 'modelV3/multiclass_model.joblib'), os.path.join(models_dir, 'modelV3/label_encoder.joblib'))
        #print(predict_result2)


    #result = predict_speaker(audio_file, os.path.join(models_dir, 'oneclass_svm_speaker.pkl'))
    #print(result)
    #result2 = predict_class(audio_file, os.path.join(models_dir, 'multiclass_with_others_svm.pkl'))
    #print(result2)

        try:
            if command:
                response = process_command_with_llm(command, llm_api_key)
            else:
                response = None
        except:
            print('Google LLM Modeline Bağlanılamadı veya Bir Sorun Oluştu')
            response = None

        
        if response:
            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            json_matchV2 = re.search(r'"""json\s*(.*?)\s*"""', response, re.DOTALL)
        else:
            json_match = None
            json_matchV2 = None

        commands_file = os.path.join(project_root, "config", "commands.json")
        
        if json_match:
            json_str = json_match.group(1)  
            
            try:
                json_data = json.loads(json_str)
                with open(commands_file, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)

                print(f"✅ JSON dosyası başarıyla kaydedildi: {commands_file}")
            
            except json.JSONDecodeError as e:
                print("❌ JSON ayrıştırılamadı:", e)

        elif json_matchV2:
            json_str = json_matchV2.group(1)  
            
            try:
                json_data = json.loads(json_str)
                with open(commands_file, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)

                print(f"✅ JSON dosyası başarıyla kaydedildi: {commands_file}")
            
            except json.JSONDecodeError as e:
                print("❌ JSON ayrıştırılamadı:", e)

        else:
            print("❌ JSON bloğu bulunamadı.")
            #Create fallback commands when APIs fail
            if not response:
                print("🔄 API yanıtı olmadığı için varsayılan komutlar oluşturuluyor...")
                default_commands = [
                    {
                        "komut": "ileri_git",
                        "hiz": 50,
                        "kosul": "3 saniye boyunca",
                        "aci": 0
                    }
                ]
                
                with open(commands_file, "w", encoding="utf-8") as f:
                    json.dump(default_commands, f, ensure_ascii=False, indent=2)
                print(f"✅ Varsayılan komutlar kaydedildi: {commands_file}")

        
        if response:
            cleaned_text = re.sub(r"```json\s*.*?\s*```", "", response, flags=re.DOTALL)
            cleaned_text = re.sub(r'"""json\s*(.*?)\s*"""', "", cleaned_text, flags=re.DOTALL)
            cleaned_text = cleaned_text.strip()

            print(f"response: {response}\n \n cleaned: {cleaned_text}")

            try:
                response_audio_file = os.path.join(data_dir, 'response_sound.mp3')
                text_to_speech(cleaned_text, response_audio_file, json_key_file)
                os.system(f"mpg123 {response_audio_file}") 
            except:
                print('Ses çıkışı başarısız.')
        else:
            print("API yanıtı alınamadığı için ses çıkışı yapılamıyor.")

    else: 
        if os.path.basename(os.getcwd()) == 'src':
        # Running from src directory
            data_dir = '../data'
        else:
            #Running from project root
            data_dir = 'data'

        response_audio_file = os.path.join(data_dir, 'kayitli.mp3')
        os.system(f"mpg123 {response_audio_file}") 

if __name__ == "__main__":
    stdout_capture = StdoutCapture()
    sys.stdout = stdout_capture
    
    main()
    execute_commands(status_server)