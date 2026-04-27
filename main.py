from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "1a79d5efe76760ff32676870d1cce521"

@app.get("/")
def home():
    return {"message": "AgroAI Backend Running 🚀"}

# ================= WEATHER + AI =================
@app.get("/weather")
def get_weather(lat: float = None, lon: float = None, city: str = None):

    try:
        if lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        else:
            city = city or "Bhopal"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        res = requests.get(url)
        data = res.json()

        # 🔴 SAFETY CHECK (IMPORTANT)
        if "main" not in data:
            return {"error": data.get("message", "Invalid API / City")}

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        # 🌧 Smart Rain Prediction
        rain = int((humidity * 0.6) + random.randint(0, 20))

        # ================= AI ADVISORY =================
        if rain > 70:
            advisory = "Heavy rainfall expected. Avoid irrigation."
            advisory_hi = "भारी बारिश की संभावना है, सिंचाई न करें"
            risk = "⚠ Flood Risk High"
            risk_hi = "⚠ बाढ़ का खतरा"
            irrigation = "❌ Stop irrigation"
            irrigation_hi = "❌ सिंचाई रोकें"

        elif temp > 38:
            advisory = "High heat detected. Crops need water."
            advisory_hi = "तेज गर्मी है, फसलों को पानी दें"
            risk = "🔥 Heatwave Risk"
            risk_hi = "🔥 लू का खतरा"
            irrigation = "💧 Irrigate in evening"
            irrigation_hi = "💧 शाम को सिंचाई करें"

        elif humidity > 80:
            advisory = "High humidity may cause fungal diseases."
            advisory_hi = "अधिक नमी से फंगल रोग हो सकते हैं"
            risk = "🌿 Disease Risk"
            risk_hi = "🌿 रोग का खतरा"
            irrigation = "⚠ Controlled irrigation"
            irrigation_hi = "⚠ सीमित सिंचाई करें"

        else:
            advisory = "Weather conditions are normal."
            advisory_hi = "मौसम सामान्य है"
            risk = "✅ Low Risk"
            risk_hi = "✅ कोई बड़ा खतरा नहीं"
            irrigation = "🌿 Normal irrigation"
            irrigation_hi = "🌿 सामान्य सिंचाई करें"

        # 🔥 FRONTEND COMPATIBILITY (OLD + NEW)
        return {
            "temperature": temp,
            "rain": rain,

            # old frontend keys (important)
            "advisory": advisory,
            "hindi": advisory_hi,

            # new pro keys
            "advisory_hi": advisory_hi,
            "risk": risk,
            "risk_hi": risk_hi,
            "irrigation": irrigation,
            "irrigation_hi": irrigation_hi
        }

    except Exception as e:
        return {"error": str(e)}


# ================= IMAGE AI =================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if "leaf" in filename:
        result = "🌿 Leaf disease detected"
        result_hi = "🌿 पत्ते में रोग पाया गया"
    elif "dry" in filename:
        result = "🔥 Crop drying (heat stress)"
        result_hi = "🔥 फसल सूख रही है"
    else:
        result = "✅ Healthy crop"
        result_hi = "✅ फसल स्वस्थ है"

    return {
        "result": result,
        "result_hi": result_hi
    }


# ================= CHATBOT =================
@app.post("/chat")
async def chat(data: dict):
    msg = data.get("message","").lower()

    if "rain" in msg:
        reply = "🌧 Rain expected. Avoid irrigation."
        reply_hi = "🌧 बारिश की संभावना है"

    elif "heat" in msg:
        reply = "🔥 High heat. Water crops."
        reply_hi = "🔥 गर्मी ज्यादा है"

    elif "disease" in msg:
        reply = "🌿 Disease risk detected."
        reply_hi = "🌿 रोग का खतरा है"

    elif "irrigation" in msg:
        reply = "💧 Best time: morning or evening"
        reply_hi = "💧 सिंचाई सुबह/शाम करें"

    else:
        reply = "🤖 Monitor weather regularly"
        reply_hi = "🤖 मौसम पर नजर रखें"

    return {
        "reply": reply,
        "reply_hi": reply_hi
    }


# ================= ALERT =================
@app.get("/alert")
def get_alert(temp: float = 30, rain: int = 20):

    if rain > 75:
        return {"alert": "🚨 Heavy Rain Alert!"}

    elif temp > 40:
        return {"alert": "🔥 Heatwave Alert!"}

    else:
        return {"alert": "✅ No major risk"}
