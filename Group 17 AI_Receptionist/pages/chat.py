import streamlit as st
from streamlit_player import st_player
import streamlit.components.v1 as components
from sqlalchemy import create_engine, Column, Integer, String, text, ForeignKey, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, date, time, timedelta
from gtts import gTTS
import yagmail
from urllib.parse import quote
import os
import glob
from book_appointment import book_appointment
from auth import get_user_id_by_email


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

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)  # Fixed Missing Column
    face_encoding = Column(LargeBinary, nullable=False)  # Face is REQUIRED

class UnavailableSlot(Base):
    __tablename__ = "unavailable_slots"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)
    designation = Column(String, nullable=False)  # Added Designation Column

    doctor = relationship("Doctor")

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

# --- Ensure the user is logged in ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You must log in before you can chat.")
    st.info("Please go to the Login page from the sidebar.")
    #st.page_link("app.py", label="Login", icon="✔️")
    st.stop()

st.subheader(f"Welcome, {st.session_state.user_email}!")
st.write("Feel free to chat with AI Receptionist to book an appointment.")

all_time_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "04:00 PM"]

def parse_time_slot(time_str):
    return datetime.strptime(time_str, "%I:%M %p").time()

current_datetime = datetime.now()
current_time = current_datetime.time()
today = date.today()
min_date = today if current_time < time(16, 0) else today + timedelta(days=1)

# Initialize chatbot state
if "chatbot_state" not in st.session_state:
    st.session_state.chatbot_state = "greeting"
    st.session_state.selected_specialist = None
    st.session_state.selected_date = None
    st.session_state.selected_time = None
    st.session_state.conversation = []

# Function to generate text-to-speech (TTS)
def generate_tts(text, filename):
    tts = gTTS(text)
    tts.save(filename)
    return filename

def get_unavailable_slots(specialist, selected_date):
    unavailable_slots = session.query(UnavailableSlot).filter_by(
        designation=specialist, date=selected_date.strftime("%Y-%m-%d")
    ).all()
    return [slot.time_slot for slot in unavailable_slots]

def send_confirmation_email(to_email, subject, body):
    sender_email = st.secrets["email"]["sender"]
    sender_password = st.secrets["email"]["password"]

    yag = yagmail.SMTP(user=sender_email, password=sender_password)
    yag.send(to=to_email, subject=subject, contents=body)

# 📅 Generate Google Calendar Link
def generate_google_calendar_link(title, start_datetime, end_datetime, description, location="Online"):
    base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
    return (
        f"{base_url}"
        f"&text={quote(title)}"
        f"&dates={start_datetime.strftime('%Y%m%dT%H%M%S')}/{end_datetime.strftime('%Y%m%dT%H%M%S')}"
        f"&details={quote(description)}"
        f"&location={quote(location)}"
        f"&sf=true&output=xml"
    )

def send_alert_email(agent_email: str, user_email: str) -> None:
    """
    Sends an alert email to a live agent when a user requests support.

    Parameters:
        agent_email (str): Email address of the live agent or support team.
        user_email (str): Email address of the user requesting assistance.
    """
    try:
        sender_email = st.secrets["email"]["sender"]
        sender_password = st.secrets["email"]["password"]

        subject = "🔔 Live Agent Support Requested"
        body = f"""
        🚨 A user has requested to talk to a live agent.

        👤 User Email: {st.session_state.user_email}

        Please respond as soon as possible.

        Timestamp: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
        """

        yag = yagmail.SMTP(user=sender_email, password=sender_password)
        yag.send(to=agent_email, subject=subject, contents=body)

    except Exception as e:
        st.error(f"❌ Failed to send alert email to agent: {e}")

# Display conversation history
st.write("---")
for msg in st.session_state.conversation:
    if isinstance(msg, dict) and "type" in msg and "text" in msg:
        if msg["type"] == "user":
            st.markdown(f"**User:** {msg['text']}")
        elif msg["type"] == "ai":
            st.markdown(f"**AI:** {msg['text']}")
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3")
st.write("---")

# --- Chatbot Logic ---
if st.session_state.chatbot_state == "greeting":
    ai_reply = "Hello! I'm your AI receptionist. How can I help you today?"
    if not any(msg["text"] == ai_reply for msg in st.session_state.conversation):
        audio_file = generate_tts(ai_reply, "greeting.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.rerun()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)  # Added extra columns for the new options

    if col1.button("📅 Book an Appointment"):
        st.session_state.chatbot_state = "select_specialist"
        st.session_state.conversation.append({"type": "user", "text": "I want to book an appointment."})
        st.rerun()

    if col2.button("❌ Exit Chat"):
        st.session_state.conversation.append({"type": "user", "text": "I want to exit."})
        st.write("Alright, let me know if you need help later.")
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.conversation = []
        st.rerun()

    if col3.button("🔍 See Upcoming Appointments"):
        st.session_state.chatbot_state = "view_appointments"
        st.session_state.conversation.append({"type": "user", "text": "I want to see my upcoming appointments."})
        st.rerun()

    if col4.button("💬 Talk to a Live Agent"):
        st.session_state.chatbot_state = "live_agent"
        st.session_state.conversation.append({"type": "user", "text": "I need to talk to a live agent."})

        try:
            send_alert_email(agent_email="U2103090@rajagiri.edu.in", user_email=st.session_state.user_email)
            st.toast("📨 Alert sent to a live agent!")
        except Exception as e:
            st.error(f"❌ Failed to send alert email: {e}")

        st.rerun()
    
elif st.session_state.chatbot_state == "view_appointments":
    user_id = get_user_id_by_email(st.session_state.user_email)

    # Fetch upcoming appointments
    upcoming_appointments = session.query(Appointment).filter(
        Appointment.user_id == user_id,
        Appointment.date >= date.today()
    ).all()

    if upcoming_appointments:
        ai_reply = "Here are your upcoming appointments:\n"
        for appt in upcoming_appointments:
            ai_reply += f"- **Doctor:** {appt.specialist} | **Date:** {appt.date} | **Time Slot:** {appt.time_slot} | **Booking ID:** `{appt.id}`\n"

        audio_file = generate_tts(ai_reply, "upcoming_appointments.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.markdown(ai_reply)

    else:
        ai_reply = "You have no upcoming appointments."
        audio_file = generate_tts(ai_reply, "no_appointments.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.markdown(ai_reply)

    # Button to return to main menu
    if st.button("🔙 Go Back to Main Menu"):
        st.session_state.chatbot_state = "greeting"
        st.session_state.conversation.append({"type": "user", "text": "Going back to the main menu."})
        ai_reply = "Hello! I'm your AI receptionist. How can I help you today?"
        audio_file = generate_tts(ai_reply, "greeting.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.rerun()

elif st.session_state.chatbot_state == "select_specialist":
    specialists = ["Cardiologist", "Neurologist", "Dermatologist", "Orthopedist", "Pediatrician"]
    ai_reply = "Please select a specialist from the options below:"
    if not any(msg["text"] == ai_reply for msg in st.session_state.conversation):
        audio_file = generate_tts(ai_reply, "doctor_selection.mp3")
        st.audio(audio_file, format="audio/mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.rerun()

    cols = st.columns(len(specialists))

    for i, specialist in enumerate(specialists):
        with cols[i]:
            if st.button(specialist):
                st.session_state.selected_specialist = specialist
                st.session_state.conversation.append({"type": "user", "text": f"Selected Specialist: {specialist}"})
                st.session_state.chatbot_state = "select_date"
                st.rerun()
    if st.button("🔙 Go Back to Main Menu"):
        st.session_state.chatbot_state = "greeting"
        st.session_state.conversation.append({"type": "user", "text": "Going back to the main menu."})
        ai_reply = "Hello! I'm your AI receptionist. How can I help you today?"
        audio_file = generate_tts(ai_reply, "greeting.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.rerun()

elif st.session_state.chatbot_state == "select_date":
    ai_reply = "Please select a date for your appointment (Future dates only):"

    if not any(msg["text"] == ai_reply for msg in st.session_state.conversation):
        audio_file = generate_tts(ai_reply, "date_selection.mp3")
        st.audio(audio_file, format="audio/mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.rerun()

    # Display Date Picker (Future Dates Only)
    selected_date = st.date_input("📅 Choose an appointment date", min_value=date.today())

    # Get Unavailable Slots for Selected Doctor
    unavailable_slots = get_unavailable_slots(st.session_state.selected_specialist, selected_date)

    # Get current datetime
    current_datetime = datetime.now()

    # Filter Available Slots for Selected Date
    available_slots = [slot for slot in ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "04:00 PM"] 
                        if slot not in unavailable_slots]

    if selected_date == date.today():
        available_slots = [slot for slot in available_slots 
                           if datetime.combine(date.today(), datetime.strptime(slot, "%I:%M %p").time()) > current_datetime]

    # Ensure there are available slots
    if not available_slots:
        st.warning("🚨 No available slots for this date. Please select another day.")
    else:
        if st.button("✅ Confirm Date"):
            st.session_state.available_slots = available_slots
            st.session_state.selected_date = selected_date
            st.session_state.conversation.append({"type": "user", "text": f"Selected Date: {selected_date}"})
            st.session_state.chatbot_state = "select_time"
            st.rerun()

    if st.button("🔙 Go Back to Main Menu"):
        st.session_state.chatbot_state = "greeting"
        st.session_state.conversation.append({"type": "user", "text": "Going back to the main menu."})
        ai_reply = "Hello! I'm your AI receptionist. How can I help you today?"
        audio_file = generate_tts(ai_reply, "greeting.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.rerun()

elif st.session_state.chatbot_state == "select_time":
    ai_reply = "Please select a time slot for your appointment:"

    if not any(msg["text"] == ai_reply for msg in st.session_state.conversation):
        audio_file = generate_tts(ai_reply, "time_selection.mp3")
        st.audio(audio_file, format="audio/mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.rerun()

    # Display only available slots
    selected_time = st.selectbox("⏰ Choose a time slot", st.session_state.available_slots)

    if st.button("✅ Confirm Time Slot"):
        selected_datetime = datetime.combine(st.session_state.selected_date, datetime.strptime(selected_time, "%I:%M %p").time())

        if selected_datetime <= datetime.now():
            st.warning("🚨 The selected time has already passed! Please choose a future time slot.")
        else:
            st.session_state.selected_time = selected_time
            st.session_state.conversation.append({"type": "user", "text": f"Selected Time: {selected_time}"})
            # st.toast("Redirecting to payment page...")
            # st.switch_page("payment.py")
            st.session_state.chatbot_state = "confirm_appointment"
            st.rerun()
    
    if st.button("🔙 Go Back to Main Menu"):
        st.session_state.chatbot_state = "greeting"
        st.session_state.conversation.append({"type": "user", "text": "Going back to the main menu."})
        ai_reply = "Hello! I'm your AI receptionist. How can I help you today?"
        audio_file = generate_tts(ai_reply, "greeting.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.rerun()

elif st.session_state.chatbot_state == "confirm_appointment":
    user_id = get_user_id_by_email(st.session_state.user_email)

    # **Prevent duplicate bookings**
    existing_appointment = session.query(Appointment).filter_by(
        user_id=user_id,
        specialist=st.session_state.selected_specialist,
        date=st.session_state.selected_date,
        time_slot=st.session_state.selected_time,
    ).first()

    if not existing_appointment:  # **Only book if no existing appointment**
        booked_appt = book_appointment(
            user_id=user_id,
            specialist=st.session_state.selected_specialist,
            date=st.session_state.selected_date,
            time_slot=st.session_state.selected_time,
        )
        st.session_state.booking_id = booked_appt.id
    else:
        st.session_state.booking_id = existing_appointment.id  # **Use existing booking ID**
    
    if "payment_pending" not in st.session_state:
        st.session_state.payment_pending = True

    if st.session_state.payment_pending:
        if not st.session_state.get("payment_prompt_shown", False):
            ai_reply = "To confirm your appointment, please complete the payment of ₹100 by scanning the QR code below."
            st.session_state.conversation.append({"type": "ai", "text": ai_reply})
            st.session_state.payment_prompt_shown = True
        
        st.image("qr_code.jpg", caption="Scan to Pay ₹100", width=200)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Payment"):
                st.session_state.payment_pending = False
                st.session_state.payment_done = True
                st.rerun()

        with col2:
            if st.button("❌ Cancel Payment"):
                st.session_state.payment_pending = False
                st.session_state.chatbot_state = "greeting"
                st.session_state.conversation.append({"type": "user", "text": "Cancelled the payment."})
                ai_reply = "Payment cancelled. Returning to the main menu."
                audio_file = generate_tts(ai_reply, "cancelled.mp3")
                st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
                st.audio(audio_file, format="audio/mp3")
                st.rerun()

    if st.session_state.get("payment_done", False):
        st.session_state.payment_done = False  # Reset after use

        confirmation_message = (
            f"✅ **Your appointment has been booked!**\n"
            f"- **Doctor:** {st.session_state.selected_specialist}\n"
            f"- **Date:** {st.session_state.selected_date}\n"
            f"- **Time Slot:** {st.session_state.selected_time}\n"
            f"- **Booking ID:** `{st.session_state.booking_id}`"
        )
        reply = f"Your appointment has been booked with {st.session_state.selected_specialist} on {st.session_state.selected_date} at {st.session_state.selected_time}. Your booking ID is {st.session_state.booking_id}."

        audio_file = generate_tts(reply, "appointment.mp3")
        st.audio(audio_file, format="audio/mp3")
        st.session_state.conversation.append({"type": "ai", "text": confirmation_message, "audio": audio_file})

        st.success(f"You're all set! Appointment booked with **{st.session_state.selected_specialist}** "
                        f"on **{st.session_state.selected_date}** at **{st.session_state.selected_time}**."
                        f"Your booking ID is **{st.session_state.booking_id}**. ✅")

        # Email
        appointment_date = datetime.strptime(str(st.session_state.selected_date), "%Y-%m-%d")
        appointment_start_time = datetime.strptime(st.session_state.selected_time, "%I:%M %p").time()
        start_datetime = datetime.combine(appointment_date, appointment_start_time)
        end_datetime = start_datetime + timedelta(minutes=30)

        calendar_link = generate_google_calendar_link(
            title=f"Appointment with {st.session_state.selected_specialist}",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description=f"Consultation with {st.session_state.selected_specialist}",
            location="Online"
        )

        email_body = f"""
        Hi {st.session_state.user_email},

        ✅ Your appointment is confirmed!

        🧑‍⚕️ Specialist: {st.session_state.selected_specialist}  
        📅 Date: {st.session_state.selected_date}  
        ⏰ Time: {st.session_state.selected_time}  
        📌 Booking ID: {st.session_state.booking_id}

        👉 [Click here to add to your Google Calendar]({calendar_link})

        Thanks for using our AI Receptionist!
        """

        try:
            send_confirmation_email(st.session_state.user_email, "Appointment Confirmation ✔️", email_body)
            st.toast("📨 Confirmation email sent!")
        except Exception as e:
            st.error(f"❌ Failed to send confirmation email: {e}")

    if st.button("🔙 Go Back to Main Menu"):
        st.session_state.chatbot_state = "greeting"
        st.session_state.conversation.append({"type": "user", "text": "Going back to the main menu."})
        ai_reply = "Hello! I'm your AI receptionist. How can I help you today?"
        audio_file = generate_tts(ai_reply, "greeting.mp3")
        st.session_state.conversation.append({"type": "ai", "text": ai_reply, "audio": audio_file})
        st.audio(audio_file, format="audio/mp3")
        st.rerun()

    elif st.button("❌ Exit Chat"):
        st.session_state.conversation.append({"type": "user", "text": "I want to exit."})
        st.write("Alright, let me know if you need help later.")
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.conversation = []
        st.rerun()

