from flask import Blueprint
from flask import request
import random
from replit import db
from replit.database.database import ObservedList
from replit.database.database import ObservedDict
from flask_sock import Sock
from simple_websocket.ws import ConnectionClosed
import string
from time import sleep
from random import randint
from threading import Thread
import json

app = Blueprint('wsApi', __name__, template_folder='templates')
sock = Sock(app)


class Player:

    def __init__(self, client, idet):
        self.id = ""
        self.client = client
        self.idet = idet

    def handle(self, data):
        global updaters
        dat = json.loads(data)
        print(dat)
        if dat["type"] == "setPoll":
            if dat["pollId"] not in updaters.keys():
                updaters[dat["pollId"]] = []
            updaters[dat["pollId"]].append(self)
            self.id = dat["pollId"]
            pass
        elif dat["type"] == "cancelPoll":
            if self.id in updaters.keys():
                updaters[self.id].remove(self)
            self.id = ""

    def send_message(self, dat):
        try:
            if self.idet in self.client.clients:
                if self.client.clients[self.idet].connected:
                    self.client.clients[self.idet].send(dat)
            else:
                self.client.close_connection(self.idet)
        except ConnectionClosed:
            self.client.close_connection(self.idet)

    def update(self, id, dat):
        if id == self.id:
            self.send_message(json.dumps(dat))
            print("update with data: " + str(dat))

    def handle_close(self):
        if self.id in updaters.keys():
            updaters[self.id].remove(self)


updaters = {}


def update(id, dat):
    global updaters
    for x in updaters[id]:
        x.update(id, dat)
    pass


class Client():

    def __init__(self):
        self.clients = {}
        self.rec = {}

    def add_client(self, ws):
        idet = randint(0, 100000)
        self.clients[idet] = ws
        self.rec[idet] = Player(self, idet)
        #Timer(10, self.close_connection, (ws,)).start()
        Thread(target=self.check_disconnect, args=(idet, )).start()
        return idet

    def run(self, idet):
        data = self.clients[idet].receive()
        self.rec[idet].handle(data)

    def active_client(self, idet):
        if idet in self.clients.keys():
            return True
        #print("not active_client")
        return False

    def check_disconnect(self, idet):
        try:
            while self.clients[idet].connected:
                #print("Is connected")
                sleep(0.05)
            self.close_connection(idet)
        except Exception as e:
            print("check disconnected errored")
            print(e)
            pass

    def close_connection(self, idet):
        if idet in self.rec.keys():
            self.rec[idet].handle_close()
            self.rec.pop(idet)
        if idet in self.clients.keys():
            self.clients.pop(idet)


client = Client()


@sock.route('/api/ws/updateListener')
def updateListener(ws):
    idet = client.add_client(ws)
    while client.active_client(idet):
        client.run(idet)
    ws.close(1006, "Invalid Message")
    return
    print("Client disconnected because of an error")
