import json
import requests
from datetime import datetime
from collections import defaultdict

def update_config(new_values):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    config.update(new_values)

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Config updated successfully.")


def load_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json not found.")
        exit()


def get_geo(api_key, city, state, country):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}&appid={api_key}'
    response = requests.get(url)
    data = response.json()

    if not data:
        print("Location not found.")
        return None, None

    return data[0]["lat"], data[0]["lon"]


def get_current_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    response = requests.get(url)
    return response.json()

def get_forecast(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    response = requests.get(url)
    return response.json()

def main():
    while True:
        config = load_config()

        api_key = config["api_key"]
        city = config["city"]
        state = config["state"]
        country = config["country"]

        lat, lon = get_geo(api_key, city, state, country)

        if lat is None:
            print("Invalid location. Fix config.json.")
            continue

        print(f"\nCurrent Location: {city}, {state}, {country}")

        print("\nWhat would you like to know?")
        print("1) Current Weather")
        print("2) Five day Forecast")
        print("3) Change Location")
        print("4) Exit")

        choice = input("Selection: ")

        if choice == '1':
            weather = get_current_weather(api_key, lat, lon)

            temp = weather["main"]["temp"]
            feels_like = weather["main"]["feels_like"]
            temp_min = weather["main"]["temp_min"]
            temp_max = weather["main"]["temp_max"]
            humidity = weather["main"]["humidity"]

            description = weather["weather"][0]["description"]

            wind_speed = weather["wind"]["speed"]
            wind_deg = weather["wind"]["deg"]

            sunrise = datetime.fromtimestamp(weather["sys"]["sunrise"]).strftime('%H:%M')
            sunset = datetime.fromtimestamp(weather["sys"]["sunset"]).strftime('%H:%M')

            print("\n" + "="*30)
            print(f"Weather for {city}")
            print("="*30)
            print(f"Conditions: {description.title()}")
            print(f"Temp: {temp}°F (feels like {feels_like}°F)")
            print(f"High/Low: {temp_max}°F / {temp_min}°F")
            print(f"Humidity: {humidity}%")
            print(f"Wind: {wind_speed} mph @ {wind_deg}°")
            print(f"Sunrise: {sunrise} | Sunset: {sunset}")

        elif choice == '2':
            forecast = get_forecast(api_key, lat, lon)

            daily = defaultdict(list)

            for entry in forecast["list"]:
                date = entry["dt_txt"].split()[0]
                daily[date].append(entry)

            print("\n5-Day Forecast:")
            print("="*30)

            for date, entries in list(daily.items())[:5]:
                temps = [e["main"]["temp"] for e in entries]

                print(f"{date}")
                print(f"High: {max(temps)}°F | Low: {min(temps)}°F")
                print("-"*30)

        elif choice == '3':
            city = input("New City: ")
            state = input("New State: ")
            country = input("New Country: ")

            update_config({
                "city": city,
                "state": state,
                "country": country
            })

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("ERROR: Please enter a correct response.")

if __name__ == "__main__":
    main()