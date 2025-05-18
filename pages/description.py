import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/features', name='Features')

df = pd.read_csv('Mental Health Dataset.csv')

feature_desc = {
    "Timestamp":               "📅 A record of the date and time when an observation or data point was recorded regarding someone's mental health.",
    "Gender":                  "🚻 The classification of a person as male or female.",
    "Country":                 "🌍 The country where a person lives, which is relevant because mental health resources and cultural attitudes can vary by location.",
    "Occupation":              "💼 A person's usual or principal work or business, which can influence stress levels and access to mental health resources.",
    "self_employed":           "🏠 Indicates whether a person is self-employed or running their own business, rather than working for an employer.",
    "family_history":          "👪 A record of a person's family relationships and medical histories, including any family history of mental health issues.",
    "treatment":               "💊 Indicates whether a person is currently undergoing treatment for mental health issues.",
    "Growing_Stress":          "📈 Indicates whether a person's stress level is increasing over time.",
    "Changes_Habits":          "🔄 Refers to changes in behavior or habits that may signal shifts in mental health.",
    "Mental_Health_History":   "📝 A record of a person's past mental health diagnoses, treatments, or issues.",
    "Mood_Swings":             "🎭 Fluctuations in a person's mood, which can be indicative of various mental health conditions.",
    "Coping_Struggles":        "🛡️ Difficulties a person may face in coping with stressors or mental health challenges.",
    "Work_Interest":           "⭐ The level of interest or engagement a person has in their work or activities.",
    "Social_Weakness":         "🤝 Difficulties or challenges in social interactions or maintaining relationships.",
    "mental_health_interview": "🗣️ May refer to a structured interview or assessment conducted to evaluate mental health.",
    "care_options":            "🧭 Options available for seeking care or treatment for mental health issues, such as therapy, medication, or support groups."
}
all_features = list(feature_desc.keys())

def make_feature_card(col, selected=False):
    series = df[col]
    non_null = series.dropna()

    missing_count = series.isna().sum()
    missing_pct   = missing_count / len(series) * 100

    if pd.api.types.is_numeric_dtype(non_null):
        vmin, q1, med, q3, vmax = (
            non_null.min(),
            non_null.quantile(0.25),
            non_null.median(),
            non_null.quantile(0.75),
            non_null.max()
        )
        mean = non_null.mean()
        std  = non_null.std()
        stats = [
            f"🔢 Min: {vmin}",
            f"🔢 Q1: {q1:.2f}",
            f"🔢 Median: {med:.2f}",
            f"🔢 Q3: {q3:.2f}",
            f"🔢 Max: {vmax}",
            f"📊 Mean: {mean:.2f}",
            f"📈 Std: {std:.2f}",
            f"❓ Missing: {missing_count} ({missing_pct:.1f}%)"
        ]
        dist_fig = px.histogram(
            non_null, nbins=20, title=None,
            marginal="box",
            labels={"value": col, "count": "Count"}
        )
    else:
        nunique = non_null.nunique()
        mode    = non_null.mode().iloc[0] if not non_null.mode().empty else "—"
        stats = [
            f"🔢 Unique: {nunique}",
            f"📊 Mode: {mode}",
            f"❓ Missing: {missing_count} ({missing_pct:.1f}%)"
        ]
        counts = non_null.value_counts().reset_index()
        counts.columns = [col, 'count']
        dist_fig = px.bar(
            counts, x=col, y='count', title=None,
            labels={col: col, 'count': 'Count'}
        )

    dist_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=120,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    dist_fig.update_xaxes(title_text='', showgrid=False)
    dist_fig.update_yaxes(title_text='Count', showgrid=False)

    header = dbc.CardHeader(
        html.H5(f"{'✨ ' if selected else ''}{col}", className='mb-0')
    )
    body = dbc.CardBody([
        html.P(feature_desc[col], className='card-text'),
        html.Ul([html.Li(s) for s in stats], className='mt-2 mb-2'),
        dcc.Graph(figure=dist_fig, config={'displayModeBar': False})
    ])

    if selected:
        card = dbc.Card([header, body],
                        color='dark', outline=True, className='h-100 shadow')
        return dbc.Col(card, width=6, className='mb-4')
    else:
        card = dbc.Card([header, body],
                        color='secondary', outline=True, className='h-100 shadow-sm')
        return dbc.Col(card, xs=12, sm=6, md=4, lg=3, className='mb-4')


layout = html.Div(style={
        'minHeight': '100vh',
        'padding': '20px 0'
    },
    children=dbc.Container([
        html.H2("Understanding Dataset Features", className='mt-4 mb-3 text-center'),

        dbc.Row([
            dbc.Col(html.Label("🔎 Select Feature:", style={'fontWeight':'bold'}), width='auto'),
            dbc.Col(
                dcc.Dropdown(
                    id='feature-dropdown',
                    options=[{'label': f, 'value': f} for f in all_features],
                    value=all_features[0],
                    clearable=False,
                    style={'maxWidth': '300px'}
                ),
            )
        ], className='mb-4'),

        html.Div(id='selected-feature-card'),

        dbc.Row(id='other-feature-cards')
    ], fluid=True)
)

@dash.callback(
    Output('selected-feature-card', 'children'),
    Output('other-feature-cards', 'children'),
    Input('feature-dropdown', 'value')
)
def show_feature_cards(selected):
    sel = make_feature_card(selected, selected=True)
    others = [
        make_feature_card(col, selected=False)
        for col in all_features if col != selected
    ]
    return dbc.Row(sel), others
