# auth.py
import os
import bcrypt
import numpy as np
import face_recognition
from sqlalchemy import create_engine, Column, Integer, String, text, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base

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

# 3) Create tables if they don't exist
Base.metadata.create_all(engine)

# 4) Functions to sign up and log in
def signup_user(email: str, password: str, face_encoding: bytes = None) -> bool:
    """
    Creates a new user in the DB. Returns True on success, False if user already exists.
    """
    session = SessionLocal()
    try:
        # Check if the user already exists
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            return False
        
        # Hash the password using bcrypt
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(email=email, password_hash=hashed_pw.decode('utf-8'), face_encoding=face_encoding)
        session.add(user)
        session.commit()
        return True
    finally:
        session.close()


def login_user(email: str, password: str) -> bool:
    """
    Verify user credentials. Returns True if valid, else False.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            return False
        
        # Compare hashed password
        return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
    finally:
        session.close()

def login_user_with_face(face_encoding: np.ndarray) -> str:
    """
    Compare 'face_encoding' from the camera with stored face_encodings in the DB.
    If a match is found, return the user's email. Otherwise, return None.
    """
    session = SessionLocal()
    try:
        users = session.query(User).all()
        for user in users:
            if user.face_encoding:
                # Convert stored binary back to numpy
                stored_encoding = np.frombuffer(user.face_encoding, dtype=np.float64)

                # Compare using face_recognition
                results = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.6)
                if results[0]:  # If a match is found
                    return user.email
        return None  # No match found
    finally:
        session.close()

def get_user_id_by_email(email: str):
    """Returns the user's ID for the given email, or None if not found."""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            return user.id
        else:
            return None
    finally:
        session.close()