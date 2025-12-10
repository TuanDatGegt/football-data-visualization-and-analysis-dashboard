import os
import urllib
import subprocess
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

    
def get_engine():
    try:
        user = os.getenv("SQL_USER")
        password = os.getenv("SQL_PASS")
        db = os.getenv("SQL_DB")
        port = os.getenv("SQL_PORT", "1433")
        host = os.getenv("WINDOWS_HOST_IP")

        sql_uri =(
            f"mssql+pyodbc://{user}:{password}"
            f"@{host}:{port}/{db}"
            f"?driver=ODBC+Driver+18+for+SQL+Server"
            f"&TrustServerCertificate=yes"
        )

        engine = create_engine(sql_uri)
        return engine
    except Exception as e:
        raise RuntimeError(f"Loi tao SQL Engine: {e}")


    