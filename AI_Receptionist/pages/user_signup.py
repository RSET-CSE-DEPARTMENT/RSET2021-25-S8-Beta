import streamlit as st
import face_recognition
from auth import signup_user
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database Configuration ---
DATABASE_URL = "sqlite:///database.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# --- Define the User Table ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    face_encoding = Column(LargeBinary, nullable=False)  # Face is now REQUIRED

# --- Create the database tables ---
Base.metadata.create_all(engine)

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

# --- Streamlit UI for User Signup ---
st.title("AI Receptionist")
st.subheader("📝 User Sign-Up")
st.subheader("Create a New Account (Face Recognition Required)")

email = st.text_input("📧 Email")
password = st.text_input("🔑 Password", type="password")

# Mandatory Face Capture
st.warning("⚠️ Face capture is required for signing up.")
face_image = st.camera_input("📸 Capture your face (Required)")

if st.button("Sign Up"):
    if not email or not password:
        st.warning("⚠️ Please enter email & password.")
    elif face_image is None:
        st.error("🚨 Face capture is required! Please capture your face.")
    else:
        # Encode the captured face
        try:
            img = face_recognition.load_image_file(face_image)
            encodings = face_recognition.face_encodings(img)
            if len(encodings) > 0:
                face_encoding = encodings[0]
                face_encoding_bytes = face_encoding.tobytes()
                
                # Call signup_user function from auth
                success = signup_user(email, password, face_encoding_bytes)
                if success:
                    st.success("✅ User created successfully! Please log in.")
                else:
                    st.error("❌ User with that email already exists. Try a different one.")
            else:
                st.error("🚨 No face detected. Please try again.")
        except Exception as e:
            st.error(f"Error processing face image: {e}")

# Button to navigate to login page
st.page_link("app.py", label="🔑 Go to Login", icon="➡️")
