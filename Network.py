import socket
import pickle
import json


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.178.138"
        self.port = 5555
        self.adress = (self.server, self.port)
        self.id = self.connect()

    def get_player_id(self):
        return self.id

    def connect(self):
        try:
            self.client.connect(self.adress)
            return self.client.recv(192).decode()  # p = 0 or 1 stored in self.id, see __init__()
        except:
            pass

    def send_player_pos_return_game_obj(self, dict_data):
        dict_data_dumped = json.dumps(dict_data)
        self.client.sendall(dict_data_dumped.encode())
        print("[SENT] Sent player position to server.")
        return pickle.loads(self.client.recv(192))