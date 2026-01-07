from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Home route (UI)
@app.route("/")
def home():
    return render_template("index.html")

# API route
@app.route("/zones")
def zones():
    df = pd.read_csv("zone_ui_data.csv")
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
