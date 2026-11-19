# Application settings

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Change this (or set the SECRET_KEY environment variable) before deploying.
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-before-deploying")

DATABASE = os.path.join(BASE_DIR, "database", "plv-laf.db")
