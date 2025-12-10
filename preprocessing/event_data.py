# import packages
import sys
import numpy as np
import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from preprocessing.db_config import get_engine

SQL_FOLDER = ROOT / "SQL_Query"

def load_sql_file(filename='event_data.sql'):
    path = SQL_FOLDER /filename
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay file SQL: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    
def load_event_data(sql_filename = 'event_data.sql', engine = None):
    if engine is None:
        engine = get_engine()
    query = load_sql_file(sql_filename)
    df = pd.read_sql(query, engine)
    return df


def cleaning_positions(df):
    """
    Normalization positions before convert to metter.
    :param df: DataFrame of head for nomalization
    """

    #Sửa subEventName có nhãn Goal kick về vị trí ở cầu môn nhà(5, 50)
    df['posOrigX'] = np.where(
        df['subEventName'] == 'Goal kick', 5, df['posOrigX']
    )
    df['posOrigY'] = np.where(
        df['subEventName'] == 'Goal kick', 50, df['posOrigY']
    )


    #Sửa subEventName có Save attempt và Reflexes về vị trí thủ môn nhà (0, 50)
    df['posOrigX'] = np.where(
        df['subEventName'].isin(['Save attempt', 'Reflexes']), 0, df['posOrigX']
    )
    df['posOrigY'] = np.where(
        df['subEventName'].isin(['Save attempt', 'Reflexes']), 50, df['posOrigY']
    )
    return df



def add_position_in_meters(df_events, cols_length, cols_width, field_length, field_width):
    """
    Docstring for add_position_in_meters: This function use for computes the position in meters instead of only a 0-100 scale.
    
    :param df: (pd.DataFrame) Data frame containing x and/or y coordinates
    :param cols_length: (list) Columns that contain values in x-direction
    :param cols_width: (list) Columns that containt values in y-direction
    :param field_length: (int) Length of the field in meters
    :param field_width: (int) Width of the field in meters
    :return: pd.DataFrame with additional columns ending in "Meters" that contain the coordinates in meters.
    """
    df = df_events.copy()

    for col in cols_length:
        df[col + "Meters"] = np.where(
            df[col].notnull(), df[col]*field_length / 100, np.nan
        )
        df[col + "Meters"] = np.round(df[col + "Meters"], 2)
    for col in cols_width:
        df[col + "Meters"] = np.where(
            df[col].notnull(), df[col]*field_width / 100, np.nan
        )
        df[col + "Meters"] = np.round(df[col + "Meters"], 2)

    df = df.drop(columns = cols_length + cols_width)

    return df

#add_position_in_meters(df_events=df, , field_length=105, field_width=68)
def load_and_process_event_data(sql_filename='event_data.sql', field_length=105, field_width=68, cols_length=["posOrigX", "posDestX"], cols_width=["posOrigY", "posDestY"], engine = None):
    df = load_event_data(sql_filename, engine)
    df = cleaning_positions(df)
    df = add_position_in_meters(df, cols_length, cols_width, field_length, field_width)

    return df

"""
def set_positions(df_events, reverse, field_length=105, field_width = 68):
    '''
    Docstring for set_positions
    
    :param df_events: Description
    :param reverse: Description
    :param field_length: Description
    :param field_width: Description
    '''

    pos_cols = ['posOrigX', 'posOrigY', 'posDestX', 'posDestY']

    for col in pos_cols:
        df_events[col].clip(lower=0, upper=1, inplace=True)

        if reverse:
            df_events[col] = 1-df_events[col]
"""