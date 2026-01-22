import dash
import dash_auth
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import callback_context, dash_table, html, dcc, Dash

import plotly.express as px
import plotly.graph_objects as go

import re
import math
import numpy as np
import pandas as pd

from datetime import date, datetime
from itertools import product

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3
from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select

import warnings
import configparser
import os

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

VIDEO_DIR = ROOT_DIR / "dataset" / "video_"

from layout.layout import create_layout

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    assets_folder=str(VIDEO_DIR),   # ✅ THÊM DÒNG NÀY
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1.0"
    }],
)


import callbacks.overview
import callbacks.xg_analysis
import callbacks.tracking
import callbacks.animation

server = app.server

app.layout = create_layout()

if __name__ == "__main__":
    app.run(debug=True)


