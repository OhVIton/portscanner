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
            "80", # http-alt
            "81", # http
            "135", # rpc
            "443", # https
            "445", # smb
            "1723", # pptp
            "2375", # docker rest api
            "2376", # docker rest api
            "3389", # rdp
            "5431", # UPnP
            "5555", # adb
            "6379", # redis
            "8000", # http-alt
            "8080", # http-alt
            "8081", # http-alt
            "8082", # http-alt
            "8443", # http-alt
            "8888", # http-alt
            "10000", # http-alt
            "10001", # http-alt
            "49152", # http-alt
            "50000", # http-alt
            "52869", # UPnP
        ],
        "udp": [
            "19", # chargen
            "53", # dns
            "123", # ntp
            "161", # snmp
            "162", # snmp
            "500", # ipsec
            "1701", # l2tp
            "1900", # ssdp
            "5000", # UPnP
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
        sr_ports = [
            p
            for p in sr["nmaprun"]["host"]["ports"]["port"]
            if p["state"]["@state"] == "open"
        ]

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
