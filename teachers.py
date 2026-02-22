#!/usr/bin/env python3

import cgi
import mysql.connector
import html

print("Content-type: text/html\n")

form = cgi.FieldStorage()
action = form.getvalue("action", "")
t_id = html.escape(form.getvalue("tid", ""))
t_name = html.escape(form.getvalue("tname", ""))
t_dept = html.escape(form.getvalue("tdept", ""))
t_add = html.escape(form.getvalue("tadd", ""))
t_contact = html.escape(form.getvalue("tcontact", ""))
t_status = html.escape(form.getvalue("tstatus", ""))
out_subj_id = html.escape(form.getvalue("out_subjid", ""))


try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="UTMEyt9pLjJq",
        database="studentenrollment"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers")
    existing_teacher = cursor.fetchall()

    if action == "insert" and t_name and t_dept and t_add and t_contact and t_status:
        if not existing_teacher:
            cursor.execute(
                '''insert into teachers (tid, tname, tdept, tadd, tcontact, tstatus)
            values (3000, %s, %s, %s, %s, %s)''', (t_name, t_dept, t_add, t_contact, t_status)
            )
            conn.commit()
        else:
            cursor.execute(
                '''insert into teachers (tid, tname, tdept, tadd, tcontact, tstatus)
            select max(tid) + 1, %s, %s, %s, %s, %s
            from teachers''', (t_name, t_dept, t_add, t_contact, t_status)
            )
            conn.commit()

    elif action == "update" and t_id and t_name and t_dept and t_add and t_contact and t_status:
        cursor.execute(
            "UPDATE teachers SET tname=%s, tdept=%s, tadd=%s, tcontact=%s, tstatus=%s WHERE tid=%s",
            (t_name, t_dept, t_add, t_contact, t_status, t_id)
        )
        conn.commit()

    elif action == "delete" and t_id:
        cursor.execute(
            "DELETE FROM assign WHERE tid=%s",
            (int(t_id),)
        )
        cursor.execute(
            "DELETE FROM teachers WHERE tid=%s",
            (int(t_id),))
        conn.commit()

    elif action == "add_to_teacher" and t_id:
        cursor.execute(
            "INSERT INTO assign (tid, subjid) VALUES (%s, %s)",
            (int(t_id), int(out_subj_id))
        )
        conn.commit()
    
    elif action == "remove_from_teacher" and t_id:
        cursor.execute(
            "DELETE FROM assign WHERE tid=%s AND subjid=%s",
            (int(t_id), int(out_subj_id))
        )
        conn.commit()

    if t_id: 
        cursor.execute("select * from teachers WHERE tid=%s", (t_id,))
        selected_teacher = cursor.fetchone()

    cursor.execute('''select t.tid, t.tname, t.tdept, t.tadd, t.tcontact, t.tstatus,
                   sum(s.subjunits) as total_units
                   from teachers as t 
                   left join assign as a on t.tid = a.tid
                   left join subjects as s on a.subjid = s.subjid
                   group by t.tid, t.tname, t.tdept, t.tadd, t.tcontact, t.tstatus;
                   ''')
    
    rows = cursor.fetchall()

    print("""
    <html>
    <head>
        <script>
            function fillForm(tid, tname, tdept, tadd, tcontact, tstatus) {
                document.getElementById("tid").value = tid;
                document.getElementById("tname").value = tname;
                document.getElementById("tdept").value = tdept;
                document.getElementById("tadd").value = tadd;
                document.getElementById("tcontact").value = tcontact;
                document.getElementById("tstatus").value = tstatus;
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
    """)
    
    if t_id:
        print(
        """ <td> <a href=\"subjects.py?out_tid={}\" style=\"cursor:pointer;\">Subjects</a> </td>
            <td>|</td>
        """
        .format(t_id)
        )
    else:
        print(
        """ <td> <a href=\"subjects.py\" style=\"cursor:pointer;\">Subjects</a> </td>
            <td>|</td>
        """
        )
        
    print("""
            <td><a href="teachers.py"> Teachers </a> </td>
        </table>
    """)
    
    print("""
            <h3>Teachers Form</h3>
                <br>
                <form action="teachers.py" method="post">

                    Teacher ID:<br>           
                    <input type="text" name="tid" id="tid" readonly><br>

                    Name:<br>
                    <input type="text" name="tname" id="tname"><br>

                    Department:<br>
                    <input type="text" name="tdept" id="tdept"><br>
          
                    Address:<br>
                    <input type="text" name="tadd" id="tadd"><br>

                    Contact:<br>
                    <input type="text" name="tcontact" id="tcontact"><br>

                    Status:<br>
                    <input type="text" name="tstatus" id="tstatus"><br>

                    <input type="hidden" name="action" id="action"><br> 
          
                    <input type="submit" value="Insert"
                        onclick="document.getElementById('action').value='insert'">
                    <input type="submit" value="Update"
                        onclick="document.getElementById('action').value='update'">
                    <input type="submit" value="Delete"
                        onclick="document.getElementById('action').value='delete'">
                </form>""")

    print("""
          </td>
            <td width="75%" valign="top">
                <h3>Teachers Table</h3>
                <table id="data-table" border="1" cellpadding="5" cellspacing="0" width="100%">
                    <tr>
                        <th>Teacher ID</th>
                        <th>Name</th>
                        <th>Department</th>
                        <th>Address</th>
                        <th>Contact</th>
                        <th>Status</th>
                        <th>Total Units Assigned</th>
                    </tr>
    """)

    for row in rows:
        # row: subjects
        tid_val = row[0]
        tname_val = str(row[1])
        tdept_val = str(row[2])
        tadd_val = str(row[3])
        tcontact_val = str(row[4])
        tstatus_val = str(row[5])
        t_total_units_val = row[6]

        print(
            "<tr onclick=\"window.location='teachers.py?tid={}&out_subjid={}'\" "
            "style=\"cursor:pointer;\">".format(tid_val, out_subj_id)
        )

        print("<td>{}</td>".format(tid_val))
        print("<td>{}</td>".format(tname_val))
        print("<td>{}</td>".format(tdept_val))
        print("<td>{}</td>".format(tadd_val))
        print("<td>{}</td>".format(tcontact_val))
        print("<td>{}</td>".format(tstatus_val))
        print("<td>{}</td>".format(t_total_units_val))
        print("</tr>")

    print("""
                </table>
            </td>
        </tr>
          
        <tr> 
          <td> 
    """)

    if out_subj_id: 
        cursor.execute("select * from assign;")
        assigned_subjects = cursor.fetchall()
        assigned_subject_ids = {str(sub[0]) for sub in assigned_subjects}

        if out_subj_id in assigned_subject_ids:
            cursor.execute('''select tid from assign where subjid = %s''', (out_subj_id,))
            assigned_teachers = cursor.fetchall()
            print("""
                <h3 style="color:red;"> Subject Code {} is already assigned to teacher {}.</h3>
                """.format(out_subj_id, assigned_teachers[0][0]))    
            # print(""" 
            #       <form action="teachers.py" method="post">
            #         <input type="hidden" name="tid" value="{}">
            #         <input type="hidden" name="out_subjid" value="{}">
            #         <button type="submit" name="action" value="remove_from_teacher">
            #             Remove Subject Code {} from Teacher {}
            #         </button>
            #     </form>
            #     """.format(t_id, out_subj_id, out_subj_id, t_id))

        elif t_id and out_subj_id and out_subj_id not in assigned_subject_ids:
            cursor.execute(
                "select subjid from assign where tid = %s;", (t_id,)
            )
            assigned_subjects = cursor.fetchall()
            assigned_subject_ids = {str(sub[0]) for sub in assigned_subjects}

            if out_subj_id not in assigned_subject_ids:
                cursor.execute("SELECT teacher_sched_conflict(%s, %s) AS conflict_mesasge;",
                               (out_subj_id, t_id)
                )
                result = cursor.fetchone()
                cursor.fetchall() 

                if result and result[0] is None: 
                    print("""
                    <form action="teachers.py" method="post">
                        <input type="hidden" name="tid" value="{}">
                        <input type="hidden" name="out_subjid" value="{}">
                        <button type="submit" name="action" value="add_to_teacher">
                            Add Subject Code {} to Teacher {}
                        </button>
                    </form>
                    """.format(t_id, out_subj_id, out_subj_id, t_id))
                elif result and result[0]:
                    print("""
                    <p style="color:red;">{}</p>
                    """.format(result[0]))

    if t_id and out_subj_id:
        cursor.execute("SELECT * FROM assign WHERE tid = %s AND subjid = %s", (t_id, out_subj_id))
        assigned_row = cursor.fetchone()
        cursor.fetchall()

        cursor.execute(
            "SELECT teacher_sched_conflict(%s, %s) AS conflict_message;",
            (out_subj_id, t_id)
        )
        result = cursor.fetchone()
        cursor.fetchall()


        if assigned_row is None:
            print("""
                <form method="post">
                  <input type="submit"
                    value="Add Subject Code {} to Teacher {}"
                    onclick="
                        document.getElementById('action').value='add_to_teacher';
                        this.form.action='teachers.py?tid={}'
                    ">
                </form>
            """.format(out_subj_id, t_id, t_id))
        elif assigned_row:
            if result:
                print("""
                <p style="color:red;">{}</p>
                    </form>
                """.format(result[0]))
            else: 
                print("</form>")
        elif assigned_row is None and result: 
            print("""
                <p style="color:red;">{}</p>
                    </form>
                """.format(result[0]))
        elif t_id and assigned_row and out_subj_id:
            print('''
                    <input type="submit" value="Drop Subject {} for Teacher {}"
                        onclick="
                            document.getElementById('action').value='drop_subject';
                            this.form.action='teachers.py?tid={}&selected_subject={}'
                        ">
                </form>
                '''.format(t_id, out_subj_id, t_id, out_subj_id))

    print("""
          </td>

        <td width = "75%" valign="top">
        
        <h3> Assigned Subjects </h3>
        <table id="students-table" border="1" cellpadding="5" cellspacing="0" width="100%">
            <tr>
                <th>Subject ID</th>
                <th>Code</th>
                <th>Description</th>
                <th>Units</th>
                <th>Schedule</th>
            </tr>""") 
    
    cursor.execute(
        ''' select s.subjid, s.subjcode, s.subjdesc, s.subjunits, s.subjsched
        from subjects as s
        join assign as a on s.subjid = a.subjid 
        where a.tid = %s
        ''',(t_id,)
    )
    subjects_row = cursor.fetchall()

    if t_id:
        for subject in subjects_row: 
            subj_id_val = subject[0]
            subj_code_val = str(subject[1])
            subj_desc_val = str(subject[2])
            subj_units_val = str(subject[3])
            subj_sched_val = str(subject[4])

            print('''
                <tr onclick="window.location='teachers.py?tid={}&out_subjid={}'" style="cursor:pointer;";>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            '''.format(t_id, subj_id_val, subj_id_val, subj_code_val, subj_desc_val, subj_units_val, subj_sched_val)
            )

        print("""
                </table>
                </td> 
            </tr>
        </table>
        """) 

    if t_id and selected_teacher:
        print("""
          <script> 
            fillForm("{}", "{}", "{}", "{}", "{}", "{}");
          </script>
    """.format(
        selected_teacher[0] if t_id else "",
        selected_teacher[1] if t_id else "",
        selected_teacher[2] if t_id else "",
        selected_teacher[3] if t_id else "",
        selected_teacher[4] if t_id else "", 
        selected_teacher[5] if t_id else "")
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
