#!/usr/bin/env python3
from time import time

from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import bot
from bot.helper.ext_utils.bot_utils import (get_readable_file_size,
                                            get_readable_time, is_gdrive_link,
                                            new_task, sync_to_async)
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import deleteMessage, sendMessage


@new_task
async def countNode(_, message):
    args = message.text.split()
    if sender_chat := message.sender_chat:
        tag = sender_chat.title
    elif username := message.from_user.username:
        tag = f"@{username}"
    else:
        tag = message.from_user.mention

    link = args[1] if len(args) > 1 else ''
    if len(link) == 0 and (reply_to := message.reply_to_message):
        link = reply_to.text.split(maxsplit=1)[0].strip()

    if is_gdrive_link(link):
        msg = await sendMessage(message, f"🧬 Counting : <code>{link}</code>")
        gd = GoogleDriveHelper()
        start_time = time()
        name, mime_type, size, files, folders = await sync_to_async(gd.count, link)
        elapsed = time() - start_time
        if mime_type is None:
            await sendMessage(message, name)
            return
        await deleteMessage(msg)
        msg = f'<b>📂 File Name :</b> <code>{name}</code>'
        msg += f'\n<b>📥 Total Size : {get_readable_file_size(size)}</b>'
        msg += f'\n<b>💾 Type Files : {mime_type}</b>'
        if mime_type == 'Folder':
            msg += f'\n<b>🗂 Total Folders : {folders}</b>'
            msg += f'\n<b>📄 Total Files : {files}</b>'
            msg += f"\n<b>⏳ Elapsed : {get_readable_time(elapsed)}</b>"
            msg += f"\n\n<b>👤 By : {tag}</b>"
    else:
        msg = '🚫 Send Me Google Drive Shareable Link 🚫'

    await sendMessage(message, msg)


bot.add_handler(MessageHandler(countNode, filters=command(
    BotCommands.CountCommand) & CustomFilters.authorized))