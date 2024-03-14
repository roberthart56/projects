'''
Code modified from James Rutter 3/10/24

This is MicroPython code that allows two devices to send values to one another
through Hive MQTT.  Devices are ESP32C3 in this instance.

Each device has button on pin 20 and LED on pin 21 (see esp32c3 pinout)
Device 1 publishes to maker-exchange/haystack/rob/dev1 and subscribes to .../dev2.
Device 2 publishes to maker-exchange/haystack/rob/dev2 and subscribes to .../dev1.
Publishing and sbscribing creates topics dynamically.

Information to add to make it work:
 - comment/uncomment for code particular to each device.
 - wifi ssid and password
 - MQTT credentials
 - Client id. (optional - gets assigned if you do not specify?)
 - Change topics - so you can experiment with your own conversation.
 - Change Payloads for your own purposes.


'''



from machine import Pin
import network
import utime
import json
from umqtt.simple import MQTTClient


# -------- CONFIGURATION --------- #

# WiFi credentials
WIFI_SSID = 'my_ssid'
WIFI_PASSWORD = 'my_password'

# HiveMQ details
MQTT_BROKER = '80cd98a8ff724b559bad56104395d810.s1.eu.hivemq.cloud'
MQTT_PORT = 0 
MQTT_USER = 'my_MQTT_username'
MQTT_PASSWORD = 'my_MQTT_password'	

# Device ID for MQTT Client
#CLIENT_ID = b"esp32c3_rob_2" # custom named client
CLIENT_ID = b"my_client_device_n"

# Generic Maker Exchange Message Format 
#TOPIC = "maker-exchange/haystack/rob/dev2"  #topic for publishing for device 2.
TOPIC = "maker-exchange/haystack/rob/dev1"  #publish topic for device 1
PAYLOAD = json.dumps({
  "sender": "xxx",
  "location": "xxx",
  "messageType": "broadcast",
  "content": "125", # value  to test process   
  "timestamp": "xx"
})

# LED Setup
led = Pin(21, Pin.OUT)
led.value(0) # ensure that the LED is off by default

# Button Setup # 
button = Pin(20, Pin.IN, Pin.PULL_UP)

DEBOUNCE_TIME = 500  # milliseconds
LAST_PRESS_TIME = 0

# Function to handle button press 
def button_pressed():
    global LAST_PRESS_TIME
    current_time = utime.ticks_ms()
    if button.value() == 0 and utime.ticks_diff(current_time, LAST_PRESS_TIME) > DEBOUNCE_TIME:
        LAST_PRESS_TIME = current_time
        return True
    return False

# Connect to WiFi function 
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Connecting to WiFi...")
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        utime.sleep(1)
    print("Connected to WiFi!")
    print(wlan.ifconfig())

# MQTT Callback Function for when message is received
def on_message(topic, msg):
    print("\nReceived MQTT Message!")
    print(f"Topic: {topic.decode()}")
    print(f"Message: {msg.decode()}\n")
    msg_str = msg.decode()  #decode the msg to a string.
    message_dict = json.loads(msg_str) # Parse the JSON message string into a Python dictionary. Thanks, Chad
    content_value = int(message_dict["content"]) # Extract the 'content' field and convert it to an integer
    print(content_value)  
    
    # Blink the LED briefly to signal that a message was received
    led.on()
    utime.sleep(0.5)
    led.off()

# Function to setup and return an MQTT client
def connectMQTT():
    client = MQTTClient(client_id=CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
        keepalive=7200,
        ssl=True,
        ssl_params={'server_hostname': MQTT_BROKER}
        )
    client.set_callback(on_message)  # Set the callback function for incoming messages
    client.connect()
    print("Connecting to MQTT Broker...")
    #client.subscribe("maker-exchange/haystack/rob/dev1")  # Subscribe to dev1
    client.subscribe("maker-exchange/haystack/rob/dev2")  # Subscribe to dev2
    print("Subscribing to topics...")
    return client

# Function to publish messages to the MQTT broker 
def publish(topic, payload):
    print("Publishing message...\n\n")
    print(f"Topic: {topic} /n Payload: {payload}")
    client.publish(topic, payload)
    print("\n\nPublishing complete!")
    
    
# ---------- SETUP --------------- #

# Step 1. Establish WiFi connection
connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)

# Step 2. Setup MQTT and connect
client = connectMQTT()

# ---------- MAIN LOOP ----------- #
while True:
    if button_pressed():
        led.on()
        publish(TOPIC, PAYLOAD)
        utime.sleep(0.5)
        led.off()
    else:
        #print("Waiting for message...")
        client.check_msg()  # Check for new messages (non-blocking)
        utime.sleep(0.1)



