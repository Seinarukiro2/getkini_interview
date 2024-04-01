from telethon import TelegramClient, events, Button
import secrets
from bot_methods import viewer_menu, eml_menu_callback_handler

client: TelegramClient = TelegramClient("bot_session", secrets.API_ID, secrets.API_HASH)


async def send_menu(event: events.NewMessage.Event) -> None:
    message= '''Hello, I'm GetKini Bot. Use the menu below to control.'''
    buttons = [
        [Button.text("Send data"), Button.text("View data")],
        [Button.text("Search matches")],
    ]
    await event.respond(message, buttons=buttons)

# Start bot command handler
@client.on(events.NewMessage(pattern="/start"))
async def start(event: events.NewMessage.Event) -> None:
    await send_menu(event)
    
@client.on(events.CallbackQuery)
async def callback_handler(event):
    callback_data = event.data.decode('utf-8')
    await eml_menu_callback_handler.handle_callback(event, callback_data)

# Buttons controller 
@client.on(events.NewMessage())
async def start(event: events.NewMessage.Event) -> None:
    button_text = event.text
    if button_text == "Send data":
        await event.respond("You chose 'Send data'")
    elif button_text == "View data":
        await viewer_menu.create_email_message(event)
    elif button_text == "Search matches":
        await event.respond("You chose 'Search matches'")



client.start()
client.run_until_disconnected()
