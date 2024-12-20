import discord, os, random, time, logging, sys, json_utils, asyncio, subprocess
from dotenv import load_dotenv
from pathlib import Path
from string_utils import *
# Yeah thats right prof thornton im using import * what are you gonna do about it

# SETUP
script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

load_dotenv()

# TOKEN = os.getenv('DISCORD_TOKEN')
SECRET_FILE_PATH = Path('secrets', 'discord bot token.txt')
TOKEN = None
MY_GUILD = os.getenv('DISCORD_GUILD')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

try:
    with open(SECRET_FILE_PATH) as file1:
        TOKEN = file1.readline()
except FileNotFoundError:
    TOKEN = os.environ['BOT_TOKEN']

# for local testing purposes
ADMIN_ONLY = False
test_file = None
try:
    test_file = open(Path("testing", "test_file.txt"))
    ADMIN_ONLY = True
except FileNotFoundError:
    ADMIN_ONLY = False
finally:
    if test_file:
        test_file.close()

# GLOBAL VARIABLES oh no im using global variables oh noo
guild_list = []
server_instance_list = []

cooldown_last_reset_time = time.time()
something_sent = True
recently_sent_messages = 0

# CONSTANTS
FOLLOWING_CHARACTERS = ['', ' ', '.', '?', '!', '"', "'"]
PRECEDING_CHARACTERS = [' ', '.', ':', '"', "'"]
ENDING_CHARACTERS = ['.', '?', '!', ':', 'bruh']
POSSESSIVE_PERSONAL_PRONOUN_LIST = ['im', "i'm", 'i am', 'I’m']
AMONG_US_TRIGGERS = ["among us", 'amongus', 'amogus', 'among sus', 'sussy', 'sus', 'baka']
THICK_OF_IT_TRIGGERS = ['ksi', 'thick of it', 'from the screen', 'to the ring', 'this is how the story goes']
AMONG_US_RESPONSES = ['https://tenor.com/view/amongus-gif-4415597529176870237',
                      'https://tenor.com/view/aacj-among-us-pizza-what-a-nice-pizza-gif-25200137',
                      'https://tenor.com/view/among-us-among-us-character-among-us-character-sents-flying-amogus-among-us-character-gets-thrown-gif-27025407'
                      'https://tenor.com/view/among-us-sus-amogus-the-voices-run-gif-24999157',
                      'https://tenor.com/view/among-us-cry-about-it-go-cry-about-it-sussy-sussy-imposter-gif-23140749']
CRAZY_RESPONSES = ["https://tenor.com/view/crazy-rubber-room-gif-10524477174166992043", """Crazy? I was crazy once.
                   They locked me in a room. A rubber room. A rubber room full of rats. And rats make me crazy.""",
                   """CRAZY?/??? I WAS CRAYZY ONCE?!?!1?!/?!?!!  THE YLCOKED MEG INA R AIROOROOM A RUBEBER ROOMA DN RUBBER MAKES
                   ME HCRANTZZyaYY""", "crazy? i was crazy once", "rats make me rubber"]
BAITS = ["what", "What", 'when', 'When', 'who', 'Who']
PRONOUNS = ['he', 'she', 'they']
TYPOS = ['SOTP', 'HWO', 'HLEP', 'imdeed', 'DYHINF', 'EHLP', 'liek', 'sitpoo', 'cehap', 'parnets', 'paretns', 'vioolni', 'sotfp', 'tahnkss', 'sucj', 'kmagine', 'heah', 'murser',
         'go dish', 'gof ish', 'g ofish', 'go fesh', 'go fsih', 'gi fish', 'gi fsih', 'go fsh', 'ho fish', 'go fihs', 'go fidh']
SWEARING_RESPONSES = ["Bro chill out dude.", "Let's calm down bro.", "Dude swearing is not cool.", "Guys lets find our happy place.",
                      "Watch your fucking language.", "That's a no-no word"]
KYS_RESPONSES = ["Let's be nice to each other ok.", "Let's all calm down guys.", "Guys lets find our happy place."]
SPEECH_BUBBLES = ['https://cdn.discordapp.com/attachments/1087868146288951389/1285450220741726278/togif.gif?ex=6722580f&is=6721068f&hm=eae8f4b73914afeef14e09b34df7eca35865ce5b6ee517558325fba6c5fcf0fb&',
                  'https://tenor.com/view/manlet-speech-bubble-bobcat-gif-25293164',
                  'https://tenor.com/view/discord-speech-bubble-small-guy-with-a-sword-speech-bubble-gif-2288421216251484021',
                  'https://media.discordapp.net/attachments/864628022102196265/974940700829437962/CA6B0BDC-78F5-4A56-ACE9-57D38B124F72.gif?ex=67228d08&is=67213b88&hm=ff7d156f5df6ee2c232c779eddfbfa641ab21d34476d4ac7339f350630a215f6&',
                  'https://cdn.discordapp.com/attachments/1036326207748325508/1098787163832864798/attachment.gif?ex=6722390a&is=6720e78a&hm=21d46263dea96c58822e61aac2919ad86ed9893a1240215597b75e2103e50ab2&',
                  'https://cdn.discordapp.com/attachments/1168677640253739039/1266269430757720176/togif.gif?ex=6722700e&is=67211e8e&hm=5c2e4881d933a2b4f410ef091d17c47816c03d5c9b63160c82aedca0cd4de555&',
                  'https://media.discordapp.net/attachments/953024451132407838/1062386011348414485/attachment-1.gif?ex=67224a93&is=6720f913&hm=71741513abd15a477e945630c388f5bc93fc91e4882838211f86eb402666fe50&',
                  'https://cdn.discordapp.com/attachments/1154140211157143552/1252355713083244584/ummmm.gif?ex=672293a5&is=67214225&hm=3dd9e871971596e7398a2e4d6a0718ba431f7dfff266ac54643c43df6b0209b1&',
                  'https://cdn.discordapp.com/attachments/741568423485767725/1268793140609810544/attachment-12.gif?ex=672263f1&is=67211271&hm=b1fd6b96e8b6009bb814c081c51810f56461924e792ec20e2fa5f7d08bead232&',
                  'https://media.discordapp.net/attachments/920152531995353128/1014407060819021844/attachment.gif?width=322&height=430&ex=67226d72&is=67211bf2&hm=d85b77f8168891c001e0e70b8dde760ad6c2769eb8c90f9cbe93e54be5392258&',
                  'https://media.discordapp.net/attachments/1160028122205401138/1301791814751096885/watermark.gif?ex=676462da&is=6763115a&hm=e3961936b46d361a6e4ee485cb11e770ca020e41f32a332b2bc4885c9e4a2c6c&=&width=1440&height=623',
                  'https://media.discordapp.net/attachments/1036326207748325508/1098787163832864798/attachment.gif?ex=6764ccca&is=67637b4a&hm=773ef5c0cc72752926e2c696f598154db794db496a6b099bfac02fa679647fc4&=&width=640&height=647',
                  'https://media.discordapp.net/attachments/820388124001173516/1111589025573261404/attachment-9-1.gif?ex=67649234&is=676340b4&hm=c44ab4beb02a7dc12700ca1c86ae2d1e8e8903ce8a759af53fdf06cb6c4e32e1&=&width=480&height=535',
                  'https://media.discordapp.net/attachments/1024047864864833647/1084661598775431178/unknown-1-1.gif?ex=6764d3d5&is=67638255&hm=fa8c4d0b2d3426e14adaa6ed2da10014519fc6c5263ff9f73f33975ee7575b2e&=&width=513&height=700']
NEGATIVE_EMOJIS = ['🤥', '🩴', '🎐', '🚮', '👹', '⛽', '🤓']
FUNNY_EMOJIS = ['😹', '😂', '🤣']

JADEN_18TH_BIRTHDAY_UNIX_TIME = 1709359200
JAMES_18TH_BIRTHDAY_UNIX_TIME = 1707033600
ARAVIND_18TH_BIRTHDAY_UNIX_TIME = 1771135200
KUSH_BIRTHDAY_UNIX_TIME = 1137852000
EPIC_MUSHROOM_ID = 456943500249006108
PALIOPOLIS_ID = 873412148880089102
KUSH_ID = 873411125633491024
JADEN_ID = 762393738676404224

IMAGES = list(Path("images").iterdir())
VIDEOS = list(Path("videos").iterdir())

COOLDOWN_LENGTH = 35
COOLDOWN_LIMIT = 8 # how many messages that can be sent per COOLDOWN_LENGTH seconds

class ServerSpecificInstance:

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

    def reset_cooldown(self, force=False) -> None:
        current_time = int(time.time())
        if force or current_time - self.cd_last_reset_time >= COOLDOWN_LENGTH:
            self.cd_last_reset_time = current_time
            self.recently_sent_messages = 0

    def time_since_cd_last_reset_time(self) -> int:
        current_time = int(time.time())
        return current_time - self.cd_last_reset_time

    def get_comedians(self) -> list[str]:
        return self.comedians

    async def send_message(self, reference, text, bypass_cd=False, file_path=None) -> None:
        file = None
        if file_path:
            file = discord.File(file_path)

        if self.on_cooldown():
            logging.info(f'On cooldown. Message withheld: {text}')

        if bypass_cd or not (self.something_sent or self.on_cooldown()):
            if not bypass_cd:
                self.something_sent = True
                self.recently_sent_messages += 1

            if file:
                await reference.channel.send(text, file=file)
            else:
                await reference.channel.send(text)

            total_triggers_file = None

            try:
                total_triggers_file = Path("trackers", "total_triggers.txt").open('r+')
                current_count = int(total_triggers_file.readline())
                total_triggers_file.seek(0)
                total_triggers_file.write(f"{current_count + 1}")
            finally:
                if total_triggers_file:
                    total_triggers_file.close()

            json_utils.update_user_database(reference.author.name)
            
        if file:
            file.close()

    async def reply_to_message(self, reference, text, bypass_cd=False, ping=True) -> None:
        if self.on_cooldown():
            logging.info(f'On cooldown. Message withheld: {text}')

        if bypass_cd or not (self.something_sent or self.on_cooldown()):
            if not bypass_cd:
                self.something_sent = True
                self.recently_sent_messages += 1

            if ping:
                await reference.reply(text)
            else:
                await reference.reply(text, allowed_mentions=discord.AllowedMentions.none())

            total_triggers_file = None

            try:
                total_triggers_file = Path("trackers", "total_triggers.txt").open('r+')
                current_count = int(total_triggers_file.readline())
                total_triggers_file.seek(0)
                total_triggers_file.write(f"{current_count + 1}")
            finally:
                if total_triggers_file:
                    total_triggers_file.close()

            json_utils.update_user_database(reference.author.name)

def random_range(start: int, stop: int) -> int:
    """random.randrange but its inclusive so i don't keep forgetting the original function has an exclusive endpoint because i have fucking dementia"""
    return random.randrange(start, stop + 1)

def hours_since(current_time: int, considered_time: int) -> int:
    seconds_since = int(current_time - considered_time)
    return seconds_since // 3600

def days_and_hours_since(current_time: int, considered_time: int) -> tuple:
    hours = hours_since(current_time, considered_time)
    days = hours // 24
    hours = hours - days * 24

    return(days, hours)

with open(Path('revenge.txt'), 'r') as lyrics:
    REVENGE_LYRICS = []

    for line in lyrics:
        REVENGE_LYRICS.append(strip_punctuation(line.strip().lower()))

@client.event
async def on_ready():
    global guild_list

    for g in client.guilds:
        # logging.info(len(client.guilds))
        logging.info(f'connected to {g.name}, server id: {g.id}')

    # editing global variables
    guild_list = list(client.guilds)

@client.event
async def on_message(message):
    global server_instance_list, guild_list

    referred_message = None
    lowercase_message_content = message.content.lower()

    current_time = int(time.time())
    current_guild = message.guild

    server_instance = None
    for instance in server_instance_list:
        if instance.get_server() == current_guild:
            server_instance = instance
    if not server_instance:
        server_instance_list.append(ServerSpecificInstance(current_guild))
        server_instance = server_instance_list[-1]

    current_display_name = server_instance.get_nickname()

    # Makes it so it doesn't reply to itself
    if message.author == client.user:
        return

    if message.reference is not None:
        referred_message = await message.channel.fetch_message(message.reference.message_id)

    # Resets the cooldown every COOLDOWN_LENGTH seconds and message cache
    server_instance.reset_cooldown()
    server_instance.clear_message_cache()

    # Enables admin commands
    is_admin = message.author.id == EPIC_MUSHROOM_ID

    # Makes the bot only respond if ADMIN_ONLY is enabled
    if ADMIN_ONLY and not is_admin:
        print("Non-admin message detected")
        return

    # Triggers start here
    index_of_im = find_index_after_word(lowercase_message_content, POSSESSIVE_PERSONAL_PRONOUN_LIST)
    index_of_pronoun = find_index_after_word(lowercase_message_content, PRONOUNS)

    if find_isolated_word_bool(message.content, REVENGE_LYRICS):
        try:
            lyric_found = find_word(message.content, REVENGE_LYRICS)
            await server_instance.reply_to_message(message, REVENGE_LYRICS[REVENGE_LYRICS.index(lyric_found) + 1], bypass_cd=True)
        except IndexError:
            pass
        except ValueError:
            pass

    if find_isolated_word_bool(message.content, ['allegro barbaro']):
        await message.add_reaction('🖕')

    if find_isolated_word_bool(message.content, POSSESSIVE_PERSONAL_PRONOUN_LIST):
        interpreted_name = strip_punctuation(message.content[index_of_im:])
        if len(interpreted_name) > 0 and random_range(1, 1) == 1:
            await server_instance.send_message(message, f"Hi {interpreted_name}, I'm {random.choice(server_instance.get_comedians())}!")

    if find_isolated_word_bool(message.content, TYPOS) and random_range(1, 1) == 1:
        await server_instance.reply_to_message(message, "https://www.wikihow.com/Type")

    if "crazy" in lowercase_message_content.lower():
        await server_instance.reply_to_message(message, f"{random.choice(CRAZY_RESPONSES)}")

    if (message.author.id == PALIOPOLIS_ID or message.author.id == JADEN_ID) and random_range(1, 1000) == 1:
        await message.add_reaction(random.choice(NEGATIVE_EMOJIS))

    if referred_message and referred_message.author == client.user:
        if referred_message.content.lower() == "who":
            if strip_punctuation(lowercase_message_content.lower()) != "asked":
                await server_instance.reply_to_message(message, "asked :rofl::rofl:", True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))
        elif referred_message.content.lower() == "what":
            if strip_punctuation(lowercase_message_content.lower()) != "ever":
                await server_instance.reply_to_message(message, "ever :joy::joy:", True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))
        elif referred_message.content.lower() == "when":
            if strip_punctuation(lowercase_message_content.lower()) != "did i ask" and strip_punctuation(lowercase_message_content.lower()) != "did you ask":
                await server_instance.reply_to_message(message, "did I ask :joy::joy::rofl:", True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))


    if find_word_bool(lowercase_message_content, THICK_OF_IT_TRIGGERS):
        await server_instance.reply_to_message(message, "https://www.youtube.com/watch?v=At8v_Yc044Y")

    if find_word_bool(lowercase_message_content, ['skibidi', 'hawk tuah', 'jelqing', 'lv 100 gyatt']):
        await server_instance.send_message(message, "no", True)

    if "FUCK" in message.content or "SHIT" in message.content or lowercase_message_content == "shut the fuck up":
        await server_instance.reply_to_message(message, f"{random.choice(SWEARING_RESPONSES)}")

    if find_isolated_word_bool(message.content, ['kys', 'kill yourself', 'kill your self']):
        await server_instance.send_message(message, f"{random.choice(KYS_RESPONSES)}")
    
    if "what is the time" in lowercase_message_content:
        await server_instance.reply_to_message(message, f"It is <t:{current_time}:f>")

    if "what is the unix time" in lowercase_message_content:
        await server_instance.reply_to_message(message, f"The unix time is {current_time}\nformatted, that's <t:{current_time}:f>")

    if find_word_index(lowercase_message_content, ['jaden', 'jedwin']) > -1:
        time_tuple = days_and_hours_since(current_time, JADEN_18TH_BIRTHDAY_UNIX_TIME)
        await server_instance.reply_to_message(message, f"Jaden has been stalking minors for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_word_index(lowercase_message_content, ['jame', 'james', 'cheung']) > -1:
        time_tuple = days_and_hours_since(current_time, JAMES_18TH_BIRTHDAY_UNIX_TIME)
        await server_instance.reply_to_message(message, f"James has been getting high for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_word_index(lowercase_message_content, ['aravind', 'arvind']) > -1:
        time_tuple = days_and_hours_since(ARAVIND_18TH_BIRTHDAY_UNIX_TIME, current_time)
        await server_instance.reply_to_message(message, f"Aravind will be legal in {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_index_after_word(lowercase_message_content, ['kush', 'hush b', 'hush']) > -1:
        time_tuple = days_and_hours_since(current_time, KUSH_BIRTHDAY_UNIX_TIME)
        await server_instance.reply_to_message(message, f"Kush has been consuming brainrot for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_index_after_word(lowercase_message_content, ['kayshav']) > -1:
        time_tuple = days_and_hours_since(current_time, KUSH_BIRTHDAY_UNIX_TIME)
        await server_instance.reply_to_message(message, f"Kayshav has been consuming brainrot for {time_tuple[0]} days and {time_tuple[1]} hours")

    if "totaltriggers" in lowercase_message_content:
        total_triggers_file = None
        current_count = None

        try:
            total_triggers_file = Path("trackers", "total_triggers.txt").open('r')
            current_count = int(total_triggers_file.readline())
        finally:
            if total_triggers_file:
                total_triggers_file.close()

        await server_instance.reply_to_message(message, f"{current_count} triggers", bypass_cd=True)

    if "debuggeneral" in lowercase_message_content:
        await server_instance.reply_to_message(message, f"I am in {len(list(client.guilds))} servers")
        await message.channel.send(f"{len(server_instance.get_comedians())} is the length of the comedians list")
        await message.channel.send(f"{len(guild_list)} is the length of the guild_list list")
        try:
            await message.channel.send(f"The name of this guild is {current_guild.name} and my nick is {current_display_name}")
        except AttributeError:
            await message.channel.send(f"I am not in a guild. However, my display name is {current_display_name}")

    if "debugcooldown" in lowercase_message_content:
        if server_instance.on_cooldown():
            await server_instance.reply_to_message(message, f"I am on cooldown. Stop freaking spamming bro. (cooldown length is {COOLDOWN_LENGTH}, "
                                        f"max number of messages able to be sent per cooldown reset period is {COOLDOWN_LIMIT}, "
                                            f"{server_instance.recently_sent_messages+1} messages were sent during this period)", True)
        else:
            await server_instance.reply_to_message(message,
                                   f"I am not on cooldown. (cooldown length is {COOLDOWN_LENGTH}, "
                                   f"max number of messages able to be sent per cooldown reset is {COOLDOWN_LIMIT}, "
                                   f"{server_instance.recently_sent_messages+1} messages were sent during this period)",
                                   True)

    if find_word_bool(message.content, ['resetcd']):
        if is_admin:
            await server_instance.reply_to_message(message, 'Reset cooldown', bypass_cd=True)
            server_instance.reset_cooldown(force=True)
        else:
            await server_instance.reply_to_message(message, 'Nah I don\'t feel like it', bypass_cd=True)

    if "HALOOLY BRIKTAY" == message.content:
        await server_instance.reply_to_message(message, message.content, bypass_cd=True)

    if find_word_bool(message.content, ['ur mom', 'your mom', 'ur dad', 'ur gae', 'ur gay', "you're gay"]):
        await message.add_reaction(random.choice(FUNNY_EMOJIS))

    if find_isolated_word_bool(lowercase_message_content, AMONG_US_TRIGGERS):
        await server_instance.send_message(message, random.choice(AMONG_US_RESPONSES))

    if find_word_bool(message.content, ['mind blowing', 'mindblowing', ":exploding_head:", "🤯"]):
        image_path = random.choice(IMAGES)
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            await server_instance.send_message(message, "file wasn't found (how the fuck did this happen bro)")

    if find_isolated_word_bool(message.content, ['persona', 'specialist']):
        video_path = random.choice(VIDEOS)
        try:
            await server_instance.send_message(message, "** **", file_path=video_path)
        except FileNotFoundError:
            await server_instance.send_message(message, "file wasn't found (how the fuck did this happen bro)")

    if find_word_bool(message.content, ['testingmultmessages', 'testmultmessages']):
        await server_instance.send_message(message, 'test')
        await server_instance.send_message(message, 'test2', bypass_cd=True)

    if find_isolated_word_bool(message.content, ['speech bubble', 'speechbubble']) and referred_message:
        if not message.mentions:
            await server_instance.reply_to_message(referred_message, random.choice(SPEECH_BUBBLES))
        else:
            await server_instance.reply_to_message(referred_message, random.choice(SPEECH_BUBBLES), ping=False)

    if find_isolated_word_bool(message.content, ['brawl stars', 'hop on brawl']):
        await server_instance.reply_to_message(message, 'https://tenor.com/view/wanna-play-brawl-stars-lonely-no-one-plays-brawl-stars-lmoa-gif-23811622')

    if find_isolated_word_bool(message.content, ['sigma']):
        await server_instance.reply_to_message(message, 'https://tenor.com/view/not-a-sigma-sorry-you-are-not-a-sigma-sorry-you%27re-not-a-sigma-you-aren%27t-a-sigma-you-are-not-sigma-gif-337838532227751572')

    if find_isolated_word_bool(message.content, ['uwu', 'owo', ':3']):
        await server_instance.reply_to_message(message, 'https://tenor.com/view/kekw-gif-21672467')

    if find_isolated_word_bool(message.content, ['can i', 'can we']):
        index_can = find_index_after_word(message.content, ['can i', 'can we'])
        interpreted_text = strip_punctuation(message.content[index_can:])
        if len(interpreted_text) > 0:
            await server_instance.send_message(message, f"idk can you {interpreted_text}")

    if random_range(1, 888) == 1:
        await server_instance.send_message(message, '🫠 (this message has a 1/888 chance to appear)', bypass_cd=True)

    if random_range(1, 6666) == 1:
        await server_instance.send_message(message, '🐺 (this message has a 1/6,666 chance to appear)', bypass_cd=True)

    if find_word_bool(message.content, ['flip a coin']):
        if random_range(1, 2) == 1:
            await server_instance.send_message(message, 'Heads', bypass_cd=True)
        else:
            await server_instance.send_message(message, 'Tails', bypass_cd=True)

    if find_word_bool(message.content, ['roll a die', 'roll a dice', 'diceroll']):
        await server_instance.send_message(message, random_range(1, 6), bypass_cd=True)

    if find_word_bool(message.content, ['roll a d20']):
        await server_instance.send_message(message, random_range(1, 20), bypass_cd=True)

    if find_word_bool(message.content, ['what is my name']):
        await server_instance.reply_to_message(message, f"{message.author.display_name} *({message.author.name})*")

    if find_word_bool(message.content, ['fortnite battle']):
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
        await server_instance.send_message(message, fortnite_battle_pass)

    if find_word_bool(message.content, ['🐟', '🎣', '🐠', 'asdfghjkl', 'go fish', 'गो फिश', 'go gamble', 'jobless behavior', 'le fishe',
                                        'quiero comer pescado', 'lets go gambling', 'let\'s go gambling',
                                        '.fish', 'let’s go gambling', '去钓鱼', '><>', '<><', '2+2', 'godfisa',
                                        'zxcvbnm', 'qwertyuiop']):
        if random_range(1, 750) == 1:
            jumpscare = await message.channel.send('https://tenor.com/view/oceanmam-fnaf-jumpscare-gif-22911379')
            await asyncio.sleep(0.27)
            await jumpscare.delete()
            await asyncio.sleep(0.5)

        try:
            await server_instance.reply_to_message(message, f'{'[TESTING ONLY] ' if not json_utils.FISHING_ENABLED else ''}' +
                                                            f'{json_utils.fish_event(message.author.name)}',
                                                   bypass_cd=True)
        except json_utils.OnFishingCooldownError:
            await server_instance.reply_to_message(message, f"You're on fishing cooldown (" +
                                                            f"{json_utils.FISHING_COOLDOWN - (current_time - json_utils.get_user_last_fish_time(message.author.name))} seconds until you can fish again)", bypass_cd=True)

        except json_utils.MaintenanceError:
            await server_instance.reply_to_message(message, f'fishing is currently disabled, go do college apps in the meantime or some shit')

    if message.content.startswith('admin:') and len(message.content) > 6:
        if is_admin:
            if message.content.startswith('admin:fishtest'):
                parts = message.content.split(' ')
                for l in range(min(int(parts[-1] if len(parts) > 1 else 1), 12)):
                    try:
                        await server_instance.send_message(message, json_utils.fish_event('test_user', bypass_fish_cd=True),
                                                               bypass_cd=True)
                    except json_utils.OnFishingCooldownError:
                        await server_instance.reply_to_message(message, f"You're on fishing cooldown (" +
                                                                        f"{json_utils.FISHING_COOLDOWN - (current_time - json_utils.get_user_last_fish_time(message.author.name))}"
                                                                        f"seconds until you can fish again)", bypass_cd=True)

            elif message.content.startswith('admin:switch'):
                if json_utils.switch_fishing():
                    await server_instance.send_message(message, 'Fishing sim turned on. let the brainrot begin')
                else:
                    await server_instance.send_message(message, 'Fishing sim turned off. go outside everyone')

            elif message.content.startswith('admin:shutdown'):
                await server_instance.send_message(message, "Shutting down bot :(", bypass_cd=True)
                exit(2)

        else:
            await server_instance.reply_to_message(message, 'you can\'t do that (reference to 1984 by George Orwell)',
                                                   bypass_cd=True)

    if is_admin or json_utils.FISHING_ENABLED:
        if find_word_bool(message.content, ['show profile', 'show pf']):
            username_temp = message.author.name
            if lowercase_message_content.startswith('show profile '):
                parts = message.content.split(' ')
                username_temp = parts[-1]

            embed = discord.Embed(title=f'{username_temp}\'s Profile', description=json_utils.profile_to_string(username_temp))
            await message.channel.send(embed=embed)
            # await server_instance.send_message(message, json_utils.profile_to_string(username_temp), bypass_cd=True)

        if find_word_bool(message.content, ['show leaderboard', 'show lb']):
            embed = discord.Embed(title='Leaderboard', description=json_utils.leaderboard_string())
            await message.channel.send(embed=embed)
            # await server_instance.send_message(message, json_utils.leaderboard_string(), bypass_cd=True)

        if find_word_bool(message.content, ['luck lb', 'rng lb', 'show luck']):
            embed = discord.Embed(title='RNG Leaderboard', description=json_utils.leaderboard_string(sort_by_luck=True))
            await message.channel.send(embed=embed)

        if find_word_bool(message.content, ['all fish', 'global stats', 'global fish', 'all stats', 'combined profiles', 'combined joblessness',
                                            'global joblessness', 'how jobless is everyone', '.allfish']):
            embed = discord.Embed(title='Universal Stats', description=json_utils.universal_profile_to_string())
            await message.channel.send(embed=embed)
            # await server_instance.send_message(message, json_utils.universal_profile_to_string(), bypass_cd=True)

    if find_word_bool(message.content, ['catchjonklerfishdebug']):
        await server_instance.send_message(message, "that doesn't work anymore dumbass",
                                           bypass_cd=True)

    if message.content.startswith('!spam '):
        parts = message.content.split(' ')
        times = int(parts[1])
        kush = await client.fetch_user(KUSH_ID)

        for i in range(times):
            if len(parts) >= 3:
                await kush.send(f'{parts[2]}')
            else:
                await kush.send('Hi')

    if find_word_bool(message.content, ['embedtestingthing']):
        embed = discord.Embed(description='Hello\nthis\nis\nsupposed\nto\nbe\na\ndescription')
        await message.channel.send(embed=embed)

    if random_range(1, 210) == 1:
        await server_instance.reply_to_message(message, f"{random.choice(BAITS)}", ping=False)
    elif index_of_pronoun > -1 and random_range(1, 27) == 1:
        await server_instance.reply_to_message(message, f"{random.choice(BAITS[4:])}", ping=False)

if __name__ == '__main__':
    user_input = None
    while user_input != "exit":
        user_input = input("shell command: ")

        if user_input == "exit":
            break

        else:
            try:
                command = user_input.strip().lower().split(' ')
                output = subprocess.run(command, capture_output=True, text=True)
                print(output.stdout)

            except Exception as err:
                print(f'exception: {err}')

    client.run(TOKEN)