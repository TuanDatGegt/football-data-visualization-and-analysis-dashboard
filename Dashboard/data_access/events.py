# Dashboard/data_access/events.py
from pathlib import Path
import pandas as pd

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DASHBOARD_ROOT.parent

DATASET_DIR = PROJECT_ROOT / "dataset"
DATA_TRANSFORM_DIR = DATASET_DIR / "data_transforms"
DATA_MODEL_DIR = DATASET_DIR / "dataModel"

ASSETS_DIR = DASHBOARD_ROOT / "assets"
VIDEO_DIR = ASSETS_DIR / "video"


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
    Return available phase IDs for a match (from assets/video)
    """
    if not VIDEO_DIR.exists():
        return []

    phases = set()

    for p in VIDEO_DIR.glob(f"match_{match_id}_phase_*_*.mp4"):
        try:
            phase = int(p.stem.split("_phase_")[1].split("_")[0])
            phases.add(phase)
        except (IndexError, ValueError):
            continue

    return sorted(phases)


def list_matches_with_video():
    """
    Return sorted list of match IDs that have videos
    """
    if not VIDEO_DIR.exists():
        return []

    match_ids = set()

    for p in VIDEO_DIR.glob("match_*_phase_*_*.mp4"):
        try:
            match_id = int(p.stem.split("_")[1])
            match_ids.add(match_id)
        except (IndexError, ValueError):
            continue

    return sorted(match_ids)
