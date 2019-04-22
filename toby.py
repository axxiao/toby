# The Core of Toby
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from ax.tools import load_function


logger = logging.getLogger('werkzeug')
debug_flg = True if os.getenv('TOBY_DEBUG', 'True') == 'True' else False
app = Flask('Toby')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['TOBY_DB_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.logger.setLevel(logging.DEBUG if debug_flg else logging.INFO)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = SQLAlchemy(app).engine.connect()
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route("/")
def ping():
    return "<h1 style='color:blue'>Hello There! This is Toby</h1>"


@app.route("/process")
def process():
    func = load_function
    resp = func()
    return jsonify(resp)


if __name__ == "__main__":
    app.run()
