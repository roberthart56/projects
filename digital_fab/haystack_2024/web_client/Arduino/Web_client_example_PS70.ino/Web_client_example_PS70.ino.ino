
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const int outpin = D5;
const char* ssid = "Purple Cow 4";
const char* password =  "indiana0623";

const String endpoint = "https://api.weather.gov/gridpoints/TOP/31,80/forecast";

void setup() {
  
  pinMode(outpin, OUTPUT);
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  Serial.println("Connected to the WiFi network");

}

void loop() {

  if ((WiFi.status() == WL_CONNECTED)) { //Check the current connection status

    HTTPClient http;

    http.begin(endpoint); //Specify the URL
    int httpResponseCode = http.GET();  // Make the GET request

    if (httpResponseCode > 0) {   // Execute if we get a good response

      String payload = http.getString();
      Serial.println(httpResponseCode);
      // Serial.println(payload); // Uncomment to view the entire payload

      DynamicJsonDocument doc(10000); // Create a buffer of 10000 bytes

      // Deserialize the JSON document
      DeserializationError error = deserializeJson(doc, payload);

      // Test if parsing succeeds.
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.c_str());
        return;
      }

      // Navigate through JSON document, extracting some values
      const int temp = doc["properties"]["periods"][0]["temperature"];
      const char* unit = doc["properties"]["periods"][0]["temperatureUnit"];
      const char* forecast = doc["properties"]["periods"][0]["shortForecast"];

      Serial.print("All I care about is the current weather, which is ");
      Serial.print(temp);
      Serial.print(unit);
      Serial.print(", ");
      Serial.println(forecast);

      http.end();   // Close the connection
      if (temp > 50) {
      digitalWrite(outpin, HIGH);
      }
    }
    
    delay(10000); // Wait 10 seconds between requests 
    digitalWrite(outpin, LOW);
  }
}
