import subprocess
from tempfile import NamedTemporaryFile
import xmltodict

import logging

import os
from dotenv import load_dotenv

import logging

load_dotenv()
SCREENSHOT_SAVE_PATH = os.environ.get("SCREENSHOT_SAVE_PATH")
LOG_PATH = os.environ.get("LOG_PATH")

logger = logging.getLogger("portscanner")



def scan_ports(
    ip: str,
    ports={
        "tcp": [
            "21", # ftp
            "22", # ssh
            "23", # telnet
            "25", # smtp
            "80", # http-alt
            "81", # http
            "110", # pop3
            "135", # rpc
            "137", # netbios-ns 
            "138", # netbios-dgm
            "139", # netbios-ssn
            "443", # https
            "445", # smb
            "465", # smtp
            "515", # lpr
            "587", # smtp
            "631", # ipp
            "995", # pop3
            "1433", # microsoft sql
            "1723", # pptp
            "2222", # directadmin default
            "2375", # docker rest api
            "2376", # docker rest api
            "2525", # smtp
            "3128", # http-proxy
            "3306", # mysql
            "3389", # rdp
            "5431", # UPnP
            "5555", # adb
            "6379", # redis
            "8000", # http-alt
            "8080", # http-alt
            "8081", # http-alt
            "8082", # http-alt
            "8088", # http-alt
            "8090", # http-alt
            "8443", # http-alt
            "8888", # http-alt
            "10000", # http-alt
            "10001", # http-alt
            "37215", # huawei router
            "49152", # http-alt
            "50000", # http-alt
            "52869", # UPnP
        ],
        "udp": [
            "19", # chargen
            "53", # dns
            "123", # ntp
            "137", # netbios-ns 
            "138", # netbios-dgm
            "161", # snmp
            "162", # snmp
            "500", # ipsec
            "1701", # l2tp
            "1900", # ssdp
            "5000", # UPnP
            "5060", # sip
            "5350", #  nat-pmp
            "5351", # nat-pmp
            "5353", # dns
            "11211", # memcached
        ],
    },
):
    try:
        logger.info(f"[portscanner] start a portscan to {ip}")
        logger.debug(
            f"[portscanner] Scan will be held at {ports}"
        )
        sr = _nmap([ip], ports)
        # openなポートのみ取り出す
        
        
        sr_ports = []
        if type(sr["nmaprun"]["host"]["ports"]["port"]) == list:
            sr_ports = [
                p
                for p in sr["nmaprun"]["host"]["ports"]["port"]
                if p["state"]["@state"] == "open"
            ]
        elif type(sr["nmaprun"]["host"]["ports"]["port"]) == dict and sr["nmaprun"]["host"]["ports"]["port"]["state"]["@state"] == "open":
            sr_ports = [sr["nmaprun"]["host"]["ports"]["port"]]

        if len(sr_ports):
            logger.info(
                f"[portscanner] {ip} has open ports {str(sr_ports)}"
            )

            return sr_ports
        else:
            logger.info(
                f"[portscanner] {ip} has no open ports available"
            )
            return []

    except KeyError as ke:
        logger.info(
            f"[portscanner] {ip} has no open ports available"
        )
        return []


def _portargs(portdict: dict):
    outlist = []
    for protocol, ports in portdict.items():
        if protocol == "tcp":
            h = "T:"
        elif protocol == "udp":
            h = "U:"
        else:
            raise Exception(protocol + "is not tcp nor udp.")

        outlist += [f"{h}{port}" for port in ports]
    return ",".join(outlist)


def _nmap(iplist, portdict) -> dict:
    with NamedTemporaryFile(mode="w+t") as ipf, NamedTemporaryFile(mode="w+t") as xmlf:
        for ip in iplist:
            ipf.write(ip + "\n")

        ipf.flush()

        subprocess.run(
            ["nmap","-sV","-p", _portargs(portdict), "-i", ipf.name, "-oX", xmlf.name],
            capture_output=True,
            text=True,
        )

        srdict = xmltodict.parse(xmlf.read())
    return srdict
