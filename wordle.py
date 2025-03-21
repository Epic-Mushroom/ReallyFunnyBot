from pathlib import Path
import random

NUM_POSSIBLE_WORDS = 2315
WORD_LENGTH = 5
MAX_CHANCES = 6
ALPHABET = "qwertyuiopasdfghjklzxcvbnm"

class InvalidGuessError(Exception):
    pass

class GameEndError(Exception):
    pass

class WordStatus:
    """
    Represents the status of a guess with respect to the correct word
    """
    GRAY = 0
    YELLOW = 1
    GREEN = 2

    def __init__(self, guess: str, correct_word: str):
        self.guess = guess.lower().strip()
        self.correct_word = correct_word.lower()

        if len(self.guess) != WORD_LENGTH or len(self.correct_word) != WORD_LENGTH:
            raise ValueError

        self.status = []
        for i in range(WORD_LENGTH):
            if self.guess[i] == self.correct_word[i]:
                self.status.append(WordStatus.GREEN)

            elif self.guess[i] in self.correct_word:
                self.status.append(WordStatus.YELLOW)

            else:
                self.status.append(WordStatus.GRAY)

    def is_correct(self):
        return all(status == WordStatus.GREEN for status in self.status)

    def __str__(self):
        output = ""

        for status in self.status:
            output += ("🟩" if status == WordStatus.GREEN else "🟨" if status == WordStatus.YELLOW
            else "⬛")

        return output

class WordleGame:
    UNFINISHED = 0
    LOSS = 1
    WIN = 2

    def __init__(self, username, correct_word = None):
        self.username = username
        self.correct_word = WordleGame.get_random_word() if correct_word is None else correct_word
        self.guesses = []
        self.game_state = WordleGame.UNFINISHED

    def register_guess(self, guess: str):
        guess = guess.lower().strip()

        if len(guess) != WORD_LENGTH or not WordleGame.validate_word(guess):
            raise InvalidGuessError

        elif self.correct_word in self.guesses or len(self.guesses) >= MAX_CHANCES:
            raise GameEndError

        for char in guess:
            if not char in ALPHABET:
                raise InvalidGuessError

        self.guesses.append(guess)

        self.update_game_state()

    def update_game_state(self):
        self.game_state = WordleGame.UNFINISHED

        if len(self.guesses) >= 1:
            word_status = WordStatus(self.guesses[-1], self.correct_word)

            if word_status.is_correct():
                self.game_state = WordleGame.WIN

            elif len(self.guesses) >= MAX_CHANCES:
                self.game_state = WordleGame.LOSS

    @staticmethod
    def get_random_word():
        with Path("word-bank.csv").open() as word_bank:
            for i in range(random.randrange(0, NUM_POSSIBLE_WORDS)):
                word_bank.readline()

            return word_bank.readline().rstrip()

    @staticmethod
    def validate_word(word) -> bool:
        word = word.lower().strip()

        with Path("word-bank.csv").open() as word_bank:
            for i in range(NUM_POSSIBLE_WORDS):
                valid_word = word_bank.readline().strip()

                if valid_word == word:
                    return True

            return False

if __name__ == '__main__':
    word_status = WordStatus('birds', 'brick')
    assert word_status.status[0] == WordStatus.GREEN
    assert word_status.status[1] == WordStatus.YELLOW
    assert word_status.status[2] == WordStatus.YELLOW
    assert word_status.status[3] == WordStatus.GRAY
    assert word_status.status[4] == WordStatus.GRAY
    assert not word_status.is_correct()

    word_status = WordStatus('blaze', 'blaze')
    assert word_status.is_correct()

    assert WordleGame.validate_word('blaze')
    assert WordleGame.validate_word('zonal')
    assert not WordleGame.validate_word('asdfe')

    game = WordleGame("epicmushroom.", "grind")

    while game.game_state == WordleGame.UNFINISHED:
        guess = input()
        game.register_guess(guess)
