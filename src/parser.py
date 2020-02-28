import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (StaleElementReferenceException,
                                        NoSuchElementException,
                                        TimeoutException)

from src.helper_functions import try_convert_to_float, is_element_empty
from src.odds_classes import LiveSoccerOdds, LiveSoccerOddsList


class DafabetParser:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')

        self.driver = webdriver.Chrome(chrome_options=self.options)

    def set_window_size(self, windows_size):
        self.driver.set_window_size(*windows_size)

    def get_url(self, url):
        self.driver.get(url)

    def login(self, login, password):
        login_element = self.driver.find_element_by_id('LoginForm_username')
        login_element.send_keys(login)
        password_element = self.driver.find_element_by_id('LoginForm_password')
        password_element.send_keys(password)
        password_element.send_keys(Keys.ENTER)

    def switch_to_sports_frame(self, wait_time):
        WebDriverWait(self.driver, wait_time).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'betframe')))
        WebDriverWait(self.driver, wait_time).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'sportsFrame')))

    def change_odd_format_to_decimal(self, wait_time):
        odd_format = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.icon-malayOdds:nth-child(1)')))

        ActionChains(self.driver).move_to_element(odd_format).click(
            odd_format).perform()

        decimal_odd_format = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.icon-decimalOdds')))

        ActionChains(self.driver).move_to_element(decimal_odd_format).click(
            decimal_odd_format).perform()

    def select_live_tab(self, wait_time):
        live_tab = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.widgetPanel:nth-child(5) .icon-sportsMenu-live > '
                 '.itemContent')))

        ActionChains(self.driver).move_to_element(live_tab).click(
            live_tab).perform()

    def select_soccer(self, wait_time):
        all_tab = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.icon-sportAll .checkbox')))

        ActionChains(self.driver).move_to_element(all_tab).click(
            all_tab).perform()

        soccer_tab = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.icon-sport1 .checkbox')))

        ActionChains(self.driver).move_to_element(soccer_tab).click(
            soccer_tab).perform()

    def scroll_till_page_end(self):
        script = "window.scrollTo(0, document.body.scrollHeight);" \
                 "var lenOfPage=document.body.scrollHeight;" \
                 "return lenOfPage;"
        page_len = self.driver.execute_script(script)
        match = False
        while not match:
            last_len = page_len
            page_len = self.driver.execute_script(script)
            if last_len == page_len:
                match = True

    def get_leagues(self, wait_time):
        leagues = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'leagueGroup')))
        return leagues

    def get_league_name(self, league):
        try:
            name = league.find_element_by_class_name(
                'leagueName').text.replace(
                'Soccer / ', '')
        except StaleElementReferenceException:
            return False
        return name

    def get_matches(self, league):
        matches = league.find_elements_by_class_name('matchArea')
        return matches

    def get_teams(self, match):
        try:
            teams = match.find_elements_by_xpath(
                './/div[@class="team"]//div[@class="text"]')
        except StaleElementReferenceException:
            return False
        return teams

    def get_teams_names(self, teams):
        home_team = teams[0].find_element_by_xpath('./span').text
        away_team = teams[1].find_element_by_xpath('./span').text
        return home_team, away_team

    def get_red_card(self, element):
        try:
            red_card = element.find_element_by_xpath(
                './div[@class="card "]').text
            red_card = int(red_card)
        except NoSuchElementException:
            red_card = 0
        return red_card

    def get_red_cards(self, teams):
        red_card_h = self.get_red_card(teams[0])
        red_card_a = self.get_red_card(teams[1])
        return red_card_h, red_card_a

    def get_scores(self, match):
        score = match.find_element_by_xpath(
            './/div[@class="score"]').text.split('-')
        score_h = int(score[0])
        score_a = int(score[1])
        return score_h, score_a

    def get_date(self, match):
        date = match.find_element_by_class_name('timePlaying').text
        date = date.replace("'", "")
        return date

    def get_odds_row(self, match):
        multi_odds = match.find_elements_by_class_name('multiOdds')
        return multi_odds

    def get_odds_w_opt(self, odd_row):
        odds_w_opt = odd_row.find_elements_by_xpath(
            './div[@class="odds subtxt"]')
        return odds_w_opt

    def get_odds_w_opt_bet(self, odd_w_opt):
        odds_bet = odd_w_opt.find_elements_by_class_name(
            'oddsBet')
        ft_h_odd = float(odds_bet[0].text)
        ft_a_odd = float(odds_bet[1].text)
        return ft_h_odd, ft_a_odd

    def get_opts(self, odd_w_opt):
        options = odd_w_opt.find_elements_by_class_name('txt')
        ft_h_opt_raw = options[0].text
        ft_a_opt_raw = options[1].text
        ft_h_opt = try_convert_to_float(ft_h_opt_raw)
        ft_a_opt = try_convert_to_float(ft_a_opt_raw)
        return ft_h_opt, ft_a_opt

    def get_odds_wo_opt(self, odd_row):
        odds = odd_row.find_elements_by_xpath('./div[@class="odds"]')
        return odds

    def get_odds_wo_opt_bet(self, odd_wo_opt):
        odds_bet = odd_wo_opt.find_elements_by_class_name('betArea')
        ft_1x2_h = float(odds_bet[0].text)
        ft_1x2_a = float(odds_bet[1].text)
        ft_1x2_d = float(odds_bet[2].text)
        return ft_1x2_h, ft_1x2_a, ft_1x2_d

    def get_others_panel(self, match):
        others = match.find_element_by_class_name('others')
        return others

    def open_more_bet_types(self, others):
        more_btn = others.find_element_by_xpath(
            './button[@title="More Bet Types"]')

        ActionChains(self.driver).move_to_element(more_btn).click(
            more_btn).perform()

    def get_correct_score_set(self, wait_time):
        cs_set = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'oneSet-a')))
        return cs_set

    def get_correct_scores(self, cs_set):
        all_scores = cs_set.find_element_by_class_name('betTypeTitle')
        scores = all_scores.find_elements_by_class_name('betCol')
        return scores

    def get_odds_for_correct_scores(self, cs_set):
        all_odds_cs = cs_set.find_element_by_class_name('betTypeContent')
        odds_cs = all_odds_cs.find_elements_by_class_name('betCol')
        return odds_cs

    def get_odds_for_cs_bet(self, odd_cs):
        bet_areas_cs = odd_cs.find_elements_by_class_name('betArea')
        odd_h_cs = bet_areas_cs[0].text.replace('--', '-')
        odd_a_cs = bet_areas_cs[1].text.replace('--', '-')
        odd_h_cs = try_convert_to_float(odd_h_cs)
        odd_a_cs = try_convert_to_float(odd_a_cs)
        return odd_h_cs, odd_a_cs

    def parse_data(self, wait_time):
        odds_list = LiveSoccerOddsList()

        leagues = self.get_leagues(wait_time)
        for i in range(len(leagues)):
            # after reload of leagues there can be less values
            try:
                # returns False if element is not attached to the page document
                name = self.get_league_name(leagues[i])
            except IndexError:
                break

            # reload leagues if league is not available anymore
            while True:
                if isinstance(name, bool):
                    leagues = self.get_leagues(wait_time)
                    # after reload of leagues there can be less values
                    try:
                        name = self.get_league_name(leagues[i])
                    except IndexError:
                        # indicator for breaking leagues loop
                        break_leagues = True
                        break
                else:
                    break_leagues = False
                    break

            if break_leagues:
                break

            matches = self.get_matches(leagues[i])
            for j in range(len(matches)):
                # returns False if element is not attached to the page document
                try:
                    # after reload of matches there can be less values
                    teams = self.get_teams(matches[j])
                except IndexError:
                    break

                # reload matches if match is not available anymore
                while True:
                    if isinstance(teams, bool):
                        try:
                            matches = self.get_matches(leagues[i])
                            teams = self.get_teams(matches[j])
                        except IndexError:
                            # indicator for breaking matches loop
                            break_matches = True
                            break
                    else:
                        break_matches = False
                        break

                if break_matches:
                    break

                home_team, away_team = self.get_teams_names(teams)
                red_card_h, red_card_a = self.get_red_cards(teams)
                score_h, score_a = self.get_scores(matches[j])
                date = self.get_date(matches[j])

                # initialize odds object which will be appended to final list
                odds_obj = LiveSoccerOdds(name, home_team, away_team,
                                          red_card_h, red_card_a, score_h,
                                          score_a, date)

                odds_row = self.get_odds_row(matches[j])

                for odd_row in odds_row:
                    # start parsing FT_HDP, FT_OU odds
                    odds_w_opt = self.get_odds_w_opt(odd_row)

                    for k, odd_w_opt in enumerate(odds_w_opt):
                        # parse only 2 types of odds with opt (FT_HDP, FT_OU)
                        if k > 1:
                            break
                        # check if odds with options are present
                        if is_element_empty(odd_w_opt):
                            continue

                        ft_h_odd, ft_a_odd = self.get_odds_w_opt_bet(odd_w_opt)
                        ft_h_opt, ft_a_opt = self.get_opts(odd_w_opt)

                        # for FT_HDP
                        if k == 0:
                            bet_types = ('FT_HDP_h', 'FT_HDP_a')
                            if ft_h_opt == '':
                                ft_h_opt = ft_a_opt * -1
                            else:  # ft_a_opt == ''
                                ft_a_opt = ft_h_opt * -1
                        # for FT_OU
                        else:
                            bet_types = ('FT_OU_o', 'FT_OU_u')
                            if ft_h_opt == 'u':
                                ft_h_opt = ft_a_opt
                            else:  # ft_a_opt == 'u'
                                ft_a_opt = ft_h_opt

                        # append odds with options for home team
                        odds_obj.append_mainline_bets(bet_type=bet_types[0],
                                                      opt=ft_h_opt,
                                                      odd=ft_h_odd)
                        # append odds with options for away team
                        odds_obj.append_mainline_bets(bet_type=bet_types[1],
                                                      opt=ft_a_opt,
                                                      odd=ft_a_odd)

                    # start parsing FT_1X2 odds
                    odds_w_opt = self.get_odds_wo_opt(odd_row)

                    for l, odd_wo_opt in enumerate(odds_w_opt):
                        # parse only first type of odds without opt (FT_1X2)
                        if l > 0:
                            break
                        # check if odds without options are present
                        if is_element_empty(odd_wo_opt):
                            continue

                        ft_1x2_h, ft_1x2_a, ft_1x2_d = \
                            self.get_odds_wo_opt_bet(odd_wo_opt)

                        bet_types = ('FT_1X2_h', 'FT_1X2_a', 'FT_1X2_d')

                        # append odds without options for home team
                        odds_obj.append_mainline_bets(bet_type=bet_types[0],
                                                      opt='-',
                                                      odd=ft_1x2_h)
                        # append odds without options for away team
                        odds_obj.append_mainline_bets(bet_type=bet_types[1],
                                                      opt='-',
                                                      odd=ft_1x2_a)
                        # append odds without options for draw
                        odds_obj.append_mainline_bets(bet_type=bet_types[2],
                                                      opt='-',
                                                      odd=ft_1x2_d)

                # start parsing FT_CS
                others = self.get_others_panel(matches[j])
                # check if other bet types are available
                if is_element_empty(others):
                    odds_list.append_live_soccer_odds(odds_obj)
                    continue

                self.open_more_bet_types(others)

                try:
                    cs_set = self.get_correct_score_set(wait_time)
                except TimeoutException:
                    odds_list.append_live_soccer_odds(odds_obj)
                    continue

                scores = self.get_correct_scores(cs_set)
                odds_cs = self.get_odds_for_correct_scores(cs_set)

                for g in range(len(scores)):
                    # parse scores until 3-0
                    if g == 4:
                        break

                    odd_h_cs, odd_a_cs = self.get_odds_for_cs_bet(odds_cs[g])

                    # append odds with correct score for home team
                    odds_obj.append_mainline_bets(bet_type='FT_CS_h',
                                                  opt=scores[g].text,
                                                  odd=odd_h_cs)
                    # append odds with correct score for away team
                    odds_obj.append_mainline_bets(bet_type='FT_CS_a',
                                                  opt=scores[g].text,
                                                  odd=odd_a_cs)

                # append odds object to final list
                odds_list.append_live_soccer_odds(odds_obj)
        return odds_list
