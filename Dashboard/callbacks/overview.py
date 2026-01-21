from dash import Input, Output, callback
import plotly.graph_objects as go

from data_access.events import load_event_data, load_xg_data
from supportFolder.heatmap_xG import build_goal_probability_heatmap, filter_outlier_shots_and_plot_heatmap
from supportFolder.metrics_eval import build_xg_calibration_figure



# =========================
# GOAL PROBABILITY HEATMAP
# =========================
@callback(
    Output("goal-probability-heatmap-raw", "figure"),
    Input("url", "pathname"),
)
def update_goal_probability_heatmap(_):

    df_shots = load_event_data(shots_only=True)

    if df_shots.empty:
        return go.Figure()

    fig = build_goal_probability_heatmap(df_shots)
    return fig

# =========================
# SCORING PROBABILITY HEATMAP
# =========================
@callback(
    Output("scoring-probability-heatmap", "figure"),
    Input("url", "pathname"),
)
def update_scoring_probability_heatmap(_):

    df_events = load_event_data(shots_only=False)

    if df_events.empty:
        return go.Figure()

    fig = filter_outlier_shots_and_plot_heatmap(
        df_events, prob_threshold=0.1, nb_buckets_x=24, nb_buckets_y=17
    )

    return fig


@callback(
    Output("xg-calibration-curve", "figure"),
    Input("model-selector", "value"),
)
def update_calibration_curve(selected_models):

    if not selected_models:
        return go.Figure()

    df_test = load_xg_data(split="test")

    fig = build_xg_calibration_figure(
        df_test,
        models=tuple(selected_models)
    )

    return fig


