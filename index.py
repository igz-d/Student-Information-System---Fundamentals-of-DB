#!/usr/bin/env python3

print("Content-Type: text/html\n")

from http.cookies import SimpleCookie
import uuid
import cgi 
import mysql.connector
import html

form = cgi.FieldStorage()
action = form.getvalue("action", "")
database = form.getvalue("database", "")
username = html.escape(form.getvalue("username", ""))
password = html.escape(form.getvalue("password", ""))

if action == "log_in": 

    session_id = str(uuid.uuid4())

    # Save session data to file
    with open(f"/tmp/session_{session_id}.txt", "w") as f:
        f.write(f"{username}|{password}|{database}")

    cookie = SimpleCookie()
    cookie["session_id"] = session_id
    cookie["session_id"]["path"] = "/"

    print(cookie.output())
    print("Content-Type: text/html\n")

    print('''
    <script> 
          alert('Log In Successful'); 
          window.location.href = "students.py";
    </script>
          ''')

print(''' 
<html> 
<head>
    <title>Student Enrollment System</title>
    <link rel="stylesheet" type="text/css" href="enrol_style.css">
</head> 
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
        <input type="hidden" name="action" id="action" value="insert">
        <h3> Login </h3>
        Username: <br> 
        <input type="text" name="username" id="username" required><br>
        Password: <br> 
        <input type="password" name="password" id="password" required><br>
</html>      
''')

if action == "choose_db":
    username = html.escape(form.getvalue("username", ""))
    password = html.escape(form.getvalue("password", ""))

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=username,
            password=password,
        )

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''
                SHOW DATABASES
            ''')
            dbs = cursor.fetchall()
            dbs_list = [db[0] for db in dbs if '_sy' in db[0]]
            
            print('''
            <script>
                document.getElementById("username").value = "{}"; 
                document.getElementById("password").value = "{}";
            </script>
                  
            <p> Select a database to manage:</p>
            <select name="database" id="database" required> 
                    '''.format(username, password))

            for db in dbs_list:
                print(f'<option value="{db}">{db}</option>')

            print('''              
            </select>
                  <br> <br>
                  <input type="submit" value="Continue" onclick="document.getElementById('action').value='log_in'; documnent.getElementById('database').value = document.getElementById('database').value;">
                  </form>
                    ''')

    except mysql.connector.Error:
        print("""
            <script>
                alert("Invalid username or password.");
                window.location.href = "index.py";
            </script>
            """)
    
else:
    print('''
    <input type="submit" value="Login" onclick="document.getElementById('action').value='choose_db'">
    </form>
            ''')
            