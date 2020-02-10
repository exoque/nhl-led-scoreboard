from data.game import GameStateChange


class Data:
    def __init__(self):
        self.games = {}
        self.current_item = 0
        self.last_item = -1

    def add_game(self, game, events):
        self.games[game.key] = DataGame(game, events)

    def update_game(self, key, game, events):
        if key not in self.games:
            self.add_game(game, events)

        data_game = self.games[key]
        data_game.update_game(game)
        data_game.update_events(events)
        return data_game.game_change

    def update_events(self, key, events):
        self.games[key].events = events

    def get_next_item_to_display(self):
        if self.games is None or len(self.games) == 0:
            return None

        if self.last_item != -1:
            self.current_item = (self.current_item + 1) % len(self.games)

        self.last_item = self.current_item

        return self.games[list(self.games.keys())[self.current_item]]

    def _item_has_changed(self):
        return self.current_item != self.last_item


class DataGame:
    def __init__(self, game, events):
        self.game = game
        self.events = events
        self.game_change = GameStateChange.NONE

    def update_game(self, game):
        game_state_change = self.game.update(game)
        self.game_change = game_state_change
        return game_state_change

    def update_events(self, events):
        for key, value in events.items():
            self.events[key] = value

