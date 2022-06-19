import urllib.request
import sys
import ssl
import json
import argparse
import subprocess

myssl = ssl.create_default_context()
myssl.check_hostname=False
myssl.verify_mode=ssl.CERT_NONE
hdr = {"Content-Type" : "application/json"}


def runcmd(cmd, verbose=False, *args, **kwargs) -> str:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    return std_err if(not verbose) else str(std_out + std_err)



def GET_with_jwt(url:str,jwt:str,output_file:str) -> str:
    r = urllib.request.Request(url,headers=hdr,method="GET")
    r.add_header(f"Authorization", f"Bearer {jwt}")
    # r.add_header("Cookie", "access_token="+token["access_token"])
    # r.add_header("X-CSRF-TOKEN", token["access_token"])
    try: r = urllib.request.urlopen(r,context=myssl)
    except urllib.error.HTTPError as err:
        print(err.reason)
        print(err.read())
        exit(1)
    open(f"{output_file}","wb").write(r.read())


def POST_with_jwt(url:str,jwt:str,hdr:str,data:str,output_file:str) -> str:
    # r = http.request.Request(url,data=bytes(dat,"utf-8"),headers=hdr,method="POST")
    r = urllib.request.Request(url,headers=hdr,method="POST",data=data)
    r.add_header("Authorization", f"Bearer {jwt}")
    try: r = urllib.request.urlopen(r,context=myssl)
    except urllib.error.HTTPError as err:
        print(err.reason)
        print(err.read())
        exit(1)
    open(f"{output_file}","wb").write(r.read())

def create_pub_priv_key(username:str,path_nebula:str="./nebula-cert") -> str:
    # print(f"{path_nebula} keygen -out-key {username}.priv -out-pub {username}.pub")
    return runcmd(f"{path_nebula} keygen -out-key {username}.priv -out-pub {username}.pub",verbose=False)

# user : 31841e1a-ae71-46fc-9d78-847786148749
# pass : poulpe
"""
{
 "user" : "31841e1a-ae71-46fc-9d78-847786148749",
 "pass" : "poulpe"
}
"""

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        exit(1)

if __name__ == "__main__":
    try:
        # parser = argparse.ArgumentParser(description='Process some integers.')
        parser = MyParser()
        parser.add_argument('--user', metavar='UUID', type=str,required=True, help='The username for the client')
        parser.add_argument('--passw', metavar='Password', type=str,required=True, help='The password of the client')
        parser.add_argument('--ip',metavar='ip', default="127.0.0.1",type=str,help='IP of the server (default : 127.0.0.1)')
        parser.add_argument('--port',metavar='port', default="8080",type=str,help='The port of the server (default : 8080)')
        parser.add_argument('--gen_keys',action='store_true',help='Create public key and private key with UUID and password')
        args = parser.parse_args()
    except:
        exit(1)

    if args.gen_keys:
        create_pub_priv_key(args.user,"../nebula-cert")

    user = args.user
    passw = args.passw
    print(f"{user}, {passw}")
    token = ""
    hdr = {"Content-Type" : "application/json"}
    url = f"https://{args.ip}:{args.port}/"
    url_cert = f"https://{args.ip}:{args.port}/certification"

    
    dat = "{ \"username\" : \""+user+"\""+",\"password\" : \""+passw+"\" }"
    print(dat)
    r = urllib.request.Request(url+"login",data=bytes(dat,"utf-8"),headers=hdr,method="POST") 
    try: r = urllib.request.urlopen(r,context=myssl)
    except urllib.error.HTTPError as err:
        print(err.reason)
        print(err.read())
        exit(1)
    print(r)
    
    token = json.loads(r.read())
    res = open(f"{user}.pub", "rb").read()
    POST_with_jwt(url+"certification", token["access_token"], hdr, res, f"{user}.crt")
    GET_with_jwt(url+"config", token["access_token"], f"{user}.yaml")
    GET_with_jwt(url+"ca",token["access_token"],f"ca.crt")