import pandas as pd
import numpy as np
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

SQL_FOLDER = ROOT / "SQL_Query"
DATA_EXTRACTION_FOLDER = ROOT / "dataset" / "data_extractions"

DATA_EXTRACTION_FOLDER.mkdir(parents=True, exist_ok=True)

from preprocessing.db_config import get_engine



def load_sql_file(filename: str) -> str:
    path = SQL_FOLDER / filename
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy script file SQL: {path}")
    return path.read_text(encoding="utf-8")



def inject_matchID(sql: str, matchID: int) -> str:

    """
    Replace: DECLARE @game INT by DECLARE @game INT = matchID
    """

    return sql.replace(
        "DECLARE @game INT;",
        f"DECLARE @game INT = {matchID};"
    )



def extract_and_save(engine, sql_filename: str, matchID: int, output_name: str):
    raw_sql = load_sql_file(sql_filename)
    sql = inject_matchID(raw_sql, matchID)

    df = pd.read_sql(sql, engine)

    output_path = DATA_EXTRACTION_FOLDER / f"{output_name}_{matchID}.parquet"
    df.to_parquet(output_path, index=False)

    print(f"Đã lưu thành công file: {output_path} ({len(df)} row)")
    return df



def crawl_matchEvent_data(matchID: int):
    engine = get_engine()

    print(f"\n Lấy thông tin dữ liệu cho trận đấu matchID = {matchID}")

    extract_and_save(engine, sql_filename="event_tracking.sql", matchID=matchID, output_name="event_tracking_raw")

    extract_and_save(engine, sql_filename="event_tags.sql", matchID=matchID, output_name="event_tags_raw")

    extract_and_save(engine, sql_filename="formation_timeline.sql", matchID=matchID, output_name="formation_timeline_raw")

    print("\n Thu thập thông tin từ CSDL hệ thống thành công.")


if __name__ == "__main__":
    MATCH_ID = 2499767
    """
    dicts = dict{
        "Manchester City - Manchester United": 2500045, #England (ngau nhien)
        "Portugal - France": 1694440, #European Champion League (National) (vô dich giai dau)
        "Monaco - Olympique Lyonnais": 2500920, #Ligue 1 (France) (duoc danh gia tot nhung lai da kem)
        "Bayern Mucnchen - Stuttgart": 2517036, #Germany (doi bong noi tieng)
        "SPAL - Sampdoria": 2576337, #Germany (da tot mua giai khi bi danh gia kem)
        "Barcelona - Real Madrid": 2565907, #Spain Doi thi dau giu duoc thu hang tot nhat
        "France - Croatia": 2058017 # Doi vo dich world cup 2018 Mbappé toa sang trong thi dau
    }
    """
    crawl_matchEvent_data(MATCH_ID)

