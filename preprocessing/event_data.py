# import packages
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from preprocessing.db_config import get_engine
from preprocessing.tagsname import extract_tags_mapping_query

## CẤU HÌNH ĐƯỜNG DẪN
ROOT = Path(__file__).resolve().parent.parent
SQL_FOLDER = ROOT / "SQL_Query"
DATASET_FOLEDER = ROOT / "dataset"
DATA_EXTRACTION_FOLDER = DATASET_FOLEDER / "data_extractions"
DATA_TRANSFORM_FOLDER = DATASET_FOLEDER / "data_transforms"

sys.path.append(str(ROOT))

events_filename = 'data_Wyscount_event.sql'
tagsname_filename = 'tagsName.sql'

def load_sql_file(filename):
    path = SQL_FOLDER /filename
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay file SQL: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    
def extract_events_data(engine = None):
    """
    Extract data event.
    """
    #Extract event dataset and save file extractions
    event_query = load_sql_file(events_filename)
    df_events = pd.read_sql(event_query, engine)

    extract_events_path = DATA_EXTRACTION_FOLDER / "events_raw.parquet"
    df_events.to_parquet(extract_events_path, index=False, engine='pyarrow')
    print(f"Save a backup of raw data events: {extract_events_path}")

    return df_events

def apply_tags_pivot(df_events, df_tags):
    """
    Extract tags name from tagsName.sql and mapping tags with events
    """
    df_tags = extract_tags_mapping_query(engine = None)
    tags_pivot = df_tags.pivot_table(
        index= 'eventRecordID',
        columns='Description',
        aggfunc='size',
        fill_value=0
    ).reset_index()

    tag_cols = [c for c in tags_pivot.columns if c != 'eventRecordID']
    tags_pivot[tag_cols] = (tags_pivot[tag_cols] > 0).astype(int)

    df = pd.merge(df_events, tags_pivot, on='eventRecordID', how='left')
    df[tag_cols] = df[tag_cols].fillna(0).astype(int)

    if 'Accurate' in df.columns:
        df['accurate_flag'] = df['Accurate']
    elif 'Not accurate' in df.columns:
        df['accurate_flag'] = 1 - df['Not accurate']
    else:
        df['accurate_flag'] = 0

    return df, tag_cols    

def clean_and_convert_positions(df, field_length = 105, field_width = 68):
    """
    Normalization positions before convert to metter. Computes the position in meters instead of only a 0-100 scale.
    
    :param df: (pd.DataFrame) Data frame containing x and/or y coordinates
    :param cols_length: (list) Columns that contain values in x-direction
    :param cols_width: (list) Columns that containt values in y-direction
    :param field_length: (int) Length of the field in meters
    :param field_width: (int) Width of the field in meters
    :return: pd.DataFrame with additional columns ending in "Meters" that contain the coordinates in meters.
    """
    df.loc[df['subEventName'] == 'Goal kick', ['posOrigX', 'posOrigY']] == [5, 50]
    mask_save = df['subEventName'].isin(['Save attempt', 'Reflexes'])
    df.loc[mask_save, ['posOrigX', 'posOrigY']] == [0, 50]

    #Conver position to Meters
    df['posBeforeXMeter'] = np.round(df['posOrigX'] * field_length / 100, 2)
    df['posBeforeYMeter'] = np.round(df['posOrigY'] * field_width / 100, 2)
    df['posAfterXMeter'] = np.round(df['posDestX'] * field_length / 100, 2)
    df['posAfterYMeter'] = np.round(df['posDestY'] * field_width / 100, 2)

    return df.drop(columns = ['posOrigX', 'posOrigY', 'posDestX', 'posDestY'])

def compute_possession(df):
    """
    comput column teamPossession
    """

    pos = pd.Series(np.nan, index = df.index())

    active = ['Pass', 'Free kick', 'Others on the ball', 'Shot', 'Save attempt']
    pos.loc[df['eventName'].isin(active)] = df['teamID']

    is_duel = (df['eventName'] == 'Duel')
    acc = df['accurate_flag']

    pos.loc[is_duel & (acc==1)] = df['teamID']

    is_home = (df['teamID'] == df['homeTeamID'])
    pos.loc[is_duel & (acc == 0) & is_home] = df['awayTeamID']
    pos.loc[is_duel & (acc == 0) & (~is_home)] = df['homeTeamID']

    pos.loc[df['eventName'].isin(['Foul', 'Interruption', 'Offside'])] = 0
    
    return pos

def compute_bodyPartShot(df):
    """
    Docstring for compute_bodyPartShot
    
    :param df: Description
    """
    left = df['Left foot'] if 'Left foot' in df.columns else pd.Series(0, index=df.index)
    right = df['Right foot'] if 'Right foot' in df.columns else pd.Series(0, index=df.index)
    head_body = df['Head/body'] if 'Head/body' in df.columns else pd.Series(0, index = df.index)

    conditions = [
        (left == 1),
        (head_body == 1),
        (right == 1)
    ]

    choice_str = ['leftFoot', 'head/body', 'rightFoot']

    choice_code = [1, 2, 3]

    df['bodyPartShot'] = np.select(conditions, choice_str, default='Unknown')
    df['bodyPartShotCode'] = np.select(conditions, choice_code, default= 0)

    return df

def finalized_transform(df, extra_tags):
    df['teamPossession'] = compute_possession(df)

    df = compute_bodyPartShot(df)

    rename_map = {
        "eventRecordID": "ID",
        "Sname": "playerName",
        "pRole": "playerPosition",
        "foot": "playerStrongFoot",
        "accurate_flag": "accurate"
    }

    df.rename(columns = rename_map, inplace=True)
    
    base_cols = [
        'ID', 'matchID', 'matchPeriod', 'eventSec', 'eventName', 'subEventName', 'teamID',
        'posBeforeXMeters', 'posBeforeYMeters', 'posAfterXMeters', 'posAfterYMeters', 'playerID',
        'playerName', 'playerPosition', 'playerStrongFoot', 'teamPossession', 'homeTeamID', 'awayTeamID', 'accurate', 'notAccurate', 'bodyPartShot', 'bodyPartShotCode'
    ]

    all_cols = base_cols + [c for c in extra_tags if c not in ['Accurate', 'Not accurate', 'Left foot', 'Right foot', 'Head/body']]

    final_cols = [c for c in all_cols if c not in df.columns]

    return df[final_cols]

def run_pipeline():
    engine = engine

    df_raw = extract_events_data(engine)

    df_map, tag_cols = apply_tags_pivot(df_raw, engine)

    df_clean = clean_and_convert_positions(df_map)

    df_final = finalized_transform(df_clean, tag_cols)

    output_path = DATA_TRANSFORM_FOLDER / "event_data_transform.parquet"
    df_final.to_parquet(output_path, engine='pyarrow', index = False)

    print(f"Transform Event Data Compeletely!")

    return df_final

if __name__ == "__main__":
    run_pipeline()

    