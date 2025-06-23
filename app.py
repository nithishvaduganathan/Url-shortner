from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import string
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize database
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT NOT NULL,
            short TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_url()

        conn = sqlite3.connect('urls.db')
        c = conn.cursor()

        # Check for duplicate
        c.execute("SELECT short FROM urls WHERE original = ?", (original_url,))
        result = c.fetchone()
        if result:
            flash("Short URL already exists!", "info")
            short_url = result[0]
        else:
            c.execute("INSERT INTO urls (original, short) VALUES (?, ?)", (original_url, short_url))
            conn.commit()
            flash("Short URL created!", "success")

        conn.close()
        return render_template('index.html', short_url=request.host_url + short_url)

    return render_template('index.html')

@app.route('/<short>')
def redirect_short_url(short):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT original FROM urls WHERE short = ?", (short,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "<h1>URL Not Found</h1>", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
