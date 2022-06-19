import sys
import requests
import subprocess

link = "https://github.com/slackhq/nebula/releases/download/v1.5.2/nebula-linux-amd64.tar.gz"
program = "nebula-linux-amd64.tar.gz"
config_lnk = "https://raw.githubusercontent.com/Exo-poulpe/NebulaConfig/main/config.orig.yaml"


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


def client_config() -> None:
    runcmd('wget "' + client_config_lnk + '"', verbose=False)

def server_config() -> None:
    runcmd('wget "' + server_config_lnk + '"', verbose=False)

def clean() -> None:
    runcmd('rm nebula*' , verbose=False)
    runcmd('rm config*' , verbose=False)

def file_to_str(filename:str) -> str:
    f = open(filename,"r")
    return ''.join(f.readlines())

def str_to_file(filename:str,data:str) -> None:
    f = open(filename,"w")
    f.write(data)
    f.close()

def create_pub_priv_key(username:str,path_nebula:str="./nebula-cert") -> str:
    return runcmd(f"{path_nebula} keygen -out-key {username}.priv -out-pub {username}.pub",verbose=False)

def create_cert(username:str,path_nebula:str="./nebula-cert") -> str:
    return runcmd(f"{path_nebula} ca -name \"{username}\"",verbose=False)

def self_sign(username:str="lighthouse",ip:str="192.168.1.1/24",path_nebula:str="./nebula-cert") -> str:
    return runcmd(f"{path_nebula} sign -name \"{username}\" -ip \"{ip}\"",verbose=False)

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print(f"Usage : {sys.argv[0]} client OR server OR clean")
        exit(0)
    runcmd('wget ' + link, verbose=False)
    runcmd('tar xvf ' + program, verbose=False)
    is_lighthouse = False
    runcmd('wget "' + config_lnk + '"', verbose=False)

    if sys.argv[1] == "client":
        # client_config()
        is_lighthouse = False

    elif sys.argv[1] == "server":
        # server_config()
        is_lighthouse = True
        
    elif sys.argv[1] == "clean":
        clean()
        exit(0)
    elif sys.argv[1] == "run":
        runcmd("./nebula --config " + "config.yaml2")
    
    # addr_node = input("Addresse of node : ")
    addr_house_pub = input("Name public of lighthouse or IP addr : ")
    port_house = input("Port of lighthouse : ")
    vpn_ip = input("VPN IP of lighthouse : ")
    network_name = input("Network name : ")
    if not is_lighthouse:
        host_ip = input("Static host know ip addr : ")
        public_key_house = input("Public key path of lighthouse : ")
    if not is_lighthouse:
        priv_pub = input("Create public and private key ? [Y/n] ")
        if (priv_pub == "" or priv_pub == "y" or priv_pub == "Y"):
            name = input("Name of user ? ")
            create_pub_priv_key(name)
            cert_path = name+".crt"
            key_path = name+".key"
        else:
            cert_path = input("Host cert path : ")
            key_path = input("Host key path : ")
    else:
        name = input("Name of lighthouse ? ")
        create_cert(name)
        self_sign(name)
        public_key_house = "ca.key"
        cert_path =  name+".crt"
        key_path =  name+".key"

    
    fstr = file_to_str("config.orig.yaml")
    fstr = fstr.replace("<network_name>", f"{network_name}")
    fstr = fstr.replace("<host_ip>", f"#" if is_lighthouse else f"- \"{host_ip}\"" )
    fstr = fstr.replace("<i_am_lighthouse>", "true" if is_lighthouse else "false")
    fstr = fstr.replace("<vpn_ip>", f"{vpn_ip}")
    fstr = fstr.replace("<public_ip_lighthouse>", f"{addr_house_pub}")
    fstr = fstr.replace("<lighthouse_port>", f"{port_house}")
    fstr = fstr.replace("<key_path>", f"{key_path}")
    fstr = fstr.replace("<cert_path>", f"{cert_path}")
    fstr = fstr.replace("<public_key_house>", f"{public_key_house}")
    str_to_file("config.yaml", fstr)

    run = input("Run nebula ? (y/n) : ")
    if run == "y":
        runcmd("./nebula --config config.yaml")