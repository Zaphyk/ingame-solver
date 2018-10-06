import websocket
import requests
import json
import sys
import trivia
import threading

class Client():

    def __init__(self):
        self.debug = True
        self.endpoint = 'ws://socket.ingame.dift.co/main'
        self.headers = [
            'accept: */*',
            'Accept-Encoding: gzip',
            'Content-Type: application/json; charset=utf-8',
            'User-Agent: okhttp/3.10.0',
            'Sec-WebSocket-Protocol: graphql-ws',
            'origin: http://socket.ingame.dift.co/',
        ]
        self.trivia = trivia.Guesser()
        self.ws = None
        self.is_running = False
        self.question_id = None
        self.quiz = None
        self.options = None

    def run(self):
        self.open()
        self.susbscribe()
        self.listen()

    def open(self):
        self.ws = websocket.WebSocket()
        if self.debug:
            self.ws.connect(self.endpoint, http_proxy_host="192.168.0.14", http_proxy_port=8888, header=self.headers)
        else:
            self.ws.connect(self.endpoint, header=self.headers)
        self.send('{"type":"connection_init","payload":{}}')
        self.is_running = True

    def listen(self):
        while self.is_running:
            self.on_msg(json.loads(self.ws.recv()))

    def send(self, msg):
        print(f" ---> {msg}")
        self.ws.send(msg)

    def susbscribe(self):
        self.send(r'{"id":"7","type":"start","payload":{"variables":{},"extensions":{},"operationName":"onQuestionStart","query":"subscription onQuestionStart {\n  questionStarted {\n    ...questionStarted\n    __typename\n  }\n}\n\nfragment questionStarted on QuestionStarted {\n  id\n  quiz\n  options\n  index\n  bgColor\n  footer {\n    logoUrl\n    alignment\n    __typename\n  }\n  __typename\n}\n","authorization":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjViOTE1ZDQzODU2YjdhNTUwZDAzZTU4MCIsInNjb3BlIjpbIlVTRVIiXSwiaWF0IjoxNTM2NjgzNDE2fQ.IOUFqVxFVW5nq5XJme0_y1Yqw4OeP0UDiQff0Hj5lY0"}}')
        self.send(r'{"id":"8","type":"start","payload":{"variables":{},"extensions":{},"operationName":"onQuestionFinish","query":"subscription onQuestionFinish {\n  questionFinished {\n    ...questionFinished\n    __typename\n  }\n}\n\nfragment questionFinished on QuestionFinished {\n  id\n  quiz\n  answer\n  options\n  stats\n  index\n  extraLifeAllowed\n  bgColor\n  footer {\n    logoUrl\n    alignment\n    __typename\n  }\n  __typename\n}\n","authorization":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjViOTE1ZDQzODU2YjdhNTUwZDAzZTU4MCIsInNjb3BlIjpbIlVTRVIiXSwiaWF0IjoxNTM2NjgzNDE2fQ.IOUFqVxFVW5nq5XJme0_y1Yqw4OeP0UDiQff0Hj5lY0"}}')
        self.send(r'{"id":"5","type":"start","payload":{"variables":{},"extensions":{},"operationName":"onGameStateUpdated","query":"subscription onGameStateUpdated {\n  gameStateUpdated {\n    id\n    state\n    __typename\n  }\n}\n","authorization":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjViOTE1ZDQzODU2YjdhNTUwZDAzZTU4MCIsInNjb3BlIjpbIlVTRVIiXSwiaWF0IjoxNTM2NjgzNDE2fQ.IOUFqVxFVW5nq5XJme0_y1Yqw4OeP0UDiQff0Hj5lY0"}}')

    def join_game(self):
        pass

    def answer_question(self):
        pass

    def on_msg(self, data):
        if 'id' in data and data['id'] is 7:
            print('-----QUESTION RECEIVED----')
            content = json.loads(data['payload'])
            options = content['options']
            quiz = content['quiz']
            id = content['id']
            self.process_question(id, quiz, options)
            print(f"question id: {id}")
            print(f"quiz: {quiz}")
            print(f"options: {options}")
        else:
            print(json.dumps(data))
        sys.stdout.flush()

    def process_question(self, question_id, quiz, options):
        self.question_id = question_id
        self.quiz = quiz
        self.options = options
        def guess():
            self.guess_callback(self.trivia.guess(quiz, options))
        thread = Thread(guess)
        thread.start()

    def guess_callback(self, answer_index):
        answer = self.options[answer_index]
        print(f"best guess is: '{answer}' ")

client = Client()
client.run()