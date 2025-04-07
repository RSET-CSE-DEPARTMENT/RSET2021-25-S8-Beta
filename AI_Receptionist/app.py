# app.py
import streamlit as st
from streamlit_player import st_player
import streamlit.components.v1 as components
import os
import face_recognition
from gtts import gTTS
import glob
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, text, ForeignKey, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from auth import signup_user, login_user, login_user_with_face, get_user_id_by_email
from datetime import datetime, date, time, timedelta
from book_appointment import book_appointment
import google.generativeai as genai
from api import GEMINI_API_KEY


# --- Streamlit App Config ---
st.set_page_config(page_title="AI Receptionist", layout="centered")

# 1) Initialize database
DATABASE_URL = "sqlite:///database.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# 2) Define a User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    face_encoding = Column(LargeBinary, nullable=True)

    # If you want a backref relationship:
    appointments = relationship("Appointment", back_populates="user")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    specialist = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="appointments")

# 3) Create tables if they don't exist
Base.metadata.create_all(engine)
session = SessionLocal()

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {visibility: hidden;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "conversation" not in st.session_state or not isinstance(st.session_state.conversation, list):
    st.session_state.conversation = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login"


# IMPORTANT: Initialize chat_input BEFORE creating the widget
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

def clear_audio_files():
    for file in glob.glob("*.mp3"):
        try:
            os.remove(file)
        except Exception as e:
            st.error(f"Error removing file {file}: {e}")

def generate_tts(text, filename):
    tts = gTTS(text)
    tts.save(filename)
    return filename

# --- Main Title ---
st.title("AI Receptionist")

# --- Sidebar for Navigation ---

# --- Page Navigation ---
if st.session_state.current_page == "Login":
    st.subheader("Login to Your Account")

    if st.button("Login as Doctor"):
        st.session_state.current_page = "doctor_login"

    if st.button("Don't have an account? Sign-up here"):
        st.session_state.current_page = "user_signup"

    # Let user pick login method
    login_mode = st.radio("Choose login method", ["📧 Email & Password", "📸 Face Recognition"])

    if login_mode == "📧 Email & Password":
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("✅ Login successful!")
                st.session_state.current_page = "chat"  # Navigate to chat page

                # **Display Upcoming Appointments with Booking ID**
                user_id = get_user_id_by_email(email)
                upcoming_appointments = session.query(Appointment).filter(
                    Appointment.user_id == user_id,
                    Appointment.date >= date.today()
                ).all()

                if upcoming_appointments:
                    st.write("## 📅 Your Upcoming Appointments:")
                    for appt in upcoming_appointments:
                        st.write(f"- **Doctor:** {appt.specialist} | **Date:** {appt.date} | **Time Slot:** {appt.time_slot} | **Booking ID:** `{appt.id}`")
                else:
                    st.info("No upcoming appointments.")
                
            else:
                st.error("❌ Invalid email or password.")

    else:  # **Face login (No email required)**
        st.info("Please capture your face to log in.")
        face_image = st.camera_input("📸 Capture your face")

        if face_image is not None:
            # Process the captured image
            img = face_recognition.load_image_file(face_image)
            encodings = face_recognition.face_encodings(img)

            if len(encodings) > 0:
                captured_encoding = encodings[0]

                # **Match against the database using login_user_with_face**
                matched_email = login_user_with_face(captured_encoding)

                if matched_email:
                    st.session_state.logged_in = True
                    st.session_state.user_email = matched_email
                    st.success(f"✅ Face login successful! Welcome, {matched_email}")
                    st.session_state.current_page = "chat"  # Navigate to chat page

                    # **Display Upcoming Appointments with Booking ID**
                    user_id = get_user_id_by_email(matched_email)
                    upcoming_appointments = session.query(Appointment).filter(
                        Appointment.user_id == user_id,
                        Appointment.date >= date.today()
                    ).all()

                    if upcoming_appointments:
                        st.write("## 📅 Your Upcoming Appointments:")
                        for appt in upcoming_appointments:
                            st.write(f"- **Doctor:** {appt.specialist} | **Date:** {appt.date} | **Time Slot:** {appt.time_slot} | **Booking ID:** `{appt.id}`")
                    else:
                        st.info("No upcoming appointments.")

                else:
                    st.error("❌ Face login failed: No match or user doesn't have face data.")
            else:
                st.error("❌ Face login failed. Please try again.")

elif st.session_state.current_page == "user_signup":
    st.subheader("Create a New Account")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")
    confirm_password = st.text_input("🔑 Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("❌ Passwords do not match.")
        elif not email or not password:
            st.error("❌ Email and password cannot be empty.")
        else:
            # Call the signup_user function to register the user
            if signup_user(email, password):
                st.success("✅ Account created successfully! Please capture your face for authentication.")
                st.session_state.current_page = "face_capture"
                st.experimental_rerun()  # Reload the app to navigate to the face capture page
            else:
                st.error("❌ Signup failed. Email might already be in use.")

    if st.button("Back to Login"):
        st.session_state.current_page = "Login"
        st.experimental_rerun()  # Reload the app to navigate back to the login page

elif st.session_state.current_page == "face_capture":
    st.subheader("Capture Your Face for Authentication")

    face_image = st.camera_input("📸 Capture your face")

    if face_image is not None:
        # Process the captured image
        img = face_recognition.load_image_file(face_image)
        encodings = face_recognition.face_encodings(img)

        if len(encodings) > 0:
            captured_encoding = encodings[0]

            # Save the face encoding to the database
            user_email = st.session_state.user_email
            user = session.query(User).filter(User.email == user_email).first()
            if user:
                user.face_encoding = captured_encoding.tobytes()
                session.commit()
                st.success("✅ Face captured and saved successfully! You can now log in using face recognition.")
                st.session_state.current_page = "Login"
                st.experimental_rerun()  # Reload the app to navigate back to the login page
            else:
                st.error("❌ Failed to save face data. Please try again.")
        else:
            st.error("❌ No face detected. Please try again.")

    if st.button("Skip"):
        st.warning("⚠️ You skipped face capture. You can still log in using email and password.")
        st.session_state.current_page = "Login"
        st.experimental_rerun()  # Reload the app to navigate back to the login page