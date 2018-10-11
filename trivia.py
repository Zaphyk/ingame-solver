from termcolor import colored
from timeit import default_timer as timer
import spacy
import json
from googleapiclient.discovery import build

class Searcher():

    def __init__(self):
        self.config = self.load_config()
        self.api_key = self.config['google_api_key']
        self.cse_id = self.config['google_cse_id']

    def load_config(self):
        with open(os.path.dirname(__file__) + '/settings.json', 'r') as fp:
            return json.load(fp)

    def google_search(self, search_term, **kwargs):
        service = build("customsearch", "v1", developerKey=self.api_key)
        res = service.cse().list(q=search_term, cx=self.cse_id, **kwargs).execute()
        return res

    def search(self, query: str) -> dict:
        return self.google_search(query, num=10)


class Guesser():

    def __init__(self):
        self.solver = Searcher()

    def get_keywords(self, question: str) -> list:
        keywords = []
        nlp = spacy.load('es_core_news_sm')
        doc = nlp(question)

        for token in doc:
            if token.is_alpha and token.pos_ is not 'AUX' and token.pos_ is not 'ADP':
                keywords.append(token.text.lower())
        return keywords

    def get_search_queries(self, keywords: list, options: list) -> list:
        base = ' '.join(keywords)
        return [f"{base} {o}" for o in options]

    def search_and_rank_queries(self, queries: list, keywords: list, options: list) -> dict:
        probabilities = {}
        for i in range(0, len(queries)):
            print(f"Running query '{queries[i]}'")
            data = self.solver.search(queries[i])
            probabilities[options[i]] = self.rank(data, keywords, options[i])
            print(f"Option '{options[i]}' was ranked with {probabilities[options[i]]} points.")
        return probabilities


    def rank(self, data: dict, keywords: list, option: str) -> int:
        rank = 0
        for item in data['items']:
            snippet = item['snippet'].lower()
            title = item['title'].lower()

            for keyword in keywords:
                rank += snippet.count(keyword)
                rank += title.count(keyword)
            rank += snippet.count(option.lower())
            rank += title.count(option.lower())
        return rank

    def analyze(self, probabilities: dict, options: list):
        highest = -1
        highest_name = None
        for name, probability in probabilities.items():
            if probability > highest:
                highest = probability
                highest_name = name
        return options.index(highest_name)

    def guess(self, question: str, options: list) -> int:
        keywords = self.get_keywords(question)
        queries = self.get_search_queries(keywords, options)
        probabilities = self.search_and_rank_queries(queries, keywords, options)
        return self.analyze(probabilities, options)

def test():
    accuracy = 0
    total = 0
    def assert_guess(question: str, options: list, answer: int):
        trivia = Guesser()
        nonlocal total
        nonlocal accuracy
        start = timer()
        best_guess = trivia.guess(question, options)
        end = timer()
        correct = best_guess is answer
        if correct:
            accuracy += 1
        print('-------------------------------------------------------------------')
        print(
            colored(
                f"\n{question}. \n* Your answer is '{options[best_guess]}' \n* Correct answer is '{options[answer]}'\n",
                'green' if correct else 'red'
            )
        )
        print(f"Answering this question took {end - start} seconds")
        total += 1

    assert_guess(
        '¿Cuál de estos deportistas argentinos fue dos veces abanderado Olímpico?',
        ["Luciana Aymar", "Carlos Espínola", "Juan Curuchet"],
        1
    )

    assert_guess(
        '¿Qué libro fue prohibido durante la dictadura militar argentina?',
        ["La Metamorfosis","El Principito","Moby Dick"],
        1
    )

    assert_guess(
        '¿Dónde se encuentra el mejor restaurante de Latinoamérica según "Chefs\' Choice Award"?',
        ["Buenos Aires, Argentina","Bogotá, Colombia","Lima, Perú"],
        2
    )

    print('-------------------------------------------------------------------')
    print(f" Trivia guesser had an accuracy of '{(accuracy / total) * 100.0}%'")

if __name__ == '__main__':
    test()