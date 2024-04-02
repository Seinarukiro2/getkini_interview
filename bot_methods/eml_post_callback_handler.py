import os
from functions.eml_worker import process_email
from functions.new_application_request import send_application


async def send_post_request(event, callback_data) -> None:
    """
    Handle callback data from inline buttons.

    Args:
        event: The event triggering the callback.
        callback_data (str): The callback data received from the button.

    Returns:
        None
    """
    if callback_data.startswith("post_eml_"):
        # Extract the filename from the callback data
        eml_filename = callback_data[len("post_eml_") :]
        eml_data = process_email(eml_filename)
        response = send_application(eml_data)
        await event.respond(f"Request status: {response}")
