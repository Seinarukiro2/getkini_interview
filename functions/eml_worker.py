import os
import email
from bs4 import BeautifulSoup
from datetime import datetime
import re

async def extract_eml_data(eml_file_path):
    """
    Extract data from the EML file.

    Args:
        eml_file_path (str): The path to the EML file.

    Returns:
        dict: A dictionary containing extracted data.
    """
    # Initialize an empty dictionary to store the extracted data
    eml_data = {}

    # Check if the file exists
    if os.path.exists(eml_file_path):
        # Open and parse the EML file
        with open(eml_file_path, 'r', encoding='utf-8') as file:
            eml_content = file.read()
            msg = email.message_from_string(eml_content)

            # Extract message content
            eml_data['sender'] = msg['From']
            eml_data['subject'] = msg['Subject']
            eml_data['to'] = msg['To']

            # Extract company ID from the recipient's email address
            recipient_email = msg['To']
            if recipient_email:
                match = re.search(r'applications\+(\d+)@getkini\.com', recipient_email)
                if match:
                    eml_data['company_id'] = match.group(1)
                else:
                    eml_data['company_id'] = None

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
            body = ''
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    html_content = part.get_payload(decode=True).decode(errors='ignore')
                    soup = BeautifulSoup(html_content, 'html.parser')
                    # Find all text nodes in the HTML
                    text_nodes = soup.find_all(text=True)
                    # Concatenate text from all text nodes
                    body += '\n'.join(text_nodes)

            # Remove extra spaces and empty lines
            eml_data['body'] = '\n'.join(line.strip() for line in body.splitlines() if line.strip())

            # Format the date_sent
            eml_data['date_sent'] = date_sent if date_sent else None

    return eml_data
