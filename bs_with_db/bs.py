import json, urllib.parse
from config import *
from modules.udp import UdpServer
from relay import set_relay, barix_set_relay_all, barix_set_relays
from modules.http_funtions import get_https
from modules.db import Database

main_server_ip_addr = default_data["main_server_ip_addr"]

def init_udp_server(port):
    udpserver = UdpServer(port, udp_server_callback)
    udpserver.run()

def udp_server_callback(data, addr):
    try:
        global num_of_relays
        msg = data.decode().replace("\x00", '').rstrip("!")
        if not msg:
            return

        params = msg.split(",")
        relay_indices = [int(x) for x in params[1:]]

        command = params[0]
        if command == "#on":
            for idx in relay_indices:
                set_relay(idx - 1, True)
        elif command == "#off":
            for idx in relay_indices:
                set_relay(idx - 1, False)
        elif command == "#reset":
            barix_set_relay_all(False)
            for idx in relay_indices:
                if idx < num_of_relays:
                    set_relay(idx - 1, False)
        elif command == "#allon":
            for idx in relay_indices:
                if idx < num_of_relays:
                    set_relay(idx - 1, True)
    except Exception as e:
        logger.error(f"udp_server_callback() Exception e={e}")

def get_data_from_server():
    db = Database()
    try:
        addr = f"/api/amx?{urllib.parse.urlencode({'ipaddress': qsys_ip_addr})}"
        response_data = get_https(host=main_server_ip_addr, url=addr)
        data = json.loads(response_data)
        
        if "time" in data:
            db.update("setup", {"Value": int(data["time"])}, {"key": "powerOnDelay"}, upsert=True)
        
        if "barixes" in data:
            for idx, ip in enumerate(data["barixes"]):
                if ip:
                    db.update("zones", {"Barix": ip}, {"id": idx + 1}, upsert=True)

        if "qsys" in data:
            local_device = data["qsys"]
            # DB
            db.update("setup", {"String": data["qsys"]["name"]}, {"key": "name"})
            for idx, zone in enumerate(data["qsys"]["ZoneStatus"]):
                if zone:
                    db.update("zones",
                        {
                            "Name": zone.get("Name", f"지역-{idx + 1}"),
                            "Gain": zone.get("gain", 0.0),
                            "Mute": zone.get("mute", False),
                            "Active": zone.get("Active", False)
                        },
                        {
                            "id": zone.get("Zone", idx+1)
                        },
                        upsert=True
                        )
            db.update("setup", {"Value": len(data["qsys"]["ZoneStatus"])}, {"key": "numOfZones"}, upsert=True)
    except Exception as e:
        logger.error(f"get_data_from_server() Exception e={e}")
            
def get_barixes():
    global main_server_ip_addr, page
    addr = f"/api/amx/barix?{urllib.parse.urlencode({'ipaddress': qsys_ip_addr})}"
    response_data = get_https(host=main_server_ip_addr, url=addr)
    for id, ip in enumerate(json.loads(response_data)):
        if ip is not None:
            barixes_ip_addr.update({id + 1: ip})


def handle_bs_get_delaytime():
    global main_server_ip_addr, page
    addr = f"/api/amx/relayontime?{urllib.parse.urlencode({'ipaddress': qsys_ip_addr})}"
    response_data = get_https(main_server_ip_addr, url=addr)
    result = json.loads(response_data)
    if result.get("time") is not None:
        page["power_on_delay"] = int(result.get("time"))

