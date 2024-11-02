# ---------------------------------------------------------------------------- #
import http.client
import json
import ssl
import urllib.parse
# ---------------------------------------------------------------------------- #
from config import *
from tp import tp_set_btn_text_unicode, convert_text_to_unicode
from modules.udp import UdpServer
from config import barixes_ip_addr, logger
from relay import set_relay

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
            for idx in relay_indices:
                if idx < num_of_relays:
                    set_relay(idx - 1, False)
        elif command == "#allon":
            for idx in relay_indices:
                if idx < num_of_relays:
                    set_relay(idx - 1, True)
    except Exception as e:
        logger.error(f"udp_server_callback() Exception e={e}")

# ---------------------------------------------------------------------------- #
def get_https(host, url, max_redirects=1):
    sslcontext = ssl.create_default_context()
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    try:
        conn = http.client.HTTPSConnection(host=host, context=sslcontext)
        conn.request(method="GET", url=url)
        response = conn.getresponse()
        if response.status == 301 and max_redirects > 0:
            location = response.getheader("Location")
            conn.close()
            parsed_url = urllib.parse.urlparse(location)
            return get_https(
                host=parsed_url.netloc,
                url=parsed_url.path + "?" + parsed_url.query,
                max_redirects=max_redirects - 1,
            )
        elif max_redirects == 0:
            print("get_https() max redirection reached...")
            return None
        data = response.read()
        conn.close()
        return data.decode()
    except Exception as e:
        print(f"get_https() Exception: {e}")
        return None


def get_data_from_server():
    global main_server_ip_addr, barixes_ip_addr, power_on_delay, local_device, venue_name, zone_name
    global tp_qrc_on_air_zone_list, qrc_zone_gain_status, qrc_zone_mute_status, qrc_zone_on_air_status
    REQ_PATH = "/api/amx"
    PARAMS = urllib.parse.urlencode({"ipaddress": qsys_ip_addr})
    FULL_PATH = f"{REQ_PATH}?{PARAMS}"
    response_data = get_https(host=main_server_ip_addr, url=FULL_PATH)
    data = json.loads(response_data)
    
    if "time" in data:
        power_on_delay = int(data["time"])
    
    if "barixes" in data:
        for id, ip in enumerate(data["barixes"]):
            if ip:
                barixes_ip_addr[id + 1] = ip
    
    if "qsys" in data:
        local_device = data["qsys"]
        if local_device.get("name") and venue_name != local_device["name"]:
            venue_name = local_device["name"]
            tp_set_btn_text_unicode(DV_TP, 2, 1, convert_text_to_unicode(text=venue_name))
            default_data["devices"][local_id]["name"] = venue_name
            with open("default_data.json", "w") as f:
                json.dump(default_data, f, indent=4)

        if "ZoneStatus" in local_device:
            zones = [zone.get("name", f"지역-{idx + 1}") for idx, zone in enumerate(local_device["ZoneStatus"])]
            if zones != zone_name:
                zone_name = zones
                for idx, zone in enumerate(zone_name):
                    tp_set_btn_text_unicode(DV_TP, 2, idx + 21, convert_text_to_unicode(zone))
                default_data["devices"][local_id]["zones"] = zone_name
                default_data["devices"][local_id]["num_of_zones"] = len(zone_name)
                with open("default_data.json", "w") as f:
                    json.dump(default_data, f, indent=4)

                def adjust_list_length(lst, target_length, default_value):
                    lst.extend([default_value] * (target_length - len(lst)))
                    return lst[:target_length]

                tp_qrc_on_air_zone_list = adjust_list_length(tp_qrc_on_air_zone_list, len(zone_name), False)
                qrc_zone_gain_status = adjust_list_length(qrc_zone_gain_status, len(zone_name), 0.0)
                qrc_zone_mute_status = adjust_list_length(qrc_zone_mute_status, len(zone_name), False)
                qrc_zone_on_air_status = adjust_list_length(qrc_zone_on_air_status, len(zone_name), False)
                
# ---------------------------------------------------------------------------- #
def get_barixes():
    global main_server_ip_addr, barixes_ip_addr
    REQ_PATH = "/api/amx/barix"
    PARAMS = urllib.parse.urlencode({"ipaddress": qsys_ip_addr})
    FULL_PATH = f"{REQ_PATH}?{PARAMS}"
    response_data = get_https(host=main_server_ip_addr, url=FULL_PATH)
    # ---------------------------------------------------------------------------- #
    for id, ip in enumerate(json.loads(response_data)):
        if ip is not None:
            barixes_ip_addr.update({id + 1: ip})


# ---------------------------------------------------------------------------- #
def handle_bs_get_delaytime():
    global main_server_ip_addr, power_on_delay
    REQ_PATH = "/api/amx/relayontime"
    PARAMS = urllib.parse.urlencode({"ipaddress": qsys_ip_addr})
    FULL_PATH = f"{REQ_PATH}?{PARAMS}"
    response_data = get_https(main_server_ip_addr, FULL_PATH)
    # ---------------------------------------------------------------------------- #
    result = json.loads(response_data)
    if result.get("time") is not None:
        power_on_delay = int(result.get("time"))

def barix_set_relay(ip_address, state):
    global logger
    try:
        state_str = 1 if state else 0
        conn = http.client.HTTPConnection(ip_address)
        conn.request("GET", f"/rc.cgi?R={state_str}")
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data.decode()
    except Exception as e:
        logger.error(f"barix_set_relay() Exception e={e}")
        
def barix_set_relays (zone_idx_list, state):
    global logger, barixes_ip_addr
    try:
        for idx, ip in barixes_ip_addr():
            if idx in zone_idx_list:
                barix_set_relay(ip, state)
    except Exception as e:
        logger.error(f"barix_set_relays() Exception e={e}")

