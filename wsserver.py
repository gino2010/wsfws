import threading
import time
import redis

import requests

from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


__author__ = 'gino'

RC = redis.StrictRedis(host='localhost', port=6379, db=0)
RunFlag = True


class GetData(threading.Thread):
    def __init__(self):
        super(GetData, self).__init__()

    def run(self):
        while RunFlag:
            time.sleep(0.5)
            try:
                reqdata = requests.get('http://yourorientedserver', timeout=1)
                RC.setex("data", 1, reqdata.text.encode("UTF-8"))
            except Exception as e:
                print(e.message)


class SendData(threading.Thread):
    def __init__(self, bs):
        super(SendData, self).__init__()
        self.bs = bs

    def run(self):
        while RunFlag:
            try:
                self.bs.sendMessage(RC.get("data"))
            except Exception as e:
                break


class SimpleForward(WebSocket):
    def handleMessage(self):
        SendData(self).start()


if __name__ == '__main__':
    GetData().start()
    server = SimpleWebSocketServer('', 5566, SimpleForward)
    try:
        server.serveforever()
    except KeyboardInterrupt:
        RunFlag = False
