from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/test")
def test():
    return "Smart Water Tanker Flask is working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)