from mojo import context
import time
from config import *
from modules.qrc2 import QRC
from qsys.parser import qrc_parser
from qsys.qrc_comm import qrc_get_all_zone_gain, qrc_get_all_zone_mute

qrc_check_event_poll = context.services.get("timeline")
tp_btn_refresh_loop = context.services.get("timeline")

qrc = QRC(qsys_ip_addr, qrc_parser)

def qrc_check_zone_props(_):
    global page, qrc
    if page["qrc_onair"] or not qrc.connected:
        return
    try:
        qrc_get_all_zone_gain(qrc)
        qrc_get_all_zone_mute(qrc)
    except Exception as e:
        print(f"qrc_check_zone_props() Exception {e=}")

def _btn_refresh_is_on_air_btn(_):
    global page
    try:
        DV_TP.port[2].channel[11].value = page["qrc_onair"]
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
    qrc.connect(qrc_connected)
    
    qrc_check_event_poll.expired.listen(qrc_check_zone_props)
    tp_btn_refresh_loop.expired.listen(_btn_refresh_is_on_air_btn)
    qrc_check_event_poll.start([500000], True, -1)
    tp_btn_refresh_loop.start([1000], True, -1)
    
