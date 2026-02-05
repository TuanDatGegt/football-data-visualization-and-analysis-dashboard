# Dashboard/app.py
import dash
import dash_bootstrap_components as dbc
from dash import Dash



from datetime import date, datetime
from itertools import product

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import logout_user, current_user, LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select


import sys
from pathlib import Path

# ===============================
# PATH CONFIG
# ===============================
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# ===============================
# APP INIT
# ===============================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1.0"
    }],
)

server = app.server

# ===============================
# LAYOUT
# ===============================
from layout.layout import create_layout
app.layout = create_layout()

# ===============================
# CALLBACKS
# ===============================
import callbacks.overview
import callbacks.xg_analysis
import callbacks.tracking
import callbacks.animation

if __name__ == "__main__":
    app.run(debug=True)