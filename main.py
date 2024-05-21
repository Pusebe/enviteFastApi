import uvicorn as uvicorn
from game.game import Game
from game.player import Player
from fastapi import FastAPI, Request, Response, WebSocket,  WebSocketDisconnect
from starlette.websockets import WebSocketState
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import time
import asyncio


app = FastAPI()
tables = {} 
users_connected_to_socket = {}
game_started = {}
game = None
new_set = False
card = None

# Montar la carpeta "static" para servir los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
# Configurar la ubicación de las plantillas
templates = Jinja2Templates(directory="templates")

def set_user_id(request, response):
    if not request.cookies.get("user_id"): #if is the first time of the user here, give them a cookie id
        user_id = str(uuid.uuid4())
        response.set_cookie(key="user_id", value=user_id)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    
    response = templates.TemplateResponse("index.html", {"request": request})

    set_user_id(request, response)

    return response

@app.get("/mesa/{table_id}", response_class=HTMLResponse)
async def get_table(request: Request, response: Response, table_id:int):
    
    user_id = (request.cookies.get("user_id"))
    if user_id is None:
        return RedirectResponse("/")

    if table_id not in tables:
        tables[table_id] = Game([])

    game = tables[table_id]
    
    user_exists = any(user_id in player.name for player in game.players)

    if not user_exists:
        game.players.append(Player(user_id))

    if len(game.players) > 2:
        return "Vaya, parece que ya empezó la partida"

    response = templates.TemplateResponse("table.html", {"request": request, "table_id": table_id})
    return response


@app.get("/reload", response_class=HTMLResponse)
async def reload(request: Request):
    global tables
    global users_connected_to_socket
    global game_started
    global game 
    global new_set 
    global card 


        # Cerrar todas las conexiones de WebSocket activas
    for websocket in manager.active_connections:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
    manager.active_connections.clear()

    # Reiniciar los datos de las mesas y las conexiones de usuarios
    tables = {}
    users_connected_to_socket = {}
    game_started = {}
    game = None
    new_set = False
    card = None


    response = templates.TemplateResponse("index.html", {"request": request})
    return response

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket is not None and websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                # La conexión WebSocket ya ha sido cerrada, omitir
                pass

    async def disconnect_all(self):
        # Cerrar todas las conexiones de websockets activas
        for websocket in self.active_connections:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        self.active_connections.clear()

manager = ConnectionManager()

@app.websocket("/ws/{table_id}")
async def websocket_endpoint(websocket: WebSocket, table_id:int):
    await manager.connect(websocket)
    global users_connected_to_socket 
    global game_started
    global game
    global new_set
    global card
    try:
        if table_id in tables:
            game = tables[table_id]
        else:
        # Si el WebSocket se conecta a una mesa que no existe, cerramos la conexión
            await websocket.close()
            return
        
        while True:
            data = await websocket.receive_json()
            user_id = data.get("user_id")
            card_value = data.get("card")

            if data.get("reset"):
                del tables[table_id]
                del game_started[table_id]
                users_connected_to_socket = {}
                await manager.broadcast({"reload":True})
                await manager.disconnect_all()
                break
            if card_value is not None:
                card = int(card_value)

            #comprueba si está la id y si no está la añade
            if user_id:
                websocket_user = users_connected_to_socket.get(user_id)
                if websocket_user is None or websocket_user == websocket:
                    users_connected_to_socket[user_id] = websocket
                else:
                    # Si hay otro WebSocket asociado a este usuario, cierra esta conexión
                    await websocket.close()
                    return
            #comprobamos si el juego está iniciado, y sino, lo inicializamos   
            if not game_started.get(table_id) and len(game.players) == 2:
                game_started[table_id] = True
                game.create_teams()
                #game.set_next_player()
                game.prepare_deck_and_deal()
                new_set= True
           
            if game_started.get(table_id, False):                                    
                if not (game.team1.has_won_round(game.points_to_win_round) or game.team2.has_won_round(game.points_to_win_round)): 
                    if new_set:
                        #si le toca al jugador de este websocket mandamos turn true para saber que le toca a él
                        await manager.broadcast({"turn": False})
                        await manager.send_personal_message({"turn": True}, users_connected_to_socket.get(game.players_order[0].name))
                        
                        players_id = [player.name for player in game.players]
                        await manager.broadcast({"players": players_id})
                        await manager.broadcast({"vira":f"{(game.deck.vira.value + game.deck.vira.suit).lower()}"})
                        for player in game.players_order:
                            await manager.send_personal_message({"hand": player.json_hand()}, users_connected_to_socket[player.name])
                        
                        new_set = False
                    
                    #recibe la info de la carta jugada de cada jugador
                    if users_connected_to_socket.get(game.players_order[0].name) == websocket and card:
                        for player in  game.players_order:
                            #si eres el primero de players order te toca jugar
                            if player.name == game.players_order[0].name:
                                card_played = player.play_card(card)
                                game.cards_played.append(card_played)
                                await manager.broadcast({"player": player.name,"card_played" : card_played.value + card_played.suit})
                                #ya jugaste asi que le mando al cliente que ya no es tu turno
                                await manager.send_personal_message({"turn": False}, users_connected_to_socket.get(game.players_order[0].name))
                        card = None
                        #manera de rotar la lista
                        game.players_order.append(game.players_order.pop(0))
                        #una vez rotada la lista mandamos de nuevo el turno ok
                        await manager.send_personal_message({"turn": True}, users_connected_to_socket.get(game.players_order[0].name))

                    if len(game.players) == len(game.cards_played):
                        highest_card = game.determine_highest_card(game.cards_played)
                        game.play_rounds(highest_card)
                    # El jugador que jugó la carta más alta gana la ronda
                        print(f"\nEl jugador 1 jugó: {game.cards_played[0].value} de {game.cards_played[0].suit}\n"
                        f"El jugador 2 jugó: {game.cards_played[1].value} de {game.cards_played[1].suit}\n" )
                        print(f"La vira es el {game.deck.vira.value} de {game.deck.vira.suit}")
                        print(f"\n{game.winning_player.name} gana la mano con {highest_card.value} de {highest_card.suit}\n")
                        game.cards_played = []

                        game.set_next_player()
                       
                       #el que gana la mano le mandamos un mensajito cambiando el turno a true
                        await manager.broadcast({"turn": False})
                        await manager.send_personal_message({"turn": True}, users_connected_to_socket.get(game.players_order[0].name))
                                      
                    if game.team1.has_won_round(game.points_to_win_round):
                        game.team1.increment_sets_won()
                        print("El equipo 1 uno ganó la ronda y dos piedritas")
                        
                    if game.team2.has_won_round(game.points_to_win_round):
                        game.team2.increment_sets_won()
                        print("El equipo 2 dos ganó la ronda y dos piedritas")

                    if game.team1.has_won_set(game.points_to_win_set):
                        game.team1.increment_games_won()
                        
                    if game.team2.has_won_set(game.points_to_win_set):
                        game.team2.increment_games_won()

                if (game.team1.has_won_round(game.points_to_win_round) or game.team2.has_won_round(game.points_to_win_round)):
                    print(f"El equipo 1 tiene {game.team1.games_won} chicos.\nY el equipo 2 tiene {game.team2.games_won} chicos.\n")
                    new_set = True
                    game.reset_rounds()
                    game.prepare_deck_and_deal()
                    #esta parte del código es un poco lio, y no me acalro ni yo, establezco el indice del jugador que comienza en +1 y luego igualo eso a next player to play, y por ultimo lo establezco con la funcion que rota la lista de orden de jguadores
                    #mucho lio, pero funciona
                    game.start_player_index = (game.start_player_index + 1) % len(game.players)
                    game.next_player_to_play = game.start_player_index
                    game.set_next_player()
                    #enviamos los resultados
                    await manager.broadcast({"chicos": {"team1": game.team1.games_won, "team2":game.team2.games_won} , "piedras": {"team1":game.team1.sets_won, "team2":game.team2.sets_won}})
                    #revisamos que vuelva a jugar el jugador qsiguiento.
                    await manager.broadcast({"turn": False})
                    await asyncio.sleep(3) 
                    await manager.broadcast({"next_round": True})
                    await manager.send_personal_message({"turn": True}, users_connected_to_socket.get(game.players_order[0].name))

                    if (game.team1.has_won_set(game.points_to_win_set) or game.team2.has_won_set(game.points_to_win_set)):
                        print("alguno ganó los sets ya")
                        game.reset_sets()
                        await manager.broadcast({"chicos": {"team1": game.team1.games_won, "team2":game.team2.games_won} , "piedras": {"team1":game.team1.sets_won, "team2":game.team2.sets_won}})


                    if game.team1.has_won_game(game.points_to_win_game):
                        print("El equipo 1 gana la partida.")
                        game.reset_game()
                        
                    if game.team2.has_won_game(game.points_to_win_game):
                        print("El equipo 2 gana la partida.")
                        game.reset_game()
   
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        disconnected_user_id = None
        for user_id, ws in users_connected_to_socket.items():
            if ws == websocket:
                disconnected_user_id = user_id
                break
        if disconnected_user_id:
            del users_connected_to_socket[disconnected_user_id]

        #if len(users_connected_to_socket) < 0:
         #   await manager.broadcast({f"Client #{disconnected_user_id} left the chat": "adiós"})
        new_set= True

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)