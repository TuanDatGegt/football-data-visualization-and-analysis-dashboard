# Dashboard/layout/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc


# ===============================
# SIDEBAR
# ===============================
def sidebar():
    return html.Div(
        [
            html.H5(
                "Soccer Analyst",
                className="text-center mt-2 mb-2 fw-bold"
            ),
            html.Hr(className="my-2"),

            # =========================
            # LEAGUE
            # =========================
            html.Small("Competition", className="fw-bold text-muted"),
            dcc.Dropdown(
                id="league-dropdown",
                options=[
                    {"label": "Demo League", "value": "demo_league"},
                ],
                value="demo_league",
                clearable=False,
                className="mb-2",
            ),

            # =========================
            # MATCH
            # =========================
            html.Small("Match", className="fw-bold text-muted"),
            dcc.Dropdown(
                id="match-dropdown",
                options=[],
                value=None,
                clearable=False,
                className="mb-2",
            ),

            # =========================
            # TEAM (VIDEO SIDE)
            # =========================
            html.Small("Video Side", className="fw-bold text-muted"),
            dbc.RadioItems(
                id="team-radio",
                options=[
                    {"label": "Home", "value": "home"},
                    {"label": "Away", "value": "away"},
                ],
                value="home",
                inline=True,
                className="mb-3",
            ),

            html.Hr(className="my-2"),

            # =========================
            # ANALYSIS MODE
            # =========================
            html.Small("Analysis Mode", className="fw-bold text-muted"),
            dbc.Checklist(
                id="analysis-checklist",
                options=[
                    {"label": "Passing", "value": "pass"},
                    {"label": "Shooting", "value": "shot"},
                    {"label": "Tracking", "value": "tracking"},
                ],
                value=["pass", "shot"],
                switch=True,
                className="mt-1",
            ),
        ],
        className="bg-light vh-100 px-3 pt-2",
    )


# ===============================
# TEAM KPI CARDS (NO xG)
# ===============================
def team_kpi_cards():
    return dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Shots"),
                html.H4(id="shots_kpi")
            ])), width=2),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Passes"),
                html.H4(id="passes_kpi")
            ])), width=2),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Pass Accuracy %"),
                html.H4(id="accuracy_kpi")
            ])), width=2),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Mean Pass Length (m)"),
                html.H4(id="mean_pass_length_kpi")
            ])), width=2),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Duels"),
                html.H4(id="duels_kpi")
            ])), width=2),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Goals"),
                html.H4(id="goals_kpi")
            ])), width=2),
        ],
        className="mb-4",
    )


# ===============================
# MODEL SECTION
# ===============================
def model_section():
    return dbc.Card(
        [
            dbc.CardHeader("xG Model & Calibration"),
            dbc.CardBody(
                [
                    dcc.Checklist(
                        id="model-selector",
                        options=[
                            {"label": " Logistic Regression", "value": "lr"},
                            {"label": " Random Forest", "value": "rf"},
                            {"label": " SVM (RBF)", "value": "svm"},
                        ],
                        value=["lr"],
                        inline=True,
                        className="mb-3",
                        labelClassName="me-4"
                    ),
                    dcc.Graph(
                        id="xg-calibration-curve",
                        style={"height": "450px"},
                        config={"displayModeBar": False},
                    ),
                    html.Hr(),
                    html.Div(id="xg-model-metrics"),
                ]
            ),
        ],
        className="mb-4",
    )


# ===============================
# HEATMAP SECTION
# ===============================
def heatmap_section():
    return dbc.Card(
        [
            dbc.CardHeader("Goal Probability Heatmaps (All League)"),
            dbc.CardBody(
                [
                    dcc.Graph(
                        id="goal-probability-heatmap-raw",
                        style={"height": "240px"},
                        config={"displayModeBar": False},
                    ),
                    html.Hr(),
                    dcc.Graph(
                        id="scoring-probability-heatmap",
                        style={"height": "240px"},
                        config={"displayModeBar": False},
                    ),
                ]
            ),
        ],
        className="mb-4",
    )


# ===============================
# VIDEO PRESEDUO
# ===============================
def video_section():
    return dbc.Card(
        [
            dbc.CardHeader("Video Tracking"),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Small("Phase", className="fw-bold text-muted"),
                            dcc.Slider(
                                id="phase-slider",
                                min=1,
                                max=1,
                                step=1,
                                value=1,
                                marks={},
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ],
                        className="mb-3",
                    ),

                    html.Video(
                        id="video-player",
                        controls=True,
                        style={
                            "width": "100%",
                            "height": "auto",
                            "backgroundColor": "black"
                        }
                    ),
                ]
            ),
        ]
    )





# ===============================
# MAIN LAYOUT (WITH TABS)
# ===============================
def create_layout():
    return dbc.Container(
        [
            dcc.Location(id="url"),

            html.H2("Soccer Analyst Dashboard", className="text-center my-3"),

            dbc.Row(
                [
                    # =========================
                    # SIDEBAR
                    # =========================
                    dbc.Col(
                        sidebar(),
                        width=2,
                        className="p-0"
                    ),

                    # =========================
                    # MAIN CONTENT (TABS)
                    # =========================
                    dbc.Col(
                        dbc.Tabs(
                            id="main-tabs",
                            active_tab="tab-model",
                            children=[
                                # ==================================================
                                # TAB 1: MODEL & LEAGUE ANALYSIS
                                # ==================================================
                                dbc.Tab(
                                    label="Model & League",
                                    tab_id="tab-model",
                                    children=[
                                        dbc.Row(
                                            [
                                                dbc.Col(heatmap_section(), width=4),
                                                dbc.Col(model_section(), width=8),
                                            ]
                                        )
                                    ],
                                ),

                                # ==================================================
                                # TAB 2: TEAM & MATCH ANALYSIS
                                # ==================================================
                                dbc.Tab(
                                    label="Team & Match",
                                    tab_id="tab-team",
                                    children=[
                                        team_kpi_cards(),
                                        video_section(),
                                    ],
                                ),

                                # ==================================================
                                # TAB 3: FUTURE (PLACEHOLDER)
                                # ==================================================
                                dbc.Tab(
                                    label="Future",
                                    tab_id="tab-future",
                                    children=[
                                        dbc.Alert(
                                            "This section is reserved for future analysis modules.",
                                            color="secondary",
                                            className="mt-3",
                                        )
                                        # TODO:
                                        # - Tactical patterns
                                        # - Pressing sequences
                                        # - Player clustering
                                        # - Advanced tracking analytics
                                    ],
                                ),
                            ],
                        ),
                        width=10,
                    ),
                ]
            ),
        ],
        fluid=True,
    )

