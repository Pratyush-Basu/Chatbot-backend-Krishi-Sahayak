"""
from flask import Flask, request, jsonify
import requests
import os
import time
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument, ResourceExhausted, NotFound

app = Flask(__name__)

# ----------------- Gemini Configuration ----------------- #
# Use environment variable in production instead of hardcoding
genai.configure(api_key="PASTE YOUR API KEY")  # Replace with your actual working key

# Recommended free and stable model
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# ----------------- Weather Codes ----------------- #
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow fall", 95: "Thunderstorm"
}

# ----------------- Weather Functions ----------------- #
def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
    headers = {"User-Agent": "DialogflowWeatherBot"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# ----------------- Gemini Query Function ----------------- #
def ask_gemini(user_query, max_retries=3):
    prompt = f"User asks: {user_query}\nProvide short, simple agricultural advice."
    for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
        try:
            model = genai.GenerativeModel(f"models/{model_name}")
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 200},
            )
            if hasattr(response, "text") and response.text:
                print("Gemini response:", response.text)
                return response.text
            else:
                print("⚠️ No valid text returned. Finish reason:", getattr(response, "finish_reason", "unknown"))
        except Exception as e:
            print(f"Error with {model_name}:", e)
            continue
    return "Sorry, I couldn't generate an answer right now. Please try again."

# ----------------- Flask Webhook ----------------- #
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    city = req.get("queryResult", {}).get("parameters", {}).get("geo-city")
    user_query = req.get("queryResult", {}).get("queryText", "")

    # Weather intent
    if city and intent.lower() == "get weather":
        lat, lon = get_coordinates(city)
        if not lat or not lon:
            return jsonify({"fulfillmentText": f"Sorry, I couldn't find {city}."})

        weather_data = get_weather(lat, lon)
        if not weather_data:
            return jsonify({"fulfillmentText": "Sorry, I couldn't fetch weather info right now."})

        current = weather_data["current_weather"]
        temp = current["temperature"]
        wind = current["windspeed"]
        code = current["weathercode"]
        condition = WEATHER_CODES.get(code, "Unknown")

        daily = weather_data["daily"]
        forecast_lines = []
        for i in range(len(daily["time"])):
            date = daily["time"][i]
            tmin = daily["temperature_2m_min"][i]
            tmax = daily["temperature_2m_max"][i]
            rain = daily["precipitation_sum"][i]
            wind_speed = daily["windspeed_10m_max"][i]
            forecast_lines.append(
                f"📅 {date}: 🌡️ {tmin}°C - {tmax}°C, 🌧️ {rain} mm rain, 💨 {wind_speed} km/h wind"
            )

        response_text = (
            f"The current weather in {city} is {condition}. 🌡️ {temp}°C, 💨 {wind} km/h.\n\n"
            + "\n".join(forecast_lines)
        )
        return jsonify({"fulfillmentText": response_text})

    # Default Fallback Intent → call Gemini
    elif intent == "Default Fallback Intent":
        gemini_response = ask_gemini(user_query)
        return jsonify({"fulfillmentText": gemini_response})

    else:
        return jsonify({"fulfillmentText": "I didn’t understand that."})


# ----------------- Main ----------------- #
if __name__ == "__main__":
    app.run(port=5000, debug=True)

    """
    
    
    
from flask import Flask, request, jsonify
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# ======================================================
# GEMINI CONFIGURATION (FROM ENVIRONMENT VARIABLE)
# ======================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Use a fast & stable Gemini model
MODEL_NAME = "models/gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)

# ======================================================
# WEATHER CODES
# ======================================================
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    95: "Thunderstorm"
}

# ======================================================
# WEATHER FUNCTIONS
# ======================================================
def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
    headers = {"User-Agent": "KrishiSahayakBot"}
    res = requests.get(url, headers=headers).json()
    if res:
        return float(res[0]["lat"]), float(res[0]["lon"])
    return None, None


def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"windspeed_10m_max&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# ======================================================
# GEMINI QUERY FUNCTION (CONCISE & FORMATTED)
# ======================================================
def ask_gemini(user_query):
    prompt = f"""
You are KrishiSahayak, an agriculture assistant chatbot.

Rules:
- Maximum 3 short bullet points
- Simple language
- No long paragraphs
- Use emojis
- Keep response concise

User question:
{user_query}

Response format:
🌱 Advice:
• Point 1
• Point 2
• Point 3
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 120
            }
        )
        return response.text.strip() if hasattr(response, "text") else \
            "❌ Sorry, I couldn’t generate an answer right now."
    except Exception as e:
        print("Gemini error:", e)
        return "❌ AI service is temporarily unavailable."

# ======================================================
# DIALOGFLOW WEBHOOK
# ======================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    query_result = req.get("queryResult", {})
    intent = query_result.get("intent", {}).get("displayName", "")
    parameters = query_result.get("parameters", {})
    user_query = query_result.get("queryText", "")

    # ---------------- WEATHER INTENT ----------------
    city = parameters.get("geo-city")
    if intent.lower() == "get weather" and city:
        lat, lon = get_coordinates(city)
        if not lat:
            return jsonify({"fulfillmentText": f"❌ City not found: {city}"})

        weather_data = get_weather(lat, lon)
        if not weather_data:
            return jsonify({"fulfillmentText": "❌ Unable to fetch weather data right now."})

        current = weather_data["current_weather"]
        temp = current["temperature"]
        wind = current["windspeed"]
        condition = WEATHER_CODES.get(current["weathercode"], "Unknown")

        daily = weather_data["daily"]
        forecast_lines = []
        for i in range(min(3, len(daily["time"]))):
            forecast_lines.append(
                f"📅 {daily['time'][i]}: 🌡️ {daily['temperature_2m_min'][i]}°C - "
                f"{daily['temperature_2m_max'][i]}°C, 🌧️ {daily['precipitation_sum'][i]} mm, "
                f"💨 {daily['windspeed_10m_max'][i]} km/h"
            )

        response_text = f"""
🌦️ Weather Update – {city}

🌡️ Temperature: {temp}°C
☁️ Condition: {condition}
💨 Wind Speed: {wind} km/h

📅 Forecast:
""" + "\n".join(forecast_lines)

        return jsonify({"fulfillmentText": response_text.strip()})

    # ---------------- ALL OTHER QUERIES → GEMINI ----------------
    gemini_response = ask_gemini(user_query)
    return jsonify({"fulfillmentText": gemini_response})

# ======================================================
# RUN (LOCAL / RENDER)
# ======================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
