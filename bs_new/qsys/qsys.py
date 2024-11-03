from mojo import context
from config import *
from tp import *
# from lib_tp import *
from modules.qrc2 import QRC
from qsys.parser import qrc_parser
from qsys.qrc_comm import qrc_get_all_zone_gain, qrc_get_all_zone_mute

qrc_check_event_poll = context.services.get("timeline")
tp_btn_refresh_loop = context.services.get("timeline")

qrc = QRC(qsys_ip_addr, qrc_parser)


def qrc_get_on_air_zone_idx_list():
    global page
    on_air_zone_list = [i + 1 for i, zone_enabled in enumerate(qrc_zones) if zone_enabled]
    return on_air_zone_list

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
    btn_refresh_is_on_air_btn()

def init_qsys():
    qrc.connect()
    
    qrc_check_event_poll.expired.listen(qrc_check_zone_props)
    tp_btn_refresh_loop.expired.listen(_btn_refresh_is_on_air_btn)
    qrc_check_event_poll.start([40000], True, -1)
    tp_btn_refresh_loop.start([1000], True, -1)
