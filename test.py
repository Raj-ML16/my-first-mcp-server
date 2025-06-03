from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import sqlite3
from datetime import datetime
import os

# SQLite DB path
DB_PATH = r"D:/claude_test/my-first-mcp-server/employees.db"
print(f"[DEBUG] Using DB at: {DB_PATH}")

# DB_PATH = os.path.abspath("employees.db")
print(f"[OK] Using DB at: {DB_PATH}")

# Connect to the database
def get_db_connection():
    return sqlite3.connect(DB_PATH)

# Initialize MCP server
mcp = FastMCP("LeaveManager")

# Tool: Get Leave Balance
@mcp.tool()
def get_leave_balance(identifier: str) -> str:
    """Check how many leave days are left for the employee using employee_id or name"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Try to find by employee_id first
    cursor.execute("SELECT employee_id, leave_balance FROM employees WHERE employee_id = ?", (identifier,))
    row = cursor.fetchone()

    # If not found, try finding by name (case-insensitive)
    if not row:
        cursor.execute("SELECT employee_id, leave_balance FROM employees WHERE LOWER(name) = LOWER(?)", (identifier,))
        row = cursor.fetchone()

    conn.close()

    if row:
        return f"Employee {row[0]} has {row[1]} leave days remaining."
    return "Employee not found. Please check the ID or name."

# Tool: Apply Leave
@mcp.tool()
def apply_leave(identifier: str, leave_dates: List[str]) -> str:
    """
    Apply leave for specific dates (e.g., ["2025-04-17", "2025-05-01"])
    Accepts either employee ID or name as identifier.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Try finding by employee_id
    cursor.execute("SELECT employee_id, leave_balance, leave_history FROM employees WHERE employee_id = ?", (identifier,))
    row = cursor.fetchone()

    # If not found, try finding by name (case-insensitive)
    if not row:
        cursor.execute("SELECT employee_id, leave_balance, leave_history FROM employees WHERE LOWER(name) = LOWER(?)", (identifier,))
        row = cursor.fetchone()

    if not row:
        conn.close()
        return "Employee not found. Please check the ID or name."

    employee_id, balance, history = row
    requested_days = len(leave_dates)

    if balance < requested_days:
        conn.close()
        return f"Insufficient leave balance. You requested {requested_days} day(s) but have only {balance}."

    # Update leave balance and history
    new_balance = balance - requested_days
    new_history = history.split(',') if history else []
    new_history.extend(leave_dates)
    updated_history = ','.join(new_history)

    cursor.execute("""
        UPDATE employees SET leave_balance = ?, leave_history = ? WHERE employee_id = ?
    """, (new_balance, updated_history, employee_id))

    conn.commit()
    conn.close()

    return f"Leave applied for {requested_days} day(s) for employee {employee_id}. Remaining balance: {new_balance}."

# Tool: Get Leave History
@mcp.tool()
def get_leave_history(identifier: str) -> str:
    """Get leave history for the employee using employee ID or name"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Try finding by employee_id
    cursor.execute("SELECT employee_id, leave_history FROM employees WHERE employee_id = ?", (identifier,))
    row = cursor.fetchone()

    # If not found, try finding by name (case-insensitive)
    if not row:
        cursor.execute("SELECT employee_id, leave_history FROM employees WHERE LOWER(name) = LOWER(?)", (identifier,))
        row = cursor.fetchone()

    conn.close()

    if not row:
        return "Employee not found. Please check the ID or name."

    employee_id, history = row
    if not history:
        return f"Leave history for {employee_id}: No leaves taken."
    return f"Leave history for {employee_id}: {history}"

# Tool: Get Full Employee Info (by ID or name)
@mcp.tool()
def get_employee_info(employee_id: Optional[str] = None, name: Optional[str] = None) -> str:
    """
    Retrieve comprehensive information about an employee by ID or Name.
    """
    if not employee_id and not name:
        return "Please provide either employee_id or name to retrieve information."

    conn = get_db_connection()
    cursor = conn.cursor()

    if employee_id:
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    elif name:
        cursor.execute("SELECT * FROM employees WHERE name LIKE ?", (f"%{name}%",))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return "Employee not found."

    columns = [description[0] for description in cursor.description]
    conn.close()

    employee_data = dict(zip(columns, row))
    info_lines = [f"{key.replace('_', ' ').title()}: {value}" for key, value in employee_data.items()]
    return "\n".join(info_lines)

# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

# Run the server
if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    mcp.run()
