import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "dataset"

DATA_TRANSFORM_DIR = DATASET_DIR / "data_transforms"
DATA_MODEL_DIR = DATASET_DIR / "dataModel"
VIDEO_DIR = DATASET_DIR / "video_"


def load_event_data(
    shots_only=True,
    file_name="event_data_transform.parquet"
):
    """
    Load transformed event data (events / shots)
    """
    path = DATA_TRANSFORM_DIR / file_name
    df_events = pd.read_parquet(path)

    if shots_only:
        return df_events[df_events["eventName"] == "Shot"].copy()

    return df_events

def load_xg_data(split="train"):
    """
    Load xG model data
    split: 'train' | 'test'
    """
    if split == "train":
        path = DATA_MODEL_DIR / "df_train_xG.parquet"
    elif split == "test":
        path = DATA_MODEL_DIR / "df_test_xG.parquet"
    else:
        raise ValueError("split must be 'train' or 'test'")

    return pd.read_parquet(path)

"""
def load_video_event_data(match_id: int):
    #Load event data used for video tracking / phases
    file_name = f"events_transformed_{match_id}.parquet"
    path = DATA_TRANSFORM_DIR / file_name

    if not path.exists():
        raise FileNotFoundError(f"{file_name} not found")

    return pd.read_parquet(path)
"""

