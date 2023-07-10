import pymongo
from pyrogram import Client, filters
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, ADMINS, CHANNELS, CUSTOM_FILE_CAPTION
from database.ia_filterdb import save_file
import asyncio
import random
from utils import get_size
from pyrogram.errors import FloodWait


media_filter = filters.document | filters.video | filters.audio

myclient = pymongo.MongoClient(DATABASE_URI)
db = myclient[DATABASE_NAME]
col = db[COLLECTION_NAME]

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def start(client, message):
    try:
        for file_type in ("document", "video", "audio"):
            media = getattr(message, file_type, None)
            if media is not None:
                break
        else:
            return

        media.file_type = file_type
        media.caption = message.caption
        await save_file(media)
        await message.reply_text("Saved In DB")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_message(filters.command("savefile") & filters.user(ADMINS))
async def start(client, message):
    try:
        for file_type in ("document", "video", "audio"):
            media = getattr(message.reply_to_message, file_type, None)
            if media is not None:
                break
        else:
            return

        media.file_type = file_type
        media.caption = message.reply_to_message.caption
        await save_file(media)
        await message.reply_text("Saved In DB")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_message(filters.command("sendall") & filters.user(ADMINS))
async def x(app, msg):
    args = msg.text.split(maxsplit=1)
    if len(args) == 1:
        return await msg.reply_text("Give Chat ID Also Where To Send Files")
    args = args[1]
    try:
        args = int(args)
    except Exception:
        return await msg.reply_text("Chat Id must be an integer not a string")
    jj = await msg.reply_text("Processing...")
    documents = col.find({})
    last_msg = col.find_one({'_id': 'last_msg'})
    if not last_msg:
        col.update_one({'_id': 'last_msg'}, {'$set': {'index': 0}}, upsert=True)
        last_msg = 0
    else:
        last_msg = last_msg.get('index', 0)
    id_list = [{'id': document['_id'], 'file_name': document.get('file_name', 'N/A'), 'file_caption': document.get('caption', 'N/A'), 'file_size': document.get('file_size', 0)} for document in documents]
    await jj.edit(f"Found {len(id_list)} Files In The DB Starting To Send In Chat {args}")
    for j, i in enumerate(id_list[last_msg:], start=last_msg):
        try:
            try:
                await app.send_video(msg.chat.id, i['id'], caption=CUSTOM_FILE_CAPTION.format(file_name=i['file_name'], file_caption=i['file_caption'], file_size=get_size(int(i['file_size']))))
            except Exception as e:
                print(e)
                await app.send_document(msg.chat.id, i['id'], caption=CUSTOM_FILE_CAPTION.format(file_name=i['file_name'], file_caption=i['file_caption'], file_size=get_size(int(i['file_size']))))
            await jj.edit(f"Found {len(id_list)} Files In The DB Starting To Send In Chat {args}\nProcessed: {j+1}")
            col.update_one({'_id': 'last_msg'}, {'$set': {'index': j}}, upsert=True)
            delay = random.randint(3, 6)
            await asyncio.sleep(delay)
        except FloodWait as e:
            print(f"Sleeping for {e.value} seconds.")
            await asyncio.sleep(e.value)
        except Exception as e:
            print(e)
    await jj.delete()
    await msg.reply_text("Completed")

@Client.on_message(filters.command("resetsend") & filters.user(ADMINS))
async def reset_send(app, msg):
    col.update_one({'_id': 'last_msg'}, {'$set': {'index': 0}}, upsert=True)
    await msg.reply_text("Sending process reset. Files will be sent from the beginning.")


@Client.on_message(filters.command("sendkey") & filters.user(ADMINS))
async def send_messages_with_keyword(app, msg):
    try:
        keywords = msg.command[1].split("-")
    except IndexError:
        await msg.reply_text("Please provide keyword(s) to search for in the file names.")
        return
    regex_pattern = "|".join(keywords)
    documents = col.find({"file_name": {"$regex": '|'.join(keywords)}})
    
    id_list = [
        {
            'id': document['_id'],
            'file_name': document.get('file_name', 'N/A'),
            'file_caption': document.get('caption', 'N/A'),
            'file_size': document.get('file_size', 0)
        } 
        for document in documents
    ]
    
    for j, i in enumerate(id_list):
        try:
            try:
                await app.send_video(
                    msg.chat.id,
                    i['id'],
                    caption=CUSTOM_FILE_CAPTION.format(
                        file_name=i['file_name'],
                        file_caption=i['file_caption'],
                        file_size=get_size(int(i['file_size']))
                    )
                )
            except Exception as e:
                print(e)
                await app.send_document(
                    msg.chat.id,
                    i['id'],
                    caption=CUSTOM_FILE_CAPTION.format(
                        file_name=i['file_name'],
                        file_caption=i['file_caption'],
                        file_size=get_size(int(i['file_size']))
                    )
                )
            
            await asyncio.sleep(random.randint(3,6))
        except FloodWait as e:
            print(f"Sleeping for {e.x} seconds.")
            await asyncio.sleep(e.x)
        except Exception as e:
            print(e)
            #await jj.delete()
            await msg.reply_text("An error occurred while sending messages.")
            break
    
    await msg.reply_text("Completed")



@Client.on_message(filters.command('skipseries') & filters.user(ADMINS))
async def skip_series_command(bot, message):
    
    toggle_text = "𝗗𝗜𝗦𝗔𝗕𝗟𝗘" if skip_series else "𝗘𝗡𝗔𝗕𝗟𝗘"
    callback_data = "disable_series" if skip_series else "enable_series"
    button = InlineKeyboardButton(toggle_text, callback_data=callback_data)
    keyboard = InlineKeyboardMarkup([[button]])

    await message.reply("☮️ ᴅɪsᴀʙʟᴇ sᴋɪᴘᴘɪɴɢ sᴇʀɪᴇs ☮️" if skip_series else "☯️ ᴇɴᴀʙʟᴇ sᴋɪᴘᴘɪɴɢ sᴇʀɪᴇs ☯️", reply_markup=keyboard)
    #await message.reply(f"series skipping stats: ({skip_series})", reply_markup=keyboard)
skip_series = True
@Client.on_callback_query(filters.regex("^(disable_series|enable_series)$"))
async def handle_callback(bot, callback_query):
    global skip_series

    if callback_query.data == "enable_series":
        skip_series = True
    elif callback_query.data == "disable_series":
        skip_series = False
    
 

    toggle_text = "𝗗𝗜𝗦𝗔𝗕𝗟𝗘" if skip_series else "𝗘𝗡𝗔𝗕𝗟𝗘"
    callback_data = "disable_series" if skip_series else "enable_series"
    button = InlineKeyboardButton(toggle_text, callback_data=callback_data)
    keyboard = InlineKeyboardMarkup([[button]])

    await callback_query.answer()
    #await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    #Show the current value of skip_series in the message reply
    await callback_query.message.edit_text("☮️ ᴅᴏɴᴇ,sᴇʀɪᴇs ᴡɪʟʟ ɴᴏᴛ sᴀᴠᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ ɴᴏᴡ ᴏɴ ☮️" if skip_series else "☯️ ᴅᴏɴᴇ,sᴇʀɪᴇs ᴄᴀɴ ᴀsʟᴏ sᴀᴠᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ ɴᴏᴡ ᴏɴ ☯️")
