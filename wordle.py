from pathlib import Path
import random

NUM_POSSIBLE_WORDS = 2315
NUM_VALID_WORDS = 12972
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

        return output + f" ({self.guess.upper()})"

class WordleGame:
    UNFINISHED = 0
    LOSS = 1
    WIN = 2

    WIN_MESSAGES = ["Cheater...", "Damn, okay.", "Well played.", "Good job.", "👍", "Not close at all..."]

    def __init__(self, username, correct_word = None):
        self.username = username
        self.correct_word = WordleGame.get_random_word() if correct_word is None else correct_word
        self.guesses = []
        self.game_state = WordleGame.UNFINISHED

        self.green_letters = []
        self.yellow_letters = []
        self.gray_letters = []
        self.unused_letters: list[str] = [char.upper() for char in ALPHABET].sort()

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
        self.update_letter_colors()

    def update_game_state(self):
        self.game_state = WordleGame.UNFINISHED

        if len(self.guesses) >= 1:
            word_status = WordStatus(self.guesses[-1], self.correct_word)

            if word_status.is_correct():
                self.game_state = WordleGame.WIN

            elif len(self.guesses) >= MAX_CHANCES:
                self.game_state = WordleGame.LOSS

    def update_letter_colors(self):
        if len(self.guesses) >= 1:
            word_status = WordStatus(self.guesses[-1], self.correct_word)

            for i in range(WORD_LENGTH):
                if word_status.status[i] == WordStatus.GREEN:
                    self.green_letters.append(self.guesses[-1][i].upper())

                elif word_status.status[i] == WordStatus.YELLOW:
                    self.yellow_letters.append(self.guesses[-1][i].upper())

                else:
                    self.gray_letters.append(self.guesses[-1][i].upper())

                if self.guesses[-1][i].upper() in self.unused_letters:
                    self.unused_letters.pop(self.unused_letters.index(self.guesses[-1][i].upper()))

    def __str__(self):
        output = f"Username: {self.username}\nGuesses: {len(self.guesses)}/{MAX_CHANCES}\n\n"

        if self.game_state == WordleGame.LOSS:
            output += f"❌ **You lost!**\nThe word was: **{self.correct_word.upper()}**\n"

        elif self.game_state == WordleGame.WIN:
            output += f"✅ {WordleGame.WIN_MESSAGES[len(self.guesses) - 1]}\n\n"

        for i in range(len(self.guesses)):
            output += f"{WordStatus(self.guesses[i], self.correct_word)}\n"

        for i in range(len(self.guesses), MAX_CHANCES):
            output += "🔳🔳🔳🔳🔳\n"

        output += "\n"
        if len(self.green_letters) > 0:
            output += "🟩: " + ", ".join(self.green_letters) + "\n"
        if len(self.yellow_letters) > 0:
            output += "🟨: " + ", ".join(self.yellow_letters) + "\n"
        if len(self.gray_letters) > 0:
            output += "⬛: " + ", ".join(self.gray_letters) + "\n"
        if len(self.unused_letters) > 0:
            output += "🔳: " + ", ".join(self.unused_letters) + "\n"

        return output

    @staticmethod
    def get_random_word():
        with Path("word-bank.csv").open() as word_bank:
            for i in range(random.randrange(0, NUM_POSSIBLE_WORDS)):
                word_bank.readline()

            return word_bank.readline().rstrip()

    @staticmethod
    def validate_word(word) -> bool:
        word = word.lower().strip()

        with Path("valid-words.csv").open() as word_bank:
            for i in range(NUM_VALID_WORDS):
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
    assert WordleGame.validate_word('zymic')
    assert not WordleGame.validate_word('asdfe')

    game = WordleGame("epicmushroom.", "grind")
    print(game)

    while game.game_state == WordleGame.UNFINISHED:
        guess = input()
        game.register_guess(guess)

        print(game)
