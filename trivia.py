from termcolor import colored
from timeit import default_timer as timer
import spacy
import json
import config
from random import shuffle
import os
from googleapiclient.discovery import build

class Searcher():

    def __init__(self):
        self.config = config.load()
        self.api_key = self.config['google_api_key']
        self.cse_id = self.config['google_cse_id']

    def google_search(self, search_term, **kwargs):
        service = build("customsearch", "v1", developerKey=self.api_key)
        res = service.cse().list(q=search_term, cx=self.cse_id, **kwargs).execute()
        return res

    def search(self, query: str) -> dict:
        return self.google_search(query, num=10)


class Guesser():

    def __init__(self):
        self.solver = Searcher()
        self.config = config.load()
        self.nlp = spacy.load('es_core_news_sm')
        self.verbose = self.config['verbose']

    def log(self, msg: str):
        if self.verbose:
            print(msg)

    def get_keywords(self, question: str) -> list:
        start = timer()
        keywords = []
        doc = self.nlp(question)

        for token in doc:
            if token.is_alpha and token.pos_ is not 'AUX' and token.pos_ is not 'ADP':
                keywords.append(token.text.lower())
        end = timer()
        self.log(f"NLP took '{end - start}' seconds.")
        return keywords

    def get_search_queries(self, keywords: list, options: list) -> list:
        base = ' '.join(keywords)
        return [f"{base} {o}" for o in options]

    def search_and_rank_queries(self, queries: list, keywords: list, options: list) -> dict:
        probabilities = {}
        for i in range(0, len(queries)):
            self.log(f"Running query '{queries[i]}'")
            data = self.solver.search(queries[i])
            probabilities[options[i]] = self.rank(data, keywords, options[i]) if 'items' in data else 0
            self.log(f"Option '{options[i]}' was ranked with {probabilities[options[i]]} points.")
        return probabilities


    def rank(self, data: dict, keywords: list, option: str) -> int:
        rank = 0
        for item in data['items']:
            snippet = item['snippet'].lower()
            title = item['title'].lower()

            rank += snippet.count(option.lower())
            rank += title.count(option.lower())
        return rank

    def analyze(self, keywords: list, probabilities: dict, options: list) -> list:
        highest = -sys.maxint
        highest_name = None
        lowest = sys.maxint
        lowest_name = None
        sum_probabilities = 0
        for name, probability in probabilities.items():
            sum_probabilities += probability

            if probability > highest:
                highest = probability
                highest_name = name

            if probability < lowest:
                lowest = probability
                lowest_name = name

        if 'no' in keywords:
            return [options.index(lowest_name), int(100 - low / sum_probabilities * 100)]
        else:
            return [options.index(highest_name), int(highest / sum_probabilities * 100)]

    def guess(self, question: str, options: list) -> list:
        keywords = self.get_keywords(question)
        queries = self.get_search_queries(keywords, options)
        probabilities = self.search_and_rank_queries(queries, keywords, options)
        return self.analyze(keywords, probabilities, options)

def test():
    accuracy = 0
    total = 0
    total_time = 0
    trivia = Guesser()
    verbose = config.load()['verbose']
    def assert_guess(question: str, options: list, answer: int):
        nonlocal total
        nonlocal accuracy
        nonlocal total_time
        start = timer()
        best_guess, confidence = trivia.guess(question, options)
        end = timer()
        correct = best_guess is answer
        if correct:
            accuracy += 1
        if verbose:
            print('-------------------------------------------------------------------')
            print(
                colored(
                    f"\n{question}. \n* Your answer is '{options[best_guess]}' \n* Correct answer is '{options[answer]}'\n",
                    'green' if correct else 'red'
                )
            )
            print(f"Answering this question took {end - start} seconds")
        total_time = end - start
        total += 1

    with open(os.path.dirname(os.path.abspath(__file__)) + '/trivia.json', 'r') as fp:
        test_data = json.load(fp)['items']
        shuffle(test_data)
        cases = test_data[0:8]
        for item in cases:
            assert_guess(
                item['quiz'],
                item['options'],
                item['answer']
            )
    print('-------------------------------------------------------------------')
    print(f"Average question took '{(total_time / total)}' seconds")
    print(f" Trivia guesser had an accuracy of '{(accuracy / total) * 100.0}%'")

if __name__ == '__main__':
    test()