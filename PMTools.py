import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from templates.app import app
from flask import abort

from templates.pages import (
    svg_to_pdf_converter,
    pmd_charts,
    pmm_dir_charts,
    pmcalc,
)
import webbrowser

server = app.server

app.layout = html.Div(
    [
        # Head
        dbc.Navbar(
            dbc.Container(
                children=[
                    html.A(
                        children=[
                            html.Img(  # Constellation Compass
                                src=app.get_asset_url("pm-tools-icon-disable.svg"),
                                height="40px",
                            ),
                        ],
                        href="/"
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Collapse(
                        children=[
                            dbc.Nav(
                                children=[
                                    dbc.DropdownMenu(
                                        children=[
                                            dbc.DropdownMenuItem(html.A("Demagnetization", href="/", target="_blank")),
                                            dbc.DropdownMenuItem(html.A("PMCalc", href="/pmcalc", target="_blank"))
                                        ],
                                        in_navbar=True,
                                        caret=False,
                                        label="Menu",
                                        right=True,
                                        color="primary",
                                        style={"width":"150px",}
                                    )
                                ],
                                className="ml-auto align-items-center text-center",
                                navbar=True,
                            ),
                        ],
                        id="navbar-collapse",
                        navbar=True,
                    ),
                ],
                className="ml-5 mr-5",
                fluid=True
            ),
            className="mb-2",
            color="dark",
            dark=True
        ),
        # Body
        dbc.Container(
            id="page-container",
            fluid=True,
        ),
        # URL for body-page
        dcc.Location(
            id="page-url",
            refresh=False,
        ),
    ],
)


# Navbar collapse
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n_clicks, is_open):
    if n_clicks is not None:
        return not is_open
    return is_open


# Page update
@app.callback(
    Output("page-container", "children"),
    [Input("page-url", "pathname")]
)
def display_page(pathname):
    if pathname == "/":
        return pmd_charts.layout
    elif pathname == "/svg2pdf":
        return svg_to_pdf_converter.layout
    elif pathname == "/pmm":
        return pmm_dir_charts.layout
    elif pathname == "/pmcalc":
        return pmcalc.layout
    else:
        return abort(404)


webbrowser.open("http://127.0.0.1:8050", new=2)

if __name__ == "__main__":
    app.run_server(debug=False)
