# db.py

import oracledb

# OPTIONAL: use if instant client is not in system PATH
# oracledb.init_oracle_client(lib_dir=r"C:\instantclient_21_13")

def get_connection():
    return oracledb.connect(
        user="system",
        password="dhivya",
        dsn="localhost/XE"
    )
