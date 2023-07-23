import random
from .card import Card

class Deck:
    def __init__(self):
        self.suits = ["Oros","Copas", "Espadas", "Bastos"]
        self.values = {
            "As": 8,
            "Dos": 2,
            "Tres": 3,
            "Cuatro": 4,
            "Cinco": 5,
            "Seis": 6,
            "Siete": 7,
            "Sota": 10,
            "Caballo": 11,
            "Rey": 12
        }
        self.cards = [Card(value, suit, self.values[value]) for suit in self.suits for value in self.values]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def cut_deck(self):
        cut_index = random.randint(0, len(self.cards)-1)
        self.vira = self.cards.pop()
        self.cards = self.cards[cut_index:] + self.cards[:cut_index]

    def rebuild_deck(self):
        self.cards = [Card(value, suit, self.values[value]) for suit in self.suits for value in self.values]

    def deal(self, num_players):
        hands = [[] for _ in range(num_players)]
        for i in range(num_players):
            for _ in range(3): #Número de cartas a repartir
                card = self.cards.pop(0)
                hands[i].append(card)
        return hands
        