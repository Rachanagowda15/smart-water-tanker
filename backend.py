from flask import Flask, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime
import os
import time

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Allow Vercel frontend to access Render backend
CORS(app)


# =========================================================
# MQTT SETTINGS
# =========================================================

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC = "smart_water_tanker/ruchitha"


# =========================================================
# DATABASE
# =========================================================

DATABASE = "smart_tanker.db"


# =========================================================
# LATEST SENSOR DATA
# =========================================================

latest_data = {
    "road_condition": "UNKNOWN",
    "road_temperature": 0,
    "ambient_temperature": 0,
    "rain_sensor": 0,

    "water_level_distance": 0,

    "latitude": 0,
    "longitude": 0,
    "satellites": 0,
    "altitude": 0,
    "speed": 0,

    "sprinkler_decision": "OFF",

    "timestamp": ""
}


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            road_condition TEXT,
            road_temperature REAL,
            ambient_temperature REAL,
            rain_sensor INTEGER,
            water_level_distance REAL,
            latitude REAL,
            longitude REAL,
            satellites INTEGER,
            altitude REAL,
            speed REAL,
            sprinkler_decision TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("Database initialized")


# =========================================================
# SAVE SENSOR DATA
# =========================================================

def save_data(data):

    try:

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sensor_data (
                timestamp,
                road_condition,
                road_temperature,
                ambient_temperature,
                rain_sensor,
                water_level_distance,
                latitude,
                longitude,
                satellites,
                altitude,
                speed,
                sprinkler_decision
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            data.get("timestamp", ""),

            data.get("road_condition", "UNKNOWN"),

            data.get("road_temperature", 0),

            data.get("ambient_temperature", 0),

            data.get("rain_sensor", 0),

            data.get("water_level_distance", 0),

            data.get("latitude", 0),

            data.get("longitude", 0),

            data.get("satellites", 0),

            data.get("altitude", 0),

            data.get("speed", 0),

            data.get("sprinkler_decision", "OFF")
        ))

        conn.commit()
        conn.close()

        print("Sensor data saved")

    except Exception as e:

        print("Database error:", e)


# =========================================================
# MQTT CONNECT
# =========================================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    print("========================================")
    print("MQTT CONNECTION CALLBACK")
    print("Reason code:", reason_code)

    if reason_code == 0:

        print("CONNECTED TO HIVEMQ SUCCESSFULLY")

        result = client.subscribe(TOPIC)

        print("Subscribe result:", result)
        print("Subscribed to:", TOPIC)

    else:

        print("MQTT CONNECTION FAILED")
        print("Reason:", reason_code)

    print("========================================")


# =========================================================
# MQTT DISCONNECT
# =========================================================

def on_disconnect(
    client,
    userdata,
    disconnect_flags,
    reason_code,
    properties=None
):

    print("MQTT DISCONNECTED")
    print("Reason:", reason_code)


# =========================================================
# MQTT MESSAGE RECEIVED
# =========================================================

def on_message(client, userdata, msg):

    global latest_data

    try:

        payload = msg.payload.decode()

        print("========================================")
        print("MQTT MESSAGE RECEIVED")
        print("Topic:", msg.topic)
        print("Payload:", payload)
        print("========================================")

        data = json.loads(payload)

        # Update latest sensor values
        latest_data.update(data)

        # Add server timestamp
        latest_data["timestamp"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Save sensor data to database
        save_data(latest_data)

        print("LATEST DATA UPDATED")

    except json.JSONDecodeError:

        print("Invalid JSON received from ESP32")

    except Exception as e:

        print("MQTT processing error:", e)


# =========================================================
# MQTT CLIENT
# =========================================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect


# =========================================================
# START MQTT
# =========================================================

def start_mqtt():

    while True:

        try:

            print("Connecting to HiveMQ...")
            print("Broker:", BROKER)
            print("Port:", PORT)
            print("Topic:", TOPIC)

            mqtt_client.connect(
                BROKER,
                PORT,
                60
            )

            mqtt_client.loop_start()

            print("MQTT client started")

            break

        except Exception as e:

            print("MQTT connection error:", e)
            print("Retrying MQTT connection in 10 seconds...")

            time.sleep(10)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "project": "Smart Water Tanker",
        "status": "Backend is running",
        "mqtt": "HiveMQ",
        "topic": TOPIC
    })


# =========================================================
# TEST
# =========================================================

@app.route("/test")
def test():

    return "Smart Water Tanker Flask Backend is working!"


# =========================================================
# LIVE DATA
# =========================================================

@app.route("/data")
def get_data():

    try:

        # IMPORTANT:
        # Read the latest value directly from SQLite database.
        # This prevents /data from returning the initial zero values.

        conn = sqlite3.connect(DATABASE)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                timestamp,
                road_condition,
                road_temperature,
                ambient_temperature,
                rain_sensor,
                water_level_distance,
                latitude,
                longitude,
                satellites,
                altitude,
                speed,
                sprinkler_decision
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()

        conn.close()

        # If database contains sensor data
        if row:

            print("Sending latest database data to dashboard")

            return jsonify(dict(row))

        # If database is empty, return default data
        print("No database data available yet")

        return jsonify(latest_data)

    except Exception as e:

        print("Data API error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def get_history():

    try:

        conn = sqlite3.connect(DATABASE)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                timestamp,
                road_condition,
                road_temperature,
                ambient_temperature,
                rain_sensor,
                water_level_distance,
                latitude,
                longitude,
                satellites,
                altitude,
                speed,
                sprinkler_decision
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()

        conn.close()

        history = []

        for row in rows:

            history.append(dict(row))

        return jsonify(history)

    except Exception as e:

        print("History error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# DATABASE COUNT
# =========================================================

@app.route("/database_count")
def database_count():

    try:

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM sensor_data
        """)

        count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "total_records": count
        })

    except Exception as e:

        print("Database count error:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# START MQTT
# =========================================================

start_mqtt()


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )