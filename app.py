import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from collections import defaultdict

app = Flask(__name__)

# ---------- CONFIG ----------
def load_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def update_config(new_values):
    config = load_config()
    config.update(new_values)

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

def is_config_valid(config):
    return all([
        config.get("api_key"),
        config.get("city"),
        config.get("state"),
        config.get("country")
    ])

# ---------- API ----------
def get_geo(api_key, city, state, country):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}&appid={api_key}'
    data = requests.get(url).json()

    if isinstance(data, dict) or not data:
        return None, None

    return data[0]["lat"], data[0]["lon"]

def get_current_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    return requests.get(url).json()

def get_forecast(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    return requests.get(url).json()

# ---------- ROUTES ----------

# 🏠 Dashboard (with first-time setup)
@app.route("/")
def dashboard():
    config = load_config()

    # First-time setup screen
    if not is_config_valid(config):
        return render_template("setup.html")

    lat, lon = get_geo(
        config["api_key"],
        config["city"],
        config["state"],
        config["country"]
    )

    if lat is None:
        return "Invalid location or API key. Go to settings."

    current = get_current_weather(config["api_key"], lat, lon)
    forecast_raw = get_forecast(config["api_key"], lat, lon)

    daily = defaultdict(list)
    for entry in forecast_raw["list"]:
        date = entry["dt_txt"].split()[0]
        daily[date].append(entry)

    forecast = []
    for date, entries in list(daily.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]
        forecast.append({
            "date": date,
            "high": max(temps),
            "low": min(temps)
        })

    return render_template(
        "dashboard.html",
        current=current,
        forecast=forecast,
        config=config
    )


# ⚙️ Settings page (also handles setup form POST)
@app.route("/settings", methods=["GET", "POST"])
def settings():
    config = load_config()

    if request.method == "POST":
        update_config({
            "api_key": request.form["api_key"],
            "city": request.form["city"],
            "state": request.form["state"],
            "country": request.form["country"]
        })

        return redirect(url_for("dashboard"))

    return render_template("settings.html", config=config)


# 🚀 Run app
if __name__ == "__main__":
    app.run(debug=True)