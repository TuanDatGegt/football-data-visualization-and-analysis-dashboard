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

ASSIST_TAG = [301]
OWN_GOAL_TAG = [102]
KEY_PASS_TAG = [302]

def crawl_raw_data(game: int, save: bool = True):

    crawl_matchEvent_data(matchID=game, saved=save)

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
def map_to_player(df_events: pd.DataFrame, df_tags: pd.DataFrame):

    df_events = df_events.copy()
    df_tags = df_tags[["eventRecordID", "tagID", "playerID", "playerName"]]

    df_events = df_events.merge(df_tags, on="eventRecordID", how="left", suffixes=("", "_tag"))

    df_events['toPlayerID'] = np.nan
    df_events["toPLayerName"] = np.nan

    def assign_toPlayer(row):
        if row["tagID"] in ASSIST_TAG + KEY_PASS_TAG + OWN_GOAL_TAG:
            return row["playerID"], row["playerName"]
        return row["toPlayerID"], row["toPlayerName"]
    
    df_events[["toPlayerID", "toPlayerName"]] = df_events.apply(assign_toPlayer, axis=1, result_type="expand")

    df_events = df_events.drop(columns=['tagID', 'playerID', 'playerName'])

    return df_events


#--------------------------------
def preprocessing_events(df_events_raw: pd.DataFrame, df_tags: pd.DataFrame):

    df_events = df_events_raw.copy()

    home_teamID, away_teamID = map_home_away_teams(df_events_raw)
    df_events["homeTeamID"] = home_teamID
    df_events["awayTeamID"] = away_teamID

    df_events["goal"] = 0
    df_events["ownGoal"] = 0
    df_events["accurate"] = 1

    df_events = map_to_player(df_events, df_tags)

    df_events.loc[df_events['toPlayerID'].notnull() & df_events['toPlayerID'].isin(OWN_GOAL_TAG), "ownGoal"] = 1

    field_LENGTH, field_WIDTH = 105, 68

    df_events["posBeforeXMeters"] = df_events['posOrigX'] * field_LENGTH / 100
    df_events["posBeforeYMeters"] = df_events['posOrigY'] * field_WIDTH / 100
    df_events["posAfterXMeters"] = df_events['posDestX'] * field_LENGTH / 100
    df_events["posAfterYMeters"] = df_events['posDestY'] * field_WIDTH / 100
    
    return df_events


#--------------------------------
def save_transformed_file(df_events: pd.DataFrame, df_formation: pd.DataFrame, game: int):
    df_events.to_parquet(DATA_TRANSFORM_FOLDER/ f"events_transformed_{game}.parquet", index=False)
    df_formation.to_parquet(DATA_TRANSFORM_FOLDER / f"formation_transformed_{game}.parquet", index=False)


#--------------------------------
def read_metrica_event_data(game: int, save: bool = True):
    
    # 1.Crawl
    crawl_raw_data(game, saved=save)

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
    df_events, df_formations = read_metrica_event_data(GAME_ID)
    print(df_events.head)
    print(df_formations.head())  
#--------------------------------
#--------------------------------
#--------------------------------
