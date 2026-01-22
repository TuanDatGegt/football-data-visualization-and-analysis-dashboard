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


def load_event_data_kpis(matchID: int = 2500045) -> pd.DataFrame:
    """
    Load event data for ONE match
    Used by:
    - overview_data.py
    - xG tab
    - shots map
    """

    file_path = DATA_TRANSFORM_DIR / f"events_transformed_{matchID}.parquet"

    if not file_path.exists():
        return pd.DataFrame()

    df = pd.read_parquet(file_path)

    # safety check
    if df["matchID"].nunique() > 1:
        raise ValueError("Event file contains multiple matchID")

    return df


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




def list_video_phases(match_id: int):
    """
    Return available phase IDs for a match
    """
    if not VIDEO_DIR.exists():
        return []

    phases = []
    for p in VIDEO_DIR.glob(f"video_{match_id}_phase*.mp4"):
        try:
            phase_id = int(p.stem.split("phase")[-1])
            phases.append(phase_id)
        except ValueError:
            continue

    return sorted(phases)