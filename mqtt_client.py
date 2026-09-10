import paho.mqtt.client as mqtt
import json

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_water_tanker/ruchitha"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected successfully")
        client.subscribe(TOPIC)
        print("Subscribed to:", TOPIC)
    else:
        print("MQTT connection failed. Code:", rc)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Received data:")
        print(data)

    except Exception as e:
        print("Error:", e)


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT broker...")

client.connect(BROKER, PORT, 60)

client.loop_forever()