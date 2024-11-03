import json, urllib.parse
from config import *
from tp import tp_set_btn_text_unicode, convert_text_to_unicode
from modules.udp import UdpServer
from relay import set_relay, barix_set_relay_all, barix_set_relays
from modules.http_funtions import get_https

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
            barix_set_relays(relay_indices, True)
            for idx in relay_indices:
                set_relay(idx - 1, True)
        elif command == "#off":
            barix_set_relays(relay_indices, False)
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
    global main_server_ip_addr, page, local_device, venue_name, zone_name, qrc_zones, barixes_ip_addr, qrc_zones_gain, qrc_zones_mute, qrc_zones_onair
    try:
        addr = f"/api/amx?{urllib.parse.urlencode({'ipaddress': qsys_ip_addr})}"
        response_data = get_https(host=main_server_ip_addr, url=addr)
        data = json.loads(response_data)
        data_edit = False
        
        if "time" in data:
            page["power_on_delay"] = int(data["time"])
        
        if "barixes" in data:
            for idx, ip in enumerate(data["barixes"]):
                if ip:
                    barixes_ip_addr.update({idx + 1: ip})
            if barixes_ip_addr != default_data["devices"][local_id]["barix"]:
                data_edit = True
                default_data["devices"][local_id]["barix"] = barixes_ip_addr
            logger.info('barixes_ip_addr: %s' % barixes_ip_addr)
        
        if "qsys" in data:
            local_device = data["qsys"]
            if local_device.get("name") and venue_name != local_device["name"]:
                venue_name = local_device["name"]
                tp_set_btn_text_unicode(DV_TP, 2, 1, convert_text_to_unicode(text=venue_name))
                default_data["devices"][local_id]["name"] = venue_name
            if "ZoneStatus" in local_device:
                zones = [zone["name"] if zone["name"] else f"지역-{idx + 1}" for idx, zone in enumerate(local_device["ZoneStatus"])]
                logger.info(f"zones: {zones}")
                
                if zones != zone_name:
                    zone_name = zones
                    data_edit = True
                    for idx, zone in enumerate(zone_name):
                        tp_set_btn_text_unicode(DV_TP, 2, idx + 21, convert_text_to_unicode(zone))
                    default_data["devices"][local_id]["zones"] = zone_name
                    default_data["devices"][local_id]["num_of_zones"] = len(zone_name)

                    def adjust_list_length(lst, target_length, default_value):
                        lst.extend([default_value] * (target_length - len(lst)))
                        return lst[:target_length]

                    qrc_zones = adjust_list_length(qrc_zones, len(zone_name), False)
                    qrc_zones_gain = adjust_list_length(qrc_zones_gain, len(zone_name), 0.0)
                    qrc_zones_mute = adjust_list_length(qrc_zones_mute, len(zone_name), False)
                    qrc_zones_onair = adjust_list_length(qrc_zones_onair, len(zone_name), False)
        if data_edit:
            with open("default_data.json", "w") as f:
                json.dump(default_data, f, indent=4)
        logger.info(f"get_data_from_server")
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

