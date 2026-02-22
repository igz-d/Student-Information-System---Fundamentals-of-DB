#!/usr/bin/env python3

from http.cookies import SimpleCookie
import os
import uuid
import cgi
import html
import mysql.connector

form = cgi.FieldStorage()
action = form.getvalue("action", "")
database = form.getvalue("database", "")
username = html.escape(form.getvalue("username", ""))
password = html.escape(form.getvalue("password", ""))

# ================= LOGIN HANDLER =================
if action == "log_in":

    session_id = str(uuid.uuid4())

    session_dir = "sessions"
    os.makedirs(session_dir, exist_ok=True)

    with open(f"{session_dir}/session_{session_id}.txt", "w") as f:
        f.write(f"{username}|{password}|{database}")

    cookie = SimpleCookie()
    cookie["session_id"] = session_id
    cookie["session_id"]["path"] = "/"

    print("Content-Type: text/html")
    print(cookie.output())
    print()

    print("""
    <script>
        alert('Log In Successful');
        window.location.href = "students.py";
    </script>
    """)
    exit()

# ================= NORMAL PAGE =================
print("Content-Type: text/html")
print()

print("""
<html>
<head>
    <title>Student Enrollment System</title>
    <link rel="stylesheet" type="text/css" href="enrol_style.css">
</head>
<body>

<header class="site-header">
    <div class="header-container">
        <img src="logo.png" alt="Logo" class="logo">
        <div class="title-block">
            <h1>STUDENT INFORMATION SYSTEM</h1>
            <p>UNIVERSITY NAME</p>
        </div>
    </div>
</header>

<form action="index.py" method="post">
<input type="hidden" name="action" id="action">

<h3>Login</h3>

Username:<br>
<input type="text" name="username" id="username" required><br>

Password:<br>
<input type="password" name="password" id="password" required><br>
""")

# ================= DATABASE SELECTION =================
if action == "choose_db":

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=username,
            password=password,
        )

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            dbs = cursor.fetchall()

            dbs_list = [db[0] for db in dbs if "_sy" in db[0]]

            print(f"""
            <script> 
                  document.getElementById('username').value = '{username}';
                  document.getElementById('password').value = '{password}';
            </script>
            <p>Select a database to manage:</p>
            <select name="database" id="database" required>
            """)

            for db in dbs_list:
                print(f'<option value="{db}">{db}</option>')

            print("""
            </select><br><br>

            <input type="submit" value="Continue"
                onclick="document.getElementById('action').value='log_in'">
            """)

    except mysql.connector.Error:
        print("""
        <script>
            alert("Invalid username or password.");
            window.location.href = "index.py";
        </script>
        """)

# ================= DEFAULT LOGIN BUTTON =================
else:
    print("""
    <input type="submit" value="Login"
        onclick="document.getElementById('action').value='choose_db'">
    """)

print("""
</form>
</body>
</html>
""")