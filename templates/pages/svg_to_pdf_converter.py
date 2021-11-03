# import base64
# import os
# from urllib.parse import quote as urlquote
#
# from flask import Flask, send_from_directory
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import cairosvg
# from templates.app import server, app
#
#
# UPLOAD_DIRECTORY = "/PM-Tools/svg2pdf"
#
# if not os.path.exists(UPLOAD_DIRECTORY):
#     os.makedirs(UPLOAD_DIRECTORY)
#
# @server.route("/download/<path:path>")
# def download(path):
#     """Serve a file from the upload directory."""
#     return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)
#
#
# layout = [
#     html.Div(
#         children=[
#             html.Div(
#                 children=[
#                     dcc.Upload(
#                         id="upload-data",
#                         className="upload-container",
#                         children=html.Div([
#                             html.A('Select'),
#                             ' or drop file (only .svg)'
#                         ]),
#                         multiple=False,
#                     )
#                 ]
#             ),
#             html.Div(
#                 className="padding-center",
#                 children=[
#                     html.H4("Converted file:"),
#                     html.Ul(id="file-list"),
#                 ]
#             )
#         ]
#     )
# ]
#
#
# def save_file(name, content):
#     """Decode and store a file uploaded with Plotly Dash."""
#     data = cairosvg.svg2pdf(url=content)
#     with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
#         fp.write(data)
#
#
# def uploaded_files():
#     """List the files in the upload directory."""
#     files = []
#     for filename in os.listdir(UPLOAD_DIRECTORY):
#         path = os.path.join(UPLOAD_DIRECTORY, filename)
#         if os.path.isfile(path):
#             files.append(filename)
#     return files
#
#
# def file_download_link(filename):
#     """Create a Plotly Dash 'A' element that downloads a file from the app."""
#     location = "/download/{}".format(urlquote(filename))
#     return html.A(filename, href=location)
#
#
# @app.callback(
#     Output("file-list", "children"),
#     [Input("upload-data", "filename"),
#      Input("upload-data", "contents")],
# )
# def update_output(uploaded_filenames, uploaded_file_contents):
#     """Save uploaded files and regenerate the file list."""
#
#     if uploaded_filenames is not None and uploaded_file_contents is not None:
#         for name, data in zip(uploaded_filenames, uploaded_file_contents):
#             filename, file_extension = os.path.splitext(name)
#             pdf_file_name = filename + ".pdf"
#             save_file(pdf_file_name, data)
#
#     files = uploaded_files()
#     if len(files) == 0:
#         return [html.Li("No files yet!")]
#     else:
#         return [file_download_link(files[0])]

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

import os
import cairosvg

from templates.app import app, server
from urllib.parse import quote as urlquote
from flask import send_from_directory

# UPLOAD_DIRECTORY = "/PM-Tools/svg2pdf"
#
# if not os.path.exists(UPLOAD_DIRECTORY):
#     os.makedirs(UPLOAD_DIRECTORY)
#
#
# @server.route("/download/<path:path>")
# def download(path):
#     """Serve a file from the upload directory."""
#     return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


layout = [
    html.Div(
        [
            html.Div(
                className="twelve columns card",
                children=[
                    dcc.Upload(
                        id='upload-svg-to-convert',
                        className="upload-container",
                        children=html.Div([
                            html.A('Select'),
                            ' or drop file (only .svg)'
                        ]),
                        multiple=False
                    ),
                ]
            ),

            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding-center",
                        children=[
                            html.H6(
                                id='first-line',
                                children='',
                                className="margin__rows",
                            ),
                            html.Button(
                                'CONVERT',
                                id='convert-button',
                                className='submit__button',
                            ),
                            html.H6(
                                id='second-line',
                                children='',
                                className="margin__rows",
                            )
                        ]
                    ),
                ]
            )
        ]
    )
]


@app.callback(
    dash.dependencies.Output("first-line", "children"),
    [dash.dependencies.Input("upload-svg-to-convert", "contents"),
     dash.dependencies.Input("upload-svg-to-convert", "filename")]
)
def file_was_uploaded(svg_file, svg_file_name):
    if not svg_file:
        return ""
    return 'File '+svg_file_name+' was uploaded'

@app.callback(
    dash.dependencies.Output("second-line", "children"),
    [dash.dependencies.Input("convert-button", "n_clicks")],
    [dash.dependencies.State("upload-svg-to-convert", "contents"),
     dash.dependencies.State("upload-svg-to-convert", "filename"),]
)
def convert_svg_to_pdf(n_clicks, svg_file, svg_file_name):
    if not svg_file:
        return ""
    if n_clicks is None:
        return ""

    Home = os.path.expanduser('~')
    downloads_path = os.path.join(Home, "Downloads")
    filename, file_extension = os.path.splitext(svg_file_name)
    pdf_file_name = filename + ".pdf"
    pdf_file = downloads_path + "\\" + pdf_file_name
    data = cairosvg.svg2pdf(url=svg_file)#, write_to=pdf_file)

    with open(os.path.join(UPLOAD_DIRECTORY, pdf_file_name), "wb") as fp:
        fp.write(data)
    location = "/download/{}".format(urlquote(pdf_file_name))
    return html.A(filename, href=location)



