from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# CORS (frontend connect ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "a93a3f678d8bbbd79d19039760a518d1"

# ================= WEATHER =================
@app.get("/weather")
def get_weather(lat: float = None, lon: float = None, city: str = None):

    try:
        if lat and lon:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        else:
            city = city or "Bhopal"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        res = requests.get(url)
        data = res.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        rain = int(humidity * 0.7)

        if rain > 70:
            advisory = "Heavy rainfall expected. Avoid irrigation."
            advisory_hindi = "भारी बारिश - सिंचाई न करें"
        elif temp > 38:
            advisory = "High heat. Give water to crops."
            advisory_hindi = "गर्मी ज्यादा है - पानी दें"
        else:
            advisory = "Weather normal"
            advisory_hindi = "मौसम सामान्य है"

        return {
            "temperature": temp,
            "rain": rain,
            "advisory": advisory,
            "hindi": advisory_hindi
        }

    except:
        return {"error": "Weather fetch failed"}

# ================= IMAGE AI =================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if "leaf" in filename:
        result = "🌿 Leaf disease detected"
    elif "dry" in filename:
        result = "🌿 Crop drying (heat stress)"
    else:
        result = "🌿 Healthy crop"

    return {"result": result}

# ================= CHATBOT =================
@app.post("/chat")
async def chat(data: dict):
    msg = data.get("message","").lower()

    if "rain" in msg:
        reply = "🌧 Rain expected, irrigation avoid"
    elif "heat" in msg:
        reply = "🔥 Give water to crops"
    else:
        reply = "🌱 Crop looks fine"

    return {"reply": reply}
