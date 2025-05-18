import dash
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    brand="🧠 Mental Health Dashboard",
    brand_href="/",
    color="dark", dark=True,
    children=[
      dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
      dbc.NavItem(dbc.NavLink("Features", href="/features", active="exact")),
      dbc.NavItem(dbc.NavLink("Visualizations", href="/visualizations", active="exact")),
    ]
)

app.layout = html.Div(
    style={
      "backgroundColor": "#F3F2F5FF",
      "minHeight": "100vh",
      "padding": "0"
    },
    children=[
      navbar,
      page_container
    ]
)

if __name__ == "__main__":
    app.run(debug=True)


