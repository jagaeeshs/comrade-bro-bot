from pyrogram import Client
from pyrogram import filters

# Create a Pyrogram client
app = Client("my_bot", bot_token="5965090572:AAEaBQxjFwnaa2_g__n6nLmnKT7kZPq4sVU")

# Function to handle the broadcast command
@app.on_message(filters.command("broadcast") & filters.reply)
def broadcast_command(client, message):
    # Get the replied message
    replied_message = message.reply_to_message

    # Check if the replied message exists and is not a broadcast command
    if replied_message and not replied_message.text.startswith("/broadcast"):
        # Get the message text
        broadcast_message = replied_message.text

        # Retrieve all the dialogs (conversations)
        dialogs = client.iter_dialogs()

        # Iterate over the dialogs and send the broadcast message to each user
        for dialog in dialogs:
            user_id = dialog.chat.id
            client.send_message(chat_id=user_id, text=broadcast_message)

# Start the bot
app.run()
