
    
from flask import Flask, request, jsonify
import requests
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ======================================================
# GROQ CONFIG (FROM ENV)
# ======================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in .env")

client = Groq(api_key=GROQ_API_KEY)


# ======================================================
# DIALOGFLOW RESPONSE HELPER
# ======================================================
def df_text_response(text):
    lines = []

    for line in text.split("\n"):
        line = line.strip()

        # remove bullets or symbols if present
        if line.startswith(("•", "-", "*")):
            line = line[1:].strip()

        if line:
            lines.append(line)

    return jsonify({
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [line]
                }
            } for line in lines
        ]
    })



# ======================================================
# WEATHER CODES
# ======================================================
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    51: "Light drizzle",
    61: "Rain",
    63: "Moderate rain",
    65: "Heavy rain",
    95: "Thunderstorm"
}

# ======================================================
# WEATHER HELPERS
# ======================================================
def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
    headers = {"User-Agent": "KrishiSahayakBot"}
    data = requests.get(url, headers=headers).json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&"
        f"daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,windspeed_10m_max&timezone=auto"
    )
    return requests.get(url).json()

# ======================================================
# GROQ LLM (LLAMA-3)
# ======================================================
def ask_llm(user_query):
    prompt = f"""
You are KrishiSahayak, an agriculture assistant for Indian farmers.

Rules:
- Use very simple farmer-friendly language
- Write exactly 3 short sentences
- Each sentence must be on a new line
- Do NOT use bullets
- Do NOT use symbols like •, -, *
- Do NOT use headings
- Do NOT use markdown or formatting
- Do NOT use emojis inside sentences

Question:
{user_query}
"""


    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  #MODEL
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )

        text = completion.choices[0].message.content.strip()

        if len(text) < 30:
            raise ValueError("LLM response too short")

        return text

    except Exception as e:
        print("Groq error:", e)
        return (
            "🌱 Advice:\n"
            "• Add organic compost or manure\n"
            "• Practice crop rotation\n"
            "• Maintain proper irrigation and drainage"
        )

# ======================================================
# DIALOGFLOW WEBHOOK
# ======================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    query_result = req.get("queryResult", {})
    intent = query_result.get("intent", {}).get("displayName", "")
    user_query = query_result.get("queryText", "")
    params = query_result.get("parameters", {})

    # ---------------- WEATHER ----------------
    city = params.get("geo-city")
    if intent.lower() == "get weather" and city:
        lat, lon = get_coordinates(city)
        if not lat:
            return df_text_response(f"City not found: {city}")

        data = get_weather(lat, lon)
        current = data["current_weather"]
        condition = WEATHER_CODES.get(current["weathercode"], "Unknown")

        forecast = []
        for i in range(min(3, len(data["daily"]["time"]))):
            forecast.append(
                f"📅 {data['daily']['time'][i]}: "
                f"🌡️ {data['daily']['temperature_2m_min'][i]}–"
                f"{data['daily']['temperature_2m_max'][i]}°C, "
                f"🌧️ {data['daily']['precipitation_sum'][i]} mm"
            )

        weather_text = (
            f"🌦️ Weather Update – {city}\n\n"
            f"🌡️ Temperature: {current['temperature']}°C\n"
            f"☁️ Condition: {condition}\n"
            f"💨 Wind Speed: {current['windspeed']} km/h\n\n"
            f"📅 Forecast:\n" + "\n".join(forecast)
        )

        return df_text_response(weather_text)

    # ---------------- FALLBACK → GROQ LLM ----------------
    return df_text_response(ask_llm(user_query))


# ======================================================
# RUN (LOCAL / RENDER)
# ======================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



