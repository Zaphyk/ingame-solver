import os
import json

def load() -> dict:
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/settings.json", 'r') as fp:
        return json.load(fp)