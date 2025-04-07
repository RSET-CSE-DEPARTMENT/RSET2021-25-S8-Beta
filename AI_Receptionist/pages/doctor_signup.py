import os
import streamlit as st
import face_recognition
import bcrypt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# --- Database Setup ---
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
    designation = Column(String, nullable=False)  # New Designation Field
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

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Doctor Signup", layout="centered")
st.title("👨‍⚕️ Doctor Signup")
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

st.warning("⚠️ Face capture is required for signing up.")

# --- Signup Form ---
email = st.text_input("📧 Email")
name = st.text_input("👤 Full Name")
password = st.text_input("🔑 Password", type="password")

# **Select Designation**
designations = ["Cardiologist", "Neurologist", "Dermatologist", "Orthopedist", "Pediatrician"]
designation = st.selectbox("🏥 Select Your Designation", designations)

# **Mandatory Face Capture**
face_image = st.camera_input("📸 Capture your face (Required)")

if st.button("Sign Up"):
    if not email or not password or not name or not designation:
        st.warning("⚠️ Please enter all details.")
    elif face_image is None:
        st.error("🚨 Face capture is required! Please capture your face.")
    else:
        # Check if the email already exists
        existing_doctor = session.query(Doctor).filter_by(email=email).first()
        if existing_doctor:
            st.error("❌ A doctor with this email already exists.")
        else:
            # Hash password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Encode Face
            try:
                img = face_recognition.load_image_file(face_image)
                encodings = face_recognition.face_encodings(img)
                if len(encodings) > 0:
                    face_encoding_bytes = encodings[0].tobytes()

                    # Create new doctor record
                    new_doctor = Doctor(
                        email=email,
                        name=name,
                        designation=designation,
                        password_hash=hashed_pw.decode('utf-8'),
                        face_encoding=face_encoding_bytes
                    )
                    session.add(new_doctor)
                    session.commit()
                    st.success("✅ Doctor account created successfully! Please log in.")
                else:
                    st.error("🚨 No face detected. Please try again.")
            except Exception as e:
                st.error(f"⚠️ Error processing face image: {e}")

# Button to navigate to login page
#st.page_link("doctor_login.py", label="🔑 Go to Login", icon="➡️")
