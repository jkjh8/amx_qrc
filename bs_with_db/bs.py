import json, urllib.parse
from config import *
from modules.udp import UdpServer
from relay import set_relay, barix_set_relay_all, barix_set_relays
from modules.http_funtions import get_https
from db.db_setup import db_setup_update, db_setup_find_one
from db.db_zones import db_zones_update, db_zones_find

def init_udp_server(port):
    udpserver = UdpServer(port, udp_server_callback)
    udpserver.run()

def udp_server_callback(data, addr):
    try:
        num_of_relays = db_setup_find_one({"key": "numOfRelay"})["Value"]
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
    try:
        addr = f"/api/amx?{urllib.parse.urlencode({'ipaddress': db_setup_find_one({'key': 'qsys'})['String']})}"
        response_data = get_https(host=db_setup_find_one({"key": "serverIpAddr"})["String"], url=addr)
        data = json.loads(response_data)
        if "time" in data:
            db_setup_update({"Value": int(data["time"])}, {"key": "powerOnDelay"})

        if "barixes" in data:
            for idx, ip in enumerate(data["barixes"]):
                if ip:
                    db_zones_update({"Barix": ip}, {"id": idx + 1}, upsert=True)

        if "qsys" in data:
            # DB
            db_setup_update({"String": data["qsys"]["name"]}, {"key": "name"}, upsert=True)
            db_setup_update({"Value": len(data["qsys"]["ZoneStatus"])}, {"key": "numOfZones"}, upsert=True)
            for idx, zone in enumerate(data["qsys"]["ZoneStatus"]):
                if zone:
                    db_zones_update({
                        "Name": zone.get("name", f"지역-{idx + 1}") or f"지역-{idx + 1}",
                        "Gain": zone.get("gain", 0.0),
                        "Mute": zone.get("mute", False),
                        "Active": zone.get("Active", False)
                    }, {"id": zone.get("Zone", idx+1)}, upsert=True)
    except Exception as e:
        logger.error(f"get_data_from_server() Exception e={e}")
            
def get_barixes():
    addr = f"/api/amx?{urllib.parse.urlencode({'ipaddress': db_setup_find_one({'key': 'qsys'})['String']})}"
    response_data = get_https(host=db_setup_find_one({"key": "serverIpAddr"})["String"], url=addr)
    for id, ip in enumerate(json.loads(response_data)):
        if ip is not None:
            db_zones_update({"Barix": ip}, {"id": id + 1}, upsert=True)


def handle_bs_get_delaytime():
    addr = f"/api/amx?{urllib.parse.urlencode({'ipaddress': db_setup_find_one({'key': 'qsys'})['String']})}"
    response_data = get_https(host=db_setup_find_one({"key": "serverIpAddr"})["String"], url=addr)
    result = json.loads(response_data)
    if result.get("time") is not None:
        db_setup_update({"Value": int(result.get("time"))}, {"key": "powerOnDelay"})

