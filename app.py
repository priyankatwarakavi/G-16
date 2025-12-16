import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import psycopg2
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

OWNER_DOWNLOAD_KEY = os.getenv('OWNER_DOWNLOAD_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
bcrypt = Bcrypt(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://",
)

def connect_to_db():
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        return None 
    
    try:
        conn = psycopg2.connect(database_url)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None


def create_table():
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users_list (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

create_table()

FULL_FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G-16 Project</title>
    <!-- Favicon link needs a static folder to work correctly with Flask (cannot use absolute paths here easily) -->
    <!-- <link rel="icon" type="image/png" href="favicon.png"> -->
    <style>
        /* Base Styles */
        body {
            font-family: Arial, sans-serif;
            background: #8fd368;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 350px;
            margin: 50px auto;
            background: #f0f2f5;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 40px rgba(115, 180, 10, 0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        label {
            display: block;
            margin-top: 10px;
            color: #555;
        }
        input[type=text], input[type=email], input[type=password], input[type=date] {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        input[type=submit] {
            width: 100%;
            padding: 10px;
            margin-top: 15px;
            background: #4CAF50;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        input[type=submit]:hover {
            background: #45a049;
        }
        a {
            color: #4CAF50;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        nav ul {
            text-align: center;
            padding: 0;
            list-style-type: none;
        }
        nav ul li {
            display: inline;
            margin: 0 10px;
        }

        .page-section {
            display: none; 
        }
        /* Uses Flask flash message categories for colors */
        .flash-red { color: red; text-align: center; }
        .flash-green { color: green; text-align: center; }
        .flash-info { color: blue; text-align: center; }
        ul.flashes { list-style-type: none; padding: 0; margin-top: 10px; }

        /* Logic to show correct section when using URL hashes */
        #welcome:target,
        #register:target,
        #login:target {
            display: block;
        }
        #welcome {
            display: block;
            color: rgb(177, 89, 13);
        }
        .my-hover-link {
            color: blue;
            text-decoration: none;
        }
        .my-hover-link:hover {
            color: black;
        }
        @keyframes float {
            0%, 100% {
                transform: translateY(0px); 
            }
            50% {
                transform: translateY(-10px); 
            }
        }
        
        .floating-heading {
            animation: float 3s ease-in-out infinite; 
        }
        .span {
            font-size: 20px;
            color: darkblue;
            font-weight: bold;
        }
        .span1 {
            font-size: 20px;
            color: rgb(56, 139, 0);
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1><strong>Welcome to G-16 Project</strong></h1>
    <h1 style="color: brown;">Secure User Authentication System Using Flask</h1>
    <h3 style="text-align: center;color: slategrey;"><b> <span class="span">Project Guide:</span></b> <span class="span1" ></span> <span class="span1">Mrs.B.Vijaya Lakshmi</span1><br><b><span class="span">Project members:</span></b> <br><span class="span1" >T Priyanka<br>SK Nafeesa Ruksana <br> E Deepika <br>S Sharon Priyanka</span></h3>
    <div class="container">
        <!-- Flask Flash Messages Rendered Here -->
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul class="flashes">
            {% for category, message in messages %}
              <li class="flash-{{ category }}">{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}

        <!-- Navigation Header -->
        <nav>
            <ul>
                <!-- Note: url_for('index') needs explicit _external=True to keep the #hash intact on redirect -->
                <li><a href="{{ url_for('index', _external=True) }}#register" class="my-hover-link">Register</a></li>
                <li><a href="{{ url_for('index', _external=True) }}#login" class="my-hover-link">Login</a></li>
            </ul>
        </nav>
        <hr>

        <!-- Welcome Page -->
        <div id="welcome" class="page-section">
            <h1 style="color: #0b0b0b;" class="floating-heading">Welcome</h1>
            <p style="text-align: center;">Use the links above to navigate.</p>
        </div>

        <!-- Registration Form Section -->
        <div id="register" class="page-section">
            <h1>Register</h1>
            <form method="POST" action="{{ url_for('register') }}">
                <label>Name</label>
                <input type="text" name="name" required>

                <label>Date of Birth</label>
                <input type="date" name="dob" required>

                <label>Email</label>
                <input type="email" name="email" required>

                <label>Password</label>
                <input type="password" name="password" required>
                
                <input type="submit" value="Register">
            </form>
            <p style="text-align:center; margin-top:10px;">
                <a href="{{ url_for('index', _external=True) }}#login">Already have an account? Login</a>
            </p>
        </div>

        <!-- Login Form Section -->
        <div id="login" class="page-section">
            <h1>Login</h1>
            <form method="POST" action="{{ url_for('login') }}">
                <label>Email</label>
                <input type="email" name="email" required>

                <label>Password</label>
                <input type="password" name="password" required>
                
                <input type="submit" value="Login">
            </form>
            <p style="text-align:center; margin-top:10px;">
                <a href="{{ url_for('index', _external=True) }}#register">No account? Register</a>
            </p>
        </div>

    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(FULL_FRONTEND_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO users_list (name, dob, email, password) VALUES (%s,%s,%s,%s)",
                    (name, dob, email, hashed_password)
                )
                conn.commit()
                flash("Registration successful! Please log in.", "green")
                return redirect(url_for('index', _external=True) + '#login')
            except psycopg2.Error:
                flash("Email already exists or DB error!", "red")
            finally:
                conn.close()
    return redirect(url_for('index', _external=True) + '#register')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT * FROM users_list WHERE email=%s", (email,))
                user_record = cur.fetchone()
                if user_record and bcrypt.check_password_hash(user_record[4], password): # Use index 4 for the hashed password
                    session['user_id'] = user_record[0]
                    session['user_name'] = user_record[1]
                    return redirect(url_for('dashboard'))
                else:
                    flash("Invalid email or password", "red")
            finally:
                conn.close()
    return redirect(url_for('index', _external=True) + '#login')


@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        flash("Login first", "red")
        return redirect(url_for('index', _external=True) + '#login')
        
    return f"<h1>Dashboard</h1><p>Welcome, {session['user_name']}!</p><p style='text-align:center;'><a href='{url_for('logout')}'>Logout</a></p>"


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "green")
    return redirect(url_for('index'))

@app.route('/print_users')
def print_users():
    secret = request.args.get('secret')
    if secret != OWNER_DOWNLOAD_KEY:
        return "Access denied!", 403
    
    conn = connect_to_db()
    if not conn:
        return "Database connection error!", 500
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, dob, email FROM users_list")
        users_list = cur.fetchall()
        print("\n------ USERS DATA ------")
        for u in users_list:
            print(f"ID: {u}, Name: {u}, DOB: {u}, Email: {u}")
        print("------------------------\n")
        return "Users printed in VS Code terminal successfully!"
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=False)
