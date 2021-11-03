import pandas as pd
import numpy as np

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

import io, base64, os

import plotly.graph_objs as go

from .Statistics import *


def column_cleaner(string):
    while len(string) and not (string[0] >= "0" and string[0] <= "9"):
        string = string[1:]
    return string


def transform_data(raw_table, file_extension):
    extra_data = []
    if file_extension == ".pmd" or file_extension == ".PMD":
        tmp_data = raw_table
        tmp_data.to_csv("TMP")
        data = pd.read_csv("TMP", header=None)

        # delete all before "PAL"

        i = 0
        while True:
            if data.iloc[i][1][:4] == " PAL" or data.iloc[i][1][:4] == "PAL ":
                break
            i += 1
        # additional data, non-table format

        extra_data = data.iloc[i - 1][1].split('   ')
        # code_name = extra_data[0]
        k = 1
        while not bool(extra_data[k]): k += 1
        A = float(extra_data[k].split('=')[1])
        B = float(extra_data[k + 1].split('=')[1])
        S = float(extra_data[k + 2].split('=')[1])
        D = float(extra_data[k + 3].split('=')[1])
        # v = extra_data[5]
        extra_data = [A, B, S, D]
        # delete extra_data from data
        a = []
        for j in range(i + 1):
            a.append(j)
        data.drop(a, axis=0, inplace=True)

        # create DataFrame

        tmp_tb = []
        for i in data[1]:
            tmp_tb.append(i.split())
        data = pd.DataFrame(tmp_tb)

        # checking first col for bad data like "T 20" instead of "T20"

        for i in range(0, len(data), 1):
            if data[0][i].isalpha() and data[len(data.columns) - 1][i] != None:
                for j in range(0, len(data.columns) - 1, 1):
                    data[j][i] += data[j + 1][i]
                    data[j + 1][i] = ''

        # cleaning DataFrame from extra columns

        if len(data.columns) > 10:
            for i in range(10, len(data.columns), 1):
                data.drop(data.columns[[i]], axis='columns', inplace=True)

        # cleaning DataFrame from bad rows with unresolved symbols

        if not data[0][len(data) - 1].isalnum():
            data.drop(len(data) - 1, axis=0, inplace=True)

        # cleaning first column from symbols and create first_col_measure for name this column

        first_col = data[0]
        first_col_measure = "T"
        if data[0][0][0] == "M":
            first_col_measure = "M"
        data[0] = list(map(column_cleaner, first_col))

        # renaming DataFrame columns

        data.rename(
            columns={
                0: first_col_measure,
                1: "X",
                2: "Y",
                3: "Z",
                4: "MAG",
                5: "Dg",
                6: "Ig",
                7: "Ds",
                8: "Is",
                9: "a95"
            },
            inplace=True
        )

        # Data to numeric format

        for i in data.columns:
            data[i] = pd.to_numeric(data[i])

        data['X'] = data['X'].map('{:,.2E}'.format)
        data['Y'] = data['Y'].map('{:,.2E}'.format)
        data['Z'] = data['Z'].map('{:,.2E}'.format)
        data['MAG'] = data['MAG'].map('{:,.2E}'.format)
    elif file_extension == ".pmm" or file_extension == ".PMM":
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
    id = []
    for i in range(0, len(data), 1):
        id.append(i + 1)
    data.insert(0, "id", id)

    # Return data and additional data

    return data, extra_data


def parse_contents_for_plot_dt(contents, filename, for_what, edit_mode):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    filename, file_extension = os.path.splitext(filename)
    extra_data = []
    extra_data_names = ["a", "b", "s", "d"]
    raw_df = None

    if file_extension != ".csv":
        if file_extension == ".pmd" or file_extension == ".PMD":
            raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        if file_extension == ".pmm" or file_extension == ".PMM":
            raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', skiprows=3)
        if file_extension == ".dir" or file_extension == ".DIR":
            raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')
        df, extra_data = transform_data(raw_df, file_extension)
    else:
        raw_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=',')
        df = pd.DataFrame(raw_df)
        nums = []
        for i in range(0, len(df), 1):
            nums.append(i + 1)
        df.insert(0, "id", nums)

    if for_what == "for_table":
        row_selectable= False
        selected_rows = []
        if edit_mode:
            row_selectable = "multi"
            selected_rows = np.arange(0, len(df), 1)
        if extra_data:  # .PMD
            return dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            dash_table.DataTable(
                                id='demag-table-data',
                                data=df.to_dict('records'),
                                columns=[{'name': i, 'id': i} for i in df.columns],
                                row_selectable=row_selectable,
                                selected_rows=selected_rows,
                                editable=True,
                                row_deletable=True,
                                style_table={
                                    'height': '180px',
                                },
                                fixed_rows={'headers': True, 'data': 0},
                            ),
                        ],
                        width=11
                    ),
                    dbc.Col(
                        children=[
                            dash_table.DataTable(
                                id='extra-data-pmd',
                                editable=True,
                                columns=[
                                    {"name": "", "id": "bed_elements"},
                                    {"name": "", "id": "bed_elements_num"},
                                ],
                                data=[
                                    {
                                        "bed_elements": extra_data_names[i],
                                        "bed_elements_num": extra_data[i],
                                    }
                                    for i in range(len(extra_data))
                                ],
                            ),
                        ],
                        width=1
                    )
                ],
            )
        else:  # .PMM and .DIR
            return html.Div(
                dash_table.DataTable(
                    id="demag-table-data",
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    row_selectable=row_selectable,
                    selected_rows=selected_rows,
                    editable=True,
                    row_deletable=True,
                    style_table={
                        'height': '180px',
                    },
                    fixed_rows={'headers': True, 'data': 0},
                ),
            )
    if for_what == "for_extra_data":
        return extra_data


def create_dots_list(data, droplist_name):
    df = pd.DataFrame(data)
    labels = list()

    unit = u"\u00B0"
    first_col_name = 'T'

    if 'M' in data[0]:
        first_col_name = 'M'
        unit = "mT"
    if droplist_name == "dots-with-annotation":
        for i in range(len(df)):
            labels.append(
                {
                    'label': str(df["id"][i]),
                    'value': i
                }
            )

    return labels


def create_orthodromy(data_table, system):
    col_D = "Dg"
    col_I = "Ig"

    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"
    raw_longitudes = data_table[col_D]
    raw_latitudes = data_table[col_I]
    orthodromes_D = []
    orthodromes_I = []

    for i in range(len(data_table) - 1):

        start_longitude = np.radians(raw_longitudes[i])
        start_latitude = np.radians(raw_latitudes[i])
        end_longitude = np.radians(raw_longitudes[i + 1])
        end_latitude = np.radians(raw_latitudes[i + 1])

        reverse = False

        if start_longitude > end_longitude:
            start_longitude, end_longitude = end_longitude, start_longitude
            reverse = True

        if np.degrees(end_longitude) - np.degrees(start_longitude) > 180:
            reverse = not reverse
            start_longitude, end_longitude = end_longitude, start_longitude + 2 * np.pi

        orthodromy_D = []
        orthodromy_I = []

        for longitude in np.arange(start_longitude, end_longitude + abs(start_longitude - end_longitude) / 100, abs(start_longitude - end_longitude) / 100):
            longitude %= 2 * np.pi

            latitude = np.degrees(
                np.arctan(
                    ((np.tan(start_latitude) * np.sin(end_longitude - longitude)) /
                     (np.sin(end_longitude - start_longitude))) +
                    ((np.tan(end_latitude) * np.sin(longitude - start_longitude)) /
                     (np.sin(end_longitude - start_longitude)))
                )
            )

            longitude = np.degrees(longitude)

            orthodromy_D.append(longitude)
            orthodromy_I.append(abs(abs(latitude) - 90))

        if reverse:
            orthodromy_D = orthodromy_D[::-1]
        orthodromes_D.append(orthodromy_D)
        orthodromes_I.append(orthodromy_I)

    return (
        orthodromes_D, orthodromes_I
    )


def graph_data_elem_cartesian(x, y, mode, size, symbol, color, opacity, text, text_position, data):
    if mode == "markers":
        return (
            go.Scatter(
                x=x,
                y=y,
                mode=mode,
                hovertemplate='<b>%{text}</b>',
                text=['id: {}'.format(data["id"][i]) for i in range(len(data))],
                marker=dict(
                    color=color,
                    size=size,
                    symbol=symbol,
                    opacity=opacity
                )
            )
        )
    if mode == "lines":
        return (
            go.Scatter(
                x=x,
                y=y,
                mode=mode,
                line=dict(
                    color=color,
                    width=1,
                )
            )
        )
    if mode == "lines+markers":
        return (
            go.Scatter(
                x=x,
                y=y,
                mode=mode,
                hovertemplate='<b>%{text}</b>',
                text=['id: {}'.format(data["id"][i]) for i in range(len(data))],
                marker=dict(
                    color=color[0],
                    size=size,
                    line=dict(
                        color=color[1],
                        width=1
                    ),
                    symbol=symbol
                ),
                line=dict(
                    color=color[2],
                    width=1
                )
            ),
        )
    if mode == "text":
        return (
            go.Scatter(
                x=x,
                y=y,
                mode=mode,
                text=text,
                textposition=text_position,
                textfont=dict(
                    family='Times New Roman',
                    size=16,
                    color=color
                )
            )
        )


def graph_data_elem_polar(r, theta, mode, size, symbol, color, text, text_position, data):
    if mode == "markers":
        return go.Scatterpolar(
            r=r,
            theta=theta,
            mode=mode,
            #hovertext=data["id"],
            hovertemplate='<b>%{text}</b>',
            text=['id: {}'.format(data["id"][i]) for i in range(len(data))],
            marker=dict(
                color=color[0],
                size=size,
                symbol=symbol,
                line=dict(
                    color=color[1],
                    width=1
                ),
            )
        )
    if mode == "lines":
        return go.Scatterpolar(
            r=r,
            theta=theta,
            mode=mode,
            line=dict(
                color=color,
                width=1
            )
        )
    if mode == "text":
        return go.Scatterpolar(
            r=r,
            theta=theta,
            mode=mode,
            text=text,
            textposition=text_position,
            textfont=dict(
                family='Times New Roman',
                size=16,
                color='black',
            )
        )


def draw_error_circle(Dm, Im, a95, x_0, y_0, z_0, dots_size, marker_symbol, data):
    # Сalculating the coordinates of the trust circle
    circle_i = []
    circle_d = []

    a95_norm = a95 * np.sqrt(2) / 90
    step = a95_norm / 1024
    for z in np.arange(z_0 - a95_norm, z_0 + a95_norm + 100*step, step):
        coef = 1 - z * z_0 - (a95_norm ** 2) / 2
        D_1 = coef ** 2 * x_0 ** 2 - (x_0 ** 2 + y_0 ** 2) * (
                y_0 ** 2 * z ** 2 + coef ** 2 - y_0 ** 2)  # (1-z**2)*(x_0**2 + y_0**2) - (coef**2)*(y_0**2)
        if D_1 < 0:
            continue

        x_1 = (coef * x_0 + np.sqrt(D_1)) / (x_0 ** 2 + y_0 ** 2)
        x_2 = (coef * x_0 - np.sqrt(D_1)) / (x_0 ** 2 + y_0 ** 2)
        y_1 = (coef - x_1 * x_0) / y_0
        y_2 = (coef - x_2 * x_0) / y_0
        z_1 = z
        z_2 = z

        i_1, d_1 = xyz_to_dir(x_1, y_1, z_1, "single")
        i_2, d_2 = xyz_to_dir(x_2, y_2, z_2, "single")
        i_12 = [i_1, i_2]
        d_12 = [d_1, d_2]
        for j in range(2):
            if i_12[j] < 0:
                i_12[j] += 90
            else:
                i_12[j] -= 90
            circle_i.append(abs(i_12[j]))
        circle_d.extend(d_12)

    # Да, это ужасный код, я знаю. Зато работает
    circle_i_left, circle_i_right, circle_d_left, circle_d_right = [], [], [], []
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



    # D0, I0, = Dm, Im
    # if I0 < 0:
    #     I0 = abs(-90 - I0)
    # else:
    #     I0 = 90 - I0
    # for i in range(0, 360, 1):
    #     i = np.radians(i)
    #     circle_d.append(D0 + a95 * np.cos(i))
    #     circle_i.append(I0 + a95 * np.sin(i))

    # Trust circle settings
    trust_circle = graph_data_elem_polar(circle_i, circle_d, "lines", None, None, "#119dff", None, None, data)

    # Mean dot settings
    mean_vector_i = []
    mean_vector_d = []
    mean_dot = {}
    # Because plotly polar charts start from I=0 in center and end with I=90 in border
    mean_vector_d = [Dm]
    if Im < 0:
        mean_vector_i = [abs(Im + 90)]
        mean_dot = graph_data_elem_polar(mean_vector_i, mean_vector_d, "markers", dots_size, marker_symbol,
                                         ["white", "#119dff"], None, None, data)
    else:
        mean_vector_i = [abs(Im - 90)]
        mean_dot = graph_data_elem_polar(mean_vector_i, mean_vector_d, "markers", dots_size, marker_symbol,
                                         ["#119dff", "#119dff"], None, None, data)

    return mean_dot, trust_circle




def draw_fisher_mean(data, selected_dots, system, dots_size, marker_symbol):
    a95, k, Rs, Dm, Im, x_0, y_0, z_0 = fisher_stat(data, selected_dots, system)
    mean_dot, trust_circle = draw_error_circle(Dm, Im, a95, x_0, y_0, z_0, dots_size, marker_symbol, data)
    return mean_dot, trust_circle


def draw_halls_mean(data, selected_dots, system, dots_size, marker_symbol, mode):
    # Look at Halls, 1976 (doi:10.1111/j.1365-246x.1976.tb00327.x)
    # I_min, D_min, a95_min, I_max, D_max, a95_max = bingham_stat(data, selected_dots, system, mode)
    I, D, MAD = pca(data, selected_dots, system, mode)
    x0, y0, z0 = dir_to_xyz(D, I, 1)

    # Rs = np.sqrt(x0 ** 2 + y0 ** 2 + z0 ** 2)
    # x0 /= Rs
    # y0 /= Rs
    # z0 /= Rs

    mean_dot, trust_circle = draw_error_circle(D, I, MAD, x0, y0, z0, dots_size, marker_symbol, data)
    remag_circ_center, remag_circle = draw_error_circle(D, I, 90, x0, y0, z0, dots_size, marker_symbol, data)
    return mean_dot, trust_circle, remag_circle, remag_circ_center


def draw_pca(data, selected_dots, system, dots_size, marker_symbol, mode):
    # Look at Kirschvink, 1980

    I, D, MAD = pca(data, selected_dots, system, mode)
    x0_max, y0_max, z0_max = dir_to_xyz(D, I, 1)
    #
    # Rs = np.sqrt(x0_max ** 2 + y0_max ** 2 + z0_max ** 2)
    # x0_max /= Rs
    # y0_max /= Rs
    # z0_max /= Rs

    mean_dot, trust_circle = draw_error_circle(D, I, MAD, x0_max, y0_max, z0_max, dots_size, marker_symbol,
                                               data)
    return mean_dot, trust_circle

