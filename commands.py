import random

import discord
import wordle
from fish_utils import fish_event, all_pfs

def make_wordle_embed(wordle_game: wordle.WordleGame) -> discord.Embed:
    gray = discord.Colour.from_str("#787C7E")
    red = discord.Colour.from_str("#DD2E44")
    green = discord.Colour.from_str("#78B159")

    embed_color = (gray if wordle_game.game_state == wordle.WordleGame.UNFINISHED else
                   red if wordle_game.game_state == wordle.WordleGame.LOSS else
                   green)
    embed_msg = wordle_game.__str__()

    if len(wordle_game.guesses) == 0:
        embed_msg += "\n*Enter a guess using the /guess command*"

    return discord.Embed(color = embed_color, title = "Wordle", description = embed_msg)

class TestView(discord.ui.View):
    @discord.ui.button(label="Click me")
    async def on_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Congratulations, you clicked a button that does literally nothing. I hope you feel proud of yourself for that.")

class Commands:
    def __init__(self, tree: discord.app_commands.CommandTree):
        self.tree = tree

        self.wordle_games = dict() # follows format "{username}": WordleGame()

    def set_up_commands(self):
        # All commands are to be implemented here
        @self.tree.command(name = "button_test", description = "This is a description")
        async def button_test(interaction: discord.Interaction):
            await interaction.response.send_message("Here is a button", view = TestView())

        @self.tree.command(name = "play_wordle", description = "Starts a game of Wordle")
        async def play_wordle(interaction: discord.Interaction):
            username = interaction.user.name

            if username in self.wordle_games.keys():
                await interaction.response.send_message("You are already playing a game of Wordle")
                return

            game = wordle.WordleGame(username)
            self.wordle_games[username] = game
            await interaction.response.send_message(embed = make_wordle_embed(game))
            await interaction.channel.send(f"The word is {game.correct_word}")

        @self.tree.command(name = "guess", description = "Guess a word (Wordle)")
        @discord.app_commands.describe(word = "Your guess (must be a valid five-letter word)")
        async def guess(interaction: discord.Interaction, word: str):
            username = interaction.user.name

            if username not in self.wordle_games.keys():
                game = wordle.WordleGame(username)
                self.wordle_games[username] = game

            else:
                game = self.wordle_games[username]

            try:
                game.register_guess(word)

            except wordle.InvalidGuessError:
                await interaction.channel.send("That's not a valid word")

            await interaction.response.send_message(embed = make_wordle_embed(game))

            if game.game_state != wordle.WordleGame.UNFINISHED:
                del self.wordle_games[username]

                if random.randint(1, 1000) <= game.calculate_score(): # score divided by 10 is the chance in %
                    await interaction.channel.send(fish_event(username, force_fish_name = "Wordlefish", bypass_fish_cd = True))
                    all_pfs.write_data()


