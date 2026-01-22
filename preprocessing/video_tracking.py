import sys
from pathlib import Path
import pandas as pd
import numpy as np

# ===============================
# Path & project setup
# ===============================
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

DATA_EXTRACTION_FOLDER = ROOT / "dataset" / "data_extractions"
DATA_TRANSFORM_FOLDER = ROOT / "dataset" / "data_transforms"
DATA_TRANSFORM_FOLDER.mkdir(parents=True, exist_ok=True)



# ===============================
# Import crawler
# ===============================
from preprocessing.db_config import get_engine
from supportFolder.cralw_eventData import crawl_matchEvent_data

#--------------------------------
#Tag mapping for toPlayer
GOAL_TAG = 101
OWN_GOAL_TAG = 102
ASSIST_TAG = 301
KEY_PASS_TAG = 302
ACCURATE_TAG = 1801
NOT_ACCURATE_TAG = 1802

#frame per seconds
FPS = 25
FIELD_LENGTH = 105
FIELD_WIDTH = 68


#--------------------------------
#load file
def load_raw_parquet(game: int):
    
    df_event_raw = pd.read_parquet(DATA_EXTRACTION_FOLDER / f"event_tracking_raw_{game}.parquet")
    df_tags_raw = pd.read_parquet(DATA_EXTRACTION_FOLDER / f"event_tags_raw_{game}.parquet")
    df_formations_raw = pd.read_parquet(DATA_EXTRACTION_FOLDER / f"formation_timeline_raw_{game}.parquet")

    return df_event_raw, df_tags_raw, df_formations_raw


#--------------------------------
# Mapping hometeam and awayteam
def map_home_away_teams(df_events_raw: pd.DataFrame):

    home_team_id = df_events_raw[df_events_raw["side"] == "home"]['teamID'].unique()[0]
    away_team_id = df_events_raw[df_events_raw["side"] == "away"]['teamID'].unique()[0]

    return home_team_id, away_team_id


#--------------------------------
def mapping_tags_to_mertrics(df_events: pd.DataFrame, df_tags: pd.DataFrame):
    """
    Lấy tag từ fỉle event_tags ánh xạ qua file event_tracking
    """
    goal_ids = set(df_tags[df_tags["tagID"] == GOAL_TAG]['eventRecordID'])
    own_goal_ids = set(df_tags[df_tags["tagID"] == OWN_GOAL_TAG]['eventRecordID'])
    accurate_ids = set(df_tags[df_tags["tagID"] == ACCURATE_TAG]['eventRecordID'])
    not_accurate_ids = set(df_tags[df_tags["tagID"] == NOT_ACCURATE_TAG]['eventRecordID'])

    df_events["Goal"] = df_events["eventRecordID"].apply(lambda x: 1 if x in goal_ids else 0)
    df_events["ownGoal"] = df_events["eventRecordID"].apply(lambda x: 1 if x in own_goal_ids else 0)

    def check_accurate(event_id):
        if event_id in accurate_ids: return 1
        if event_id in not_accurate_ids: return 0
        return 1
    
    df_events ["accurate"] = df_events["eventRecordID"].apply(check_accurate)

    return df_events


#--------------------------------
def preprocessing_events(df_events_raw: pd.DataFrame, df_tags: pd.DataFrame):

    df_events = df_events_raw.copy()
    
    homeTeamID, awayTeamID = map_home_away_teams(df_events_raw)
    df_events["homeTeamID"] = homeTeamID
    df_events["awayTeamID"] = awayTeamID

    df_events = mapping_tags_to_mertrics(df_events, df_tags)

    df_events["posBeforeXMeters"] = df_events["posOrigX"] * FIELD_LENGTH / 100
    df_events["posBeforeYMeters"] = df_events["posOrigY"] * FIELD_WIDTH / 100
    df_events["posAfterXMeters"] = df_events["posDestX"] * FIELD_LENGTH / 100
    df_events["posAfterYMeters"] = df_events["posDestY"] * FIELD_WIDTH / 100

    df_events["eventSecEnd"] = df_events.groupby("matchPeriod")['eventSec'].shift(-1)

    df_events["toPlayerID"] = df_events.groupby("matchPeriod")["playerID"].shift(-1)
    df_events["toPlayerName"] = df_events.groupby("matchPeriod")["playerName"].shift(-1)
    
    maxGap = 5.0
    maskGap = (df_events["eventSecEnd"] - df_events["eventSec"]) > maxGap
    df_events.loc[maskGap, "eventSecEnd"] = df_events.loc[maskGap, "eventSec"] + 1.2

    df_events["eventSecEnd"] = df_events["eventSecEnd"].fillna(df_events["eventSec"] + 1.0)

    df_events["startFrame"] = (df_events["eventSec"] * FPS).astype(int)
    df_events["endFrame"] = (df_events["eventSecEnd"] * FPS).astype(int)

    maskInvalid = df_events["startFrame"] >= df_events["endFrame"]
    df_events.loc[maskInvalid, "endFrame"] = df_events.loc[maskInvalid, "startFrame"] + 1

    df_events["Team"] = df_events["side"].str.capitalize()

    cols_rename = {
        'eventRecordID': 'ID',
        'playerRole': 'playerPosition'
    }

    df_final = df_events.rename(columns=cols_rename)

    final_columns = ['ID', 'matchID', 'matchPeriod', 'eventSec', 'eventSecEnd', 
        'startFrame', 'endFrame', 'eventName', 'subEventName', 
        'teamID', 'Team', 'posBeforeXMeters', 'posBeforeYMeters', 
        'posAfterXMeters', 'posAfterYMeters', 'playerID', 'playerName', 
        'playerPosition', 'toPlayerID', 'toPlayerName', 'homeTeamID', 
        'awayTeamID', 'accurate', 'Goal', 'ownGoal']

    existing_cols = [c for c in final_columns if c in df_final.columns]

    return df_final[existing_cols]


#--------------------------------
def save_transformed_file(df_events: pd.DataFrame, df_formation: pd.DataFrame, game: int):
    df_events.to_parquet(DATA_TRANSFORM_FOLDER/ f"events_transformed_{game}.parquet", index=False)
    df_formation.to_parquet(DATA_TRANSFORM_FOLDER / f"formation_transformed_{game}.parquet", index=False)


#--------------------------------
def read_metrica_event_data(game: int, saved: bool = True):

    print(f"\n____Xử lý dữ liệu trận: {game}___")

    # 2.Load
    df_event_raw, df_tags_raw, df_formation= load_raw_parquet(game)

    # 3.Transforms data
    df_events = preprocessing_events(df_event_raw, df_tags_raw)

    # 4. Save transform data
    save_transformed_file(df_events, df_formation, game)

    return df_events, df_formation


#--------------------------------
if __name__ == "__main__":
    GAME_ID = 2500045
    df_ev, df_form = read_metrica_event_data(GAME_ID)
    
    # Kiểm tra thử 10 dòng đầu
    print("\n[Preview Data]")
    print(df_ev[['Team', 'eventName', 'eventSec', 'eventSecEnd', 'startFrame', 'endFrame', 'toPlayerID']].head(10))
#--------------------------------
#--------------------------------
#--------------------------------















"""
    dicts = dict{
        "Manchester City - Manchester United": 2500045, #England (ngau nhien)
        "Portugal - France": 1694440, #European Champion League (National) (vô dich giai dau)
        "Monaco - Olympique Lyonnais": 2500920, #Ligue 1 (France) (duoc danh gia tot nhung lai da kem)
        "Bayern Mucnchen - Stuttgart": 2517036, #Germany (doi bong noi tieng)
        "SPAL - Sampdoria": 2576337, #Germany (da tot mua giai khi bi danh gia kem)
        "Barcelona - Real Madrid": 2565907, #Spain Doi thi dau giu duoc thu hang tot nhat
        "France - Croatia": 2058017 # Doi vo dich world cup 2018 Mbappé toa sang trong thi dau
"""