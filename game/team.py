class Team:
    def __init__(self):
        self.players = []  # Lista de jugadores en el equipo
        self.rounds_won = 0  # Contador de rondas ganadas por el equipo
        self.sets_won = 0
        self.games_won = 0

    def add_player(self, player):
        self.players.append(player)

    def increment_rounds_won(self):
        self.rounds_won += 1

    def increment_sets_won(self):
        self.sets_won += 2

    def increment_games_won(self):
        self.games_won += 1

    def has_won_round(self, points_to_win_round):
        return self.rounds_won >= points_to_win_round
    
    def has_won_set(self, points_to_win_set):
        return self.sets_won >= points_to_win_set
    
    def has_won_game(self, points_to_win_game):
        return self.games_won >= points_to_win_game