import os
import email
from bs4 import BeautifulSoup
from datetime import datetime
from functions.eml_worker import process_email
import json
import xml.etree.ElementTree as ET
import re

async def handle_callback(event, callback_data) -> None:
    """
    Handle callback data from inline buttons.

    Args:
        event: The event triggering the callback.
        callback_data (str): The callback data received from the button.

    Returns:
        None
    """
    if callback_data.startswith("view_eml_"):
        # Extract the filename from the callback data
        eml_filename = callback_data[len("view_eml_"):]

        # Get absolute path to the 'data' directory
        script_dir = os.getcwd()  # Get the current working directory
        data_dir = os.path.join(script_dir, 'data')

        # Construct the full path to the EML file
        eml_file_path = os.path.join(data_dir, eml_filename)

        # Check if the file exists
        if os.path.exists(eml_file_path):
            email_data = process_email(eml_file_path)
            if email_data:
                sender = email_data["sender"]
                subject = email_data["subject"]
                date_sent = email_data["date_sent"]
                to = email_data["to"]
                position = email_data["position"]
                company = email_data["company"]
                ref_nr = email_data["ref_nr"]
                body = email_data["body"]
                attachments = email_data["attachments"]

                # Prepare message text
                message_text = f"Sender: {sender}\nSubject: {subject}\nDate Sent: {date_sent}\nTo: {to}\nPosition: {position}\nCompany: {company}\nRef Nr: {ref_nr}\n\n{body}"

                # Send message text
                await event.respond(message_text)

                # Send attachments if available
                if attachments:
                    for filename in attachments:
                        if os.path.exists(filename):  # Check if file exists
                            await event.respond(f"Sending attachment: {filename}")
                            await event.client.send_file(event.chat_id, filename, force_document=True)
                            os.remove(filename)  # Remove the file after sending
                        else:
                            await event.respond(f"Attachment not found: {filename}")
                else:
                    await event.respond("No attachments found.")
            else:
                await event.respond("Failed to process email.")
        else:
            await event.respond("File not found.")
