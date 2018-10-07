from termcolor import colored

class Guesser():

    def __init__(self):
        pass

    def guess(self, question: str, options: list) -> int:
        return 2


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
        ["Luciana Aymar","Carlos Espínola","Juan Curuchet"],
        1
    )

    assert_guess(
        '¿Qué libro fue prohibido durante la dictadura militar argentina?',
        ["La Metamorfosis","El Principito","Moby Dick"],
        1
    )

    assert_guess(
        '¿Dónde se encuentra el mejor restaurante de Latinoamérica según "Chefs\' Choice Award"?',
        ["Lima, Perú","Bogotá, Colombia","Buenos Aires, Argentina"],
        1
    )
    print('-------------------------------------------------------------------')
    print(f" Trivia guesser had an accuracy of '{(accuracy / total) * 100.0}%'")

if __name__ == '__main__':
    test()