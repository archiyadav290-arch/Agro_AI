from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import random
from gtts import gTTS
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "YOUR_API_KEY"

# ================= HOME =================
@app.get("/")
def home():
    return {"message": "AgroAI PRO Backend Running 🚀"}

# ================= WEATHER + SMART AI =================
@app.get("/weather")
def get_weather(lat: float = None, lon: float = None, city: str = None):

    if lat and lon:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    else:
        city = city or "Bhopal"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    res = requests.get(url)
    data = res.json()

    if "main" not in data:
        return {"error": data.get("message", "Invalid API")}

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]

    # 🌧 Rain prediction (improved logic)
    rain = int((humidity * 0.7) + random.randint(0, 15))

    # ================= DECISION ENGINE =================

    # 🌾 Irrigation Decision
    if rain > 70:
        irrigation = "STOP irrigation"
        irrigation_hi = "सिंचाई रोकें"
    elif temp > 35:
        irrigation = "Irrigate in evening"
        irrigation_hi = "शाम को सिंचाई करें"
    else:
        irrigation = "Normal irrigation"
        irrigation_hi = "सामान्य सिंचाई करें"

    # 🌿 Disease Risk
    if humidity > 80:
        disease = "High fungal disease risk"
        disease_hi = "फंगल रोग का खतरा"
        pesticide = "Spray fungicide"
        pesticide_hi = "फंगीसाइड का छिड़काव करें"
    else:
        disease = "Low disease risk"
        disease_hi = "कम रोग खतरा"
        pesticide = "No spray needed"
        pesticide_hi = "कोई दवा आवश्यक नहीं"

    # ⚠ Risk scoring
    risk_score = (temp / 50) + (humidity / 100) + (rain / 100)

    if risk_score > 2:
        risk = "HIGH RISK"
        risk_hi = "उच्च खतरा"
    elif risk_score > 1.2:
        risk = "MEDIUM RISK"
        risk_hi = "मध्यम खतरा"
    else:
        risk = "LOW RISK"
        risk_hi = "कम खतरा"

    return {
        "temperature": temp,
        "humidity": humidity,
        "rain_probability": rain,

        "irrigation": irrigation,
        "irrigation_hi": irrigation_hi,

        "disease": disease,
        "disease_hi": disease_hi,

        "pesticide": pesticide,
        "pesticide_hi": pesticide_hi,

        "risk": risk,
        "risk_hi": risk_hi
    }

# ================= IMAGE AI =================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if "leaf" in filename:
        return {
            "result": "Leaf disease detected",
            "result_hi": "पत्ते में रोग पाया गया",
            "solution": "Apply fungicide spray",
            "solution_hi": "फंगीसाइड का उपयोग करें"
        }

    return {
        "result": "Healthy crop",
        "result_hi": "फसल स्वस्थ है"
    }

# ================= SMART CHATBOT =================
@app.post("/chat")
async def chat(data: dict):
    msg = data.get("message","").lower()

    if "irrigation" in msg:
        return {"reply": "Check soil moisture & weather", "reply_hi": "मिट्टी और मौसम देखें"}

    elif "pesticide" in msg:
        return {"reply": "Spray only if disease risk high", "reply_hi": "रोग होने पर ही दवा डालें"}

    return {"reply": "Monitoring is important", "reply_hi": "नियमित निगरानी जरूरी है"}

# ================= VOICE ASSISTANT =================
@app.post("/voice")
async def voice(data: dict):
    text = data.get("text", "मौसम सामान्य है")

    tts = gTTS(text=text, lang='hi')
    file_path = "voice.mp3"
    tts.save(file_path)

    return {"audio_file": file_path}

# ================= ALERT SYSTEM =================
@app.get("/alert")
def alert(temp: float = 30, rain: int = 20, humidity: int = 50):

    alerts = []

    if rain > 75:
        alerts.append("🚨 Heavy Rain Alert")

    if temp > 40:
        alerts.append("🔥 Heatwave Alert")

    if humidity > 85:
        alerts.append("🌿 Disease Risk Alert")

    if not alerts:
        alerts.append("✅ All conditions normal")

    return {"alerts": alerts}
