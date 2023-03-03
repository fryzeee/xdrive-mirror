#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import user_data, DATABASE_URL, bot
from bot.helper.telegram_helper.message_utils import sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.ext_utils.bot_utils import update_user_ldata


async def authorize(client, message):
    msg = message.text.split()
    if len(msg) > 1:
        id_ = int(msg[1].strip())
    elif reply_to := message.reply_to_message:
        id_ = reply_to.from_user.id
    else:
        id_ = message.chat.id
    if id_ in user_data and user_data[id_].get('is_auth'):
        msg = '✅ <b>Already Authorized</b> ✅'
    else:
        update_user_ldata(id_, 'is_auth', True)
        if DATABASE_URL:
            await DbManger().update_user_data(id_)
        msg = '✅ <b>Authorized</b> ✅'
    await sendMessage(message, msg)

async def unauthorize(client, message):
    msg = message.text.split()
    if len(msg) > 1:
        id_ = int(msg[1].strip())
    elif reply_to := message.reply_to_message:
        id_ = reply_to.from_user.id
    else:
        id_ = message.chat.id
    if id_ not in user_data or user_data[id_].get('is_auth'):
        update_user_ldata(id_, 'is_auth', False)
        if DATABASE_URL:
            await DbManger().update_user_data(id_)
        msg = '🚫 <b>Unauthorized</b> 🚫'
    else:
        msg = '🚫 <b>Already Unauthorized</b> 🚫'
    await sendMessage(message, msg)

async def addSudo(client, message):
    id_ = ""
    msg = message.text.split()
    if len(msg) > 1:
        id_ = int(msg[1].strip())
    elif reply_to := message.reply_to_message:
        id_ = reply_to.from_user.id
    if id_:
        if id_ in user_data and user_data[id_].get('is_sudo'):
            msg = '✅ <b>Already Sudo</b> ✅'
        else:
            update_user_ldata(id_, 'is_sudo', True)
            if DATABASE_URL:
                await DbManger().update_user_data(id_)
            msg = '✅ <b>Promoted as Sudo</b> ✅'
    else:
        msg = "🚫 <b>Give ID or Reply People Messages to Promote</b> 🚫"
    await sendMessage(message, msg)

async def removeSudo(client, message):
    id_ = ""
    msg = message.text.split()
    if len(msg) > 1:
        id_ = int(msg[1].strip())
    elif reply_to := message.reply_to_message:
        id_ = reply_to.from_user.id
    if id_ and id_ not in user_data or user_data[id_].get('is_sudo'):
        update_user_ldata(id_, 'is_sudo', False)
        if DATABASE_URL:
            await DbManger().update_user_data(id_)
        msg = '🚫 <b>Demoted</b> 🚫'
    else:
        msg = "🚫 <b>Give ID or Reply People Messages to Promote</b> 🚫"
    await sendMessage(message, msg)

bot.add_handler(MessageHandler(authorize, filters=command(BotCommands.AuthorizeCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(unauthorize, filters=command(BotCommands.UnAuthorizeCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(addSudo, filters=command(BotCommands.AddSudoCommand) & CustomFilters.sudo))
bot.add_handler(MessageHandler(removeSudo, filters=command(BotCommands.RmSudoCommand) & CustomFilters.sudo))
