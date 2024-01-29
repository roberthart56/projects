import urequests as requests
import network

w = network.WLAN()
w.active(True)

ap = 'Purple Cow 4'
password = 'indiana0623'

w.connect(ap,password)
print(w.ifconfig()	)	#should return a tuple of (IP address, netmask, gateway address, DNS address).

def get_wind_speed(latitude, longitude):
    # NOAA's National Weather Service API endpoint for current weather conditions
    #url = f"https://api.weather.gov/gridpoints/TOP/latitude,longitude/forecast"
    url = f"https://api.weather.gov/points/39.7456,-97.0892"
    try:
        # Send an HTTP GET request to the API endpoint
        response = requests.get(url)
        print(response.text)
        data = response.json()

        # Extract wind speed from the response
        wind_speed = data['properties']['periods'][0]['windSpeed']

        return wind_speed
    except Exception as e:
        print("Error:", e)
        return None

def main():
    # Latitude and longitude coordinates of the location (e.g., Boston, MA)
    latitude = 42.3601
    longitude = -71.0589

    wind_speed = get_wind_speed(latitude, longitude)

    if wind_speed is not None:
        print(f"The current wind speed at the location is {wind_speed}.")
    else:
        print("Failed to retrieve the wind speed.")

if __name__ == "__main__":
    main()

