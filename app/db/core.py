from configparser import ConfigParser
import psycopg2
from typing import Annotated
from fastapi import Depends
from pathlib import Path
from psycopg2.extensions import connection
PROJECT_ROOT = Path(__file__).resolve().parents[2]

filename =  PROJECT_ROOT / "app/db/database.ini"
section = "postgresql"

def _load_config():
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return config

def connect():
    """ Connect to the PostgreSQL database server """
    try:
        config = _load_config()
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

Conn = Annotated[connection, Depends(connect)]