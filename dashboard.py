from tkinter import *
import time
import ttkthemes
from tkinter.ttk import Treeview
from tkinter import messagebox,filedialog,ttk
import pymysql
import pandas

# functionality part
def iexit():
    result = messagebox.askyesno('Confirm', 'Do you want to Exit?')
    if result:
        root.destroy()

    else:
        pass

def export_data():
    try:
        # Ask user to choose file location and name
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            indexing = studentTable.get_children()
            newlist = []

            for index in indexing:
                content = studentTable.item(index)
                datalist = content['values']
                newlist.append(datalist)

            # Create a Pandas DataFrame
            table = pandas.DataFrame(newlist,
                                     columns=['Id', 'Name', 'Mobile', 'Email', 'Address', 'Gender', 'DOB', 'Added Date',
                                              'Added Time'])

            # Save DataFrame to CSV file
            table.to_csv(file_path, index=False)
            messagebox.showinfo('Success', 'Data is saved successfully')

    except Exception as e:
        messagebox.showerror('Error', f'An error occurred during data export: {e}')

def validate_phone_number(entry):
    if entry.isdigit() and len(entry) == 10:
        return True
    else:
        messagebox.showerror('Error', 'Please enter a valid 10-digit phone number.')
        return False
def toplevel_data(title,button_text,command):
    global idEntry,phoneEntry,nameEntry,emailEntry,addressEntry,genderEntry,DOBEntry,screen
    screen = Toplevel()
    screen.title('Update student')
    screen.grab_set()
    screen.register(False, False)
    idLabel = Label(screen, text='Id', font=('times new roman', 20, 'bold'))
    idLabel.grid(row=0, column=0, padx=30, pady=15, sticky=W)
    idEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    idEntry.grid(row=0, column=1, pady=15, padx=10)

    nameLabel = Label(screen, text='Name', font=('times new roman', 20, 'bold'))
    nameLabel.grid(row=1, column=0, padx=30, pady=15, sticky=W)
    nameEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    nameEntry.grid(row=1, column=1, pady=15, padx=10)

    phoneLabel = Label(screen, text='Phone', font=('times new roman', 20, 'bold'))
    phoneLabel.grid(row=2, column=0, padx=30, pady=15, sticky=W)
    phoneEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    phoneEntry.grid(row=2, column=1, pady=15, padx=10)

    emailLabel = Label(screen, text='Email', font=('times new roman', 20, 'bold'))
    emailLabel.grid(row=3, column=0, padx=30, pady=15, sticky=W)
    emailEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    emailEntry.grid(row=3, column=1, pady=15, padx=10)

    addressLabel = Label(screen, text='Address', font=('times new roman', 20, 'bold'))
    addressLabel.grid(row=4, column=0, padx=30, pady=15, sticky=W)
    addressEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    addressEntry.grid(row=4, column=1, pady=15, padx=10)

    genderLabel = Label(screen, text='Gender', font=('times new roman', 20, 'bold'))
    genderLabel.grid(row=5, column=0, padx=30, pady=15, sticky=W)
    genderEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    genderEntry.grid(row=5, column=1, pady=15, padx=10)

    DOBLabel = Label(screen, text='D.O.B', font=('times new roman', 20, 'bold'))
    DOBLabel.grid(row=6, column=0, padx=30, pady=15, sticky=W)
    DOBEntry = Entry(screen, font=('roman', 15, 'bold'), width=24)
    DOBEntry.grid(row=6, column=1, pady=15, padx=10)

    student_button = ttk.Button(screen, text=button_text, command=command)
    student_button.grid(row=7, columnspan=2, pady=15)

    if title == 'Update Student':
        indexing = studentTable.focus()
        content = studentTable.item(indexing)
        listdata = content['values']
        idEntry.insert(0, listdata[0])
        nameEntry.insert(0, listdata[1])
        phoneEntry.insert(0, listdata[2])
        emailEntry.insert(0, listdata[3])
        addressEntry.insert(0, listdata[4])
        genderEntry.insert(0, listdata[5])
        DOBEntry.insert(0, listdata[6])


def update_data():
    try:
        query = 'UPDATE student SET name=%s, mobile=%s, email=%s, address=%s, gender=%s, DOB=%s, time=%s WHERE id=%s'
        mycursor.execute(query, (
            nameEntry.get(), phoneEntry.get(), emailEntry.get(), addressEntry.get(), genderEntry.get(), DOBEntry.get(),
            currenttime, idEntry.get()))
        con.commit()

        # Calculate CGPA for the updated student
        new_cgpa = calculate_cgpa(idEntry.get())

        # Update the CGPA and grade in the grades table
        query_update_grades = 'UPDATE grades SET cgpa=%s, grade=%s WHERE student_id=%s'
        mycursor.execute(query_update_grades, (new_cgpa, calculate_grade(new_cgpa), idEntry.get()))
        con.commit()

        messagebox.showinfo('Success', f'Id{idEntry.get()} is Updated successfully', parent=screen)
        screen.destroy()
        show_student()

    except Exception as e:
        messagebox.showerror('Error', f'An error occurred during update: {e}', parent=screen)





def calculate_cgpa(student_id):
    try:
        query = 'SELECT marks, credits FROM subjects WHERE student_id=%s'
        mycursor.execute(query, (student_id,))
        subject_data = mycursor.fetchall()

        total_weighted_grade_points = 0
        total_credits = 0

        for subject in subject_data:
            marks, credits = subject
            if marks is not None and credits is not None:
                grade_points = calculate_grade_points(marks)
                total_weighted_grade_points += grade_points * credits
                total_credits += credits

        if total_credits == 0:
            return 0  # Avoid division by zero

        cgpa = total_weighted_grade_points / total_credits

        return round(cgpa, 2)  # Round CGPA to two decimal places

    except Exception as e:
        print(f'Error calculating CGPA: {e}')
        return None

# Function to calculate grade points based on VTU grading system
def calculate_grade_points(marks):
    if marks >= 90:
        return 10
    elif 80 <= marks < 90:
        return 9
    elif 70 <= marks < 80:
        return 8
    elif 60 <= marks < 70:
        return 7
    elif 45 <= marks < 60:
        return 6
    elif 40 <= marks < 45:
        return 4
    else:
        return 0

# Function to calculate grade based on CGPA
def calculate_grade(cgpa):
    if cgpa >= 9.0:
        return 'A+'
    elif 8.0 <= cgpa < 9.0:
        return 'A'
    elif 7.0 <= cgpa < 8.0:
        return 'B'
    elif 6.0 <= cgpa < 7.0:
        return 'C'
    elif 5.0 <= cgpa < 6.0:
        return 'D'
    else:
        return 'F'


# Function to display grades in a separate window
def show_student_grades():
    # Create a new window for displaying student grades
    grade_window = Toplevel()
    grade_window.title('Student Grades')

    # Add labels, Treeview, or any other widgets to display the grades
    grade_table = Treeview(grade_window, columns=('Student ID', 'Subject', 'Marks', 'Credits', 'CGPA', 'Grade'))
    grade_table.heading('Student ID', text='Student ID')
    grade_table.heading('Subject', text='Subject')
    grade_table.heading('Marks', text='Marks')
    grade_table.heading('Credits', text='Credits')
    grade_table.heading('CGPA', text='CGPA')
    grade_table.heading('Grade', text='Grade')

    # Set anchor for each column to CENTER
    for col in grade_table['columns']:
        grade_table.heading(col, anchor=CENTER)
        grade_table.column(col, anchor=CENTER)

    # Iterate through students
    for item in studentTable.get_children():
        student_id = studentTable.item(item, 'values')[0]

        # Fetch subject details for the student
        query_fetch_subjects = 'SELECT subject, marks, credits FROM subjects WHERE student_id=%s'
        mycursor.execute(query_fetch_subjects, (student_id,))
        subject_data = mycursor.fetchall()

        # If there are no subjects, skip to the next student
        if not subject_data:
            continue

        # Calculate CGPA and Grade for the student
        cgpa = calculate_cgpa(student_id)
        grade = calculate_grade(cgpa)

        # Display student details in the Treeview
        for subject in subject_data:
            grade_table.insert('', END, values=(student_id, subject[0], subject[1], subject[2], cgpa, grade))

    grade_table.pack()

def show_student_marks():
    try:
        # Get selected student data from the treeview
        selected_item = studentTable.selection()

        if not selected_item:
            messagebox.showwarning('Warning', 'Please select a student.')
            return

        student_data = studentTable.item(selected_item)['values']

        # Extract student ID from the selected row
        student_id = student_data[0]

        # Query to fetch student marks
        query = 'SELECT subject, marks, credits FROM subjects WHERE student_id=%s'
        mycursor.execute(query, (student_id,))
        subject_data = mycursor.fetchall()

        # Create a Toplevel window to display the student marks
        student_marks_window = Toplevel(root)
        student_marks_window.title('Student Marks')

        # Create a Treeview to display the data
        marks_table = ttk.Treeview(student_marks_window, columns=('Subject', 'Marks', 'Credits'))
        marks_table.heading('Subject', text='Subject')
        marks_table.heading('Marks', text='Marks')
        marks_table.heading('Credits', text='Credits')

        for subject in subject_data:
            marks_table.insert('', END, values=subject)

        marks_table.pack()

    except Exception as e:
        messagebox.showerror('Error', f'Error displaying Student Marks: {e}')
def show_student():
    query = 'select * from student'
    mycursor.execute(query)
    fetched_data = mycursor.fetchall()
    studentTable.delete(*studentTable.get_children())
    for data in fetched_data:
        studentTable.insert('', END, values=data)

# Function to submit the subject entries
def submit_subject_entry(student_id, subjects, marks, credits, window):
    try:
        for subject, mark, credit in zip(subjects, marks, credits):
            query_insert_subject = 'INSERT INTO subjects (student_id, subject, marks, credits) VALUES (%s, %s, %s, %s)'
            mycursor.execute(query_insert_subject, (student_id, subject.get(), mark.get(), credit.get()))

        con.commit()
        messagebox.showinfo('Success', 'Subjects and marks added successfully')

        # Close the add_subject_screen
        window.destroy()

    except Exception as e:
        messagebox.showerror('Error', f'Error processing subject entry: {e}')


def delete_subject_entry():
    global delete_subject_screen, student_id_entry_delete

    delete_subject_screen = Toplevel()
    delete_subject_screen.title('Delete Subject Details')
    delete_subject_screen.geometry('400x200')

    student_id_label = Label(delete_subject_screen, text='Enter Student ID:', font=('arial', 14, 'bold'))
    student_id_label.grid(row=0, column=0, padx=10, pady=10)

    student_id_entry_delete = Entry(delete_subject_screen, font=('roman', 12, 'bold'))
    student_id_entry_delete.grid(row=0, column=1, padx=10, pady=10)

    delete_button = ttk.Button(delete_subject_screen, text='Delete Subject', command=confirm_delete_subject)
    delete_button.grid(row=1, columnspan=2, pady=15)


def confirm_delete_subject():
    student_id = student_id_entry_delete.get()

    if not student_id:
        messagebox.showwarning('Warning', 'Please enter Student ID.')
        return

    result = messagebox.askyesno('Confirm', f'Do you want to delete subject details for Student ID: {student_id}?')

    if result:
        # Write the code to delete subject details for the given student_id
        try:
            query_delete_subjects = 'DELETE FROM subjects WHERE student_id=%s'
            mycursor.execute(query_delete_subjects, (student_id,))
            con.commit()

            messagebox.showinfo('Success', f'Subject details for Student ID {student_id} deleted successfully')

            # Close the delete_subject_screen
            delete_subject_screen.destroy()

        except Exception as e:
            messagebox.showerror('Error', f'Error deleting subject details: {e}', parent=delete_subject_screen)

    else:
        # User chose not to delete, close the delete_subject_screen
        delete_subject_screen.destroy()


# Function to add subject and marks entry
def add_subject_entry():
    add_subject_screen = Toplevel()
    add_subject_screen.title('Add Subjects and Marks')
    add_subject_screen.geometry('800x800')

    # Student ID Label and Entry at the top
    Label(add_subject_screen, text='Enter Student ID:', font=('arial', 14, 'bold')).grid(row=0, column=0, padx=10, pady=10)
    student_id_entry = Entry(add_subject_screen, font=('roman', 12, 'bold'))
    student_id_entry.grid(row=0, column=1, padx=10, pady=10)

    # Subjects and Marks Label below
    Label(add_subject_screen, text='Enter Subjects, Marks, and Credits:', font=('arial', 14, 'bold')).grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    # Frame to hold subject, marks, and credits entries
    entry_frame = Frame(add_subject_screen)
    entry_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    # Create lists to store Entry widgets
    subject_entries = []
    marks_entries = []
    credits_entries = []

    # Function to dynamically add subject, marks, and credits fields
    def add_entry():
        # Subject label and entry
        subject_label = Label(entry_frame, text=f"Subject {len(subject_entries) + 1}:", font=('arial', 12, 'bold'))
        subject_label.grid(row=len(subject_entries), column=0, padx=5, pady=5)
        subject_entry = Entry(entry_frame, font=('roman', 12, 'bold'))
        subject_entry.grid(row=len(subject_entries),column=1, padx=5, pady=5)
        subject_entries.append(subject_entry)

        # Marks label and entry
        marks_label = Label(entry_frame, text="Marks:", font=('arial', 12, 'bold'))
        marks_label.grid(row=len(subject_entries)-1, column=2, padx=5, pady=5)
        marks_entry = Entry(entry_frame, font=('roman', 12, 'bold'))
        marks_entry.grid(row=len(subject_entries)-1, column=3, padx=5, pady=5)
        marks_entries.append(marks_entry)

        # Credits label and entry
        credits_label = Label(entry_frame, text="Credits:", font=('arial', 12, 'bold'))
        credits_label.grid(row=len(subject_entries)-1, column=4, padx=5, pady=5)
        credits_entry = Entry(entry_frame, font=('roman', 12, 'bold'))
        credits_entry.grid(row=len(subject_entries)-1, column=5, padx=5, pady=5)
        credits_entries.append(credits_entry)

    # "Add Entry" button below the label
    add_entry_button = Button(add_subject_screen, text='Add Entry', command=add_entry)
    add_entry_button.grid(row=3, column=0, columnspan=4, pady=10)

    delete_subject_button = ttk.Button(add_subject_screen, text='Delete Subject Details', command=delete_subject_entry)
    delete_subject_button.grid(row=4, column=1, pady=10)

    # "Submit" button below the entry fields
    submit_button = Button(add_subject_screen, text='Submit', command=lambda: submit_subject_entry(student_id_entry.get(), subject_entries, marks_entries, credits_entries, add_subject_screen))
    submit_button.grid(row=3, column=1, columnspan=4, pady=10)

def delete_student():
    try:
        indexing = studentTable.focus()
        content = studentTable.item(indexing)
        content_id = content['values'][0]

        # Delete associated records from the grades table first
        query_delete_grades = 'DELETE FROM grades WHERE student_id=%s'
        mycursor.execute(query_delete_grades, content_id)
        con.commit()

        # Now delete the student from the student table
        query_delete_student = 'DELETE FROM student WHERE id=%s'
        mycursor.execute(query_delete_student, content_id)
        con.commit()

        messagebox.showinfo('Deleted', f'Id {content_id} deleted successfully')
        show_student()

    except Exception as e:
        messagebox.showerror('Error', f'Error during deletion: {e}')


def add_data():
    if idEntry.get() == '' or nameEntry.get() == '' or phoneEntry.get() == '' or emailEntry.get() == '' or addressEntry.get() == '' or genderEntry.get() == '' or DOBEntry.get() == '':
        messagebox.showerror('Error', 'All Fields are required', parent=screen)
    else:
        try:
            # Check if ID already exists
            query_check_id = 'SELECT * FROM student WHERE id=%s'
            mycursor.execute(query_check_id, (idEntry.get(),))
            existing_student = mycursor.fetchone()

            if existing_student:
                messagebox.showerror('Error', 'Student with this ID already exists', parent=screen)
            else:
                # Insert the new student
                query_insert_student = 'INSERT INTO student (id, name, mobile, email, address, gender, DOB, time, added_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                mycursor.execute(query_insert_student, (
                    idEntry.get(), nameEntry.get(), phoneEntry.get(), emailEntry.get(), addressEntry.get(),
                    genderEntry.get(), DOBEntry.get(), currenttime, date))
                con.commit()

                # Calculate CGPA for the new student
                new_cgpa = calculate_cgpa(idEntry.get())

                # Insert the CGPA and grade into the grades table
                query_insert_grades = 'INSERT INTO grades (student_id, cgpa, grade) VALUES (%s, %s, %s)'
                mycursor.execute(query_insert_grades, (idEntry.get(), new_cgpa, calculate_grade(new_cgpa)))
                con.commit()

                result = messagebox.askyesno('Confirm', 'Data added successfully, Do you want to clean the form?', parent=screen)
                if result:
                    # Clear the form
                    idEntry.delete(0, END)
                    nameEntry.delete(0, END)
                    phoneEntry.delete(0, END)
                    emailEntry.delete(0, END)
                    addressEntry.delete(0, END)
                    genderEntry.delete(0, END)
                    DOBEntry.delete(0, END)
                else:
                    pass

                # Refresh the student table
                show_student()

        except Exception as e:
            print(e)
            messagebox.showerror('Error', f'An error occurred during insertion: {e}', parent=screen)

        query = 'select * from student'
        mycursor.execute(query)
        fetched_data = mycursor.fetchall()

        studentTable.delete(*studentTable.get_children())
        for data in fetched_data:
            studentTable.insert('', END, values=data)

def connect_database():
    def connect():
        global mycursor,con
        try:
            con = pymysql.connect(host='localhost', user='root', password='2002')
            mycursor = con.cursor()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to connect to the database server: {e}', parent=connectwindow)
            return

        try:
            # Check if the database exists
            query_check_db = "SHOW DATABASES LIKE 'Student_Grading_System'"
            mycursor.execute(query_check_db)
            result = mycursor.fetchone()

            if not result:
                # Create the Student_Grading_System database
                query_create_db = 'CREATE DATABASE Student_Grading_System'
                mycursor.execute(query_create_db)
                messagebox.showinfo('Success', 'Database created successfully')

            # Use the Student_Grading_System database
            query_use_db = 'USE Student_Grading_System'
            mycursor.execute(query_use_db)

            # Create the student table
            query_create_student_table = '''
                CREATE TABLE IF NOT EXISTS student (
                    id INT NOT NULL PRIMARY KEY,
                    name VARCHAR(30),
                    mobile VARCHAR(10),
                    email VARCHAR(20),
                    address VARCHAR(100),
                    gender VARCHAR(20),
                    DOB VARCHAR(50),
                    time VARCHAR(50)
                )
            '''
            mycursor.execute(query_create_student_table)
            # Create the cgpa table
            query_create_cgpa_table = '''
                            CREATE TABLE IF NOT EXISTS cgpa (
                                student_id INT PRIMARY KEY,
                                cgpa FLOAT,
                                FOREIGN KEY (student_id) REFERENCES student(id)
                            )
                        '''
            mycursor.execute(query_create_cgpa_table)

            # Create the subjects table
            query_create_subjects_table = '''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    subject VARCHAR(50),
                    marks INT,
                    credits INT,
                    FOREIGN KEY (student_id) REFERENCES student(id)
                )
            '''
            mycursor.execute(query_create_subjects_table)

            con.commit()
            query_create_grades_table = '''
                       CREATE TABLE IF NOT EXISTS grades (
                           grade_id INT AUTO_INCREMENT PRIMARY KEY,
                           student_id INT,
                           cgpa DECIMAL(4, 2),
                           grade VARCHAR(10),
                           FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
                       )
                   '''
            mycursor.execute(query_create_grades_table)

            con.commit()

        except Exception as e:
            messagebox.showerror('Error', f'An error occurred during table creation: {e}')


        except Exception as e:
            messagebox.showerror('Error', f'An error occurred during table creation: {e}')
            return

        messagebox.showinfo('Success', 'Database connection is successful', parent=connectwindow)
        connectwindow.destroy()
        addstudentButton.config(state=NORMAL)
        addsubjectButton.config(state=NORMAL)
        updatestudentButton.config(state=NORMAL)
        deletestudentButton.config(state=NORMAL)
        showstudentButton.config(state=NORMAL)
        exportstudentButton.config(state=NORMAL)
        showstudentmarkButton.config(state=NORMAL)
        show_grades_button.config(state=NORMAL)

    connectwindow = Toplevel()
    connectwindow.geometry('470x250+730+250')
    connectwindow.title('Database Connection')
    connectwindow.resizable(0, 0)

    hostnameLabel = Label(connectwindow, text='Host Name', font=('arial', 20, 'bold'))
    hostnameLabel.grid(row=0, column=0, padx=20)

    hostEntry = Entry(connectwindow, font=('roman', 15, 'bold'), bd=2)
    hostEntry.grid(row=0, column=1, padx=40, pady=20)

    usernameLabel = Label(connectwindow, text='User Name', font=('arial', 20, 'bold'))
    usernameLabel.grid(row=1, column=0, padx=20)

    usernameEntry = Entry(connectwindow, font=('roman', 15, 'bold'), bd=2)
    usernameEntry.grid(row=1, column=1, padx=40, pady=20)

    passwordEntryLabel = Label(connectwindow, text='Password', font=('arial', 20, 'bold'))
    passwordEntryLabel.grid(row=2, column=0, padx=20)

    passwordEntry = Entry(connectwindow, font=('roman', 15, 'bold'), bd=2)
    passwordEntry.grid(row=2, column=1, padx=40, pady=20)

    ConnectButton = ttk.Button(connectwindow, text='CONNECT', command=connect)
    ConnectButton.grid(row=3, columnspan=2)


count = 0
text = ''


def slider():
    global text, count
    if count == len(s):
        count = 0
        text = ''
    text = text + s[count]
    sliderLabel.config(text=text)
    count += 1
    root.after(500, slider)
def clock():
    global date, currenttime
    date = time.strftime('%d/%m/%Y')
    currenttime = time.strftime('%H:%M:%S')
    datetimeLabel.config(text=f'    Date: {date}\nTime:{currenttime}')
    datetimeLabel.after(100, clock)

root = ttkthemes.ThemedTk()
root.get_themes()
root.set_theme('radiance')

root.attributes('-fullscreen', True)
root.geometry('1174x688+0+0')
root.resizable (0,0)
root.title('Student Grading system')

datetimeLabel = Label(root, font=('times new roman', 17, 'bold'))
datetimeLabel.place(x=5, y=5)
clock()

s = 'Student Grading System'
sliderLabel = Label(root, font=('arial', 25, 'italic bold'), width=25)
sliderLabel.place(x=200, y=0)
slider()

connectButton = Button(root, text='Connect database', command=connect_database)
connectButton.place(x=900, y=0)

leftframe = Frame(root)
leftframe.place(x=50, y=80, width=300, height=600)

logo_image = PhotoImage(file='1st.png')
logo_Label = Label(leftframe, image=logo_image)
logo_Label.grid(row=0, column=0)

addstudentButton = Button(leftframe, text='Add Student', width=25, state=DISABLED,
                          command=lambda: toplevel_data('Add Student', 'Add Student', add_data))
addstudentButton.grid(row=1, column=0, pady=10)

addsubjectButton = Button(leftframe, text='Add Subject', width=25, state=DISABLED,command=add_subject_entry)
addsubjectButton.grid(row=2, column=0, pady=10)

deletestudentButton = Button(leftframe, text='Delete Student', width=25, state=DISABLED, command=delete_student)
deletestudentButton.grid(row=3, column=0, pady=10)

updatestudentButton = Button(leftframe, text='Update Student', width=25, state=DISABLED,
                             command=lambda: toplevel_data('Update Student', 'Update', update_data))
updatestudentButton.grid(row=4, column=0, pady=10)

showstudentButton = Button(leftframe, text='Show Student', width=25, state=DISABLED, command=show_student)
showstudentButton.grid(row=5, column=0, pady=10)

show_grades_button = Button(leftframe, text='Students Grades', width=25,state=DISABLED, command=show_student_grades)
show_grades_button.grid(row=6, column=0, pady=10)

exportstudentButton = Button(leftframe, text='Export Student', width=25, state=DISABLED, command=export_data)
exportstudentButton.grid(row=7, column=0, pady=10)

showstudentmarkButton = Button(leftframe, text='student marks', width=25, state=DISABLED, command=show_student_marks)
showstudentmarkButton.grid(row=8, column=0, pady=10)

exitButton = Button(leftframe, text='Exit', width=25, command=iexit)
exitButton.grid(row=9, column=0, pady=10)

rightframe = Frame(root)
rightframe.place(x=350, y=80, width=820, height=600)

scrollBarx = Scrollbar(rightframe, orient=HORIZONTAL)
scrollBary = Scrollbar(rightframe, orient=VERTICAL)

scrollBarx = Scrollbar(rightframe, orient=HORIZONTAL)
scrollBary = Scrollbar(rightframe, orient=VERTICAL)

studentTable = Treeview(rightframe, columns=('Id', 'Name', 'Mobile', 'Email', 'Address', 'Gender', 'D.O.B', 'Added Date', 'Added Time'),
                        xscrollcommand=scrollBarx.set, yscrollcommand=scrollBary.set)

scrollBarx.config(command=studentTable.xview)
scrollBary.config(command=studentTable.yview)

# Correct placement of the scrollbars
scrollBarx.pack(side=BOTTOM, fill=X)
scrollBary.pack(side=RIGHT, fill=Y)

studentTable.pack(fill=BOTH, expand=1)

studentTable.heading('Id', text='Id')
studentTable.heading('Name', text='Name')
studentTable.heading('Mobile', text='Mobile')
studentTable.heading('Email', text='Email')
studentTable.heading('Address', text='Address')
studentTable.heading('Gender', text='Gender')
studentTable.heading('D.O.B', text='D.O.B')
studentTable.heading('Added Date', text='Added Date')
studentTable.heading('Added Time', text='Added Time')

studentTable.column('Id', width=50, anchor=CENTER)
studentTable.column('Name', width=300, anchor=CENTER)
studentTable.column('Mobile', width=300, anchor=CENTER)
studentTable.column('Email', width=200, anchor=CENTER)
studentTable.column('Address', width=300, anchor=CENTER)
studentTable.column('Gender', width=100, anchor=CENTER)
studentTable.column('D.O.B', width=100, anchor=CENTER)
studentTable.column('Added Date', width=200, anchor=CENTER)
studentTable.column('Added Time', width=200, anchor=CENTER)

style = ttk.Style()

style.configure('Treeview', rowheight=40, font=('arial', 12, 'bold'), background='white', fieldbackground='white')
style.configure('Treeview.Heading', font=('arial', 14, 'bold'), foreground='red')

studentTable.config(show='headings')

root.mainloop()
