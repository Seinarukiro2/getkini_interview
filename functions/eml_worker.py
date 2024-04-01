import os
import email
from bs4 import BeautifulSoup
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import re
from typing import List, Dict

def process_email(eml_filename) -> Dict:
    email_data = {}
    attachments = []
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

            # Search for position using regular expressions
            position = None
            position_match = re.search(r'Bewerbung\s+als\s+(.*?)$', body, re.IGNORECASE | re.MULTILINE)
            if position_match:
                position = position_match.group(1).strip()
            
            # Search for RefNr using regular expressions
            ref_nr = None
            ref_nr_match = re.search(r'(?:Ref(?:erenz)?\s*|Referenznummer|ref(?:erence)?\s*|ref\s*|Referal\s*|referal\s*|Referal\s*Number|RefNr\.?\s*-?)\s*[:\.]?\s*(\d{6,}-[a-zA-Z\d]+)', body, re.IGNORECASE)
            if ref_nr_match:
                ref_nr = ref_nr_match.group(1)

            # Search for company using regular expressions
            company = None
            company_match = re.search(r'bei\s+(.*?)\s+ausgeschriebene\s+Stelle', body, re.IGNORECASE)
            if company_match:
                company = company_match.group(1)

            # Check for attachments
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)
                    with open(filename, 'wb') as f:
                        f.write(part.get_payload(decode=True))

            email_data = {
                "sender": sender,
                "subject": subject,
                "date_sent": date_sent,
                "to": to,
                "position": position if position else "(Position not found)",
                "company": company if company else "(Company not found)",
                "ref_nr": ref_nr if ref_nr else "(RefNr not found)",
                "body": body if body else "(No text body found)",
                "attachments": attachments
            }

    return email_data