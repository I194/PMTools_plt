# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table

import plotly.graph_objs as go

import pandas as pd
import math
import numpy as np

import base64
import io, os

from templates.app import app

# from templates.pages.pmd_charts import create_pdf_copy

dff = pd.DataFrame(
            {'ID': [], 'CODE': [], 'STEPRANGE': [], 'N': [], 'Dg': [], 'Ig': [],
             'Ds': [], 'Is': [], 'a95': [], 'COMMENT': []})


def transform_data(raw_table, file_extension):
    if file_extension == ".pmm" or file_extension == ".PMM":
        tmp_data = raw_table
        tmp_data.to_csv("TMP")

        data = pd.read_csv("TMP", header=None)

        # create DataFrame

        tmp_tb = []
        for i in data[1]:
            tmp_tb.append(i.split(','))
        data = pd.DataFrame(tmp_tb)

        # cleaning DataFrame from extra columns

        if len(data.columns) > 12:
            for i in range(12, len(data.columns), 1):
                data.drop(data.columns[[i]], axis='columns', inplace=True)

        # cleaning DataFrame from extra whitespaces

        for column in data:
            for i in range(0, len(data[column]), 1):
                data[column][i] = data[column][i].strip()

        # cleaning second col from extra letters

        second_col_name = data[2][1][0]
        for id, item in enumerate(data[2]):
            data[2][id] = data[2][id].replace(second_col_name, "")

        # renaming DataFrame columns

        data.rename(
            columns={0: "ID",
                     1: "CODE",
                     2: "STEPRANGE " + second_col_name,
                     3: "N",
                     4: "Dg",
                     5: "Ig",
                     6: "kg",
                     7: "a95g",
                     8: "Ds",
                     9: "Is",
                     10: "ks",
                     11: "a95s"
                     },
            inplace=True)

        # data to numeric format

        for i in data.columns:
            if i == "ID" or i == "CODE" or i == "STEPRANGE " + second_col_name:
                continue
            data[i] = pd.to_numeric(data[i])
    elif file_extension == ".dir" or file_extension == ".DIR":
        tmp_data = raw_table
        tmp_data.to_csv("TMP")

        data = pd.read_csv("TMP", header=None)

        # create DataFrame

        tmp_tb = []
        for i in data[1]:
            tmp_tb.append(i.split())
        data = pd.DataFrame(tmp_tb)

        # cleaning DataFrame from bad rows with unresolved symbols

        if not data[0][len(data) - 1].isalnum():
            data.drop(len(data) - 1, axis=0, inplace=True)

        # cleaning second col from extra letters

        second_col_name = data[2][1][0]
        for id, item in enumerate(data[2]):
            data[2][id] = data[2][id].replace(second_col_name, "")

        # renaming DataFrame columns

        data.rename(
            columns={0: "ID",
                     1: "CODE",
                     2: "STEPRANGE " + second_col_name,
                     3: "N",
                     4: "Dg",
                     5: "Ig",
                     6: "Ds",
                     7: "Is",
                     8: "a95",
                     9: "COMMENT"
                     },
            inplace=True)

        # data to numeric format

        for i in data.columns:
            if i == "ID" or i == "CODE" or i == "STEPRANGE " + second_col_name or i == "COMMENT":
                continue
            data[i] = pd.to_numeric(data[i])
    else:
        data = pd.DataFrame()

    # Analogue of .DIR or .pmm "ID", difference is that nums start from 0
    nums = []
    for i in range(0, len(data), 1):
        nums.append(i+1)
    data.insert(0, "№", nums)

    return data


def parse_contents_for_plot_dt(contents, filename, show_fisher):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    filename, file_extension = os.path.splitext(filename)

    if file_extension != ".csv":
        raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', skiprows=3)
        if file_extension == ".dir" or file_extension == ".DIR":
            raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')
        df = transform_data(raw_df, file_extension)
    else:
        raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=',')
        df = pd.DataFrame(raw_df)
        nums = []
        for i in range(0, len(df), 1):
            nums.append(i + 1)
        df.insert(0, "id", nums)

    if show_fisher:
        return html.Div([
            html.H6('Current file is ' + filename),

            dash_table.DataTable(
                id="datatable-pmm-dir",
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                row_selectable="multi",
                selected_rows=np.arange(0, len(df), 1),
                style_header={
                    'backgroundColor': '#F5FFFA',
                    'fontWeight': 'bold',

                }
            ),
        ])
    else:
        return html.Div([
            html.H6('Current file is ' + filename),

            dash_table.DataTable(
                id="datatable-pmm-dir",
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                style_header={
                    'backgroundColor': '#F5FFFA',
                    'fontWeight': 'bold',

                }
            ),
        ])


def create_dots_list(data):
    df = pd.DataFrame(data)
    labels = list()

    for i in range(len(df["ID"])):
        labels.append({'label': str(int(df["№"][i])), 'value': df["№"][i]})

    return labels


def give_a95_k_rm(data, system):
    col_D = "Dg"
    col_I = "Ig"

    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"
    x = 0
    y = 0
    z = 0
    a95 = 0  # the radius of the confidence circle
    Rs = 1  # average vector always has the length of 1 because all vectors have the same length of 1
    n = len(data)
    for i in data["№"]:
        rI = math.radians(float(data[col_I][i-1]))
        rD = math.radians(float(data[col_D][i-1]))
        # because of all vectors is have the length of 1, ipar <> 1 is False and then ri is always 1:
        x += math.cos(rI) * math.cos(rD)
        y += math.cos(rI) * math.sin(rD)
        z += math.sin(rI)  # because all vectors have a length of 1
    # xyzDIR
    Rs = math.sqrt(x * x + y * y + z * z)
    Dm = math.degrees(math.acos(x / math.sqrt(x * x + y * y)))
    if y < 0: Dm = -Dm
    dr = Dm - 360 * int(Dm / 360)
    if dr < 0: dr += 360
    Dm = dr
    Im = math.degrees(math.asin(z / Rs))
    # normalized x, y, z
    x /= Rs
    y /= Rs
    z /= Rs
    # because of all vectors is have the length of 1, ipar <= 1 is True and then:
    Rm = Rs / n  # normalized length of the average vector
    k = (n - 1) / (n - Rs)
    if k < 4:
        if Rm <= 0.001:
            k = 3 * Rm
            a95 = 180
            return a95, k, Rs, Dm, Im, x, y, z
        k = 20
        while True:
            cth = (1 + math.exp(-2 * k) / (1 - math.exp(-2 * k)))
            k1 = 1 / (cth - Rm)
            # print(str(cth) + "____" + str(k1) + "<-----")
            if abs(k - k1) <= 0.01:
                k = k1
                break
            k = k1
        a95 = math.degrees(math.acos(1 + math.log(1 - 0.95 * (1 - math.exp(-2 * k))) / k))
        return a95, k, Rs, Dm, Im, x, y, z
    a95 = math.degrees(math.acos(1 - 2.9957 / (n * k)))
    return a95, k, Rs, Dm, Im, x, y, z


def xyz_to_dir(x, y, z):
    Rs = np.sqrt(x * x + y * y + z * z)
    D = np.degrees(np.arccos(x / np.sqrt(x * x + y * y)))
    if y < 0:
        D = -D
    dr = D - 360 * int(D / 360)
    if dr < 0:
        dr += 360
    D = dr
    I = np.degrees(np.arcsin(z / Rs))
    return I, D

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'rgba(17, 157, 255, .50)',
    'color': 'white',
    'padding': '6px'
}
radio_tab_style = {
    'backgroundColor': 'white',
    'padding': '6px'
}
layout = [
    html.Div(
        [
            html.Div(
                className="twelve columns card",
                children=[
                    dcc.Upload(
                        id='upload-data-pmm-dir',
                        className="upload-container",
                        children=html.Div([
                            html.A('Select'),
                            ' or drop file (only .DIR or .pmm)'
                        ]),
                        multiple=False
                    ),
                ]
            ),

            html.Div(
                html.Div(
                    className="four columns card",
                    children=[
                        html.Div(
                            html.Div(
                                className="bg-white user-control",
                                style={
                                    # because chart and user-controls in one card
                                    'margin-bottom': '16px'
                                },
                                children=[
                                    dcc.Tabs(
                                        id='system',
                                        value="geographic",
                                        children=[
                                            dcc.Tab(
                                                label="geographic",
                                                value="geographic",
                                                className="radio-tab",
                                                style=radio_tab_style,
                                                selected_style=tab_selected_style
                                            ),
                                            dcc.Tab(
                                                label="stratigraphic",
                                                value="stratigraphic",
                                                className="radio-tab",
                                                style=radio_tab_style,
                                                selected_style=tab_selected_style
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        className="row padding-top-bot",
                                        children=[
                                            html.Div(
                                                className="nine columns",
                                                children=[
                                                    html.Abbr(
                                                        className="pretty-abbr",
                                                        title="Automatically creating pdf copy of chart after downloading this chart.",
                                                        children=[
                                                            dcc.Markdown(
                                                                className="pretty-markdown-left",
                                                                children=[
                                                                    "**Auto-PDF**"
                                                                ]
                                                            )
                                                        ]
                                                    ),

                                                ],
                                                style={
                                                    "padding-top":"6px",
                                                }
                                            ),
                                            html.Div(
                                                className="three columns",
                                                children=[
                                                    daq.BooleanSwitch(
                                                        id="pdf-copy",
                                                        on=True,
                                                    ),
                                                ],
                                                style={
                                                    "padding-top":"6px",
                                                }
                                            ),
                                            dcc.Markdown(
                                                id="pdf-copy-output",
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        className="row padding-top-bot",
                                        children=[
                                            html.Div(
                                                className="four columns centering",
                                                children=[
                                                    dcc.Markdown("**Dots**"),
                                                ],
                                                style={
                                                    "padding-top":"6px",
                                                }
                                            ),
                                            html.Div(
                                                className="four columns",
                                                children=[
                                                    daq.NumericInput(
                                                        id='dots-size',
                                                        min=1,
                                                        max=12,
                                                        value=8,
                                                        size=100,
                                                    )
                                                ],
                                                style={
                                                    "align":"center",
                                                }
                                            ),
                                            html.Div(
                                                className="four columns",
                                                children=[
                                                    dcc.Dropdown(
                                                        id='marker-symbol',
                                                        options=[
                                                            {'label': 'Circle', 'value': 'circle'},
                                                            {'label': 'Square', 'value': 'square'},
                                                            {'label': 'Triangle', 'value': 'triangle-up'},
                                                            {'label': 'Star', 'value': 'star'}
                                                        ],
                                                        value='circle'
                                                    )
                                                ],
                                                style={
                                                    "padding-top":"1.4px",
                                                }
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        className="row padding-top-bot",
                                        children=[
                                            html.Div(
                                                className="four columns centering",
                                                children=[
                                                    dcc.Markdown("**Annotations**"),
                                                ],
                                                style={
                                                    "padding-top":"6px",
                                                }
                                            ),
                                            html.Div(
                                                className="four columns",
                                                children=[
                                                    daq.NumericInput(
                                                        id='font-size',
                                                        min=6,
                                                        max=26,
                                                        value=16,
                                                        size=100,
                                                    )
                                                ],
                                                style={
                                                    "align":"center",
                                                }
                                            ),
                                            html.Div(
                                                className="four columns",
                                                children=[
                                                    daq.BooleanSwitch(
                                                        id="show-hide-annotations",
                                                        on=False,
                                                    ),
                                                ],
                                                style={
                                                    "padding-top":"6px",
                                                }
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        className="padding-top-bot",
                                        children=[
                                            dcc.Dropdown(
                                                id='text-position-polar-pmm-dir',
                                                options=[
                                                    {'label': 'Top left', 'value': 'top left'},
                                                    {'label': 'Top center', 'value': 'top center'},
                                                    {'label': 'Top right', 'value': 'top right'},
                                                    {'label': 'Middle left', 'value': 'middle left'},
                                                    {'label': 'Middle', 'value': 'middle center'},
                                                    {'label': 'Middle right', 'value': 'middle right'},
                                                    {'label': 'Bottom left', 'value': 'bottom left'},
                                                    {'label': 'Bottom center', 'value': 'bottom center'},
                                                    {'label': 'Bottom right', 'value': 'bottom right'}
                                                ],
                                                value='top left',
                                                style={
                                                    # 'width': '100%',
                                                    'margin-top': '5px',
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),

                        html.Div(
                            className="bg-white chart",
                            children=[
                                dcc.Graph(
                                    id='polar-scatter-pm-pmm-dir',
                                    config={
                                        'toImageButtonOptions': {
                                            'format': 'svg'
                                        },
                                        'showLink': True,
                                        'displaylogo': False,
                                        'scrollZoom': True,
                                        'displayModeBar': True
                                    },
                                ),
                            ]
                        )
                    ]
                ),
            ),

            html.Div(
                className="eight columns card",
                children=[
                    html.Div(
                        className="bg-white user-control",
                        style={
                            'margin-bottom': '16px'
                        },
                        children=[
                            html.Div(
                                className="row",
                                children=[
                                    html.Button(
                                        'Fisher',
                                        id='fisher-button',
                                        className="choose-button"
                                    ),
                                    dcc.Markdown(
                                        id="fisher-data",
                                        children='',
                                        style={
                                            "text-transform":"none",
                                            "font-family": "Roboto",
                                            "font-weight": "500",
                                            "font-size": "16px",
                                            "text-align": "center",
                                            "border-bottom": "1px solid #C8D4E3",
                                            "border-top": "1px solid #C8D4E3",
                                            "padding-top":"6px",
                                            "margin-top": "10px",
                                        }
                                    )
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="bg-white table",
                        id='output-datatable-pmm-dir',
                        children=[
                            dash_table.DataTable(
                                id="datatable-pmm-dir",
                                data=dff.to_dict('records'),
                                columns=[{'name': i, 'id': i} for i in dff.columns],
                                style_header={
                                    'backgroundColor': '#F5FFFA',
                                    'fontWeight': 'bold',
                                }
                            )
                        ]
                    ),
                ]
            ),
        ]
    )
]


@app.callback(
    dash.dependencies.Output('polar-scatter-pm-pmm-dir', 'figure'),
    [dash.dependencies.Input('system', 'value'),
     dash.dependencies.Input('text-position-polar-pmm-dir', 'value'),
     dash.dependencies.Input('datatable-pmm-dir', 'data'),
     dash.dependencies.Input('show-hide-annotations', 'on'),
     dash.dependencies.Input('font-size', 'value'),
     dash.dependencies.Input('dots-size', 'value'),
     dash.dependencies.Input('marker-symbol', 'value'),
     dash.dependencies.Input('fisher-button', 'n_clicks'),
     dash.dependencies.Input('datatable-pmm-dir', 'selected_rows')]
)
def update_graph_polar_pm(system, text_position, data, show_annotations,
                          font_size, dots_size, marker_symbol,
                          n_clicks, selected_rows):
        df = pd.DataFrame(data)

        if selected_rows is None:
            selected_rows = np.arange(0,len(df),1)
        df = pd.DataFrame(df.loc[selected_rows])
        axdots_r = []
        axdots_a = []
        for i in [0, 90, 180, 270]:
            for j in range(10, 90, 10):
                axdots_r.append(j)
                axdots_a.append(i)

        if df.empty:
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
                        size=25,
                        color="black"
                    ),
                    showlegend=False,
                    polar=dict(
                        angularaxis=dict(
                            tickfont=dict(
                                size=25,
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

        for i in df["№"]:
            if df[col_I][i-1] < 0:
                values_neg.append(abs(df[col_I][i-1]+90))
                values_abs.append(abs(df[col_I][i-1]+90))
                angles_neg.append(df[col_D][i-1])
            else:
                values_pos.append(abs(df[col_I][i-1]-90))
                values_abs.append(abs(df[col_I][i-1]-90))
                angles_pos.append(df[col_D][i-1])

        dots_with_annotation_r = list()
        dots_with_annotation_t = list()
        dots_with_annotation_u = list()

        if show_annotations:
            dots_with_annotation_r = values_abs
            dots_with_annotation_t = angles_abs
            for i in df["№"]:
                dots_with_annotation_u.append(str(df["ID"][i-1]))

        a95, k, Rs, Dm, Im, x_0, y_0, z_0 = give_a95_k_rm(df, system)

        circle_i = []
        circle_d = []
        circle_x = []
        circle_y = []
        circle_z = []

        a95_norm = a95 / 90

        mean_vector_i = []
        mean_vector_d = []
        mean_marker = dict(
            color='#119DFF',
            size=dots_size,
            symbol=marker_symbol
        )
        if Im < 0:
            mean_marker = dict(
                color='white',
                size=dots_size,
                symbol=marker_symbol,
                line=dict(
                    color='#119DFF',
                    width=1
                )
            )
        if n_clicks is not None:
            if n_clicks%2 == 1:
                if Im <= 0:
                    Im += 90
                else:
                    Im -= 90
                mean_vector_i = [abs(Im)]
                mean_vector_d = [Dm]
                step = a95_norm/360
                print(x_0, y_0, z_0)
                for z in np.arange(z_0 - a95_norm, z_0 + a95_norm + step, step):
                    k = 1 - z * z_0 - (a95_norm ** 2) / 2
                    D_1 = k ** 2 * x_0 ** 2 - (x_0 ** 2 + y_0 ** 2) * (
                            y_0 ** 2 * z ** 2 + k ** 2 - y_0 ** 2)  # (1-z**2)*(x_0**2 + y_0**2) - (k**2)*(y_0**2)
                    if D_1 < 0:
                        continue

                    x_1 = (k * x_0 + np.sqrt(D_1)) / (x_0 ** 2 + y_0 ** 2)
                    x_2 = (k * x_0 - np.sqrt(D_1)) / (x_0 ** 2 + y_0 ** 2)
                    y_1 = (k - x_1 * x_0) / y_0
                    y_2 = (k - x_2 * x_0) / y_0
                    z_1 = z
                    z_2 = z

                    circle_x.append(x_1)
                    circle_x.append(x_2)
                    circle_y.append(y_1)
                    circle_y.append(y_2)
                    circle_z.append(z_1)
                    circle_z.append(z_2)

                    i, d = xyz_to_dir(x_1, y_1, z_1)
                    if i <= 0:
                        i += 90
                    else:
                        i -= 90
                    circle_i.append(abs(i))
                    circle_d.append(d)
                    i, d = xyz_to_dir(x_2, y_2, z_2)
                    if i <= 0:
                        i += 90
                    else:
                        i -= 90
                    circle_i.append(abs(i))
                    circle_d.append(d)

                circle_i_left = []
                circle_i_right = []
                circle_d_left = []
                circle_d_right = []
                for i in range(0, len(circle_i), 2):
                    circle_i_left.append(circle_i[i])
                    circle_i_right.append(circle_i[i + 1])
                    circle_d_left.append(circle_d[i])
                    circle_d_right.append(circle_d[i + 1])
                circle_i_right.reverse()
                circle_d_right.reverse()
                circle_i = circle_i_left + circle_i_right
                circle_d = circle_d_left + circle_d_right
                circle_i.append(circle_i[0])
                circle_d.append(circle_d[0])

        return {
            'data': [
                # graph structure
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
                ),
                # annotations
                go.Scatterpolar(
                    r=dots_with_annotation_r,
                    theta=dots_with_annotation_t,
                    mode="text",
                    text=dots_with_annotation_u,
                    textposition=text_position,
                    textfont=dict(
                        family='Times New Roman',
                        size=font_size,
                        color='black'
                    )
                ),
                # dots
                go.Scatterpolar(
                    r=values_pos,
                    theta=angles_pos,
                    mode="markers",
                    marker=dict(
                        color='black',
                        size=dots_size,
                        symbol=marker_symbol,
                    ),
                ),
                go.Scatterpolar(
                    r=values_neg,
                    theta=angles_neg,
                    mode="markers",
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
                #  average dot and confidence circle
                go.Scatterpolar(
                    r=mean_vector_i,
                    theta=mean_vector_d,
                    mode="markers",
                    marker=mean_marker
                ),
                go.Scatterpolar(
                    r=circle_i,
                    theta=circle_d,
                    mode="lines",
                    marker=dict(
                        color='#119DFF',
                        size=2,
                    )
                )

            ],
            'layout': go.Layout(
                font=dict(
                    family="Times New Roman",
                    size=25,
                    color="black"
                ),
                showlegend=False,
                polar=dict(
                    angularaxis=dict(
                        tickfont=dict(
                            size=25,
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


@app.callback(dash.dependencies.Output('output-datatable-pmm-dir', 'children'),
    [dash.dependencies.Input('upload-data-pmm-dir', 'contents'),
     dash.dependencies.Input('fisher-button', 'n_clicks')],
    [dash.dependencies.State('upload-data-pmm-dir', 'filename')]
)
def update_output_datatable(list_of_contents, n_clicks, list_of_names):
    if list_of_contents is not None and n_clicks is not None:
        if n_clicks % 2 == 1:
            children = [parse_contents_for_plot_dt(list_of_contents, list_of_names, True)]
        else:
            children = [parse_contents_for_plot_dt(list_of_contents, list_of_names, False)]
        return children
    elif list_of_contents is not None and n_clicks is None:
        children = [parse_contents_for_plot_dt(list_of_contents, list_of_names, False)]
        return children
    else:
        df = pd.DataFrame(
            {'ID': [], 'CODE': [], 'STEPRANGE': [], 'N': [], 'Dg': [], 'Ig': [], 'Ds': [], 'Is': [], 'a95': [], 'COMMENT': []})
        return (
            dash_table.DataTable(
                id="datatable-pmm-dir",
                data=dff.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                style_header={
                    'backgroundColor': '#F5FFFA',
                    'fontWeight': 'bold',
                }
            )
        )


@app.callback(
    dash.dependencies.Output('dots-with-annotation-pmm-dir', 'options'),
    [dash.dependencies.Input('datatable-upload-container-pmm-dir', 'data-pmm-dir')]
)
def update_dots_list(data):
        df = pd.DataFrame(data)
        if df.empty:
            return [{'label': '', 'value': 'None'}]
        labels = create_dots_list(data)

        return labels

@app.callback(
    dash.dependencies.Output('fisher-button', 'style'),
    [dash.dependencies.Input('fisher-button', 'n_clicks')]
)
def fisher_color(n_clicks):
    if n_clicks is not None:
        if n_clicks%2 == 1:
            return {
                "border": "1.5px solid #119dff",
                "background-color": 'rgba(17, 157, 255, .50)'
            }
        return {
            "border": "1.5px solid #119dff",
            "background-color": "white"
        }

@app.callback(
    dash.dependencies.Output('fisher-data', 'children'),
    [dash.dependencies.Input('fisher-button', 'n_clicks'),
     dash.dependencies.Input('datatable-pmm-dir', 'data'),
     dash.dependencies.Input('system', 'value'),
     dash.dependencies.Input('datatable-pmm-dir', 'selected_rows')]
)
def fisher_data(n_clicks, data, system, selected_rows):
    if n_clicks is not None and data:
        df = pd.DataFrame(data)
        if selected_rows is None:
            selected_rows = np.arange(0,len(df),1)
        df = pd.DataFrame(df.loc[selected_rows])
        a95, k, Rs, Dm, Im, x, y, z = give_a95_k_rm(df, system)
        if n_clicks%2 == 1:
            if system == "stratigraphic":
                return (
                        "**Ds** = " + str(round(Dm, 1)) + ";"
                        "    **Is** = " + str(round(Im, 1)) + ";"
                        "    **Ks** = " + str(round(k, 1)) + ";"
                        "  **a95s** = " + str(round(a95, 1))

                )
            else:
                return (
                        "**Dg** = " + str(round(Dm, 1)) + ";"
                        "    **Ig** = " + str(round(Im, 1)) + ";"
                        "    **Kg** = " + str(round(k, 1)) + ";"
                        "  **a95g** = " + str(round(a95, 1))
                )

        return
