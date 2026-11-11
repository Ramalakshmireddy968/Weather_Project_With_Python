import os
import requests

from dotenv import load_dotenv
from django.conf import settings
from django.shortcuts import render

from .models import CitySearch


load_dotenv(settings.BASE_DIR / ".env")

API_KEY = os.getenv("WEATHER_API_KEY")


def home(request):

    weather_data = None
    error = None

    if request.method == "POST":

        city = request.POST.get("city", "").strip()

        if not city:
            error = "Please enter a city name."

        elif not API_KEY:
            error = "Weather API key is not configured."

        else:

            url = "https://api.openweathermap.org/data/2.5/weather"

            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            }

            try:

                response = requests.get(
                    url,
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:

                    data = response.json()

                    weather_data = {
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"],
                        "description": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"],
                        "temp_min": data["main"]["temp_min"],
                        "temp_max": data["main"]["temp_max"],
                    }

                    CitySearch.objects.create(city=city)

                elif response.status_code == 404:
                    error = "City not found. Try another city."

                elif response.status_code == 401:
                    error = "Invalid API key or API key not activated."

                else:
                    error = "Unable to retrieve weather information."

            except requests.RequestException:
                error = "Network error. Please try again."

    history = CitySearch.objects.order_by("-searched_at")[:5]

    context = {
        "weather": weather_data,
        "error": error,
        "history": history,
    }

    return render(request, "weather/index.html", context)