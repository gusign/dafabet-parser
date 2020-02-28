class LiveSoccerOddsList:
    def __init__(self):
        self.final_json = []

    def __repr__(self):
        return ', '.join([str(x) for x in self.final_json])

    def append_live_soccer_odds(self, live_soccer_odds):
        self.final_json.append(live_soccer_odds)


class LiveSoccerOdds:
    def __init__(self, league, home_team, away_team, red_card_h, red_card_a,
                 score_h, score_a, date):
        self.sport = 'Soccer'
        self.is_live = 1
        self.league = league
        self.home_team = home_team
        self.away_team = away_team
        self.red_card_h = red_card_h
        self.red_card_a = red_card_a
        self.score_h = score_h
        self.score_a = score_a
        self.date = date
        self.mainline_bets = []

    def __repr__(self):
        return f'sport: {self.sport}\n' \
               f'is_live: {self.is_live}\n' \
               f'league: {self.league}\n' \
               f'home_team: {self.home_team}\n' \
               f'away_team: {self.away_team}\n' \
               f'red_card_h: {self.red_card_h}\n' \
               f'red_card_a: {self.red_card_a}\n' \
               f'score_h: {self.score_h}\n' \
               f'score_a: {self.score_a}\n' \
               f'date: {self.date}\n' \
               f'mainline_bets: {self.mainline_bets}'

    def append_mainline_bets(self, bet_type, opt, odd):
        bet = {'type': bet_type,
               'opt': opt,
               'odd': odd}
        self.mainline_bets.append(bet)
