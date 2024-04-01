from telethon import TelegramClient, events, Button
import secrets

client: TelegramClient = TelegramClient("bot_session", secrets.API_ID, secrets.API_HASH)

# 
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

# Buttons controller 
@client.on(events.NewMessage())
async def start(event: events.NewMessage.Event) -> None:
    button_text = event.text
    if button_text == "Send data":
        await event.respond("You chose 'Send data'")
    elif button_text == "View data":
        await event.respond("You chose 'View data'")
    elif button_text == "Search matches":
        await event.respond("You chose 'Search matches'")



client.start()
client.run_until_disconnected()
