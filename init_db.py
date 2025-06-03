import sqlite3
import random
from faker import Faker

SEED = 42  # You can use any integer

random.seed(SEED)
fake = Faker()
fake.seed_instance(SEED)

departments = ["Sales", "AI/ML", "Data Engineering", "Digital Engineering", "HR", "Finance"]
certifications = ["AWS", "Azure", "GCP", "PMP", "Scrum", "None"]

def create_db():
    conn = sqlite3.connect("employees_update.db")
    cursor = conn.cursor()

    # Drop table if exists
    cursor.execute("DROP TABLE IF EXISTS employees")
    

    
    # Create table
    cursor.execute("""
        CREATE TABLE employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            gender TEXT,
            experience INTEGER,
            department TEXT,
            position TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            certifications TEXT,
            joining_date TEXT,
            salary INTEGER,
            manager TEXT,
            leave_balance INTEGER,
            leave_history TEXT,
            performance_rating REAL,
            status TEXT,
            location TEXT,
            shift TEXT
        )
    """)

    # Populate table with 50 employees
    for i in range(1, 51):
        employee_id = f"E{str(i).zfill(3)}"
        name = fake.name()
        age = random.randint(22, 60)
        gender = random.choice(["Male", "Female", "Other"])
        experience = random.randint(0, age - 21)
        department = random.choice(departments)
        position = fake.job()
        email = fake.email()
        phone = fake.phone_number()
        address = fake.address().replace("\n", ", ")
        certs = ",".join(random.sample(certifications, random.randint(1, 3)))
        joining_date = fake.date_between(start_date='-10y', end_date='today').isoformat()
        salary = random.randint(30000, 150000)
        manager = fake.name()
        leave_balance = random.randint(10, 30)
        leave_history = ""  # initially empty
        rating = round(random.uniform(2.0, 5.0), 1)
        status = random.choice(["Active", "On Leave", "Resigned"])
        location = fake.city()
        shift = random.choice(["Day", "Night", "Rotational"])

        cursor.execute("""
            INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (employee_id, name, age, gender, experience, department, position, email, phone, address,
              certs, joining_date, salary, manager, leave_balance, leave_history, rating, status, location, shift))

    # Drop projects table if exists
    cursor.execute("DROP TABLE IF EXISTS projects")

    # Create projects table
    cursor.execute("""
        CREATE TABLE projects (
            project_id TEXT PRIMARY KEY,
            project_name TEXT,
            employee_id TEXT,
            start_date TEXT,
            end_date TEXT,
            role TEXT,
            status TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
        )
    """)

    # Populate projects table with sample data
    project_names = ["AI Chatbot", "Data Lake", "HR Portal", "Sales Dashboard", "Cloud Migration"]
    project_statuses = ["Active", "Completed", "On Hold"]

    for i in range(1, 101):  # 100 project assignments
        project_id = f"P{str(i).zfill(3)}"
        project_name = random.choice(project_names)
        employee_id = f"E{str(random.randint(1, 50)).zfill(3)}"
        start_date_obj = fake.date_between(start_date='-3y', end_date='-1y')
        end_date_obj = fake.date_between(start_date=start_date_obj, end_date='today')
        start_date = start_date_obj.isoformat()
        end_date = end_date_obj.isoformat()
        role = random.choice(["Developer", "Lead", "Tester", "Manager", "Analyst"])
        status = random.choice(project_statuses)
        cursor.execute("""
            INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, project_name, employee_id, start_date, end_date, role, status))

    # Now commit all changes
    conn.commit()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("[DEBUG] Tables in DB:", cursor.fetchall())
    # Print number of records in each table
    cursor.execute("SELECT COUNT(*) FROM employees")
    num_employees = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM projects")
    num_projects = cursor.fetchone()[0]
    conn.close()
    print(f"Database 'employees_update.db' created with {num_employees} employees and {num_projects} project assignments.")

if __name__ == "__main__":
    create_db()
