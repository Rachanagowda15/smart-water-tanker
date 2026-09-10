from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime
import os

# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# MQTT SETTINGS
# ==========================================

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_water_tanker/ruchitha"

DATABASE = "smart_tanker.db"


# ==========================================
# LIVE SENSOR DATA
# ==========================================

sensor_data = {
    "road_condition": "UNKNOWN",
    "rain_sensor": 0,
    "road_temperature": 0.0,
    "ambient_temperature": 0.0,
    "water_level_distance": 0.0,
    "latitude": 0.0,
    "longitude": 0.0,
    "satellites": 0,
    "altitude": 0.0,
    "speed": 0.0,
    "sprinkler_decision": "UNKNOWN"
}


# ==========================================
# CREATE DATABASE
# ==========================================

def create_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            road_condition TEXT,
            rain_sensor INTEGER,
            road_temperature REAL,
            ambient_temperature REAL,
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

    print("SQLite database ready")


# ==========================================
# SAVE SENSOR DATA TO DATABASE
# ==========================================

def save_to_database(data):

    try:

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO sensor_readings (
                timestamp,
                road_condition,
                rain_sensor,
                road_temperature,
                ambient_temperature,
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

            timestamp,

            data.get(
                "road_condition",
                "UNKNOWN"
            ),

            data.get(
                "rain_sensor",
                0
            ),

            data.get(
                "road_temperature",
                0.0
            ),

            data.get(
                "ambient_temperature",
                0.0
            ),

            data.get(
                "water_level_distance",
                0.0
            ),

            data.get(
                "latitude",
                0.0
            ),

            data.get(
                "longitude",
                0.0
            ),

            data.get(
                "satellites",
                0
            ),

            data.get(
                "altitude",
                0.0
            ),

            data.get(
                "speed",
                0.0
            ),

            data.get(
                "sprinkler_decision",
                "UNKNOWN"
            )
        ))

        conn.commit()

        conn.close()

        print("Data saved to SQLite")

    except Exception as e:

        print("SQLite error:", e)


# ==========================================
# MQTT CONNECT
# ==========================================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):

    print()
    print("================================")
    print("          FLASK MQTT")
    print("================================")

    print("Reason code:", reason_code)

    if reason_code == 0:

        print("CONNECTED TO HIVEMQ")

        result, mid = client.subscribe(TOPIC)

        print(
            "Subscribe result:",
            result
        )

        print("Subscribed topic:")
        print(TOPIC)

        print("Waiting for ESP32 data...")

    else:

        print("MQTT CONNECTION FAILED")


# ==========================================
# MQTT MESSAGE RECEIVED
# ==========================================

def on_message(
    client,
    userdata,
    msg
):

    global sensor_data

    print()
    print("================================")
    print("      ESP32 MESSAGE RECEIVED")
    print("================================")

    print("Topic:", msg.topic)

    try:

        # Convert MQTT message to text
        message = msg.payload.decode()

        print("Message:")
        print(message)

        # Convert JSON text to Python dictionary
        data = json.loads(message)

        # Update live sensor data
        sensor_data.update(data)

        print()
        print("LIVE DATA:")
        print(sensor_data)

        # Save to SQLite
        save_to_database(data)

    except Exception as e:

        print("ERROR:", e)


# ==========================================
# MQTT CLIENT
# ==========================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="SmartWaterTankerFlask"
)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


# ==========================================
# CONNECT TO HIVEMQ
# ==========================================

print()
print("Connecting to HiveMQ...")

try:

    mqtt_client.connect(
        BROKER,
        PORT,
        60
    )

except Exception as e:

    print("MQTT ERROR:", e)


# ==========================================
# START MQTT LOOP
# ==========================================

mqtt_client.loop_start()


# ==========================================
# FLASK ROUTES
# ==========================================

@app.route("/")
def home():

    return """
    <h1>Smart Water Tanker Backend</h1>
    <p>Flask server is running successfully.</p>
    <p>MQTT connection is active.</p>
    <p>Use /data to view live sensor data.</p>
    <p>Use /history to view previous readings.</p>
    """


# ==========================================
# LIVE DATA API
# ==========================================

@app.route("/data")
def data():

    return jsonify(sensor_data)


# ==========================================
# HISTORY API
# ==========================================

@app.route("/history")
def history():

    try:

        conn = sqlite3.connect(DATABASE)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT 20
        """)

        rows = cursor.fetchall()

        conn.close()

        return jsonify([
            dict(row)
            for row in rows
        ])

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


# ==========================================
# DATABASE COUNT API
# ==========================================

@app.route("/database_count")
def database_count():

    try:

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM sensor_readings"
        )

        count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "total_records": count
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


# ==========================================
# START FLASK SERVER
# ==========================================

if __name__ == "__main__":

    print()
    print("================================")
    print("       SMART WATER TANKER")
    print("        FLASK SERVER")
    print("================================")

    print()
    print("Dashboard:")
    print("http://127.0.0.1:5000")

    print()
    print("Live Data:")
    print("http://127.0.0.1:5000/data")

    print()
    print("History:")
    print("http://127.0.0.1:5000/history")

    print()
    print("Database Count:")
    print("http://127.0.0.1:5000/database_count")

    # Create database before starting server
    create_database()

    # Render provides PORT automatically.
    # Locally it will use port 5000.
    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )