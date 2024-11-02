from config import *

def set_relay(idx, state_bool):
    if idx >= 1 and idx <= num_of_relays:
        # print("set_relay() {} {}".format(idx, state_bool))
        DV_RELAYS[idx - 1].state.value = state_bool
        return state_bool
    
def set_all_relay(state_bool):
    for i in range(num_of_relays):
        DV_RELAYS[i].state.value = state_bool
    
def check_relay(_):
    try:
        if num_of_relays == 0 or not qrc_zone_on_air_status:
            return
        relays = min(num_of_relays, len(qrc_zone_on_air_status))
        for idx in range(relays):
            set_relay(idx, qrc_zone_on_air_status[idx])
    except Exception as e:
        logger.error("check_relay() {}".format(e))
            