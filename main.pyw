import os, random, time, asyncio
import discord
import commands, fish_utils, shop_utils, backup_utils

from pathlib import Path
from discord.ext import tasks
from string_utils import *
from constants import *


class BotInstance:

    def __init__(self, client: discord.Client):
        self.server_instance_list: list[ServerInstance] = []
        self.current_status_task: asyncio.Task | None = None
        self.client = client

        self.tree = discord.app_commands.CommandTree(self.client)

    def get_tree(self):
        return self.tree

    def add_server_instance(self, guild: discord.Guild):
        self.server_instance_list.append(ServerInstance(guild))

    def get_server_instance(self, guild: discord.Guild):
        return next((i for i in self.server_instance_list if i.server == guild), None)

    def set_current_status_task(self, task):
        self.current_status_task = task

    def cancel_current_status_task(self):
        try:
            self.current_status_task.cancel()

        except AttributeError:
            pass

class ServerInstance:

    def __init__(self, guild: discord.Guild):
        self.server = guild
        try:
            self.server_name = guild.name
            self.nickname = guild.me.display_name
        except AttributeError:
            self.server_name = None
            self.nickname = client.user.name

        self.recently_sent_messages = 0
        self.cd_last_reset_time = int(time.time())
        self.something_sent = False
        self.comedians = ["Kush", "Kayshav", "dad", "James", 'Dad',
                          self.nickname]

        self.lockdown = 0  # unix time when lockdown expires

    def get_server(self):
        return self.server

    def get_server_name(self):
        return self.server_name

    def get_nickname(self) -> str:
        return self.nickname

    def on_cooldown(self) -> bool:
        current_time = int(time.time())
        return (self.recently_sent_messages >= COOLDOWN_LIMIT
                and (current_time - self.cd_last_reset_time) < COOLDOWN_LENGTH)

    def clear_message_cache(self) -> None:
        self.something_sent = False

    def reset_cooldown(self, force = False) -> None:
        current_time = int(time.time())
        if force or current_time - self.cd_last_reset_time >= COOLDOWN_LENGTH:
            self.cd_last_reset_time = current_time
            self.recently_sent_messages = 0

    def time_since_cd_last_reset_time(self) -> int:
        current_time = int(time.time())
        return current_time - self.cd_last_reset_time

    def get_comedians(self) -> list[str]:
        return self.comedians

    async def send_message(self, reference, text, reply = True, ping = True,
                           bypass_cd = False, file_path = None,
                           fishing = False) -> discord.Message | None:
        # prevents message length from going over 2000
        if len(str(text)) > 1990:
            text = ("[*some parts of this message were removed because of discord's character limit*]\n" +
                    text[-1800:])

        file = None
        if file_path:
            file = discord.File(file_path)

        if self.on_cooldown() and not fishing:
            print(f'On cooldown. Message withheld: {text}')
            return

        if self.on_lockdown() and not fishing:
            print(f'On lockdown. Message withheld: {text}')
            return

        if bypass_cd or not (self.something_sent or self.on_cooldown()):
            self.something_sent = True

            if not bypass_cd:
                self.recently_sent_messages += 1

            msg = await reference.channel.send(text, file = file, allowed_mentions = None if ping else discord.AllowedMentions().none(), reference = reference if reply else None)

            increment_total_triggers()

        if file:
            file.close()

        return msg

    async def mimic_presence(self, default_name=""):
        """
        Copies the status of a certain user when called. If the user has no activity,
        changes bot's activity to default_name
        """
        try:
            stalked_member = self.server.get_member(STALKED_ID)

            if stalked_member is None:
                # on_presence_update gets called once for every mutual server with the user
                raise AttributeError

        except AttributeError:
            return

        # print(f"attempting to mimic the status of {stalked_member.name}")

        stalked_activity = next((activity for activity in stalked_member.activities if activity.type == discord.ActivityType.playing), None)

        if stalked_activity is not None:
            # print(f"changing bot's activity to {stalked_activity.name}")
            await client.change_presence(activity = stalked_activity)

        else:
            # print(f"this user does not have a "playing" activity, changing bot activity to {default_name if
            # default_name else "nothing"}")

            await change_presence(default_name)

    async def change_nickname(self, nickname):
        bot_member = self.server.get_member(client.user.id)

        await bot_member.edit(nick = nickname)

    def set_lockdown(self, seconds) -> int:
        self.lockdown = int(time.time()) + seconds
        return self.lockdown

    def on_lockdown(self):
        return int(time.time()) < self.lockdown

# Directory setup
script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

# For local testing purposes; the 'testing' directory should only be available on local
ADMIN_ONLY = False
test_file = None
try:
    test_file = open(Path("testing", "adminonlyenabled.txt"))
    ADMIN_ONLY = True
except FileNotFoundError:
    ADMIN_ONLY = False
finally:
    if test_file:
        test_file.close()

# Token and commands guild setup
SECRET_FILE_PATH_MAIN = Path('secrets', 'discord bot token.txt')
SECRET_FILE_PATH_TEST = Path('secrets', 'test discord bot token.txt')
TOKEN = None

token_path = SECRET_FILE_PATH_TEST if ADMIN_ONLY else SECRET_FILE_PATH_MAIN

with open(token_path) as file1:
    TOKEN = file1.readline()

# Setup certain variables according to value of ADMIN_ONLY
COMMANDS_GUILD = None
STALKED_ID = JAMES_ID

if ADMIN_ONLY:
    COMMANDS_GUILD = discord.Object(id = MY_GUILD)
    STALKED_ID = EPIC_MUSHROOM_ID

# Discord client setup
intents = discord.Intents.all()
client = discord.Client(intents = intents)

bot_instance = BotInstance(client)

REVENGE_LYRICS = file_lines_to_list(Path('revenge.txt'))
DRUG_NAMES = file_lines_to_list(Path('drugs_list.txt'))

def random_range(start: int, stop: int) -> int:
    """me when i don't know that random.randint exists"""
    return random.randrange(start, stop + 1)

def increment_total_triggers(count=1):
    total_triggers_file = None

    try:
        total_triggers_file = Path("trackers", "total_triggers.txt").open('r+')
        current_count = int(total_triggers_file.readline())
        total_triggers_file.seek(0)
        total_triggers_file.write(f"{current_count + 1}")

    finally:
        if total_triggers_file:
            total_triggers_file.close()

async def change_presence(game_name=""):
    if not game_name:
        await client.change_presence()

    else:
        await client.change_presence(activity = discord.Game(game_name))

async def fishing_status_coro(server_instance):
    possible_presences = ["fishing", "go fish", "><>", "<><",
                          "go fish", "jobless behavior", "fishe"]
    chosen_presence = random.choice(possible_presences)
    client_activity = server_instance.server.get_member(client.application_id).activity

    if client_activity is not None and client_activity.name in possible_presences:
        chosen_presence = client_activity.name

    await server_instance.mimic_presence(default_name = chosen_presence)
    await asyncio.sleep(20)
    await server_instance.mimic_presence()

@tasks.loop(time=REMINDER_TIME)
async def reminder():
    me = await client.fetch_user(EPIC_MUSHROOM_ID)
    await me.send('@everyone')

@client.event
async def on_ready():
    # syncs commands
    my_commands = commands.Commands(bot_instance.get_tree())
    my_commands.set_up_commands()

    # commands should not be synced all the time
    # await bot_instance.get_tree().sync()
    print(f'number of commands synced: {len(bot_instance.get_tree().get_commands())}')

    # for c in bot_instance.get_tree().get_commands():
    #     print(c.name, c.description)

    # starts tasks
    reminder.start()

    # adds server instances to bot instance
    for g in client.guilds:
        bot_instance.add_server_instance(g)

    print(f'connected to {len(client.guilds)} servers')

    # sends startup message in a specific channel
    if not ADMIN_ONLY:
        lgg_channel = await client.fetch_channel(LETS_GO_GAMBLING_CHANNEL_ID)
        await lgg_channel.send("Bot successfully started")

@client.event
async def on_presence_update(before, after: discord.Member):
    if after.id == STALKED_ID and after.guild.id == (PRIVATE_SERVER_ID if ADMIN_ONLY else GROUP_CHAT_SERVER_ID) :
        instance = bot_instance.get_server_instance(after.guild)
        # print(f"entered conditional, user's guild is {after.guild.name}")

        if instance is None:
            raise AttributeError("no guild found (?? what??)")

        if before.activity != after.activity:
            await instance.mimic_presence()

@client.event
async def on_message(message: discord.Message):
    async def send(content = '** **', reply = True, bypass_cd = False, ping = True, file_path=None, fishing=False):
        return await server_instance.send_message(message, content, reply = reply, ping = ping, bypass_cd = bypass_cd, file_path = file_path, fishing = fishing)

    referred_message = None
    lowercase_message_content = message.content.lower()

    current_time = int(time.time())
    current_guild = message.guild

    server_instance: None | ServerInstance = bot_instance.get_server_instance(current_guild)

    # Creates a server instance for dms if the message was sent through dms
    if server_instance is None:
        bot_instance.add_server_instance(current_guild)
        server_instance = bot_instance.server_instance_list[-1]

    # Makes it so it doesn't reply to itself (or other bots)
    if message.author.bot:
        return

    if message.reference is not None:
        referred_message = await message.channel.fetch_message(message.reference.message_id)

    # Resets the cooldown every COOLDOWN_LENGTH seconds and message cache
    server_instance.reset_cooldown()
    server_instance.clear_message_cache()

    # Enables admin commands
    is_admin = message.author.id == EPIC_MUSHROOM_ID

    # Makes the bot only respond in dms/my server if ADMIN_ONLY is enabled
    can_proceed = not ADMIN_ONLY or (is_admin and (server_instance.server_name is None or server_instance.get_server().id == MY_GUILD))
    if not can_proceed:
        print("Non-admin message detected while in testing mode")
        return

    # Triggers start here
    index_of_im = index_after_any_word(lowercase_message_content, POSSESSIVE_PERSONAL_PRONOUN_LIST)
    index_of_pronoun = index_after_any_word(lowercase_message_content, PRONOUNS)

    # if any(lowercase_message_content.strip().startswith(lyric) for lyric in REVENGE_LYRICS):
    #     try:
    #         lyric_found = find_any_substring(message.content, REVENGE_LYRICS)
    #         await send(REVENGE_LYRICS[REVENGE_LYRICS.index(lyric_found) + 1])
    #     except IndexError:
    #         pass
    #     except ValueError:
    #         pass

    if has_any_word(message.content, ['allegro barbaro']):
        await message.add_reaction('👎')

    if has_any_word(message.content, POSSESSIVE_PERSONAL_PRONOUN_LIST):
        interpreted_name = strip_punctuation(message.content[index_of_im:])
        if len(interpreted_name) > 0 and random_range(1, 1) == 1:
            await server_instance.send_message(message, f"Hi {interpreted_name}, I'm {random.choice(server_instance.get_comedians())}!", ping = False)

    if has_any_word(message.content, TYPOS) and random_range(1, 1) == 1:
        await send("https://www.wikihow.com/Type", reply = True)

    if "crazy" in lowercase_message_content.lower():
        await send(f"{random.choice(CRAZY_RESPONSES)}", reply = True)

    if random_range(1, 1000) == 1 and (message.author.id == PALIOPOLIS_ID or message.author.id == JADEN_ID):
        await message.add_reaction(random.choice(NEGATIVE_EMOJIS))

    if random_range(1, 100) == 1 and message.author.id == MOKSHA_ID:
        await message.add_reaction("🧔🏿‍♀️")

    if referred_message and referred_message.author == client.user:
        if referred_message.content.lower() == "who":
            if strip_punctuation(lowercase_message_content.lower()) != "asked":
                await send("asked :rofl::rofl:", bypass_cd = True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))
        elif referred_message.content.lower() == "what":
            if strip_punctuation(lowercase_message_content.lower()) != "ever":
                await send("ever :joy::joy:", bypass_cd = True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))
        elif referred_message.content.lower() == "when":
            if strip_punctuation(lowercase_message_content.lower()) != "did i ask" and strip_punctuation(lowercase_message_content.lower()) != "did you ask":
                await send("did I ask :joy::joy::rofl:", bypass_cd = True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))

    if has_any_substring(lowercase_message_content, THICK_OF_IT_TRIGGERS):
        await send(file_path = Path('videos', 'thick of it lipsync.mp4'))

    if has_any_substring(lowercase_message_content, ['skibidi', 'hawk tuah', 'jelqing', 'lv 100 gyatt']):
        await send("no", reply = False)

    if "FUCK" in message.content or "SHIT" in message.content or lowercase_message_content == "shut the fuck up":
        await send(random.choice(SWEARING_RESPONSES))

    if has_any_word(message.content, ['kys', 'kill yourself', 'kill your self']):
        await send(random.choice(KYS_RESPONSES))
    
    if "what is the time" in lowercase_message_content:
        await send(f"It is <t:{current_time}:f>")

    if "what is the unix time" in lowercase_message_content:
        await send(f"The unix time is {current_time}\nformatted, that's <t:{current_time}:f>")

    if "totaltriggers" in lowercase_message_content:
        total_triggers_file = None
        current_count = None

        try:
            total_triggers_file = Path("trackers", "total_triggers.txt").open('r')
            current_count = int(total_triggers_file.readline())
        finally:
            if total_triggers_file:
                total_triggers_file.close()

        await send(f"{current_count} triggers", bypass_cd = True)

    if "cooldownstatus" in lowercase_message_content:
        if server_instance.on_cooldown():
            await send(f"I am on cooldown. Stop freaking spamming bro. (cooldown length is {COOLDOWN_LENGTH}, "
                       f"max number of messages able to be sent per cooldown reset period is {COOLDOWN_LIMIT}, "
                       f"{server_instance.recently_sent_messages+1} messages were sent during this period)", bypass_cd = True)

        else:
            await send(f"I am not on cooldown. (cooldown length is {COOLDOWN_LENGTH}, "
                       f"max number of messages able to be sent per cooldown reset is {COOLDOWN_LIMIT}, "
                       f"{pluralize(server_instance.recently_sent_messages + 1, "message")} were sent during this period)", bypass_cd = True)

    if has_any_substring(message.content, ['resetcd']):
        if is_admin:
            await send("Reset cooldown", bypass_cd = True)
            server_instance.reset_cooldown(force = True)

        else:
            await send('Nah I don\'t feel like it', bypass_cd = True)

    if "HALOOLYH BRIKTAY" == message.content:
        await send(message.content)

    if has_any_word(message.content, ['money']) and random_range(1, 30) == 1:
        temu = """Happy New Year~ Sending you a New Year's card. Come and see my New Year's wishes and accept my invitation.
-For real?
-Sure, only 2 steps to take the gift and help me get mine!
https://temu.com/s/Ut2tvFcWcwAKgdUM"""
        await asyncio.sleep(5)
        await send(temu, reply = False)

    if has_any_substring(message.content, ['ur mom', 'your mom', 'ur dad', 'ur gae', 'ur gay', "you're gay"]):
        await message.add_reaction(random.choice(FUNNY_EMOJIS))

    if has_any_word(lowercase_message_content, AMONG_US_TRIGGERS):
        await server_instance.send_message(message, random.choice(AMONG_US_RESPONSES))

    if has_any_substring(message.content, ['mind blowing', 'mindblowing', ":exploding_head:", "🤯"]):
        image_path = Path("images", "emoji483.png")
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if has_any_word(message.content, ['literally 1984']):
        winston = """It was a bright cold day in April, and the clocks were striking thirteen. Winston Smith, his chin nuzzled into his breast in an effort to escape the vile wind, slipped quickly through the glass doors of Victory Mansions, though not quickly enough to prevent a swirl of gritty dust from entering along with him.

The hallway smelt of boiled cabbage and old rag mats. At one end of it a coloured poster, too large for indoor display, had been tacked to the wall. It depicted simply an enormous face, more than a metre wide: the face of a man of about forty-five, with a heavy black moustache and ruggedly handsome features. Winston made for the stairs. It was no use trying the lift. Even at the best of times it was seldom working, and at present the electric current was cut off during daylight hours. It was part of the economy drive in preparation for Hate Week. The flat was seven flights up, and Winston, who was thirty-nine and had a varicose ulcer above his right ankle, went slowly, resting several times on the way. On each landing, opposite the lift-shaft, the poster with the enormous face gazed from the wall. It was one of those pictures which are so contrived that the eyes follow you about when you move. BIG BROTHER IS WATCHING YOU, the caption beneath it ran."""

        await send(winston, reply = False)

    if random_range(1, 420) == 1 and has_any_word(message.content, DRUG_NAMES):
        await send("https://tenor.com/view/sobriety-prevent-the-misuse-of-drugs-and-alcohol-your-mental-health-will-thank-you-sober-recovery-gif-25389902", reply = False)
        # await message.delete()

    if has_any_substring(message.content, ["kachow"]):
        image_path = Path("images", "jedwin", "kachow.png")
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if has_any_substring(message.content, ["slavery"]):
        image_path = Path("images", "jedwin", "Jailed_Jedgar.jpg")
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if has_any_substring(message.content, ["jaden christian edwin"]):
        image_path = random.choice(list(Path("images", "jedwin").iterdir()))
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if has_any_word(message.content, ['persona', 'specialist']):
        video_path = Path("videos", "p4 specialist compressed.mp4")
        try:
            await server_instance.send_message(message, "** **", file_path=video_path)
        except FileNotFoundError:
            print(f"'{str(video_path)} wasn't found'")

    if has_any_word(message.content, ['speech bubble', 'speechbubble']) and referred_message:
        await referred_message.reply(random.choices(SPEECH_BUBBLES), allowed_mentions = discord.AllowedMentions().none()
                                     if message.mentions else None)

    if has_any_word(message.content, ['brawl stars', 'hop on brawl']):
        await send('https://tenor.com/view/wanna-play-brawl-stars-lonely-no-one-plays-brawl-stars-lmoa-gif-23811622')

    if has_any_word(message.content, ['sigma']):
        await send('https://tenor.com/view/not-a-sigma-sorry-you-are-not-a-sigma-sorry-you%27re-not-a-sigma-you-aren%27t-a-sigma-you-are-not-sigma-gif-337838532227751572')

    if has_any_word(message.content, ['uwu', 'owo', ':3']):
        await send('https://tenor.com/view/kekw-gif-21672467')

    if has_any_word(message.content, ['can i', 'can we']):
        index_can = index_after_any_word(message.content, ['can i', 'can we'])
        interpreted_text = strip_punctuation(message.content[index_can:])
        
        if len(interpreted_text) > 0:
            await send(f"idk can you {interpreted_text}", reply = False)

    if random_range(1, 6666) == 1:
        await send('🐺 (this message has a 1/6,666 chance to appear)', bypass_cd = True, reply = False)

    if has_any_substring(message.content, ['flip a coin']):
        if random_range(1, 2) == 1:
            await send('Heads', bypass_cd = True)
        else:
            await send('Tails', bypass_cd = True)

    if has_any_substring(message.content, ['roll a die', 'roll a dice', 'diceroll']):
        await send(str(random_range(1, 6)), bypass_cd = True)

    if has_any_substring(message.content, ['roll a d20']):
        await send(str(random_range(1, 20)), bypass_cd = True)

    if has_any_substring(message.content, ['what is my name']):
        await send(f"{message.author.display_name} *({message.author.name})*", reply = True)

    if has_any_substring(message.content, ['battle pass']):
        fortnite_battle_pass = """Fortnite Battle Pass 🗣️🗣️
I just shit out my ass 🗣️🗣️🗣️
Booted up my PC 💻💻
'Cause I need-need 🥴🥴🥴
To get that Fortnite Battle Pass 🗣️🗣️
I like Fortnite 👶👶
Did I mention Fortnite?🗣️🗣️
I like Fortnite 👶
Its Nighttime🌃🌃
I mean, it's 5 o'clock 🕔 🕔, that's basically nighttime 😴😴 🌃
Y'all remember Cartoon Network?; Adventure Time 🐕‍🦺
        """
        await send(fortnite_battle_pass)

    if has_any_substring(message.content, ['🐟', '🎣', '🐠', '🐡', 'asdfghjkl', 'go phish', 'go fish', 'jobless behavior', 'le fishe',
                                        'quiero comer pescado',
                                        '.fish', '><>', '去钓鱼', '<><', '2+2', 'godfisa',
                                        'zxcvbnm', 'qwertyuiop', 'go ghoti']):
        if random_range(1, 1000) == 1:
            jumpscare = await send(file_path = Path('images', 'deepfriedjumpscare.png'), fishing = True)
            await asyncio.sleep(0.42)
            await jumpscare.delete()
            await asyncio.sleep(0.5)

        if not message.channel.id in [GENERAL_CHANNEL_ID_1, GENERAL_CHANNEL_ID_2, GENERAL_CHANNEL_ID_3]:
            try:
                # if ADMIN_ONLY and is_admin:
                #     fish_utils.all_pfs.profile_from_name(message.author.name).last_fish_time = 0

                content = f'{'[TESTING ONLY] ' if not fish_utils.FISHING_ENABLED else ''}{fish_utils.fish_event(message.author.name)}'
                await send(content, reply = True, bypass_cd = True, fishing = True)

            except fish_utils.MaintenanceError:
                await send(f'fishing is currently disabled, go play minecraft in the meantime or some shit', fishing = True)

            fish_utils.all_pfs.write_data()

            bot_instance.cancel_current_status_task()
            bot_instance.set_current_status_task(asyncio.create_task(fishing_status_coro(server_instance)))

        elif not has_any_substring(message.content, ['2+2', 'zxcvbnm', 'qwertyuiop', 'asdfghjkl', '🐟', '🎣', '🐠', '🐡', 'jobless behavior']):
            temp_path = Path("images", "no fishing in general.gif")
            await send(reply = True, file_path = temp_path)

            return

    if message.content.startswith('admin:') and len(message.content) > 6:
        if is_admin:
            if message.content.startswith('admin:switch'):
                if fish_utils.switch_fishing():
                    await server_instance.send_message(message, 'Fishing sim turned on. let the brainrot begin', fishing= True)
                else:
                    await server_instance.send_message(message, 'Fishing sim turned off. go outside everyone', fishing= True)

            elif message.content.startswith('admin:restart'):
                try:
                    backup_utils.make_backup()
                    await server_instance.send_message(message, "Restarting bot", bypass_cd = True)
                    exit(2)

                except Exception as e:
                    await send(f'bro you done fucked smth up ({e})', fishing = True)

            elif message.content.startswith('admin:backup'):
                try:
                    backup_utils.make_backup()
                    await send('Backup successful', fishing = True)

                except Exception as e:
                    await send(f'bro you done fucked smth up ({e})', fishing = True)

            elif message.content.startswith('admin:mutebot '):
                parts = message.content.split(' ')
                timeout_length = int(parts[-1])

                lockdown_expiry_time = server_instance.set_lockdown(timeout_length)
                await send(f'The bot may not exercise freedom of speech until <t:{lockdown_expiry_time}:f>', reply = False, bypass_cd = True, fishing = True)

            elif message.content.startswith('admin:unmutebot'):
                server_instance.set_lockdown(-1)
                await send('The bot may exercise freedom of speech again', reply = False, bypass_cd = True)

            elif message.content.startswith('admin:save'):
                fish_utils.all_pfs.write_data()

            elif message.content.startswith('admin:give'):
                # ONLY USE THIS IF FISH IS UNFAIRLY LOST/GAINED BECAUSE OF BUGS
                # format: "admin:give "epicmushroom." "God" 3"
                parts = message.content.split('"')

                if len(parts) <= 1:
                    # send with no args to get help message
                    await send('format: \'admin:give "epicmushroom." "God" 3\'')

                temp_username = parts[1]
                temp_fish = fish_utils.get_fish_from_name(parts[3])
                try:
                    temp_count = int(parts[4].strip())
                except IndexError:
                    temp_count = 1
                except ValueError:
                    temp_count = 1
                except Exception as e:
                    await send(f"Something went wrong [{e}]", bypass_cd = True)
                    return

                temp_profile = fish_utils.all_pfs.profile_from_name(temp_username)
                if temp_profile is not None and temp_fish is not None:
                    temp_profile.add_fish(temp_fish, temp_count)
                else:
                    await send("User/fish couldn't be found", bypass_cd = True)
                    return

                await send(f"Gave {temp_count} {temp_fish.name} to {temp_username}\n", bypass_cd = True)
                fish_utils.all_pfs.write_data()

            elif message.content.startswith("admin:ban"):
                # format: "admin:ban epicmushroom. 3600 testing testing"
                parts = message.content.split(" ")

                if len(parts) <= 1:
                    # send with no args to get help message
                    await send('format: "admin:ban epicmushroom. 3600 the reason"')

                temp_username = parts[1]
                try:
                    temp_duration = int(parts[2])
                except IndexError:
                    temp_duration = 60
                except ValueError:
                    await send("Invalid ban duration")
                    return
                if len(parts) >= 4:
                    temp_reason = ' '.join(parts[3:])
                else:
                    temp_reason = "none"

                try:
                    fish_utils.all_pfs.profile_from_name(temp_username).ban(temp_duration, temp_reason)
                except AttributeError:
                    await send("Profile not found")
                    return

                await send(f"Banned {temp_username} from fishing for {temp_duration} seconds with reason \"{temp_reason}\"")

                fish_utils.all_pfs.write_data()

            elif message.content.startswith("admin:unban"):
                parts = message.content.split(" ")

                temp_username = parts[1]

                try:
                    fish_utils.all_pfs.profile_from_name(temp_username).unban()
                except AttributeError:
                    await send("Profile not found")
                    return

                await send(f"Unbanned {temp_username} from fishing")

                fish_utils.all_pfs.write_data()

            elif message.content.startswith("admin:saymessage"):
                try:
                    await send(message.content[len("admin:saymessage"):])

                except discord.errors.HTTPException:
                    pass

        else:
            await send('you can\'t do that (reference to 1984 by George Orwell)',
                                                   bypass_cd = True)

    if is_admin or fish_utils.FISHING_ENABLED:
        if has_any_substring(message.content, ['show profile', 'show pf']):
            username_temp = message.author.name
            if (lowercase_message_content.startswith('show profile ') or
                lowercase_message_content.startswith('show pf ')):
                parts = message.content.split(' ')
                username_temp = parts[-1]

            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}'
                                        f'{username_temp}\'s Profile', description=fish_utils.profile_to_string(username_temp))
            await message.channel.send(embed = embed)

            return

        if has_any_substring(message.content, ['show leaderboard', 'show lb', '.lb']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Leaderboard',
                                  description=fish_utils.leaderboard_string())
            await message.channel.send(embed = embed)
            # await server_instance.send_message(message, fish_utils.leaderboard_string(), bypass_cd = True)

            return

        if has_any_substring(message.content, ['item rng lb', 'old luck lb', 'old rng lb', 'show luck old', '.oldrnglb', '.oldlbrng', '.oldlbluck', '.oldlucklb']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}RNG Leaderboard (by item)',
                                  description=fish_utils.leaderboard_string(sort_by_luck= True))
            await message.channel.send(embed = embed)

            return

        elif has_any_substring(message.content, ['luck lb', 'rng lb', 'show luck', '.rnglb', '.lbrng', '.lbluck', '.lucklb']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}RNG Leaderboard',
                                  description=fish_utils.luck_leaderboard_string())
            await message.channel.send(embed = embed)

            return

        if has_any_substring(message.content, ['all fish', 'global stats', 'global fish', 'all stats', 'combined profiles', 'combined joblessness',
                                            'global joblessness', 'how jobless is everyone', '.allfish']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Universal Stats',
                                  description=fish_utils.universal_profile_to_string())
            await message.channel.send(embed = embed)

            return

        if lowercase_message_content.startswith('go shop') or lowercase_message_content.startswith('show shop'):
            parts = message.content.split(' ')
            page_num = 1

            try:
                page_num = int(parts[-1])
            except ValueError:
                pass

            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Shop (Page '
                                        f'{page_num:,} of {shop_utils.max_page():,})', description=shop_utils.display_shop_page(page_num),
                                  color=0xffffff)
            await message.channel.send(embed = embed)

        if lowercase_message_content.startswith('go buy'):
            parts = message.content.split(' ')
            item_id = None

            try:
                item_id = int(parts[-1])
            except ValueError:
                pass

            try:
                item = shop_utils.get_shop_item_from_id(item_id)
                item.sell_to(message.author.name)

                await message.reply(f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}You purchased {item.name}')

                fish_utils.all_pfs.write_data()
            except shop_utils.UserIsBroke:
                await message.reply(f'You are too broke to buy that item!')
            except shop_utils.AlreadyOwned:
                await message.reply(f'You already have that upgrade!')
            except shop_utils.RequirementError:
                await message.reply(f'You don\'t have the prerequisite upgrades owned!')
            except AttributeError:
                await message.reply(f'That\'s not a valid ID')

            return

        if has_any_substring(message.content, ['show manifesto', 'go manifesto']):
            # returns the fishing manifesto factor and percent boost for a given user
            parts = message.content.split(' ')

            pf = fish_utils.all_pfs.profile_from_name(parts[-1])
            if pf is None:
                pf = fish_utils.all_pfs.profile_from_name(message.author.name)
            factor = fish_utils.fishing_manifesto_factor(pf.username)

            if pf:
                await send(f'{pf.username}: {fish_utils.factor_to_percent_increase(factor):.1f}% boost on avg (doesn\'t include effects of powerups)',
                       bypass_cd = True)
            else:
                await send("That user (probably) doesn't exist", bypass_cd = True)

    if message.content.startswith('!spam '):
        parts = message.content.split(' ')
        times = int(parts[1])
        kush = await client.fetch_user(KUSH_ID)

        for i in range(times):
            if len(parts) >= 3:
                await kush.send(f'{parts[2]}')
            else:
                await kush.send('Hi')

    if has_any_word(lowercase_message_content, ['guess what']):
        await send('chicken butt', reply = True)

    if has_any_word(lowercase_message_content, JOB_RELATED_TERMS_1):
        await send(random.choice(AI_RESPONSES), ping = False)
        return

    if has_any_word(message.content, JOB_RELATED_TERMS_2) and not has_any_word(lowercase_message_content, JOB_RELATED_TERMS_1):
        await message.add_reaction('👎')

    if find_any_substring(lowercase_message_content, ['jaden status', 'jedwin']):
        time_tuple = days_and_hours_since(current_time, JADEN_18TH_BIRTHDAY_UNIX_TIME)
        await send(f"Jaden has been stalking minors for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_any_substring(lowercase_message_content, ['james status']):
        time_tuple = days_and_hours_since(current_time, JAMES_18TH_BIRTHDAY_UNIX_TIME)
        await send(f"James has been getting high for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_any_substring(lowercase_message_content, ['aravind status', 'arvind']):
        time_tuple = days_and_hours_since(ARAVIND_18TH_BIRTHDAY_UNIX_TIME, current_time)
        await send(f"Aravind will be legal in {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_any_substring(lowercase_message_content, ['kush status', 'hush b', 'hush']):
        time_tuple = days_and_hours_since(current_time, KUSH_BIRTHDAY_UNIX_TIME)
        await send(f"Kush has been consuming brainrot for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_any_substring(lowercase_message_content, ['kayshav status']):
        time_tuple = days_and_hours_since(current_time, KUSH_BIRTHDAY_UNIX_TIME)
        await send(f"Kayshav has been consuming brainrot for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_any_substring(lowercase_message_content, ['show house profits', 'show casino profits']):
        await send(f"The house has made {fish_utils.all_pfs.house_profits():,} moneys")
        return

    if find_any_substring(lowercase_message_content, ['hop on']):
        if random_range(1, 50) == 1:
            await send("hop on deez nuts imo", reply = False)

        if has_any_word(lowercase_message_content, ['vc']):
            vc = await client.fetch_channel(VOICE_CHANNEL_ID)
            await vc.connect()

    if has_any_word(lowercase_message_content, ['am i cooked', 'is he cooked', 'are we cooked', 'is she cooked', 'is it cooked']):
        await send(random.choice(EIGHT_BALL_RESPONSES))
        return

    if lowercase_message_content == 'wait':
        await send("I'm waiting", reply = False)
        return

    if lowercase_message_content == 'listen':
        await send("I'm listening", reply = False)
        return

    if lowercase_message_content == 'look':
        await send("I'm looking", reply = False)
        return

    if find_any_substring(lowercase_message_content, ['testingtesting']):
        await server_instance.change_nickname("test")

    # if random_range(1, 210) == 1:
    #     await send(f"{random.choice(BAITS)}", ping = False)
    # elif index_of_pronoun > -1 and random_range(1, 27) == 1:
    #     await send(f"{random.choice(BAITS[4:])}", ping = False)

if __name__ == '__main__':
    client.run(TOKEN)