import sys
import json
from typing import List
import argparse
import uuid
import bcrypt
import sqlite3

def database_add_user_id(user_id:str,passw:str) -> str():
    connection=sqlite3.connect("databses.db")
    cursor=connection.cursor()
    try:
        if len(user_id) != 36:
            raise sqlite3.OperationalError()
        salt = bcrypt.gensalt()
        passwd = bcrypt.hashpw(bytes(passw,"utf-8"), salt)
        # print(f"{passwd}   {salt}")
        cursor.execute(f"INSERT INTO users ('user_id','user_pass','user_pass_salt') VALUES (\"{user_id}\",\"{passwd.decode('utf-8')}\",\"{salt.decode('utf-8') }\");")
        connection.commit()
    except sqlite3.OperationalError as err:
        return err
    cursor.close()
    return None
    
def database_add_groups_for_user(user_id:str,groups:List[str]) -> bool:
    connection=sqlite3.connect("databses.db")
    cursor=connection.cursor()
    try:
        if len(user_id) != 36:
            raise sqlite3.OperationalError()
        for grp in groups:
            cursor.execute(f"SELECT group_id FROM groups WHERE name = '{grp}';")
            tmp_id = cursor.fetchall()[0][0]
            cursor.execute(f"INSERT INTO groups_member ('user_id','group_id') VALUES ('{user_id}','{tmp_id}');")
            connection.commit()
    except sqlite3.OperationalError as err:
        return res
    cursor.close()
    return None

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        exit(1)


if __name__ == "__main__":
    try:
        # parser = argparse.ArgumentParser(description='Create new client in database ')
        parser = MyParser()
        parser.add_argument('--user', metavar='UUID', type=str,required=False, help='The username for the client (if empty random UUID generated)')
        parser.add_argument('--passw', metavar='Password', type=str,required=True, help='The password of the client')
        parser.add_argument('--database',metavar='database file', default="databses.db",type=str,help='IP of the server')
        parser.add_argument('--groups',metavar='groups', default="User",required=True,type=str,help='The groups for the user')
        args = parser.parse_args()
    except:
        exit(1)
    
    if args.user == None:
        args.user = str(uuid.uuid4())

    # print(f"{args.user}")
    res = database_add_user_id(args.user, args.passw)
    if  res != None:
        print(f"Error add user : {res}")
        exit(1)
    res = database_add_groups_for_user(args.user, list(args.groups.split(",")))
    if  res != None:
        print(f"Error add groups {res}")
        exit(1)
    print(f"User : {args.user} added")
    print(f"Passwd : {args.passw}")


