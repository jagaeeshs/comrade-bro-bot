import os
import logging
from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
import json
import base64
from settings import get_skip_series, set_skip_series

logger = logging.getLogger(__name__)



@Client.on_message(filters.command('skipseries') & filters.user(ADMINS))
async def skip_series_command(bot, message):
    skip_series = get_skip_series()
    toggle_text = "𝗗𝗜𝗦𝗔𝗕𝗟𝗘" if skip_series else "𝗘𝗡𝗔𝗕𝗟𝗘"
    callback_data = "disable_series" if skip_series else "enable_series"
    button = InlineKeyboardButton(toggle_text, callback_data=callback_data)
    keyboard = InlineKeyboardMarkup([[button]])

    await message.reply("☮️ ᴅɪsᴀʙʟᴇ sᴋɪᴘᴘɪɴɢ sᴇʀɪᴇs ☮️" if skip_series else "☯️ ᴇɴᴀʙʟᴇ sᴋɪᴘᴘɪɴɢ sᴇʀɪᴇs ☯️", reply_markup=keyboard)
    #await message.reply(f"series skipping stats: ({skip_series})", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^(disable_series|enable_series)$"))
async def handle_callback(bot, callback_query):
    skip_series = get_skip_series()

    if callback_query.data == "enable_series":
        set_skip_series(True)
    elif callback_query.data == "disable_series":
        set_skip_series(False)
    
 

    toggle_text = "𝗗𝗜𝗦𝗔𝗕𝗟𝗘" if skip_series else "𝗘𝗡𝗔𝗕𝗟𝗘"
    callback_data = "disable_series" if skip_series else "enable_series"
    button = InlineKeyboardButton(toggle_text, callback_data=callback_data)
    keyboard = InlineKeyboardMarkup([[button]])

    await callback_query.answer()
    #await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    #Show the current value of skip_series in the message reply
    await callback_query.message.edit_text("☮️ ᴅᴏɴᴇ,sᴇʀɪᴇs ᴡɪʟʟ ɴᴏᴛ sᴀᴠᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ ɴᴏᴡ ᴏɴ ☮️" if skip_series else "☯️ ᴅᴏɴᴇ,sᴇʀɪᴇs ᴄᴀɴ ᴀsʟᴏ sᴀᴠᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ ɴᴏᴡ ᴏɴ ☯️")
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
# https://t.me/LazyDeveoper
async def verupikkals(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed =0

    success = 0
    async for user in users:
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked+=1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(f"Lazy Broadcast is in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Lazy Broadcast is Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
