from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel
from groq import Groq
import os

app = FastAPI()

# Loading the model we trained in the previous steps
model = joblib.load('anomaly_detector.pkl')

# Connecting to Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Defining the data structure - it is important that the names are the same as what is sent from the app
class ServerMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    errors: int
    latency: float

class AnalysisRequest(BaseModel):
    current: ServerMetrics
    history: list[dict]

def get_agent_explanation(current, status, history):
   # If everything is normal, no in-depth analysis is needed
    if status == "OK":
        return "System is healthy. No action required."
    
    history_text = "No previous history available."
    
    # Check if there is data in history
    if history and len(history) > 0:
        history_text = "" # Initialize as empty text to fill it
        for entry in history[-5:]:
            h_cpu = entry.get('cpu_usage', 0)
            h_lat = entry.get('latency', 0)
            history_text += f"- CPU: {h_cpu}%, Latency: {h_lat}ms\n"

    # # Now the prompt will always know the history_text variable
    prompt = f"""
    You are 'InsightOps Sentry', a DevOps Expert.
    
    CURRENT STATE: {current}
    
    RECENT TREND (Last 5 checks):
    {history_text}
    
    Task: Analyze if this is a sudden spike or a consistent issue. 
    Respond with: SUMMARY, ANALYSIS, and ACTION.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Agent Analysis Error: {str(e)}"

@app.post("/analyze")
def analyze_metrics(request: AnalysisRequest):
    # # Convert the current data to a DataFrame for the model
    input_data = pd.DataFrame([request.current.model_dump()])
    
    # Anomaly prediction
    prediction = model.predict(input_data)[0]
    status = "OK" if prediction == 1 else "ANOMALY DETECTED"
    
    agent_res = get_agent_explanation(request.current.model_dump(), status, request.history)
    
    return {
        "status": status,
        "agent_analysis": agent_res
    }