from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import threading
import os
import requests
import logging
import socket
import speech_recognition as sr
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

tracking_active = False
voice_active = False
tracking_lock = threading.Lock()
voice_lock = threading.Lock()

# IFTTT Configuration for Tapo L530B control
IFTTT_KEY = "ifttt key"
TURN_ON_URL = f"INSERT"
TURN_OFF_URL = f"INSERT"

# Twilio credentials
#A_SID = ''
#AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''
TO_PHONE_NUMBER = ''
client = Client(A_SID, AUTH_TOKEN)
BASE_URL = ''  # Update with your actual ngrok URL

# Reminder storage
reminders = []


def check_network_connectivity():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except socket.error:
        return False


def eye_tracking():
    global tracking_active
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            logging.error("Failed to open camera")
            with tracking_lock:
                tracking_active = False
            socketio.emit('gaze_update', {'x': None, 'y': None, 'dwell_progress': 0})
            return

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cam.set(cv2.CAP_PROP_FPS, 20)

        face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        screen_w, screen_h = pyautogui.size()
        smooth_factor = 0.19
        cursor_x, cursor_y = 0, 0
        sensitivity_scale = 1.5
        dwell_time_threshold = 4
        dwell_start_time = None
        last_update_time = 0
        update_interval = 0.1

        while tracking_active:
            current_time = time.time()
            ret, frame = cam.read()
            if not ret:
                logging.warning("Camera frame capture failed, retrying...")
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks

            if landmark_points:
                landmarks = landmark_points[0].landmark
                target_x = np.interp(landmarks[475].x, [0.4, 0.6], [0, screen_w])
                target_y = np.interp(landmarks[475].y, [0.4, 0.6], [0, screen_h])
                target_x = cursor_x + sensitivity_scale * (target_x - cursor_x)
                target_y = cursor_y + sensitivity_scale * (target_y - cursor_y)
                cursor_x = smooth_factor * cursor_x + (1 - smooth_factor) * target_x
                cursor_y = smooth_factor * cursor_y + (1 - smooth_factor) * target_y
                pyautogui.moveTo(cursor_x, cursor_y)

                if dwell_start_time is None:
                    dwell_start_time = time.time()
                dwell_progress = min((time.time() - dwell_start_time) / dwell_time_threshold, 1.0)
                if dwell_progress >= 1:
                    pyautogui.click()
                    dwell_start_time = None

                if current_time - last_update_time >= update_interval:
                    socketio.emit('gaze_update', {
                        'x': cursor_x,
                        'y': cursor_y,
                        'dwell_progress': dwell_progress,
                        'timestamp': current_time
                    })
                    last_update_time = current_time
            else:
                dwell_start_time = None
                if current_time - last_update_time >= update_interval:
                    socketio.emit('gaze_update',
                                  {'x': None, 'y': None, 'dwell_progress': 0.0, 'timestamp': current_time})
                    last_update_time = current_time
    except Exception as e:
        logging.error(f"Eye tracking error: {e}")
    finally:
        cam.release()
        cv2.destroyAllWindows()
        with tracking_lock:
            tracking_active = False


class VoiceCommandListener:
    def __init__(self):
        self.running = False
        self.recognizer = sr.Recognizer()
        self.commands = {
            "turn on bulb": lambda: turn_on_bulb_command(),
            "turn off bulb": lambda: turn_off_bulb_command(),
            "emergency sms": lambda: socketio.emit('voice_command', {'command': 'emergency_sms'}),
            "home automation": lambda: socketio.emit('voice_command', {'command': 'home_automation'}),
            "exit": lambda: stop_voice_mode_command(),
            "stop": lambda: self.stop()
        }

    def run(self):
        global voice_active
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                while self.running and voice_active:
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        recognized_text = self.recognizer.recognize_google(audio).lower().strip()
                        socketio.emit('voice_update', {'text': recognized_text})
                        for keyword, func in self.commands.items():
                            if keyword in recognized_text:
                                func()
                                socketio.emit('voice_update', {'text': f"Command executed: {keyword}"})
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        socketio.emit('voice_update', {'text': f"Speech Recognition API Error: {e}"})
        except Exception as e:
            socketio.emit('voice_update', {'text': f"An error occurred in voice recognition: {e}"})
        finally:
            with voice_lock:
                voice_active = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False


def turn_on_bulb_command():
    try:
        response = requests.post(TURN_ON_URL, timeout=10)
        socketio.emit('voice_update',
                      {'text': "Bulb turned on" if response.status_code == 200 else f"Failed: {response.text}"})
    except requests.RequestException as e:
        socketio.emit('voice_update', {'text': f"Network error: {str(e)}"})


def turn_off_bulb_command():
    try:
        response = requests.post(TURN_OFF_URL, timeout=10)
        socketio.emit('voice_update',
                      {'text': "Bulb turned off" if response.status_code == 200 else f"Failed: {response.text}"})
    except requests.RequestException as e:
        socketio.emit('voice_update', {'text': f"Network error: {str(e)}"})


def stop_voice_mode_command():
    global voice_active
    with voice_lock:
        voice_active = False
        voice_listener.stop()
    socketio.emit('voice_update', {'text': "Voice mode stopped"})
    socketio.emit('voice_command', {'command': 'exit'})


def check_reminders():
    while True:
        current_time = datetime.now()
        for reminder in reminders[:]:
            reminder_time = datetime.strptime(f"{reminder['date']} {reminder['time']}", "%Y-%m-%d %H:%M")
            if current_time >= reminder_time:
                send_reminder_sms(reminder['title'])
                reminders.remove(reminder)
        time.sleep(60)  # Check every minute


def send_reminder_sms(title):
    message_body = f"Reminder: {title}"
    try:
        client.messages.create(body=message_body, from_=TWILIO_PHONE_NUMBER, to=TO_PHONE_NUMBER)
        logging.info(f"Reminder SMS sent: {title}")
    except Exception as e:
        logging.error(f"Error sending reminder SMS: {str(e)}")


voice_listener = VoiceCommandListener()


@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')


@app.route('/services')
def services():
    return send_from_directory(os.getcwd(), 'services.html')


@app.route('/virtual-keyboard')
def virtual_keyboard():
    return send_from_directory(os.getcwd(), 'virtual_keyboard.html')


@app.route('/start-eye-tracking', methods=['POST'])
def start_eye_tracking():
    global tracking_active
    with tracking_lock:
        if not tracking_active:
            cam_test = cv2.VideoCapture(0)
            if not cam_test.isOpened():
                return "Camera unavailable", 500
            cam_test.release()
            tracking_active = True
            threading.Thread(target=eye_tracking, daemon=True).start()
    return "Eye tracking started"


@app.route('/stop-eye-tracking', methods=['POST'])
def stop_eye_tracking():
    global tracking_active
    with tracking_lock:
        tracking_active = False
    socketio.emit('gaze_update', {'x': None, 'y': None, 'dwell_progress': 0})
    return "Eye tracking stopped"


@app.route('/start-voice-mode', methods=['POST'])
def start_voice_mode():
    global voice_active
    with voice_lock:
        if not voice_active:
            voice_active = True
            voice_listener.start()
            threading.Thread(target=voice_listener.run, daemon=True).start()
    return "Voice mode started"


@app.route('/stop-voice-mode', methods=['POST'])
def stop_voice_mode():
    global voice_active
    with voice_lock:
        voice_active = False
        voice_listener.stop()
    socketio.emit('voice_update', {'text': "Voice mode stopped"})
    return "Voice mode stopped"


@app.route('/turn-on-bulb', methods=['POST'])
def turn_on_bulb():
    if not check_network_connectivity():
        return "Network connectivity issue", 500
    try:
        response = requests.post(TURN_ON_URL, timeout=10)
        return "Bulb turned on" if response.status_code == 200 else f"Error: {response.text}", 200 if response.status_code == 200 else 500
    except requests.RequestException as e:
        return f"Network error: {str(e)}", 500


@app.route('/turn-off-bulb', methods=['POST'])
def turn_off_bulb():
    if not check_network_connectivity():
        return "Network connectivity issue", 500
    try:
        response = requests.post(TURN_OFF_URL, timeout=10)
        return "Bulb turned off" if response.status_code == 200 else f"Error: {response.text}", 200 if response.status_code == 200 else 500
    except requests.RequestException as e:
        return f"Network error: {str(e)}", 500


@app.route('/api/send-emergency-sms', methods=['GET'])
def send_emergency_sms():
    message_body = 'Emergency, I need help'
    try:
        client.messages.create(body=message_body, from_=TWILIO_PHONE_NUMBER, to=TO_PHONE_NUMBER)
        return jsonify(success=True, message='Emergency SMS sent successfully!')
    except Exception as e:
        return jsonify(success=False, message=f'Error sending SMS: {str(e)}'), 500


@app.route('/api/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message', '').strip()
    message_type = data.get('type', 'sms')  # Default to SMS if type not specified
    if not message:
        return jsonify({'success': False, 'message': 'No message provided'}), 400

    try:
        if message_type == 'sms':
            # Send SMS
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=TO_PHONE_NUMBER
            )
            return jsonify({'success': True, 'message': f'SMS sent: {message}'})
        elif message_type == 'call':
            # Initiate call with the typed message
            call_url = f'{BASE_URL}/api/voice?message={message.replace(" ", "%20")}'
            call = client.calls.create(
                url=call_url,
                to=TO_PHONE_NUMBER,
                from_=TWILIO_PHONE_NUMBER
            )
            return jsonify({'success': True, 'message': f'Call initiated: {message}', 'sid': call.sid})
        else:
            return jsonify({'success': False, 'message': 'Invalid message type'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/set-reminder', methods=['POST'])
def set_reminder():
    data = request.get_json()
    title = data.get('title')
    date = data.get('date')
    time_str = data.get('time')
    if title and date and time_str:
        reminders.append({'title': title, 'date': date, 'time': time_str})
        return jsonify(success=True, message='Reminder set successfully!')
    return jsonify(success=False, message='Invalid reminder data'), 400


@app.route('/api/request-service', methods=['POST'])
def request_service():
    data = request.get_json()
    service_type = data.get('service')
    message = {
        'water': 'I need water',
        'food': 'I need food',
        'bathroom': 'I need to go to the bathroom'
    }.get(service_type, 'I need assistance')
    try:
        call_url = f'{BASE_URL}/api/voice?message={message.replace(" ", "%20")}'
        call = client.calls.create(url=call_url, to=TO_PHONE_NUMBER, from_=TWILIO_PHONE_NUMBER)
        return jsonify({'success': True, 'message': f'Call initiated. SID: {call.sid}'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error initiating call: {str(e)}'}), 500


@app.route('/api/voice', methods=['POST'])
def voice():
    message = request.args.get('message', 'I need assistance')
    resp = VoiceResponse()
    resp.say(message, voice='alice')
    return str(resp), 200, {'Content-Type': 'text/xml'}


@socketio.on('connect')
def handle_connect():
    emit('gaze_update', {'x': 0, 'y': 0, 'dwell_progress': 0})
    emit('voice_update', {'text': "Connected to voice and gaze updates"})


@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')


if __name__ == '__main__':
    threading.Thread(target=check_reminders, daemon=True).start()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)