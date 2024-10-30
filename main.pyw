import discord, os, random, time, logging, sys
from dotenv import load_dotenv
from pathlib import Path

# SETUP
script_directory = Path(__file__).parent.resolve()
os.chdir(script_directory)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

load_dotenv()

try:
    TOKEN = os.environ['DISCORD_TOKEN']
except KeyError:
    TOKEN = os.getenv('DISCORD_TOKEN')
MY_GUILD = os.getenv('DISCORD_GUILD')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# GLOBAL VARIABLES oh no im using global variables oh noo
comedians = ["Kush", "Kayshav", "dad", "James", "GUYS IF YOU SEE THIS TEXT THE BOT IS BUGGED LOL"] # last element must be debug string
guild_list = []

cooldown_last_reset_time = time.time()
something_sent = True
recently_sent_messages = 0

# CONSTANTS
FOLLOWING_CHARACTERS = ['', ' ', '.', '?', '!', '"', "'"]
PRECEDING_CHARACTERS = [' ', '.', ':', '"', "'"]
ENDING_CHARACTERS = ['.', '?', '!', ':', 'bruh'] # god forbid anyone other than me read this unholy mess of code oh my god
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
TYPOS = ['SOTP', 'HWO', 'HLEP', 'imdeed', 'DYHINF', 'EHLP', 'liek', 'sitpoo', 'cehap', 'parnets', 'paretns', 'vioolni', 'sotfp', 'tahnkss', 'sucj', 'kmagine', 'heah']
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
                  'https://media.discordapp.net/attachments/920152531995353128/1014407060819021844/attachment.gif?width=322&height=430&ex=67226d72&is=67211bf2&hm=d85b77f8168891c001e0e70b8dde760ad6c2769eb8c90f9cbe93e54be5392258&']
NEGATIVE_EMOJIS = ['🤥', '🩴', '🎐', '🚮', '👹', '⛽']
FUNNY_EMOJIS = ['😹', '😂', '🤣']

JADEN_18TH_BIRTHDAY_UNIX_TIME = 1709359200
JAMES_18TH_BIRTHDAY_UNIX_TIME = 1707033600
EPIC_MUSHROOM_ID = 456943500249006108
PALIOPOLIS_ID = 873412148880089102
JADEN_ID = 762393738676404224

USER_TRIGGERS = Path("trackers\\user_triggers.txt")
IMAGES = list(Path("images").iterdir())
VIDEOS = list(Path("videos").iterdir())

COOLDOWN_LENGTH = 30
COOLDOWN_LIMIT = 4 # how many messages that can be sent per COOLDOWN_LENGTH seconds

def on_cooldown():
    global recently_sent_messages, cooldown_last_reset_time

    current_time = int(time.time())
    return recently_sent_messages >= COOLDOWN_LIMIT and (current_time - cooldown_last_reset_time) < COOLDOWN_LENGTH

def hours_since(current_time: int, considered_time: int) -> int:
    seconds_since = int(current_time - considered_time)
    return seconds_since // 3600

def days_and_hours_since(current_time: int, considered_time: int) -> tuple:
    hours = hours_since(current_time, considered_time)
    days = hours // 24
    hours = hours - days * 24

    return(days, hours)

def strip_punctuation(text: str) -> str:
    found_ending_index = find_word_index(text, ENDING_CHARACTERS)

    if found_ending_index > -1:
        text = text[:found_ending_index]

    return text.strip()

def find_word_bool(text: str, words: list[str]) -> bool:
    """Returns False if none of the elements in words are in text, returns True otherwise"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return True

    return False

def find_isolated_word_bool(text: str, words: list[str]) -> bool:
    """Same thing as find_word_bool except it checks to see if the word is 'isolated' (meaning no Scunthorpe problem)"""
    return find_index_after_word(text, words) > -1

def find_word(text: str, words: list[str]) -> str:
    """Returns the first occurrence in text of an element in words, returns None if none of the
        elements in words are in text"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return w

    return None

def find_word_index(text: str, words: list[str]) -> int:
    """Returns the index of the first occurrence in text of an element in words, returns -1 if none of the
    elements in words are in text"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return text.find(w)

    return -1

def find_index_after_word(text: str, words: list[str]) -> int:
    """Yeah"""

    found_word_index = find_word_index(text, words)
    index = found_word_index
    found_word = find_word(text, words)

    # probably the worst code i have ever written in my entire life what the fuck is this dudeee
    if index == -1:
        return -1
    else:
        check_beginning = (index - 1 != -1) and (text[index - 1] in PRECEDING_CHARACTERS)
        check_end = False

        if index - 1 == -1:
            check_beginning = True

        if check_beginning:
            try:
                check_end = text[index + len(found_word)] in FOLLOWING_CHARACTERS
            except IndexError:
                check_end = True

        if check_end:
            return index + len(found_word)
        else:
            return -1

def update_user_database(path: Path, username: str, increment=1) -> None:
    file = path.open('r+')
    split_data = [] # should become formatted like ['username1', 'user1striggers', 'username2', 'user2striggers'...]
    user_found = False
    data_lines = file.readlines()

    file.seek(0)

    for line in data_lines:
        if len(line.split(' ')) == 2:
            split_data += line.split(' ')
        else:
            return

    for i in split_data:
        i = i.strip()

    for i in range(0, len(split_data), 2):
        if split_data[i] == username:
            user_found = True

            triggers = int(split_data[i + 1]) + increment
            data_lines[i // 2] = f'{username} {triggers}\n'
            break

    if not user_found:
        data_lines.append(f'{username} {increment}\n')

    file.writelines(data_lines)
    file.truncate()
    file.close()

async def send_message(reference, text, bypass_cd=False, file_path=None) -> None:
    global something_sent, recently_sent_messages

    file = None
    if file_path:
        file = discord.File(file_path)

    if on_cooldown():
        logging.info(f'On cooldown. Message withheld: {text}')

    if bypass_cd or not (something_sent or on_cooldown()):
        something_sent = True
        recently_sent_messages += 1
        if file:
            await reference.channel.send(text, file=file)
        else:
            await reference.channel.send(text)

        total_triggers_file = None

        try:
            total_triggers_file = Path("trackers\\total_triggers.txt").open('r+')
            current_count = int(total_triggers_file.readline())
            total_triggers_file.seek(0)
            total_triggers_file.write(f"{current_count + 1}")
        finally:
            if total_triggers_file:
                total_triggers_file.close()

        update_user_database(USER_TRIGGERS, reference.author.name)

async def reply_to_message(reference, text, bypass_cd=False, ping=True) -> None:
    global something_sent, recently_sent_messages

    if on_cooldown():
        logging.info(f'On cooldown. Message withheld: {text}')

    if bypass_cd or not (something_sent or on_cooldown()):
        something_sent = True
        recently_sent_messages += 1
        if ping:
            await reference.reply(text)
        else:
            await reference.reply(text, allowed_mentions=discord.AllowedMentions.none())

        total_triggers_file = None

        try:
            total_triggers_file = Path("trackers\\total_triggers.txt").open('r+')
            current_count = int(total_triggers_file.readline())
            total_triggers_file.seek(0)
            total_triggers_file.write(f"{current_count + 1}")
        finally:
            if total_triggers_file:
                total_triggers_file.close()

        update_user_database(USER_TRIGGERS, reference.author.name)



@client.event
async def on_ready():
    global comedians, guild_list

    for g in client.guilds:
        # logging.info(len(client.guilds))
        logging.info(f'connected to {g.name}, server id: {g.id}')

    logging.info(f'{client.user} (nicked as {g.me.display_name}) is now here. brace yourselves.')

    # editing global variables
    guild_list = list(client.guilds)

@client.event
async def on_message(message):
    global comedians, guild_list, cooldown_last_reset_time, something_sent, recently_sent_messages

    referred_message = None
    lowercase_message_content = message.content.lower()

    current_time = int(time.time())
    current_guild = message.guild
    try:
        current_display_name = current_guild.me.display_name
    except AttributeError:
        current_display_name = client.user.name

    comedians[-1] = current_display_name

    # makes it so it doesn't reply to itself
    if message.author == client.user:
        return

    something_sent = False

    if message.reference is not None:
        referred_message = await message.channel.fetch_message(message.reference.message_id)

    # resets the cooldown
    if current_time - cooldown_last_reset_time >= COOLDOWN_LENGTH:
        cooldown_last_reset_time = current_time
        recently_sent_messages = 0

    # Triggers start here
    index_of_im = find_index_after_word(lowercase_message_content, POSSESSIVE_PERSONAL_PRONOUN_LIST)
    index_of_pronoun = find_index_after_word(lowercase_message_content, PRONOUNS)

    if find_isolated_word_bool(message.content, POSSESSIVE_PERSONAL_PRONOUN_LIST):
        interpreted_name = strip_punctuation(message.content[index_of_im:])
        if len(interpreted_name) > 0:
            await send_message(message, f"Hi {interpreted_name}, I'm {random.choice(comedians)}!")

    if find_isolated_word_bool(message.content, TYPOS) and random.randrange(1, 2) == 1:
        await reply_to_message(message, "https://www.wikihow.com/Type")

    if "crazy" in lowercase_message_content.lower():
        await reply_to_message(message, f"{random.choice(CRAZY_RESPONSES)}")

    if (message.author.id == PALIOPOLIS_ID or message.author.id == JADEN_ID) and random.randrange(1, 8) == 1:
        await message.add_reaction(random.choice(NEGATIVE_EMOJIS))

    if referred_message and referred_message.author == client.user:
        if referred_message.content.lower() == "who":
            if strip_punctuation(lowercase_message_content.lower()) != "asked":
                await reply_to_message(message, "asked :rofl::rofl:", True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))
        elif referred_message.content.lower() == "what":
            if strip_punctuation(lowercase_message_content.lower()) != "ever":
                await reply_to_message(message, "ever :joy::joy:", True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))
        elif referred_message.content.lower() == "when":
            if strip_punctuation(lowercase_message_content.lower()) != "did i ask" and strip_punctuation(lowercase_message_content.lower()) != "did you ask":
                await reply_to_message(message, "did I ask :joy::joy::rofl:", True)
            else:
                await message.add_reaction(random.choice(FUNNY_EMOJIS))

    if not something_sent:
        if random.randrange(1, 51) == 1:
            await reply_to_message(message, f"{random.choice(BAITS)}")
        elif index_of_pronoun > -1 and random.randrange(1, 5) == 1:
            await reply_to_message(message, f"{random.choice(BAITS[4:])}")

    if find_word_bool(lowercase_message_content, THICK_OF_IT_TRIGGERS):
        await reply_to_message(message, "https://www.youtube.com/watch?v=At8v_Yc044Y")

    if find_word_bool(lowercase_message_content, ['skibidi']):
        await send_message(message, "no", True)

    if "FUCK" in message.content or "SHIT" in message.content or lowercase_message_content == "shut the fuck up":
        await reply_to_message(message, f"{random.choice(SWEARING_RESPONSES)}")
    
    if "what is the time" in lowercase_message_content:
        await reply_to_message(message, f"It is <t:{current_time}:f>")

    if "what is the unix time" in lowercase_message_content:
        await reply_to_message(message, f"The unix time is {current_time}\nformatted, that's <t:{current_time}:f>")

    if find_word_index(lowercase_message_content, ['jaden', 'jedwin']) > -1:
        time_tuple = days_and_hours_since(current_time, JADEN_18TH_BIRTHDAY_UNIX_TIME)
        await reply_to_message(message, f"Jaden has been stalking minors for {time_tuple[0]} days and {time_tuple[1]} hours")

    if find_word_index(lowercase_message_content, ['jame', 'james', 'cheung']) > -1:
        time_tuple = days_and_hours_since(current_time, JAMES_18TH_BIRTHDAY_UNIX_TIME)
        await reply_to_message(message, f"James has been getting high for {time_tuple[0]} days and {time_tuple[1]} hours")

    if "totaltriggers" in lowercase_message_content:
        total_triggers_file = None
        current_count = None

        try:
            total_triggers_file = Path("trackers\\total_triggers.txt").open('r')
            current_count = int(total_triggers_file.readline())
        finally:
            if total_triggers_file:
                total_triggers_file.close()

        await reply_to_message(message, f'{current_count} times', bypass_cd=True)

    if "debuggeneral" in lowercase_message_content:
        await reply_to_message(message, f"I am in {len(list(client.guilds))} servers")
        await message.channel.send(f"{len(comedians)} is the length of the comedians list")
        await message.channel.send(f"{len(guild_list)} is the length of the guild_list list")
        try:
            await message.channel.send(f"The name of this guild is {current_guild.name} and my nick is {current_display_name}")
        except AttributeError:
            await message.channel.send(f"I am not in a guild. However, my display name is {current_display_name}")
        # await message.channel.send(f"This message does not contribute to the total triggers txt file")

    if "debugcooldown" in lowercase_message_content:
        if on_cooldown():
            await reply_to_message(message, f"I am on cooldown. Stop freaking spamming bro. (cooldown length is {COOLDOWN_LENGTH}, "
                                        f"max number of messages able to be sent per cooldown reset period is {COOLDOWN_LIMIT}, "
                                            f"{recently_sent_messages+1} messages were sent during this period)", True)
        else:
            await reply_to_message(message,
                                   f"I am not on cooldown. (cooldown length is {COOLDOWN_LENGTH}, "
                                   f"max number of messages able to be sent per cooldown reset is {COOLDOWN_LIMIT}, "
                                   f"{recently_sent_messages+1} messages were sent during this period)",
                                   True)

    if "HALOOLY BRIKTAY" == message.content:
        await reply_to_message(message, message.content, True)

    if find_word_bool(message.content, ['ur mom', 'your mom', 'ur dad', 'ur gae', 'ur gay', "you're gay"]):
        await message.add_reaction(random.choice(FUNNY_EMOJIS))

    if find_isolated_word_bool(lowercase_message_content, AMONG_US_TRIGGERS):
        await send_message(message, random.choice(AMONG_US_RESPONSES))

    if find_word_bool(message.content, ['mind blowing', 'mindblowing', ":exploding_head:", "🤯"]):
        image_path = random.choice(IMAGES)
        try:
            await send_message(message, "** **", file_path=image_path)
        except FileNotFoundError:
            await send_message(message, "file wasn't found (how the fuck did this happen bro)")

    if find_isolated_word_bool(message.content, ['persona', 'specialist']):
        video_path = random.choice(VIDEOS)
        try:
            await send_message(message, "** **", file_path=video_path)
        except FileNotFoundError:
            await send_message(message, "file wasn't found (how the fuck did this happen bro)")

    if find_word_bool(message.content, ['testingmultmessages', 'testmultmessages']):
        await send_message(message, 'test')
        await send_message(message, 'test2', bypass_cd=True)

    if find_isolated_word_bool(message.content, ['speech bubble', 'speechbubble']) and referred_message:
        if not message.mentions:
            await reply_to_message(referred_message, random.choice(SPEECH_BUBBLES))
        else:
            await reply_to_message(referred_message, random.choice(SPEECH_BUBBLES), ping=False)

    if find_word_bool(message.content, ['flip a coin']):
        if random.randrange(1, 3) == 1:
            await send_message(message, 'heads', bypass_cd=True)
        else:
            await send_message(message, 'tails', bypass_cd=True)

    if find_word_bool(message.content, ['roll a die', 'roll a dice', 'diceroll']):
        await send_message(message, random.randrange(1, 6), bypass_cd=True)

    if find_word_bool(message.content, ['what is my name']):
        await reply_to_message(message, f"{message.author.display_name} *({message.author.name})*")

# keep_awake()

client.run(TOKEN)
