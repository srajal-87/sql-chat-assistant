import sqlite3
import pandas as pd
from pathlib import Path

def create_sample_database():
    # Create database file in the same directory as the script
    db_path = Path(__file__).parent / "student.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        age INTEGER,
        grade_level INTEGER,
        enrollment_date DATE
    )
    ''')

    # Create Courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        course_id INTEGER PRIMARY KEY,
        course_name TEXT NOT NULL,
        department TEXT,
        credits INTEGER,
        professor TEXT
    )
    ''')

    # Create Enrollments table (junction table)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        semester TEXT,
        grade REAL,
        FOREIGN KEY (student_id) REFERENCES students (student_id),
        FOREIGN KEY (course_id) REFERENCES courses (course_id)
    )
    ''')

    # Sample student data
    students_data = [
        (1, 'John', 'Doe', 18, 12, '2023-09-01'),
        (2, 'Jane', 'Smith', 17, 11, '2023-09-01'),
        (3, 'Michael', 'Johnson', 16, 10, '2023-09-01'),
        (4, 'Emily', 'Brown', 18, 12, '2023-09-01'),
        (5, 'William', 'Davis', 17, 11, '2023-09-01')
    ]

    # Sample courses data
    courses_data = [
        (1, 'Introduction to Biology', 'Science', 4, 'Dr. Smith'),
        (2, 'World History', 'History', 3, 'Prof. Johnson'),
        (3, 'Algebra II', 'Mathematics', 4, 'Dr. Brown'),
        (4, 'English Literature', 'English', 3, 'Prof. Davis'),
        (5, 'Chemistry', 'Science', 4, 'Dr. Wilson')
    ]

    # Sample enrollments data with grades
    enrollments_data = [
        (1, 1, 1, 'Fall 2023', 3.8),
        (2, 1, 3, 'Fall 2023', 3.5),
        (3, 2, 2, 'Fall 2023', 4.0),
        (4, 2, 4, 'Fall 2023', 3.7),
        (5, 3, 1, 'Fall 2023', 3.9),
        (6, 3, 5, 'Fall 2023', 3.6),
        (7, 4, 6, 'Fall 2023', 3.8)
    ]

    # Insert sample data
    cursor.executemany('INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?)', students_data)
    cursor.executemany('INSERT OR REPLACE INTO courses VALUES (?,?,?,?,?)', courses_data)
    cursor.executemany('INSERT OR REPLACE INTO enrollments VALUES (?,?,?,?,?)', enrollments_data)

    # Create some views for easier querying
    # Student Performance View
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS student_performance AS
    SELECT 
        s.student_id,
        s.first_name || ' ' || s.last_name as student_name,
        c.course_name,
        e.grade,
        e.semester
    FROM students s
    JOIN enrollments e ON s.student_id = e.student_id
    JOIN courses c ON e.course_id = c.course_id
    ''')

    # Department Statistics View
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS department_stats AS
    SELECT 
        c.department,
        COUNT(DISTINCT e.student_id) as total_students,
        AVG(e.grade) as average_grade
    FROM courses c
    JOIN enrollments e ON c.course_id = e.course_id
    GROUP BY c.department
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Database created successfully at: {db_path}")
    print("\nSample queries you can try:")
    print("1. Show all students: SELECT * FROM students")
    print("2. Show course enrollment counts: SELECT course_name, COUNT(*) as enrollment_count FROM courses JOIN enrollments ON courses.course_id = enrollments.course_id GROUP BY course_name")
    print("3. Show student performance: SELECT * FROM student_performance")
    print("4. Show department statistics: SELECT * FROM department_stats")

if __name__ == "__main__":
    try:
        create_sample_database()
    except Exception as e:
        print(f"Error creating database: {str(e)}")
