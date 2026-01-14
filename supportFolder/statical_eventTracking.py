import pandas as pd
import numpy as np

def compute_length(df):
    dx = df["posAfterXMeters"] - df["posBeforeXMeters"]
    dy = df["posAfterYMeters"] - df["posBeforeYMeters"]

    df["lengthMeters"] = np.sqrt(dx**2 + dy**2)
    return df

def compute_totalPasses(df_events, group_cols):
    df_passes = df_events[df_events["eventName"] == "Pass"]
    return df_passes.groupby(group_cols).agg(totalPasses=("ID", "size")).reset_index()

def compute_totalAccuratePass(df_events, group_cols):
    mask = (df_events["eventName"] == "Pass") & (df_events["accurate"] == 1)
    return df_events[mask].groupby(group_cols).agg(totalAccuratePasses=("ID", "size")).reset_index()

def compute_meanPassLength(df_events, group_cols):
    df_passes = df_events[df_events["eventName"] == "Pass"].copy()
    df_passes = compute_length(df_passes)
    return df_passes.groupby(group_cols).agg(meanPassLength=("lengthMeters", "mean")).reset_index()

def compute_totalShot(df_events, group_cols):
    df_shots = df_events[df_events["eventName"] == "Shot"]
    return df_shots.groupby(group_cols).agg(totalShots = ("ID", "size")).reset_index()

def compute_totalGoals(df_events, group_cols):
    df_goals = df_events[df_events["eventName"].isin(["Shot", "Free Kick"])]
    return df_goals.groupby(group_cols).agg(totalGoals= ("Goal", "sum")).reset_index()

def compute_own_goals(df_events, group_cols):
    df_ownGoal = df_events[df_events["ownGoal"] == 1].copy()

    df_ownGoal['teamID'] = np.where(
        df_ownGoal['teamID'] == df_ownGoal["homeTeamID"],
        df_ownGoal["awayTeamID"],
        df_ownGoal["homeTeamID"]
    )

    return df_ownGoal.groupby(group_cols).agg(totalOwnGoals=("ownGoal", "sum")).reset_index()

def compute_totalDuels(df_events, group_cols):
    df_duels = df_events[df_events["eventName"] == "Duel"]
    return df_duels.groupby(group_cols).agg(totalDuels=("ID", "size")).reset_index()

def compute_centroids(df_events, group_cols, centroids_events=None):
    df = df_events.copy()
    if centroids_events:
        df = df[df["eventName"].isin(centroids_events)]

    return df.groupby(group_cols).agg(
        centroidX = ("posBeforeXMeters", "mean"),
        centroidY = ("posBeforeYMeters", "mean")
    ).reset_index()

def compute_minutePlayed(df_events, group_cols, df_formations):
    match_ids = df_events["matchID"].unique()
    df_formate = df_formations[df_formations["matchID"].isin(match_ids)]

    return df_formate.groupby(group_cols).agg(
        lineup = ("lineup", "sum"),
        substituteIn = ("substituteIn", "sum"),
        substituteOut = ("substituteOut", "sum"),
        minutePlayed = ("minutePlayed", "sum")
    ).reset_index()


def compute_statistics(df_events, group_col, keep_kpis="all", drop_KPIS = None, centroid_events=None, df_formations=None):
    # Khởi tạo danh sách KPI
    all_kpis = ["totalPasses", "totalAccuratePasses", "shareAccuratePasses", "passLength", 
                "totalShots", "totalGoals", "totalDuels", "centroid", "minutePlayed", "totalPasses90"]
    
    kpis = all_kpis if keep_kpis == "all" else keep_kpis
    
    if drop_KPIS is not None:
        kpis = [kpi for kpi in kpis if kpi not in drop_KPIS]

    need_passes = "totalPasses" in kpis or "shareAccuratePasses" in kpis
    need_accurate = "totalAccurate" in kpis or "shareAccuratePasses" in kpis

    # Thiết lập bảng kết quả ban đầu dựa trên group_col
    if group_col == "player":
        target_col = "playerID"
        df_agg = df_events.groupby(target_col).agg(
            playerName=("playerName", "min"),
            playerPosition=("playerPosition", "min"),
            teamID=("teamID", lambda x: x.value_counts().index[0]),
            nbMatches=("matchID", "nunique")
        ).reset_index()
        df_agg = df_agg[df_agg[target_col] != 0]
    elif group_col == "Team":
        target_col = "teamID"
        df_agg = df_events.groupby(target_col).agg(nbMatches=("matchID", "nunique")).reset_index()
    else:
        # Xử lý cho match, player_match, team_match...
        target_col = group_col
        df_agg = df_events.groupby(target_col).agg(nbMatches=("matchID", "nunique")).reset_index()

    # Tính toán và Merge từng chỉ số
    if need_passes:
        df_var = compute_totalPasses(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalPasses": 0})

    if need_accurate:
        df_var = compute_totalAccuratePass(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalAccuratePasses": 0})

    if "passLength" in kpis:
        df_var = compute_meanPassLength(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left")

    if "shareAccuratePasses" in kpis:
        df_agg["shareAccuratePasses"] = np.round(df_agg["totalAccuratePasses"] / df_agg["totalPasses"] * 100, 2)
        df_agg["shareAccuratePasses"] = df_agg["shareAccuratePasses"].fillna(0)

    if "totalAccuratePasses" not in kpis and "totalAccuratePasses" in df_agg.columns:
        df_agg.drop(columns="totalAccuratePasses", inplace=True)

    if "totalPasses" not in kpis and "totalPasses" in df_agg.columns:
        df_agg.drop(columns="totalPasses", inplace=True)

    if "totalDuels" in kpis:
        df_var = compute_totalDuels(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalDuels": 0})

    if "totalShots" in kpis:
        df_var = compute_totalShot(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalShots": 0})

    if "totalGoals" in kpis:
        df_var = compute_totalGoals(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalGoals": 0})
        # Cộng thêm bàn phản lưới nếu thống kê theo Team/Match
        if "playerID" not in str(target_col):
            df_og = compute_own_goals(df_events, target_col)
            df_agg = pd.merge(df_agg, df_og, how="left").fillna({"totalOwnGoals": 0})
            df_agg["totalGoals"] += df_agg["totalOwnGoals"]
            df_agg.drop(columns="totalOwnGoals", inplace=True)

    if "minutePlayed" in kpis and df_formations is not None:
        df_var = compute_minutePlayed(df_events, target_col, df_formations)
        df_agg = pd.merge(df_agg, df_var, how="left")

    if "totalPasses90" in kpis and "minutePlayed" in df_agg.columns:
        df_agg["totalPasses90"] = (df_agg["totalPasses"] / df_agg["minutePlayed"] * 90).replace([np.inf, -np.inf], 0)

    if "centroid" in kpis:
        df_var = compute_centroids(df_events, target_col, centroid_events)
        df_agg = pd.merge(df_agg, df_var, how="left")

    return df_agg