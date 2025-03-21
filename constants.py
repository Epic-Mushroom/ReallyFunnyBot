import datetime

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
MOKSHA_ID = 834088137939615764
JAMES_ID = 336702837792833536
KUSH_ID = 873411125633491024
JADEN_ID = 762393738676404224

GROUP_CHAT_SERVER_ID = 1309380397410291712
PRIVATE_SERVER_ID = 964941621110120538

GENERAL_CHANNEL_ID_1 = 1309380397410291715
GENERAL_CHANNEL_ID_2 = 1096685257891250228
GENERAL_CHANNEL_ID_3 = 964941621110120541

MY_GUILD = 964941621110120538

COOLDOWN_LENGTH = 10
COOLDOWN_LIMIT = 4 # how many messages that can be sent per COOLDOWN_LENGTH seconds

REMINDER_TIME = datetime.time(hour = 12, minute = 0, tzinfo = datetime.timezone(datetime.timedelta(hours=-7)))