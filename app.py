import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from collections import defaultdict

app = Flask(__name__)

# ---------------- CONFIG ----------------
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

# ---------------- API CALLS ----------------
def get_geo(api_key, city, state, country):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}&appid={api_key}'
    response = requests.get(url).json()

    if not response:
        return None, None

    return response[0]["lat"], response[0]["lon"]

def get_current_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    return requests.get(url).json()

def get_forecast(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    return requests.get(url).json()

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    config = load_config()

    if request.method == "POST":
        update_config({
            "api_key": request.form["api_key"],
            "city": request.form["city"],
            "state": request.form["state"],
            "country": request.form["country"]
        })
        return redirect(url_for("index"))

    return render_template("index.html", config=config)


@app.route("/weather")
def weather():
    config = load_config()

    lat, lon = get_geo(
        config["api_key"],
        config["city"],
        config["state"],
        config["country"]
    )

    if lat is None:
        return "Invalid location"

    data = get_current_weather(config["api_key"], lat, lon)

    return render_template("weather.html", data=data, config=config)


@app.route("/forecast")
def forecast():
    config = load_config()

    lat, lon = get_geo(
        config["api_key"],
        config["city"],
        config["state"],
        config["country"]
    )

    data = get_forecast(config["api_key"], lat, lon)

    daily = defaultdict(list)

    for entry in data["list"]:
        date = entry["dt_txt"].split()[0]
        daily[date].append(entry)

    forecast_data = []
    for date, entries in list(daily.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]
        forecast_data.append({
            "date": date,
            "high": max(temps),
            "low": min(temps)
        })

    return render_template("forecast.html", forecast=forecast_data, config=config)


if __name__ == "__main__":
    app.run(debug=True)