from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests

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

        # 🔴 IMPORTANT check
        if "main" not in data:
            return {"error": data.get("message", "Invalid API / City")}

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

    except Exception as e:
        return {"error": str(e)}
