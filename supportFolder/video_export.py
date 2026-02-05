import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Rectangle, Circle, Arc
import pandas as pd

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO_DIR = ROOT / "dataset" / "video_"
DEFAULT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


# ===============================
# COLOR CONFIG
# ===============================
TEAM_COLOURS = {
    "Home": "#3498db",
    "Away": "#e74c3c",
    "Ball": "#000000"
}


# ===============================
# PITCH DRAWING (PURE MPL)
# ===============================
def draw_pitch_mpl(ax, length=105, width=68, theme="white"):
    """
    Draw a full soccer pitch using Matplotlib
    (ported from Plotly create_soccer_Pitch)
    """

    themes = {
        "classic": dict(
            pitch="#224422",
            line="white",
            goal="white"
        ),
        "white": dict(
            pitch="#0CE834",
            line="#171818",
            goal="black"
        )
    }

    cfg = themes.get(theme, themes["white"])

    # Background
    ax.set_facecolor(cfg["pitch"])

    # ===== Outer lines =====
    ax.add_patch(
        Rectangle((0, 0), length, width,
                  fill=False, edgecolor=cfg["line"], linewidth=1.5)
    )

    # ===== Halfway line =====
    ax.plot([length / 2, length / 2], [0, width],
            color=cfg["line"], linewidth=1.5)

    # ===== Center circle =====
    ax.add_patch(
        Circle((length / 2, width / 2), 9.15,
               fill=False, edgecolor=cfg["line"], linewidth=1.5)
    )

    # ===== Center spot =====
    ax.scatter(length / 2, width / 2, color=cfg["line"], s=30)

    # ===== Penalty spots =====
    ax.scatter([11, length - 11], [width / 2, width / 2],
               color=cfg["line"], s=30)

    # ===== Penalty areas & goals =====
    for side in [0, 1]:
        x_edge = side * length
        direction = 1 if side == 0 else -1

        # 16m50 box
        ax.add_patch(
            Rectangle(
                (x_edge, (width - 40.3) / 2),
                direction * 16.5, 40.3,
                fill=False, edgecolor=cfg["line"], linewidth=1.5
            )
        )

        # 5m50 box
        ax.add_patch(
            Rectangle(
                (x_edge, (width - 18.3) / 2),
                direction * 5.5, 18.3,
                fill=False, edgecolor=cfg["line"], linewidth=1.5
            )
        )

        # Goal
        ax.add_patch(
            Rectangle(
                (x_edge - direction * 1.5, (width - 7.32) / 2),
                direction * 1.5, 7.32,
                fill=False, edgecolor=cfg["goal"], linewidth=2
            )
        )

        # Penalty arc (D)
        arc_angle = (-53, 53) if side == 0 else (127, 233)
        ax.add_patch(
            Arc(
                (11 if side == 0 else length - 11, width / 2),
                height=18.3, width=18.3,
                angle=0,
                theta1=arc_angle[0],
                theta2=arc_angle[1],
                color=cfg["line"],
                linewidth=1.5
            )
        )

    # ===== Axis config =====
    ax.set_xlim(-5, length + 5)
    ax.set_ylim(-5, width + 5)
    ax.set_aspect("equal")
    ax.axis("off")

# ===============================
# MAIN CLASS
# ===============================
class MPLFootballAnimator:
    """
    Matplotlib-based pseudo tracking animator (MP4)
    """

    def __init__(
        self,
        tracking_df: pd.DataFrame,
        fps: int = 10,
        pitch_length: int = 105,
        pitch_width: int = 68,
        matchID: int = None,
        phase_idx: int = None,
        video_dir: Path = DEFAULT_VIDEO_DIR
    ):
        self.df = tracking_df.copy()
        self.fps = fps
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width

        self.matchID = matchID
        self.phase_idx = phase_idx
        self.video_dir = video_dir
        
        required_cols = {"frame", "xPos", "yPos", "team", "entityType"}
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        self.df.sort_values("frame", inplace=True)
        self.frames = sorted(self.df["frame"].unique())

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.patch.set_facecolor("#0CE834") 

    # ===============================
    # FRAME UPDATE
    # ===============================
    def _update(self, frame_id):
        self.ax.clear()
        draw_pitch_mpl(self.ax, self.pitch_length, self.pitch_width)

        fdf = self.df[self.df["frame"] == frame_id]

        # PLAYER OWNER
        owners = fdf[fdf["entityType"] == "PLAYER_OWNER"]
        for _, row in owners.iterrows():
            self.ax.scatter(
                row["xPos"],
                row["yPos"],
                s=160,
                c=TEAM_COLOURS.get(row["team"], "gray"),
                edgecolors="white",
                linewidths=2,
                zorder=3
            )

        # PLAYER TARGET
        targets = fdf[fdf["entityType"] == "PLAYER_TARGET"]
        for _, row in targets.iterrows():
            self.ax.scatter(
                row["xPos"],
                row["yPos"],
                s=110,
                c=TEAM_COLOURS.get(row["team"], "gray"),
                alpha=0.6,
                edgecolors="white",
                linewidths=1.5,
                zorder=2
            )

        # BALL
        balls = fdf[fdf["entityType"] == "BALL"]
        for _, row in balls.iterrows():
            self.ax.scatter(
                row["xPos"],
                row["yPos"],
                s=40,
                c=TEAM_COLOURS["Ball"],
                edgecolors="white",
                linewidths=1,
                zorder=4
            )

        self.ax.set_title(f"Frame: {frame_id}", fontsize=12)

    # ===============================
    # SAVE MP4
    # ===============================
    def save_mp4(self, out_path: str| Path | None = None):

        owners = self.df[self.df["entityType"] == "PLAYER_OWNER"]

        team_labels = (
            owners["team"].value_counts().idxmax()
            if not owners.empty else "Unknown"
        )


        if out_path is None:
            if self.matchID is None or self.phase_idx is None:
                raise ValueError(
                    "Hoặc cung cấp out_path HOẶC thiết lập match_id & phase_idx để tự động tạo tên tệp."
                )

            out_path = (self.video_dir /
                f"match_{self.matchID}_phase_{self.phase_idx}_{team_labels}.mp4")
            

        writer = FFMpegWriter(fps=self.fps)

        ani = FuncAnimation(
            self.fig,
            self._update,
            frames=self.frames,
            interval=1000 / self.fps
        )

        ani.save(str(out_path), writer=writer)
        plt.close(self.fig)

        print(f"✅ Saved MP4: {out_path}")
