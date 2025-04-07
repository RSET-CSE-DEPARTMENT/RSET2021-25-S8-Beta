# payment.py
import streamlit as st
import time

st.set_page_config(page_title="Payment", page_icon="💳")

st.title("💳 Consultation Fee Payment")
st.markdown("Please scan the QR code below to pay the **₹100 consultation fee**.")

# Show QR code
st.image("qr_code.jpg", caption="Scan to Pay ₹100", width=250)

with st.spinner("Waiting for payment confirmation..."):
    time.sleep(2)

st.markdown("---")
st.info("Once you've completed the payment, click below to confirm.")

col1, col2 = st.columns(2)

# ✅ Payment Confirmed
if col1.button("✅ Confirm Payment"):
    with st.spinner("Verifying payment..."):
        time.sleep(2)  # Simulated delay
        st.success("Payment confirmed!")
    st.session_state.confirm_appointment = True
    st.toast("Redirecting to chat...")
    time.sleep(1)
    st.switch_page("chat.py")

# ❌ Payment Canceled
if col2.button("❌ Cancel Payment"):
    st.warning("Payment cancelled.")
    st.session_state.confirm_appointment = False
    st.toast("Returning to main menu...")
    time.sleep(1)
    st.switch_page("chat.py")

