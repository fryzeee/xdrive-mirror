#!/usr/bin/env python3
from time import time

from pyrogram.filters import command, regex
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

from bot import LOGGER, bot
from bot.helper.ext_utils.bot_utils import (checking_access, get_readable_time,
                                            get_telegraph_list, new_task,
                                            sync_to_async)
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (anno_checker,
                                                      editMessage, isAdmin,
                                                      request_limiter,
                                                      sendMessage)


async def list_buttons(user_id, isRecursive=True):
    buttons = ButtonMaker()
    buttons.ibutton("📁 Folders", f"list_types {user_id} Folders {isRecursive}")
    buttons.ibutton("📄 Files", f"list_types {user_id} Files {isRecursive}")
    buttons.ibutton("👍 File & Folder", f"list_types {user_id} both {isRecursive}")
    buttons.ibutton("🚫 Cancel 🚫", f"list_types {user_id} cancel")
    return buttons.build_menu(2)


async def _list_drive(key, message, item_type, isRecursive):
    LOGGER.info(f"listing: {key}")
    start_time = time()
    gdrive = GoogleDriveHelper()
    telegraph_content, contents_no = await sync_to_async(gdrive.drive_list, key, isRecursive=isRecursive, itemType=item_type)
    Elapsed = get_readable_time(time() - start_time)
    if telegraph_content:
        try:
            button = await get_telegraph_list(telegraph_content)
        except Exception as e:
            await editMessage(message, e)
            return
        msg = f'<b>✅ Found {contents_no} Result For <i>{key}</i></b>\n\n<b>💡 Type : {item_type}\n<b>💡 Recursive : {isRecursive}</b>'
        await editMessage(message, msg, button)
    else:
        msg = f'<b>❌ No Result Found For <i>{key}</i></b>\n\n<b>💡 Type : {item_type}</b>\n<b>💡 Recursive : {isRecursive}</b>'
        await editMessage(message, msg)


@new_task
async def select_type(_, query):
    user_id = query.from_user.id
    message = query.message
    key = message.reply_to_message.text.split(maxsplit=1)[1].strip()
    data = query.data.split()
    if user_id != int(data[1]):
        return await query.answer(text="Not Yours", show_alert=True)
    elif data[2] == 'rec':
        await query.answer()
        isRecursive = not bool(eval(data[3]))
        buttons = await list_buttons(user_id, isRecursive)
        return await editMessage(message, '📍 Choose Options :', buttons)
    elif data[2] == 'cancel':
        await query.answer()
        return await editMessage(message, "🚫 Canceled 🚫")
    await query.answer()
    item_type = data[2]
    isRecursive = eval(data[3])
    await editMessage(message, f"<b>🔎 Searching For <i>{key}</i></b>")
    await _list_drive(key, message, item_type, isRecursive)


async def drive_list(_, message):
    if len(message.text.split()) == 1:
        return await sendMessage(message, '🚫 Send Me a Keyword 🚫')
    if not message.from_user:
        message.from_user = await anno_checker(message)
    if not message.from_user:
        return
    user_id = message.from_user.id
    if not await isAdmin(message, user_id):
        if await request_limiter(message):
            return
        if message.chat.type != message.chat.type.PRIVATE:
            msg, btn = checking_access(user_id)
            if msg is not None:
                await sendMessage(message, msg, btn.build_menu(1))
                return
    buttons = await list_buttons(user_id)
    await sendMessage(message, '📍 Choose Options :', buttons)

bot.add_handler(MessageHandler(drive_list, filters=command(
    BotCommands.ListCommand) & CustomFilters.authorized))
bot.add_handler(CallbackQueryHandler(
    select_type, filters=regex("^list_types")))
