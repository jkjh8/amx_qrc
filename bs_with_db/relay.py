from config import *
import http.client

def set_relay(idx, state_bool):
    global DV_RELAYS, num_of_relays, logger
    if idx >= 1 and idx <= num_of_relays:
        DV_RELAYS[idx - 1].state.value = state_bool
        logger.info("set_relay() {} {}".format(idx, state_bool))
        return state_bool
    
def set_all_relay(state_bool):
    global logger, DV_RELAYS
    try:
        for i in range(num_of_relays):
            DV_RELAYS[i].state.value = state_bool
        logger.info("set_all_relay() {}".format(state_bool))
    except Exception as e:
        logger.error("set_all_relay() {}".format(e))
    
def check_relay(_):
    global page, qrc_zones_onair, num_of_relays, logger, DV_RELAYS
    try:
        if num_of_relays == 0 or not qrc_zones_onair:
            return
        relays = min(num_of_relays, len(qrc_zones_onair))
        for idx in range(relays):
            DV_RELAYS[idx].state.value = qrc_zones_onair[idx]
    except Exception as e:
        logger.error("check_relay() {}".format(e))
            
def barix_set_relay(ip_address, state):
    global logger
    try:
        state_str = 1 if state else 0
        conn = http.client.HTTPConnection(ip_address)
        conn.request("GET", f"/rc.cgi?R={state_str}")
        response = conn.getresponse()
        data = response.read()
        conn.close()
        logger.info(f"barix_set_relay() ip_address={ip_address} state={state}")
        return data.decode()
    except Exception as e:
        logger.error(f"barix_set_relay() Exception e={e}")
        
def barix_set_relay_all(state):
    global logger, barixes_ip_addr
    try:
        for ip in barixes_ip_addr.values():
            barix_set_relay(ip, state)
    except Exception as e:
        logger.error(f"barix_set_realy_all() Exception e={e}")
        
def barix_set_relays (zones, state):
    global logger, barixes_ip_addr
    print(f"barix_set_relays() {zones} {state} {barixes_ip_addr}")
    try:
        for idx in zones:
            if idx in barixes_ip_addr:
                barix_set_relay(barixes_ip_addr[idx], state)
    except Exception as e:
        logger.error(f"barix_set_relays() Exception e={e}")

