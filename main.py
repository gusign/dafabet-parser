import time
import json

from src.parser import DafabetParser
from src.properties import *


if __name__ == '__main__':
    parser = DafabetParser(headless=True)
    parser.set_window_size(WINDOWS_SIZE)
    parser.get_url(URL)

    if LOGIN != '' and PASSWORD != '':
        parser.login(LOGIN, PASSWORD)

    parser.switch_to_sports_frame(IMPLICITLY_WAIT_FRAMES)

    # wait until frame will be completely loaded
    time.sleep(EXPLICITLY_WAIT_BETFRAME_LOADING)

    parser.change_odd_format_to_decimal(IMPLICITLY_WAIT_ELEMENTS)

    parser.select_live_tab(IMPLICITLY_WAIT_ELEMENTS)

    parser.select_soccer(IMPLICITLY_WAIT_ELEMENTS)

    # wait until all matches will be loaded
    time.sleep(EXPLICITLY_WAIT_LEAGUES_LOADING)

    odds_list = parser.parse_data(IMPLICITLY_WAIT_ELEMENTS)

    with open('odds.json', 'w') as f:
        json.dump(odds_list.__dict__, f, default=lambda x: x.__dict__,
                  indent=4)
