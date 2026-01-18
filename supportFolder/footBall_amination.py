import pandas as pd
import numpy as np
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
    Event-based pseudo tracking animation for WyScout data
    """

    def __init__(self, event_data: pd.DataFrame, speed: float = 1.0):
        self.df = event_data.copy()
        self.speed = speed

        # validate minimal columns
        required_cols = {"frame", "xPos", "yPos", "team"}
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing columns for animation: {missing}")

        self.df.sort_values("frame", inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    # ===============================
    # CORE LOGIC
    # ===============================
    def _interpolate_position(self, row, frame):
        """
        Linear interpolation between start and end position
        """
        total = max(1, row["endFrame"] - row["startFrame"])
        alpha = (frame - row["startFrame"]) / total

        x = row["posBeforeXMeters"] + alpha * (
            row["posAfterXMeters"] - row["posBeforeXMeters"]
        )
        y = row["posBeforeYMeters"] + alpha * (
            row["posAfterYMeters"] - row["posBeforeYMeters"]
        )
        return x, y

    def _draw_actor(self, x, y, row):
        """
        Player currently involved in event
        """
        return go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            marker=dict(
                size=14,
                color=TEAM_COLOURS.get(row["Team"], "gray"),
                line=dict(width=2, color="white")
            ),
            text=[row["playerName"]],
            textposition="top center",
            name="Player",
            hoverinfo="skip"
        )

    def _draw_ball(self, x, y):
        return go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(size=8, color="black"),
            name="Ball",
            hoverinfo="skip"
        )

    def _draw_path(self, row):
        return go.Scatter(
            x=[row["posBeforeXMeters"], row["posAfterXMeters"]],
            y=[row["posBeforeYMeters"], row["posAfterYMeters"]],
            mode="lines",
            line=dict(color="rgba(255,255,255,0.4)", dash="dash"),
            name="Trajectory",
            hoverinfo="skip"
        )

    # ===============================
    # BUILD ANIMATION
    # ===============================
    def build_animation(self):
        pitch = create_soccer_Pitch(theme="classic")
        fig = pitch.fig

        frames = []
        slider_steps = []

        # frame-level dataframe
        for frame_id, fdf in self.df.groupby("frame"):
            traces = []
            static_players = fdf[fdf["entityType"] == "PLAYER_STATIC"]

            for _, row in static_players.iterrows():
                traces.append(go.Scatter(
                    x=[row["xPos"]],
                    y=[row["yPos"]],
                    mode="markers",
                    marker=dict(
                        size=10,
                        color=TEAM_COLOURS.get(row["team"], "gray"),
                        opacity=0.6,
                        line=dict(width=1, color="white")
                    ),
                    hoverinfo="skip",
                    name="Player"
                ))

            # ==========================
            # 1. DRAW PLAYER WITH BALL
            # ==========================
            players = fdf[fdf["entityType"] == "PLAYER_BALL"]

            for _, row in players.iterrows():
                traces.append(go.Scatter(
                    x=[row["xPos"]],
                    y=[row["yPos"]],
                    mode="markers+text",
                    marker=dict(
                       size=14,
                       color=TEAM_COLOURS.get(row["team"], "gray"),
                        line=dict(width=2, color="white")
                    ),
                    text=[row.get("playerName", "")],
                    textposition="top center",
                    hoverinfo="skip",
                    name="Player"
                ))

            # ==========================
            # 2. DRAW BALL (ALWAYS ON TOP)
            # ==========================
            balls = fdf[fdf["entityType"] == "BALL"]

            for _, row in balls.iterrows():
                traces.append(go.Scatter(
                    x=[row["xPos"]],
                    y=[row["yPos"]],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=TEAM_COLOURS.get("Ball", "black"),
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

        # initial frame
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
