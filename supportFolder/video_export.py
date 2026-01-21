"""
video_export.py
----------------
Utilities for exporting pseudo tracking animations
(MP4 only, no Plotly / no Kaleido)

Author: Soccer Analyst
"""

from pathlib import Path
import shutil

import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter

from supportFolder.plot_pitch import create_soccer_Pitch


# =========================================================
# PROJECT PATH
# =========================================================
ROOT = Path(__file__).resolve().parents[1]

VIDEO_DIR = ROOT / "dataset" / "video_"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# UTILS
# =========================================================
def _check_ffmpeg():
    """Ensure ffmpeg is available."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found. Install it with:\n"
            "sudo apt install ffmpeg"
        )


# =========================================================
# CORE: TRACKING DF -> MP4
# =========================================================
def save_phase_mp4(
    tracking_df,
    match_id: int,
    phase_idx: int,
    fps: int = 10,
    dpi: int = 100,
    figsize=(12, 8),
):
    """
    Save pseudo tracking animation as MP4 (H.264).

    Parameters
    ----------
    tracking_df : pd.DataFrame
        Pseudo tracking dataframe (ONE phase)
        Required columns: ['frame', 'xPos', 'yPos', 'team']
    match_id : int
        Match ID used for output filename
    phase_idx : int
        Phase index (for logging / review only)
    fps : int
        Frames per second
    dpi : int
        Video resolution control
    figsize : tuple
        Figure size in inches
    """
    _check_ffmpeg()

    out_path = VIDEO_DIR / f"video_{match_id}.mp4"

    fig, ax = plt.subplots(figsize=figsize)

    writer = FFMpegWriter(
        fps=fps,
        metadata={
            "title": f"Match {match_id} | Phase {phase_idx}",
            "artist": "Soccer Analyst",
        },
        codec="libx264",
        bitrate=1800,
    )

    frames = sorted(tracking_df["frame"].unique())

    with writer.saving(fig, out_path, dpi=dpi):
        for frame_id in frames:
            ax.clear()

            # Draw pitch
            create_soccer_Pitch(ax)

            frame_df = tracking_df[tracking_df["frame"] == frame_id]

            # Plot players & ball
            for team, color in {
                "Home": "#3498db",
                "Away": "#e74c3c",
                "Ball": "#000000",
            }.items():
                team_df = frame_df[frame_df["team"] == team]
                if not team_df.empty:
                    ax.scatter(
                        team_df["xPos"],
                        team_df["yPos"],
                        s=60 if team != "Ball" else 30,
                        c=color,
                        edgecolors="white",
                        linewidths=0.5,
                        zorder=3,
                    )

            ax.set_title(
                f"Match {match_id} | Phase {phase_idx} | Frame {frame_id}",
                fontsize=10,
            )

            writer.grab_frame()

    plt.close(fig)

    print(
        f"✅ Saved MP4 | match_id={match_id} | "
        f"phase={phase_idx} | path={out_path}"
    )
