import os
import streamlit as st
import face_recognition
import bcrypt
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import date

# Database Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)  # Added Designation Column
    face_encoding = Column(LargeBinary, nullable=False)  # Face is REQUIRED

class UnavailableSlot(Base):
    __tablename__ = "unavailable_slots"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)
    designation = Column(String, nullable=False)  # Added Designation Column

    doctor = relationship("Doctor")

Base.metadata.create_all(engine)
session = SessionLocal()

# Streamlit Page Config
st.set_page_config(page_title="Doctor Login", layout="centered")
st.title("👨‍⚕️ Doctor Portal")
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

# Session State
if "doctor_logged_in" not in st.session_state:
    st.session_state.doctor_logged_in = False
if "doctor_email" not in st.session_state:
    st.session_state.doctor_email = ""

# Doctor Login Function
def login_doctor(email, password):
    doctor = session.query(Doctor).filter_by(email=email).first()
    if doctor and bcrypt.checkpw(password.encode('utf-8'), doctor.password_hash.encode('utf-8')):
        return doctor
    return None

def login_doctor_with_face(face_encoding):
    """Match a given face encoding with stored doctor face data."""
    doctors = session.query(Doctor).all()

    for doctor in doctors:
        if doctor.face_encoding:
            # Convert stored binary face encoding to NumPy array
            stored_encoding = np.frombuffer(doctor.face_encoding, dtype=np.float64)
            
            # Compare stored face encoding with the new captured one
            match = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.6)
            if match[0]:  # If match is found
                return doctor

    return None

# Doctor Login Form
if not st.session_state.doctor_logged_in:
    st.subheader("🔐 Doctor Login")
    login_mode = st.radio("Choose login method", ["📧 Email & Password", "📸 Face Recognition"])

    if login_mode == "📧 Email & Password":
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        if st.button("🔓 Login"):
            doctor = login_doctor(email, password)
            if doctor:
                st.session_state.doctor_logged_in = True
                st.session_state.doctor_email = email
                st.session_state.doctor_id = doctor.id
                st.session_state.doctor_designation = doctor.designation  # Store Designation
                st.success(f"🎉 Welcome, Dr. {doctor.name}!")
                st.rerun()
            else:
                st.error("❌ Invalid Email or Password")

    else:  # Face Recognition Login
        st.info("📸 Capture your face to log in.")
        face_image = st.camera_input("Capture your face")

        if face_image:
            img = face_recognition.load_image_file(face_image)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                matched_doctor = login_doctor_with_face(encodings[0])
                if matched_doctor:
                    st.session_state.doctor_logged_in = True
                    st.session_state.doctor_email = matched_doctor.email
                    st.session_state.doctor_id = matched_doctor.id
                    st.session_state.doctor_designation = matched_doctor.designation  # Store Designation
                    st.success(f"✅ Face login successful! Welcome, Dr. {matched_doctor.name}")
                    st.rerun()
                else:
                    st.error("❌ Face not recognized! Please try again.")
            else:
                st.error("⚠️ No face detected. Try again.")
        else:
            st.warning("⚠️ Please capture your face.")

# Allow Doctors to Select Unavailable Slots
if st.session_state.doctor_logged_in:
    st.subheader("📅 Mark Unavailable Slots")

    selected_date = st.date_input("📅 Select Date", min_value=date.today())
    available_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "04:00 PM"]
    selected_slots = st.multiselect("⏰ Select Unavailable Slots", available_slots)

    if st.button("✅ Save Unavailability"):
        for slot in selected_slots:
            existing_entry = session.query(UnavailableSlot).filter_by(
                doctor_id=st.session_state.doctor_id, date=selected_date, time_slot=slot
            ).first()

            if not existing_entry:
                new_unavailable_slot = UnavailableSlot(
                    doctor_id=st.session_state.doctor_id,
                    date=selected_date.strftime("%Y-%m-%d"),
                    time_slot=slot,
                    designation=st.session_state.doctor_designation  # Store Designation
                )
                session.add(new_unavailable_slot)
        
        session.commit()
        st.success("✅ Unavailable slots updated successfully!")

    # Display Upcoming Unavailable Slots
    st.subheader("📜 Your Upcoming Unavailable Slots")
    today_date = date.today().strftime("%Y-%m-%d")

    unavailable_slots = session.query(UnavailableSlot).filter(
        UnavailableSlot.doctor_id == st.session_state.doctor_id,
        UnavailableSlot.date >= today_date
    ).order_by(UnavailableSlot.date, UnavailableSlot.time_slot).all()

    if unavailable_slots:
        for slot in unavailable_slots:
            st.write(f"📅 **Date:** {slot.date} | 🕒 **Time:** {slot.time_slot} ")
    else:
        st.info("ℹ️ No unavailable slots marked yet.")

    # Logout Button
    if st.button("🚪 Logout"):
        st.session_state.doctor_logged_in = False
        st.session_state.doctor_email = ""
        st.rerun()
