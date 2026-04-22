from flask import Flask, request, render_template_string, send_from_directory
import sqlite3, os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        filename TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/upload", methods=["POST"])
def upload():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    file = request.files["file"]

    filename = file.filename
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (first_name, last_name, filename) VALUES (?, ?, ?)",
              (first_name, last_name, filename))
    conn.commit()
    conn.close()

    return "✅ Registration successful!"

@app.route("/users")
def users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id, first_name, last_name, filename FROM users")
    rows = c.fetchall()
    conn.close()

    html = """
    <h2>Registered Users</h2>
    <table border="1" cellpadding="5">
      <tr><th>ID</th><th>First Name</th><th>Last Name</th><th>File</th></tr>
      {% for row in rows %}
        <tr>
          <td>{{row[0]}}</td>
          <td>{{row[1]}}</td>
          <td>{{row[2]}}</td>
          <td><a href="/uploads/{{row[3]}}" target="_blank">{{row[3]}}</a></td>
        </tr>
      {% endfor %}
    </table>
    """
    return render_template_string(html, rows=rows)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
