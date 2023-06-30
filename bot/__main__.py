#!/usr/bin/env python3
from asyncio import create_subprocess_exec, gather
from os import execl as osexecl
from signal import SIGINT, signal
from sys import executable
from time import time
from uuid import uuid4

from aiofiles import open as aiopen
from aiofiles.os import path as aiopath
from aiofiles.os import remove as aioremove
from psutil import (boot_time, cpu_count, cpu_percent, disk_usage,
                    net_io_counters, swap_memory, virtual_memory)
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import (DATABASE_URL, INCOMPLETE_TASK_NOTIFIER, LOGGER,
                 STOP_DUPLICATE_TASKS, Interval, QbInterval, bot, botStartTime,
                 config_dict, scheduler, user_data)
from bot.helper.listeners.aria2_listener import start_aria2_listener

from .helper.ext_utils.bot_utils import (cmd_exec, get_readable_file_size,
                                         get_readable_time, set_commands,
                                         sync_to_async)
from .helper.ext_utils.db_handler import DbManger
from .helper.ext_utils.fs_utils import clean_all, exit_clean_up, start_cleanup
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.message_utils import (editMessage, sendFile,
                                                   sendMessage)
from .modules import (anonymous, authorize, bot_settings, cancel_mirror,
                      category_select, clone, eval, gd_count, gd_delete,
                      gd_list, leech_del, mirror_leech, rmdb, rss,
                      save_message, shell, status, torrent_search,
                      torrent_select, users_settings, ytdlp)


async def stats(client, message):
    total, used, free, disk = disk_usage('/')
    swap = swap_memory()
    memory = virtual_memory()
    net_io = net_io_counters()
    if await aiopath.exists('.git'):
        last_commit = await cmd_exec("git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True)
        last_commit = last_commit[0]
    else:
        last_commit = 'No UPSTREAM_REPO'
    stats = f'<b>📊 Time Calculation 📊</b>\n\n'\
            f'<b>⏰ Bot Uptime : {get_readable_time(time() - botStartTime)}</b>\n'\
            f'<b>🖥 OS Uptime : {get_readable_time(time() - boot_time())}</b>\n\n'\
			f'<b>📊 Data Usage  📊</b>\n\n'\
            f'<b>🗃 Storage : {get_readable_file_size(total)}</b>\n'\
            f'<b>📈 Used : {get_readable_file_size(used)}</b> | <b>📉 Free : {get_readable_file_size(free)}</b>\n'\
            f'<b>📤 Upload : {get_readable_file_size(net_io_counters().bytes_sent)}</b>\n'\
            f'<b>📥 Download : {get_readable_file_size(net_io_counters().bytes_recv)}</b>\n\n'\
			f'<b>📊 Performance Meter 📊</b>\n\n'\
            f'<b>🖥 CPU : {cpu_percent(interval=0.5)}%</b>\n'\
            f'<b>⚙️ RAM : {memory.percent}%</b>\n'\
            f'<b>🗃 DISK : {disk}%</b>\n'\
            f'<b>🪅 Physical Cores : {cpu_count(logical=False)}</b>\n'\
            f'<b>🎛 Total Cores : {cpu_count(logical=True)}</b>\n'\
            f'<b>🛡 Swap Memory : {get_readable_file_size(swap.total)}</b> | <b>⏳ Used : {swap.percent}%</b>\n'\
            f'<b>💽 Memory Total : {get_readable_file_size(memory.total)}</b>\n'\
            f'<b>📉 Memory Free : {get_readable_file_size(memory.available)}</b>\n'\
            f'<b>📈 Memory Used : {get_readable_file_size(memory.used)}</b>\n'
    await sendMessage(message, stats)


async def start(_, message):
    if len(message.command) > 1:
        userid = message.from_user.id
        input_token = message.command[1]
        if userid not in user_data:
            return await sendMessage(message, 'Who are you?')
        data = user_data[userid]
        if 'token' not in data or data['token'] != input_token:
            return await sendMessage(message, 'This is a token already expired')
        data['token'] = str(uuid4())
        data['time'] = time()
        user_data[userid].update(data)
        return await sendMessage(message, 'Token refreshed successfully!')
    elif config_dict['DM_MODE']:
        start_string = 'Bot Started.\n' \
            'Now I will send your files and links here.\n'
    else:
        start_string = 'This bot can mirror all your links to Google Drive!\n' \
            'Type /help to get a list of available commands\n'
    await sendMessage(message, start_string)


async def restart(_, message):
    restart_message = await sendMessage(message, "Restarting...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    for interval in [QbInterval, Interval]:
        if interval:
            interval[0].cancel()
    await sync_to_async(clean_all)
    proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|aria2c|qbittorrent-nox|ffmpeg|rclone')
    proc2 = await create_subprocess_exec('python3', 'update.py')
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(message, "Starting Ping")
    end_time = int(round(time() * 1000))
    await editMessage(reply, f'{end_time - start_time} ms')


async def log(_, message):
    await sendFile(message, 'log.txt')

help_string = f'''
Available Commands :

/{BotCommands.MirrorCommand} : Start Mirror to Google Drive.

/{BotCommands.QbMirrorCommand} : Start Mirror to Google Drive Using qBitTorrent.

/{BotCommands.YtdlCommand} : Mirror YTDL Supported Link.

/{BotCommands.LeechCommand} : Start Leeching / Upload to Telegram.

/{BotCommands.QbLeechCommand} : Start Leeching / Upload Using qBitTorrent.

/{BotCommands.YtdlLeechCommand} : Leech YTDL Supported Link.

/{BotCommands.CloneCommand} : Copy File/Folder to Google Drive.

/{BotCommands.CountCommand} : Count File/Folder of Google Drive.

/{BotCommands.DeleteCommand} : Delete File/Folder From Google Drive.

/{BotCommands.CancelMirror}: Cancel Mirror

/{BotCommands.ListCommand} : Search File/Folder of Google Drive.

/{BotCommands.SearchCommand} : Torrents Search with API.

/{BotCommands.StatusCommand} : Shows a Status of All the Downloads.

/{BotCommands.StatsCommand} : Show Stats of the Machine.

/{BotCommands.PingCommand} : Check Active Bot.

Commands for ZIP / UNZIP Mirror
Note : Add Commands [ -z / -e ] After Your Link
-z = Zip 
-e = Unzip

/{BotCommands.MirrorCommand} [Link] -z : Start Mirror and Upload to Google Drive as .ZIP File.

/{BotCommands.MirrorCommand} [Link] -e : Start Mirror and Upload to Google Drive as Extracted File.

/{BotCommands.QbMirrorCommand} [Link] -z  : Start Mirror and Upload to Google Drive as .ZIP File Using qBitTorrent.

/{BotCommands.QbMirrorCommand} [Link] -e  : Start Mirror and Upload to Google Drive as Extracted File Using qBitTorrent.

/{BotCommands.LeechCommand} [Link] -z : Start Leech / Upload File to Telegram as .ZIP File.

/{BotCommands.LeechCommand} [Link] -e : Start Leech / Upload File to Telegram as as Extracted File.
'''


async def bot_help(_, message):
    await sendMessage(message, help_string)


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0

    async def send_incompelete_task_message(cid, msg):
        try:
            if msg.startswith('Restarted Successfully!'):
                await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
                await bot.send_message(chat_id, msg, disable_web_page_preview=True, reply_to_message_id=msg_id)
                await aioremove(".restartmsg")
            else:
                await bot.send_message(chat_id=cid, text=msg, disable_web_page_preview=True,
                                       disable_notification=True)
        except Exception as e:
            LOGGER.error(e)

    if DATABASE_URL:
        if INCOMPLETE_TASK_NOTIFIER and (notifier_dict := await DbManger().get_incomplete_tasks()):
            for cid, data in notifier_dict.items():
                msg = 'Restarted Successfully!' if cid == chat_id else 'Bot Restarted!'
                for tag, links in data.items():
                    msg += f"\n\n{tag}: "
                    for index, link in enumerate(links, start=1):
                        msg += f" <a href='{link}'>{index}</a> |"
                        if len(msg.encode()) > 4000:
                            await send_incompelete_task_message(cid, msg)
                            msg = ''
                if msg:
                    await send_incompelete_task_message(cid, msg)

        if STOP_DUPLICATE_TASKS:
            await DbManger().clear_download_links()

    if await aiopath.isfile(".restartmsg"):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
        except:
            pass
        await aioremove(".restartmsg")


async def main():
    await gather(start_cleanup(), torrent_search.initiate_search_tools(), restart_notification(), set_commands(bot))
    await sync_to_async(start_aria2_listener, wait=False)

    bot.add_handler(MessageHandler(
        start, filters=command(BotCommands.StartCommand)))
    bot.add_handler(MessageHandler(log, filters=command(
        BotCommands.LogCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(restart, filters=command(
        BotCommands.RestartCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(ping, filters=command(
        BotCommands.PingCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(bot_help, filters=command(
        BotCommands.HelpCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(stats, filters=command(
        BotCommands.StatsCommand) & CustomFilters.authorized))
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
