import streamlit as st
import requests
import pandas as pd
import time
import random

st.set_page_config(page_title="InsightOps Sentry", layout="wide")

st.title("🛡️ InsightOps Sentry - AI Monitor")

# אתחול היסטוריה בזיכרון הדפדפן
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['cpu_usage', 'memory_usage', 'errors', 'latency'])

# --- תפריט צד ---
st.sidebar.header("Simulation Control")
mode = st.sidebar.radio("Mode", ["Manual", "Live Simulation"])

if mode == "Manual":
    cpu = st.sidebar.slider("CPU Usage (%)", 0.0, 100.0, 25.0)
    mem = st.sidebar.slider("Memory Usage (MB)", 0.0, 1000.0, 300.0)
    err = st.sidebar.number_input("Errors", 0, 100, 0)
    lat = st.sidebar.slider("Latency (ms)", 0.0, 2000.0, 20.0)
    run_btn = st.sidebar.button("Analyze System")
else:
    run_sim = st.sidebar.toggle("Start Feed")
    # יצירת נתונים אקראיים (עם סיכוי לתקלה)
    if random.random() > 0.8:
        cpu, mem, err, lat = (92.0, 400.0, 12, 1100.0)
    else:
        cpu, mem, err, lat = (random.uniform(10, 30), 300.0, 0, 15.0)
    run_btn = run_sim

# --- שליחת הנתונים ---
if run_btn:
    # בניית ה-Payload בדיוק לפי מה שה-Server מצפה
    payload = {
        "current": {
            "cpu_usage": cpu,
            "memory_usage": mem,
            "errors": int(err),
            "latency": lat
        },
        "history": st.session_state.history.to_dict('records')
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/analyze", json=payload)
        data = response.json()
        
        # שמירה להיסטוריה (לוקחים רק את 20 האחרונים)
        new_row = pd.DataFrame([[cpu, mem, err, lat]], columns=st.session_state.history.columns)
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(20)
        
        # תצוגה
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Status")
            if data["status"] == "OK":
                st.success("SYSTEM HEALTHY")
            else:
                st.error("ANOMALY DETECTED")
            st.line_chart(st.session_state.history['cpu_usage'])
            
        with col2:
            st.subheader("AI Insight")
            st.info(data["agent_analysis"])
            
        if mode == "Live Simulation" and run_sim:
            time.sleep(1)
            st.rerun()
            
    except Exception as e:
        st.error(f"Connection Error: {e}")