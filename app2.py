import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app2 = Flask(__name__)

app2.secret_key = '1234567890'

def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                status TEXT
            )
        ''')
        conn.commit()

init_db()
@app2.route('/')
def home():
    return redirect(url_for('login'))

@app2.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        res_name = request.form.get('name')
        res_email = request.form.get('email')
        res_password = request.form.get('password')
        
        hashed_pw = generate_password_hash(res_password)
        
        try:
            with sqlite3.connect('users.db') as conn:
                conn.execute('''
                    INSERT INTO user_data (username, email, password)
                    VALUES (?, ?, ?)
                ''', (res_name, res_email, hashed_pw))
                conn.commit()

            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already registered! Please go back and log in."

    return render_template('register.html')
@app2.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name = request.form.get('username')
        login_password = request.form.get('password')
        if login_name == 'admin' and login_password == '1234':
            session['user_id'] = 0
            session['username'] = 'admin'
            session['is_admin'] = True
            return redirect(url_for('tasks'))
        
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_data WHERE username = ?', (login_name,))
            user = cursor.fetchone()

            if user and check_password_hash(user[3], login_password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard'))
            else:
                return "Invalid username or password. Please try again."

    return render_template('login.html')

@app2.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome back, {session['username']}! <br><br> <a href='/logout'>Logout</a>"
    else:
        return redirect(url_for('login'))
@app2.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app2.route('/tasks')
def tasks():
    if not session.get('is_admin'):
        return "Access Denied. You must be an admin to view this page.", 403
        
    with sqlite3.connect('tasks.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        all_tasks = cursor.fetchall()
        
    return render_template('tasks.html', tasks=all_tasks)
@app2.route('/add_task', methods=['POST'])
def add_task():
    if not session.get('is_admin'):
        return "Access Denied.", 403
        
    task_title = request.form.get('title')
    task_status = request.form.get('status')
    
    with sqlite3.connect('tasks.db') as conn:
        conn.execute('''
            INSERT INTO tasks (title, status)
            VALUES (?, ?)
        ''', (task_title, task_status))
        conn.commit()
        
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app2.run(debug=True)