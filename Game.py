from Network import Network

class Game():
    def __init__(self):
        self.ready = False
        self.Players_pos = {}
        self.winner = None

    def get_Player_pos(self, data):
        for k, v in data.items():
            key = int(k)       # undoing the conversion of dict.key to str due to JSON serialization
            self.Players_pos[key] = v

    def is_Over(self):  # look at the scores and decide to end the game by setting bool
        for k, v in self.Players_pos.items():
            if v[-1] >= 10:
                self.winner = k
                return True
            return False






