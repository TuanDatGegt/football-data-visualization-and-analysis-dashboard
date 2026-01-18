import pandas as pd
import plotly.graph_objects as go
from supportFolder.plot_pitch import create_soccer_Pitch


# ===============================
# COLOR CONFIG
# ===============================
TEAM_COLOURS = {
    "Home": "#3498db",
    "Away": "#e74c3c",
    "Ball": "#000000"
}


# ===============================
# MAIN CLASS
# ===============================
class FootballAnimator:
    """
    Event-based pseudo tracking animation (OWNER / TARGET / BALL)
    """

    def __init__(self, event_data: pd.DataFrame, speed: float = 1.0):
        self.df = event_data.copy()
        self.speed = speed

        required_cols = {"frame", "xPos", "yPos", "team", "entityType"}
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        self.df.sort_values("frame", inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    # ===============================
    # BUILD ANIMATION
    # ===============================
    def build_animation(self):
        pitch = create_soccer_Pitch(theme="classic")
        fig = pitch.fig

        frames = []
        slider_steps = []

        for frame_id, fdf in self.df.groupby("frame"):
            traces = []

            # ==========================
            # PLAYER OWNER
            # ==========================
            owners = fdf[fdf["entityType"] == "PLAYER_OWNER"]

            for _, row in owners.iterrows():
                traces.append(go.Scatter(
                    x=[row["xPos"]],
                    y=[row["yPos"]],
                    mode="markers+text",
                    marker=dict(
                        size=16,
                        color=TEAM_COLOURS.get(row["team"], "gray"),
                        line=dict(width=3, color="white")
                    ),
                    text=[row.get("playerName", "")],
                    textposition="top center",
                    hoverinfo="skip",
                    name="Owner"
                ))

            # ==========================
            # PLAYER TARGET
            # ==========================
            targets = fdf[fdf["entityType"] == "PLAYER_TARGET"]

            for _, row in targets.iterrows():
                traces.append(go.Scatter(
                    x=[row["xPos"]],
                    y=[row["yPos"]],
                    mode="markers+text",
                    marker=dict(
                        size=13,
                        color=TEAM_COLOURS.get(row["team"], "gray"),
                        opacity=0.6,
                        line=dict(width=2, color="white")
                    ),
                    text=[row.get("playerName", "")],
                    textposition="top center",
                    hoverinfo="skip",
                    name="Target"
                ))

            # ==========================
            # BALL (TOP LAYER)
            # ==========================
            balls = fdf[fdf["entityType"] == "BALL"]

            for _, row in balls.iterrows():
                traces.append(go.Scatter(
                    x=[row["xPos"]],
                    y=[row["yPos"]],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=TEAM_COLOURS["Ball"],
                        line=dict(width=1, color="white")
                    ),
                    hoverinfo="skip",
                    name="Ball"
                ))

            frames.append(go.Frame(data=traces, name=str(frame_id)))

            slider_steps.append({
                "args": [[str(frame_id)], {"mode": "immediate"}],
                "label": str(frame_id),
                "method": "animate"
            })

        fig.frames = frames

        # Initial frame
        if frames:
            fig.add_traces(frames[0].data)

        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "x": 0.5,
                "y": -0.08,
                "xanchor": "center",
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [None, {
                            "frame": {"duration": int(40 / self.speed)},
                            "fromcurrent": True
                        }]
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [[None], {"mode": "immediate"}]
                    }
                ]
            }],
            sliders=[{
                "steps": slider_steps,
                "currentvalue": {"prefix": "Frame: "}
            }]
        )

        return fig
