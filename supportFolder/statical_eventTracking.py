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

def compute_centroids(df_events, group_cols, centroid_events=None):
    df = df_events.copy()
    if centroid_events is not None:
        df = df[df["eventName"].isin(centroid_events)]

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
    all_kpis = ["totalPasses", "totalAccuratePasses", "shareAccuratePasses", "meanPassLength", 
                "totalShots", "totalGoals", "totalDuels", "centroid", "minutePlayed", "totalPasses90"]
    
    kpis = all_kpis if keep_kpis == "all" else keep_kpis
    
    if drop_KPIS is not None:
        kpis = [k for k in kpis if k not in drop_KPIS]

    
    need_passes = ("totalPasses" in kpis or "shareAccuratePasses" in kpis or "totalPasses90" in kpis)

    need_accurate = ("totalAccuratePasses" in kpis or "shareAccuratePasses" in kpis)

    # Thiết lập bảng kết quả ban đầu dựa trên group_col
    if group_col == "player":
        target_col = "playerID"
        df_agg = (df_events.groupby(target_col).agg(
            playerName=("playerName", "min"),
            playerPosition=("playerPosition", "min"),
            teamID=("teamID", lambda x: x.value_counts().index[0]),
            nbMatches=("matchID", "nunique")
        ).reset_index())
        df_agg = df_agg[df_agg[target_col] != 0]

    elif group_col == "team":
        target_col = "teamID"
        df_agg = (df_events.groupby(target_col).agg(nbMatches=("matchID", "nunique")).reset_index())

    elif group_col == "match":
        target_col = "matchID"
        df_agg = (df_events.groupby(target_col).agg(nbMatches=("matchID", "nunique")).reset_index())

    elif group_col == "player_match":
        target_col = ["playerID", "matchID"]
        df_agg = (df_events.groupby(target_col).agg(
            playerName=("playerName", "min"),
            playerPosition=("playerPosition", "min"),
            teamID=("teamID", lambda x: x.value_counts().index[0]),
            nbMatches=("matchID", "nunique")
        ).reset_index())
        df_agg = df_agg[df_agg["playerID"] != 0]

    elif group_col == "team_match":
        target_col=["teamID", "matchID"]
        df_agg = (df_events.groupby(target_col).agg(nbMatches=("matchID", "nunique")).reset_index())

    else:
        raise ValueError("Nhóm cột không tồn tại trong mô hình")
    

    # Tính toán và Merge từng chỉ số
    if need_passes:
        df_var = compute_totalPasses(df_events, target_col) 
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalPasses": 0})


    if need_accurate:
        df_var = compute_totalAccuratePass(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalAccuratePasses": 0})


    if "shareAccuratePasses" in kpis:
        df_agg["shareAccuratePasses"] = np.where(
            df_agg["totalPasses"] > 0,
            np.round(df_agg["totalAccuratePasses"] / df_agg["totalPasses"] * 100, 2),0
        )

        if "totalPasses" not in kpis:
            df_agg.drop(columns="totalPasses", inplace=True)
        if "totalAccuratePasses" not in kpis:
            df_agg.drop(columns="totalAccuratePasses", inplace=True)
    

    if "meanPassLength" in kpis:
        df_var = compute_meanPassLength(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left")


    if "totalShots" in kpis:
        df_var = compute_totalShot(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalShots": 0})

    
    if "totalGoals" in kpis:
        df_var = compute_totalGoals(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalGoals": 0})

        is_player_level = (
            target_col == "playerID" or
            (isinstance(target_col, list) and "playerID" in target_col)
        )

        # Cộng thêm bàn phản lưới nếu thống kê theo Team/Match
        if not is_player_level:
            df_og = compute_own_goals(df_events, target_col)
            df_agg = pd.merge(df_agg, df_og, how="left").fillna({"totalOwnGoals": 0})
            df_agg["totalGoals"] += df_agg["totalOwnGoals"]
            df_agg.drop(columns="totalOwnGoals", inplace=True)


    if "totalDuels" in kpis:
        df_var = compute_totalDuels(df_events, target_col)
        df_agg = pd.merge(df_agg, df_var, how="left").fillna({"totalDuels": 0})

    
    if ("minutePlayed" in kpis and df_formations is not None and (
        target_col=="playerID" or (isinstance(target_col, list) and "playerID" in target_col))):
        df_var = compute_minutePlayed(df_events, target_col, df_formations)
        df_agg = pd.merge(df_agg, df_var, how="left")

    if "totalPasses90" in kpis and "minutePlayed" in df_agg.columns:
        df_agg["totalPasses90"] = (
            df_agg["totalPasses"] / df_agg["minutePlayed"] * 90).replace([np.inf, -np.inf], 0)
        
    
    if "centroid" in kpis:
        df_var = compute_centroids(df_events, target_col, centroid_events if centroid_events is not None else None)
        df_agg = pd.merge(df_agg, df_var, how="left")


    return df_agg

def number_pass_accurate(df_events, team_id):
    df_team = df_events[df_events["teamID"] == team_id].copy()
    df_team.sort_values(["matchID", "matchPeriod", "eventSec"], inplace=True)

    df_team["nextPlayerID"] = df_team.groupby(["matchID", "matchPeriod"])["playerID"].shift(-1)

    df_passes = df_team[
        (df_team["eventName"] == "Pass") & (df_team["accurate"] == 1)
    ].copy()

    df_passes = df_passes.dropna(subset=["nextPlayerID"])

    df_passes["player1ID"] = np.where(
        df_passes["playerID"] < df_passes["nextPlayerID"],
        df_passes["playerID"],
        df_passes["nextPlayerID"]
    )

    df_passes["player2ID"] = np.where(
        df_passes["playerID"] < df_passes["nextPlayerID"],
        df_passes["nextPlayerID"],
        df_passes["playerID"]
    )

    df_passes_count = (
        df_passes.groupby(["player1ID", "player2ID"]).agg(totalPasses=("playerID", "count")).reset_index()
    )

    return df_passes_count



#==========================
#Các hàm hỗ trợ tính toán vị trí bóng trên từng khung hình
PITCH_LENGTH = 105.0
PITCH_WIDTH = 68.0

GOAL_CENTER_HOME = (0.0, PITCH_WIDTH / 2)
GOAL_CENTER_AWAY = (PITCH_LENGTH, PITCH_WIDTH / 2)

PASS_SUBEVENTS = {
    "Cross", "Hand pass", "Head pass",
    "High pass", "Launch", "Simple pass", "Smart pass"
}

DUEL_SUBEVENTS = {
    "Air duel", "Ground attacking duel",
    "Ground defending duel", "Ground loose ball duel"
}

STOP_SUBEVENTS = {
    "Ball out of the field", "Whistle", "Offside"
}

def valid_pos(x, y):
    return pd.notna(x) and pd.notna(y) and not (x == 0 and y == 0)


def get_attacking_goal(row):
    is_home = row["teamID"] == row["homeTeamID"]
    is_first_half = row["matchPeriod"] == "1H"

    if is_first_half:
        return GOAL_CENTER_AWAY if is_home else GOAL_CENTER_HOME
    else:
        return GOAL_CENTER_HOME if is_home else GOAL_CENTER_AWAY
    

def infer_ball_target(row):
    x0, y0 = row["posBeforeXMeters"], row["posBeforeYMeters"]
    x1, y1 = row.get("posAfterXMeters"), row.get("posAfterYMeters")

    event = row["eventName"]
    sub = row.get("subEventName", "")
    is_goal = row.get("Goal", 0) == 1

    # SHOT → GOAL
    if event == "Shot" and is_goal:
        return get_attacking_goal(row)

    # PASS / CLEARANCE / TOUCH
    if event == "Pass" or sub in PASS_SUBEVENTS or sub in {"Clearance", "Touch"}:
        if valid_pos(x1, y1):
            return x1, y1
        return x0, y0

    # SAVE ATTEMPT
    if event == "Save attempt":
        if valid_pos(x1, y1):
            return x1, y1
        gx, gy = get_attacking_goal(row)
        return gx + (2 if gx == 0 else -2), gy

    # DUEL → bóng rung nhẹ
    if event == "Duel" or sub in DUEL_SUBEVENTS:
        return x0 + np.random.uniform(-1, 1), y0 + np.random.uniform(-1, 1)

    # FOUL / INTERRUPTION
    if event == "Foul" or sub in STOP_SUBEVENTS:
        return x0, y0

    return x0, y0


def event_to_ball_frames(row, fps=25):
    x0, y0 = row["posBeforeXMeters"], row["posBeforeYMeters"]
    if pd.isna(x0) or pd.isna(y0):
        return []

    xt, yt = infer_ball_target(row)

    if np.isclose([x0, y0], [xt, yt]).all():
        return [{"xPos": x0, "yPos": y0}]

    xs = np.linspace(x0, xt, fps)
    ys = np.linspace(y0, yt, fps)

    return [{"xPos": x, "yPos": y} for x, y in zip(xs, ys)]


def infer_target_player(row, next_row):
    """
    Infer receiver / shooter / next actor
    """
    if next_row is None:
        return None

    if (
        row["teamID"] == next_row["teamID"] and
        next_row["eventSec"] - row["eventSec"] <= 3 and
        valid_pos(next_row["posBeforeXMeters"], next_row["posBeforeYMeters"])
    ):
        return {
            "playerID": next_row["playerID"],
            "playerName": next_row.get("playerName"),
            "team": "Home" if next_row["teamID"] == next_row["homeTeamID"] else "Away",
            "xPos": next_row["posBeforeXMeters"],
            "yPos": next_row["posBeforeYMeters"]
        }

    return None


def mean_position_player(df_events):
    df = df_events[
        df_events["posBeforeXMeters"].notna() &
        df_events["posBeforeYMeters"].notna()
    ].copy()

    df["team"] = np.where(
        df["teamID"] == df["homeTeamID"], "Home", "Away"
    )

    return (
        df.groupby(["playerID", "team"], as_index=False)
          .agg(
              centroidX=("posBeforeXMeters", "mean"),
              centroidY=("posBeforeYMeters", "mean")
          )
    )


def build_event_tracking(df_events: pd.DataFrame, event_ids, fps: int = 25):
    """
    Event-based pseudo tracking
    - PLAYER_OWNER  : event owner
    - PLAYER_TARGET : receiver / shooter
    - BALL          : inferred trajectory
    """

    frames = []
    global_frame = 0

    df_phase = (
        df_events[df_events["ID"].isin(event_ids)]
        .sort_values("eventSec")
        .reset_index(drop=True)
    )

    if df_phase.empty:
        return pd.DataFrame(frames)

    for i, row in df_phase.iterrows():
        next_row = df_phase.iloc[i + 1] if i + 1 < len(df_phase) else None

        x0, y0 = row["posBeforeXMeters"], row["posBeforeYMeters"]
        if not valid_pos(x0, y0):
            continue

        team_label = "Home" if row["teamID"] == row["homeTeamID"] else "Away"

        ball_frames = event_to_ball_frames(row, fps=fps)
        if not ball_frames:
            continue

        target_player = infer_target_player(row, next_row)

        for b in ball_frames:

            # ---- OWNER
            frames.append({
                "frame": global_frame,
                "entityType": "PLAYER_OWNER",
                "playerID": row["playerID"],
                "playerName": row.get("playerName"),
                "team": team_label,
                "xPos": x0,
                "yPos": y0,
                "eventID": row["ID"],
                "eventName": row["eventName"]
            })

            # ---- TARGET
            if target_player:
                frames.append({
                    "frame": global_frame,
                    "entityType": "PLAYER_TARGET",
                    **target_player,
                    "eventID": row["ID"]
                })

            # ---- BALL
            frames.append({
                "frame": global_frame,
                "entityType": "BALL",
                "team": "Ball",
                "xPos": b["xPos"],
                "yPos": b["yPos"],
                "eventID": row["ID"]
            })

            global_frame += 1

    return pd.DataFrame(frames)


def filter_time_windows(df, match_id, period, start_sec, end_sec):

    return(
        df[
            (df["matchID"] ==   match_id) &
            (df["matchPeriod"] == period) &
            (df["eventSec"] >= start_sec) &
            (df["eventSec"] <= end_sec)
        ].sort_values("eventSec").copy())


def single_event_phases(df_events, eventName, preSec=10, postSec=2):
    phases=[]

    targets = df_events[df_events["eventName"] == eventName]

    for _, ev in targets.iterrows():
        start = max(0, ev["eventSec"] - preSec)
        end = ev["eventSec"] + postSec

        phase = filter_time_windows(df_events, ev["matchID"], ev["matchPeriod"], start, end)

        if not phase.empty:
            phases.append(phase)
    return phases


def pair_event_phases(df_events, event_pair, preSec=6, postSec=2, timeGap = 4):

    e1, e2 = event_pair
    phases = []

    df = df_events.sort_values(
        ["matchID", "matchPeriod", "eventSec"]
    ).reset_index(drop=True)

    for i in range(len(df) - 1):
        r1 = df.loc[i]
        r2 = df.loc[i + 1]

        if(
            r1["eventName"] == e1 and 
            r2["eventName"] == e2 and
            r1["teamID"] == r2["teamID"] and
            r1["matchID"] == r2["matchID"] and
            r1["matchPeriod"] == r2["matchPeriod"] and
            (r2["eventSec"] - r1["eventSec"]) <= timeGap
        ):
            
            start = max(0, r1["eventSec"] - preSec)
            end = r2["eventSec"] + postSec

            phase = filter_time_windows(df_events, r1["matchID"], r2["matchPeriod"], start, end)

            if not phase.empty:
                phases.append(phase)

    return phases


def lead_to_goal_phases(df_events, preSec=15, postSec=2, allowed_events=None):
    
    phases = []

    df = df_events.sort_values(
        ["matchID", "matchPeriod", "eventSec"]
    )

    goals = df[df["Goal"] == 1]


    for _, goal in goals.iterrows():
        start = max(0, goal["eventSec"] - preSec)
        end = goal["eventSec"] + postSec

        phase = filter_time_windows(df, goal["matchID"], goal["matchPeriod"], start, end)

        phase = phase[phase["teamID"] == goal["teamID"]]

        if allowed_events is not None:
            phase = phase[phase["eventName"].isin(allowed_events)]

        if not phase.empty:
            phases.append(phase)

    return phases


def select_hightlight_events(df_events, event_types, preSec=10, postSec=2, timeGap=4, allowed_events=None):

    if isinstance(event_types, str):
        if event_types == "LEAD_TO_GOAL":
            return lead_to_goal_phases(df_events, preSec, postSec, allowed_events)
        else:
            return single_event_phases(df_events, event_types, preSec, postSec)
    
    if isinstance(event_types, tuple) and len(event_types) == 2:
        return pair_event_phases(df_events, event_types, preSec, postSec, timeGap)
    
    raise ValueError(f"{event_types} Không hợp lệ")




