import requests


def get_wind_speed(latitude, longitude):
    # NOAA's National Weather Service API endpoint for current weather conditions
    url = f"https://api.weather.gov/gridpoints/TOP/31,80/forecast"

    try:
        # Send an HTTP GET request to the API endpoint
        response = requests.get(url)
        data = response.json()
        print(data)

        # Extract wind speed from the response
        wind_speed = data['properties']['periods'][0]['windSpeed']
        
        return wind_speed
    except Exception as e:
        print("Error:", e)
        return None

#def main():
    # Latitude and longitude coordinates of the location (e.g., Boston, MA)
latitude = 42.3601
longitude = -71.0589

wind_speed = get_wind_speed(latitude, longitude)

    

# if __name__ == "__main__":
#     main()
