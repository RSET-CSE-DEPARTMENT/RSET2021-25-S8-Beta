import socket
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from deepface import DeepFace
import threading
import time
from collections import deque
from sklearn.tree import DecisionTreeClassifier
# Server details (update IP with actual server laptop IP)
SERVER_IP = "10.0.7.171"  # Replace with actual IP of the server
SERVER_PORT = 5000

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Load trained models
violence_model = load_model("final_violence_model.keras")
gender_model = load_model("gender_detection_model.keras")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Parameters
IMG_SIZE = (224, 224)
SEQUENCE_LENGTH = 10
FRAME_QUEUE = deque(maxlen=SEQUENCE_LENGTH)

# Decision tree for abuse detection
X = [[0, 0], [0, 1], [1, 0], [1, 1]]  # [is_female, is_not_happy]
Y = [0, 0, 0, 1]  # Alert only if female and not happy
decision_tree = DecisionTreeClassifier()
decision_tree.fit(X, Y)

# Global variables
violence_detected = False
abuse_alert = False
text_display = ""
alert_sent = False  # Flag to track if alert was sent
alert_start_time = None  # Track time of first detection

# Background subtractor for motion detection
fgbg = cv2.createBackgroundSubtractorMOG2()

# Function to preprocess frames
def preprocess_frame(frame):
    frame = cv2.resize(frame, IMG_SIZE)
    frame = preprocess_input(frame)
    return frame

# Function to detect gender & expression asynchronously
def analyze_face(frame):
    global abuse_alert, text_display

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_crop = frame[y:y + h, x:x + w]
        if face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
            continue

        # Gender detection
        face_resized = cv2.resize(face_crop, (96, 96))
        face_resized = face_resized.astype("float") / 255.0
        face_resized = img_to_array(face_resized)
        face_resized = np.expand_dims(face_resized, axis=0)

        gender_conf = gender_model.predict(face_resized)[0]
        gender_label = "woman" if np.argmax(gender_conf) == 1 else "man"
        is_female = 1 if gender_label == "woman" else 0

        # Expression detection (DeepFace)
        try:
            result = DeepFace.analyze(face_crop, actions=['emotion'], enforce_detection=False)
            emotion = result[0]['dominant_emotion']
            is_not_happy = 1 if emotion != "happy" else 0
        except:
            is_not_happy = 0  # If face analysis fails, assume neutral

        # Decision tree prediction
        abuse_alert = decision_tree.predict([[is_female, is_not_happy]])[0]

        # Display labels
        label = f"{gender_label}, {emotion}"
        color = (0, 255, 0) if not abuse_alert else (0, 0, 255)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Final alert text
        text_display = "ABUSE AGAINST WOMEN DETECTED" if abuse_alert else "VIOLENCE DETECTED"

        # Send abuse alert to server
        if abuse_alert:
            abuse_message = f"ALERT from {socket.gethostname()} - ABUSE DETECTED ({gender_label}, {emotion})"
            client_socket.sendto(abuse_message.encode(), (SERVER_IP, SERVER_PORT))

# Start video capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Motion detection using background subtraction
    fg_mask = fgbg.apply(frame)
    motion_detected = np.mean(fg_mask) > 10  # Lower threshold from 15 to 10

    # Preprocess frame and add to queue
    processed_frame = preprocess_frame(frame)
    FRAME_QUEUE.append(processed_frame)

    if len(FRAME_QUEUE) == SEQUENCE_LENGTH:
        input_sequence = np.expand_dims(np.array(FRAME_QUEUE), axis=0)
        prediction = violence_model.predict(input_sequence)[0][0]

        # Adjust threshold for better accuracy
        violence_detected = prediction > 0.50 and motion_detected  # Lower threshold from 0.7 to 0.55

        # Debugging: Print the violence prediction score
        print(f"Violence Score: {prediction:.4f} | Motion: {motion_detected}")

        if violence_detected:
            if alert_start_time is None:
                alert_start_time = time.time()  # Start timing

            elapsed_time = time.time() - alert_start_time
            if elapsed_time > 5 and not alert_sent:  # Send alert after 5 seconds
                alert_message = f"ALERT from {socket.gethostname()} - VIOLENCE DETECTED (Score: {prediction:.4f})"
                client_socket.sendto(alert_message.encode(), (SERVER_IP, SERVER_PORT))
                alert_sent = True  # Prevent duplicate alerts

            # Analyze gender & emotion in a separate thread
            analysis_thread = threading.Thread(target=analyze_face, args=(frame,))
            analysis_thread.start()
        
        else:
            alert_start_time = None  # Reset timing when violence stops
            alert_sent = False  # Allow new alert when violence starts again

    # Display result
    if violence_detected:
        color = (0, 0, 255) if abuse_alert else (0, 165, 255)
        cv2.putText(frame, text_display, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Violence & Abuse Detection", frame)

    # Exit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()