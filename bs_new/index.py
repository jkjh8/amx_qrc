import json, time, threading
from mojo import context
from modules.UIMenu import UIMenu
from bs import init_udp_server, get_data_from_server
from qsys.qsys import init_qsys
from qsys.buttons import init_buttons_evt, btn_refresh_page_time_count, init_UI
from config import logger, venue_name, zone_name
from tp import *
from relay import check_relay

def tp_online(_):
    global venue_name, zone_name, page, qrc_zones
    try:
        if venue_name:
            DV_TP.port[2].send_command(f"^UNI-{1},0," + "".join(format(ord(char), '04X') for char in venue_name))
        if zone_name and len(zone_name) > 0:
            for zone_id, zone_name in enumerate(zone_name):
                DV_TP.port[2].send_command(f"^UNI-{zone_id + 21},0," + "".join(format(ord(char), '04X') for char in zone_name))
        DV_TP.port[2].channel[7].value = page["qrc_chime"]
        DV_TP.port[2].send_command("^TXT-5,0," + str(page["qrc_max_page_time"]) + "s")
        for idx in range(1, page["num_of_zones"] + 1):
            DV_TP.port[2].channel[idx + 20].value = qrc_zones[idx - 1]
    except Exception as e:
        logger.error(f"tp_online() {e=}")
    
def bs_check(_):
    get_data_from_server()
    
if __name__ == "__main__":
    # get_data_form_server
    get_data_from_server()
    # udp server start
    init_udp_server(9000)
    # qsys start
    threading.Thread(target=init_qsys, daemon=True).start()
    # tp online
    DV_TP.online(tp_online)
    # bs check poll
    bs_check_poll = context.services.get("timeline")
    bs_check_poll.start([600000], True, -1)
    bs_check_poll.expired.listen(bs_check)    
    # server starts
    relay_on_air_poll = context.services.get("timeline")
    relay_on_air_poll.expired.listen(check_relay)
    relay_on_air_poll.start([100000], True, -1)
    # UIMenu(DV_TP)
    init_UI()
    
    init_buttons_evt()
    
    context.run(globals())
