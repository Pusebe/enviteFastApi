from fastapi import FastAPI
from player import Player
from game import Game
import json

app = FastAPI()
game = None
player_names = []

@app.get("/join/{player_name}")
def join_game(player_name: str):
    if len(player_names) < 2:
        player_names.append(player_name)
        return f"¡Jugador {player_name} se ha unido al juego!"
    else:
        return "El juego ya tiene 2 jugadores"

@app.get("/start")
def start_game():
    global game

    if len(player_names) == 2:
        players = [Player(name) for name in player_names]
        game = Game(players)
        game.set_next_player()
        game.prepare_deck_and_deal()

        for i, hand in enumerate(game.hands):
            game.players[i].receive_cards(hand)
        # Resto del código del juego...

        return "¡Juego iniciado!"
    else:
        return "No se pueden iniciar el juego. Deben unirse 2 jugadores."
    
@app.get("/hand/{player_id}")
def show_hand(player_id: int):
    if game is not None and player_id in [0, 1]:
        player = game.players[player_id]
        hand_dict = [[i, card.value, card.suit] for i, card in enumerate(player.hand)]
        return hand_dict
    else:
        return "No se puede mostrar la mano. El juego no ha comenzado o el jugador no existe."

# Ruta para que cada jugador elija una carta
@app.get("/play/{player_id}/{card_index}")
def play_card(player_id: int, card_index: int):
    if game is not None and player_id in [1, 2]:
        player = game.players[player_id - 1]
        card = player.play_card(card_index)
        return f"El Jugador {player_id} ha jugado la carta: {card.value} de {card.suit}"
    else:
        return "No se puede jugar la carta. El juego no ha comenzado o el jugador no existe."

# Ruta para mostrar el resultado de cada ronda
@app.get("/round_result")
def round_result():
    if game is not None:
        result = ""
        for i, card in enumerate(game.cards_played):
            result += f"El Jugador {i+1} jugó: {card.value} de {card.suit}\n"
        result += f"La vira es el {game.deck.vira.value} de {game.deck.vira.suit}\n"
        result += f"\n{game.winning_player.name} gana la mano con {game.highest_card.value} de {game.highest_card.suit}\n"
        return result
    else:
        return "El juego no ha comenzado."

# Resto de las rutas y lógica del juego...