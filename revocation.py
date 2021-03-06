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

DB_NAME = "databses.db"

def database_user_fingerprint(username:str) -> None:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    try: 
        if len(username) != 36:
            raise sqlite3.OperationalError()
        cursor.execute(f"SELECT user_fingerprint FROM cert WHERE user_id = '{username}';")
    except sqlite3.OperationalError as err:
        print(f"Error : {err}")
    except sqlite3.IntegrityError as unique_id_err:
        print(f"ID already exist : {unique_id_err}")
    data=cursor.fetchall()
    cursor.close()
    if(data == []):
        return ""
    return str(data[0][0])

def database_user_invalidate(username:str) -> None:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    try: 
        if len(username) != 36:
            raise sqlite3.OperationalError()
        cursor.execute(f"UPDATE cert SET user_validate = 0 WHERE user_id = '{username}';")
        connection.commit()
    except sqlite3.OperationalError as err:
        print(f"Error : {err}")
    except sqlite3.IntegrityError as unique_id_err:
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
        args = parser.parse_args()
    except:
        exit(1)
    uuid = args.user
    DB_NAME = args.database
    config = "config.yaml" if len(sys.argv) == 2 else sys.argv[2]
    contents = []
    with open(config, "r+") as f:
        contents = f.readlines()
        # print(contents)
        idx = contents.index("  blocklist:\n")
        contents.insert(idx+1,f"\t- {database_user_fingerprint(uuid)}\n")

    database_user_invalidate(uuid)

    with open(config, "w") as f:
        final = "".join(contents)
        f.write(final)
    f.close()

    # Reload config in nebula process
    # https://github.com/slackhq/nebula/issues/304
    pids = psutil.get_pid_list()  
    for pid in pids:  
        if psutil.Process(pid).name == "nebula":  
            os.kill(pid,signal.SIGHUP)
            break 