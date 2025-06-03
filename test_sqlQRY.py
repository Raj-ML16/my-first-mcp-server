import sqlite3
from typing import Optional

# Simulate MCP tool decorator (you can ignore this if not using MCP directly)
def mcp_tool():
    def decorator(func):
        return func
    return decorator

# Database connection function
def get_db_connection():
    # Use in-memory DB for testing; replace with "employee.db" if needed
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Set up table and insert dummy data
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT
        )
    """)
    cursor.executemany("""
        INSERT INTO employees (employee_id, name, email, phone, address) VALUES (?, ?, ?, ?, ?)
    """, [
        ("E001", "Alice Johnson", "alice@example.com", "123-456-7890", "123 Main St"),
        ("E002", "Bob Smith", "bob@example.com", "234-567-8901", "456 Elm St"),
    ])
    conn.commit()
    return conn

# Define the update_contact_info tool
@mcp_tool()
def update_contact_info(employee_id: Optional[str] = None, name: Optional[str] = None,
                        email: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None) -> str:
    if not employee_id and not name:
        return "Please provide either employee_id or name."
    if not (email or phone or address):
        return "No fields to update."

    conn = get_db_connection()
    cursor = conn.cursor()

    # Find the employee
    if employee_id:
        cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ?", (employee_id,))
    else:
        cursor.execute("SELECT employee_id FROM employees WHERE LOWER(name) = LOWER(?)", (name,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Employee not found."

    emp_id = row[0]

    # Prepare update query
    updates = []
    values = []
    if email:
        updates.append("email = ?")
        values.append(email)
    if phone:
        updates.append("phone = ?")
        values.append(phone)
    if address:
        updates.append("address = ?")
        values.append(address)

    values.append(emp_id)
    query = f"UPDATE employees SET {', '.join(updates)} WHERE employee_id = ?"
    cursor.execute(query, tuple(values))
    conn.commit()

    # Confirm update
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (emp_id,))
    updated = cursor.fetchone()
    conn.close()

    return f"Updated contact information for employee {emp_id}: {dict(updated)}"

# ------------------------------
# Run Test Cases
# ------------------------------
print("TEST 1 - Update by name:")
print(update_contact_info(name="Allison Hill", phone="999-999-9999"))

print("\nTEST 2 - Update by employee_id:")
print(update_contact_info(employee_id="E002", email="bob.new@example.com", address="999 Maple Rd"))

print("\nTEST 3 - No fields to update:")
print(update_contact_info(name="Alice Johnson"))

print("\nTEST 4 - Invalid name:")
print(update_contact_info(name="Charlie Unknown", phone="000-000-0000"))
