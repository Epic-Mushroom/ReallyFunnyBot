import random

MAX_HAND_VALUE = 21

class GameOverError(Exception):
    pass

class Card:
    SUITS = ['hearts', 'clubs', 'spades', 'diamonds']
    TYPES = ['ace', 'jack', 'queen', 'king'] + [str(i) for i in range(2, 11)]

    def __init__(self, type, suit, value):
        self.type = type
        self.suit = suit
        self.value = value

        if self.type not in Card.TYPES or self.suit not in Card.SUITS:
            raise ValueError("Not a valid card type or suit")

    def __str__(self):
        return f'{self.type} of {self.suit}'

class Hand:
    def __init__(self, cards):
        self.cards: list[Card] = cards
        self.convert_aces()

    def total_value(self):
        return sum(card.value for card in self.cards)

    def convert_aces(self):
        for card in self.cards:
            if card.type == 'ace' and self.total_value() <= MAX_HAND_VALUE - 10:
                card.value += 10

    def add_card(self, card):
        self.cards.append(card)
        self.convert_aces()

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

class BlackjackGame:
    UNFINISHED = 0
    LOSS = 1
    WIN = 2
    TIE = 3

    def __init__(self, username: str, wager: int, rigged = False):
        self.username = username
        self.wager = wager
        self.rigged = rigged

        self.main_deck = build_initial_deck()
        self.dealer_hand = Hand([draw_from_deck(self.main_deck)])
        self.player_hand = Hand([draw_from_deck(self.main_deck), draw_from_deck(self.main_deck)])

        self.game_state = BlackjackGame.UNFINISHED

    def hit(self):
        if not self.game_state == BlackjackGame.UNFINISHED:
            raise GameOverError

        card = draw_from_deck(self.main_deck)
        self.player_hand.add_card(card)

        if player_value > MAX_HAND_VALUE:
            # only update game state if player busts
            self.update_game_state()

    def stand(self):
        if not self.game_state == BlackjackGame.UNFINISHED:
            raise GameOverError

        while self.dealer_hand.total_value() < 17:
            if self.rigged:
                card = draw_from_deck(self.main_deck,
                                      force_value = MAX_HAND_VALUE - self.dealer_hand.total_value() - 1)
                self.dealer_hand.add_card(card)

            card = draw_from_deck(self.main_deck)
            self.dealer_hand.add_card(card)

        self.update_game_state()

    def update_game_state(self):
        dealer_value = self.dealer_hand.total_value()
        player_value = self.player_hand.total_value()

        if dealer_value > MAX_HAND_VALUE:
            self.game_state = BlackjackGame.WIN
            return

        elif player_value > MAX_HAND_VALUE:
            self.game_state = BlackjackGame.LOSS
            return

        self.game_state = (BlackjackGame.WIN if player_value > dealer_value else
                           BlackjackGame.LOSS if player_value < dealer_value else
                           BlackjackGame.TIE)

    def get_game_end_message(self) -> str:
        # -499 <= wager < 0
        NEGATIVE_LOW_WAGER_WIN = ["..."]
        # wager <= -500
        NEGATIVE_BIG_WAGER_WIN = ["This game isn't rigged, I swear.", "You won fair and square :)))))"]

        ZERO_WAGER_TIE = ["Well... you weren't going to lose or gain anything anyway."]
        ZERO_WAGER_LOSS = ["How unfor--wait, you bet literally nothing.", "You didn't lose any money, how boring...",
                           "Testing the waters?", "C'mon, bet more than zero next time."]
        ZERO_WAGER_WIN = ["Hooray.", "Nice job. Now actually bet money next time."]

        # 1 <= wager <= 49
        LOW_WAGER_TIE = ["You should bet your life savings next time."]
        LOW_WAGER_LOSS = ["Good on you for playing it safe, I guess.", "You should bet your life savings next time."]
        LOW_WAGER_WIN = ["C'mon, bet some actual money next time."]

        # 50 <= wager <= 499
        MEDIUM_WAGER_TIE = [""]
        MEDIUM_WAGER_WIN = ["Yeah, you probably cheated.", "Good job, now travel back to 2014 and invest in Bitcoin.", "I can't think of any funny messages so uhh sigma balls"]
        MEDIUM_WAGER_LOSS = ["Remember, 99% of gamblers...", "Statistically speaking, you can only lose 100% of your money, but you can gain over 2000% of it.",
                             "If you're not broke yet, you can always try again.", "Did you know that manually breathing increases your odds of winning?"]

        # wager >= 500
        BIG_WAGER_TIE = ["That's no fun."]
        # 500 <= wager <= 1499
        BIG_WAGER_WIN = ["Bet you got a real dopamine hit out of that."]
        BIG_WAGER_LOSS = ["The dealer can start saving for retirement now."]

        # wager >= 1500
        VERY_BIG_WAGER_WIN = ["Congrats, you are now one step closer to affording NYU tuition."]
        VERY_BIG_WAGER_LOSS = ["Hi, this is the dealer. I just bought another yacht. Thanks!"]

        if self.game_state == BlackjackGame.UNFINISHED:
            return ""

        if self.game_state == BlackjackGame.TIE:
            if self.wager < 0:
                return "That wasn't supposed to happen."

            elif self.wager == 0:
                return random.choice(ZERO_WAGER_TIE)

            elif 1 <= self.wager <= 49:
                return random.choice(LOW_WAGER_TIE)

            elif 50 <= self.wager <= 499:
                return random.choice(MEDIUM_WAGER_TIE)

            else:
                return random.choice(BIG_WAGER_TIE)

        elif self.game_state == BlackjackGame.LOSS:
            if self.wager < 0:
                return "That wasn't supposed to happen."

            elif self.wager == 0:
                return random.choice(ZERO_WAGER_LOSS)

            elif 1 <= self.wager <= 49:
                return random.choice(LOW_WAGER_LOSS)

            elif 50 <= self.wager <= 499:
                return random.choice(MEDIUM_WAGER_LOSS)

            elif 500 <= self.wager <= 1499:
                return random.choice(BIG_WAGER_LOSS)

            else:
                return random.choice(VERY_BIG_WAGER_LOSS)

        elif self.game_state == BlackjackGame.WIN:
            if self.wager <= -500:
                return random.choice(NEGATIVE_BIG_WAGER_WIN)

            elif -499 <= self.wager <= -1:
                return random.choice(NEGATIVE_LOW_WAGER_WIN)

            elif self.wager == 0:
                return random.choice(ZERO_WAGER_WIN)

            elif 1 <= self.wager <= 49:
                return random.choice(LOW_WAGER_WIN)

            elif 50 <= self.wager <= 499:
                return random.choice(MEDIUM_WAGER_WIN)

            elif 500 <= self.wager <= 1499:
                return random.choice(BIG_WAGER_WIN)

            else:
                return random.choice(VERY_BIG_WAGER_WIN)

        return "If you are seeing this then something went wrong. Ping me about this lol"

    def __str__(self):
        output = f"Username: {self.username}\nWager: {self.wager} moneys\n\n"

        if self.game_state == BlackjackGame.TIE:
            output += f"🟨 **You tied.** "
        elif self.game_state == BlackjackGame.LOSS:
            output += f"❌ **You lost!** "
        elif self.game_state == BlackjackGame.WIN:
            output += f"✅ **You won!** "

        output += self.get_game_end_message() + '\n\n'

        output += f"**Dealer:**\n{str(self.dealer_hand)}\n\n**You:**\n{str(self.player_hand)}"

def build_initial_deck() -> list[Card]:
    # god i love list comps
    return [Card(type, suit, 1 if type == 'ace' else 10 if type in ['jack', 'queen', 'king'] else int(type))
            for type in Card.TYPES for suit in Card.SUITS]

def draw_from_deck(deck: list[Card], force_value: int | None = None) -> Card:
    try:
        if force_value is not None:
            new_deck = [card for card in deck if card.value == force_value]
            card = random.choice(new_deck)

        else:
            raise IndexError

    except IndexError:
        card = random.choice(deck)

    deck.remove(card)

    return card

if __name__ == '__main__':
    for card in build_initial_deck():
        print(card)