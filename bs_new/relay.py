from config import *

def set_relay(idx, state_bool):
    if idx >= 1 and idx <= num_of_relays:
        # print("set_relay() {} {}".format(idx, state_bool))
        DV_RELAYS[idx - 1].state.value = state_bool
        return state_bool
    
def set_all_relay(state_bool):
    try:
        for i in range(num_of_relays):
            DV_RELAYS[i].state.value = state_bool
        logger.info("set_all_relay() {}".format(state_bool))
    except Exception as e:
        logger.error("set_all_relay() {}".format(e))
    
def check_relay(_):
    global page
    try:
        if num_of_relays == 0 or not page["qrc_zone_on_air_status"]:
            return
        relays = min(num_of_relays, len(page["qrc_zone_on_air_status"]))
        for idx in range(relays):
            set_relay(idx, page["qrc_zone_on_air_status"][idx])
    except Exception as e:
        logger.error("check_relay() {}".format(e))
            