import json
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_cards(self, cards):
        self.hand.clear()
        self.hand.extend(cards)

    def show_hand(self):
        return self.hand
    
    def json_hand(self):
        cards_data = []
        for card in self.hand:
            if card is not None:
                card_data = {
                    "value": card.value,
                    "suit": card.suit,
                    "numeric_value": card.numeric_value
                }
                cards_data.append(card_data)
        return json.dumps(cards_data)

    def play_card(self, choice):
        try:
            choice_index = int(choice) - 1
            if choice_index < 0 or choice_index >= len(self.hand):
                raise ValueError
            played_card = self.hand[choice_index]
            self.hand[choice_index] = None
            return played_card        
        except ValueError:
            print("Entrada inválida. Por favor, elige un número válido correspondiente a una de tus cartas.")