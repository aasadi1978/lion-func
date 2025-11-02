from os import getenv

def get_sql_env_vars():
    return {
        "AZURE_SQL_USER": getenv("AZURE_SQL_USER", "lion2025"),
        "AZURE_SQL_PASS": getenv("AZURE_SQL_PASS"),
        "AZURE_SQL_SERVER": getenv("AZURE_SQL_SERVER"),
        "AZURE_SQL_DB": getenv("AZURE_SQL_DB")
    }
