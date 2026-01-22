import base64
from dash import Input, Output, callback, State
import plotly.graph_objects as go

from Dashboard.data_access.events import list_video_phases

@callback(
    Output("phase-dropdown", "options"),
    Output("phase-dropdown", "value"),
    Input("match-dropdown", "value"),
)
def update_phase_dropdown(match_id):
    if match_id is None:
        return [], None

    phases = list_video_phases(match_id)

    options = [
        {"label": f"Phase {p}", "value": p}
        for p in phases
    ]

    return options, (phases[0] if phases else None)


@callback(
    Output("video-player", "src"),
    Output("video-player", "key"),
    Input("phase-dropdown", "value"),
    Input("match-dropdown", "value"),
)
def update_video_src(phase_id, match_id):
    if not phase_id or not match_id:
        return None, "empty"

    filename = f"video_{match_id}_phase{phase_id}.mp4"
    src = f"/assets/{filename}"

    key = f"{match_id}-{phase_id}"

    return src, key
