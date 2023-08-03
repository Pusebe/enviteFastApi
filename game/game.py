from.team import Team
from .deck import Deck

class Game:
    def __init__(self, players):
        self.hands = None
        self.team1 = Team()
        self.team2 = Team()
        self.players = players
        self.start_player_index = 0
        self.next_player_to_play = 0
        self.points_to_win_round = 2 #basas para ganar la ronda
        self.points_to_win_set = 11 # puntos para ganar un chico
        self.points_to_win_game = 2 # chicos para ganar la partida
        self.cards_played = []
        self.round_num = 1
        self.players_order = []
        self.deck = Deck()

        
    def create_teams(self):
        for i, player in enumerate(self.players):
            if i % 2 == 0:
                self.team1.add_player(player)
            else:
                self.team2.add_player(player)

    def play_rounds(self, highest_card):
        self.next_player_to_play = self.start_player_index 


        print(f"Ronda {self.round_num}")
            
        # Determinamos la carta más alta jugada en esta ronda
        winning_player_index = self.cards_played.index(highest_card)
        self.winning_player = self.players_order[winning_player_index] #escoge el indice del jugador que ganó teniendo en cuenta que puede estar ordenado diferentea la lista original
        self.next_player_to_play = self.players.index(self.winning_player)
        
        # Incrementamos el contador de rondas ganadas para el equipo del jugador ganador
        if self.winning_player in self.team1.players:
            self.team1.increment_rounds_won()
        else:
            self.team2.increment_rounds_won()

        self.round_num += 1
        self.start_player_index = (self.start_player_index + 1) % len(self.players)

    def determine_highest_card(self, cards):
        highest_card = 0
        for card in cards:
            if highest_card is 0 or self.is_higher(card, highest_card, self.deck.vira.suit):
                highest_card = card
        return highest_card

    def is_higher(self, card, previous_highest_card, vira_suit):
        
        if card.suit == "Oros" and card.numeric_value == 5 and len(self.players) > 6:
            card.numeric_value = 16
            return True
        
        if len(self.players) > 4:
            if card.suit == "Bastos" and card.numeric_value == 3:
                card.numeric_value = 15
                return previous_highest_card.numeric_value < 15
            
            if card.suit == "Bastos" and card.numeric_value == 11:
                card.numeric_value = 14
                return previous_highest_card.numeric_value < 14
            
            if card.suit == "Oros" and card.numeric_value == 10:
                card.numeric_value = 13
                return previous_highest_card.numeric_value < 13

        if card.suit == vira_suit and card.numeric_value == 2:
            card.numeric_value = 12.5
            return previous_highest_card.numeric_value < 12.5
        
        if card.suit not in [previous_highest_card.suit, vira_suit]:
            return False
        if card.suit == vira_suit and previous_highest_card.suit != vira_suit and previous_highest_card.numeric_value <= 12:
            return True
        return card.numeric_value > previous_highest_card.numeric_value

    def prepare_deck_and_deal(self):
        self.deck.rebuild_deck()     
        self.deck.shuffle()
        self.deck.cut_deck()
        self.hands = self.deck.deal(num_players=len(self.players))
        for i, hand in enumerate(self.hands):
            self.players[i].receive_cards(hand)

    def reset_sets(self):
        self.team1.sets_won = 0
        self.team2.sets_won = 0
    
    def reset_rounds(self):
        self.team1.rounds_won = 0
        self.team2.rounds_won = 0

    def set_next_player(self):
        self.players_order = self.players[self.next_player_to_play:] + self.players[:self.next_player_to_play]
