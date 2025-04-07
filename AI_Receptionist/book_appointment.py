# book_appointment.py

from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine
import os

# -----------------------------------------------------------------------------
# 1. Initialize Database (reuse or match your existing setup)
# -----------------------------------------------------------------------------

DATABASE_URL = "sqlite:///database.db"  # or your actual DB path
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# -----------------------------------------------------------------------------
# 2. Existing 'users' table from your schema (reference only)
# -----------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    face_encoding = Column(LargeBinary, nullable=True)

    # If you want a backref relationship:
    appointments = relationship("Appointment", back_populates="user")

# -----------------------------------------------------------------------------
# 3. New 'appointments' table
# -----------------------------------------------------------------------------

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    specialist = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="appointments")

# -----------------------------------------------------------------------------
# 4. Create tables if they don't exist
# -----------------------------------------------------------------------------
Base.metadata.create_all(engine)

# -----------------------------------------------------------------------------
# 5. Function to book an appointment
# -----------------------------------------------------------------------------
def book_appointment(user_id: int, specialist: str, date: str, time_slot: str):
    
    # Create a new appointment in the database, linked to the user by user_id.

    db = SessionLocal()
    try:
        new_appt = Appointment(
            user_id=user_id,
            specialist=specialist,
            date=date,
            time_slot=time_slot
        )
        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)
        return new_appt
    finally:
        db.close()
