# supportFolder/overview_data.py
import numpy as np
import pandas as pd

from supportFolder.statical_eventTracking import compute_statistics
from Dashboard.data_access.events import load_event_data_kpis


def build_overview_team_kpis(df_events: pd.DataFrame, team_id: int) -> dict:
    """
    Build KPI cho 1 teamID trong 1 match
    """

    if df_events.empty:
        return {}

    df_stats = compute_statistics(
        df_events,
        group_col="team",
        keep_kpis=[
            "totalGoals",
            "totalShots",
            "totalPasses",
            "shareAccuratePasses",
            "meanPassLength",
            "totalDuels",
        ]
    )

    if df_stats.empty:
        return {}

    row = df_stats[df_stats["teamID"] == team_id]
    if row.empty:
        return {}

    row = row.iloc[0]

    return {
        "shot_kpi": int(row["totalShots"]),
        "passes_kpi": int(row["totalPasses"]),
        "accuracy_kpi": float(row["shareAccuratePasses"]),  # đã là %
        "mean_pass_length_kpi": float(row["meanPassLength"]),
        "duels_kpi": int(row["totalDuels"]),
        "goals_kpi": int(row["totalGoals"]),
    }
