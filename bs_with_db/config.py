import json
from mojo import context
from db.db_setup import db_setup_update
# devices
# DV_MUSE = context.devices.get("idevice")
# DV_TP = context.devices.get("AMX-10001")
# DV_RELAYS = context.devices.get("idevice").relay
# # logger
logger = context.log
#  variables
local_id = 0

def init_default_from_json():
    with open("data.json", "r") as f:
        default_data = json.load(f)
        db_setup_update({"Value": default_data["devices"][local_id]["num_of_relays"]}, {"key": "numOfRelay"})
        db_setup_update({"String": default_data["main_server_ip_addr"]}, {"key": "serverIpAddr"})
        db_setup_update({"String": default_data["devices"][local_id]["qsys"]}, {"key": "qsys"})
    