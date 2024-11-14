import threading
from mojo import context
from modules.db import Database
from bs import init_udp_server, get_data_from_server
from qsys.qsys import init_qsys
from qsys.buttons import init_buttons_evt, init_UI, update_tp_gain_mute, update_tp_btn_names, update_ui_from_db
from config import DV_TP, logger, venue_name, zone_name, page, qrc_zones
from relay import check_relay

def tp_online(_):
    try:
        # update_tp_btn_names()
        # update_tp_gain_mute()
        update_ui_from_db()
    except Exception as e:
        logger.error(f"tp_online() {e=}")
    
def bs_check(_):
    get_data_from_server()
    
if __name__ == "__main__":
    # start db
    db = Database()
    db.create_table('setup', { 'key': 'TEXT', 'Value': 'INTEGER', 'String': 'TEXT', 'Bool': 'BOOLEAN' })
    db.create_table('zones', { 'Name': 'TEXT', 'Gain': 'REAL', 'Mute': 'BOOLEAN', 'Active': 'BOOLEAN', 'Barix': 'TEXT', 'Sel': 'BOOLEAN' })
    db.insert('setup', {'key': 'chime', 'Bool': True })
    db.insert('setup', {'key': 'pageTime', 'Value': 30 })
    print("DB Started")
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
