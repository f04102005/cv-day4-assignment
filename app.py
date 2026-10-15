import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = '1234567890'

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

init_db()
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_email = request.form.get('email')
        login_password = request.form.get('password')
        
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_data WHERE email = ?', (login_email,))
            user = cursor.fetchone()

            if user and check_password_hash(user[3], login_password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard'))
            else:
                return "Invalid email or password. Please try again."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome back, {session['username']}! <br><br> <a href='/logout'>Logout</a>"
    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)