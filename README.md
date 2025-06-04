1.Go to your desired project folder
2.Initialize the project using(uv init my-first-mcp-server)
3. Move into the new project folder(cd my-first-mcp-server)
4. Create and activate a virtual environment (if not already done) [python -m venv .venv  & then \.venv\Scripts\Activate.ps1]
5. Install MCP CLI inside this project using uv add "mcp[cli]"
6. pip install --upgrade typer
7. Add your main.py leave management code
8. Install your server using (uv run mcp install main.py)
Finally, Restart Claude Desktop if needed.
