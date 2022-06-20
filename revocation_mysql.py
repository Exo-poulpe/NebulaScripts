from datetime import timedelta
import ssl
import sys
import uuid
import flask
import subprocess
import bcrypt
import sqlite3
import argparse
import json
import psutil
import os
import signal
import mysql.connector


DB_PORT = 3306
DB_HOST = "192.168.122.22"
DB_NAME = "databses.db"


def database_user_fingerprint(username:str) -> None:
    # connection=sqlite3.connect(DB_NAME)
    # cursor=connection.cursor()
    cursor = dataBase.cursor()
    try:
        cursor.execute(f"SELECT user_fingerprint FROM cert WHERE user_id = '{username}';")
    except Exception() as err:
        print(f"Error : {err}")
        print(f"ID already exist : {unique_id_err}")
    data=cursor.fetchall()
    cursor.close()
    if(data == []):
        return ""
    return str(data[0][0])

def database_user_invalidate(username:str) -> None:
    cursor = dataBase.cursor()
    try:
        cursor.execute(f"UPDATE cert SET user_validate = 0 WHERE user_id = '{username}';")
        dataBase.commit()
    except Exception() as err:
        print(f"Error : {err}")
        print(f"ID already exist : {unique_id_err}")
    cursor.close()


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        exit(1)

if __name__ == "__main__":
    try:
        # parser = argparse.ArgumentParser(description='Revocation of certificat in database')
        parser = MyParser()
        parser.add_argument('--user', metavar='UUID', type=str,required=True, help='The username for the client')
        parser.add_argument('--database', metavar='Database file',default=DB_NAME, type=str,required=False, help='The databases sqlite3 file')
        parser.add_argument('--ip', metavar='Database ip',default=DB_HOST, type=str,required=False, help='The databases ip')
        parser.add_argument('--port', metavar='Database port',default=DB_PORT, type=str,required=False, help='The databases port')
        parser.add_argument('--config', metavar='VPN config file',default="config.yaml", type=str,required=False, help='The config file for lighthouse')
        args = parser.parse_args()
    except:
        exit(1)

    dataBase = mysql.connector.connect(
        host = args.ip,
        port = args.port,
        user ="light",
        passwd ="Jesuisunetartine#22",
        database = 'vpn'
    )
    
    uuid = args.user
    config = args.config
    contents = []
    with open(config, "r+") as f:
        contents = f.readlines()
        print(contents)
        idx = contents.index("  blocklist:\n")
        contents.insert(idx+1,f"    - {database_user_fingerprint(uuid)}\n")

    database_user_invalidate(uuid)

    with open(config, "w") as f:
        final = "".join(contents)
        f.write(final)
    f.close()

    dataBase.close()

    # Reload config in nebula process
    # https://github.com/slackhq/nebula/issues/304
    pids = psutil.process_iter()
    for pid in pids:
        if pid.name == "nebula":
            os.kill(pid.pid,signal.SIGHUP)
            break 