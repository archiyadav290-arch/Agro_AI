from fastapi import FastAPI, UploadFile, File
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
        if lat and lon:
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

        # 🌧 ML prediction
        rain = int(model.predict([[temp, humidity]])[0])
        rain = max(0, min(rain, 100))

        # 📊 score
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

        # ✅ IMPORTANT FIX (rain issue solved)
        return {
            "temperature": temp,
            "humidity": humidity,

            "rain_probability": rain,
            "rain": rain,   # 👈 FIX: extra key for frontend

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

        rain = int(model.predict([[temp, humidity]])[0])
        rain = max(0, min(rain, 100))

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
async def chat(data: dict):
    try:
        msg = data.get("message", "").strip().lower()

        # ✅ FIX: empty message handle
        if not msg:
            return {"reply": "🤖 Please type something", "reply_hi": "🤖 कुछ लिखें"}

        if "rain" in msg:
            return {"reply": "🌧 Rain expected", "reply_hi": "🌧 बारिश की संभावना"}

        elif "heat" in msg:
            return {"reply": "🔥 High heat", "reply_hi": "🔥 गर्मी अधिक"}

        elif "crop" in msg:
            return {"reply": "🌾 Check soil & weather before crop selection",
                    "reply_hi": "🌾 फसल से पहले मिट्टी और मौसम देखें"}

        # ✅ fallback fix
        return {"reply": "🤖 Monitor weather regularly",
                "reply_hi": "🤖 मौसम नियमित देखें"}

    except Exception:
        return {"reply": "⚠ Error", "reply_hi": "⚠ त्रुटि"}

# ================= ALERT =================
@app.get("/alert")
async def get_alert(temp: float = 30, rain: int = 20):

    if rain > 75:
        return {"alerts": ["🚨 Heavy Rain"], "alerts_hi": ["🚨 भारी बारिश"]}

    elif temp > 40:
        return {"alerts": ["🔥 Heatwave"], "alerts_hi": ["🔥 लू"]}

    return {"alerts": ["✅ Safe"], "alerts_hi": ["✅ सुरक्षित"]}
