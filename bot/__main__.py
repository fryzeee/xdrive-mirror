#!/usr/bin/env python3
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from aiofiles import open as aiopen
from os import execl as osexecl
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from time import time
from sys import executable
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from asyncio import create_subprocess_exec

from bot import bot, botStartTime, LOGGER, Interval, DATABASE_URL, user, QbInterval, INCOMPLETE_TASK_NOTIFIER, scheduler
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, cmd_exec, sync_to_async
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .modules import authorize, list, cancel_mirror, mirror_status, mirror_leech, clone, ytdlp, rss, shell, eval, delete, count, users_settings, search, bt_select, bot_settings


async def stats(client, message):
    if await aiopath.exists('.git'):
        last_commit = await cmd_exec("git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True)
        last_commit = last_commit[0]
    else:
        last_commit = 'No UPSTREAM_REPO'
    total, used, free, disk = disk_usage('/')
    swap = swap_memory()
    memory = virtual_memory()
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

async def start(client, message):
    buttons = ButtonMaker()
    buttons.ubutton("My Master", "https://t.me/hilmay619")
    reply_markup = buttons.build_menu(2)
    if await CustomFilters.authorized(client, message):
        start_string = f'''
Mirror All Your File/Links to Google Drive or Telegram
Type /{BotCommands.HelpCommand} to Get a List of Available Commands
'''
        await sendMessage(message, start_string, reply_markup)
    else:
        await sendMessage(message, '🚫 Oops! You Not a Authorized User 🚫', reply_markup)

async def restart(client, message):
    restart_message = await sendMessage(message, "Restarting...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    if QbInterval:
        QbInterval[0].cancel()
        QbInterval.clear()
    await sync_to_async(clean_all)
    await (await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|aria2c|qbittorrent-nox|ffmpeg')).wait()
    await (await create_subprocess_exec('python3', 'update.py')).wait()
    async with aiopen(".restartmsg", "w") as f:
        await f.truncate(0)
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")

async def ping(client, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(message, "Starting Ping")
    end_time = int(round(time() * 1000))
    await editMessage(reply, f'{end_time - start_time} ms')

async def log(client, message):
    await sendFile(message, 'log.txt')

help_string = f'''
Available Commands :
______________
/{BotCommands.MirrorCommand} : Start Mirroring
/{BotCommands.QbMirrorCommand} : Mirror Using QBitTorrent
/{BotCommands.YtdlZipCommand} : Mirror YTDL as .Zip
/{BotCommands.ZipMirrorCommand} : Mirror and Upload as .Zip
/{BotCommands.QbZipMirrorCommand} : Mirror Torrent and Upload as .Zip Using QBitTorrent
/{BotCommands.UnzipMirrorCommand} : Mirror and Upload as Extract Files
/{BotCommands.QbUnzipMirrorCommand} : Mirror Torrent and Upload as Extract Files Using QBitTorrent
/{BotCommands.LeechCommand} : Mirror as Upload to Telegram
/{BotCommands.QbLeechCommand} : Mirror Torrent and Upload to Telegram Using QBitTorrent
/{BotCommands.YtdlLeechCommand} : Leech YTDL Upload as Extract Files
/{BotCommands.ZipLeechCommand} : Mirror & Upload File to Telegram as .Zip
/{BotCommands.QbZipLeechCommand} : Mirror Torrent and Upload to Telegram as .Zip Using QBitTorrent
/{BotCommands.UnzipLeechCommand} : Mirror & Upload File as Extracted to Telegram
/{BotCommands.QbUnzipLeechCommand} : Mirror Torrent and Upload as Extract Using QBitTorrent
/{BotCommands.YtdlZipLeechCommand} : Upload File to Telegram YTDL Supported Link as .Zip
/{BotCommands.YtdlCommand} : Mirror YTDL
/{BotCommands.CloneCommand} : Copy File/Folder to Google Drive.
/{BotCommands.CountCommand} : Count File/Folder of Google Drive.
/{BotCommands.DeleteCommand} : Delete File/Folder From Google Drive
/{BotCommands.CancelMirror} : Cancel Task
/{BotCommands.ListCommand} : Search File/Folder in Google Drive
/{BotCommands.StatusCommand} : Shows a Status Downloaded
/{BotCommands.StatsCommand} : Show Stats of the Machine
/{BotCommands.PingCommand} : Check Active Bot
/{BotCommands.SearchCommand} : Torrent Search
______________
'''

async def bot_help(client, message):
    await sendMessage(message, help_string)

async def main():
    await start_cleanup()
    await search.initiate_search_tools()
    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := await DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                if await aiopath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = 'Restarted Successfully!'
                else:
                    msg = 'Bot Restarted!'
                for tag, links in data.items():
                    msg += f"\n\n{tag}: "
                    for index, link in enumerate(links, start=1):
                        msg += f" <a href='{link}'>{index}</a> |"
                        if len(msg.encode()) > 4000:
                            if 'Restarted Successfully!' in msg and cid == chat_id:
                                try:
                                    await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=msg)
                                except:
                                    pass
                                await aioremove(".restartmsg")
                            else:
                                try:
                                    await bot.send_message(chat_id=cid, text=msg, disable_web_page_preview=True,
                                                           disable_notification=True)
                                except Exception as e:
                                    LOGGER.error(e)
                            msg = ''
                if 'Restarted Successfully!' in msg and cid == chat_id:
                    try:
                        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=msg)
                    except:
                        pass
                    await aioremove(".restartmsg")
                else:
                    try:
                        await bot.send_message(chat_id=cid, text=msg, disable_web_page_preview=True,
                                         disable_notification=True)
                    except Exception as e:
                        LOGGER.error(e)

    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="Restarted Successfully!")
        except:
            pass
        await aioremove(".restartmsg")

    bot.add_handler(MessageHandler(start, filters=command(BotCommands.StartCommand)))
    bot.add_handler(MessageHandler(log, filters=command(BotCommands.LogCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(restart, filters=command(BotCommands.RestartCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(ping, filters=command(BotCommands.PingCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(bot_help, filters=command(BotCommands.HelpCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(stats, filters=command(BotCommands.StatsCommand) & CustomFilters.authorized))
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
