import websocket
import requests
import json
import config
import sys
import trivia
from threading import Thread
import os

class Client():

    def __init__(self):
        self.endpoint = 'ws://socket.ingame.dift.co/main'
        self.headers = [
            'accept: */*',
            'Accept-Encoding: gzip',
            'Content-Type: application/json; charset=utf-8',
            'User-Agent: okhttp/3.10.0',
            'Sec-WebSocket-Protocol: graphql-ws',
            'origin: http://socket.ingame.dift.co/',
        ]
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.config = config.load()
        self.token = self.config['ingame_token']
        self.debug = self.config['debug_proxy']
        self.trivia = trivia.Guesser()
        self.ws = None
        self.is_running = False
        self.quiz = None
        self.options = None

    def run(self):
        self.open()
        self.susbscribe()
        self.listen()

    def open(self):
        self.ws = websocket.WebSocket()
        if self.debug:
            self.ws.connect(self.endpoint, http_proxy_host=self.config['debug_proxy_ip'], http_proxy_port=self.config['debug_proxy_ports'], header=self.headers)
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
        self.send(r'{"id":"7","type":"start","payload":{"variables":{},"extensions":{},"operationName":"onQuestionStart","query":"subscription onQuestionStart {\n  questionStarted {\n    ...questionStarted\n    __typename\n  }\n}\n\nfragment questionStarted on QuestionStarted {\n  id\n  quiz\n  options\n  index\n  bgColor\n  footer {\n    logoUrl\n    alignment\n    __typename\n  }\n  __typename\n}\n","authorization":"' + self.token + '"}}')
        self.send(r'{"id":"8","type":"start","payload":{"variables":{},"extensions":{},"operationName":"onQuestionFinish","query":"subscription onQuestionFinish {\n  questionFinished {\n    ...questionFinished\n    __typename\n  }\n}\n\nfragment questionFinished on QuestionFinished {\n  id\n  quiz\n  answer\n  options\n  stats\n  index\n  extraLifeAllowed\n  bgColor\n  footer {\n    logoUrl\n    alignment\n    __typename\n  }\n  __typename\n}\n","authorization":"' + self.token + '"}}')
        self.send(r'{"id":"5","type":"start","payload":{"variables":{},"extensions":{},"operationName":"onGameStateUpdated","query":"subscription onGameStateUpdated {\n  gameStateUpdated {\n    id\n    state\n    __typename\n  }\n}\n","authorization":"' + self.token + '"}}')

    def on_msg(self, data):
        if 'id' in data:
            if data['id'] is '7':
                print('-----QUESTION RECEIVED----')
                options = data['payload']['data']['questionStarted']['options']
                quiz = data['payload']['data']['questionStarted']['quiz']
                self.process_question(quiz, options)
                print(f"quiz: {quiz}")
                print(f"options: {options}")

            elif data['id'] is '8':
                print('-----ANSWER RECEIVED----')
                self.log_question(data['payload']['data']['questionFinished'])

            elif data['id'] is '5' and data['payload']['data']['gameStateUpdated']['state'] is 'FINISHED':
                print('------GAME ENDED----')
                sys.exit(0)
        else:
            print(json.dumps(data))
        sys.stdout.flush()

    def process_question(self, quiz, options):
        self.quiz = quiz
        self.options = options
        def guess():
            index, confidence = self.trivia.guess(quiz, options)
            self.send_answer(index, confidence)
        thread = Thread(target=guess)
        thread.start()

    def send_answer(self, answer_index, confidence):
        answer = self.options[answer_index]
        payload = {
            "value1": f"Best guess is: '{answer}' with {confidence}% confidence"
        }
        requests.post(self.config['notification_url'], data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    def log_question(self, data):
        answers = {
            'items': []
        }
        log_path = f"{self.current_directory}/trivia.json"
        if os.path.exists(log_path):
            with open(log_path, 'r') as fp:
                answers = json.load(fp)

        answers['items'].append({
            'quiz': data['quiz'],
            'options' : data['options'],
            'answer' : data['answer']
        })

        with open(log_path, 'w+') as fp:
            json.dump(answers, fp)


client = Client()
#client.on_msg(json.loads('{"type": "data", "id": "7", "payload": {"data": {"questionStarted": {"id": "5bc0c3ed2a43c338a9048094", "quiz": "\u00bfQu\u00e9 significa la sigla R.I.P. en espa\u00f1ol?", "options": ["Reanimaci\u00f3n cardiovascular", "Descanse en paz", "Auxilio"], "index": 0, "bgColor": null, "footer": null, "__typename": "QuestionStarted"}}}}'))
#client.send_answer(1)
#client.on_msg(json.loads('{"type": "data", "id": "8", "payload": {"data": {"questionFinished": {"id": "5bc0c3ed2a43c338a9048094", "quiz": "\u00bfQu\u00e9 significa la sigla R.I.P. en espa\u00f1ol?", "answer": 1, "options": ["Reanimaci\u00f3n cardiovascular", "Descanse en paz", "Auxilio"], "stats": [3045, 47523, 332], "index": 0, "extraLifeAllowed": true, "bgColor": null, "footer": null, "__typename": "QuestionFinished"}}}}'))
client.run()