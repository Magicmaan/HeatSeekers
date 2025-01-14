import paho.mqtt.client as mqtt
import time

# Define MQTT broker details
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC = "test/topic"

# Callback function when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully!")
        client.subscribe(TOPIC)
    else:
        print(f"Connection failed with code {rc}")

# Callback function when a message is received
def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")

# Callback function when the client publishes a message
def on_publish(client, userdata, mid):
    print(f"Message published: {mid}")

# Set up the MQTT client for publishing and subscribing
client = mqtt.Client()

# Assign the callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

try:
    # Connect to the MQTT broker
    client.connect(BROKER_ADDRESS, PORT, keepalive=60)

    # Start the MQTT client loop in a separate thread
    client.loop_start()

    # Publish messages to the topic
    for i in range(5):
        message = f"Hello MQTT {i}"
        client.publish(TOPIC, message)
        print(f"Publishing message: {message}")
        time.sleep(1)  # Wait for 1 second between messages

    # Wait a bit to receive messages
    time.sleep(2)

finally:
    # Stop the loop and disconnect from the broker
    client.loop_stop()
    client.disconnect()
    print("Disconnected from broker.")