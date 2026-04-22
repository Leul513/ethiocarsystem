# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os, random
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database
conn = sqlite3.connect("teams.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    members INTEGER,
    team_id TEXT,
    image TEXT,
    created_at TEXT
)
''')
conn.commit()

# Routes
@app.route('/')
def generator():
    return render_template("generator.html")

@app.route('/databasee')
def databasee():
    c.execute("SELECT * FROM teams ORDER BY id DESC")
    data = c.fetchall()
    return render_template("databasee.html", data=data)

@app.route('/team/<int:id>')
def team_profile(id):
    c.execute("SELECT * FROM teams WHERE id=?", (id,))
    team = c.fetchone()
    return render_template("team.html", team=team)

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['team_name']
    members = request.form['members']
    file = request.files['image']

    filename = ""
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    rand = random.randint(1000,9999)
    year = datetime.now().year
    team_id = f"{name[:3].upper()}-{members}-{year}-{rand}"

    c.execute("INSERT INTO teams (team_name, members, team_id, image, created_at) VALUES (?, ?, ?, ?, ?)",
              (name, members, team_id, filename, str(datetime.now())))
    conn.commit()

    return redirect(url_for('databasee'))

if __name__ == '__main__':
    # Binds to the specific IP on port 5000
    app.run(host='192.168.1.5', port=5000)