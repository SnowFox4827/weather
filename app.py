import json
import os
from collections import defaultdict
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

load_dotenv()

app = Flask(__name__)

CONFIG_FILE = "config.json"
API_KEY = os.getenv("API_KEY")


# ---------- CONFIG ----------

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def update_config(new_values):
    config = load_config()
    config.update(new_values)

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def is_config_valid(config):
    return all([
        API_KEY,
        config.get("city"),
        config.get("state"),
        config.get("country")
    ])


# ---------- API ----------

def get_geo(city, state, country):
    url = (
        "https://api.openweathermap.org/geo/1.0/direct"
        f"?q={city},{state},{country}"
        f"&appid={API_KEY}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not data:
        return None, None

    return data[0]["lat"], data[0]["lon"]


def get_current_weather(lat, lon):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&units=imperial"
        f"&appid={API_KEY}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


def get_forecast(lat, lon):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&units=imperial"
        f"&appid={API_KEY}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


# ---------- ROUTES ----------

@app.route("/")
def dashboard():
    config = load_config()

    if not is_config_valid(config):
        return render_template("setup.html")

    try:
        lat, lon = get_geo(
            config["city"],
            config["state"],
            config["country"]
        )

        if lat is None:
            return "Invalid location."

        current = get_current_weather(lat, lon)
        current_icon = current["weather"][0]["icon"]

        forecast_raw = get_forecast(lat, lon)

    except requests.RequestException:
        return "Unable to contact OpenWeatherMap."

    daily = defaultdict(list)

    for entry in forecast_raw["list"]:
        date = entry["dt_txt"].split()[0]
        daily[date].append(entry)

    forecast = []

    for date, entries in list(daily.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]

        parsed_date = datetime.strptime(date, "%Y-%m-%d")

        forecast.append({
            "date": parsed_date.strftime("%a, %b %d"),
            "high": round(max(temps)),
            "low": round(min(temps)),
            "icon": entries[0]["weather"][0]["icon"]
        })

    return render_template(
        "dashboard.html",
        current=current,
        current_icon=current_icon,
        forecast=forecast,
        config=config
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    config = load_config()

    if request.method == "POST":

        update_config({
            "city": request.form["city"],
            "state": request.form["state"],
            "country": request.form["country"]
        })

        return redirect(url_for("dashboard"))

    return render_template("settings.html", config=config)


# ---------- RUN ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
