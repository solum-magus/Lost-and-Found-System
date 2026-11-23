# creates the app, connects database, and registers the routes (also the entry point for the app)

from flask import Flask

import config
from database import connection
from routes import admin_routes, auth_routes, shared_routes, user_routes


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(config) # loads the config.py file and overrides with any test_config if provided
    if test_config:
        app.config.update(test_config)

    connection.init_app(app) # creates the tables if they don't exist

    for module in (auth_routes, user_routes, admin_routes, shared_routes):
        app.register_blueprint(module.bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0")
