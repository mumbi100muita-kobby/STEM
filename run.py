"""Convenience launcher: python run.py

Prefer `flask --app wsgi:app run` once the virtual environment is active.
"""

from stem import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
