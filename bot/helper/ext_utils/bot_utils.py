#!/usr/bin/env python3
from asyncio import (create_subprocess_exec, create_subprocess_shell,
                     run_coroutine_threadsafe, sleep)
from asyncio.subprocess import PIPE
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from html import escape
from re import match as re_match
from time import time
from html import escape
from uuid import uuid4
from psutil import virtual_memory, cpu_percent, disk_usage, virtual_memory
from pyrogram.types import BotCommand
from asyncio import create_subprocess_exec, create_subprocess_shell, run_coroutine_threadsafe, sleep
from asyncio.subprocess import PIPE
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession

from bot import (bot_loop, bot_name, botStartTime, config_dict, download_dict,
                 download_dict_lock, extra_buttons, user_data)
from bot.helper.ext_utils.shortener import short_url
from bot.helper.ext_utils.telegraph_helper import telegraph
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker

THREADPOOL = ThreadPoolExecutor(max_workers=1000)

MAGNET_REGEX = r'^magnet:\?.*xt=urn:(btih|btmh):[a-zA-Z0-9]*\s*'

URL_REGEX = r'^(?!\/)(rtmps?:\/\/|mms:\/\/|rtsp:\/\/|https?:\/\/|ftp:\/\/)?([^\/:]+:[^\/@]+@)?(www\.)?(?=[^\/:\s]+\.[^\/:\s]+)([^\/:\s]+\.[^\/:\s]+)(:\d+)?(\/[^#\s]*[\s\S]*)?(\?[^#\s]*)?(#.*)?$'

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

STATUS_START = 0
PAGES = 1
PAGE_NO = 1


class MirrorStatus:
    STATUS_UPLOADING = "Uploading. . . 📤"
    STATUS_DOWNLOADING = "Downloading. . . 📥"
    STATUS_CLONING = "Cloning. . . ♻️"
    STATUS_QUEUEDL = "Queued Download. . . 📝"
    STATUS_QUEUEUP = "Queued Upload. . . 📝"
    STATUS_PAUSED = "Paused. . . ⭕️"
    STATUS_ARCHIVING = "Archiving. . . 🔐"
    STATUS_EXTRACTING = "Extracting. . . 📂"
    STATUS_SPLITTING = "Split. . . ✂️ "
    STATUS_CHECKING = "Checking. . . 🔎"
    STATUS_SEEDING = "Seeding. . . 🌧"


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.task = bot_loop.create_task(self.__set_interval())

    async def __set_interval(self):
        while True:
            await sleep(self.interval)
            await self.action()

    def cancel(self):
        self.task.cancel()


def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes}B'


async def getDownloadByGid(gid):
    async with download_dict_lock:
        return next((dl for dl in download_dict.values() if dl.gid() == gid), None)


async def getAllDownload(req_status, user_id=None):
    dls = []
    async with download_dict_lock:
        for dl in list(download_dict.values()):
            if user_id and user_id != dl.message.from_user.id:
                continue
            status = dl.status()
            if req_status in ['all', status]:
                dls.append(dl)
    return dls


def bt_selection_buttons(id_, isCanCncl=True):
    gid = id_[:12] if len(id_) > 20 else id_
    pincode = ''.join([n for n in id_ if n.isdigit()][:4])
    buttons = ButtonMaker()
    BASE_URL = config_dict['BASE_URL']
    if config_dict['WEB_PINCODE']:
        buttons.ubutton("👆 Select Files 👆", f"{BASE_URL}/app/files/{id_}")
        buttons.ibutton("🔰 Pin Code 🔰", f"btsel pin {gid} {pincode}")
    else:
        buttons.ubutton(
            "👆 Select Files 👆", f"{BASE_URL}/app/files/{id_}?pin_code={pincode}")
    if isCanCncl:
        buttons.ibutton("🚫 Cancel 🚫", f"btsel rm {gid} {id_}")
    buttons.ibutton("✅ Done Selecting ✅", f"btsel done {gid} {id_}")
    return buttons.build_menu(2)


async def get_telegraph_list(telegraph_content):
    path = [(await telegraph.create_page(title='xDrive Search', content=content))["path"] for content in telegraph_content]
    if len(path) > 1:
        await telegraph.edit_telegraph(path, telegraph_content)
    buttons = ButtonMaker()
    buttons.ubutton("🔍 Check 🔎", f"https://telegra.ph/{path[0]}", 'header')
    buttons = extra_btns(buttons)
    return buttons.build_menu(1)


def get_progress_bar_string(pct):
    pct = float(pct.strip('%'))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = '■' * cFull
    p_str += '□' * (12 - cFull)
    return f"[{p_str}]"


def get_readable_message():
    msg = ""
    button = None
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    tasks = len(download_dict)
    globals()['PAGES'] = (tasks + STATUS_LIMIT - 1) // STATUS_LIMIT
    if PAGE_NO > PAGES and PAGES != 0:
        globals()['STATUS_START'] = STATUS_LIMIT * (PAGES - 1)
        globals()['PAGE_NO'] = PAGES
    for download in list(download_dict.values())[STATUS_START:STATUS_LIMIT+STATUS_START]:
        msg += f"<b>📄 File Name :</b> <code>{escape(f'{download.name()}')}</code>"
        msg += f"\n<b>🗃️ Total Size : {download.size()}</b>"
        msg += f"\n<b>🌀 Status : {download.status()}</b>"
        if download.status() not in [MirrorStatus.STATUS_SPLITTING, MirrorStatus.STATUS_SEEDING]:
            msg += f"\n<b>🚀 {get_progress_bar_string(download.progress())} {download.progress()}</b>"
            msg += f"\n<b>🔥 Running : {download.processed_bytes()} of {download.size()}</b>"
            msg += f"\n<b>⚡️ Speed : {download.speed()}\n</b><b>⏳ Estimated : {download.eta()}</b>"
            if hasattr(download, 'seeders_num'):
                try:
                    msg += f"\n<b>🔍 Tracker :- 🧲 Seeds : {download.seeders_num()}</b> | <b>🧲 Leechs : {download.leechers_num()}</b> "
                except:
                    pass
        elif download.status() == MirrorStatus.STATUS_SEEDING:
            msg += f"\n<b>🗃️ Total Size : {download.size()}</b>"
            msg += f"\n<b>⚡️ Speed : {download.upload_speed()}</b>"
            msg += f" | <b>📤 Upload : {download.uploaded_bytes()}</b>"
            msg += f"\n<b>🔀 Ratio : {download.ratio()}</b>"
            msg += f" | <b>⏳ Time : {download.seeding_time()}</b>"
        else:
            msg += f"\n<b>🗃️ Total Size : {download.size()}</b>"
        msg += f"\n<b>⏳ Elapsed : {get_readable_time(time() - download.extra_details['startTime'])}</b>"
        msg += f"\n<b>🚫 Stop : <code>/{BotCommands.CancelMirror} {download.gid()}</code></b>\n\n"
    if len(msg) == 0:
        return None, None
    dl_speed = 0
    up_speed = 0
    for download in download_dict.values():
        tstatus = download.status()
        if tstatus == MirrorStatus.STATUS_DOWNLOADING:
            spd = download.speed()
            if 'K' in spd:
                dl_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                dl_speed += float(spd.split('M')[0]) * 1048576
        elif tstatus == MirrorStatus.STATUS_UPLOADING:
            spd = download.speed()
            if 'K' in spd:
                up_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                up_speed += float(spd.split('M')[0]) * 1048576
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            spd = download.upload_speed()
            if 'K' in spd:
                up_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                up_speed += float(spd.split('M')[0]) * 1048576
    if tasks > STATUS_LIMIT:
        buttons = ButtonMaker()
        buttons.ibutton("<<", "status pre")
        buttons.ibutton(f"{PAGE_NO}/{PAGES} ({tasks})", "status ref")
        buttons.ibutton(">>", "status nex")
        button = buttons.build_menu(3)
    msg += f"<b>📊 Performance Meter 📊</b>\n\n"
    msg += f"<b>🖥 CPU            : {cpu_percent()}%</b>\n<b>🗃 DISK           : {get_readable_file_size(disk_usage(config_dict['DOWNLOAD_DIR']).free)}</b>"
    msg += f"\n<b>⚙️ RAM           : {virtual_memory().percent}%</b>\n<b>🖥 UPTIME     : {get_readable_time(time() - botStartTime)}</b>"
    msg += f"\n\n<b>⚡️ Internet Speed Meter ⚡️</b>\n\n"
    msg += f"<b>🔻 Download  : {get_readable_file_size(dl_speed)}/s</b>\n<b>🔺 Upload       : {get_readable_file_size(up_speed)}/s</b>"
    return msg, button


async def turn_page(data):
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    global STATUS_START, PAGE_NO
    async with download_dict_lock:
        if data[1] == "nex":
            if PAGE_NO == PAGES:
                STATUS_START = 0
                PAGE_NO = 1
            else:
                STATUS_START += STATUS_LIMIT
                PAGE_NO += 1
        elif data[1] == "pre":
            if PAGE_NO == 1:
                STATUS_START = STATUS_LIMIT * (PAGES - 1)
                PAGE_NO = PAGES
            else:
                STATUS_START -= STATUS_LIMIT
                PAGE_NO -= 1


def get_readable_time(seconds):
    periods = [(' Days ', 86400), (' Hours ', 3600), (' Minutes ', 60), (' Seconds ', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result


def is_magnet(url):
    return bool(re_match(MAGNET_REGEX, url))


def is_url(url):
    return bool(re_match(URL_REGEX, url))


def is_gdrive_link(url):
    return "drive.google.com" in url


def is_telegram_link(url):
    return url.startswith(('https://t.me/', 'tg://openmessage?user_id='))


def is_share_link(url: str):
    if 'gdtot' in url:
        regex = r'(https?:\/\/.+\.gdtot\..+\/file\/\d+)'
    else:
        regex = r'(https?:\/\/(\S+)\..+\/file\/\S+)'
    return bool(re_match(regex, url))


def is_mega_link(url):
    return "mega.nz" in url or "mega.co.nz" in url


def is_rclone_path(path):
    return bool(re_match(r'^(mrcc:)?(?!magnet:)(?![- ])[a-zA-Z0-9_\. -]+(?<! ):(?!.*\/\/).*$|^rcl$', path))


def get_mega_link_type(url):
    return "folder" if "folder" in url or "/#F!" in url else "file"


def arg_parser(items, arg_base):
    if not items:
        return arg_base
    t = len(items)
    i = 0
    while i + 1 <= t:
        part = items[i]
        if part in arg_base:
            if part in ['-s', '-j']:
                arg_base[part] = True
            elif t == i + 1:
                if part in ['-b', '-e', '-z', '-s', '-j', '-d']:
                    arg_base[part] = True
            else:
                sub_list = []
                for j in range(i+1, t):
                    item = items[j]
                    if item in arg_base:
                        if part in ['-b', '-e', '-z', '-s', '-j', '-d']:
                            arg_base[part] = True
                        break
                    sub_list.append(item)
                    i += 1
                if sub_list:
                    arg_base[part] = " ".join(sub_list)
        i += 1
    if items[0] not in arg_base:
        arg_base['link'] = items[0]
    return arg_base


async def get_content_type(url):
    try:
        async with ClientSession(trust_env=True) as session:
            async with session.get(url, verify_ssl=False) as response:
                return response.headers.get('Content-Type')
    except:
        return None


def update_user_ldata(id_, key, value):
    if not key and not value:
        user_data[id_] = {}
        return
    user_data.setdefault(id_, {})
    user_data[id_][key] = value


def extra_btns(buttons):
    if extra_buttons:
        for btn_name, btn_url in extra_buttons.items():
            buttons.ubutton(btn_name, btn_url)
    return buttons


async def check_user_tasks(user_id, maxtask):
    if tasks := await getAllDownload(MirrorStatus.STATUS_DOWNLOADING, user_id):
        return len(tasks) >= maxtask


def checking_access(user_id, button=None):
    if not config_dict['TOKEN_TIMEOUT']:
        return None, button
    user_data.setdefault(user_id, {})
    data = user_data[user_id]
    expire = data.get('time')
    isExpired = (expire is None or expire is not None and (
        time() - expire) > config_dict['TOKEN_TIMEOUT'])
    if isExpired:
        token = data['token'] if expire is None and 'token' in data else str(
            uuid4())
        if expire is not None:
            del data['time']
        data['token'] = token
        user_data[user_id].update(data)
        if button is None:
            button = ButtonMaker()
        button.ubutton('Refresh Token', short_url(
            f'https://t.me/{bot_name}?start={token}'))
        return 'Token is expired, refresh your token and try again.', button
    return None, button


async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper


async def sync_to_async(func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    future = bot_loop.run_in_executor(THREADPOOL, pfunc)
    return await future if wait else future


def async_to_sync(func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future


def new_thread(func):
    @wraps(func)
    def wrapper(*args, wait=False, **kwargs):
        future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
        return future.result() if wait else future
    return wrapper


async def set_commands(client):
    if config_dict['SET_COMMANDS']:
        await client.set_bot_commands([
            BotCommand(f'{BotCommands.MirrorCommand}', 'Mirror'),
            BotCommand(f'{BotCommands.LeechCommand}', 'Leech'),
            BotCommand(f'{BotCommands.QbMirrorCommand}', 'Mirror Torrent Using qBitTorrent'),
            BotCommand(f'{BotCommands.QbLeechCommand}', 'Leech Torrent Using qBitTorrent'),
            BotCommand(f'{BotCommands.YtdlCommand}', 'Mirror YTDL Supported Link'),
            BotCommand(f'{BotCommands.YtdlLeechCommand}', f' Leech YTDL Supported Link'),
            BotCommand(f'{BotCommands.CloneCommand}','Copy File/Folder to Drive'),
            BotCommand(f'{BotCommands.StatusCommand}', 'Get Mirror Status Message'),
            BotCommand(f'{BotCommands.StatsCommand}', 'Check Bot Stats'),
            BotCommand(f'{BotCommands.BtSelectCommand}', 'Select Files to Download Only Torrents'),
            BotCommand(f'{BotCommands.CategorySelect}', 'Select Category to Upload Only Mirror'),
            BotCommand(f'{BotCommands.CancelMirror}', 'Cancel a Task'),
            BotCommand(f'{BotCommands.CancelAllCommand}', f'Cancel All Tasks'),
            BotCommand(f'{BotCommands.ListCommand}', 'Search in Drive'),
            BotCommand(f'{BotCommands.SearchCommand}', 'Search in Torrent'),
            BotCommand(f'{BotCommands.UserSetCommand}', 'Users Settings'),
            BotCommand(f'{BotCommands.HelpCommand}', 'Help'),
        ])
