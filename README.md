# Krishi-Sahayak – AI Farming Assistant (Backend)

Krishi-Sahayak is an AI-powered farming chatbot designed to assist Indian farmers with crop-related guidance and weather information using simple, easy-to-understand language.

The chatbot is primarily trained using Dialogflow, and extended using a Flask-based webhook backend to handle dynamic responses like weather updates and AI-generated farming advice.

# What I Built

Developed the complete backend system using Flask

Integrated Dialogflow Webhook for intent handling

Connected Groq LLM (LLaMA 3.1) for intelligent fallback responses

Implemented real-time weather fetching using Open-Meteo API

Used OpenStreetMap (Nominatim) for city-to-coordinate conversion

Designed farmer-friendly responses with strict formatting rules

# How the System Works

User interacts with the chatbot via Dialogflow

Dialogflow detects intent and sends data to the Flask webhook

If the intent is weather-related, real-time weather data is fetched

For other farming queries, the request is sent to Groq LLM

The response is cleaned and formatted before returning to Dialogflow

# AI & Logic Highlights

Uses LLM only as fallback, keeping Dialogflow as the primary brain

Enforces simple language, short sentences and no symbols

Optimized for low-latency responses

Designed specifically for Indian agriculture use cases

# Tech Stack

Backend: Flask (Python)

AI / LLM: Groq API (LLaMA-3.1-8B)

NLP Platform: Dialogflow

APIs: Open-Meteo, OpenStreetMap (Nominatim)

Deployment Ready: Supports local & cloud (Render)

Config: dotenv (.env for secrets)

# Use Case

Crop guidance for farmers

Weather-based farming decisions

Text chatbot integration

Scalable AI assistant for agriculture platforms

## 💬 Chatbot Example

Below is an example interaction with the **Krishi Sahayak AI Chatbot**, showing how it answers farmer queries using LLM-powered reasoning.

### Example: Crop Disease Query
![Chatbot Example](https://github.com/Pratyush-Basu/Chatbot-backend-Krishi-Sahayak/blob/7d5be40998159a45cce41150ba1abda02bc8abd5/Screenshot%20(744).png)


# Future Enhancements

Crop disease image analysis

Multi-language (regional Indian languages) support

Market price prediction

Soil-based crop recommendations
