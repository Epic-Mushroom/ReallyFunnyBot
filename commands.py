import random

import discord
import wordle, fish_utils

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
                await interaction.channel.send("You are already playing a game of Wordle")

            else:
                game = wordle.WordleGame(username)
                self.wordle_games[username] = game

            await interaction.response.send_message(embed = make_wordle_embed(self.wordle_games[username]))
            # await interaction.channel.send(f"The word is {game.correct_word}")

        @self.tree.command(name = "guess", description = "Guess a word (Wordle)")
        @discord.app_commands.describe(word = "Your guess (must be a valid five-letter word). Enter \"quit\" to give up")
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

                score = game.calculate_score()
                profile = fish_utils.all_pfs.profile_from_name(username)
                profile.wordle_points += score

                if game.game_state == wordle.WordleGame.LOSS:
                    profile.wordle_losses += 1
                else:
                    profile.wordle_wins += 1

                if random.uniform(1, 1000) <= score: # score divided by 10 is the chance in %
                    await interaction.channel.send(fish_utils.fish_event(username, force_fish_name = "Wordlefish", bypass_fish_cd = True))

                fish_utils.all_pfs.write_data()

        @self.tree.command(name = "leaderboard", description = "Displays the leaderboard")
        @discord.app_commands.describe(type = "Type of leaderboard to display (defaults to moneys)")
        @discord.app_commands.choices(type = [discord.app_commands.Choice(name = "moneys", value = "default"),
                                              discord.app_commands.Choice(name = "RNG", value = "rng"),
                                              discord.app_commands.Choice(name = "Wordle", value = "wordle")])
        async def leaderboard(interaction: discord.Interaction, type: str = 'default'):
            embed = None
            if type == 'default':
                embed = discord.Embed(
                    title = f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Leaderboard',
                    description = fish_utils.leaderboard_string())

            elif type == 'rng':
                embed = discord.Embed(
                    title = f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}RNG Leaderboard',
                    description = fish_utils.luck_leaderboard_string())

            elif type == 'wordle':
                embed = discord.Embed(
                    title = 'Wordle Leaderboard',
                    description = fish_utils.wordle_leaderboard_string()
                )

            await interaction.response.send_message(embed = embed)

        @self.tree.command(name = "profile", description = "Displays a user's fishing stats")
        @discord.app_commands.describe(user = "User whose profile will be displayed (defaults to self)")
        async def profile(interaction: discord.Interaction, user: discord.User | None = None):
            username = interaction.user.name if user is None else user.name

            embed = discord.Embed(
                title = f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}'
                        f'{username}\'s Profile',
                description = fish_utils.profile_to_string(username))

            await interaction.response.send_message(embed = embed)

        @self.tree.command(name = "universal_stats", description = "Displays universal fishing stats")
        async def universal_stats(interaction: discord.Interaction):
            embed = discord.Embed(
                title = f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Universal Stats',
                description = fish_utils.universal_profile_to_string())

            await interaction.response.send_message(embed = embed)


