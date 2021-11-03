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

UPLOAD_DIRECTORY = "/PM-Tools/plots"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


dff = pd.DataFrame(
    {'T or M': [], 'X': [], 'Y': [], 'Z': [], 'MAG': [],
     'Dg': [], 'Ig': [], 'Ds': [], 'Is': [], 'a95': []}
)
bing_df = pd.DataFrame(
    {"ID": [], "Steprange": [], "N": [], "Dg": [], "Ig": [],
     "a95g": [], "Ds": [], "Is": [], "a95s": []}
)
fish_df = pd.DataFrame(
    {"ID": [], "Steprange": [], "N": [], "Dg": [], "Ig": [], "Kg": [],
     "a95g": [], "Ds": [], "Is": [], "Ks": [], "a95s": []}
)

# Default charts configuration
chart_config = {
    'toImageButtonOptions': {'format': 'png'},
    'showLink': False,
    'displaylogo': False,
    'scrollZoom': True,
    'displayModeBar': False,
    # 'modeBarButtonsToRemove': [
    #     'zoom2d',
    #     'pan2d',
    #     'select2d',
    #     'lasso2d',
    #     'autoScale2d',
    #     'resetScale2d',
    #     'toggleHover',
    #     'hoverClosestCartesian',
    #     'hoverCompareCartesian',
    #     'toggleSpikelines'
    #     ],
    # 'edits': {
    #     'annotationPosition': True,
    #     'annotationText': True,
    #     'annotationTail': True
    # },
}

margin_scatter_2d = dict(b=60, l=60, t=60, r=60)
margin_scatter_polar = dict(b=30, l=30, t=30, r=30)

layout = [
    dbc.Container(
        children=[
            # Top content
            dbc.Container(
                children=[
                    dbc.Row(
                        children=[
                            # Left block, cols=4
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        children=[
                                            # Top content of left block, upload and 3 as 1 button
                                            dbc.CardHeader(
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(
                                                                children=[
                                                                    # Upload form
                                                                    dcc.Upload(
                                                                        id='upload-data',
                                                                        className="upload-container",
                                                                        accept=".pmd, .pmm, .dir, .csv",
                                                                        children=[
                                                                            html.Div(
                                                                                children=[
                                                                                    html.A('Select'),
                                                                                    ' or drop file'
                                                                                ]
                                                                            ),
                                                                        ],
                                                                        multiple=False
                                                                    ),
                                                                ],
                                                                width=8
                                                            ),
                                                            dbc.Col(
                                                                children=[
                                                                    # 3 charts as 1 in modal
                                                                    dbc.Button("3 in 1", id="open-3-in-1", block=True),
                                                                    dbc.Modal(
                                                                        children=[
                                                                            dbc.ModalHeader(
                                                                                children=[
                                                                                    dcc.Loading(
                                                                                        dbc.Row(
                                                                                            children=[
                                                                                                dbc.Col(
                                                                                                    children=[
                                                                                                        dbc.ButtonGroup(
                                                                                                            children=[
                                                                                                                html.A(
                                                                                                                    id="svg-allCharts",
                                                                                                                    className="w-100",
                                                                                                                    children=[
                                                                                                                        dbc.Button(
                                                                                                                            "Download .SVG",
                                                                                                                            color="link",
                                                                                                                            block=True,
                                                                                                                        )
                                                                                                                    ]
                                                                                                                ),
                                                                                                                html.A(
                                                                                                                    id="pdf-allCharts",
                                                                                                                    className="w-100",
                                                                                                                    children=[
                                                                                                                        dbc.Button(
                                                                                                                            "Download .PDF",
                                                                                                                            color="link",
                                                                                                                            block=True
                                                                                                                        )
                                                                                                                    ]
                                                                                                                ),
                                                                                                            ],
                                                                                                            className="btn-group d-flex"
                                                                                                        ),
                                                                                                    ],
                                                                                                    width=12
                                                                                                )
                                                                                            ],
                                                                                            no_gutters=True,
                                                                                        ),
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                            dbc.ModalBody(
                                                                                children=[
                                                                                    dcc.Loading(
                                                                                        html.Div(
                                                                                            className="bg-white chart",
                                                                                            id='allCharts-scatter-pmd',
                                                                                            children=[
                                                                                                dcc.Graph(
                                                                                                    id="allCharts-pmd",
                                                                                                )

                                                                                            ],
                                                                                        ),
                                                                                    ),
                                                                                ],
                                                                                style={"width": "100%"},
                                                                            ),
                                                                            dbc.ModalFooter(
                                                                                dbc.Button("Close", id="close-3-in-1",
                                                                                           className="ml-auto")
                                                                            )
                                                                        ],
                                                                        id="modal-3-in-1",
                                                                        size="xl"
                                                                    ),
                                                                ],
                                                                width=4,
                                                                align="center",
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # Bottom content of left block, statistics
                                            dbc.CardBody(
                                                children=[
                                                    dbc.ButtonGroup(
                                                        children=[
                                                            dbc.Button(
                                                                "PCA",
                                                                className="w-100",
                                                                id="pca-toggle",
                                                            ),
                                                            dbc.Button(
                                                                "Remagnetization Circles",
                                                                className="w-100",
                                                                id="halls-toggle",
                                                            ),
                                                            dbc.Button(
                                                                "Fisher",
                                                                className="w-100",
                                                                id="fisher-toggle",
                                                            )
                                                        ],
                                                        className="btn-group d-flex"
                                                    ),
                                                    dbc.Container(
                                                        children=[
                                                            dbc.Collapse(
                                                                id="pca-collapse",
                                                                children=[
                                                                    dcc.Tabs(
                                                                        id='pca-mode',
                                                                        value="DE-BFL",
                                                                        children=[
                                                                            dcc.Tab(
                                                                                label="standard",
                                                                                value="DE-BFL",
                                                                                className="radio-tab-collapse",
                                                                            ),
                                                                            dcc.Tab(
                                                                                label="origin",
                                                                                value="DE-BFL-O",
                                                                                className="radio-tab-collapse",
                                                                            ),
                                                                        ]
                                                                    ),
                                                                    dcc.Loading(
                                                                        html.Div(
                                                                            id='pca-stat-result'
                                                                        ),
                                                                    ),
                                                                    dbc.Button(
                                                                        'Add to table',
                                                                        id='pca-add-button',
                                                                        block=True
                                                                    ),
                                                                    dbc.Tooltip(
                                                                        "Look at PCA.csv tab",
                                                                        target="pca-add-button",
                                                                        placement="bottom",
                                                                    ),
                                                                ]
                                                            ),
                                                            dbc.Collapse(
                                                                id="remag-circ-collapse",
                                                                children=[
                                                                    dcc.Tabs(
                                                                        className="padding-top-bot",
                                                                        id='halls-mode',
                                                                        value="DE-BFP",
                                                                        children=[
                                                                            dcc.Tab(
                                                                                label="standard",
                                                                                value="DE-BFPp",
                                                                                className="radio-tab-collapse",
                                                                                disabled=True,
                                                                            ),
                                                                            dcc.Tab(
                                                                                label="normalized",
                                                                                value="DE-BFP",
                                                                                className="radio-tab-collapse",
                                                                            ),
                                                                        ]
                                                                    ),
                                                                    dcc.Loading(
                                                                        html.Div(
                                                                            id='halls-stat-result'
                                                                        ),
                                                                    ),
                                                                    dbc.Button(
                                                                        'Add to table',
                                                                        id='halls-add-button',
                                                                        block=True
                                                                    ),
                                                                    dbc.Tooltip(
                                                                        "Look at RemagCircles.csv tab",
                                                                        target="halls-add-button",
                                                                        placement="bottom",
                                                                    ),
                                                                ]
                                                            ),
                                                            dbc.Collapse(
                                                                id="fisher-collapse",
                                                                children=[
                                                                    dcc.Loading(
                                                                        html.Div(
                                                                            id='fisher-stat-result'
                                                                        ),
                                                                    ),
                                                                    dbc.Button(
                                                                        'Add to table',
                                                                        id='fisher-add-button',
                                                                        block=True
                                                                    ),
                                                                    dbc.Tooltip(
                                                                        "Look at FisherMean.csv tab",
                                                                        target="fisher-add-button",
                                                                        placement="bottom",
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        className="accordion",
                                                        fluid=True
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                ],
                                width=4,
                            ),
                            # Right block, cols=8
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        children=[
                                            dbc.CardHeader(
                                                children=[
                                                    dcc.Tabs(
                                                        id="file-tabs",
                                                        value="main-file",
                                                        children=[
                                                            dcc.Tab(
                                                                label="Your Data",
                                                                id="main-file-tab",
                                                                value="main-file",
                                                                className="radio-tab-collapse"
                                                            ),
                                                            dcc.Tab(
                                                                label="PCA.csv",
                                                                id="pca-table-tab",
                                                                value="pca-table",
                                                                className="radio-tab-collapse"
                                                            ),
                                                            dcc.Tab(
                                                                label="GreatCircles.csv",
                                                                id="halls-table-tab",
                                                                value="halls-table",
                                                                className="radio-tab-collapse"
                                                            ),
                                                            dcc.Tab(
                                                                label="FisherMean.csv",
                                                                id="fisher-table-tab",
                                                                value="fisher-table",
                                                                className="radio-tab-collapse"
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            dbc.CardBody(
                                                children=[
                                                    dbc.Container(
                                                        children=[
                                                            dbc.Collapse(
                                                                id='demag-table-collapse',
                                                                children=[
                                                                    dash_table.DataTable(
                                                                        id="demag-table-data",
                                                                        data=dff.to_dict('records'),
                                                                        columns=[{'name': i, 'id': i} for i in
                                                                                 dff.columns],
                                                                        editable=True,
                                                                        row_deletable=True,
                                                                        style_table={
                                                                            'height': '180px',
                                                                        },
                                                                        fixed_rows={'headers': True, 'data': 0},
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.Collapse(
                                                                id="pca-table-collapse",
                                                                children=[
                                                                    dbc.Row(
                                                                        children=[
                                                                            dbc.Col(
                                                                                children=[
                                                                                    dbc.Input(
                                                                                        placeholder="Filename",
                                                                                        type="text",
                                                                                        id="pca-filename",
                                                                                    )
                                                                                ],
                                                                                width=2,
                                                                            ),
                                                                            dbc.Col(
                                                                                children=[
                                                                                    html.A(
                                                                                        className="w-100",
                                                                                        id='pca-export',
                                                                                        children=[
                                                                                            dbc.Button(
                                                                                                "Download PCA data",
                                                                                                color="link",
                                                                                                block=True,
                                                                                            )
                                                                                        ]
                                                                                    ),
                                                                                ],
                                                                                width=2,
                                                                            )
                                                                        ],
                                                                        no_gutters=True,
                                                                    ),
                                                                    dash_table.DataTable(
                                                                        id="pca-table-data",
                                                                        data=bing_df.to_dict('records'),
                                                                        columns=[{'name': i, 'id': i} for i in
                                                                                 bing_df.columns],
                                                                        editable=True,
                                                                        row_deletable=True,
                                                                        style_table={
                                                                            'height': '150px',
                                                                        },
                                                                        fixed_rows={'headers': True, 'data': 0},
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.Collapse(
                                                                id="halls-table-collapse",
                                                                children=[
                                                                    dbc.Row(
                                                                        children=[
                                                                            dbc.Col(
                                                                                children=[
                                                                                    dbc.Input(
                                                                                        placeholder="Filename",
                                                                                        type="text",
                                                                                        id="halls-filename",
                                                                                    )
                                                                                ],
                                                                                width=2,
                                                                            ),
                                                                            dbc.Col(
                                                                                children=[
                                                                                    html.A(
                                                                                        className="w-100",
                                                                                        id='halls-export',
                                                                                        children=[
                                                                                            dbc.Button(
                                                                                                "Download RC data",
                                                                                                color="link",
                                                                                                block=True,
                                                                                            )
                                                                                        ]
                                                                                    ),
                                                                                ],
                                                                                width=2,
                                                                            )
                                                                        ],
                                                                        no_gutters=True,
                                                                    ),
                                                                    dash_table.DataTable(
                                                                        id="halls-table-data",
                                                                        data=bing_df.to_dict('records'),
                                                                        columns=[{'name': i, 'id': i} for i in
                                                                                 bing_df.columns],
                                                                        editable=True,
                                                                        row_deletable=True,
                                                                        style_table={
                                                                            'height': '150px',
                                                                        },
                                                                        fixed_rows={'headers': True, 'data': 0},
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.Collapse(
                                                                id="fisher-table-collapse",
                                                                children=[
                                                                    dbc.Row(
                                                                        children=[
                                                                            dbc.Col(
                                                                                children=[
                                                                                    dbc.Input(
                                                                                        placeholder="Filename",
                                                                                        type="text",
                                                                                        id="fisher-filename",
                                                                                    )
                                                                                ],
                                                                                width=2,
                                                                            ),
                                                                            dbc.Col(
                                                                                children=[
                                                                                    html.A(
                                                                                        className="w-100",
                                                                                        id='fisher-export',
                                                                                        children=[
                                                                                            dbc.Button(
                                                                                                "Download Fisher data",
                                                                                                color="link",
                                                                                                block=True,
                                                                                            )
                                                                                        ]
                                                                                    ),
                                                                                ],
                                                                                width=2,
                                                                            )
                                                                        ],
                                                                        no_gutters=True,
                                                                    ),
                                                                    dash_table.DataTable(
                                                                        id="fisher-table-data",
                                                                        data=bing_df.to_dict('records'),
                                                                        columns=[{'name': i, 'id': i} for i in
                                                                                 fish_df.columns],
                                                                        editable=True,
                                                                        row_deletable=True,
                                                                        style_table={
                                                                            'height': '150px',
                                                                        },
                                                                        fixed_rows={'headers': True, 'data': 0},
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                        className="accordion",
                                                        fluid=True,
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                width=8
                            )
                        ]
                    )
                ],
                fluid=True,
                className="mb-5"
            ),
            # Bottom content
            dbc.Container(
                children=[
                    dbc.Row(
                        children=[
                            # Left block, demagnetization chart
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        children=[
                                            # Header
                                            dbc.CardHeader(
                                                children=[
                                                    dbc.ButtonGroup(
                                                        children=[
                                                            dbc.DropdownMenu(
                                                                label="Chart settings",
                                                                id="mag-settings",
                                                                group=True,
                                                                className="w-100 text-center",
                                                                children=[
                                                                    html.H6("Annotations", id="annot-mag",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Annotations, its position and mode",
                                                                                target="annot-mag", placement="right"),
                                                                    dcc.Dropdown(
                                                                        id="mag-dots-annots",
                                                                        multi=True,
                                                                        value=None
                                                                    ),
                                                                    dbc.Select(
                                                                        id='text-position-mag',
                                                                        options=[
                                                                            {'label': 'Top left', 'value': 'top left'},
                                                                            {'label': 'Top center',
                                                                             'value': 'top center'},
                                                                            {'label': 'Top right',
                                                                             'value': 'top right'},
                                                                            {'label': 'Middle left',
                                                                             'value': 'middle left'},
                                                                            {'label': 'Middle',
                                                                             'value': 'middle center'},
                                                                            {'label': 'Middle right',
                                                                             'value': 'middle right'},
                                                                            {'label': 'Bottom left',
                                                                             'value': 'bottom left'},
                                                                            {'label': 'Bottom center',
                                                                             'value': 'bottom center'},
                                                                            {'label': 'Bottom right',
                                                                             'value': 'bottom right'}
                                                                        ],
                                                                        value='bottom right',
                                                                        className="w-100",
                                                                    ),
                                                                    dcc.Tabs(
                                                                        id="text-mode-mag",
                                                                        value="id",
                                                                        children=[
                                                                            dcc.Tab(label="Off", value="off",
                                                                                    className="radio-tab text-uppercase", ),
                                                                            dcc.Tab(label="id", value="id",
                                                                                    className="radio-tab text-uppercase", ),
                                                                            dcc.Tab(label="demag. measure",
                                                                                    value="measure",
                                                                                    className="radio-tab text-uppercase", ),
                                                                        ],
                                                                    ),
                                                                    dbc.DropdownMenuItem(divider=True),
                                                                    html.H6("Dots", id="dots-mag",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Dots size and symbol",
                                                                                target="dots-mag", placement="right"),
                                                                    dbc.InputGroup(
                                                                        children=[
                                                                            dbc.Input(id='mag-dots-size', type="number",
                                                                                      min=1,
                                                                                      max=12, value=8, step=1,
                                                                                      style={"height": "30px"}),
                                                                            dbc.Select(
                                                                                id='mag-dots-symbol',
                                                                                options=[
                                                                                    {'label': 'Circle',
                                                                                     'value': 'circle'},
                                                                                    {'label': 'Square',
                                                                                     'value': 'square'},
                                                                                    {'label': 'Triangle',
                                                                                     'value': 'triangle-up'},
                                                                                    {'label': 'Star',
                                                                                     'value': 'star'}
                                                                                ],
                                                                                value='circle',
                                                                            ),
                                                                        ],
                                                                        className="d-flex",
                                                                    ),
                                                                ],
                                                            ),
                                                            dbc.Button(
                                                                "Generate high-res images",
                                                                id="gen-img-mag",
                                                                className="w-100"
                                                            ),
                                                        ],
                                                        className="btn-group d-flex"
                                                    ),
                                                    dbc.Collapse(
                                                        children=[
                                                            dbc.ButtonGroup(
                                                                children=[
                                                                    html.A(
                                                                        id="svg-mag",
                                                                        className="w-100",
                                                                        children=[
                                                                            dbc.Button(
                                                                                "Download .SVG",
                                                                                color="link",
                                                                                block=True,
                                                                            )
                                                                        ]
                                                                    ),
                                                                    html.A(
                                                                        id="pdf-mag",
                                                                        className="w-100",
                                                                        children=[
                                                                            dbc.Button(
                                                                                "Download .PDF",
                                                                                color="link",
                                                                                block=True
                                                                            )
                                                                        ]
                                                                    ),
                                                                ],
                                                                className="btn-group d-flex"
                                                            ),
                                                        ],
                                                        id="img-collapse-mag"
                                                    ),
                                                ],
                                            ),
                                            # Body
                                            dbc.CardBody(
                                                dcc.Loading(
                                                    dcc.Graph(
                                                        id='mag-chart',
                                                        config=chart_config,
                                                    ),
                                                )
                                            )
                                        ]
                                    )
                                ],
                                width=4,
                            ),
                            # Central block, polar chart
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        children=[
                                            dbc.CardHeader(
                                                children=[
                                                    dbc.ButtonGroup(
                                                        children=[
                                                            dbc.DropdownMenu(
                                                                label="Chart settings",
                                                                id="polar-settings",
                                                                group=True,
                                                                className="w-100 text-center",
                                                                children=[
                                                                    dcc.Tabs(
                                                                        id='system-polar',
                                                                        value="geographic",
                                                                        children=[
                                                                            dcc.Tab(label="geographic",
                                                                                    value="geographic",
                                                                                    className="radio-tab", ),
                                                                            dcc.Tab(label="stratigraphic",
                                                                                    value="stratigraphic",
                                                                                    className="radio-tab", ),
                                                                        ]
                                                                    ),
                                                                    dcc.Tabs(
                                                                        id='line-mode-polar',
                                                                        value="great_circles",
                                                                        children=[
                                                                            dcc.Tab(label="straight lines",
                                                                                    value="straight",
                                                                                    className="radio-tab",
                                                                                    id="straight-lines-polar-tab"),
                                                                            dcc.Tab(label="great circles",
                                                                                    value="great_circles",
                                                                                    className="radio-tab",
                                                                                    id="great-circles-polar-tab"),
                                                                            dcc.Tab(label="without lines",
                                                                                    value="nothing",
                                                                                    className="radio-tab", ),
                                                                        ]
                                                                    ),
                                                                    html.H6("Annotations", id="annot-polar",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Annotations, its position and mode",
                                                                                target="annot-polar",
                                                                                placement="right"),
                                                                    dcc.Dropdown(
                                                                        id="polar-dots-annots",
                                                                        multi=True,
                                                                        value=None
                                                                    ),
                                                                    dbc.Select(
                                                                        id='text-position-polar',
                                                                        options=[
                                                                            {'label': 'Top left', 'value': 'top left'},
                                                                            {'label': 'Top center',
                                                                             'value': 'top center'},
                                                                            {'label': 'Top right',
                                                                             'value': 'top right'},
                                                                            {'label': 'Middle left',
                                                                             'value': 'middle left'},
                                                                            {'label': 'Middle',
                                                                             'value': 'middle center'},
                                                                            {'label': 'Middle right',
                                                                             'value': 'middle right'},
                                                                            {'label': 'Bottom left',
                                                                             'value': 'bottom left'},
                                                                            {'label': 'Bottom center',
                                                                             'value': 'bottom center'},
                                                                            {'label': 'Bottom right',
                                                                             'value': 'bottom right'}
                                                                        ],
                                                                        value='top left',
                                                                        className="w-100",
                                                                    ),
                                                                    dcc.Tabs(
                                                                        id="text-mode-polar",
                                                                        value="id",
                                                                        children=[
                                                                            dcc.Tab(label="Off", value="off",
                                                                                    className="radio-tab text-uppercase", ),
                                                                            dcc.Tab(label="id", value="id",
                                                                                    className="radio-tab text-uppercase", ),
                                                                            dcc.Tab(label="demag. measure",
                                                                                    value="measure",
                                                                                    className="radio-tab text-uppercase",
                                                                                    id="demag-measure-polar-tab"),
                                                                        ],
                                                                    ),
                                                                    dbc.DropdownMenuItem(divider=True),
                                                                    html.H6("Dots", id="dots-polar",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Dots size and symbol",
                                                                                target="dots-polar", placement="right"),
                                                                    dbc.InputGroup(
                                                                        children=[
                                                                            dbc.Input(id='polar-dots-size',
                                                                                      type="number", min=1,
                                                                                      max=12, value=8, step=1,
                                                                                      style={"height": "30px"}),
                                                                            dbc.Select(
                                                                                id='polar-dots-symbol',
                                                                                options=[
                                                                                    {'label': 'Circle',
                                                                                     'value': 'circle'},
                                                                                    {'label': 'Square',
                                                                                     'value': 'square'},
                                                                                    {'label': 'Triangle',
                                                                                     'value': 'triangle-up'},
                                                                                    {'label': 'Star',
                                                                                     'value': 'star'}
                                                                                ],
                                                                                value='circle',
                                                                            ),
                                                                        ],
                                                                        className="d-flex",
                                                                    ),
                                                                ]
                                                            ),
                                                            dbc.Button(
                                                                "Generate high-res images",
                                                                id="gen-img-polar",
                                                                className="w-100"
                                                            ),
                                                        ],
                                                        className="btn-group d-flex"
                                                    ),
                                                    dbc.Collapse(
                                                        children=[
                                                            dbc.ButtonGroup(
                                                                children=[
                                                                    html.A(
                                                                        id="svg-polar",
                                                                        className="w-100",
                                                                        children=[
                                                                            dbc.Button(
                                                                                "Download .SVG",
                                                                                color="link",
                                                                                block=True,
                                                                            )
                                                                        ]
                                                                    ),
                                                                    html.A(
                                                                        id="pdf-polar",
                                                                        className="w-100",
                                                                        children=[
                                                                            dbc.Button(
                                                                                "Download .PDF",
                                                                                color="link",
                                                                                block=True
                                                                            )
                                                                        ]
                                                                    ),
                                                                ],
                                                                className="btn-group d-flex"
                                                            ),
                                                        ],
                                                        id="img-collapse-polar"
                                                    ),
                                                ]
                                            ),
                                            dbc.CardBody(
                                                dcc.Loading(
                                                    dcc.Graph(
                                                        id='polar-chart',
                                                        config=chart_config,
                                                    ),
                                                )
                                            )
                                        ]
                                    )
                                ],
                                width=4,
                            ),
                            # Right block, Zyiderveld's chart
                            dbc.Col(
                                children=[
                                    dbc.Card(
                                        children=[
                                            dbc.CardHeader(
                                                children=[
                                                    dbc.ButtonGroup(
                                                        children=[
                                                            dbc.DropdownMenu(
                                                                label="Chart settings",
                                                                id="zyid-settings",
                                                                group=True,
                                                                className="w-100",
                                                                children=[
                                                                    dcc.Tabs(
                                                                        id='system-zyid',
                                                                        value="core",
                                                                        children=[
                                                                            dcc.Tab(label="core", value="core",
                                                                                    className="radio-tab", ),
                                                                            dcc.Tab(label="geographic",
                                                                                    value="geographic",
                                                                                    className="radio-tab", ),
                                                                            dcc.Tab(label="stratigraphic",
                                                                                    value="stratigraphic",
                                                                                    className="radio-tab", ),
                                                                        ]
                                                                    ),
                                                                    dcc.Tabs(
                                                                        id='zyid-projection',
                                                                        value="NN",
                                                                        children=[
                                                                            dcc.Tab(label="N,N / E,UP", value="NN",
                                                                                    className="radio-tab", ),
                                                                            dcc.Tab(label="N,UP / E,E", value="NUP",
                                                                                    className="radio-tab", ),
                                                                            dcc.Tab(label="W,UP / N,N", value="WUP",
                                                                                    className="radio-tab", ),
                                                                        ]
                                                                    ),
                                                                    html.H6("Annotations", id="annot-mag",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Annotations position and mode",
                                                                                target="annot-mag", placement="right"),
                                                                    dcc.Dropdown(
                                                                        id="zyid-dots-annots",
                                                                        multi=True,
                                                                        value=None
                                                                    ),
                                                                    dbc.Select(
                                                                        id='text-position-zyid',
                                                                        options=[
                                                                            {'label': 'Top left', 'value': 'top left'},
                                                                            {'label': 'Top center',
                                                                             'value': 'top center'},
                                                                            {'label': 'Top right',
                                                                             'value': 'top right'},
                                                                            {'label': 'Middle left',
                                                                             'value': 'middle left'},
                                                                            {'label': 'Middle',
                                                                             'value': 'middle center'},
                                                                            {'label': 'Middle right',
                                                                             'value': 'middle right'},
                                                                            {'label': 'Bottom left',
                                                                             'value': 'bottom left'},
                                                                            {'label': 'Bottom center',
                                                                             'value': 'bottom center'},
                                                                            {'label': 'Bottom right',
                                                                             'value': 'bottom right'}
                                                                        ],
                                                                        value='bottom right',
                                                                        className="w-100",
                                                                    ),
                                                                    dcc.Tabs(
                                                                        id="text-mode-zyid",
                                                                        value="id",
                                                                        children=[
                                                                            dcc.Tab(label="Off", value="off",
                                                                                    className="radio-tab text-uppercase", ),
                                                                            dcc.Tab(label="id", value="id",
                                                                                    className="radio-tab text-uppercase", ),
                                                                            dcc.Tab(label="demag. measure",
                                                                                    value="measure",
                                                                                    className="radio-tab text-uppercase", ),
                                                                        ],
                                                                    ),
                                                                    dbc.DropdownMenuItem(divider=True),
                                                                    html.H6("Dots", id="dots-mag",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Dots size and symbol",
                                                                                target="dots-mag", placement="right"),
                                                                    dbc.InputGroup(
                                                                        children=[
                                                                            dbc.Input(id='zyid-dots-size',
                                                                                      type="number", min=1,
                                                                                      max=12, value=8, step=1,
                                                                                      style={"height": "30px"}),
                                                                            dbc.Select(
                                                                                id='zyid-dots-symbol',
                                                                                options=[
                                                                                    {'label': 'Circle',
                                                                                     'value': 'circle'},
                                                                                    {'label': 'Square',
                                                                                     'value': 'square'},
                                                                                    {'label': 'Triangle',
                                                                                     'value': 'triangle-up'},
                                                                                    {'label': 'Star',
                                                                                     'value': 'star'}
                                                                                ],
                                                                                value='circle',
                                                                            ),
                                                                        ],
                                                                        className="d-flex",
                                                                    ),
                                                                    dbc.DropdownMenuItem(divider=True),
                                                                    html.H6("Scale", id="scale-zyid",
                                                                            className="text-muted text-uppercase"),
                                                                    dbc.Tooltip("Chart scale mode", target="scale-zyid",
                                                                                placement="right"),
                                                                    dbc.Input(id='zyid-chart-scale', type="number",
                                                                              min=1, max=4, value=1, step=1),
                                                                ]
                                                            ),
                                                            dbc.Button(
                                                                "Generate high-res images",
                                                                id="gen-img-zyid",
                                                                className="w-100"
                                                            ),
                                                        ],
                                                        className="btn-group d-flex"
                                                    ),
                                                    dbc.Collapse(
                                                        children=[
                                                            dbc.ButtonGroup(
                                                                children=[
                                                                    html.A(
                                                                        id="svg-zyid",
                                                                        className="w-100",
                                                                        children=[
                                                                            dbc.Button(
                                                                                "Download .SVG",
                                                                                color="link",
                                                                                block=True,
                                                                            )
                                                                        ]
                                                                    ),
                                                                    html.A(
                                                                        id="pdf-zyid",
                                                                        className="w-100",
                                                                        children=[
                                                                            dbc.Button(
                                                                                "Download .PDF",
                                                                                color="link",
                                                                                block=True
                                                                            )
                                                                        ]
                                                                    ),
                                                                ],
                                                                className="btn-group d-flex"
                                                            ),
                                                        ],
                                                        id="img-collapse-zyid"
                                                    ),
                                                ]
                                            ),
                                            dbc.CardBody(
                                                dcc.Loading(
                                                    dcc.Graph(
                                                        id='zyid-chart',
                                                        config=chart_config,
                                                    ),
                                                )
                                            )
                                        ]
                                    )
                                ],
                                width=4,
                            )
                        ],
                    ),
                ],
                fluid=True,
            ),
        ],
        fluid=True,
        # style={"height": "100vh", "overflow":"hidden"}
    )
]


@app.callback(
    [Output("demag-table-collapse", "is_open"),
     Output("pca-table-collapse", "is_open"),
     Output("halls-table-collapse", "is_open"),
     Output("fisher-table-collapse", "is_open"), ],
    [Input("file-tabs", "value"), ]
)
def table_switch(table_tab):
    if table_tab == "main-file":
        return True, False, False, False
    elif table_tab == "pca-table":
        return False, True, False, False
    elif table_tab == "halls-table":
        return False, False, True, False
    elif table_tab == "fisher-table":
        return False, False, False, True
    else:
        return True, False, False, False


@app.callback(
    Output("main-file-tab", "label"),
    [Input('upload-data', 'contents'), ],
    [State('upload-data', 'filename')]
)
def main_file_tab(content, filename):
    if filename:
        return filename
    return "Your Data"


@app.callback(
    [Output("pca-collapse", "is_open"),
     Output("remag-circ-collapse", "is_open"),
     Output("fisher-collapse", "is_open")],
    [Input("pca-toggle", "n_clicks"),
     Input("halls-toggle", "n_clicks"),
     Input("fisher-toggle", "n_clicks"), ],
    [State("pca-collapse", "is_open"),
     State("remag-circ-collapse", "is_open"),
     State("fisher-collapse", "is_open")]
)
def toggle_statistics(n_clc_pca, n_clc_circ, n_clc_fisher, is_open_pca, is_open_circ, is_open_fisher):
    ctx = dash.callback_context

    if not ctx.triggered:
        return ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "pca-toggle" and n_clc_pca:
        return not is_open_pca, False, False
    elif button_id == "halls-toggle" and n_clc_circ:
        return False, not is_open_circ, False
    elif button_id == "fisher-toggle" and n_clc_fisher:
        return False, False, not is_open_fisher
    else:
        return False, False, False


@app.callback(
    [Output("demag-measure-polar-tab", "disabled"),
     Output("straight-lines-polar-tab", "disabled"),
     Output("great-circles-polar-tab", "disabled"),
     Output("pca-toggle", "disabled"),
     Output("fisher-toggle", "disabled"),
     Output("halls-toggle", "disabled"),
     Output("open-3-in-1", "disabled"),
     Output("line-mode-polar", "value"), ],
    [Input("demag-table-data", "data")],
    [State("line-mode-polar", "value")]
)
def disable_content_pmm_dir(data, linemode):
    if data:
        disable = False
        line_mode = "great_circles"
        df = pd.DataFrame(data)
        if "CODE" in df.columns or "Steprange" in df.columns:
            disable = True
            line_mode = "nothing"
        return disable, disable, disable, disable, False, False, disable, line_mode
    disabled = []
    for i in range(7): disabled.append(True)
    disabled.append(linemode)
    return False, False, False, True, True, True, True, linemode


@app.callback(
    Output("demag-table-collapse", "children"),
    [Input('upload-data', 'contents'),
     Input("pca-collapse", "is_open"),
     Input("remag-circ-collapse", "is_open"),
     Input("fisher-collapse", "is_open"), ],
    [State('upload-data', 'filename')]
)
def update_output_datatable(list_of_contents, is_open_pca, is_open_circ, is_open_fisher, name):
    if list_of_contents is not None:
        edit_mode = False
        if is_open_pca or is_open_circ or is_open_fisher:
            edit_mode = True
        table = [parse_contents_for_plot_dt(list_of_contents, name, "for_table", edit_mode)]
        return table
    else:
        df = pd.DataFrame(
            {'T or M': [], 'X': [], 'Y': [], 'Z': [], 'MAG': [], 'Dg': [], 'Ig': [], 'Ds': [], 'Is': [], 'a95': []})
        return html.Div(
            children=[
                dash_table.DataTable(
                    id='demag-table-data',
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    editable=True,
                    row_deletable=True,
                    style_table={
                        'height': '180px',
                    },
                    fixed_rows={'headers': True, 'data': 0},
                ),
            ]
        )


def download_table(data, filename):
    if filename:
        name = filename + ".csv"
    else:
        name = "Data.csv"
    export_table = pd.DataFrame(data)
    csv_string = export_table.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return (csv_string, name)


app.callback(
    [dash.dependencies.Output('pca-export', 'href'),
     dash.dependencies.Output('pca-export', 'download')],
    [dash.dependencies.Input('pca-table-data', 'data'),
     dash.dependencies.Input('pca-filename', 'value')]
)(download_table)

app.callback(
    [dash.dependencies.Output('halls-export', 'href'),
     dash.dependencies.Output('halls-export', 'download')],
    [dash.dependencies.Input('halls-table-data', 'data'),
     dash.dependencies.Input('halls-filename', 'value')]
)(download_table)

app.callback(
    [dash.dependencies.Output('fisher-export', 'href'),
     dash.dependencies.Output('fisher-export', 'download')],
    [dash.dependencies.Input('fisher-table-data', 'data'),
     dash.dependencies.Input('fisher-filename', 'value')]
)(download_table)


def gen_img(n_clicks, figure, is_open):
    fmts = ["svg", "pdf"]
    urls = []
    if n_clicks is not None:
        if is_open:
            return [None, None, False]
        for fmt in fmts:
            filename = "figure{}.".format(time.strftime("%Y.%m.%d.-%H.%M.%S")) + fmt
            write_image(figure, os.path.join(UPLOAD_DIRECTORY, filename))
            urls.append("/download/{}".format(urlquote(filename)))
        return urls[0], urls[1], not is_open
    return [None, None, False]


#  Try to replace this by 1 callback by cycle "for" with ["polar", "mag", "zyid"]
app.callback(
    [Output("svg-mag", "href"),
     Output("pdf-mag", 'href'),
     Output("img-collapse-mag", "is_open")],
    [Input("gen-img-mag", "n_clicks"), ],
    [State("mag-chart", "figure"),
     State("img-collapse-mag", "is_open")],
)(gen_img)

app.callback(
    [Output("svg-polar", "href"),
     Output("pdf-polar", 'href'),
     Output("img-collapse-polar", "is_open")],
    [Input("gen-img-polar", "n_clicks"), ],
    [State("polar-chart", "figure"),
     State("img-collapse-polar", "is_open")],
)(gen_img)

app.callback(
    [Output("svg-zyid", "href"),
     Output("pdf-zyid", 'href'),
     Output("img-collapse-zyid", "is_open")],
    [Input("gen-img-zyid", "n_clicks"), ],
    [State("zyid-chart", "figure"),
     State("img-collapse-zyid", "is_open")],
)(gen_img)


@app.callback(
    [Output("svg-allCharts", "href"),
     Output("pdf-allCharts", 'href'), ],
    [Input("allCharts-pmd", "figure"), ]
)
def gen_allCharts(figure):
    fmts = ["svg", "pdf"]
    urls = []
    if figure:
        figure['layout']['width'] = 1400
        for fmt in fmts:
            filename = "figure{}.".format(time.strftime("%Y.%m.%d.-%H.%M.%S")) + fmt
            write_image(figure, os.path.join(UPLOAD_DIRECTORY, filename))
            urls.append("/download/{}".format(urlquote(filename)))
        return urls[0], urls[1]
    return [None, None]


@app.callback(
    Output("modal-3-in-1", "is_open"),
    [Input("open-3-in-1", "n_clicks"),
     Input("close-3-in-1", "n_clicks")],
    [State("modal-3-in-1", "is_open")]
)
def toggle_modal_3_in_1(open_n_clicks, close_n_clicks, is_open):
    if open_n_clicks or close_n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output('polar-chart', 'figure'),
    [Input('system-polar', 'value'),
     Input('polar-dots-size', 'value'),
     Input('polar-dots-symbol', 'value'),
     Input('polar-dots-annots', 'value'),
     Input('text-position-polar', 'value'),
     Input('text-mode-polar', 'value'),
     Input('demag-table-data', 'data'),
     Input('demag-table-data', 'selected_rows'),
     Input('line-mode-polar', 'value'),
     Input("pca-collapse", "is_open"),
     Input("remag-circ-collapse", "is_open"),
     Input("fisher-collapse", "is_open"),
     Input("pca-mode", "value"),
     Input("halls-mode", "value")]
)
def update_graph_polar_pm(system, dots_size, marker_symbol, dots_with_annotation, text_position, text_mode,
                          data, selected_dots, line_mode, is_open_pca, is_open_circ, is_open_fisher,
                          pca_mode, halls_mode):
    df = pd.DataFrame(data)

    if "CODE" not in df.columns and "Steprange" not in df.columns:
        for i in df.columns:
            df[i] = pd.to_numeric(df[i])
    else:
        df["id"] = pd.to_numeric(df["id"])

    axdots_r = []
    axdots_a = []
    for i in [0, 90, 180, 270]:
        for j in range(10, 90, 10):
            axdots_r.append(j)
            axdots_a.append(i)

    if df.empty:
        df = pd.DataFrame(
            {'T/M': [], 'X': [], 'Y': [], 'Z': [], 'MAG': [], 'Dg': [], 'Ig': [], 'Ds': [], 'Is': [],
             'a95': []})
        return {
            'data': [
                go.Scatterpolar(
                    r=axdots_r,
                    theta=axdots_a,
                    mode="markers",
                    marker=dict(
                        color='black',
                        size=2
                    )
                ),
                go.Scatterpolar(
                    r=[0],
                    theta=[0],
                    mode="markers",
                    marker=dict(
                        color='black',
                        size=7,
                        symbol="cross-thin-open"
                    )
                )
            ],
            'layout': go.Layout(
                font=dict(
                    family="Times New Roman",
                    size=18,
                    color="black"
                ),
                showlegend=False,
                template="presentation",
                margin=margin_scatter_polar,
                polar=dict(
                    angularaxis=dict(
                        tickfont=dict(
                            size=18,
                            family="Times New Roman"
                        ),
                        rotation=90,
                        direction="clockwise",
                        dtick=90,
                        tickmode="array",
                        tickvals=[0, 90, 180, 270],
                        ticktext=["N", "E", "S", "W"],
                        ticksuffix=0,
                        showgrid=False
                    ),
                    radialaxis=dict(
                        range=[0, 90],
                        visible=False
                    )
                )
            )
        }

    col_D = "Dg"
    col_I = "Ig"

    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"

    angles_neg = []
    angles_pos = []
    values_neg = []
    values_pos = []
    values_abs = []
    angles_abs = list(abs(df[col_D]))

    for i in range(0, len(df[col_I]), 1):
        if df[col_I][i] < 0:
            values_neg.append(abs(df[col_I][i] + 90))
            values_abs.append(abs(df[col_I][i] + 90))
            angles_neg.append(df[col_D][i])
        else:
            values_pos.append(abs(df[col_I][i] - 90))
            values_abs.append(abs(df[col_I][i] - 90))
            angles_pos.append(df[col_D][i])

    unit = u"\u00B0"
    first_col_name = 'T'

    if 'M' in data[0]:
        first_col_name = 'M'
        unit = "mT"

    if "CODE" in df.columns and text_mode != "off":  # "CODE" column only in .pmm and .dir files, so that first_col_name doesn't exist
        text_mode = "id"

    annot_text = []  # "off" mode is default
    annot_dots_r = []
    annot_dots_t = []
    print(dots_with_annotation)
    if dots_with_annotation:
        for dot in dots_with_annotation:
            annot_dots_r.append(values_abs[dot])
            annot_dots_t.append(df[col_D][dot])
        if text_mode == "id":
            for dot in dots_with_annotation: annot_text.append(df["id"][dot])
        if text_mode == "measure":
            for dot in dots_with_annotation: annot_text.append(df[first_col_name][dot].astype(str) + unit)
    if text_mode == "off": annot_dots_r, annot_dots_t = [], []

    annot_dots_txt = annot_text

    if "CODE" not in df.columns:
        orthodromen_D, orthodromen_I = create_orthodromy(df, system)
        great_circles = []
        for i in range(len(orthodromen_D)):
            great_circle = graph_data_elem_polar(orthodromen_I[i], orthodromen_D[i], "lines", None, None,
                                                 "black", None, None, df)
            great_circles.append(great_circle)
    else:
        line_mode = "nothing"

    graph_data = [
        graph_data_elem_polar(axdots_r, axdots_a, "markers", 2, "circle", ["black", "black"], None, None, df),
        graph_data_elem_polar([0], [0], "markers", 7, "cross-thin-open", ["black", "black"], None, None, df),
        graph_data_elem_polar(annot_dots_r, annot_dots_t, "text", None, None, None, annot_dots_txt, text_position, df),
    ]

    if line_mode == "straight":
        graph_data.append(graph_data_elem_polar(values_abs, angles_abs, "lines", None, None, "black", None, None, df))
    elif line_mode == "great_circles":
        for great_circle in great_circles:
            graph_data.append(great_circle)
    # Dots after lines because order is important
    graph_data.extend(
        [graph_data_elem_polar(values_pos, angles_pos, "markers", dots_size,
                               marker_symbol, ["black", "black"], None, None, df),
         graph_data_elem_polar(values_neg, angles_neg, "markers", dots_size,
                               marker_symbol, ["white", "black"], None, None, df)]
    )
    # Statistics
    if selected_dots:
        df_selected_dots = pd.DataFrame(df.loc[selected_dots])
        mean_dot, error_circle = {}, {}
        if is_open_fisher:
            mean_dot, error_circle = draw_fisher_mean(df, selected_dots, system, dots_size, marker_symbol)
            graph_data.extend([mean_dot, error_circle])
        if is_open_circ:
            mean_dot, error_circle, remag_circle, rem_circ_cent = draw_halls_mean(df, selected_dots, system, dots_size,
                                                                                  marker_symbol, halls_mode)
            graph_data.extend([mean_dot, error_circle, remag_circle, rem_circ_cent])
        if is_open_pca:
            mean_dot, error_circle = draw_pca(df, selected_dots, system, dots_size, marker_symbol, pca_mode)
            graph_data.extend([mean_dot, error_circle])

    return {
        'data': graph_data,
        'layout': go.Layout(
            font=dict(
                family="Times New Roman",
                size=18,
                color="black"
            ),
            showlegend=False,
            template="presentation",
            margin=margin_scatter_polar,
            polar=dict(
                angularaxis=dict(
                    tickfont=dict(
                        size=18,
                        family="Times New Roman"
                    ),
                    rotation=90,
                    direction="clockwise",
                    dtick=90,
                    tickmode="array",
                    tickvals=[0, 90, 180, 270],
                    ticktext=["N", "E", "S", "W"],
                    ticksuffix=0,
                    showgrid=False
                ),
                radialaxis=dict(
                    range=[0, 90],
                    visible=False
                )
            ),
        )
    }


@app.callback(
    Output('mag-chart', 'figure'),
    [Input('mag-dots-size', 'value'),
     Input('mag-dots-symbol', 'value'),
     Input('demag-table-data', 'data'),
     Input('mag-dots-annots', 'value'),
     Input('text-position-mag', 'value'),
     Input('text-mode-mag', 'value'),
     ]
)
def update_graph_intensity(dots_size, marker_symbol, data, dots_with_annotation, text_position, text_mode):
    df = pd.DataFrame(data)

    relative_mag = []
    first_col = []

    if df.empty or "CODE" in df.columns or "Steprange" in df.columns:  # "CODE" column only in .pmm and .dir files
        return {
            'data': [
                go.Scatter(
                    x=first_col,
                    y=relative_mag,
                    mode='lines',
                )
            ],
            'layout': go.Layout(
                font=dict(
                    family="Times New Roman",
                    size=25,
                    color="black"
                ),
                showlegend=False,
                template="presentation",
                margin=margin_scatter_2d,
                grid=dict(
                    xside='bottom plot',
                    yside='left',
                ),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    showline=True,
                    linewidth=1.5,
                    anchor='free',
                    rangemode='tozero'
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    showline=True,
                    linewidth=1.5,
                    anchor='free',
                    rangemode='tozero'
                ),
            )
        }

    for i in df.columns:
        df[i] = pd.to_numeric(df[i])

    for mag in df.MAG:
        relative_mag.append(mag / max(df.MAG))

    unit = u'\u2103'
    first_col_name = "T"
    x_title_space = 1.10

    if "M" in data[0]:
        first_col_name = "M"
        unit = "mT"
        x_title_space = 1.15

    for i in df[first_col_name]:
        first_col.append(i)

    axes_titles = [
        go.layout.Annotation(
            x=x_title_space,
            y=-0.03,
            showarrow=False,
            text=unit,
            xref="paper",
            yref="paper"
        ),
        go.layout.Annotation(
            x=-0.1,
            y=1.07,
            showarrow=False,
            text='M/M' + u'\u2098' + u'\u2090' + u'\u2093' + '|M' + u'\u2098' + u'\u2090' + u'\u2093' +
                 ' = ' + str(format(max(df.MAG), '.2E')) + ' A/m',
            xref="paper",
            yref="paper"
        )
    ]

    annot_text = []  # "off" mode is default
    dots_with_annotation_x = []
    dots_with_annotation_y = []
    if dots_with_annotation:
        for dot in dots_with_annotation:
            dots_with_annotation_x.append(df[first_col_name][dot])
            dots_with_annotation_y.append(relative_mag[dot])
        if text_mode == "id":
            for dot in dots_with_annotation: annot_text.append(df["id"][dot])
        if text_mode == "measure":
            for dot in dots_with_annotation: annot_text.append(df[first_col_name][dot].astype(str) + unit)
    if text_mode == "off": dots_with_annotation_x, dots_with_annotation_y = [], []

    annot_dots_txt = annot_text

    tick_values = [0, max(first_col) / 2, max(first_col)]
    tick_text_x = [0, max(first_col) / 2, max(first_col)]
    if first_col_name == "T":
        tick_values = np.arange(0, max(first_col), 50)
        tick_text_x = []
        for i in range(0, len(tick_values)):
            if i % 2 == 0:
                tick_text_x.append(tick_values[i])
            else:
                tick_text_x.append('')

    return {
        'data': [
            go.Scatter(
                x=first_col,
                y=relative_mag,
                mode='lines',
                line=dict(
                    color='black',
                    width=1
                )
            ),
            go.Scatter(
                x=first_col,
                y=relative_mag,
                mode="markers",
                hovertemplate='<b>%{text}</b>',
                text=['id: {}'.format(df["id"][i]) for i in range(len(df))],
                marker=dict(
                    color='white',
                    size=dots_size,
                    line=dict(
                        color='black',
                        width=1
                    ),
                    symbol=marker_symbol
                )
            ),
            go.Scatter(
                x=dots_with_annotation_x,
                y=dots_with_annotation_y,
                mode="text",
                text=annot_dots_txt,
                textposition=text_position,
                textfont=dict(
                    family='Times New Roman',
                    size=16,
                    color='black'
                )
            )
        ],
        'layout': go.Layout(
            hovermode='closest',
            font=dict(
                family="Times New Roman",
                size=18,
                color="black"
            ),
            showlegend=False,
            template="presentation",
            margin=margin_scatter_2d,
            xaxis=dict(
                showgrid=False,
                tickvals=tick_values,
                ticktext=tick_text_x,
                ticks='inside',
                ticklen=10,
                tickson='boundaries',
                showline=True,
                linewidth=1.5,
                anchor='free',
                rangemode='tozero'
            ),
            yaxis=dict(
                showgrid=False,
                tickvals=[0.5, 1],
                ticks='inside',
                ticklen=10,
                tickson='boundaries',
                showline=True,
                linewidth=1.5,
                anchor='free',
                rangemode='tozero',
            ),
            annotations=axes_titles
        )
    }


@app.callback(
    Output('zyid-chart', 'figure'),
    [Input('upload-data', 'contents'),
     Input('system-zyid', 'value'),
     Input('demag-table-data', 'data'),
     Input('demag-table-data', 'selected_rows'),
     Input('zyid-dots-size', 'value'),
     Input('zyid-dots-symbol', 'value'),
     Input('zyid-dots-annots', 'value'),
     Input('text-position-zyid', 'value'),
     Input('text-mode-zyid', 'value'),
     Input('zyid-projection', 'value'),
     Input("pca-mode", "value"),
     Input("pca-collapse", "is_open"),
     Input('zyid-chart-scale', 'value'),
     ],
    [dash.dependencies.State('upload-data', 'filename')]
)
def update_graph_xyz(list_of_contents, system, data, selected_dots,
                     dots_size, marker_symbol, dots_with_annotation, text_position, text_mode,
                     orientation, pca_mode, is_open_pca, scale, name):
    df = pd.DataFrame(data)
    if df.empty or "CODE" in df.columns or "Steprange" in df.columns:  # "CODE" column only in .pmm and .dir files
        return {
            'data': [
                go.Scatter(
                    x=[0, 0],
                    y=[0, 0],
                    mode='lines'
                )
            ],
            'layout': go.Layout(
                font=dict(
                    family="Times New Roman",
                    size=25,
                    color="black"
                ),
                showlegend=False,
                margin=margin_scatter_2d,
                xaxis=dict(showgrid=False,
                           showticklabels=False,
                           zerolinewidth=1.5,
                           zerolinecolor='black',
                           ),
                yaxis=dict(
                    showgrid=False,
                    showticklabels=False,
                    zerolinewidth=1.5,
                    zerolinecolor='black',
                )
            )
        }

    for i in df.columns:
        df[i] = pd.to_numeric(df[i])

    extra_data = parse_contents_for_plot_dt(list_of_contents, name, "for_extra_data", False)

    if extra_data:
        A = extra_data[0]
        B = extra_data[1]
        S = extra_data[2]
        D = extra_data[3]

    hor_x = []
    hor_y = []
    vert_x = []
    vert_y = []
    title_x = ''
    title_y = ''

    # "core" is default parameter

    X = df['X']
    Y = df['Y']
    Z = df['Z']
    if system == "geographic":
        X, Y, Z = dir_to_xyz(df["Dg"], df["Ig"], df["MAG"])
    if system == "stratigraphic":
        X, Y, Z = dir_to_xyz(df["Ds"], df["Is"], df["MAG"])

    if orientation == 'NN':
        hor_x = Y
        hor_y = X
        vert_x = -Z
        vert_y = X
        title_x = 'E,UP'
        title_y = 'N,N'
    if orientation == 'NUP':
        hor_x = Y
        hor_y = X
        vert_x = Y
        vert_y = -Z
        title_x = 'E,E'
        title_y = 'N,UP'
    if orientation == 'WUP':
        hor_x = X
        hor_y = -Y
        vert_x = X
        vert_y = -Z
        title_x = 'N,N'
        title_y = 'W,UP'

    unit = u"\u00B0"
    first_col_name = 'T'

    if 'M' in data[0]:
        first_col_name = 'M'
        unit = "mT"

    annot_text = []  # "off" mode is default
    dots_with_annotation_x = []
    dots_with_annotation_y = []
    all_coord_x = list(hor_x) + list(vert_x)
    all_coord_y = list(hor_y) + list(vert_y)
    if dots_with_annotation:
        for dot in dots_with_annotation:
            dots_with_annotation_x.extend([hor_x[dot], vert_x[dot]])
            dots_with_annotation_y.extend([hor_y[dot], vert_y[dot]])
        if text_mode == "id":
            for dot in dots_with_annotation: annot_text.append(df["id"][dot])
        if text_mode == "measure":
            for dot in dots_with_annotation: annot_text.append(df[first_col_name][dot].astype(str) + unit)
    if text_mode == "off": dots_with_annotation_x, dots_with_annotation_y = [], []

    annot_dots_txt = list(annot_text) + list(annot_text)
    graph_data = [
        graph_data_elem_cartesian(hor_x, hor_y, "lines+markers",
                                  dots_size, marker_symbol, ['white', 'black', 'black'], None, None, None, df)[0],
        graph_data_elem_cartesian(vert_x, vert_y, "lines+markers",
                                  dots_size, marker_symbol, ['black', 'black', 'black'], None, None, None, df)[0],
        graph_data_elem_cartesian(dots_with_annotation_x, dots_with_annotation_y, "text",
                                  None, None, 'black', None, annot_dots_txt, text_position, df)
    ]

    # Add scale-button
    scale = 1 / scale
    border = {
        "x_min": min(all_coord_x) * (scale - np.sign(min(all_coord_x))),  # Because (-1)*sign(-1)*(-2) = -2
        "x_max": max(all_coord_x) * (scale + np.sign(max(all_coord_x))),  # and 1*sign(1)*(-2)= -2
        "y_min": min(all_coord_y) * (scale - np.sign(min(all_coord_y))),
        "y_max": max(all_coord_y) * (scale + np.sign(max(all_coord_y))),
    }

    border_y_start = 1
    border_x_start = 1
    border_shift_x = 0.1  # Unstable components
    border_shift_y = 0.1
    if abs(border['y_min']) < abs(border['y_max']):
        border_y_start = 0
    if abs(border['x_min']) < abs(border['x_max']):
        border_x_start = 0
    # titles of axes
    annotation_titles = [
        go.layout.Annotation(
            x=1.10,
            y=abs(min(abs(border['y_min']), abs(border['y_max'])) /
                  (abs(border['y_min']) + abs(border['y_max'])) - border_y_start),
            showarrow=False,
            text=title_x,
            xref="paper",
            yref="paper"
        ),
        go.layout.Annotation(
            x=abs(min(abs(border['x_min']), abs(border['x_max'])) /
                  (abs(border['x_min']) + abs(border['x_max'])) - border_x_start),
            y=1.07,
            showarrow=False,
            text=title_y,
            xref="paper",
            yref="paper"
        )
    ]
    click_mode = 'event'

    # pca

    pca_hor_x = []
    pca_hor_y = []
    pca_vert_x = []
    pca_vert_y = []

    pca_res_hor_x = []
    pca_res_hor_y = []
    pca_res_vert_x = []
    pca_res_vert_y = []

    # Statistics
    if selected_dots:
        df_selected_dots = pd.DataFrame(df.loc[selected_dots])
        mean_dot, error_circle = {}, {}
        if is_open_pca:
            for dot in selected_dots:
                pca_hor_x.append(hor_x[dot])
                pca_hor_y.append(hor_y[dot])
                pca_vert_x.append(vert_x[dot])
                pca_vert_y.append(vert_y[dot])

            hor = []
            for i in range(len(pca_hor_x)):
                hor.append([pca_hor_x[i], pca_hor_y[i]])
            hor = np.array(hor)
            pca_res_hor_x, pca_res_hor_y = give_principal_components(hor, data, selected_dots, pca_mode)
            k_hor, b_hor = kb_for_xy(
                pca_res_hor_x[0],
                pca_res_hor_x[1],
                pca_res_hor_y[0],
                pca_res_hor_y[1],
            )
            extra_hor_x = [-1, 1]
            extra_hor_y = give_y_from_x(k_hor, b_hor, extra_hor_x)
            pca_res_hor_x = np.append(pca_res_hor_x, extra_hor_x)
            pca_res_hor_y = np.append(pca_res_hor_y, extra_hor_y)

            vert = []
            for i in range(len(pca_hor_x)):
                vert.append([pca_vert_x[i], pca_vert_y[i]])
            vert = np.array(vert)
            pca_res_vert_x, pca_res_vert_y = give_principal_components(vert, data, selected_dots, pca_mode)
            k_vert, b_vert = kb_for_xy(
                pca_res_vert_x[0],
                pca_res_vert_x[1],
                pca_res_vert_y[0],
                pca_res_vert_y[1],
            )
            extra_vert_x = [-1, 1]
            extra_vert_y = give_y_from_x(k_vert, b_vert, extra_vert_x)
            pca_res_vert_x = np.append(pca_res_vert_x, extra_vert_x)
            pca_res_vert_y = np.append(pca_res_vert_y, extra_vert_y)

            x_sol, y_sol = xy_solution(k_hor, b_hor, k_vert, b_vert)

            graph_data.append(graph_data_elem_cartesian(pca_hor_x, pca_hor_y, 'markers',
                                                        dots_size + 6, marker_symbol, '#119DFF', 0.5, None, None, df))
            graph_data.append(graph_data_elem_cartesian(pca_vert_x, pca_vert_y, 'markers',
                                                        dots_size + 6, marker_symbol, '   ', 0.5, None, None, df))
            graph_data.append(graph_data_elem_cartesian(pca_res_hor_x, pca_res_hor_y, 'lines',
                                                        None, None, '#119DFF', None, None, None, df))
            graph_data.append(graph_data_elem_cartesian(pca_res_vert_x, pca_res_vert_y, 'lines',
                                                        None, None, '#9933FF', None, None, None, df))
            graph_data.append(graph_data_elem_cartesian([x_sol], [y_sol], "markers",
                                                        dots_size, marker_symbol, '#119DFF', 1, None, None, df))
    return {
        'data': graph_data,
        'layout': go.Layout(
            font=dict(
                family="Times New Roman",
                size=18,
                color="black"
            ),
            showlegend=False,
            template="presentation",
            margin=margin_scatter_2d,
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zerolinewidth=1.5,
                zerolinecolor='black',
                zeroline=True,
                range=[border['x_min'], border['x_max']],
                scaleratio=1,
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zerolinewidth=1.5,
                zerolinecolor='black',
                zeroline=True,
                range=[border['y_min'], border['y_max']],
                scaleanchor="x",
                scaleratio=1,
            ),
            annotations=annotation_titles,
            clickmode=click_mode
        )
    }


@app.callback(
    dash.dependencies.Output('allCharts-scatter-pmd', 'children'),
    [dash.dependencies.Input("modal-3-in-1", "is_open"),
     dash.dependencies.Input('polar-chart', 'figure'),
     dash.dependencies.Input('mag-chart', 'figure'),
     dash.dependencies.Input('zyid-chart', 'figure'),
     ]
)
def update_multi_chart(create_multi_plot, polar_chart, intensity_chart, zyid_chart):
    if create_multi_plot:
        fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'xy'}, {'type': 'polar'}, {'type': 'xy'}]],
                            print_grid=False, shared_yaxes=False, shared_xaxes=False)
        for data in polar_chart['data']:
            fig.append_trace(data, row=1, col=2)
        for data in intensity_chart['data']:
            fig.append_trace(data, row=1, col=1)
        for data in zyid_chart['data']:
            fig.append_trace(data, row=1, col=3)

        fig.update_xaxes(intensity_chart['layout']['xaxis'], row=1, col=1)
        fig.update_yaxes(intensity_chart['layout']['yaxis'], row=1, col=1)
        fig.update_xaxes(zyid_chart['layout']['xaxis'], row=1, col=3)
        fig.update_yaxes(zyid_chart['layout']['yaxis'], row=1, col=3)

        intensity_chart['layout']['annotations'][0]['x'] = 0.3
        intensity_chart['layout']['annotations'][1]['x'] = -0.02
        zyid_chart['layout']['annotations'][0]['x'] = 1.025
        zyid_chart['layout']['annotations'][1]['x'] = (2 + zyid_chart['layout']['annotations'][1]['x']) / 3 + 0.04
        all_annotations = intensity_chart['layout']['annotations'] + zyid_chart['layout']['annotations']

        fig.update_layout(template="none", annotations=all_annotations)
        fig.update_layout(polar_chart['layout'])
        # fig.update_layout(intensity_chart['layout'])
        return (
            dcc.Graph(
                id="allCharts-pmd",
                figure=fig,
                config=chart_config,
                style={
                    'width': '100%'
                }
            ),
        )
        #
        # return fig


@app.callback(
    [Output('pca-stat-result', 'children'),
     Output('halls-stat-result', 'children'),
     Output('fisher-stat-result', 'children')],
    [Input('demag-table-data', 'data'),
     Input('demag-table-data', 'selected_rows'),
     Input('pca-mode', 'value'),
     Input("halls-mode", "value"),
     Input("pca-collapse", "is_open"),
     Input("remag-circ-collapse", "is_open"),
     Input("fisher-collapse", "is_open"), ],
)
def stat_result(data, selected_dots, pca_mode, halls_mode, is_open_pca, is_open_circ, is_open_fisher):
    if selected_dots and data:
        df = pd.DataFrame(data)
        if "CODE" not in df.columns and "Steprange" not in df.columns:
            for i in df.columns:
                df[i] = pd.to_numeric(df[i])

        if is_open_pca:
            Ig, Dg, MADg = pca(df, selected_dots, "geographic", pca_mode)
            Is, Ds, MADs = pca(df, selected_dots, "stratigraphic", pca_mode)
            return (
                html.P(
                    "Dg: " + str(round(Dg, 1)) + " Ig: " + str(round(Ig, 1)) + " MADg: " + str(
                        round(MADg, 1)) +
                    " Ds: " + str(round(Ds, 1)) + " Is: " + str(round(Is, 1)) + " MADs: " + str(
                        round(MADs, 1))
                    ,
                    className="text-center"
                ),
                None, None
            )
        if is_open_circ:
            Ig, Dg, MADg = pca(df, selected_dots, "geographic", halls_mode)
            Is, Ds, MADs = pca(df, selected_dots, "stratigraphic", halls_mode)
            return (
                None,
                html.P(
                    "Dg: " + str(round(Dg, 1)) + " Ig: " + str(round(Ig, 1)) + " a95g: " + str(
                        round(MADg, 1)) +
                    " Ds: " + str(round(Ds, 1)) + " Is: " + str(round(Is, 1)) + " a95s: " + str(
                        round(MADs, 1)),
                    className="text-center"
                ),
                None
            )
        if is_open_fisher:
            a95g, kg, rg, Dg, Ig, xg, yg, zg = fisher_stat(df, selected_dots, "Geographic")
            a95s, ks, rs, Ds, Is, xs, ys, zs = fisher_stat(df, selected_dots, "Geographic")
            return (
                None, None,
                (
                    html.P(
                        "Dg: " + str(round(Dg, 1)) + " Ig: " + str(round(Ig, 1)) +
                        " a95g: " + str(round(a95g, 1)) + " Kg: " + str(round(kg, 1)),
                        className="text-center"
                    ),
                    html.P(
                        " Ds: " + str(round(Ds, 1)) + " Is: " + str(round(Is, 1)) +
                        " a95s: " + str(round(a95s, 1)) + " Ks: " + str(round(ks, 1)),
                        className="text-center"
                    ),
                )
            )
    return [None, None, None]


@app.callback(
    [Output('pca-table-data', 'data'),
     Output('halls-table-data', 'data'),
     Output('fisher-table-data', 'data')],
    [Input("pca-add-button", "n_clicks"),
     Input("halls-add-button", "n_clicks"),
     Input("fisher-add-button", "n_clicks"), ],
    [State('demag-table-data', 'data'),
     State('demag-table-data', 'selected_rows'),
     State('pca-mode', 'value'),
     State('halls-mode', 'value'),
     State("pca-collapse", "is_open"),
     State("remag-circ-collapse", "is_open"),
     State("fisher-collapse", "is_open"),
     State('pca-table-data', 'data'),
     State('pca-table-data', 'columns'),
     State('halls-table-data', 'data'),
     State('halls-table-data', 'columns'),
     State('fisher-table-data', 'data'),
     State('fisher-table-data', 'columns'),
     State('upload-data', 'filename')]
)
def statistics_tables(
        pca_clicks, halls_clicks, fisher_clicks,
        data, selected_dots, pca_mode, halls_mode,
        is_open_pca, is_open_circ, is_open_fisher,
        pca_rows, pca_columns, halls_rows,
        halls_columns, fisher_rows, fisher_columns,
        name,
):
    if selected_dots and data:
        df = pd.DataFrame(data)
        if "CODE" not in df.columns and "Steprange" not in df.columns:
            for i in df.columns:
                df[i] = pd.to_numeric(df[i])

        fcn = "T"  # first column name
        if "M" in data[0]:
            fcn = "M"
        steprange = "site_avg"
        if "CODE" not in df.columns and "Steprange" not in df.columns:
            steprange = fcn + str(df[fcn][min(selected_dots)]) + "-" + fcn + str(df[fcn][max(selected_dots)])
        if is_open_pca:
            Ig_min, Dg_min, a95g_min, Ig_max, Dg_max, a95g_max = bingham_stat(df, selected_dots, "Geographic", pca_mode)
            Is_min, Ds_min, a95s_min, Is_max, Ds_max, a95s_max = bingham_stat(df, selected_dots, "Stratigraphic",
                                                                              pca_mode)
            new_data = [name, steprange, len(selected_dots) + 1,
                        round(Dg_max, 1), round(Ig_max, 1), round(a95g_max, 1),
                        round(Ds_max, 1), round(Is_max, 1), round(a95s_max, 1)]
            if pca_clicks is not None:
                pca_rows.append({col['id']: new_data[i] for i, col in enumerate(pca_columns)})
        if is_open_circ:
            Ig_min, Dg_min, a95g_min, Ig_max, Dg_max, a95g_max = bingham_stat(df, selected_dots, "Geographic",
                                                                              halls_mode)
            Is_min, Ds_min, a95s_min, Is_max, Ds_max, a95s_max = bingham_stat(df, selected_dots, "Stratigraphic",
                                                                              halls_mode)
            new_data = [name, steprange, len(selected_dots) + 1,
                        round(Dg_min, 1), round(Ig_min, 1), round(a95g_min, 1),
                        round(Ds_min, 1), round(Is_min, 1), round(a95s_min, 1)]
            if halls_clicks is not None:
                halls_rows.append({col['id']: new_data[i] for i, col in enumerate(halls_columns)})
        if is_open_fisher:
            a95g, kg, rg, Dg, Ig, xg, yg, zg = fisher_stat(df, selected_dots, "Geographic")
            a95s, ks, rs, Ds, Is, xs, ys, zs = fisher_stat(df, selected_dots, "Geographic")
            new_data = [name, steprange, len(selected_dots) + 1,
                        round(Dg, 1), round(Ig, 1), round(kg, 1), round(a95g, 1),
                        round(Ds, 1), round(Is, 1), round(ks, 1), round(a95s, 1)]
            if fisher_clicks is not None:
                fisher_rows.append({col['id']: new_data[i] for i, col in enumerate(fisher_columns)})
    return pca_rows, halls_rows, fisher_rows


def annot_dots_list(data):
    df = pd.DataFrame(data)
    if df.empty:
        return [{'label': '', 'value': 'None'}]
    labels = create_dots_list(data, 'dots-with-annotation')
    return labels


app.callback(
    dash.dependencies.Output('mag-dots-annots', 'options'),
    [dash.dependencies.Input('demag-table-data', 'data')]
)(annot_dots_list)

app.callback(
    dash.dependencies.Output('polar-dots-annots', 'options'),
    [dash.dependencies.Input('demag-table-data', 'data')]
)(annot_dots_list)

app.callback(
    dash.dependencies.Output('zyid-dots-annots', 'options'),
    [dash.dependencies.Input('demag-table-data', 'data')]
)(annot_dots_list)
