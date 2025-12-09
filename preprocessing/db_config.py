import os
import subprocess
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_windows_host_ip():
    #read nameserver in /etc/resolv.conf - often pointer to windows Host
    try:
        res = subprocess.check_output("grep nameserver /etc/resolv.conf | awk '{print $2}'", shell=True)
        return res.decode().strip()
    except Exception:
        # fallback: user can set WINDOWS_HOST_IP in .env
        return os.getenv("WINDOWS_HOST_IP")
    
def get_engine():
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASS")
    db = os.getenv("SQL_DB")
    port = os.getenv("SQL_PORT", "1433")
    host = get_windows_host_ip()

    if not all([user, password, db, host]):
        raise ValueError("DB config incomplete. Check .env or WINDOWS_HOST_IP env var")
    
    conn_str = (
        f"mssql+pydodbc://{user}:{password}@{host}:{port}/{db}"
        "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    return create_engine(conn_str)

    