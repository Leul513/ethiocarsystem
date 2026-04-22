from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_time TEXT,
    server_time TEXT,
    server_name TEXT,
    car_name TEXT,
    car_number TEXT
)
''')
conn.commit()

state = {
    "client_btn": "start",
    "server_btn": "accept",
    "car_name": "",
    "car_number": ""
}

@app.route('/')
def home():
    return "Open /client , /server , /database"

@app.route('/client')
def client():
    return render_template("client.html")

@app.route('/server')
def server():
    return render_template("server.html")

@app.route('/database')
def database():
    c.execute("SELECT * FROM logs ORDER BY id DESC")
    data = c.fetchall()
    return render_template("database.html", data=data)

@app.route('/action', methods=['POST'])
def action():
    data = request.json
    user = data.get("user")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user == "client":
        state["car_name"] = data.get("car_name")
        state["car_number"] = data.get("car_number")

        if state["client_btn"] == "start":
            state["client_btn"] = "process"
        elif state["client_btn"] == "process":
            state["client_btn"] = "stop"
        elif state["client_btn"] == "stop":
            state["client_btn"] = "process"
        elif state["client_btn"] == "accept":
            state["client_btn"] = "start"

    elif user == "server":
        if state["server_btn"] == "accept":
            state["server_btn"] = "mission_complete"
            state["client_btn"] = "stop"
        elif state["server_btn"] == "mission_complete":
            state["server_btn"] = "accept"
            state["client_btn"] = "accept"

            c.execute(
                "INSERT INTO logs (client_time, server_time, server_name, car_name, car_number) VALUES (?, ?, ?, ?, ?)",
                (now, now, "Server1", state["car_name"], state["car_number"])
            )
            conn.commit()

    return jsonify(state)

@app.route('/state')
def get_state():
    return jsonify(state)

if __name__ == '__main__':
    app.run(host='192.168.0.117', port=5000, debug=True)