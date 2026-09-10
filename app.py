from flask import Flask, render_template, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = "smart_tanker.db"


# ==========================================
# HOME - DASHBOARD
# ==========================================

@app.route("/")
def home():
    return render_template("dashboard.html")


# ==========================================
# TEST
# ==========================================

@app.route("/test")
def test():
    return "Smart Water Tanker Flask is working!"


# ==========================================
# LIVE DATA
# ==========================================

@app.route("/data")
def data():

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 1
        """)

        row = cursor.fetchone()

        conn.close()

        if row:
            return jsonify(dict(row))

        return jsonify({
            "water_level": 0,
            "water_used": 0,
            "flow_rate": 0,
            "latitude": 0,
            "longitude": 0,
            "road_status": "UNKNOWN",
            "sprinkler": "OFF",
            "leakage": "NO",
            "timestamp": ""
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# HISTORY
# ==========================================

@app.route("/history")
def history():

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows])

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# DATABASE COUNT
# ==========================================

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
            "count": count
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# RUN FLASK
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )