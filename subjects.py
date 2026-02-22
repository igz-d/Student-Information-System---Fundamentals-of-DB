#!/usr/bin/env python3

from http.cookies import SimpleCookie
import os
import cgi
import mysql.connector
import html

form = cgi.FieldStorage()
action = form.getvalue("action", "")
subj_id = html.escape(form.getvalue("subjid", ""))
subj_code = html.escape(form.getvalue("subjcode", ""))
subj_desc = html.escape(form.getvalue("subjdesc", ""))
subj_units = html.escape(form.getvalue("subjunits", ""))
subj_sched = html.escape(form.getvalue("subjsched", ""))

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

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    existing_subject = cursor.fetchall()

    if action == "insert" and subj_code and subj_desc and subj_units and subj_sched:
        if not existing_subject:
            cursor.execute(
                '''insert into subjects (subjid, subjcode, subjdesc, subjunits, subjsched)
            values (2000, %s, %s, %s, %s)''', (subj_code, subj_desc, subj_units, subj_sched)
            )
            conn.commit()
        else:
            cursor.execute(
                '''insert into subjects (subjid, subjcode, subjdesc, subjunits, subjsched)
            select max(subjid) + 1, %s, %s, %s, %s
            from subjects''', (subj_code, subj_desc, subj_units, subj_sched)
            )
            conn.commit()

    elif action == "update" and subj_id and subj_code and subj_desc and subj_units and subj_sched:
        cursor.execute(
            "UPDATE subjects SET subjcode=%s, subjdesc=%s, subjunits=%s, subjsched=%s WHERE subjid=%s",
            (subj_code, subj_desc, subj_units, subj_sched, subj_id)
        )
        conn.commit()

    elif action == "delete" and subj_id:
        cursor.execute(
            "DELETE FROM subjects WHERE subjid=%s",
            (int(subj_id),)
        )
        conn.commit()
    
    if subj_id: 
        cursor.execute("select * from subjects WHERE subjid=%s", (subj_id,))
        selected_subject = cursor.fetchone()

    cursor.execute("select s.subjid, s.subjcode, s.subjdesc, s.subjunits, s.subjsched, count(e.studid) from subjects as s left join enroll as e on s.subjid = e.subjid group by s.subjid, s.subjcode, s.subjdesc, s.subjunits, s.subjsched;")
    rows = cursor.fetchall()

    print("""
    <html>
    <head>
        <script>
            function fillForm(subj_id, subj_code, subj_desc, subj_units, subj_sched) {
                document.getElementById("subjid").value = subj_id;
                document.getElementById("subjcode").value = subj_code;
                document.getElementById("subjdesc").value = subj_desc;
                document.getElementById("subjunits").value = subj_units;
                document.getElementById("subjsched").value = subj_sched;
            }
        </script>
    </head>
    <body>

    <table width="100%" cellpadding="10">
        <tr>
            <td width="25%" valign="top">
                <table>
                    <tr> """)
    if subj_id:
        print(
        """ <td> <a href=\"students.py?out_subjid={}\" style=\"cursor:pointer;\">Students</a> </td>
            <td>|</td>
        """
        .format(subj_id)
        )
    else:
        print(
        """<td> <a href=\"students.py\" style=\"cursor:pointer;\">Students</a> </td>
        <td>|</td>
        """
        )

    print("""
    <td><a href="subjects.py"> Subjects </a></td>
    <td>|</td>""")
    
    if subj_id:
        print(
        """ <td> <a href=\"teachers.py?out_subjid={}\" style=\"cursor:pointer;\">Teachers</a> </td>
            <td>|</td>
        """
        .format(subj_id)
        )
    else:
        print(
        """<td> <a href=\"teachers.py\" style=\"cursor:pointer;\">Teachers</a> </td>
        <td>|</td>
        """
        )
    
    
    print(
        """
    </tr>
    </table>
                <h3>Subjects Form</h3>
                <br>
                <form action="subjects.py" method="post">

                    Subject ID:<br>           
                    <input type="text" name="subjid" id="subjid" readonly><br>

                    Code:<br>
                    <input type="text" name="subjcode" id="subjcode"><br>

                    Description:<br>
                    <input type="text" name="subjdesc" id="subjdesc"><br>

                    Units:<br>
                    <input type="text" name="subjunits" id="subjunits"><br>

                    Schedule:<br>
                    <input type="text" name="subjsched" id="subjsched"><br>

                    <input type="hidden" name="action" id="action"><br> 
          
                    <input type="submit" value="Insert"
                        onclick="document.getElementById('action').value='insert'">
                    <input type="submit" value="Update"
                        onclick="document.getElementById('action').value='update'">
                    <input type="submit" value="Delete"
                        onclick="document.getElementById('action').value='delete'">
                </form>
            </td>

            <td width="75%" valign="top">
                <h3>User Table</h3>
                <table id="data-table" border="1" cellpadding="5" cellspacing="0" width="100%">
                    <tr>
                        <th>Subject ID</th>
                        <th>Code</th>
                        <th>Description</th>
                        <th>Units</th>
                        <th>Schedule</th>
                        <th>Total Students</th>
                    </tr>
            </td>
    """)

    for row in rows:
        # row: subjects
        subjid_val = row[0]
        subjcode_val = str(row[1])
        subjdesc_val = str(row[2])
        subjunits_val = row[3]
        subjsched_val = str(row[4])
        subjstudentscount_val = row[5]

        print(
            "<tr onclick=\"window.location='subjects.py?subjid={}'\" "
            "style=\"cursor:pointer;\">".format(subjid_val)
        )

        print("<td>{}</td>".format(subjid_val))
        print("<td>{}</td>".format(subjcode_val))
        print("<td>{}</td>".format(subjdesc_val))
        print("<td>{}</td>".format(subjunits_val))
        print("<td>{}</td>".format(subjsched_val))
        print("<td>{}</td>".format(subjstudentscount_val))
        print("</tr>")

    print("""
                </table>
            </td>
        </tr>
          
        <tr> 
          <td> 
          </td>
        <td>
          
        <table id="students-table" border="1" cellpadding="5" cellspacing="0" width="100%">
            <tr>
                <th>Student ID</th>
                <th>Name</th>
                <th>Address</th>
                <th>Course</th>
                <th>Gender</th>
                <th>Year Level</th>
            </tr>""") 
    
    cursor.execute(
        ''' select s.studid, s.studname, s.studadd, s.studcrs, s.studgender, s.yrlvl
            from students as s
            join enroll as e on s.studid = e.studid
            where e.subjid = %s
        ''',(subj_id,)
    )
    student_row = cursor.fetchall()

    for students in student_row: 
        stud_id_val = students[0]
        stud_name_val = str(students[1])
        stud_add_val = str(students[2])
        stud_crs_val = str(students[3])
        stud_gender_val = str(students[4])
        stud_yr_val = str(students[5]) 

        print('''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
        '''.format(stud_id_val, stud_name_val, stud_add_val, stud_crs_val, stud_gender_val, stud_yr_val)
        )
    
    print("""
          </table>
          </td> 
        </tr>
    </table>
    """) 

    if subj_id and selected_subject:
        print("""
          <script> 
            fillForm("{}", "{}", "{}", "{}", "{}");
          </script>
    """.format(
        selected_subject[0] if subj_id else "",
        selected_subject[1] if subj_id else "",
        selected_subject[2] if subj_id else "",
        selected_subject[3] if subj_id else "",
        selected_subject[4] if subj_id else "")
    )
    
    print("""</body>
    </html>
    """)

except Exception as e:
    print("<h2>Error</h2>")
    print("<pre>{}</pre>".format(e))

finally:
    if 'conn' in locals():
        conn.close()
