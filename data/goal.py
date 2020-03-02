class Goal:
    def __init__(self, time, team, kind, strength, scorer, assist1, assist2, goalie, result):
        self.time = time
        self.team = team
        self.kind = kind
        self.strength = strength
        self.scorer = scorer
        self.assist1 = assist1
        self.assist2 = assist2
        self.goalie = goalie
        self.result = result

    def __repr__(self):
        return "Goal[{}, {}, {}, {}, {}, {}, {}, {}]".format(self.time, self.team, self.kind, self.strength, self.scorer, self.assist1, self.assist2, self.goalie)
