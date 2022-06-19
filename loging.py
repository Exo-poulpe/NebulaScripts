"""
module(load="imfile" PollingInterval="10") #needs to be done just once

input(type="imfile"
      File="/home/iti/nebula.log"
      Tag="nebulog"
      Severity="info"
      Facility="local3")

template(
    name="SendRemote"
    type="string"
    string="<%PRI%>%TIMESTAMP:::date-rfc3339% %HOSTNAME% %syslogtag:1:32%%msg:::sp-if-no-1st-sp%%msg%"
)

action(type="omfwd"
	       target="192.168.122.157"
	       port="514"
               protocol="udp" 
               template="SendRemote" 
               queue.SpoolDirectory="/var/spool/rsyslog"
    	       queue.FileName="remote"
               queue.MaxDiskSpace="1g"
               queue.SaveOnShutdown="on"
               queue.Type="LinkedList"
               ResendLastMSGOnReconnect="on")
stop
"""
import sys
import argparse

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        exit(1)


if __name__ == "__main__":
    try:
        # parser = argparse.ArgumentParser(description='Process some integers.')
        parser = MyParser()
        parser.add_argument('-f','--filename', metavar='filename', type=str,required=True, help='The file for stock log data')
        parser.add_argument('-o','--output', metavar='output config',default="/etc/rsyslog.d/nebula.conf", type=str,required=False, help='The output config file name')
        parser.add_argument('--ip',metavar='ip', default="127.0.0.1",type=str,help='IP of the server (default : 127.0.0.1)')
        parser.add_argument('--port',metavar='port', default="8080",type=str,help='The port of the server (default : 8080)')
        parser.add_argument('-i','--interval',metavar='interval', default="10",type=str,help='The port of the server (default : 8080)')
        args = parser.parse_args()
    except:
        exit(1)

    content = f"""
    module(load="imfile" PollingInterval="{args.interval}") #needs to be done just once
    input(type="imfile"
        File="{args.filename}"
        Tag="nebulog"
        Severity="info"
        Facility="local3")

    template(
        name="SendRemote"
        type="string"
        string="<%PRI%>%TIMESTAMP:::date-rfc3339% %HOSTNAME% %syslogtag:1:32%%msg:::sp-if-no-1st-sp%%msg%"
    )

    action(type="omfwd"
            target="{args.ip}"
            port="{args.port}"
                protocol="udp" 
                template="SendRemote" 
                queue.SpoolDirectory="/var/spool/rsyslog"
                queue.FileName="remote"
                queue.MaxDiskSpace="1g"
                queue.SaveOnShutdown="on"
                queue.Type="LinkedList"
                ResendLastMSGOnReconnect="on")
    stop"""

    with open(args.output,"w") as f:
        f.write(content)
    print("File write")
    

