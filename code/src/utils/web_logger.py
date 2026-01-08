import json
import os
import time
from datetime import datetime

class WebLogger:
    def __init__(self, log_file="config/web_logs.json"):
        self.log_file = log_file
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Ensure the log file exists and is initialized"""
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def log_status(self, message, status_type="info"):
        """Log a status message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "type": status_type,
            "message": message
        }
        
        try:
            #Read existing logs
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            #Add new log entry
            logs.append(log_entry)
            
            #Keep only last 100 entries to prevent file from growing too large
            logs = logs[-100:]
            
            #Write back to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Web logger error: {e}")

#Global instance
web_logger = WebLogger()