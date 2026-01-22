from dash import Input, Output, callback
import plotly.graph_objects as go

from Dashboard.data_access.events import load_event_data_kpis
from supportFolder.overview_data import build_overview_team_kpis


@callback(
    Output("shots_kpi", "children"),
    Output("passes_kpi", "children"),
    Output("accuracy_kpi", "children"),
    Output("mean_pass_length_kpi", "children"),
    Output("duels_kpi", "children"),
    Output("goals_kpi", "children"),
    Input("match-dropdown", "value"),
    Input("team-radio", "value"),   # 'home' | 'away'
)
def update_team_kpis(match_id, team_side):

    if not match_id or not team_side:
        return ["–"] * 6

    df_events = load_event_data_kpis(match_id)
    if df_events.empty:
        return ["–"] * 6

    # 🔑 UI chỉ dùng để chọn teamID
    team_id = (
        df_events["homeTeamID"].iloc[0]
        if team_side == "home"
        else df_events["awayTeamID"].iloc[0]
    )

    kpis = build_overview_team_kpis(df_events, team_id)
    if not kpis:
        return ["–"] * 6

    return (
        kpis["shot_kpi"],
        kpis["passes_kpi"],
        f'{kpis["accuracy_kpi"]:.1f}%',
        f'{kpis["mean_pass_length_kpi"]:.1f}',
        kpis["duels_kpi"],
        kpis["goals_kpi"],
    )
