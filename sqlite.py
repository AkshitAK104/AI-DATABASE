import sqlite3
import os

def create_student_database():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'student.db')
    
    print(f"Creating database at: {db_path}")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        grade TEXT,
        email TEXT,
        major TEXT,
        gpa REAL
    )
    ''')

    # Insert sample student data
    students_data = [
        (1, 'John Doe', 20, 'A', 'john.doe@university.edu', 'Computer Science', 3.8),
        (2, 'Jane Smith', 19, 'B+', 'jane.smith@university.edu', 'Mathematics', 3.6),
        (3, 'Mike Johnson', 21, 'A-', 'mike.johnson@university.edu', 'Physics', 3.7),
        (4, 'Sarah Wilson', 18, 'A+', 'sarah.wilson@university.edu', 'Chemistry', 3.9),
        (5, 'David Brown', 22, 'B', 'david.brown@university.edu', 'Biology', 3.4),
        (6, 'Emily Davis', 20, 'A', 'emily.davis@university.edu', 'Engineering', 3.8),
        (7, 'Chris Lee', 19, 'B+', 'chris.lee@university.edu', 'Computer Science', 3.5),
        (8, 'Anna Taylor', 21, 'A-', 'anna.taylor@university.edu', 'Mathematics', 3.6),
        (9, 'Tom Anderson', 20, 'B', 'tom.anderson@university.edu', 'Physics', 3.3),
        (10, 'Lisa Garcia', 18, 'A+', 'lisa.garcia@university.edu', 'Chemistry', 4.0)
    ]

    cursor.executemany('INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?,?)', students_data)

    # Create courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        course_id INTEGER PRIMARY KEY,
        course_name TEXT NOT NULL,
        credits INTEGER,
        instructor TEXT,
        department TEXT,
        semester TEXT
    )
    ''')

    courses_data = [
        (1, 'Computer Science 101', 3, 'Dr. Smith', 'Computer Science', 'Fall 2024'),
        (2, 'Data Structures', 4, 'Prof. Johnson', 'Computer Science', 'Spring 2024'),
        (3, 'Calculus I', 4, 'Dr. Wilson', 'Mathematics', 'Fall 2024'),
        (4, 'Physics 101', 3, 'Prof. Brown', 'Physics', 'Fall 2024'),
        (5, 'Chemistry 101', 3, 'Dr. Davis', 'Chemistry', 'Spring 2024'),
        (6, 'Linear Algebra', 3, 'Prof. Lee', 'Mathematics', 'Spring 2024'),
        (7, 'Biology 101', 3, 'Dr. Taylor', 'Biology', 'Fall 2024'),
        (8, 'Engineering Design', 4, 'Prof. Anderson', 'Engineering', 'Fall 2024')
    ]

    cursor.executemany('INSERT OR REPLACE INTO courses VALUES (?,?,?,?,?,?)', courses_data)

    # Create enrollments table (student-course relationships)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        enrollment_date TEXT,
        final_grade TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (course_id) REFERENCES courses (course_id)
    )
    ''')

    enrollments_data = [
        (1, 1, 1, '2024-08-15', 'A'),
        (2, 1, 2, '2024-01-15', 'A-'),
        (3, 2, 3, '2024-08-15', 'B+'),
        (4, 3, 1, '2024-08-15', 'A-'),
        (5, 4, 5, '2024-01-15', 'A+'),
        (6, 5, 7, '2024-08-15', 'B'),
        (7, 2, 6, '2024-01-15', 'B+'),
        (8, 3, 4, '2024-08-15', 'A-'),
        (9, 6, 8, '2024-08-15', 'A'),
        (10, 7, 1, '2024-08-15', 'B+')
    ]

    cursor.executemany('INSERT OR REPLACE INTO enrollments VALUES (?,?,?,?,?)', enrollments_data)

    # Commit changes and close
    conn.commit()
    conn.close()

    print("✅ Sample database 'student.db' created successfully!")
    print(f"📁 Location: {db_path}")
    print("\n📊 Database contains:")
    print("   • 10 students with details (name, age, grade, email, major, GPA)")
    print("   • 8 courses with instructor and department info")
    print("   • 10 enrollment records linking students to courses")
    print("\n🚀 You can now run your Streamlit app!")

if __name__ == "__main__":
    create_student_database()