from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import random

# ✅ ML IMPORT
from sklearn.linear_model import LinearRegression
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "1a79d5efe76760ff32676870d1cce521"

# ================= ML MODEL TRAIN =================
X = np.array([
    [28, 50],
    [30, 60],
    [32, 70],
    [35, 80],
    [38, 90]
])

y = np.array([10, 25, 45, 65, 85])

model = LinearRegression()
model.fit(X, y)

# ================= HOME =================
@app.get("/")
def home():
    return {"message": "AgroAI Backend Running 🚀"}

# ================= WEATHER + ML =================
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

        if "main" not in data:
            return {"error": data.get("message", "Invalid City")}

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        # 🌧 ML Rain Prediction
        rain = int(model.predict([[temp, humidity]])[0])

        # ================= AI SCORE =================
        score = (temp * 0.3) + (humidity * 0.4) + (rain * 0.3)

        # ================= ADVISORY =================
        if score > 75:
            advisory = "Extreme weather risk. Avoid irrigation and protect crops."

            advisory_hi = "⚠️ अत्यधिक मौसम खतरा है। सिंचाई रोकें और फसल को सुरक्षित रखें।"

            risk = "🚨 High Risk"
            irrigation = "❌ Stop irrigation"

            soil = "Avoid wet soil"
            crop = "Avoid sowing new crops"

        elif score > 55:
            advisory = "Moderate risk. Monitor crops and irrigate carefully."

            advisory_hi = "⚠️ मध्यम जोखिम है। फसल की निगरानी करें और सीमित सिंचाई करें।"

            risk = "⚠ Moderate Risk"
            irrigation = "⚠ Limited irrigation"

            soil = "Maintain moisture"
            crop = "Rice / Maize suitable"

        else:
            advisory = "Weather is safe. Normal farming operations can continue."

            advisory_hi = "✅ मौसम सामान्य है। खेती के सभी कार्य सुरक्षित हैं।"

            risk = "✅ Low Risk"
            irrigation = "🌿 Normal irrigation"

            soil = "Good soil condition"
            crop = "Wheat / Pulses recommended"

        return {
            "temperature": temp,
            "humidity": humidity,
            "rain": rain,

            "advisory": advisory,
            "advisory_hi": advisory_hi,

            "risk": risk,
            "irrigation": irrigation,

            "soil": soil,
            "crop": crop
        }

    except Exception as e:
        return {"error": str(e)}

# ================= FORECAST =================
@app.get("/forecast")
def forecast():

    base_temp = 30
    forecast_data = []

    for i in range(5):
        temp = base_temp + random.randint(-2, 3)
        humidity = random.randint(50, 90)

        rain = int(model.predict([[temp, humidity]])[0])

        forecast_data.append({
            "day": f"Day {i+1}",
            "temp": temp,
            "rain": rain
        })

        base_temp = temp

    return {"forecast": forecast_data}

# ================= IMAGE AI =================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    size = len(content)

    if size % 3 == 0:
        result = "🌿 Fungal infection detected"
        result_hi = "🌿 फंगल संक्रमण पाया गया"

    elif size % 5 == 0:
        result = "🔥 Heat stress detected"
        result_hi = "🔥 गर्मी का असर"

    else:
        result = "✅ Healthy crop"
        result_hi = "✅ फसल स्वस्थ है"

    return {"result": result, "result_hi": result_hi}

# ================= CHATBOT =================
@app.post("/chat")
async def chat(data: dict):
    msg = data.get("message", "").lower()

    if "rain" in msg:
        return {"reply": "🌧 Rain expected. Avoid irrigation",
                "reply_hi": "🌧 बारिश की संभावना है, सिंचाई न करें"}

    elif "heat" in msg:
        return {"reply": "🔥 High heat. Water crops",
                "reply_hi": "🔥 गर्मी अधिक है, सिंचाई करें"}

    elif "disease" in msg:
        return {"reply": "🌿 Humidity may cause disease",
                "reply_hi": "🌿 अधिक नमी से रोग हो सकता है"}

    elif "irrigation" in msg:
        return {"reply": "💧 Best time: morning/evening",
                "reply_hi": "💧 सिंचाई सुबह या शाम करें"}

    else:
        return {"reply": "🤖 Monitor weather daily",
                "reply_hi": "🤖 रोज मौसम की जानकारी देखें"}

# ================= ALERT =================
@app.get("/alert")
def get_alert(temp: float = 30, rain: int = 20):

    if rain > 75:
        return {"alert": "🚨 Heavy Rain Alert!",
                "alert_hi": "🚨 भारी बारिश की चेतावनी"}

    elif temp > 40:
        return {"alert": "🔥 Heatwave Alert!",
                "alert_hi": "🔥 लू की चेतावनी"}

    else:
        return {"alert": "✅ No major risk",
                "alert_hi": "✅ कोई बड़ा खतरा नहीं"}
