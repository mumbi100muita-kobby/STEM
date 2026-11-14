"""WSGI entry point for local `flask run` and later production servers."""

from stem import create_app

app = create_app()
