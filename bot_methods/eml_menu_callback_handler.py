import os
import email
from bs4 import BeautifulSoup
from telethon.tl.types import DocumentAttributeFilename
from datetime import datetime
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
        data_dir = os.path.join(parent_dir, 'data')

        # Construct the full path to the EML file
        eml_file_path = os.path.join(data_dir, eml_filename)

        # Check if the file exists
        if os.path.exists(eml_file_path):
            # Open and parse the EML file
            with open(eml_file_path, 'r', encoding='utf-8') as file:
                eml_data = file.read()
                msg = email.message_from_string(eml_data)

                # Extract message content
                sender = msg['From']
                subject = msg['Subject']
                to = msg['To']
                
                # Try to find date_sent from different parts of the email
                date_sent = None
                
                # First, try to find in the main headers
                date_sent = msg['Date']
                
                # Then, try to find in the HTML body if available
                if not date_sent:
                    for part in msg.walk():
                        if part.get_content_type() == 'text/html':
                            html_content = part.get_payload(decode=True).decode(errors='ignore')
                            # Use regular expression to find date in the format "dd.mm.yyyy"
                            date_match = re.search(r'\b\d{2}\.\d{2}\.\d{4}\b', html_content)
                            if date_match:
                                date_text = date_match.group(0)
                                try:
                                    date_sent = datetime.strptime(date_text, '%d.%m.%Y').strftime('%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    pass
                            break  # stop searching once found
                
                # Extract text body from HTML content
                body = None
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        html_content = part.get_payload(decode=True).decode(errors='ignore')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body = soup.find('body').get_text(separator='\n')

                # Remove extra spaces and empty lines
                if body:
                    body = '\n'.join(line.strip() for line in body.splitlines() if line.strip())

                # Prepare JSON response
                json_response = {
                    "sender": sender,
                    "subject": subject,
                    "date_sent": date_sent,
                    "to": to,
                    "body": body if body else "(No text body found)"
                }

                # Prepare XML response
                xml_response = ET.Element("email")
                ET.SubElement(xml_response, "sender").text = sender
                ET.SubElement(xml_response, "subject").text = subject
                ET.SubElement(xml_response, "date_sent").text = date_sent
                ET.SubElement(xml_response, "to").text = to
                ET.SubElement(xml_response, "body").text = body if body else "(No text body found)"
                xml_string = ET.tostring(xml_response, encoding='unicode')

                # Save JSON and XML files
                json_filename = f"{eml_filename.split('.')[0]}.json"
                xml_filename = f"{eml_filename.split('.')[0]}.xml"
                with open(json_filename, 'w') as json_file:
                    json.dump(json_response, json_file, indent=4)
                with open(xml_filename, 'w') as xml_file:
                    xml_file.write(xml_string)

                # Send JSON and XML files
                await event.respond("Sending JSON file...")
                await event.client.send_file(event.chat_id, json_filename, force_document=True)
                await event.respond("Sending XML file...")
                await event.client.send_file(event.chat_id, xml_filename, force_document=True)

                # Check for attachments and send them
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        await event.respond(f"Sending attachment: {filename}")
                        with open(filename, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        await event.client.send_file(event.chat_id, filename, force_document=True)
                        os.remove(filename)

                # Remove JSON and XML files
                os.remove(json_filename)
                os.remove(xml_filename)

        else:
            await event.respond("File not found.")
