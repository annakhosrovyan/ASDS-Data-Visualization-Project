import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path='/visualizations', name='Visualizations')

df = pd.read_csv('Mental Health Dataset.csv')


def plot_distribution(column, data_frame):
    counts = data_frame[column].value_counts().reset_index()
    counts.columns = [column, 'count']
    fig = px.bar(
        counts, x=column, y='count',
        color=column,
        title=f"Distribution of {column}",
        hover_data={column: True, 'count': True},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_white'
    )
    rotation = 45 if counts.shape[0] > 8 else 0
    fig.update_layout(
        xaxis_tickangle=rotation,
        yaxis_title="Count",
        margin=dict(t=60, b=50, l=40, r=20),
        plot_bgcolor='white',
        showlegend=False
    )
    fig.update_xaxes(showgrid=True, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridcolor='lightgrey')
    return fig

def plot_grouped_bar(x, hue, data_frame):
    grouped = data_frame.groupby([x, hue]).size().reset_index(name='count')
    fig = px.bar(
        grouped, x=x, y='count',
        color=hue, barmode='group',
        title=f"Grouped Bar: {x} by {hue}",
        hover_data={x: True, hue: True, 'count': True},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_white'
    )
    rotation = 45 if grouped[x].nunique() > 8 else 0
    fig.update_layout(
        xaxis_tickangle=rotation,
        yaxis_title="Count",
        margin=dict(t=60, b=50, l=40, r=20)
    )
    fig.update_xaxes(showgrid=True, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridcolor='lightgrey')
    return fig

# Dropdown options
def make_opts(series):
    vals = sorted(series.dropna().unique())
    return [{'label':str(v), 'value':v} for v in vals]

country_opts    = [{'label':'All','value':'All'}] + make_opts(df['Country'])
gender_opts     = [{'label':'All','value':'All'}] + make_opts(df['Gender'])
treatment_opts  = [{'label':'All','value':'All'}] + make_opts(df['treatment'])
occupation_opts = [{'label':'All','value':'All'}] + make_opts(df['Occupation'])
selfemp_opts    = [{'label':'All','value':'All'}] + make_opts(df['self_employed'])
family_opts     = [{'label':'All','value':'All'}] + make_opts(df['family_history'])
column_opts     = [{'label':col, 'value':col} for col in df.columns]


# Tabs content

def distribution_tab():
    return dbc.CardBody([
        dbc.Row([
            dbc.Col(html.Div([html.Label("Country"), dcc.Dropdown(id='filter-country',
                options=country_opts, value=['All'], multi=True, clearable=False)]), width=4),
            dbc.Col(html.Div([html.Label("Gender"), dcc.Dropdown(id='filter-gender',
                options=gender_opts, value=['All'], multi=True, clearable=False)]), width=4),
            dbc.Col(html.Div([html.Label("Treatment"), dcc.Dropdown(id='filter-treatment',
                options=treatment_opts, value=['All'], multi=True, clearable=False)]), width=4),
        ], className="gy-3 mb-3"),
        dbc.Row([
            dbc.Col(html.Div([html.Label("Occupation"), dcc.Dropdown(id='filter-occupation',
                options=occupation_opts, value=['All'], multi=True, clearable=False)]), width=4),
            dbc.Col(html.Div([html.Label("Self-Employed"), dcc.Dropdown(id='filter-self-employed',
                options=selfemp_opts, value=['All'], multi=True, clearable=False)]), width=4),
            dbc.Col(html.Div([html.Label("Family History"), dcc.Dropdown(id='filter-family-history',
                options=family_opts, value=['All'], multi=True, clearable=False)]), width=4),
        ], className="gy-3 mb-3"),
        html.Div([html.Label("Select Column"), dcc.Dropdown(
            id='dist-column-dropdown', options=column_opts,
            value='Days_Indoors', clearable=False
        )], className="mb-4"),
        dcc.Graph(id='dist-graph', config={'displayModeBar':False})
    ])

def grouped_bar_tab():
    return dbc.CardBody([
        dbc.Row([
            dbc.Col(html.Div([html.Label("X-Axis"), dcc.Dropdown(
                id='group-x', options=column_opts, value='Country', clearable=False
            )]), width=6),
            dbc.Col(html.Div([html.Label("Hue"), dcc.Dropdown(
                id='group-hue', options=column_opts, value='Gender', clearable=False
            )]), width=6),
        ], className="gy-3 mb-4"),
        dcc.Graph(id='grouped-bar-chart', config={'displayModeBar':False})
    ])


# Layout with Tabs
layout = dbc.Container(fluid=True, className='py-4', children=[
    html.H2("Interactive Visualizations", className='text-center mb-4'),

    dbc.Tabs([
        dbc.Tab(distribution_tab(), label="Distribution", tab_id="tab-dist"),
        dbc.Tab(grouped_bar_tab(),   label="Grouped Bar",   tab_id="tab-group"),
    ], id="vis-tabs", active_tab="tab-dist")
])


# Callbacks

@callback(
    Output('dist-graph','figure'),
    Input('filter-country','value'),
    Input('filter-gender','value'),
    Input('filter-treatment','value'),
    Input('filter-occupation','value'),
    Input('filter-self-employed','value'),
    Input('filter-family-history','value'),
    Input('dist-column-dropdown','value'),
)
def update_distribution(countries, genders, treatments, occupations, selfemps, fam_hist, column):
    dff = df.copy()
    if 'All' not in countries:
        dff = dff[dff['Country'].isin(countries)]
    if 'All' not in genders:
        dff = dff[dff['Gender'].isin(genders)]
    if 'All' not in treatments:
        dff = dff[dff['treatment'].isin(treatments)]
    if 'All' not in occupations:
        dff = dff[dff['Occupation'].isin(occupations)]
    if 'All' not in selfemps:
        dff = dff[dff['self_employed'].isin(selfemps)]
    if 'All' not in fam_hist:
        dff = dff[dff['family_history'].isin(fam_hist)]
    return plot_distribution(column, dff)


@callback(
    Output('grouped-bar-chart','figure'),
    Input('group-x','value'),
    Input('group-hue','value')
)
def update_grouped_bar(x, hue):
    return plot_grouped_bar(x, hue, df)
