import dash
import dash_bootstrap_components as dbc
import os
from flask import Flask, send_from_directory

external_stylesheets = ['templates/bWLwgP.css', dbc.themes.BOOTSTRAP]

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally=True
app.config['suppress_callback_exceptions'] = True


