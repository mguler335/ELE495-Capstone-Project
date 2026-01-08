# 🚗 Voice-Controlled Autonomous Mini Vehicle (ELE 495 Capstone Project)

This project is a smart autonomous vehicle that can understand **Turkish natural language voice commands** and act accordingly using AI. The system interprets spoken commands, converts them into basic movement instructions, and controls a mobile robot accordingly — all while giving real-time voice feedback in Turkish.

---

## 🎯 Key Features

- Understands Turkish speech in natural language.  
- Uses Google Gemini to extract intent from sentences.  
- Sends motor commands in structured JSON format.  
- Moves autonomously based on commands and obstacle feedback.  
- Gives spoken responses using Text-to-Speech (TTS).  
- Real-time system monitoring through a web interface.

---

## 🧠 System Flow

1. User gives a voice command via wireless microphone.  
2. Raspberry Pi uses STT to convert speech to text.  
3. GPT-4 processes the sentence and generates JSON control data.  
4. Raspberry Pi parses JSON and moves the vehicle accordingly.  
5. Ultrasonic sensors detect obstacles during movement.  
6. Web interface shows current command, system status, and logs.  

📌 See diagram below:
<p align="center">
  <img width="650" alt="Account ownership flow (1)" src="https://github.com/user-attachments/assets/4ff87375-291d-4656-a9ba-2594944288f4" />
</p>

---

## 🖥 Web Interface

A Flask-based dashboard provides:

- Command logs.  
- Current vehicle status (moving, stopped, turning, etc.).  
- JSON command preview.  
- Live STT output.  
- Error messages and feedback.
<p align="center">
  <img width="650" height="507" alt="Ekran Resmi 2025-07-13 13 25 53" src="https://github.com/user-attachments/assets/7418f97b-9aa6-446d-b5d4-93619dc0f78d" />
</p>

---

## 🚘 Final Prototype Image

<p align="center">
  <img width="650" alt="Final Vehicle Image" src="https://github.com/user-attachments/assets/cad90b9d-c54d-490d-a50d-123af8b792b4" />
</p>

---

## 🎬 Demo Video

➡️ https://youtu.be/ZY2JyAAKZ6M

---

## 🚀 Setup and Installation

### Prerequisites
- Python 3.11 or higher.
- Raspberry Pi (for hardware components).
- Google Cloud account with Speech-to-Text and Text-to-Speech APIs enabled.
- Gemini API key.

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ELE495-2425Summer/capstoneproject-karasimsek-grup-8.git
   cd capstoneproject-karasimsek-grup-8/code
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Cloud credentials:**
   - Create a Google Cloud project and enable Speech-to-Text and Text-to-Speech APIs.
   - Create a service account and download the JSON credentials file.
   - Replace the placeholder values in `code/config/google_credentials.json` with your actual credentials.

5. **Set up Gemini API:**
   - Get your Gemini API key from Google AI Studio.
   - Configure the API key in your environment or code.

6. **Hardware setup (for Raspberry Pi):**
   - Connect motors, sensors, and microphone according to your vehicle design.
   - Update GPIO pin configurations in the code as needed.

### Running the Application

1. **Start the web interface:**
   ```bash
   cd code/src/web
   screen -S flask-app
   python app.py
   ```
   Press `Ctrl+A` then `D` to detach from screen session.

2. **Run the main application:**
   ```bash
   cd code/src
   python main.py
   ```

---

## 📁 Folder Structure

```bash
code/
├── src/
│   ├── main.py
│   ├── main2.py
│   ├── audio/
│   │   ├── recorder.py
│   │   ├── speech_to_text.py
│   │   └── text_to_speech.py
│   ├── llm/
│   │   └── gemini_client.py
│   ├── ml/
│   │   ├── command_classifier.py
│   │   ├── feature_extraction.py
│   │   └── speaker_recognition.py
│   ├── vehicle/
│   │   ├── motor_control.py
│   │   ├── navigation.py
│   │   ├── pid_control.py
│   │   └── sensors.py
│   ├── web/
│   │   ├── app.py
│   │   └── templates/
│   │       └── index.html
│   └── utils/
│       └── web_logger.py
├── config/
│   ├── commands.json
│   ├── status_logs.json
│   ├── vehicle_status.json
│   └── task_history.json
├── models/
│   ├── modelV2/
│   └── modelV3/
├── data/
├── tests/
└── requirements.txt
```