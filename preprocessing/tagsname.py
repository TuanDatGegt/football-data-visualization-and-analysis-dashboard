import sys
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from preprocessing.db_config import get_engine


SQL_FOLDER = ROOT / "SQL_Query"
DATASET_FOLDER = ROOT / "dataset"
DATA_EXTRACTION_FOLDER = DATASET_FOLDER / "data_extractions"

SQL_filename = "tagsName.sql"

def load_tags_sql(filename = SQL_filename):
    """
    Read query from file tagsName.sql
    """
    path = SQL_FOLDER /filename
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file SQL: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
    


def extract_tags_mapping_query(engine = None, save_raw=True):
    """
    Extract query for mapping Description to tagID
    """
    if engine is None:
        engine  = get_engine()
    
    query = load_tags_sql()
    print(f"-----Đang truy vấn tagsName-----")
    df_tags = pd.read_sql(query, engine)

    if save_raw:
        save_path = DATA_EXTRACTION_FOLDER / "tagsName.parquet"
        df_tags.to_parquet(save_path, index=False, engine='pyarrow')
        print(f"-----Đã sao lưu file tagsName: {save_path}-----")
    
    return df_tags

if __name__ == "__main__":
    try:
        extract_tags_mapping_query()
        print(f"-----Cập nhật tagsName thành công!-----")
    except Exception as e:
        print(f"-----Lỗi hệ thống {e}-----")