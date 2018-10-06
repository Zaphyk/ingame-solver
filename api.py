import requests
import json

class TriviaHandler():

    def __init__(self):
        with open('settings.json', 'r') as fp:
            self.config = json.loads(fp.read())
        self.host = 'http://api.ingame.dift.co'
        self.headers = {
            'authorization': self.config['token'],
            'accept': '*/*',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'okhttp/3.10.0'
        }

    def request(self, payload: dict):
        return requests.post(f"{self.host}/main", data=json.dumps(payload), headers=self.headers)   

    def status(self):
        payload = {
            'operationName': None,
            'variables': {},
            'query': """
            {
              nextGame {
                ...GameInfo
                __typename
              }
            }

            fragment GameInfo on Game {
              id
              start
              prize
              state
              host {
                name
                avatar
                __typename
              }
              __typename
            }
            """
        }
        return self.request(payload)

    def game_status(self, game_id: str):
        payload = {
            'operationName': 'game',
            'variables': {
                'gameId': game_id
            },
            'query': """
            query game($gameId: ID!) {
                game(gameId: $gameId) {
                    id
                    state
                    __typename
                }
            }
            """
        }
        return self.request(payload)

handler = TriviaHandler()
r = handler.game_status('5bb637797378a9573e88d964')
print(r.status_code, r.reason)
print(r.json())
