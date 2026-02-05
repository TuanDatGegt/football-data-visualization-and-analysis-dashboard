# Dashboard/callbacks/tracking.py
from dash import Input, Output, callback
from Dashboard.data_access.events import list_video_phases, list_matches_with_video
from pathlib import Path

# ===============================
# CALLBACK 1: UPDATE PHASE DROPDOWN
# ===============================
@callback(
    Output("phase-slider", "min"),
    Output("phase-slider", "max"),
    Output("phase-slider", "marks"),
    Output("phase-slider", "value"),
    Input("match-dropdown", "value"),
)
def update_phase_slider(match_id):
    if match_id is None:
        return 1, 1, {}, 1

    phases = list_video_phases(match_id)

    if not phases:
        return 1, 1, {}, 1

    marks = {p: str(p) for p in phases}

    return min(phases), max(phases), marks, phases[0]



# ===============================
# CALLBACK 2: UPDATE VIDEO PLAYER
# ===============================
@callback(
    Output("video-player", "src"),
    Output("video-player", "key"),
    Input("match-dropdown", "value"),
    Input("phase-slider", "value"),   # ✅ ĐÚNG
    Input("team-radio", "value"),
)
def update_video_src(match_id, phase, team):
    if not match_id or not phase or not team:
        return None, "empty"

    team = team.capitalize()  # home → Home

    filename = f"match_{match_id}_phase_{phase}_{team}.mp4"
    src = f"/assets/video/{filename}"

    key = f"{match_id}-{phase}-{team}"

    return src, key


@callback(
    Output("match-dropdown", "options"),
    Output("match-dropdown", "value"),
    Input("league-dropdown", "value"),
)
def update_match_dropdown(_):
    matches = list_matches_with_video()

    if not matches:
        return [], None

    options = [
        {"label": f"Match {m}", "value": m}
        for m in matches
    ]

    return options, matches[0]