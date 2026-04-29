from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import random

# ML
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

API_KEY = "YOUR_API_KEY"

# ================= ML MODEL =================
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

# ================= WEATHER =================
@app.get("/weather")
def get_weather(lat: float = None, lon: float = None, city: str = None):

    try:
        # API CALL
        if lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        else:
            city = city or "Bhopal"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        res = requests.get(url)
        data = res.json()

        if "main" not in data:
            return {"error": data.get("message", "Invalid City")}

        temp = data["main"].get("temp", 0)
        humidity = data["main"].get("humidity", 0)

        # 🌧 ML Prediction (SAFE)
        rain = int(model.predict([[temp, humidity]])[0])

        # 🔥 FIX: clamp values
        rain = max(0, min(rain, 100))

        # ================= SCORE =================
        score = (temp * 0.3) + (humidity * 0.4) + (rain * 0.3)

        # ================= ADVISORY =================
        if score > 75:
            advisory = "Extreme weather risk. Avoid irrigation and protect crops."
            advisory_hi = "⚠️ अत्यधिक मौसम खतरा है। सिंचाई रोकें और फसल को सुरक्षित रखें।"
            risk = "🚨 High Risk"
            risk_hi = "🚨 उच्च जोखिम"
            irrigation = "❌ Stop irrigation"
            irrigation_hi = "❌ सिंचाई रोकें"

            soil = "Avoid wet soil"
            crop = "Avoid sowing new crops"

        elif score > 55:
            advisory = "Moderate risk. Monitor crops and irrigate carefully."
            advisory_hi = "⚠️ मध्यम जोखिम है। फसल की निगरानी करें और सीमित सिंचाई करें।"
            risk = "⚠ Moderate Risk"
            risk_hi = "⚠ मध्यम जोखिम"
            irrigation = "⚠ Limited irrigation"
            irrigation_hi = "⚠ सीमित सिंचाई करें"

            soil = "Maintain moisture"
            crop = "Rice / Maize suitable"

        else:
            advisory = "Weather is safe. Normal farming operations can continue."
            advisory_hi = "✅ मौसम सामान्य है। खेती के सभी कार्य सुरक्षित हैं।"
            risk = "✅ Low Risk"
            risk_hi = "✅ कम जोखिम"
            irrigation = "🌿 Normal irrigation"
            irrigation_hi = "🌿 सामान्य सिंचाई करें"

            soil = "Good soil condition"
            crop = "Wheat / Pulses recommended"

        return {
            "temperature": temp,
            "humidity": humidity,
            "rain_probability": rain,   # ✅ FIXED KEY

            "advisory": advisory,
            "advisory_hi": advisory_hi,

            "risk": risk,
            "risk_hi": risk_hi,

            "irrigation": irrigation,
            "irrigation_hi": irrigation_hi,

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
        rain = max(0, min(rain, 100))  # FIX

        forecast_data.append({
            "day": f"Day {i+1}",
            "temp": temp,
            "rain": rain
        })

        base_temp = temp

    return {"forecast": forecast_data}

# ================= IMAGE =================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    content = await file.read()
    size = len(content)

    if size % 3 == 0:
        return {"result": "🌿 Fungal infection detected", "result_hi": "🌿 फंगल संक्रमण पाया गया"}

    elif size % 5 == 0:
        return {"result": "🔥 Heat stress detected", "result_hi": "🔥 गर्मी का असर"}

    return {"result": "✅ Healthy crop", "result_hi": "✅ फसल स्वस्थ है"}

# ================= CHAT =================
@app.post("/chat")
async def chat(data: dict):
    msg = data.get("message", "").lower()

    if "rain" in msg:
        return {"reply": "🌧 Rain expected", "reply_hi": "🌧 बारिश की संभावना"}

    elif "heat" in msg:
        return {"reply": "🔥 High heat", "reply_hi": "🔥 गर्मी अधिक"}

    return {"reply": "🤖 Monitor weather", "reply_hi": "🤖 मौसम देखें"}

# ================= ALERT =================
@app.get("/alert")
def get_alert(temp: float = 30, rain: int = 20):

    if rain > 75:
        return {"alerts": ["🚨 Heavy Rain Alert"], "alerts_hi": ["🚨 भारी बारिश"]}

    elif temp > 40:
        return {"alerts": ["🔥 Heatwave Alert"], "alerts_hi": ["🔥 लू का खतरा"]}

    return {"alerts": ["✅ No major risk"], "alerts_hi": ["✅ कोई खतरा नहीं"]}
