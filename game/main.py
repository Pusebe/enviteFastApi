
from player import Player
from game import Game

player_names = ["Jugador 1", "Jugador 2"]
players = [Player(name) for name in player_names]

game = Game(players)
game.set_next_player()
while not (game.team1.has_won_game(game.points_to_win_game) or game.team2.has_won_game(game.points_to_win_game)):
    game.reset_sets()
    while not (game.team1.has_won_set(game.points_to_win_set) or game.team2.has_won_set(game.points_to_win_set)):
        game.reset_rounds()
        game.prepare_deck_and_deal()
        for i, hand in enumerate(game.hands):
                        game.players[i].receive_cards(hand)

        while not (game.team1.has_won_round(game.points_to_win_round) or game.team2.has_won_round(game.points_to_win_round)):
            
            print(f"La vira es el {game.deck.vira.value} de {game.deck.vira.suit}")
            
            #a partir de aqui es único para cada jugador
            """
            game.players[0].show_hand()
            card = game.players[0].play_card(1)
            game.cards_played.append(card)

            game.players[1].show_hand()
            card = game.players[1].play_card(1)
            game.cards_played.append(card)
            """
            for player in game.players_order:
                player.show_hand()
                index = input("Elige carta:")
                card = player.play_card(index)
                game.cards_played.append(card)


            highest_card = game.determine_highest_card(cards=game.cards_played)

            game.play_rounds(highest_card)
            # El jugador que jugó la carta más alta gana la ronda
            print(f"\nEl jugador 1 jugó: {game.cards_played[0].value} de {game.cards_played[0].suit}\n"
                f"El jugador 2 jugó: {game.cards_played[1].value} de {game.cards_played[1].suit}\n" )
            print(f"La vira es el {game.deck.vira.value} de {game.deck.vira.suit}")
            print(f"\n{game.winning_player.name} gana la mano con {highest_card.value} de {highest_card.suit}\n")

            game.set_next_player()
                    
        if game.team1.has_won_round(game.points_to_win_round):
            game.team1.increment_sets_won()
            print("El equipo 1uno ganó la ronda y dos piedritas")
            
        if game.team2.has_won_round(game.points_to_win_round):
            game.team2.increment_sets_won()
            print("El equipo 2dos ganó la ronda y dos piedritas")

    if game.team1.has_won_set(game.points_to_win_set):
        game.team1.increment_games_won()
    else:
        game.team2.increment_games_won()
    print(f"El equipo 1 tiene {game.team1.games_won} chicos.\nY el equipo 2 tiene {game.team2.games_won} chicos.\n")

if game.team1.has_won_game(game.points_to_win_game):
    print("El equipo 1 gana la partida.")
else:
    print("El equipo 2 gana la partida.")