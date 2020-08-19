import socket
from _thread import *
import json
import pickle
from Game import Game

server = "192.168.178.138"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print("Waiting for a connection, Server Started")

idCount = 0
game = None


def threaded_client(conn, p):
    global idCount
    conn.send(str.encode(str(p)))
    print("Sent the player number:", str(p))

    while True:
        data = conn.recv(192).decode()
        obj = json.loads(data)
        print("[RECEIVED] Received player position.", obj)
        if not data:
            print("data is None")
            break
        else:
            game.get_Player_pos(obj)   # p is included in the object itself being sent from client#
            print("[UPDATE DATA] Update game.")
            pass

        conn.sendall(pickle.dumps(game))
        print("[SENT] Sent Object back to Client.")

        if game.is_Over():
            break

    print("Connection lost")
    conn.close()
    idCount = 0


while idCount <= 2:  # accept only 2 connections
    # conn is an object, addr the IP adress
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    p = 0
    game = Game()
    if idCount == 2:
        p = 1
        game.ready = True

    start_new_thread(threaded_client, (conn, p))
