from flask import Flask, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime
import os

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

DB_NAME = "smart_tanker.db"


def get_db():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            road_condition TEXT,

            road_temperature REAL,

            ambient_temperature REAL,

            rain_sensor TEXT,

            water_level_distance REAL,

            water_used REAL,

            flow_rate REAL,

            latitude REAL,

            longitude REAL,

            satellites INTEGER,

            altitude REAL,

            speed REAL,

            sprinkler_decision TEXT,

            leakage TEXT,

            timestamp TEXT
        )
    """)

    conn.commit()

    conn.close()

    print("Database initialized")


# IMPORTANT
# Initialize database when backend starts
init_db()


# =========================================================
# LATEST DATA
# =========================================================

latest_data = {

    "road_condition": "UNKNOWN",

    "road_temperature": 0,

    "ambient_temperature": 0,

    "rain_sensor": "NO",

    "water_level_distance": 0,

    "water_used": 0,

    "flow_rate": 0,

    "latitude": 0,

    "longitude": 0,

    "satellites": 0,

    "altitude": 0,

    "speed": 0,

    "sprinkler_decision": "OFF",

    "leakage": "NO",

    "timestamp": ""
}


# =========================================================
# SAVE DATA TO DATABASE
# =========================================================

def save_data(data):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data (

            road_condition,

            road_temperature,

            ambient_temperature,

            rain_sensor,

            water_level_distance,

            water_used,

            flow_rate,

            latitude,

            longitude,

            satellites,

            altitude,

            speed,

            sprinkler_decision,

            leakage,

            timestamp

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        data.get(
            "road_condition",
            "UNKNOWN"
        ),

        data.get(
            "road_temperature",
            0
        ),

        data.get(
            "ambient_temperature",
            0
        ),

        data.get(
            "rain_sensor",
            "NO"
        ),

        data.get(
            "water_level_distance",
            0
        ),

        data.get(
            "water_used",
            0
        ),

        data.get(
            "flow_rate",
            0
        ),

        data.get(
            "latitude",
            0
        ),

        data.get(
            "longitude",
            0
        ),

        data.get(
            "satellites",
            0
        ),

        data.get(
            "altitude",
            0
        ),

        data.get(
            "speed",
            0
        ),

        data.get(
            "sprinkler_decision",
            "OFF"
        ),

        data.get(
            "leakage",
            "NO"
        ),

        data.get(
            "timestamp",
            ""
        )
    ))

    conn.commit()

    conn.close()

    print("Sensor data saved")


# =========================================================
# MQTT CONNECT
# =========================================================

def on_connect(
    client,
    userdata,
    flags,
    rc,
    properties=None
):

    if rc == 0:

        print("===================================")
        print("Connected to HiveMQ MQTT broker")
        print("Broker:", BROKER)
        print("Port:", PORT)
        print("Topic:", TOPIC)
        print("===================================")

        client.subscribe(TOPIC)

        print("Subscribed to:", TOPIC)

    else:

        print(
            "MQTT connection failed:",
            rc
        )


# =========================================================
# MQTT MESSAGE
# =========================================================

def on_message(
    client,
    userdata,
    msg
):

    global latest_data

    try:

        # -------------------------------------------------
        # Read MQTT message
        # -------------------------------------------------

        payload = msg.payload.decode()

        print("")
        print("===================================")
        print("MQTT MESSAGE RECEIVED")
        print(payload)
        print("===================================")

        incoming = json.loads(payload)


        # -------------------------------------------------
        # ROAD CONDITION
        # -------------------------------------------------

        latest_data["road_condition"] = incoming.get(
            "road_condition",
            incoming.get(
                "road_status",
                "UNKNOWN"
            )
        )


        # -------------------------------------------------
        # ROAD TEMPERATURE
        # -------------------------------------------------

        latest_data["road_temperature"] = incoming.get(
            "road_temperature",
            0
        )


        # -------------------------------------------------
        # AMBIENT TEMPERATURE
        # -------------------------------------------------

        latest_data["ambient_temperature"] = incoming.get(
            "ambient_temperature",
            incoming.get(
                "temperature",
                0
            )
        )


        # -------------------------------------------------
        # RAIN SENSOR
        # -------------------------------------------------

        latest_data["rain_sensor"] = incoming.get(
            "rain_sensor",
            "NO"
        )


        # -------------------------------------------------
        # WATER LEVEL
        # -------------------------------------------------

        latest_data["water_level_distance"] = incoming.get(
            "water_level_distance",
            incoming.get(
                "water_level",
                0
            )
        )


        # -------------------------------------------------
        # WATER USED
        # -------------------------------------------------

        latest_data["water_used"] = incoming.get(
            "water_used",
            0
        )


        # -------------------------------------------------
        # FLOW RATE
        # -------------------------------------------------

        latest_data["flow_rate"] = incoming.get(
            "flow_rate",
            0
        )


        # -------------------------------------------------
        # GPS LATITUDE
        # -------------------------------------------------

        latest_data["latitude"] = incoming.get(
            "latitude",
            0
        )


        # -------------------------------------------------
        # GPS LONGITUDE
        # -------------------------------------------------

        latest_data["longitude"] = incoming.get(
            "longitude",
            0
        )


        # -------------------------------------------------
        # GPS SATELLITES
        # -------------------------------------------------

        latest_data["satellites"] = incoming.get(
            "satellites",
            0
        )


        # -------------------------------------------------
        # GPS ALTITUDE
        # -------------------------------------------------

        latest_data["altitude"] = incoming.get(
            "altitude",
            0
        )


        # -------------------------------------------------
        # GPS SPEED
        # -------------------------------------------------

        latest_data["speed"] = incoming.get(
            "speed",
            0
        )


        # -------------------------------------------------
        # SPRINKLER
        # -------------------------------------------------

        latest_data["sprinkler_decision"] = incoming.get(
            "sprinkler_decision",
            incoming.get(
                "sprinkler",
                "OFF"
            )
        )


        # -------------------------------------------------
        # LEAKAGE
        # -------------------------------------------------

        latest_data["leakage"] = incoming.get(
            "leakage",
            "NO"
        )


        # -------------------------------------------------
        # TIMESTAMP
        # -------------------------------------------------

        latest_data["timestamp"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        # -------------------------------------------------
        # SAVE TO DATABASE
        # -------------------------------------------------

        save_data(latest_data)


        print("Data saved successfully")


    except Exception as e:

        print(
            "MQTT processing error:",
            e
        )


# =========================================================
# MQTT CLIENT
# =========================================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

mqtt_client.on_connect = on_connect

mqtt_client.on_message = on_message


# =========================================================
# CONNECT TO HIVEMQ
# =========================================================

try:

    print("Connecting to HiveMQ...")

    mqtt_client.connect(
        BROKER,
        PORT,
        60
    )

    mqtt_client.loop_start()

    print("MQTT client started")


except Exception as e:

    print(
        "MQTT connection error:",
        e
    )


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/")
def home():

    return jsonify({

        "message":
        "Smart Water Tanker Backend is Running",

        "status":
        "online"
    })


# =========================================================
# TEST ROUTE
# =========================================================

@app.route("/test")
def test():

    return jsonify({

        "message":
        "Smart Water Tanker Flask Backend is Working!"
    })


# =========================================================
# CURRENT / LIVE DATA
# =========================================================

@app.route("/data")
def data():

    try:

        # -------------------------------------------------
        # READ LATEST DATA DIRECTLY FROM DATABASE
        # -------------------------------------------------

        conn = get_db()

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


        # -------------------------------------------------
        # IF DATABASE HAS DATA
        # -------------------------------------------------

        if row:

            print(
                "Sending latest database data to dashboard"
            )

            return jsonify({

                "timestamp":
                row["timestamp"],

                "road_condition":
                row["road_condition"],

                "road_temperature":
                row["road_temperature"],

                "ambient_temperature":
                row["ambient_temperature"],

                "rain_sensor":
                row["rain_sensor"],

                "water_level_distance":
                row["water_level_distance"],

                "latitude":
                row["latitude"],

                "longitude":
                row["longitude"],

                "satellites":
                row["satellites"],

                "altitude":
                row["altitude"],

                "speed":
                row["speed"],

                "sprinkler_decision":
                row["sprinkler_decision"]

            })


        # -------------------------------------------------
        # NO DATABASE DATA YET
        # -------------------------------------------------

        print(
            "No database data available yet"
        )

        return jsonify(latest_data)


    except Exception as e:

        print(
            "DATA API ERROR:",
            e
        )

        return jsonify({

            "error":
            str(e)

        }), 500


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    try:

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT

                timestamp,

                road_condition,

                road_temperature,

                ambient_temperature,

                water_level_distance,

                latitude,

                longitude,

                satellites,

                speed,

                sprinkler_decision

            FROM sensor_data

            ORDER BY id DESC

            LIMIT 100
        """)

        rows = cursor.fetchall()

        conn.close()


        result = []


        for row in rows:

            result.append({

                "timestamp":
                row["timestamp"],

                "road_condition":
                row["road_condition"],

                "road_temperature":
                row["road_temperature"],

                "ambient_temperature":
                row["ambient_temperature"],

                "water_level_distance":
                row["water_level_distance"],

                "latitude":
                row["latitude"],

                "longitude":
                row["longitude"],

                "satellites":
                row["satellites"],

                "speed":
                row["speed"],

                "sprinkler_decision":
                row["sprinkler_decision"]

            })


        return jsonify(result)


    except Exception as e:

        print(
            "HISTORY API ERROR:",
            e
        )

        return jsonify({

            "error":
            str(e)

        }), 500


# =========================================================
# DATABASE COUNT
# =========================================================

@app.route("/database_count")
def database_count():

    try:

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM sensor_data
        """)

        count = cursor.fetchone()["total"]

        conn.close()


        return jsonify({

            "total_records":
            count

        })


    except Exception as e:

        print(
            "DATABASE COUNT ERROR:",
            e
        )

        return jsonify({

            "error":
            str(e)

        }), 500


# =========================================================
# START SERVER
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