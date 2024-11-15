import threading
from mojo import context
from db.db_setup import db_setup_init, db_setup_find_one
from db.db_zones import db_zones_init
from bs import init_udp_server, get_data_from_server
from qsys.qsys import qrc, init_qsys
from qsys.buttons import init_buttons_evt, init_UI, update_ui_from_db
from config import init_default_from_json
from relay import check_relay

DV_TP = context.devices.get("AMX-10001")
logger = context.log

def tp_online(_):
    try:
        update_ui_from_db()
    except Exception as e:
        logger.error(f"tp_online() {e=}")
    
def bs_check(_):
    get_data_from_server()
    
if __name__ == "__main__":
    # start db
    db_setup_init()
    db_zones_init()
    # default data from json file
    init_default_from_json()
    # get_data_form_server
    get_data_from_server()
    # udp server start
    init_udp_server(9000)
    # qsys start
    init_qsys()
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
    for i in range(21, 44):
        DV_TP.port[2].channel[i].value = False
    init_buttons_evt()
    update_ui_from_db()
    
    
    context.run(globals())
