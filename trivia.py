
class Guesser():

    def __init__(self):
        pass

    def guess(question: str, options: list) -> int:
        pass


if __name__ == '__main__':
    trivia = Guesser()
    def assert_guess(question: str, options: list, answer: int):
        assert(trivia.guess(question, options))

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