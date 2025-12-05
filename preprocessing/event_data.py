# -*- coding: utf-8 -*-

# import packages
import numpy as np
import pandas as pd

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
