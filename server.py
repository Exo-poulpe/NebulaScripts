from flask import Flask, redirect, url_for, render_template, request, session, jsonify, send_file
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from typing import Tuple
from datetime import timedelta
import ssl
import uuid
import flask
import subprocess
import bcrypt
import sqlite3
import json
import argparse
import netifaces

config_lnk = "https://raw.githubusercontent.com/Exo-poulpe/NebulaConfig/main/config.orig.yaml"
DB_PORT = 3306
DB_HOST = "192.168.122.22"
DB_NAME = "databses.db"

#### CMD Helper
## Permet de sortir la signature d'un certificat en JSON
# ./nebula-cert print -json -path Michel.crt | jq '.["signature"]'
#
## Permet de signé la clé publique du client
# ./nebula-cert sign -ca-crt lighthouse_ca.crt -ca-key lighthouse_ca.key -in-pub User.pub -name "UserName" -ip "192.168.1.1/24"
#
## Permet de vérifé le certificat
# ./nebula-cert verify -ca Lighthouse.crt -crt Conf.crt
####

#### Request for GET all groupd from UUID
# SELECT name FROM groups WHERE group_id IN ( SELECT GM.group_id FROM groups_member as GM WHERE GM.user_id == "31841e1a-ae71-46fc-9d78-847786148749" );
####

appFlask = Flask(__name__)
appFlask.debug = True
appFlask.config["JWT_SECRET_KEY"] = "6W*vs5Vu&cde5S@M@&f466vru2rgz3NDw!&S*7tL!^gkM&3JD@68Y&b6^ch6"
appFlask.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=5)
appFlask.config["JWT_ALGORITHM"] = "HS512"

jwt = JWTManager(appFlask)

@appFlask.route('/ca', methods=['GET'])
@jwt_required()
def root_cert():
    return send_file(f"ca.crt"), 200
    
@appFlask.route('/certification', methods=['POST'])
@jwt_required()
def cert():
    current_user = get_jwt_identity()
    if database_user_already_sign(current_user):
        return jsonify({"error":"cert already build"}), 401
    try: file_byte = request.get_data()
    except KeyError as err:
        print(err)
        return jsonify({"error":"file upload"}), 401
    # str(file_byte).save(secure_filename(f"{current_user}.pub"))
    file_name = f"{current_user}.pub"
    open(file_name,"wb").write(file_byte)
    # print(f"{get_groups_from_database(current_user)}")
    print(",".join(get_groups_from_database(current_user)))
    fingerprint = create_cert(file_name,current_user,",".join(get_groups_from_database(current_user)),f"192.168.1.{database_user_id(current_user)}/24")
    print(fingerprint)
    database_user_fingerprint(current_user,fingerprint)
    print("db update")
    return send_file(f"{current_user}.crt"), 200
   

@appFlask.route('/config', methods=['GET'])
@jwt_required()
def config():
    current_user = get_jwt_identity()
    print(current_user)
    database_to_config(str(current_user))
    # str(file_byte).save(secure_filename(f"{current_user}.pub"))
    return send_file(f"{current_user}.yaml"), 200
   

@appFlask.route('/login', methods=['POST'])
def login():
    try: info = json.loads(request.data)
    except:
        return jsonify({"message" : "Invalid credentials"}), 401
    try:
        username = info["username"]
        password = info["password"]
    except KeyError as err:
        print(err)
        return jsonify({"message" : "Invalid credentials"}), 401
    print(f"u : {username}, p : {password}")
    if username:
        pass_tmp = database_user_password(username)
        if(not pass_tmp): # If password is null
            return jsonify({"message" : "Invalid credentials"}), 401
        if bcrypt.checkpw(bytes(password,"utf-8"),bytes(pass_tmp,"utf-8")): # Check password in database
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
    return jsonify({"message" : "Invalid credentials"}), 401

########### HELPERS 

def str_to_file(filename:str,data:str) -> None:
    f = open(filename,"w")
    f.write(data)
    f.close()

def file_to_str(filename:str) -> str:
    f = open(filename,"r")
    return ''.join(f.readlines())

def database_to_config(username:str) -> None:
    groups = get_groups_from_database(username)
    vpn_ip = f"192.168.1.{database_user_id(username)}/24"
    addr_house_pub = "192.168.1.225"# get_lan_ip()
    is_lighthouse = False
    network_name = "netbula1"
    port_house = 4242
    cert_path = f"{username}.crt"
    key_path = f"{username}.key"
    public_key_house = f"ca.crt"

    runcmd('wget "' + config_lnk + '"', verbose=False)
    fstr = file_to_str("config.orig.yaml")
    fstr = fstr.replace("<network_name>", f"{network_name}")
    fstr = fstr.replace("<host_ip>", f"#" if is_lighthouse else f"- \"{addr_house_pub}\"" )
    fstr = fstr.replace("<i_am_lighthouse>", "true" if is_lighthouse else "false")
    fstr = fstr.replace("<vpn_ip>", f"{addr_house_pub}")
    fstr = fstr.replace("<public_ip_lighthouse>", f"{addr_house_pub}")
    fstr = fstr.replace("<lighthouse_port>", f"{port_house}")
    fstr = fstr.replace("<key_path>", f"{key_path}")
    fstr = fstr.replace("<cert_path>", f"{cert_path}")
    fstr = fstr.replace("<public_key_house>", f"{public_key_house}")
    fstr = fstr.replace("<groups>", f"{groups}")
    str_to_file(f"{username}.yaml", fstr)


def get_lan_ip() -> str:
    res = ""
    link = netifaces.ifaddresses('eth0')[netifaces.AF_INET]
    return link['addr']

def database_user_already_sign(username:str) -> bool:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    data = ""
    try:
        cursor.execute(f"SELECT user_id FROM cert WHERE user_id = '{username}';")
    except sqlite3.OperationalError as err:
        return False
    data=cursor.fetchall()
    cursor.close()
    if(data == []):
        return False
    return True

def database_user_id(username:str) -> str:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    data = ""
    try:
        cursor.execute(f"SELECT id_row FROM users WHERE user_id = '{username}';")
    except sqlite3.OperationalError as err:
        return err
    # print(data)
    data=cursor.fetchall()
    cursor.close()
    if(data == []):
        return ""
    return str(data[0][0])

def database_user_password(username:str) -> str:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    data = ""
    try:
        cursor.execute(f"SELECT user_pass FROM users WHERE user_id = '{username}';")
    except sqlite3.OperationalError as err:
        return None
    data=cursor.fetchall()
    cursor.close()
    if(data == []):
        return ""
    return str(data[0][0])

def database_user_fingerprint(username:str,fingerprint:str) -> None:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    print(f"cur : {cursor}, user : {username}, fing : {fingerprint}")
    try:
        cursor.execute(f"INSERT INTO cert (user_id,user_fingerprint) VALUES('{username}', '{fingerprint}');")
        connection.commit()
    except sqlite3.OperationalError as err:
        print(f"Error : {err}")
    except sqlite3.IntegrityError as unique_id_err:
        print(f"ID already exist : {unique_id_err}")
    cursor.close()

def get_groups_from_database(username:str) -> str:
    connection=sqlite3.connect(DB_NAME)
    cursor=connection.cursor()
    data = ""
    try:
        rqst = f"SELECT G.name FROM groups as G WHERE group_id IN ( SELECT GM.group_id FROM groups_member as GM WHERE GM.user_id == \"{username}\" );"
        cursor.execute(f"{rqst}")
    except sqlite3.OperationalError as err:
        print(f"Error {err}")
        data = None
        return data
    data=cursor.fetchall()
    cursor.close()
    if(data == []):
        return ""
    res = []
    for elem in [''.join(i) for i in data]:
        res.append(f"- {elem}\n\t")
    return ''.join(res)



def create_cert(filename:str,username:str,groups:str,ip:str = "192.168.1.1/24",duration: int=8766) -> str:
    # runcmd(f"./nebula-cert sign -ca-crt ca.crt -ca-key ca.key -in-pub {filename} -name \"{username}\" -ip \"192.168.1.1/24\"")
    # print(filename)
    # exit(1)
    cmd = f"./nebula-cert sign -in-pub \"{filename}\" -name \"{username}\" -groups \"{groups}\" -ip \"{ip}\" -duration {str(duration)}h"
    print(f"{cmd}")
    data = runcmd(cmd)
    # print(data)
    data = runcmd(f"./nebula-cert print -json -path \"{username}.crt\"",verbose=True)
    # print(data)
    return json.loads(data)["fingerprint"]

def identity(payload):
    user_id = payload['identity']
    return {"user_id": user_id}

def runcmd(cmd, verbose=False, *args, **kwargs) -> str:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    std_out, std_err = process.communicate()
    # if verbose:
    #     print(std_out.strip(), std_err)
    return std_err if(not verbose) else str(std_out + std_err)
    
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Run server with all api endpoint')
        parser.add_argument('--crt', metavar='CSR file',default="pub.csr", type=str, help='The file CSR for TLS')
        parser.add_argument('--pem', metavar='PEM file',default="private.pem", type=str, help='The file PEM for TLS')
        parser.add_argument('--port',metavar='port number', default="8080",type=str,help='The port to use for server run')
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(1)
    ##### CMD (Create self sign cert)
    # openssl genrsa -out private.pem 4096
    ##
    # openssl req -new -x509 -key private.pem -out public.pem -days 360
    #####
    appFlask.run(ssl_context=("public.pem","private.pem"),port=args.port)