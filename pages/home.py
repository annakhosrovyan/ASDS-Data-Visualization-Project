import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name='Home')

df = pd.read_csv('Mental Health Dataset.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Date']      = df['Timestamp'].dt.date

df_enc = df.copy()
ord_mappings = {
    'self_employed':           {'No':0, 'Yes':1},
    'family_history':          {'No':0, 'Yes':1},
    'treatment':               {'No':0, 'Yes':1},
    'Growing_Stress':          {'No':0, 'Maybe':1, 'Yes':2},
    'Changes_Habits':          {'No':0, 'Maybe':1, 'Yes':2},
    'Mental_Health_History':   {'No':0, 'Maybe':1, 'Yes':2},
    'Mood_Swings':             {'Low':1, 'Medium':2, 'High':3},
    'Coping_Struggles':        {'No':0, 'Yes':1},
    'Work_Interest':           {'No':0, 'Maybe':1, 'Yes':2},
    'Social_Weakness':         {'No':0, 'Maybe':1, 'Yes':2},
    'mental_health_interview': {'No':0, 'Maybe':1, 'Yes':2},
    'care_options':            {'No':0, 'Not sure':1, 'Yes':2},
    'Days_Indoors': {
        'More than 2 months': 1,
        '31-60 days':         2,
        '15-30 days':         3,
        '1-14 days':          4,
        'Go out Every day':   5
    }
}
for c, mp in ord_mappings.items():
    if c in df_enc:
        df_enc[c] = df_enc[c].map(mp)

numeric_cols = [
    c for c in df_enc.columns
    if pd.api.types.is_numeric_dtype(df_enc[c])
]

total_records = len(df)
start_date    = df['Date'].min()
end_date      = df['Date'].max()
avg_per_day   = int(df.groupby('Date').size().mean())
treat_rate    = df['treatment'].value_counts(normalize=True).get('Yes', 0) * 100
top_occ       = (
    df['Occupation'].mode().iat[0]
    if not df['Occupation'].mode().empty else '—'
)

# Missing‐data bar
missing_df = (
    df.drop(columns=['Date'])
      .isnull()
      .sum()
      .reset_index(name='missing_count')
      .rename(columns={'index':'feature'})
      .sort_values('missing_count', ascending=True)
)
fig_missing = px.bar(
    missing_df,
    x='missing_count', y='feature', orientation='h',
    labels={'missing_count':'Missing count','feature':''},
    template='plotly_white'
)
fig_missing.update_layout(
    margin=dict(l=80, t=20, b=20, r=20),
    height=300
)
fig_missing.update_xaxes(showgrid=True, gridcolor='lightgrey')
fig_missing.update_yaxes(showgrid=True, gridcolor='lightgrey')

# Global map 
map_df = (
    df['Country']
      .value_counts()
      .rename_axis('country')
      .reset_index(name='count')
)
fig_world = px.choropleth(
    map_df,
    locations='country',
    locationmode='country names',
    color='count',
    hover_name='country',
    color_continuous_scale='Viridis',
    labels={'count':'Responses'},
    title="All Responses by Country",
    template='plotly_white'
)
fig_world.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    margin=dict(l=0, t=40, b=20, r=0),
    height=300
)

# Gender pie & treatment bar
fig_gender = px.pie(
    df, names='Gender', hole=0.4, title='Gender Breakdown',
    template='plotly_white'
)
fig_gender.update_traces(textinfo='percent+label')
fig_gender.update_layout(
    margin=dict(l=0, t=30, b=0, r=0),
    height=300,
    legend=dict(orientation='h', yanchor='bottom', y=-0.1)
)

treat_df = (
    df['treatment']
      .value_counts()
      .rename_axis('treatment')
      .reset_index(name='count')
)
fig_treat = px.bar(
    treat_df, x='treatment', y='count', text='count', title='Treatment Status',
    template='plotly_white'
)
fig_treat.update_layout(
    margin=dict(l=40, t=30, b=0, r=20),
    height=300
)
fig_treat.update_xaxes(title='')
fig_treat.update_yaxes(title='Count')

# Correlation heatmap 
corr = df_enc[numeric_cols].corr().abs()
fig_corr = px.imshow(
    corr,
    text_auto=True,
    aspect='auto',
    color_continuous_scale='Blues',
    title='Feature Correlations (|r| ≥ 0)',
    template='plotly_white'
)
fig_corr.update_layout(
    margin=dict(l=40, t=40, b=20, r=20),
    height=500,
    width=None 
)
fig_corr.update_xaxes(
    showgrid=True, gridcolor='lightgrey', tickangle=45
)
fig_corr.update_yaxes(showgrid=True, gridcolor='lightgrey')


# Layout
layout = dbc.Container(fluid=True, className='py-4', children=[

    html.H2("Statistics & EDA", className='text-center mb-4'),

    dbc.Card(className='mb-4 shadow-sm', children=dbc.CardBody([
        html.H4("Overview 🗒️", className='card-title'),
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("📋 Total Records"),
                    html.H4(f"{total_records:,}")
                ]), className='border shadow-none'),
                md=2
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("📅 Date Range"),
                    html.P(f"{start_date} → {end_date}")
                ]), className='border shadow-none'),
                md=3
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("🔢 Avg / Day"),
                    html.H4(f"{avg_per_day:,}")
                ]), className='border shadow-none'),
                md=2
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("💊 Treatment Rate"),
                    html.H4(f"{treat_rate:.1f}%")
                ]), className='border shadow-none'),
                md=2
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("💼 Top Occupation"),
                    html.H4(top_occ)
                ]), className='border shadow-none'),
                md=3
            ),
        ], className='mb-4 justify-content-center'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_gender, config={'displayModeBar':False}), md=6),
            dbc.Col(dcc.Graph(figure=fig_treat,  config={'displayModeBar':False}), md=6),
        ], className='mb-4'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_missing, config={'displayModeBar':False}), md=6),
            dbc.Col(dcc.Graph(figure=fig_world,   config={'displayModeBar':False}), md=6),
        ]),
    ])),

    # Trend Card 
    dbc.Card(className='mb-4 shadow-sm', children=dbc.CardBody([

        html.H4("Trend Over Time 📈", className='card-title'),

        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.Label("Date Range", className="form-label"),
                    dcc.DatePickerRange(
                        id='home-date-picker',
                        min_date_allowed=df['Timestamp'].min(),
                        max_date_allowed=df['Timestamp'].max(),
                        start_date=df['Timestamp'].min(),
                        end_date=df['Timestamp'].max(),
                        display_format='MM/DD/YYYY',
                        className='w-100'
                    ),
                ], className="mb-3"),
                md=6
            ),

            dbc.Col(
                html.Div([
                    dbc.Label("Aggregate By", className="form-label"),
                    dcc.RadioItems(
                        id='home-trend-agg',
                        options=[
                            {'label':'Daily','value':'D'},
                            {'label':'Weekly','value':'W'},
                            {'label':'Monthly','value':'M'}
                        ],
                        value='M',
                        inline=True,
                        labelClassName='me-3'
                    ),
                    html.Div(
                        dbc.Checklist(
                            id='home-trend-cum',
                            options=[{'label':' Show cumulative','value':'cum'}],
                            value=[],
                            switch=True
                        ),
                        className='mt-2'
                    )
                ], className="h-100 d-flex flex-column justify-content-center"),
                md=6
            ),
        ], className='mb-3'),

        dcc.Graph(
            id='home-trend-chart',
            config={'displayModeBar': False},
            style={'height':'420px'}
        ),

    ])),


    # Correlations Card
    dbc.Card(className='mb-4 shadow-sm', children=dbc.CardBody([
        html.H4("Correlations 🔗", className='card-title'),
        html.P("Filter by |r| threshold:", className='mb-2'),
        dcc.Slider(
            id='home-corr-thresh',
            min=0, max=1, step=0.05, value=0,
            marks={i/10:f"{i*10}%" for i in range(11)},
            className='mb-3'
        ),
        dcc.Graph(
            id='home-corr-heatmap',
            figure=fig_corr,
            config={'displayModeBar':False},
            style={'height':'500px'}
        )
    ])),

])


# Trend callback 
@callback(
    Output('home-trend-chart','figure'),
    Input('home-date-picker','start_date'),
    Input('home-date-picker','end_date'),
    Input('home-trend-agg','value'),
    Input('home-trend-cum','value'),
)
def update_home_trend(s, e, freq, cum):
    mask = (df['Timestamp'] >= s) & (df['Timestamp'] <= e)
    ts = (
        df.loc[mask]
          .groupby(pd.Grouper(key='Timestamp', freq=freq))
          .size()
          .reset_index(name='count')
    )

    if 'cum' in cum:
        ts['count'] = ts['count'].cumsum()
        title = "Cumulative Records Over Time"
    else:
        title = "Records per Period Over Time"

    fig = px.line(
        ts, x='Timestamp', y='count',
        title=title,
        markers=True,
        template="plotly_white"
    )
    fig.update_traces(line=dict(color='#636EFA', width=3))

    area_trace = px.area(ts, x='Timestamp', y='count', template="plotly_white").data[0]
    fig.add_trace(area_trace)

    fig.update_layout(
        title_font_size=20,
        margin=dict(t=60, b=40, l=40, r=40),
        hovermode='x unified'
    )
    fig.update_xaxes(
        showgrid=True, gridcolor='lightgrey',
        tickangle=-45, title=''
    )
    fig.update_yaxes(
        showgrid=True, gridcolor='lightgrey',
        title='Count'
    )

    return fig


# Correlation callback
@callback(
    Output('home-corr-heatmap','figure'),
    Input('home-corr-thresh','value')
)
def update_home_corr(t):
    corr_mat = df_enc[numeric_cols].corr().abs()
    masked   = corr_mat.mask(corr_mat < t)

    fig = px.imshow(
        masked,
        text_auto=True,
        aspect='auto',
        color_continuous_scale='Blues',
        title=f"Feature Correlations (|r| ≥ {t:.2f})",
        template='plotly_white'
    )
    fig.update_layout(
        margin=dict(l=40, t=40, b=20, r=20),
        height=500
    )
    fig.update_xaxes(showgrid=True, gridcolor='lightgrey', tickangle=45)
    fig.update_yaxes(showgrid=True, gridcolor='lightgrey')

    return fig
