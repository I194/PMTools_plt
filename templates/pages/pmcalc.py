# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_daq as daq
import dash_table
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np

import os, time, glob, cairosvg
import plotly.io
from plotly.io import write_image
import urllib
from urllib.parse import quote as urlquote

plotly.io.orca.config.executable = 'Orca/orca_app/orca.exe'
plotly.io.orca.config.save()
from flask import Flask, send_from_directory
from pathlib import Path

from templates.app import app, server
from .functions.Statistics import *
from .functions.SupFunc import *

layout = [
    dbc.Container(
        children=[
            html.H5("Pole from direction", id="annot-polar", className="text-muted"),
            dbc.Row([
                dbc.Col(
                    # Input block
                    dbc.Container(
                        className="w-100 text-center",
                        children=[
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Site Latitude N"),
                                    dbc.Input(placeholder="angle", type="number", id="poledir-lat"),
                                ],
                                width=3),
                                dbc.Col([
                                    dbc.Label("Site Longitude E(-W)"),
                                    dbc.Input(placeholder="angle", type="number", id="poledir-lon"),
                                ],
                                width=3),
                                dbc.Col([
                                    dbc.Label("Declination"),
                                    dbc.Input(placeholder="angle", type="number", id="poledir-dec"),
                                ],
                                width=2),
                                dbc.Col([
                                    dbc.Label("Inclination"),
                                    dbc.Input(placeholder="angle", type="number", id="poledir-inc"),
                                ],
                                width=2),
                                dbc.Col([
                                    dbc.Label("a95"),
                                    dbc.Input(placeholder="angle", type="number", id="poledir-a95"),
                                ],
                                width=2)
                            ])
                        ],
                        fluid=True,
                    ),
                    width=6
                ),
                # dbc.Col(
                #     # Compute block
                #     dbc.Container([
                #         dbc.Label("_"),
                #         dbc.Button(
                #             "Compute",
                #             color="primary",
                #         )
                #     ],)
                # ),
                dbc.Col(
                    # Output block
                    dbc.Container(
                        children=[
                            html.Div(
                                id='poledir-result'
                            ),
                        ],
                        fluid=True,
                    ),
                    width=6
                )
            ],
            className="text-center"),
            # html.H5("Direction from pole", id="annot-polar", className="text-muted"),
            # dbc.Row([
            #
            #     dbc.Col(
            #         # Input block
            #         dbc.Container(
            #             className="w-100 text-center",
            #             children=[
            #                 dbc.Row(
            #
            #                 )
            #             ],
            #             fluid=True,
            #         ),
            #         width=6
            #     ),
            #     dbc.Col(
            #         # Output block
            #         dbc.Container(
            #             children=[
            #                 dbc.Row(
            #
            #                 )
            #             ],
            #             fluid=True,
            #         ),
            #         width=6
            #     )
            # ],
            # className="text-center"),
            # html.H5("Site from direction and pole", id="annot-polar", className="text-muted"),
            # dbc.Row([
            #     dbc.Col(
            #         # Input block
            #         dbc.Container(
            #             className="w-100 text-center",
            #             children=[
            #                 dbc.Row(
            #
            #                 )
            #             ],
            #             fluid=True,
            #         ),
            #         width=6
            #     ),
            #     dbc.Col(
            #         # Output block
            #         dbc.Container(
            #             children=[
            #                 dbc.Row(
            #
            #                 )
            #             ],
            #             fluid=True,
            #         ),
            #         width=6
            #     )
            # ],
            # className="text-center"),
            html.H5("Cartesian to polar", id="annot-polar", className="text-muted"),
            dbc.Row([
                dbc.Col(
                    # Input block
                    dbc.Container(
                        className="w-100 text-center",
                        children=[
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("X"),
                                    dbc.Input(placeholder="angle", type="number", id="cartdir-x"),
                                ],
                                width=4),
                                dbc.Col([
                                    dbc.Label("Y"),
                                    dbc.Input(placeholder="angle", type="number", id="cartdir-y"),
                                ],
                                width=4),
                                dbc.Col([
                                    dbc.Label("Z"),
                                    dbc.Input(placeholder="angle", type="number", id="cartdir-z"),
                                ],
                                width=4),
                            ])
                        ],
                        fluid=True,
                    ),
                    width=6
                ),
                # dbc.Col(
                #     # Compute block
                #     dbc.Container([
                #         dbc.Label("_"),
                #         dbc.Button(
                #             "Compute",
                #             color="primary",
                #         )
                #     ],)
                # ),
                dbc.Col(
                    # Output block
                    dbc.Container(
                        children=[
                            html.Div(
                                id='cartdir-result'
                            ),
                        ],
                        fluid=True,
                    ),
                    width=6
                )
            ],
            className="text-center"),
            html.H5("Polar to cartesian", id="annot-polar", className="text-muted"),
            dbc.Row([
                dbc.Col(
                    # Input block
                    dbc.Container(
                        className="w-100 text-center",
                        children=[
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Declination"),
                                    dbc.Input(placeholder="angle", type="number", id="cartdir-dec"),
                                ],
                                width=4),
                                dbc.Col([
                                    dbc.Label("Inclination"),
                                    dbc.Input(placeholder="angle", type="number", id="cartdir-inc"),
                                ],
                                width=4),
                                dbc.Col([
                                    dbc.Label("Magnetization"),
                                    dbc.Input(placeholder="angle", type="number", id="cartdir-mag"),
                                ],
                                width=4),
                            ])
                        ],
                        fluid=True,
                    ),
                    width=6
                ),
                # dbc.Col(
                #     # Compute block
                #     dbc.Container([
                #         dbc.Label("_"),
                #         dbc.Button(
                #             "Compute",
                #             color="primary",
                #         )
                #     ],)
                # ),
                dbc.Col(
                    # Output block
                    dbc.Container(
                        children=[
                            html.Div(
                                id='dircart-result'
                            ),
                        ],
                        fluid=True,
                    ),
                    width=6
                )
            ],
            className="text-center"),
        ],
        fluid=True,
        className="text-center"
        # style={"height": "100vh", "overflow":"hidden"}
    )
]

@app.callback(
    Output('poledir-result', 'children'),
    [Input('poledir-lat', 'value'),
     Input('poledir-lon', 'value'),
     Input('poledir-dec', 'value'),
     Input('poledir-inc', 'value'),
     Input('poledir-a95', 'value'),]
)
def poledir(lat, lon, dec, inc, a95):
    if lat and lon and dec and inc and a95:
        PLat, PLon, dp, dm, PaleoLat = paleo_pole(lat, lon, dec, inc, a95)
        return (
            dbc.ListGroup(
                [
                    dbc.Row([
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("PLat", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(PLat),
                            ],
                            width=3
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("PLon", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(PLon),
                            ],
                            width=3
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("dp/dm", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(str(dp)+"/"+str(dm)),
                            ],
                            width=3
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("PaleoLat", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(PaleoLat),
                            ],
                            width=3
                        )
                    ])
                ]
            )
            # html.P(
            #     "PLat: " + str(PLat) + " PLon: " + str(PLon) +
            #     " dp/dm: " + str(dp)+"/"+str(dm) + " PaleoLat: " + str(PaleoLat),
            #     className="text-center"
            # ),
        )


@app.callback(
    Output('cartdir-result', 'children'),
    [Input('cartdir-x', 'value'),
     Input('cartdir-y', 'value'),
     Input('cartdir-z', 'value'),]
)
def poledir(x, y, z):
    if x and y and z:
        dec, inc, mag = xyz_to_dir(x,y,z,"MAG")
        return (
            dbc.ListGroup(
                [
                    dbc.Row([
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("Declination", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(dec),
                            ],
                            width=4
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("Inclination", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(inc),
                            ],
                            width=4
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("Magnitude", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(mag),
                            ],
                            width=4
                        ),
                    ])
                ]
            )
        )


@app.callback(
    Output('dircart-result', 'children'),
    [Input('cartdir-dec', 'value'),
     Input('cartdir-inc', 'value'),
     Input('cartdir-mag', 'value'),]
)
def poledir(d, i, r):
    if d and i and r:
        x, y, z = dir_to_xyz(d, i, r)
        x, y, z = round(x, 1), round(y, 1), round(z, 1)
        return (
            dbc.ListGroup(
                [
                    dbc.Row([
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("X", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(x),
                            ],
                            width=4
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("Y", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(y),
                            ],
                            width=4
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroupItemText("Z", style={"margin-bottom": "-2px",}),
                                dbc.ListGroupItem(z),
                            ],
                            width=4
                        ),
                    ])
                ]
            )
        )