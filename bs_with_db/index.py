import json, time, threading
from mojo import context
from bs import init_udp_server, get_data_from_server
from qsys.qsys import init_qsys
from qsys.buttons import init_buttons_evt, init_UI, update_tp_gain_mute, update_tp_btn_names
from config import DV_TP, logger, venue_name, zone_name, page, qrc_zones
from relay import check_relay

def tp_online(_):
    global venue_name, zone_name, page, qrc_zones
    try:
        update_tp_btn_names()
        update_tp_gain_mute()
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
    # menu bottons
    init_UI()
    
    init_buttons_evt()
    
    context.run(globals())
