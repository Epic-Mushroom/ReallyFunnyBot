import discord, os, random, datetime, time, logging, sys, fish_utils, backup_utils, asyncio, subprocess, shop_utils
from pathlib import Path
from string_utils import *
from discord.ext import tasks

# Globals
server_instance_list = []

# Constants
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
KYS_RESPONSES = ["Let's be nice to each other ok.", "Let's all calm down guys.",
                         "Guys lets find our happy place."]
TYPOS = ['SOTP', 'HWO', 'HLEP', 'imdeed', 'DYHINF', 'EHLP', 'liek', 'sitpoo', 'cehap', 'parnets', 'paretns', 'vioolni', 'sotfp', 'tahnkss', 'sucj', 'kmagine', 'heah', 'murser',
         'go dish', 'gof ish', 'g ofish', 'go fesh', 'go fsih', 'gi fish', 'gi fsih', 'go fsh', 'ho fish', 'go fihs', 'go fidh']
SWEARING_RESPONSES = ["Bro chill out dude.", "Let's calm down bro.", "Dude swearing is not cool.", "Guys lets find our happy place.",
                      "Watch your fucking language.", "That's a no-no word"]
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

GENERAL_CHANNEL_ID_1 = 1309380397410291715
GENERAL_CHANNEL_ID_2 = 1096685257891250228
GENERAL_CHANNEL_ID_3 = 964941621110120541

COOLDOWN_LENGTH = 10
COOLDOWN_LIMIT = 4 # how many messages that can be sent per COOLDOWN_LENGTH seconds

# Directory and logging setup
script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# For local testing purposes; the 'testing' directory should only be available on local
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

# Token and commands guild setup
SECRET_FILE_PATH = Path('secrets', 'discord bot token.txt')
TOKEN = None
MY_GUILD = 964941621110120538

try:
    with open(SECRET_FILE_PATH) as file1:
        TOKEN = file1.readline()
except FileNotFoundError:
    TOKEN = os.environ['BOT_TOKEN']

COMMANDS_GUILD = None
if ADMIN_ONLY:
    COMMANDS_GUILD = discord.Object(id=MY_GUILD)

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

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

        self.lockdown = 0 # unix time when lockdown expires

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

    async def send_message(self, reference, text, bypass_cd=False, file_path=None, fishing=False) -> None:
        # prevents message length from going over 2000
        if len(str(text)) > 1990:
            text = "[*some parts of this message were removed because of discord's character limit*]\n" + text[-1800:]

        file = None
        if file_path:
            file = discord.File(file_path)

        if self.on_cooldown():
            logging.info(f'On cooldown. Message withheld: {text}')

        if self.on_lockdown() and not fishing:
            logging.info(f'On lockdown. Message withheld: {text}')
            return

        if bypass_cd or not (self.something_sent or self.on_cooldown()):
            self.something_sent = True

            if not bypass_cd:
                self.recently_sent_messages += 1

            await reference.channel.send(text, file=file)

            total_triggers_file = None

            try:
                total_triggers_file = Path("trackers", "total_triggers.txt").open('r+')
                current_count = int(total_triggers_file.readline())
                total_triggers_file.seek(0)
                total_triggers_file.write(f"{current_count + 1}")
            finally:
                if total_triggers_file:
                    total_triggers_file.close()

            fish_utils.update_user_database(reference.author.name)
            
        if file:
            file.close()

    async def reply_to_message(self, reference, text, bypass_cd=False, ping=True, file_path=None, fishing=False) -> None:
        if len(str(text)) > 1990:
            text = "[*some parts of this message were removed because of discord's character limit*]" + text[-1800:]

        file = None
        if file_path:
            file = discord.File(file_path)

        if self.on_cooldown():
            logging.info(f'On cooldown. Message withheld: {text}')

        if self.on_lockdown() and not fishing:
            logging.info(f'On lockdown. Message withheld: {text}')
            return

        if bypass_cd or not (self.something_sent or self.on_cooldown()):
            self.something_sent = True

            if not bypass_cd:
                self.recently_sent_messages += 1

            if ping:
                await reference.reply(text, file=file)
            else:
                await reference.reply(text, file=file, allowed_mentions=discord.AllowedMentions.none())

            total_triggers_file = None

            try:
                total_triggers_file = Path("trackers", "total_triggers.txt").open('r+')
                current_count = int(total_triggers_file.readline())
                total_triggers_file.seek(0)
                total_triggers_file.write(f"{current_count + 1}")
            finally:
                if total_triggers_file:
                    total_triggers_file.close()

            fish_utils.update_user_database(reference.author.name)

        if file:
            file.close()

    def set_lockdown(self, seconds) -> int:
        self.lockdown = int(time.time()) + seconds
        return self.lockdown

    def on_lockdown(self):
        return int(time.time()) < self.lockdown

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

# sends a reminder to renew the server in my dms
reminder_time = datetime.time(hour=13, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=-8)))

@tasks.loop(time=reminder_time)
async def reminder():
    me = await client.fetch_user(EPIC_MUSHROOM_ID)
    await me.send('@everyone renew server')

@client.event
async def on_ready():# syncs commands
    if ADMIN_ONLY:
        await tree.sync(guild=COMMANDS_GUILD)
    else:
        await tree.sync()

    reminder.start()

    logging.info(f'connected to {len(client.guilds)} servers')
    # for g in client.guilds:
        # logging.info(f'connected to {g.name}, server id: {g.id}')

@client.event
async def on_message(message):
    async def send(content='** **', reply=False, bypass_cd=False, ping=True, file_path=None, fishing=False):
        if reply:
            await server_instance.reply_to_message(message, content, bypass_cd=bypass_cd, file_path=file_path, ping=ping, fishing=fishing)
        else:
            await server_instance.send_message(message, content, bypass_cd=bypass_cd, file_path=file_path, fishing=fishing)

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

    # Makes the bot only respond in dms/my server if ADMIN_ONLY is enabled
    can_proceed = not ADMIN_ONLY or (is_admin and (server_instance.server_name is None or server_instance.get_server().id == MY_GUILD))
    if not can_proceed:
        print("Non-admin message detected while in testing mode")
        return

    # Triggers start here
    index_of_im = find_index_after_word(lowercase_message_content, POSSESSIVE_PERSONAL_PRONOUN_LIST)
    index_of_pronoun = find_index_after_word(lowercase_message_content, PRONOUNS)

    if any(lowercase_message_content.strip().startswith(lyric) for lyric in REVENGE_LYRICS):
        try:
            lyric_found = find_word(message.content, REVENGE_LYRICS)
            await server_instance.reply_to_message(message, REVENGE_LYRICS[REVENGE_LYRICS.index(lyric_found) + 1])
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
        await send("https://www.wikihow.com/Type", reply=True)

    if "crazy" in lowercase_message_content.lower():
        await send(f"{random.choice(CRAZY_RESPONSES)}", reply=True)

    if (message.author.id == PALIOPOLIS_ID or message.author.id == JADEN_ID) and random_range(1, 1000) == 1:
        await message.add_reaction(random.choice(NEGATIVE_EMOJIS))

    if referred_message and referred_message.author == client.user:
        if referred_message.content.lower() == "who":
            if strip_punctuation(lowercase_message_content.lower()) != "asked":
                await send("asked :rofl::rofl:", reply=True, bypass_cd=True)
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
        await server_instance.send_message(message, "no")

    if "FUCK" in message.content or "SHIT" in message.content or lowercase_message_content == "shut the fuck up":
        await server_instance.reply_to_message(message, f"{random.choice(SWEARING_RESPONSES)}")

    if find_isolated_word_bool(message.content, ['kys', 'kill yourself', 'kill your self']):
        await server_instance.send_message(message, f"{random.choice(KYS_RESPONSES)}")
    
    if "what is the time" in lowercase_message_content:
        await server_instance.reply_to_message(message, f"It is <t:{current_time}:f>")

    if "what is the unix time" in lowercase_message_content:
        await server_instance.reply_to_message(message, f"The unix time is {current_time}\nformatted, that's <t:{current_time}:f>")

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

    if "cooldownstatus" in lowercase_message_content:
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

    if "HALOOLYH BRIKTAY" == message.content:
        await server_instance.reply_to_message(message, message.content)

    if find_isolated_word_bool(message.content, ['money']):
        temu = """Happy New Year~ Sending you a New Year's card. Come and see my New Year's wishes and accept my invitation.
-For real?
-Sure, only 2 steps to take the gift and help me get mine!
https://temu.com/s/Ut2tvFcWcwAKgdUM"""
        await asyncio.sleep(5)
        await send(temu)

    if find_word_bool(message.content, ['ur mom', 'your mom', 'ur dad', 'ur gae', 'ur gay', "you're gay"]):
        await message.add_reaction(random.choice(FUNNY_EMOJIS))

    if find_isolated_word_bool(lowercase_message_content, AMONG_US_TRIGGERS):
        await server_instance.send_message(message, random.choice(AMONG_US_RESPONSES))

    if find_word_bool(message.content, ['mind blowing', 'mindblowing', ":exploding_head:", "🤯"]):
        image_path = Path("images", "emoji483.png")
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if find_word_bool(message.content, ["kachow"]):
        image_path = Path("images", "jedwin", "kachow.png")
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if find_word_bool(message.content, ["slavery"]):
        image_path = Path("images", "jedwin", "Jailed_Jedgar.jpg")
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if find_word_bool(message.content, ["jaden christian edwin"]):
        image_path = random.choice(list(Path("images", "jedwin").iterdir()))
        try:
            await server_instance.send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            print(f"'{str(image_path)} wasn't found'")

    if find_isolated_word_bool(message.content, ['persona', 'specialist']):
        video_path = Path("videos", "p4 specialist compressed.mp4")
        try:
            await server_instance.send_message(message, "** **", file_path=video_path)
        except FileNotFoundError:
            print(f"'{str(video_path)} wasn't found'")

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
        await send('🫠 (this message has a 1/888 chance to appear)', bypass_cd=True)

    if random_range(1, 6666) == 1:
        await send('🐺 (this message has a 1/6,666 chance to appear)', bypass_cd=True)

    if find_word_bool(message.content, ['flip a coin']):
        if random_range(1, 2) == 1:
            await send('Heads', bypass_cd=True)
        else:
            await send('Tails', bypass_cd=True)

    if find_word_bool(message.content, ['roll a die', 'roll a dice', 'diceroll']):
        await send(str(random_range(1, 6)), bypass_cd=True)

    if find_word_bool(message.content, ['roll a d20']):
        await send(str(random_range(1, 20)), bypass_cd=True)

    if find_word_bool(message.content, ['what is my name']):
        await send(f"{message.author.display_name} *({message.author.name})*", reply=True)

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
        await send(fortnite_battle_pass)

    if find_word_bool(message.content, ['🐟', '🎣', '🐠', '🐡', 'asdfghjkl', 'go phish', 'go fish', 'go gamble', 'jobless behavior', 'le fishe',
                                        'quiero comer pescado', 'lets go gambling', 'let\'s go gambling',
                                        '.fish', 'let’s go gambling', '><>', '去钓鱼', '<><', '2+2', 'godfisa',
                                        'zxcvbnm', 'qwertyuiop', 'go ghoti']):
        if random_range(1, 1500) == 1:
            jumpscare = await message.channel.send('https://tenor.com/view/oceanmam-fnaf-jumpscare-gif-22911379')
            await asyncio.sleep(0.31)
            await jumpscare.delete()
            await asyncio.sleep(0.5)

        if not message.channel.id in [GENERAL_CHANNEL_ID_1, GENERAL_CHANNEL_ID_2, GENERAL_CHANNEL_ID_3]:
            try:
                # if ADMIN_ONLY and is_admin:
                #     fish_utils.all_pfs.profile_from_name(message.author.name).last_fish_time = 0

                content = f'{'[TESTING ONLY] ' if not fish_utils.FISHING_ENABLED else ''}{fish_utils.fish_event(message.author.name)}'
                await send(content, reply=True, bypass_cd=True, fishing=True)

            except fish_utils.MaintenanceError:
                await server_instance.reply_to_message(message, f'fishing is currently disabled, go play minecraft in the meantime or some shit', bypass_cd=True, fishing=True)

            fish_utils.all_pfs.write_data()

        elif not find_word_bool(message.content, ['2+2', 'zxcvbnm', 'qwertyuiop', 'asdfghjkl', '🐟', '🎣', '🐠', '🐡', 'jobless behavior']):
            temp_path = Path("images", "no fishing in general.gif")
            await send(reply=True, file_path=temp_path)

    if message.content.startswith('admin:') and len(message.content) > 6:
        if is_admin:
            if message.content.startswith('admin:switch'):
                if fish_utils.switch_fishing():
                    await server_instance.send_message(message, 'Fishing sim turned on. let the brainrot begin', fishing=True)
                else:
                    await server_instance.send_message(message, 'Fishing sim turned off. go outside everyone', fishing=True)

            elif message.content.startswith('admin:shutdown'):
                await server_instance.send_message(message, "Shutting down bot :(", bypass_cd=True)
                exit(2)

            elif message.content.startswith('admin:backup'):
                try:
                    backup_utils.make_backup()
                    await server_instance.reply_to_message(message, 'Backup successful', fishing=True)
                except Exception as e:
                    await server_instance.reply_to_message(message, f'bro you done fucked smth up ({e})')

            elif message.content.startswith('admin:mutebot '):
                parts = message.content.split(' ')
                timeout_length = int(parts[-1])

                lockdown_expiry_time = server_instance.set_lockdown(timeout_length)
                await message.channel.send(f'The bot may not exercise freedom of speech until <t:{lockdown_expiry_time}:f>')

            elif message.content.startswith('admin:unmutebot'):
                server_instance.set_lockdown(-1)
                await message.channel.send('The bot may exercise freedom of speech again')

            elif message.content.startswith('admin:save'):
                fish_utils.all_pfs.write_data()

            elif message.content.startswith('admin:refund'):
                # USE THIS COMMAND WITH CAUTION
                await server_instance.reply_to_message(message, fish_utils._manual_data_changes())
                fish_utils.all_pfs.write_data()

            elif message.content.startswith('admin:give'):
                # ONLY USE THIS IF FISH IS UNFAIRLY LOST/GAINED BECAUSE OF BUGS
                # format: "admin:give "epicmushroom." "God" 3"
                parts = message.content.split('"')
                temp_username = parts[1]
                temp_fish = fish_utils.get_fish_from_name(parts[3])
                try:
                    temp_count = int(parts[4].strip())
                except IndexError:
                    temp_count = 1
                except ValueError:
                    temp_count = 1
                except Exception as e:
                    await server_instance.reply_to_message(message, f"Something went wrong [{e}]", bypass_cd=True)
                    return

                temp_profile = fish_utils.all_pfs.profile_from_name(temp_username)
                if temp_profile is not None and temp_fish is not None:
                    temp_profile.add_fish(temp_fish, temp_count)
                else:
                    await server_instance.reply_to_message(message, "User/fish couldn't be found", bypass_cd=True)
                    return

                await server_instance.reply_to_message(message, f"Gave {temp_count} {temp_fish.name} to {temp_username}\n", bypass_cd=True)
                fish_utils.all_pfs.write_data()

        else:
            await server_instance.reply_to_message(message, 'you can\'t do that (reference to 1984 by George Orwell)',
                                                   bypass_cd=True)

    if is_admin or fish_utils.FISHING_ENABLED:
        if find_word_bool(message.content, ['show profile', 'show pf']):
            username_temp = message.author.name
            if (lowercase_message_content.startswith('show profile ') or
                lowercase_message_content.startswith('show pf ')):
                parts = message.content.split(' ')
                username_temp = parts[-1]

            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}'
                                        f'{username_temp}\'s Profile', description=fish_utils.profile_to_string(username_temp))
            await message.channel.send(embed=embed)

        if find_word_bool(message.content, ['show leaderboard', 'show lb', '.lb']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Leaderboard',
                                  description=fish_utils.leaderboard_string())
            await message.channel.send(embed=embed)
            # await server_instance.send_message(message, fish_utils.leaderboard_string(), bypass_cd=True)


        if find_word_bool(message.content, ['item rng lb', 'old luck lb', 'old rng lb', 'show luck old', '.oldrnglb', '.oldlbrng', '.oldlbluck', '.oldlucklb']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}RNG Leaderboard (by item)',
                                  description=fish_utils.leaderboard_string(sort_by_luck=True))
            await message.channel.send(embed=embed)

        elif find_word_bool(message.content, ['luck lb', 'rng lb', 'show luck', '.rnglb', '.lbrng', '.lbluck', '.lucklb']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}RNG Leaderboard',
                                  description=fish_utils.luck_leaderboard_string())
            await message.channel.send(embed=embed)

        if find_word_bool(message.content, ['all fish', 'global stats', 'global fish', 'all stats', 'combined profiles', 'combined joblessness',
                                            'global joblessness', 'how jobless is everyone', '.allfish']):
            embed = discord.Embed(title=f'{'(Testing Only) ' if not fish_utils.FISHING_ENABLED else ''}Universal Stats',
                                  description=fish_utils.universal_profile_to_string())
            await message.channel.send(embed=embed)
            # await server_instance.send_message(message, fish_utils.universal_profile_to_string(), bypass_cd=True)

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
            await message.channel.send(embed=embed)

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

        if find_word_bool(message.content, ['show manifesto', 'go manifesto']):
            # returns the fishing manifesto factor and percent boost for a given user
            parts = message.content.split(' ')

            pf = fish_utils.all_pfs.profile_from_name(parts[-1])
            if pf is None:
                pf = fish_utils.all_pfs.profile_from_name(message.author.name)
            factor = fish_utils.fishing_manifesto_factor(pf.username)

            if pf:
                await server_instance.reply_to_message(message, f'{pf.username}: '
                                                                f'{fish_utils.factor_to_percent_increase(factor):.1f}% boost on avg (doesn\'t include effects of powerups)',
                                                       bypass_cd=True)
            else:
                await server_instance.reply_to_message(message, "That user (probably) doesn't exist", bypass_cd=True)

    if message.content.startswith('!spam '):
        parts = message.content.split(' ')
        times = int(parts[1])
        kush = await client.fetch_user(KUSH_ID)

        for i in range(times):
            if len(parts) >= 3:
                await kush.send(f'{parts[2]}')
            else:
                await kush.send('Hi')

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

    # if random_range(1, 210) == 1:
    #     await server_instance.reply_to_message(message, f"{random.choice(BAITS)}", ping=False)
    # elif index_of_pronoun > -1 and random_range(1, 27) == 1:
    #     await server_instance.reply_to_message(message, f"{random.choice(BAITS[4:])}", ping=False)

if __name__ == '__main__':
    # print("!!!!TYPE 'exit' TO START THE BOT!!!!")
    #
    # user_input = None
    # while user_input != "exit":
    #     user_input = input("shell command: ")
    #
    #     if user_input == "exit":
    #         break
    #
    #     else:
    #         backup_utils.shell_command(user_input)

    client.run(TOKEN)