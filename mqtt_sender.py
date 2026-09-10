import paho.mqtt.client as mqtt
import json
import time


# =====================================================
# MQTT SETTINGS
# =====================================================

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "smart_water_tanker/ruchitha"


# =====================================================
# CREATE MQTT CLIENT
# =====================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)


# =====================================================
# CONNECT TO HIVEMQ
# =====================================================

print("Connecting to MQTT broker...")

client.connect(
    BROKER,
    PORT,
    60
)

print("Connected to HiveMQ!")
print("Starting automatic tanker simulation...\n")


# =====================================================
# INITIAL TANKER VALUES
# =====================================================

water_filled = 150.0

water_sprayed = 0.0

water_remaining = 150.0


# =====================================================
# GPS INITIAL LOCATION
# =====================================================

latitude = 12.971600

longitude = 77.594600


# =====================================================
# ROAD CONDITIONS
# =====================================================

road_conditions = [
    "DRY",
    "DRY",
    "DRY",
    "WET",
    "WET",
    "DRY"
]


counter = 0


# =====================================================
# CONTINUOUS SIMULATION
# =====================================================

while True:

    # ---------------------------------------------
    # NORMAL SPRAYING
    # ---------------------------------------------

    spray_amount = 5.0


    # ---------------------------------------------
    # SIMULATE LEAKAGE
    # ---------------------------------------------

    # Every 6th reading, simulate 15 L leakage

    if counter % 6 == 5:

        leakage = 15.0

    else:

        leakage = 0.0


    # ---------------------------------------------
    # UPDATE WATER VALUES
    # ---------------------------------------------

    total_water_used = spray_amount + leakage


    # Don't use more water than available

    if total_water_used > water_remaining:

        spray_amount = water_remaining

        leakage = 0.0

        total_water_used = spray_amount


    water_sprayed += spray_amount

    water_remaining -= total_water_used


    # ---------------------------------------------
    # ROAD CONDITION
    # ---------------------------------------------

    road_condition = road_conditions[
        counter % len(road_conditions)
    ]


    # ---------------------------------------------
    # SIMULATE GPS MOVEMENT
    # ---------------------------------------------

    latitude += 0.0001

    longitude += 0.0001


    # ---------------------------------------------
    # CREATE SENSOR DATA
    # ---------------------------------------------

    data = {

        "water_filled": round(water_filled, 2),

        "water_sprayed": round(water_sprayed, 2),

        "water_remaining": round(water_remaining, 2),

        "water_leakage": round(leakage, 2),

        "road_condition": road_condition,

        "latitude": round(latitude, 6),

        "longitude": round(longitude, 6)

    }


    # ---------------------------------------------
    # CONVERT DATA TO JSON
    # ---------------------------------------------

    message = json.dumps(data)


    # ---------------------------------------------
    # SEND DATA TO HIVEMQ
    # ---------------------------------------------

    result = client.publish(
        TOPIC,
        message
    )


    # ---------------------------------------------
    # PRINT DATA
    # ---------------------------------------------

    print("Sent:", message)


    # ---------------------------------------------
    # NEXT READING
    # ---------------------------------------------

    counter += 1


    # Wait 5 seconds

    time.sleep(5)