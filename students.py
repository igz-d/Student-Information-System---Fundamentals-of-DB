#!/usr/bin/env python3

import cgi
import mysql.connector
import html
from http.cookies import SimpleCookie
import os

form = cgi.FieldStorage()
action = form.getvalue("action", "")
id = form.getvalue("studid", "")
if type(id) is list:
    id = id[0]
name = html.escape(form.getvalue("name", ""))
address = html.escape(form.getvalue("address", ""))
course = html.escape(form.getvalue("course", ""))
gender = html.escape(form.getvalue("gender", ""))
yearLevel = html.escape(form.getvalue("yearLevel", ""))
subj_id = html.escape(form.getvalue("subjid", ""))
out_subj_id = html.escape(form.getvalue("out_subjid", ""))
selected_subject_id = html.escape(form.getvalue("selected_subject", ""))
database = html.escape(form.getvalue("db", ""))
db_action = form.getvalue("db_action", "")

selected_student = None

print("Content-Type: text/html\n")

cookie = SimpleCookie(os.environ.get("HTTP_COOKIE"))
session = cookie.get("session_id")

if not session:
    print("<h2>Not logged in</h2>")
    exit()

session_id = session.value
file_path = f"sessions/session_{session_id}.txt"

try:
    with open(file_path) as f:
        data = f.read().split("|")

    username, password, database = data

except FileNotFoundError:
    print("<h2>Session expired or invalid</h2>")
    exit()


try:
    conn = mysql.connector.connect(
        host="localhost",
        user=username,
        password=password,
        database=database
    )

    cursor = conn.cursor(buffered=True)

    cursor.execute("SELECT studid FROM students ORDER BY studid LIMIT 1;")
    existing_student = cursor.fetchone()

    if action == "insert" and name and address and course and gender and yearLevel:

        if not existing_student:
            cursor.execute(
                '''insert into students (studid, studname, studadd, studcrs, studgender, yrlvl)
            values (1000, %s, %s, %s, %s, %s)''', (name, address, course, gender, yearLevel)
            )

            conn.commit()

        else:
            cursor.execute(
                '''insert into students (studid, studname, studadd, studcrs, studgender, yrlvl)
            select max(studid) + 1, %s, %s, %s, %s, %s
            from students''', (name, address, course, gender, yearLevel)
            )

            conn.commit()

    elif action == "update" and name and address and course and gender and yearLevel:
        cursor.execute(
            "UPDATE students SET studname=%s, studadd=%s, studcrs=%s, studgender=%s, yrlvl=%s WHERE studid=%s",
            (name, address, course, gender, yearLevel, id)
        )
        conn.commit()

    elif action == "delete" and id:
        cursor.execute ('''
            select * from enroll where studid = %s
        ''', (id,)
        )
        existing_enroll = cursor.fetchone()
        if not existing_enroll:
            cursor.execute(
                "DELETE FROM students WHERE studid=%s",
                (id,)
            )
            conn.commit()
        elif existing_enroll:
            error_msg = "Cannot delete student with existing enrollments."
            if error_msg:
                print(f"""
                <script>
                    alert("{html.escape(error_msg)}");
                    window.location='students.py?studid={id}';
                </script>
                """)
    
    elif action == "enroll_student" and id and out_subj_id:
        cursor.execute(
            '''insert into enroll (studid, subjid) values (%s, %s)''', (int(id), int(out_subj_id))
        )
        conn.commit()

    elif action == "drop_subject" and id and selected_subject_id:
        cursor.execute(
            "DELETE FROM enroll WHERE studid=%s AND subjid=%s",
            (int(id), int(selected_subject_id))
        )
        conn.commit()

        print(f"Location: students.py?studid={id}")
        print()
        exit()

    if db_action in ["db1st_sem", "db2nd_sem", "dbsummer"]:
        print("<script>")
        if db_action == "db1st_sem":
            cursor.execute("CREATE DATABASE IF NOT EXISTS 1stSem_SY2026_2027")
            cursor.execute("USE 1stSem_SY2026_2027")

                # Load schema file
            with open("schema.sql") as f:
                sql_commands = f.read().split(";")

            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
                    conn.commit()
            
            print('''
            alert("Database 1stSem_SY2026_2027 created or already exists.");
            window.location.href = "index.py";
                  ''')
        elif db_action == "db2nd_sem":
            cursor.execute("CREATE DATABASE IF NOT EXISTS 2ndSem_SY2026_2027") 
            cursor.execute("USE 2ndSem_SY2026_2027")

            with open("schema.sql") as f: 
                sql_commands = f.read().split(";") 

            for command in sql_commands: 
                cursor.execute(command)
                conn.commit()
            
            print('''
            alert("Database 2ndSem_SY2026_2027 created or already exists.");
            window.location.href = "index.py";
                  ''')
        elif db_action == "dbsummer":
            cursor.execute("CREATE DATABASE IF NOT EXISTS Summer_SY2026_2027")
            cursor.execute("USE Summer_SY2026_2027")

            with open("schema.sql") as f:
                sql_commands = f.read().split(";")
            
            for command in sql_commands:
                cursor.execute(command)
                conn.commit()

            print('''
            alert("Database Summer_SY2026_2027 created or already exists.");
            window.location.href = "index.py";
                  ''')
        print("</script>")

    cursor.execute("select studid as x, studname, studadd, studcrs, studgender, yrlvl, (select sum(s.subjunits) FROM subjects as s, students as st, enroll as e WHERE s.subjid = e.subjid AND st.studid = e.studid AND st.studid = x) AS TotUnits FROM students;")
    rows = cursor.fetchall()

    if id:
        cursor.execute(
            "select studid as x, studname, studadd, studcrs, studgender, yrlvl, (select sum(s.subjunits) FROM subjects as s, students as st, enroll as e WHERE s.subjid = e.subjid AND st.studid = e.studid AND st.studid = x) AS TotUnits FROM students WHERE studid=%s;",
            (id,)
        )
        selected_student = cursor.fetchone()

    print("""
    <html>
    <head>
        <script>
            function fillForm(studid, name, address, course, gender, yearLevel) {
                document.getElementById("studid").value = studid;
                document.getElementById("studname").value = name;
                document.getElementById("studadd").value = address;
                document.getElementById("studgender").value = gender;
                document.getElementById("studcrs").value = course;
                document.getElementById("yrlvl").value = yearLevel;
            }
        </script>
    </head>
    <body>

    <table width="100%" cellpadding="10">
        <tr>
            <td width="25%" valign="top">
                <table>
                <tr>
                <td><a href="students.py"> Students </a></td>
                <td>|</td>
                <td><a href="subjects.py"> Subjects </a></td>
                <td>|</td>
                <td><a href="teachers.py"> Teachers </a></td>
                <td>
                <form action="students.py" method="post">
                <select onchange="handleDBChange(this.value)">
                    <option value="">Create Database</option>
                    <option value="db1st_sem">1st Sem</option>
                    <option value="db2nd_sem">2nd Sem</option>
                    <option value="dbsummer">Summer</option>
                </select>

                <script>
                function handleDBChange(val) {
                    if (val !== "") {
                        document.getElementById('db_action').value = val;
                        document.forms[0].submit();
                    }
                }
                </script>
                <input type="hidden" name="db_action" id="db_action"><br>
                </form>
                </td>
                </tr>
                </table>
                <h3>Student Form</h3>
                <br>
                <form action="students.py" method="post">
                    Student ID: <br>
                    <input type="text" name="studid" id="studid" readonly><br>
                    
                    Name:<br>
                    <input type="text" name="name" id="studname"><br>

                    Address:<br>
                    <input type="text" name="address" id="studadd"><br>

                    Gender:<br>
                    <input type="text" name="gender" id="studgender"><br>

                    Course:<br>
                    <input type="text" name="course" id="studcrs"><br>

                    Year Level:<br>
                    <input type="text" name="yearLevel" id="yrlvl"><br>

                    <input type="hidden" name="action" id="action"><br> 
          
                    <input type="submit" value="Insert"
                        onclick="document.getElementById('action').value='insert'">
                    <input type="submit" value="Update"
                        onclick="document.getElementById('action').value='update'">
                    <input type="submit" value="Delete"
                        onclick="document.getElementById('action').value='delete'">
                """) 

    print("""
            </td>

            <td width="75%" valign="top">
                <h3>Students Table for: {}</h3>
                <table id="data-table" border="1" cellpadding="5" cellspacing="0" width="100%">
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Course</th>
                        <th>Gender</th>
                        <th>Year Level</th>
                        <th>Total Units</th>
                    </tr>
            </td>
    """.format(database))

    for row in rows:
        # row: student
        id_val = str(row[0])
        name_val = html.escape(str(row[1]))
        address_val = str(row[2])
        course_val = html.escape(str(row[3]))
        gender_val = str(row[4])
        yearLevel_val = str(row[5])
        units_val = str(row[6]) if row[6] is not None else "0"

        if out_subj_id:
            print(
                "<tr onclick=\"window.location='students.py?studid={}&out_subjid={}'\" "
                "style=\"cursor:pointer;\">".format(id_val, out_subj_id)
            )
        elif id and out_subj_id == "" or not id:
            print(
                "<tr onclick=\"window.location='students.py?studid={}'\" "
                "style=\"cursor:pointer;\">".format(id_val)
            )

        print("<td>{}</td>".format(id_val))
        print("<td>{}</td>".format(name_val))
        print("<td>{}</td>".format(address_val))
        print("<td>{}</td>".format(course_val))
        print("<td>{}</td>".format(gender_val))
        print("<td>{}</td>".format(yearLevel_val))
        print("<td>{}</td>".format(units_val))
        print("</tr>")

    print("""
                </table>
            </td>
        </tr>
        <tr> 
            <td>
    """)
    if id and out_subj_id:
        cursor.execute("SELECT * FROM enroll WHERE studid = %s AND subjid = %s;", (id, out_subj_id))
        enrolled_row = cursor.fetchone()

        cursor.execute(
            "SELECT student_sched_conflict(%s, %s) AS conflict_message;",
            (out_subj_id, id)
        )
        result = cursor.fetchone()


        if enrolled_row is None and result[0] is None:
            print("""
                <input type="submit"
                    value="Enroll Student {} in Subject {}"
                    onclick="
                        document.getElementById('action').value='enroll_student';
                        this.form.action='students.py?out_subjid={}'
                    ">
            </form>
            """.format(id, out_subj_id, out_subj_id))
        elif enrolled_row is None and result: 
            print("""
                <input type="submit"
                    value="Enroll Student {} in Subject {}"
                    onclick="
                        document.getElementById('action').value='enroll_student';
                        this.form.action='students.py?out_subjid={}'
                    ">
            </form>
            """.format(id, out_subj_id, out_subj_id))            
        elif enrolled_row:
            if result and result[0]: 
                print("""
                <p style="color:red;">{}</p>
                    </form>
                """.format(result[0]))
            else: 
                print("""
                <input type="submit"
                    value="Enroll Student {} in Subject {}"
                    onclick="
                        document.getElementById('action').value='enroll_student';
                        this.form.action='students.py?out_subjid={}'
                    ">
                    </form>
            """.format(id, out_subj_id, out_subj_id))
                print("</form>")
        elif id and selected_subject_id and result[0] is None:
            print('''
                    <input type="submit" value="Drop Subject {} for Student {}"
                        onclick="
                            document.getElementById('action').value='drop_subject';
                            this.form.action='students.py?studid={}&selected_subject={}'
                        ">
                </form>
                '''.format(selected_subject_id, id, id, selected_subject_id))
        else: 
            if result and result[0]:
                print("""
                <p style="color:red;">{}</p>
                    </form>
                """.format(result[0]))
          
    print("""
           </td>
            <td width="75%" valign="top">
                <h3>Enrolled Subjects</h3>
                <table id="subjects-table" border="1" cellpadding="5" cellspacing="0" width="100%">
                    <tr>
                        <th>Subject ID</th>
                        <th>Code</th>
                        <th>Description</th>
                        <th>Units</th>
                        <th>Schedule</th>
                    </tr>
    """)    
     
    if id:
        temp_id = int(id)    
        cursor.execute("select * from enroll where studid = %s;", (id,))
        enrollment_rows = cursor.fetchall()
        final_subjects_row = []

        for e_row in enrollment_rows:
            subj_id = e_row[2]
            cursor.execute("select subjid, subjcode, subjdesc, subjunits, subjsched from subjects where subjid = %s;", (subj_id,))
            subject_row = cursor.fetchone()
            if subject_row:
                final_subjects_row.append(subject_row)

        for subject_row in final_subjects_row:
            subjid_val = str(subject_row[0])
            subjcode_val = str(subject_row[1])
            subjdesc_val = str(subject_row[2])
            subjunits_val = str(subject_row[3])
            subjsched_val = str(subject_row[4])
            
            print(
                    "<tr onclick=\"window.location='students.py?studid={}&selected_subject={}'\" "
                    "style=\"cursor:pointer;\">".format(temp_id, subjid_val)
                )

            print("<td>{}</td>".format(subjid_val))
            print("<td>{}</td>".format(subjcode_val))
            print("<td>{}</td>".format(subjdesc_val))
            print("<td>{}</td>".format(subjunits_val))
            print("<td>{}</td>".format(subjsched_val))
            print("</tr>")

            cursor.execute("SELECT studid, studname, studadd, studcrs, studgender, yrlvl FROM students WHERE studid=%s", (temp_id,))
            form_row = cursor.fetchone()

            print("""
                <script>
                fillForm('{}','{}','{}','{}','{}','{}');
                </script>
                """.format(form_row[0], form_row[1], form_row[2], form_row[3], form_row[4], form_row[5])
            )

    print("""
        </tr>
    </table>""")

    if selected_student and not selected_subject_id:
        cursor.execute("SELECT studid, studname, studadd, studcrs, studgender, yrlvl FROM students WHERE studid=%s", (selected_student[0],))
        form_row = cursor.fetchone()
        if form_row:
            print("""
                <script>
                fillForm('{}','{}','{}','{}','{}','{}');
                </script>
                """.format(form_row[0], form_row[1], form_row[2], form_row[3], form_row[4], form_row[5])
                )

    print("""
    </body>
    </html>
    """)

except Exception as e:
    print("<h2>Error</h2>")
    print("<pre>{}</pre>".format(e))

finally:
    if 'conn' in locals():
        conn.close()
