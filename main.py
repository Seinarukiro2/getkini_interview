from telethon import TelegramClient, events, Button
from bot_methods import (
    get_eml_menu,
    eml_view_callback_handler,
    eml_post_callback_handler,
)
from secrets import API_ID, API_HASH

client: TelegramClient = TelegramClient("bot_session", API_ID, API_HASH)


async def send_menu(event: events.NewMessage.Event) -> None:
    message = """Hello, I'm GetKini Bot. Use the menu below to control."""
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
    callback_data = event.data.decode("utf-8")
    await eml_view_callback_handler.send_email_data(event, callback_data)
    await eml_post_callback_handler.send_post_request(event, callback_data)


# Buttons controller
@client.on(events.NewMessage())
async def start(event: events.NewMessage.Event) -> None:
    button_text = event.text
    if button_text == "Send data":
        message = """Here you can see all the emails. \n📡 Choose one from the list to post:\n"""
        await get_eml_menu.create_email_message(event, message=message, view=False)
    elif button_text == "View data":
        message = """Here you can see all the emails. \n📃 Choose one from the list to view:\n"""
        await get_eml_menu.create_email_message(event, message=message, view=True)
    elif button_text == "Search matches":
        await event.respond("You chose 'Search matches'")


client.start()
client.run_until_disconnected()
