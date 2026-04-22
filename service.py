from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# DATABASE
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_number TEXT,
            car_name TEXT,
            latitude TEXT,
            longitude TEXT,
            message TEXT,
            status TEXT,
            date TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ROUTES
@app.route('/clientt')
def clientt():
    return render_template('clientt.html')

@app.route('/serverr')
def serverr():
    return render_template('serverr.html')

@app.route('/databaseee')
def databaseee():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cars ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template('databaseee.html', data=data)

# CLIENT SEND DATA
@app.route('/send_location', methods=['POST'])
def send_location():
    data = request.json
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    now = datetime.now()

    c.execute('''
        INSERT INTO cars (car_number, car_name, latitude, longitude, status, date, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['car_number'],
        data['car_name'],
        data['lat'],
        data['lon'],
        "Waiting",
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S")
    ))

    conn.commit()
    car_id = c.lastrowid
    conn.close()

    return jsonify({"id": car_id, "status": "Request Sent!"})

# SERVER GET ALL CLIENTS
@app.route('/get_clients')
def get_clients():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cars ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "car_number": r[1],
            "car_name": r[2],
            "lat": r[3],
            "lon": r[4],
            "status": r[6]
        })
    return jsonify(result)

# SERVER SEND MESSAGE
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE cars
        SET message=?, status="Replied"
        WHERE id=?
    ''', (data['message'], data['id']))

    conn.commit()
    conn.close()

    return jsonify({"status": "Message Sent!"})

# CLIENT GET MESSAGE
@app.route('/get_message/<int:id>')
def get_message(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT message, status FROM cars WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({
            "message": row[0],
            "status": row[1]
        })
    return jsonify({})

if __name__ == '__main__':
    # Binds to the specific IP on port 5000
    app.run(host='192.168.1.5', port=5000)
