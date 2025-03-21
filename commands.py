import discord

class TestView(discord.ui.View):
    @discord.ui.button(label="Label")
    async def on_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked a button. I bet that was pretty satisfying")

class Commands:
    def __init__(self, tree: discord.app_commands.CommandTree):
        self.tree = tree

    def set_up_commands(self):
        # All commands are to be implemented here
        @self.tree.command(name = "button_test", description = "This is a description")
        async def button_test(interaction: discord.Interaction):
            await interaction.response.send_message("Here is a button", view = TestView())