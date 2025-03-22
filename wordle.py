from pathlib import Path
import random, time
from string_utils import seconds_to_descriptive_time

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

        self.status = [None] * WORD_LENGTH
        remaining_slots = [0, 1, 2, 3, 4]
        for i in range(WORD_LENGTH):
            if self.guess[i] == self.correct_word[i]:
                self.status[i] = WordStatus.GREEN
                remaining_slots.remove(i)

        for i in remaining_slots:
            if any(self.guess[i] == self.correct_word[slot] and i != slot for slot in remaining_slots):
                self.status[i] = WordStatus.YELLOW

            else:
                self.status[i] = WordStatus.GRAY

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

    def __init__(self, username, correct_word = None):
        self.username = username
        self.correct_word = WordleGame.get_random_word() if correct_word is None else correct_word
        self.guesses = []
        self.game_state = WordleGame.UNFINISHED

        self.start_time = time.time()

        self.green_letters = []
        self.yellow_letters = []
        self.gray_letters = []
        self.unused_letters: list[str] = sorted([char.upper() for char in ALPHABET])

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
                letter = self.guesses[-1][i].upper()
                if word_status.status[i] == WordStatus.GREEN:
                    if letter not in self.green_letters:
                        self.green_letters.append(letter)

                    if letter in self.yellow_letters:
                        self.yellow_letters.remove(letter)

                elif word_status.status[i] == WordStatus.YELLOW:
                    if letter not in self.yellow_letters and letter not in self.green_letters:
                        self.yellow_letters.append(letter)

                elif word_status.status[i] == WordStatus.GRAY:
                    if letter not in self.gray_letters and letter not in self.yellow_letters and letter not in self.green_letters:
                        self.gray_letters.append(letter)

                if letter in self.unused_letters:
                    self.unused_letters.pop(self.unused_letters.index(letter))

            self.green_letters.sort()
            self.yellow_letters.sort()
            self.gray_letters.sort()

    def get_time_used(self):
        current_time = time.time()
        return round(current_time - self.start_time)

    def calculate_score(self):
        time_used = self.get_time_used()

        if not self.game_state == WordleGame.WIN:
            return 0

        if len(self.guesses) == 1:
            return 200

        elif len(self.guesses) == 2:
            return 100

        elif 3 <= len(self.guesses) <= MAX_CHANCES:
            return max(0, (6 - len(self.guesses)) * 5 + max(-5, round((120 - time_used) / 2)))

    def get_loss_message(self):
        RUSH_MESSAGES = ["Maybe don't rush it next time?", "How about you slow down a little?", "Are you trying to speedrun losing this game?"] # time_used < 20
        NORMAL_MESSAGES = ["Better luck next time.", "Too bad.", "Skill issue."]
        POOR_PERFORMANCE_MESSAGES = ["Have you considered investing in a dictionary?", "Wow, you suck.", "Maybe you should just stick to fishing."] # <= 1 green letter and <= 2 yellow letters found
        RARE_LOSS_MESSAGES = ["This is for you, human. You and only you. You are not special, you are not important, and you are not needed. You are a waste of time and resources. You are a burden on society. You are a drain on the earth. You are a blight on the landscape. You are a stain on the universe. Please die. Please."] # 0.5% chance
        CLOSE_MESSAGES = ["That hurts to look at.", "How unfortunate."] # 4 green letters
        DUPLICATE_GUESS_MESSAGES = ["Have you tried not typing the same word twice?"] # Duplicate guesses
        WASTING_TIME_MESSAGES_1 = ["Not locked in...", "You took your time... and still lost.", "Zzzzzzz"] # time_used >= 600
        JADEN_LOSS_MESSAGE = ["JED LOSES"]

        if random.randint(1, 200) == 1:
            return random.choice(RARE_LOSS_MESSAGES)

        elif self.username == "jesusfreak72" and random.randint(1, 5) == 1:
            return random.choice(JADEN_LOSS_MESSAGE)

        elif self.get_time_used() <= 25:
            return random.choice(RUSH_MESSAGES)

        elif self.get_time_used() >= 600:
            return random.choice(WASTING_TIME_MESSAGES_1)

        elif len(self.green_letters) >= 4:
            return random.choice(CLOSE_MESSAGES)

        elif len(self.green_letters) <= 1 and len(self.yellow_letters) <= 2:
            return random.choice(POOR_PERFORMANCE_MESSAGES)

        elif len(self.guesses) != len(set(self.guesses)):
            return random.choice(DUPLICATE_GUESS_MESSAGES)

        else:
            return random.choice(NORMAL_MESSAGES)

    def get_win_message(self):
        ONE_GUESS = ["Cheater...", "What the fuck?", "Excuse me?"]
        TWO_GUESSES = ["Damn, okay.", "That's crazy.", "Cracked or just lucky?"]
        THREE_GUESSES = ["Impressive. Kind of.", "Well played.", "Nice!", "Kachow"]
        FOUR_GUESSES = ["Not bad.", "Good job.", "👍"]
        FIVE_GUESSES = ["Okay.", "👍", "At least you didn't cheat."]
        SIX_GUESSES = ["\"Phew\" - John Wordle, 2021", "Not close at all..."]
        SPEEDRUN_MESSAGES = ["That was fast.", "Nerd."] # time_used <= 25
        WASTING_TIME_MESSAGES = ["You sure took your time.", "About time you finished."] # time_used >= 600
        RARE_WIN_MESSAGES = ["gae gaygen is gay"] # 2% chance
        JADEN_WIN_MESSAGES = ["JED WINS"]
        OTHER_MESSAGES = ["If you got this message, then you somehow broke the game. Ping me about this lmfao"]

        if random.randint(1, 50) == 1:
            return random.choice(RARE_WIN_MESSAGES)

        elif len(self.guesses) == 1:
            return random.choice(ONE_GUESS)

        elif random.randint(1, 5) == 1 and self.username == "jesusfreak72":
            return random.choice(JADEN_WIN_MESSAGES)

        elif self.get_time_used() >= 600 and len(self.guesses) >= 3:
            return random.choice(WASTING_TIME_MESSAGES)

        elif self.get_time_used() <= 25 and len(self.guesses) >= 3:
            return random.choice(SPEEDRUN_MESSAGES)

        elif len(self.guesses) == 2:
            return random.choice(TWO_GUESSES)

        elif len(self.guesses) == 3:
            return random.choice(THREE_GUESSES)

        elif len(self.guesses) == 4:
            return random.choice(FOUR_GUESSES)

        elif len(self.guesses) == 5:
            return random.choice(FIVE_GUESSES)

        elif len(self.guesses) == 6:
            return random.choice(SIX_GUESSES)

        else:
            return random.choice(OTHER_MESSAGES)

    def __str__(self):
        output = f"Username: {self.username}\nGuesses: {len(self.guesses)}/{MAX_CHANCES}\n\n"

        if self.game_state == WordleGame.LOSS:
            output += (f"❌ **You lost!** *{self.get_loss_message()}*\nThe word was: **{self.correct_word.upper()}**\n"
                       f"⏰ {seconds_to_descriptive_time(self.get_time_used())}\n\n")

        elif self.game_state == WordleGame.WIN:
            output += (f"✅ **You won!** *{self.get_win_message()}*\n"
                       f"⏰ {seconds_to_descriptive_time(self.get_time_used())}\n"
                       f"✨ +{self.calculate_score()} points\n\n")

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

    game = WordleGame("jesusfreak72", "stilt")
    print(game)

    while game.game_state == WordleGame.UNFINISHED:
        guess = input()
        game.register_guess(guess)

        print(game)
        print(f"Score: {game.calculate_score()}")
