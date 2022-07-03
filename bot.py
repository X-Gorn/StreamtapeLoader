import os, lk21, time, requests, math, bs4
from urllib.parse import unquote
from pySmartDL import SmartDL
from urllib.error import HTTPError
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

# Configs
API_HASH = os.environ['API_HASH'] # Api hash
APP_ID = int(os.environ['APP_ID']) # Api id/App id
BOT_TOKEN = os.environ['BOT_TOKEN'] # Bot token
OWNER_ID = int(os.environ['OWNER_ID']) # Your telegram id
AS_DOC = os.environ['AS_DOC'] # Upload method. If True: will send as document | If False: will send as video
DEFAULT_THUMBNAIL = os.environ['DEFAULT_THUMBNAIL'] # Default thumbnail. Used if bot can't find streamtape video thumbnail

# Buttons
START_BUTTONS=[
    [
        InlineKeyboardButton("Source", url="https://github.com/X-Gorn/StreamtapeLoader"),
        InlineKeyboardButton("Project Channel", url="https://t.me/xTeamBots"),
    ],
    [InlineKeyboardButton("Author", url="https://t.me/xgorn")],
]

# Helpers


# later
def streamtape_scrape(url):
    text = requests.get(url).text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    norobotlink = soup.find(id='norobotlink')
    return norobotlink.text


def scrape_poster(url):
    s = requests.Session()
    text = s.get(url).text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    try:
        mainvideo = soup.find('video', id='mainvideo')
        return True, mainvideo['poster']
    except:
        return False, 'error'

# https://github.com/SpEcHiDe/AnyDLBot
async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n {}".format(
                    ud_type,
                    tmp
                )
            )
        except:
            pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

# https://github.com/viperadnan-git/google-drive-telegram-bot/blob/main/bot/helpers/downloader.py
def download_file(url, dl_path):
  try:
    dl = SmartDL(url, dl_path, progress_bar=False)
    dl.start()
    filename = dl.get_dest()
    if '+' in filename:
          xfile = filename.replace('+', ' ')
          filename2 = unquote(xfile)
    else:
        filename2 = unquote(filename)
    os.rename(filename, filename2)
    return True, filename2
  except HTTPError as error:
    return False, error


# Running bot
xbot = Client(
    'StreamtapeLoader',
    api_id=APP_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# Start message
@xbot.on_message(filters.command('start') & filters.chat(OWNER_ID) & filters.private)
async def start(bot, update):
    await update.reply_text(f"I'm StreamtapeLoader\nYou can upload streamtape.com stream url to telegram using this bot", True, reply_markup=InlineKeyboardMarkup(START_BUTTONS))


@xbot.on_message(filters.text & filters.chat(OWNER_ID) & filters.private)
async def loader(bot, update):
    dirs = './downloads/'
    if not os.path.isdir(dirs):
        os.mkdir(dirs)
    if 'streamtape.com' in update.text:
        pass
    elif 'strtapeadblocker.xyz' in update.text:
        pass
    else:
        return
    link = update.text
    if '/' in link:
        links = link.split('/')
        if len(links) == 6:
            if link.endswith('mp4'):
                link = link
            else:
                link = link + 'video.mp4'
        elif len(links) == 5:
            link = link + '/video.mp4'
        else:
            return
    else:
        return
    bypasser = lk21.Bypass()
    url = bypasser.bypass_streamtape(link)
    pablo = await update.reply_text('Downloading...', True)
    result, dl_path = download_file(url, dirs)
    if result == True:
        import requests
        r, poster = scrape_poster(update.text)
        if r:
            thumb = f'./downloads/thumb_{update.message_id}.jpg'
            r = requests.get(poster, allow_redirects=True)
            open(thumb, 'wb').write(r.content)
        else:
            thumb_url = DEFAULT_THUMBNAIL
            thumb = f'./downloads/thumb_{update.message_id}.jpg'
            r = requests.get(thumb_url, allow_redirects=True)
            open(thumb, 'wb').write(r.content)
        if os.path.exists(thumb):
            width = 0
            height = 0
            metadata = extractMetadata(createParser(thumb))
            if metadata.has('width'):
                width = metadata.get('width')
            if metadata.has('height'):
                height = metadata.get('height')
            Image.open(thumb).convert('RGB').save(thumb)
            img = Image.open(thumb)
            # https://stackoverflow.com/a/37631799/4723940
            # img.thumbnail((90, 90))
            if AS_DOC == 'True':
                img.resize((320, height))
            elif AS_DOC == 'False':
                img.resize((90, height))
            img.save(thumb, "JPEG")
        metadata = extractMetadata(createParser(dl_path))
        if metadata is not None:
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
            else:
                duration = 0
        start_dl = time.time()
        await pablo.edit_text('Uploading...')
        if AS_DOC == 'True':
            await update.reply_document(
                document=dl_path, 
                quote=True, 
                thumb=thumb, 
                progress=progress_for_pyrogram, 
                progress_args=(
                    'Uploading...', 
                    pablo, 
                    start_dl
                )
            )
            os.remove(dl_path)
            os.remove(thumb)
        elif AS_DOC == 'False':
            await update.reply_video(
                video=dl_path,
                quote=True,
                thumb=thumb,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(
                    'Uploading...',
                    pablo,
                    start_dl
                )
            )
            os.remove(dl_path)
            os.remove(thumb)
    else:
        await pablo.edit_text('Downloading failed.')
    await pablo.delete()


xbot.run()
