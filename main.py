from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import sqlite3
from datetime import datetime
import os

# SQLite DB path
DB_PATH = r"D:/claude_test/my-first-mcp-server/employees.db"
print(f"[DEBUG] Using DB at: {DB_PATH}")

# Connect to the database
def get_db_connection():
    return sqlite3.connect(DB_PATH)

# Initialize MCP server
mcp = FastMCP("LeaveManager")

# ----------------- EXISTING TOOLS ------------------

@mcp.tool()
def get_leave_balance(identifier: str) -> str:
    """Check how many leave days are left for the employee using employee_id or name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, leave_balance FROM employees WHERE employee_id = ?", (identifier,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("SELECT employee_id, leave_balance FROM employees WHERE LOWER(name) = LOWER(?)", (identifier,))
        row = cursor.fetchone()
    conn.close()
    if row:
        return f"Employee {row[0]} has {row[1]} leave days remaining."
    return "Employee not found. Please check the ID or name."

@mcp.tool()
def apply_leave(identifier: str, leave_dates: List[str]) -> str:
    """
    Apply leave for specific dates (e.g., ["2025-04-17", "2025-05-01"])
    Accepts either employee ID or name as identifier.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, leave_balance, leave_history FROM employees WHERE employee_id = ?", (identifier,))
    row = cursor.fetchone()
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

@mcp.tool()
def get_leave_history(identifier: str) -> str:
    """Get leave history for the employee using employee ID or name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, leave_history FROM employees WHERE employee_id = ?", (identifier,))
    row = cursor.fetchone()
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

@mcp.tool()
def get_employee_info(employee_id: Optional[str] = None, name: Optional[str] = None) -> str:
    """Retrieve comprehensive information about an employee by ID or Name."""
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

# ----------------- NEW TOOLS ------------------

@mcp.tool()
def get_employee_projects(identifier: str) -> str:
    """List all projects assigned to an employee by employee_id or name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ? OR LOWER(name) = LOWER(?)", (identifier, identifier))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Employee not found. Please check the ID or name."
    employee_id = row[0]
    cursor.execute("SELECT project_id, project_name, start_date, end_date, role, status FROM projects WHERE employee_id = ?", (employee_id,))
    projects = cursor.fetchall()
    conn.close()
    if not projects:
        return f"No projects found for employee {employee_id}."
    lines = [f"Project ID: {p[0]}, Name: {p[1]}, Role: {p[4]}, Status: {p[5]}, Start: {p[2]}, End: {p[3]}" for p in projects]
    return "\n".join(lines)

@mcp.tool()
def get_project_employees(project_identifier: str) -> str:
    """List all employees assigned to a project by project_id or project_name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_id FROM projects WHERE project_id = ? OR project_name = ?", (project_identifier, project_identifier))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Project not found. Please check the ID or name."
    project_id = row[0]
    cursor.execute("""
        SELECT e.employee_id, e.name, p.role
        FROM employees e
        JOIN projects p ON e.employee_id = p.employee_id
        WHERE p.project_id = ?
    """, (project_id,))
    employees = cursor.fetchall()
    conn.close()
    if not employees:
        return f"No employees found for project {project_id}."
    lines = [f"Employee ID: {e[0]}, Name: {e[1]}, Role: {e[2]}" for e in employees]
    return "\n".join(lines)

@mcp.tool()
def get_employees_on_leave(date: str) -> str:
    """List all employees who are on leave on a given date (YYYY-MM-DD)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, name, leave_history FROM employees")
    rows = cursor.fetchall()
    conn.close()
    on_leave = []
    for emp_id, name, history in rows:
        if history and date in history.split(','):
            on_leave.append(f"{emp_id} ({name})")
    if not on_leave:
        return f"No employees are on leave on {date}."
    return f"Employees on leave on {date}: " + ", ".join(on_leave)

@mcp.tool()
def get_project_history_for_employee(identifier: str) -> str:
    """Show all projects (with dates and roles) an employee has been assigned to."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ? OR LOWER(name) = LOWER(?)", (identifier, identifier))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Employee not found. Please check the ID or name."
    employee_id = row[0]
    cursor.execute("SELECT project_name, start_date, end_date, role, status FROM projects WHERE employee_id = ?", (employee_id,))
    projects = cursor.fetchall()
    conn.close()
    if not projects:
        return f"No project history found for employee {employee_id}."
    lines = [f"{p[0]}: {p[3]} ({p[1]} to {p[2]}, Status: {p[4]})" for p in projects]
    return "\n".join(lines)

# ----------------- RESOURCES ------------------

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

# ----------------- RUN SERVER ------------------

if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    mcp.run()
