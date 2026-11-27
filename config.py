# Application settings
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY", "secret-key")

DATABASE = os.path.join(BASE_DIR, "database", "plv-laf.db")
