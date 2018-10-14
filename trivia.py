from termcolor import colored
from timeit import default_timer as timer
import spacy
import json
import os
from googleapiclient.discovery import build

class Searcher():

    def __init__(self):
        self.config = self.load_config()
        self.api_key = self.config['google_api_key']
        self.cse_id = self.config['google_cse_id']

    def load_config(self):
        with open(os.path.dirname(os.path.abspath(__file__)) + '/settings.json', 'r') as fp:
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
            probabilities[options[i]] = self.rank(data, keywords, options[i]) if 'items' in data else 0
            print(f"Option '{options[i]}' was ranked with {probabilities[options[i]]} points.")
        return probabilities


    def rank(self, data: dict, keywords: list, option: str) -> int:
        rank = 0
        for item in data['items']:
            snippet = item['snippet'].lower()
            title = item['title'].lower()

            rank += snippet.count(option.lower())
            rank += title.count(option.lower())
        return rank

    def analyze(self, probabilities: dict, options: list) -> list:
        highest = -1
        highest_name = None
        sum_probabilities = 0
        for name, probability in probabilities.items():
            sum_probabilities += probability
            if probability > highest:
                highest = probability
                highest_name = name
        return [options.index(highest_name), int(highest / sum_probabilities * 100)]

    def guess(self, question: str, options: list) -> list:
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

    assert_guess(
        u'\u00bfQu\u00e9 significa la sigla R.I.P. en espa\u00f1ol?',
        [u"Reanimaci\u00f3n cardiovascular", "Descanse en paz", "Auxilio"],
        1
    )

    assert_guess(
        u'\u00bfCu\u00e1l de estos equipos no se encuentra en la semifinal de la Copa Libertadores 2018?',
        ["Gremio", "Cruzeiro", "Palmeiras"],
        1
    )

    assert_guess(
        u'\u00bfQu\u00e9 artista participa en el nuevo video de Bad Bunny lanzado ayer?',
        ["Nicky Jam", "J. Balvin", "Drake"],
        2
    )

    assert_guess(
        u'\u00bfQui\u00e9n escribi\u00f3 \"El T\u00fanel\"?',
        [u"Ernesto S\u00e1bato", "Jorge Luis Borges", u"Julio Cort\u00e1zar"],
        0
    )

    assert_guess(
        u'\u00bfC\u00f3mo se llama el perro que recrea fotos de Madonna?',
        ["Chrisdonna", "Maxdonna", "Mikedonna"],
        1
    )

    assert_guess(
        u'\u00bfQu\u00e9 contienen las semillas de la manzana?',
        ["Cianuro", u"Almid\u00f3n", u"Prote\u00ednas"],
        0
    )

    assert_guess(
        u'\u00bfCu\u00e1l de estos no es uno de los 7 enanitos de Blanca Nieves?',
        ["Mocoso", u"Bonach\u00f3n", u"Cantar\u00edn"],
        2
    )

    assert_guess(
        u'\u00bfQu\u00e9 pa\u00eds tiene m\u00e1s pir\u00e1mides?',
        [u"M\u00e9xico", "China", u"Sud\u00e1n"],
        2
    )

    assert_guess(
        u'\u00bfCu\u00e1l de estos dinosaurios fue el m\u00e1s grande?',
        ["Paralititan", "T-Rex", "Diplodocus"],
        2
    )

    assert_guess(
        u'\u00bfQui\u00e9n fue el sucesor de George H. W. Bush?',
        ["Barack Obama", "Jimmy Carter", "Bill Clinton"],
        2
    )

    assert_guess(
        u'\u00bfHace cu\u00e1ntos a\u00f1os est\u00e1 el cuerpo de Lenin en el Kremlin?',
        [u"51 a\u00f1os", u"94 a\u00f1os", u"No est\u00e1 en el Kremlin"],
        1
    )

    print('-------------------------------------------------------------------')
    print(f" Trivia guesser had an accuracy of '{(accuracy / total) * 100.0}%'")

if __name__ == '__main__':
    test()