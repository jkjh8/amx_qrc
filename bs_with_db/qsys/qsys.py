from mojo import context
import time, threading
from config import *
from modules.qrc2 import QRC
from qsys.parser import qrc_parser
from qsys.qrc_comm import qrc_get_all_zone_gain, qrc_get_all_zone_mute
from db.db_setup import db_setup_find_one

qrc_check_event_poll = context.services.get("timeline")
tp_btn_refresh_loop = context.services.get("timeline")
DV_TP = context.devices.get("AMX-10001")
qrc = None

def qrc_check_zone_props(_):
    global qrc
    onair = db_setup_find_one({"key":"onair"})["Bool"]
    if  onair or not qrc.connected:
        return
    try:
        qrc_get_all_zone_gain(qrc)
        qrc_get_all_zone_mute(qrc)
    except Exception as e:
        print(f"qrc_check_zone_props() Exception {e=}")

def _btn_refresh_is_on_air_btn(_):
    try:
        DV_TP.port[2].channel[11].value = db_setup_find_one({"key":"onair"})["Bool"]
    except Exception as e:
        print(f"_btn_refresh_is_on_air_btn() Exception {e=}")

def qrc_connected(Status):
    if Status:
        print("qrc connected")
        time.sleep(1)
        qrc_check_zone_props(None)
    else:
        print("qrc not connected")

def init_qsys():
    global qrc
    ipaddr = db_setup_find_one({"key":"qsys"})["String"]
    print(f"qsys ipaddr {ipaddr}")
    qrc = QRC(ipaddr, qrc_parser)
    threading.Thread(target=_init, daemon=True).start()
    
    
def _init():
    qrc.connect(qrc_connected)
    qrc_check_event_poll.expired.listen(qrc_check_zone_props)
    tp_btn_refresh_loop.expired.listen(_btn_refresh_is_on_air_btn)
    qrc_check_event_poll.start([500000], True, -1)
    tp_btn_refresh_loop.start([1000], True, -1)
    
    
