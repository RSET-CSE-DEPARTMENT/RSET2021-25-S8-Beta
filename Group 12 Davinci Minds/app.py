#import libraries
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, session, Response, jsonify
import sqlite3
import os
import cv2
import mediapipe as mp
import numpy as np
import time
import requests
from moviepy.editor import VideoFileClip
import whisper
import json
import google.generativeai as genai
from collections import defaultdict
import json
import networkx as nx
import matplotlib.pyplot as plt
import time
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, request, jsonify, render_template
import io
from flask import send_file
import re


import os
os.environ["PATH"] += os.pathsep + "C:\\ffmpeg\\bin"


model = whisper.load_model("base")


genai.configure(api_key="AIzaSyALSQg60p7vqNBdn5SHpFKhu0AE8lpe1cE")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 0.7,
  "top_p": 1,
  "top_k": 50,
  "max_output_tokens": 1024,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]







mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
pose = mp_pose.Pose(static_image_mode=False)


EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3
MOUTH_AR_THRESH = 0.6
ATTENTION_LOSS_FRAMES = 10

EYE_COUNTER = 0
YAWN_COUNTER = 0
DROWSY_COUNTER = 0

face_not_detected_counter = 0
fps = 0.0
at = 0
# Head pose estimation reference points
head_model_points = np.array([
    (0.0, 0.0, 0.0),  # Nose tip
    (0.0, -330.0, -65.0),  # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),  # Right eye right corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0, -150.0, -125.0)  # Right mouth corner
], dtype=np.float32)

# Camera matrix for head pose estimation
focal_length = 1.0
camera_matrix = np.array([
    [focal_length, 0, 0.5],
    [0, focal_length, 0.5],
    [0, 0, 1]
], dtype=np.float32)

# Helper function to calculate the distance between two points
def calculate_distance(p1, p2, img_shape):
    h, w, _ = img_shape
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Helper function to calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye_landmarks, img_shape):
    vertical_1 = calculate_distance(eye_landmarks[1], eye_landmarks[5], img_shape)
    vertical_2 = calculate_distance(eye_landmarks[2], eye_landmarks[4], img_shape)
    horizontal = calculate_distance(eye_landmarks[0], eye_landmarks[3], img_shape)
    return (vertical_1 + vertical_2) / (2.0 * horizontal)

# Helper function to calculate Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth_landmarks, img_shape):
    if len(mouth_landmarks) < 10:  # Ensure we have enough landmarks
        return 0.0  # Return 0 if not enough landmarks

    vertical = calculate_distance(mouth_landmarks[3], mouth_landmarks[9], img_shape)
    horizontal = calculate_distance(mouth_landmarks[0], mouth_landmarks[6], img_shape)
    return vertical / horizontal

# Head pose estimation helper function
def get_head_pose(image_points, frame_shape):
    dist_coeffs = np.zeros((4, 1))  # No distortion coefficients
    success, rotation_vector, translation_vector = cv2.solvePnP(
        head_model_points, image_points, camera_matrix, dist_coeffs
    )
    return success, rotation_vector, translation_vector


app = Flask(__name__)
app.secret_key = '123'  

YOUTUBE_API_KEY = "AIzaSyDwHyR0yeIMnZUOVaz8XkjMtxX8dWOqh28"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

DB_NAME = "users.db"
DB_NAME_PARENT = "parents.db"
DB_NAME_SCIENCE = "science.db"
DB_NAME_ENGLISH = "english.db"
DB_NAME_MATH = "math.db"

# Function to initialize the database

def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    password TEXT NOT NULL,
                    class TEXT NOT NULL,
                    terms_accepted BOOLEAN NOT NULL
                )
            ''')
            conn.commit()


# Function to initialize the database
def init_parent_db():
    if not os.path.exists(DB_NAME_PARENT):
        with sqlite3.connect(DB_NAME_PARENT) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    parent_name TEXT NOT NULL,
                    parent_email TEXT NOT NULL,
                    parent_contact TEXT NOT NULL,
                    password TEXT NOT NULL,
                    terms_accepted BOOLEAN NOT NULL
                )
            ''')
            conn.commit()




######## SUBJECT DBs ########################################
def init_science_db():
    if not os.path.exists(DB_NAME_SCIENCE):
        with sqlite3.connect(DB_NAME_SCIENCE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS science (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tdate TEXT NOT NULL,
                    username TEXT NOT NULL,
                    score TEXT NOT NULL,
                    attention TEXT NOT NULL
                )
            ''')
            conn.commit()




def init_english_db():
    if not os.path.exists(DB_NAME_ENGLISH):
        with sqlite3.connect(DB_NAME_ENGLISH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS english (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tdate TEXT NOT NULL,
                    username TEXT NOT NULL,
                    score TEXT NOT NULL,
                    attention TEXT NOT NULL
                )
            ''')
            conn.commit()



def init_math_db():
    if not os.path.exists(DB_NAME_MATH):
        with sqlite3.connect(DB_NAME_MATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS math (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tdate TEXT NOT NULL,
                    username TEXT NOT NULL,
                    score TEXT NOT NULL,
                    attention TEXT NOT NULL
                )
            ''')
            conn.commit()



def get_user_details(username):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "full_name": user[2],
                    "email": user[3],
                    "contact": user[4],
                    "password": user[5],  # Avoid printing passwords for security
                    "class": user[6],
                    "terms_accepted": user[7]
                }
            else:
                return "User not found"
    except sqlite3.Error as e:
        return f"Database error: {e}"

# Initialize the database when the app starts
init_db()
init_parent_db()
init_science_db()
init_english_db()
init_math_db()



UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def landing():
    return render_template('home.html')

@app.route('/upload')
def upload():
    return render_template('upload2.html')

@app.route('/landing2')
def landing2():
    error = request.args.get("error") 
    return render_template('home.html', error=error)


@app.route('/login')
def login():
    error = request.args.get("error")  # Capture error message
    return render_template('login.html', error=error)


@app.route('/parent')
def parent():
    return render_template('loginParent.html')


@app.route('/signup_parent')
def signup_parent():
    error = request.args.get("error")  # Capture error message
    return render_template('signupParent.html', error=error)



@app.route('/login2', methods=['POST'])
def login2():
    if request.method == 'POST':
        return render_template('login.html', error=error)

@app.route('/signup')
def signup():
    error = request.args.get("error")  # Capture error message
    return render_template('signup.html', error=error)

@app.route('/signupsuccess', methods=['POST'])
def signupsuccess():
    if request.method == 'POST':
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        contact = request.form.get("contact")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_class = request.form.get("class")
        terms_accepted = request.form.get("terms") is not None

        if not username:
            return redirect(url_for("signup", error="Username cannot be empty."))

        if password != confirm_password:
            return redirect(url_for("signup", error="Passwords do not match."))

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return redirect(url_for("signup", error="Username already exists. Please choose a different one."))

            cursor.execute('''
                INSERT INTO users (username, full_name, email, contact, password, class, terms_accepted) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, full_name, email, contact, password, user_class, terms_accepted))
            conn.commit()

        session["username"] = username
        session["full_name"] = full_name
        session["email"] = email

        return render_template('login.html', error="Signup successful!")

'''@app.route('/home', methods=['POST'])
def home():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        print(username, password)


    return render_template('home2.html')'''



@app.route('/signupsuccess_parent', methods=['POST'])
def signupsuccess_parent():
    if request.method == 'POST':
        username = request.form.get("username")
        parent_name = request.form.get("parent_name")
        parent_email = request.form.get("parent_email")
        parent_contact = request.form.get("parent_contact")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        terms_accepted = request.form.get("terms") is not None
        print(username, parent_name, parent_email, parent_contact, password)

        if not username:
            return redirect(url_for("signup_parent", error="Username cannot be empty."))

        if password != confirm_password:
            return redirect(url_for("signup_parent", error="Passwords do not match."))

        # Step 1: Check if student username exists in DB_NAME
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if not existing_user:
                return redirect(url_for("signup_parent", error="Student doesn't exist, Please enter a valid student username."))

        # Step 2: Check if parent details already exist in DB_NAME_PARENT
        with sqlite3.connect(DB_NAME_PARENT) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parents WHERE username = ?", (username,))
            parent_exists = cursor.fetchone()

            if parent_exists:
                return redirect(url_for("signup_parent", error="Parent details for this student already exist."))

            # Step 3: Insert new parent details
            cursor.execute('''
                INSERT INTO parents (username, parent_name, parent_email, parent_contact, password, terms_accepted)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, parent_name, parent_email, parent_contact, password, terms_accepted))
            conn.commit()

        return render_template('loginParent.html', error="Signup successful!")




@app.route('/home', methods=['POST'])
def home():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                return redirect(url_for('login', error="Username does not exist."))

            # You may also add password verification here
            if user[5] != password:  # Assuming password is at index 5
                return redirect(url_for('login', error="Incorrect password."))
        session["username"] = username
        session["login_time"] = datetime.now().isoformat()
        return render_template('home2.html')



########################################## PARENT PORTAL #####################################################3

@app.route('/parent_portal', methods=['POST'])
def parent_portal():
    if request.method == 'POST':
        username = request.form.get("username")
        parent_name = request.form.get("parent_name")
        password = request.form.get("password")

        with sqlite3.connect(DB_NAME_PARENT) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parents WHERE parent_name = ?", (parent_name,))
            parent = cursor.fetchone()

            if not parent:
                return redirect(url_for('parent2', error="Parent name does not exist."))
            if parent[5] != password:
                return redirect(url_for('parent2', error="Incorrect password."))

        session["parent_name"] = parent_name
        session["student"] = username

        # Fetch subject performance data (raw score instead of percentage)
        def fetch_subject_data(db_name, subject):
            try:
                with sqlite3.connect(db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT tdate, score FROM {subject} WHERE username = ? ORDER BY tdate DESC LIMIT 15", (username,))
                    rows = cursor.fetchall()
                    data = [
                        {
                            "date": row[0],
                            "score": int(row[1].split('/')[0])
                        }
                        for row in rows
                    ][::-1]
                    print(f"{subject} data: {data}")
                    return data
            except sqlite3.Error as e:
                print(f"Database error for {subject}: {e}")
                return []

        math_data = fetch_subject_data(DB_NAME_MATH, "math")
        science_data = fetch_subject_data(DB_NAME_SCIENCE, "science")
        english_data = fetch_subject_data(DB_NAME_ENGLISH, "english")

        # Fetch attention data and calculate focus level and engagement
        def fetch_attention_data():
            try:
                with sqlite3.connect(DB_NAME_ATTENTION) as conn:
                    cursor = conn.cursor()

                    # Fetch the last 5 sessions
                    cursor.execute("SELECT login_time, logout_time, attention_duration FROM attention WHERE username = ? ORDER BY logout_time DESC LIMIT 5", (username,))
                    rows = cursor.fetchall()
                    attention_list = [
                        {
                            "date": row[1].split('T')[0] if 'T' in row[1] else row[1],
                            "attention": row[2]
                        }
                        for row in rows
                    ][::-1]
                    print(f"Attention data (last 5 sessions): {attention_list}")

                    # Calculate focus level for each session and then average
                    focus_levels = []
                    if rows:
                        global fps
                        if 'fps' not in globals() or fps <= 0:
                            fps = 30
                            print(f"FPS not set, defaulting to {fps}")

                        for session in rows:
                            login_time_str, logout_time_str, attention_lost_frames = session
                            print(f"Processing session: {session}")

                            # Parse login and logout times
                            try:
                                login_time = datetime.fromisoformat(login_time_str)
                                logout_time = datetime.fromisoformat(logout_time_str)
                            except ValueError as e:
                                print(f"Error parsing datetime: {e}")
                                continue

                            # Calculate session duration
                            session_duration_seconds = (logout_time - login_time).total_seconds()
                            print(f"Session duration (seconds): {session_duration_seconds}")

                            total_frames = session_duration_seconds * fps
                            print(f"Total frames: {total_frames}, Attention lost frames: {attention_lost_frames}")

                            # Ensure attention_lost_frames is a number
                            try:
                                attention_lost_frames = float(attention_lost_frames)
                            except (ValueError, TypeError) as e:
                                print(f"Error converting attention_lost_frames to float: {e}")
                                continue

                            # Avoid division by zero
                            if total_frames <= 0:
                                print("Total frames is zero or negative, skipping this session")
                                continue

                            # Calculate focus level for this session
                            focus_level = max(0, ((total_frames - attention_lost_frames) / total_frames) * 100)
                            focus_levels.append(focus_level)
                            print(f"Focus level for this session: {focus_level}")

                        # Calculate average focus level
                        if focus_levels:
                            avg_focus_level = sum(focus_levels) / len(focus_levels)
                            print(f"Average focus level: {avg_focus_level}")

                            # Calculate engagement based on the average focus level
                            engagement = avg_focus_level
                            # Use the latest session's attention_lost_frames for the engagement adjustment
                            latest_session = rows[0]
                            _, _, latest_attention_lost_frames = latest_session
                            try:
                                latest_attention_lost_frames = float(latest_attention_lost_frames)
                                latest_total_frames = (datetime.fromisoformat(latest_session[1]) - datetime.fromisoformat(latest_session[0])).total_seconds() * fps
                                if latest_attention_lost_frames > latest_total_frames * 0.5:
                                    engagement *= 0.5
                            except (ValueError, TypeError) as e:
                                print(f"Error in engagement calculation: {e}")

                            return attention_list, round(avg_focus_level, 2), round(engagement, 2)
                        else:
                            print("No valid sessions to calculate focus level")
                            return attention_list, 0, 0
                    else:
                        print("No attention data found for this user")
                        return [], 0, 0

            except sqlite3.Error as e:
                print(f"Database error for attention: {e}")
                return [], 0, 0

        attention_data, focus_level, engagement = fetch_attention_data()

        return render_template(
            'parentportal.html',
            parent=parent_name,
            student=username,
            math_data=math_data,
            science_data=science_data,
            english_data=english_data,
            attention_data=attention_data,
            focus_level=focus_level,
            engagement=engagement
        )

@app.route('/parent2')
def parent2():
    error = request.args.get("error")
    return render_template('loginParent.html', error=error)

@app.route('/profile')
def profile():
    username = session.get("username")
    if not username:
        return redirect(url_for('login', error="Please log in first"))

    user_details = get_user_details(username)
    if isinstance(user_details, str):  # Error case
        return user_details

    # Fetch scores from each subject database
    def fetch_scores(db_name, subject):
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT tdate, score FROM {subject} WHERE username = ? ORDER BY tdate DESC LIMIT 5", (username,))
                scores = cursor.fetchall()
                return [
                    {
                        'date': row[0],
                        'score': int(row[1].split('/')[0]),  # Raw score (numerator)
                        'total': int(row[1].split('/')[1])   # Total possible score (denominator)
                    }
                    for row in scores
                ][::-1]  # Reverse to get oldest to newest
        except sqlite3.Error as e:
            print(f"Database error for {subject}: {e}")
            return []

    math_scores = fetch_scores(DB_NAME_MATH, "math")
    science_scores = fetch_scores(DB_NAME_SCIENCE, "science")
    english_scores = fetch_scores(DB_NAME_ENGLISH, "english")

    # Find the maximum total score for each subject to set the y-axis range
    math_max_total = max([s['total'] for s in math_scores], default=5)  # Default to 5 if no scores
    science_max_total = max([s['total'] for s in science_scores], default=5)
    english_max_total = max([s['total'] for s in english_scores], default=5)

    return render_template(
        'studentprofile.html',
        user=user_details['username'],
        email=user_details['email'],
        grade=user_details['class'],
        math_scores=math_scores,
        science_scores=science_scores,
        english_scores=english_scores,
        math_max_total=math_max_total,
        science_max_total=science_max_total,
        english_max_total=english_max_total
    )

'''@app.route('/choose')
def choose():
    return render_template('choose.html')'''


'''
WORKING PART
@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return "No video file found", 400

    file = request.files['video']

    if file.filename == '':
        return "No selected file", 400

    file.save('uploads/vid.mp4')
    return render_template('upload.html')
'''


'''@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            return "No file part"
        file = request.files['video']
        if file.filename == '':
            return "No selected file"
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session["filepath"] = filepath
            return redirect(url_for('play_video', filename=file.filename))
    
    return render_template('choose.html')

@app.route('/play/<filename>')
def play_video(filename):
    return render_template('upload.html', filename=filename)'''





#################Youtube video player ############################################################################################################################################################

@app.route('/youtubesearch', methods=["GET", "POST"])
def youtubesearch():
    videos = []
    if request.method == "POST":
        query = request.form["search"]
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 10,
            "key": YOUTUBE_API_KEY,
        }
        response = requests.get(YOUTUBE_SEARCH_URL, params=params)
        data = response.json()

        if "items" in data:
            videos = [
                {
                    "title": item["snippet"]["title"],
                    "videoId": item["id"]["videoId"],
                    "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                }
                for item in data["items"]
            ]
    return render_template('youtubesearch.html', videos=videos)


'''@app.route('/play2/<video_id>')
def play_video_2(video_id):
    session['current_url'] = f"https://www.youtube.com/watch?v={video_id}"
    print(session['current_url'])
    return render_template('upload2.html', video_id=video_id)'''

@app.route('/play2/<video_id>')
def play_video_2(video_id):
    if not video_id:
        return "Invalid video ID", 400
    session['current_url'] = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Playing video with ID: {video_id}, URL: {session['current_url']}")
    return render_template('upload2.html', video_id=video_id)

def youtube_transcript(link):
    video_id = link.split("=")[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = ""
    for i in transcript:
        text = " ".join([i["text"] for i in transcript])
    return text
    

############################################ YOUTUBE SUMMARY #####################################################

def generate_summarynormal(text):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )
    chat_session = model.start_chat()
    response = chat_session.send_message("Summarize the given text into short paragraph" + text)

    return response.text if response else "❌ Error: No response from Gemini"



@app.route('/video_to_text2')
def video_to_text2():
    transcript = youtube_transcript(session['current_url'])
    try:
        print("🔍 Generating summary...")
        summary = generate_summarynormal(transcript)
        print("✅ Summary Generated:", summary)
    except Exception as e:
        print("❌ Error in Summarization:", str(e))
        return f"Error in Summarization: {str(e)}", 500

    with open("summary.txt", "w", encoding="utf-8") as file:
        file.write(summary)

    # ✅ Pass summary as 'notes' to match the template
    return render_template('notes.html', notes=summary)
    


@app.route('/home2')
def home2():
    return render_template('home2.html')



@app.route('/home3')
def home3():
    return render_template('home.html')



@app.route('/science')
def science():
    return render_template('science.html')


@app.route('/english')
def english():
    return render_template('english.html')

@app.route('/math')
def math():
    return render_template('math.html')


@app.route('/mcq2')
def mcq2():
    return render_template('mcq.html')


@app.route('/testresult')
def testresult():
    return render_template('testresult.html')

############################################ ATTENTION MONITORING ###################################################

def gen_frames():
    global at
    global fps
    cap = cv2.VideoCapture(0) #cam index
    prev_time = 0
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        else:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_result = face_mesh.process(rgb_frame)
            pose_result = pose.process(rgb_frame)
            current_time = time.time()
            fps = 1.0 / (current_time - prev_time)
            prev_time = current_time


            eye_attention = True
            yawn_attention = True
            posture_attention = True
            head_pose_attention = True

            DROWSY_COUNTER = 0

            if not face_result.multi_face_landmarks:
                face_not_detected_counter += 1
                if face_not_detected_counter > 10:
                    attention_message = "Face Not Detected"
                    cv2.putText(frame, attention_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.imshow('Attention Detection', frame)
                continue
            face_not_detected_counter = 0

            for face_landmarks in face_result.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS )

                right_eye = [face_landmarks.landmark[i] for i in range(33, 42)]
                left_eye = [face_landmarks.landmark[i] for i in range(362, 371)]

                ear_right = eye_aspect_ratio(right_eye, frame.shape)
                ear_left = eye_aspect_ratio(left_eye, frame.shape)
                avg_ear = (ear_right + ear_left) / 2.0

                if avg_ear < EYE_AR_THRESH:
                    EYE_COUNTER += 1
                    if EYE_COUNTER >= EYE_AR_CONSEC_FRAMES:
                        eye_attention = False
                        DROWSY_COUNTER += 1
                else:
                    eye_attention = True
                    EYE_COUNTER = 0

                mouth_landmarks = [face_landmarks.landmark[i] for i in range(61, 68)]
                mar = mouth_aspect_ratio(mouth_landmarks, frame.shape)

                if mar > MOUTH_AR_THRESH:
                    YAWN_COUNTER += 1
                    yawn_attention = False
                    DROWSY_COUNTER += 1

                else:
                    yawn_attention = True
                    YAWN_COUNTER = 0
                nose_tip = face_landmarks.landmark[1]
                chin = face_landmarks.landmark[152]
                left_eye_corner = face_landmarks.landmark[33]
                right_eye_corner = face_landmarks.landmark[263]
                left_mouth_corner = face_landmarks.landmark[61]
                right_mouth_corner = face_landmarks.landmark[291]

                image_points = np.array([
            (nose_tip.x, nose_tip.y),
            (chin.x, chin.y),
            (left_eye_corner.x, left_eye_corner.y),
            (right_eye_corner.x, right_eye_corner.y),
            (left_mouth_corner.x, left_mouth_corner.y),
            (right_mouth_corner.x, right_mouth_corner.y)
        ], dtype="double")

                success, rotation_vector, translation_vector = get_head_pose(image_points, frame.shape)
                if success:
                    head_pose_attention = abs(rotation_vector[1]) < 0.3


            if pose_result.pose_landmarks:
                mp_drawing.draw_landmarks(
            frame, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())


                left_shoulder = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                left_hip = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

                shoulder_distance = calculate_distance(left_shoulder, right_shoulder, frame.shape)
                hip_distance = calculate_distance(left_hip, right_hip, frame.shape)

                if shoulder_distance / hip_distance <= 0.75:
                    posture_attention = False
                    DROWSY_COUNTER += 1
            if not (eye_attention and yawn_attention and posture_attention and head_pose_attention):
                at = at+1
                attention_message = "Attention Lost: " +str(at)
            else:
                attention_message = "Attention Maintained"

            cv2.putText(frame, attention_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            #cv2.imshow('Attention Detection', frame)









            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    cap.release()


@app.route('/video_stream')
def video_stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')





@app.route('/fps')
def get_fps():
    global fps
    return jsonify(fps=fps)


@app.route('/at')
def get_at():
    global at
    return jsonify(at=at)





import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyALSQg60p7vqNBdn5SHpFKhu0AE8lpe1cE")

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 300,
    "top_p": 1,
    "top_k": 50,
}

########################################## SUMMARY #################################################################3

def generate_summary(text):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )
    chat_session = model.start_chat()
    response = chat_session.send_message("Summarize the given text with headings and bullet points, using the format: # Main Topic, ## Subheading, - Bullet point: " + text)

    return response.text if response else "❌ Error: No response from Gemini"



##MINDMAP SECTION

import json
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
from flask import send_file
import google.generativeai as genai
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_pydot import graphviz_layout


import textwrap

# Assuming genai is already configured globally in your app
# genai.configure(api_key="AIzaSyALSQg60p7vqNBdn5SHpFKhu0AE8lpe1cE")
# Safety settings and generation config are already defined globally

@app.route('/youtube_mindmap')
def youtube_mindmap():
    transcript = youtube_transcript(session['current_url'])
    try:
        print("🔍 Generating summary...")
        summary = generate_summary(transcript)
        print("✅ Summary Generated:", summary)
    except Exception as e:
        print("❌ Error in Summarization:", str(e))
        return f"Error in Summarization: {str(e)}", 500

    with open("summary.txt", "w", encoding="utf-8") as file:
        file.write(summary)
    try:
        with open("summary.txt", "r", encoding="utf-8") as f:
            text_content = f.read().strip()
        if not text_content:
            print("Warning: summary.txt is empty")
            return "Error: No content in summary.txt", 500
        generate_and_save_detailed_mindmap(text_content)
        return render_template('mindmap.html', image_url=url_for('static', filename='mindmap_detailed.jpg'))
    except FileNotFoundError:
        print("Error: summary.txt not found")
        return "Error: Summary file not found", 500
    except Exception as e:
        print(f"Error generating detailed mind map: {str(e)}")
        return f"Error generating mind map: {str(e)}", 500
    
import networkx as nx

def wrap_text(text, width=30):
    """Wraps text for better readability in nodes."""
    return '\n'.join(textwrap.wrap(text, width))

def parse_summary_file(text_content):
    """Parses text content and generates a structured mind map representation."""
    lines = text_content.split('\n')
    mindmap = []
    current_main_node = None
    current_sub_node = None

    for line in lines:
        line = line.strip()
        if line.startswith('# '):  
            current_main_node = {"name": wrap_text(line[2:]), "type": "main", "children": []}
            mindmap.append(current_main_node)
        elif line.startswith('## '):  
            current_sub_node = {"name": wrap_text(line[3:]), "type": "sub", "children": []}
            if current_main_node:
                current_main_node['children'].append(current_sub_node)
        elif line.startswith('- Bullet point:') :  
            detailed_node = {"name": wrap_text(line[16:]), "type": "detailed"}
            if current_sub_node:
                current_sub_node['children'].append(detailed_node)
        elif line.startswith('- **') or line.startswith('- '):  
            detailed_node = {"name": wrap_text(line[2:]), "type": "detailed"}
            if current_sub_node:
                current_sub_node['children'].append(detailed_node)
        

    return mindmap

def build_graph(mindmap):
    """Builds a NetworkX graph from the parsed mind map structure."""
    G = nx.DiGraph()
    for main_node in mindmap:
        G.add_node(main_node['name'], node_type=main_node['type'])
        for sub_node in main_node.get('children', []):
            G.add_node(sub_node['name'], node_type=sub_node['type'])
            G.add_edge(main_node['name'], sub_node['name'])
            for detailed_node in sub_node.get('children', []):
                G.add_node(detailed_node['name'], node_type=detailed_node['type'])
                G.add_edge(sub_node['name'], detailed_node['name'])
    return G

def generate_and_save_detailed_mindmap(text_content, filename="static/mindmap_detailed.jpg"):
    """Generates and saves the mind map with a radial layout."""
    mindmap_data = parse_summary_file(text_content)
    graph = build_graph(mindmap_data)

    # Ensure there's at least one main node
    main_nodes = [node for node in graph.nodes() if graph.nodes[node]['node_type'] == 'main']
    if not main_nodes:
        raise ValueError("No main node found in the mind map data.")
    root = main_nodes[0]

    # Apply Circular Layout for radial structure
    pos = nx.circular_layout(graph)

    plt.figure(figsize=(20, 15))

    # Define color scheme for different node types
    color_map = {'main': '#9FE2BF', 'sub': '#87CEEB', 'detailed': '#F5B7B1'}
    node_colors = [color_map[graph.nodes[node]['node_type']] for node in graph.nodes]

    # Draw the graph with curved edges for better aesthetics
    nx.draw(graph, pos, with_labels=False, node_size=3000, node_color=node_colors, edge_color="gray", width=1.5, arrows=True, connectionstyle="arc3,rad=0.3")

    # Add text labels to nodes
    for node, (x, y) in pos.items():
        plt.text(x, y, node, fontsize=10, ha='center', va='center',
                 bbox=dict(facecolor=color_map[graph.nodes[node]['node_type']], edgecolor='black', boxstyle='round,pad=1.5'))

    plt.title("Optimized Radial Mind Map")
    plt.margins(0.2)  
    plt.tight_layout()
    
    # Save the final image
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, format='jpg', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Mind map saved as {filename}")


########################################## GENERATE NOTES #######################################################


def generate_notes(text):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 500,
            "top_p": 1,
            "top_k": 50,
        },
    )
    chat_session = model.start_chat()
    prompt = f"""
    From the given text, generate detailed, descriptive notes for children (ages 8-12), including those with ADHD. Use simple, fun language and add short examples or fun facts where relevant. Format the notes with:

    # Main Topic [Relevant Emoji]
    ## Subheading [Relevant Emoji]
    - [Relevant Emoji] Bullet point (keep it short, max 15 words)
    - [Relevant Emoji] Another point with a fun twist or example
    - [Relevant Emoji] Quick tip or fact to keep it exciting

    Ensure:
    - Headings are clear and followed by ONE emoji relevant to the topic (e.g., 🌍 for Earth, ☀️ for Sun).
    - Bullet points are concise, engaging, and each starts with ONE emoji tied to the content (e.g., 🚀 for space travel).
    - Avoid Markdown syntax (e.g., ** or *) or any formatting characters; use plain text only.
    - Content is easy to read, avoids complex words, and feels playful.

    Example:
    # Solar System ☀️
    ## Planets 🪐
    - 🌍 Earth is where we live—super cool!
    - 🚀 Mars has red dirt from rust.
    - 🪐 Jupiter is the biggest planet ever!

    Text:
    {text}
    """
    response = chat_session.send_message(prompt)
    return response.text if response else "❌ Error: No response from Gemini"

@app.route('/youtubeautonotes')
def youtubeautonotes():
    transcript = youtube_transcript(session['current_url'])
    # Clean the transcript to remove any Markdown artifacts
    transcript = re.sub(r'\*\*|\*', '', transcript)  # Remove ** or *
    try:
        print("🔍 Generating notes...")
        autonotes = generate_notes(transcript)
        print("✅ Notes Generated:", autonotes)
    except Exception as e:
        print("❌ Error in note generation:", str(e))
        return f"Error in note generation: {str(e)}", 500

    with open("notes.txt", "w", encoding="utf-8") as file:
        file.write(autonotes)

    return render_template('notes2.html', notes2=autonotes)


    # ✅ Pass summary as 'notes' to match the template
    return render_template('notes2.html', notes2=autonotes)

##to download pdf

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import Flask, request, make_response, render_template, redirect, url_for, session
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics  # Add this
from reportlab.pdfbase.ttfonts import TTFont  # Add this
import io

# Register fonts (place this right after the imports and app setup)
sans_font_path = os.path.join(app.static_folder, 'fonts', 'NotoSans-Regular.ttf')
emoji_font_path = os.path.join(app.static_folder, 'fonts', 'NotoColorEmoji.ttf')

print("Sans font path:", sans_font_path)
print("Emoji font path:", emoji_font_path)

if not os.path.exists(sans_font_path):
    raise FileNotFoundError(f"Font file not found at {sans_font_path}. Please ensure NotoSans-Regular.ttf is in static/fonts/")
if not os.path.exists(emoji_font_path):
    print("Warning: NotoColorEmoji.ttf not found. Emojis may not render correctly.")

pdfmetrics.registerFont(TTFont('NotoSans', sans_font_path))
if os.path.exists(emoji_font_path):
    pdfmetrics.registerFont(TTFont('NotoColorEmoji', emoji_font_path))
    print("Fonts 'NotoSans' and 'NotoColorEmoji' registered successfully")
else:
    print("Font 'NotoSans' registered successfully; 'NotoColorEmoji' not available")

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        # Debug: Check if notes.txt exists and read it
        notes_path = os.path.join(os.getcwd(), "notes.txt")
        print(f"Looking for notes.txt at: {notes_path}")
        if not os.path.exists(notes_path):
            print("Error: notes.txt not found at the expected path")
            return "notes.txt not found", 404

        with open(notes_path, "r", encoding="utf-8") as file:
            notes = file.read().strip()
            print(f"Content of notes.txt: {notes[:100]}...")  # Print first 100 chars for debug
        
        if not notes:
            print("Error: notes.txt is empty")
            return "No content in notes.txt", 400

        # Create a PDF in memory
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Define page layout constants
        page_width, page_height = letter  # 612x792 points
        left_margin = 100
        right_margin = 50
        top_margin = 750
        bottom_margin = 50
        line_height = 20
        max_width = page_width - left_margin - right_margin

        # Set initial font
        current_font = "NotoSans"
        pdf.setFont(current_font, 12)

        # Write title
        pdf.drawString(left_margin, top_margin, "Fun Notes")
        if os.path.exists(emoji_font_path):
            pdf.setFont("NotoColorEmoji", 12)
            pdf.drawString(left_margin + pdf.stringWidth("Fun Notes", "NotoSans", 12), top_margin, "🌟")
        pdf.setFont(current_font, 12)
        y_position = top_margin - line_height

        # Process each line of notes
        lines = notes.split('\n')
        print("Number of lines in notes:", len(lines))

        for line in lines:
            if not line.strip():  # Skip empty lines
                y_position -= line_height
                continue

            if y_position < bottom_margin:  # New page if near bottom
                pdf.showPage()
                pdf.setFont(current_font, 12)
                y_position = top_margin

            # Debug: Print each line being processed
            print(f"Processing line: {line[:50]}...")

            # Handle long lines by wrapping
            remaining_line = line
            while len(remaining_line) > 0:
                if y_position < bottom_margin:
                    pdf.showPage()
                    pdf.setFont(current_font, 12)
                    y_position = top_margin

                chars_per_line = int(max_width / 6)  # Approx 6 points per char at 12pt
                if os.path.exists(emoji_font_path):
                    parts = re.split(r'([\U0001F300-\U0001F9FF])', remaining_line)
                    x_position = left_margin
                    for part in parts:
                        if not part:
                            continue
                        if re.match(r'[\U0001F300-\U0001F9FF]', part):
                            current_font = "NotoColorEmoji"
                            pdf.setFont(current_font, 12)
                        else:
                            current_font = "NotoSans"
                            pdf.setFont(current_font, 12)
                        chars_to_draw = min(len(part), chars_per_line - int((x_position - left_margin) / 6))
                        if chars_to_draw > 0:
                            pdf.drawString(x_position, y_position, part[:chars_to_draw])
                            x_position += pdf.stringWidth(part[:chars_to_draw], current_font, 12)
                            if x_position >= left_margin + max_width:
                                y_position -= line_height
                                x_position = left_margin
                        remaining_line = remaining_line[len(part):]
                else:
                    chars_to_draw = min(len(remaining_line), chars_per_line)
                    pdf.drawString(left_margin, y_position, remaining_line[:chars_to_draw])
                    remaining_line = remaining_line[chars_to_draw:]
                y_position -= line_height

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        pdf_data = buffer.getvalue()
        print("Generated PDF size:", len(pdf_data))
        buffer.close()

        if len(pdf_data) < 100:
            print("Error: Generated PDF is too small, likely invalid")
            return "Failed to generate valid PDF", 500

        response = make_response(pdf_data)
        response.headers['Content-Disposition'] = 'attachment; filename=fun_notes.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        return response

    except FileNotFoundError as e:
        print(f"FileNotFoundError: {str(e)}")
        return "notes.txt not found", 404
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return f"Error generating PDF: {str(e)}", 500

import random
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
import google.generativeai as genai

# Database Names
DB_NAME_SCIENCE = "science.db"
DB_NAME_ENGLISH = "english.db"
DB_NAME_MATH = "math.db"

# Configure Gemini API (assuming this is done globally elsewhere in your app)
genai.configure(api_key="AIzaSyALSQg60p7vqNBdn5SHpFKhu0AE8lpe1cE")  # Replace with your actual API key



################################### Function to Generate MCQs Using Gemini API######################################
def generate_mcqs(text):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        chat_session = model.start_chat()
        
        prompt = f"""
From the given text, generate 5 multiple-choice questions (MCQs) with 4 options each (a, b, c, d).
The options should be the full answer texts (without the letters a, b, c, d). 
The answer should be the correct option's letter (a, b, c, or d).
Return the result as a valid JSON array in this format:
[
    {{"question": "Question text", "options": ["Option 1 text", "Option 2 text", "Option 3 text", "Option 4 text"], "answer": "correct_option_letter"}},
    ...
]

Text:
{text}
"""
        
        response = chat_session.send_message(prompt)
        print("Raw Gemini API Response:", response.text)  # Debug log

        # Clean up the response
        response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        # Parse JSON response
        try:
            mcqs = json.loads(response_text)
            if not isinstance(mcqs, list):
                print("⚠️ Error: API response is not a list!")
                return []
            # Validate MCQ structure
            for mcq in mcqs:
                if not all(key in mcq for key in ["question", "options", "answer"]) or len(mcq["options"]) != 4:
                    print("⚠️ Invalid MCQ structure:", mcq)
                    return []
            return mcqs
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parsing Error: {e}")
            print(f"❌ Response Text: '{response_text}'")
            return []
    except Exception as e:
        print(f"❌ Unexpected error in generate_mcqs: {e}")
        return []

# Route to Generate MCQs
@app.route('/generate_mcq', methods=['POST'])
def generate_mcq():
    try:
        if request.content_type != 'application/json':
            return jsonify({"error": "Unsupported Media Type. Content-Type must be 'application/json'"}), 415
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request: No JSON data provided."}), 400
        
        subject = data.get('subject', 'science').lower()
        if subject not in ['science', 'english', 'math']:
            return jsonify({"error": "Invalid subject selected"}), 400

        # Ensure summary.txt exists
        try:
            with open("summary.txt", "r", encoding="utf-8") as f:
                text = f.read().strip()
        except FileNotFoundError:
            print("❌ Error: summary.txt not found")
            return jsonify({"error": "Summary file not found"}), 500
        
        if not text:
            print("❌ Error: summary.txt is empty")
            return jsonify({"error": "No content in summary.txt"}), 400
        
        mcqs = generate_mcqs(text)
        if not mcqs:
            print("❌ Error: Failed to generate MCQs")
            return jsonify({"error": "Failed to generate MCQs"}), 500
        
        session['mcqs'] = mcqs
        session['subject'] = subject
        return jsonify({"mcqs": mcqs})
    
    except Exception as e:
        print(f"❌ Error in /generate_mcq: {e}")
        return jsonify({"error": f"Error generating MCQs: {e}"}), 500

# Route to Render MCQ Page
@app.route('/mcq')
def mcq():
    if 'mcqs' not in session:
        return redirect(url_for('home2'))  # Redirect if no MCQs in session
    return render_template('mcq.html', mcqs=session['mcqs'])

# Route to Submit Quiz and Show Results
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'mcqs' not in session or 'username' not in session:
        return jsonify({"error": "Session expired or invalid"}), 400
    
    mcqs = session['mcqs']
    answers = request.form.to_dict()
    score = sum(1 for i, mcq in enumerate(mcqs) if answers.get(f'q{i}', '').strip().lower() == mcq['answer'].strip().lower())
    total = len(mcqs)
    percentage = (score / total) * 100 if total > 0 else 0
    
    subject = session.get('subject', 'science')
    db_map = {'science': DB_NAME_SCIENCE, 'english': DB_NAME_ENGLISH, 'math': DB_NAME_MATH}
    db_name = db_map.get(subject, DB_NAME_SCIENCE)
    
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {subject} (tdate, username, score, attention)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session['username'], f"{score}/{total}", "N/A"))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    
    # Prepare data for the results page
    results = []
    for i, mcq in enumerate(mcqs):
        user_answer_letter = answers.get(f'q{i}', '').strip().lower()
        correct_answer_letter = mcq['answer'].strip().lower()
        
        # Get answer texts using the letters
        try:
            correct_answer_index = ord(correct_answer_letter) - ord('a')
            correct_answer_text = mcq['options'][correct_answer_index]
        except (IndexError, TypeError):
            correct_answer_text = "Invalid correct answer"

        try:
            user_answer_index = ord(user_answer_letter) - ord('a')
            user_answer_text = mcq['options'][user_answer_index]
        except (IndexError, TypeError):
            user_answer_text = "Not answered"

        is_correct = user_answer_letter == correct_answer_letter
        
        results.append({
            'question': mcq['question'],
            'options': mcq['options'],
            'user_answer': f"{user_answer_letter.upper()}) {user_answer_text}",
            'correct_answer': f"{correct_answer_letter.upper()}) {correct_answer_text}",
            'is_correct': is_correct
        })
        
    session.pop('mcqs', None)
    session.pop('subject', None)
    
    return render_template('testresult.html', score=f"{score}/{total} ({percentage:.2f}%)", results=results)


##attention graph

# Add this to your imports
from datetime import datetime, timedelta

# Database Name
DB_NAME_ATTENTION = "attention.db"

# Function to initialize the attention database
def init_attention_db():
    if not os.path.exists(DB_NAME_ATTENTION):
        with sqlite3.connect(DB_NAME_ATTENTION) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attention (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    login_time TEXT NOT NULL,
                    logout_time TEXT NOT NULL,
                    attention_duration REAL NOT NULL
                )
            ''')
            conn.commit()

# Call this when the app starts
init_attention_db()

# Track login time in session
@app.route('/parenthome', methods=['POST'])
def parenthome():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                return redirect(url_for('login', error="Username does not exist."))
            if user[5] != password:
                return redirect(url_for('login', error="Incorrect password."))

        session["username"] = username
        return render_template('home2.html')

# Logout route to record attention time
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    global at  # Access the global attention loss counter
    if "username" not in session:
        return redirect(url_for('login', error="Not logged in"))

    username = session["username"]
    attention_lost_frames = at  # Get the current attention loss count
    logout_time = datetime.now().isoformat()

    # Store in attention.db
    with sqlite3.connect(DB_NAME_ATTENTION) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attention (username, login_time, logout_time, attention_duration)
            VALUES (?, ?, ?, ?)
        ''', (username, session.get("login_time", "N/A"), logout_time, attention_lost_frames))
        conn.commit()

    # Reset attention counter for the next session
    at = 0
    session.clear()
    return redirect(url_for('landing', error="Logged out successfully"))

if __name__ == "__main__":
    app.run(debug=True)