import json, time, threading
from mojo import context
from modules.UIMenu import UIMenu
from bs import init_udp_server, get_data_from_server
from qsys.qsys import init_qsys
from qsys.buttons import init_buttons_evt, btn_refresh_page_time_count
from config import logger, venue_name, zone_name
from tp import *
from relay import check_relay

def tp_online(_):
    global venue_name, zone_name, page
    try:
        UIMenu(DV_TP)
        if venue_name:
            tp_set_btn_text_unicode(DV_TP, 2, 1, convert_text_to_unicode(text=venue_name))
        if zone_name and len(zone_name) > 0:
            for zone_id, zone_name in enumerate(zone_name):
                tp_set_btn_text_unicode(DV_TP, 2, zone_id + 20 + 1, convert_text_to_unicode(zone_name))
                
        btn_refresh_all_zone_selected_btn()
        btn_refresh_page_time_count()
        tp_set_button(DV_TP, 2, 7, page["qrc_chime"])
        
        
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
    # server start
    relay_on_air_poll = context.services.get("timeline")
    relay_on_air_poll.expired.listen(check_relay)
    relay_on_air_poll.start([100000], True, -1)
    
    init_buttons_evt()
    
    context.run(globals())
