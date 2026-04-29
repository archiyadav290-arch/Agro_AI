from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
import httpx
import random
import numpy as np
from sklearn.linear_model import LinearRegression

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "1a79d5efe76760ff32676870d1cce521"

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
async def home():
    return {"message": "AgroAI Backend Running 🚀"}

# ================= WEATHER =================
@app.get("/weather")
async def get_weather(lat: float = None, lon: float = None, city: str = None):
    try:
        # ✅ FIX: proper lat/lon check
        if lat is not None and lon is not None:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        else:
            city = city or "Bhopal"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url)
            data = res.json()

        if data.get("cod") != 200:
            return {"error": data.get("message", "API Error")}

        temp = data["main"].get("temp", 0)
        humidity = data["main"].get("humidity", 0)

        # ================= 🌧 RAIN LOGIC =================
        base_rain = model.predict([[temp, humidity]])[0]

        rain = base_rain + (humidity * 0.4) - (temp * 0.2)
        rain = int(max(0, min(rain, 100)))

        # ================= SCORE =================
        score = (temp * 0.3) + (humidity * 0.4) + (rain * 0.3)

        # ================= ADVISORY =================
        if score > 75:
            advisory = "Extreme weather risk. Avoid irrigation."
            advisory_hi = "⚠️ अत्यधिक मौसम खतरा"
            risk = "🚨 High Risk"
            risk_hi = "🚨 उच्च जोखिम"
            irrigation = "❌ Stop irrigation"
            irrigation_hi = "❌ सिंचाई रोकें"

        elif score > 55:
            advisory = "Moderate risk. Be careful."
            advisory_hi = "⚠️ मध्यम जोखिम"
            risk = "⚠ Moderate Risk"
            risk_hi = "⚠ मध्यम जोखिम"
            irrigation = "⚠ Limited irrigation"
            irrigation_hi = "⚠ सीमित सिंचाई"

        else:
            advisory = "Weather is safe."
            advisory_hi = "✅ मौसम सामान्य"
            risk = "✅ Low Risk"
            risk_hi = "✅ कम जोखिम"
            irrigation = "🌿 Normal irrigation"
            irrigation_hi = "🌿 सामान्य सिंचाई"

        # ✅ FINAL RESPONSE (FULL COMPATIBILITY)
        return {
            "temperature": temp,
            "humidity": humidity,

            # 🔥 important
            "rain": rain,
            "rain_probability": rain,

            # 🔥 old frontend fix
            "hindi": advisory_hi,

            # new fields
            "advisory": advisory,
            "advisory_hi": advisory_hi,

            "risk": risk,
            "risk_hi": risk_hi,

            "irrigation": irrigation,
            "irrigation_hi": irrigation_hi
        }

    except Exception as e:
        return {"error": str(e)}

# ================= FORECAST =================
@app.get("/forecast")
async def forecast():
    base_temp = 30
    forecast_data = []

    for i in range(5):
        temp = base_temp + random.randint(-2, 3)
        humidity = random.randint(50, 90)

        rain = int(max(0, min(
            model.predict([[temp, humidity]])[0] + (humidity * 0.4) - (temp * 0.2),
            100
        )))

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
        return {"result": "🌿 Fungal infection", "result_hi": "🌿 फंगल संक्रमण"}
    elif size % 5 == 0:
        return {"result": "🔥 Heat stress", "result_hi": "🔥 गर्मी असर"}

    return {"result": "✅ Healthy crop", "result_hi": "✅ स्वस्थ फसल"}

# ================= CHAT =================
@app.post("/chat")
async def chat(data: dict = Body(...)):
    try:
        msg = data.get("message", "").strip().lower()

        if not msg:
            return {"reply": "🤖 Please type something", "reply_hi": "🤖 कुछ लिखें"}

        if "rain" in msg:
            return {"reply": "🌧 Rain depends on humidity",
                    "reply_hi": "🌧 बारिश नमी पर निर्भर है"}

        elif "heat" in msg:
            return {"reply": "🔥 High heat detected",
                    "reply_hi": "🔥 अधिक गर्मी"}

        elif "crop" in msg:
            return {"reply": "🌾 Choose crop based on soil & weather",
                    "reply_hi": "🌾 मिट्टी और मौसम के अनुसार फसल चुनें"}

        return {"reply": "🤖 Weather looks normal",
                "reply_hi": "🤖 मौसम सामान्य है"}

    except Exception:
        return {"reply": "⚠ Error", "reply_hi": "⚠ त्रुटि"}

# ================= ALERT (FIXED) =================
@app.get("/alert")
async def get_alert(temp: float = 0, rain: float = 0):

    # 🔥 REAL LOGIC (no more always SAFE)
    if rain > 80:
        alert = "🚨 Flood Risk"
        alert_hi = "🚨 बाढ़ का खतरा"

    elif rain > 60:
        alert = "🌧 Heavy Rain Risk"
        alert_hi = "🌧 भारी बारिश का खतरा"

    elif temp > 42:
        alert = "🔥 Heatwave Risk"
        alert_hi = "🔥 लू का खतरा"

    elif temp < 10:
        alert = "❄ Cold Wave Risk"
        alert_hi = "❄ ठंड का खतरा"

    else:
        alert = "✅ Weather is Safe"
        alert_hi = "✅ मौसम सामान्य"

    return {
        "alert": alert,
        "alerts": [alert],
        "alerts_hi": [alert_hi]
    }
