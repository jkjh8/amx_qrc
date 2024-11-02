# ---------------------------------------------------------------------------- #
import json
from mojo import context
# devices
DV_MUSE = context.devices.get("idevice")
DV_TP = context.devices.get("AMX-10001")
DV_RELAYS = context.devices.get("idevice").relay
# logger
logger = context.log
#  variables
with open("data.json", "r") as f:
    default_data = json.load(f)
local_id = 0
power_on_delay = default_data.get("power_on_delay", 5)
main_server_ip_addr = default_data["main_server_ip_addr"]
qsys_ip_addr = default_data["devices"][local_id]["qsys"]
num_of_zones = default_data["devices"][local_id].get("num_of_zones", 12)
num_of_relays = default_data["devices"][local_id].get("num_of_relays", 4)
venue_name = default_data["devices"][local_id].get("name", "")
zone_name = default_data["devices"][local_id].get("zones", [])
local_device = {}
# qrc
page = {
    "num_of_zones": num_of_zones,
    "qrc_page_id": 0,
    "qrc_chime": True,
    "qrc_max_page_time": 30,
    "qrc_is_on_air": False,
    "qrc_page_status": None,
    "power_on_delay": power_on_delay,
    "barixes_ip_addr": {},
    "tp_qrc_on_air_zone_list":[False] * num_of_zones,
    "qrc_zone_gain_status": [0.0] * num_of_zones,
    "qrc_zone_mute_status": [False] * num_of_zones,
    "qrc_zone_on_air_status": [False] * num_of_zones
}