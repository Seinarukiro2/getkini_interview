import requests


def send_application(email_data):
    url = "https://api.getkini.com/applications/"

    payload = {
        "company": email_data.get("company", 0),
        "partner_application_id": email_data.get("subject", "string"),
        "partner_job_id": email_data.get("ref_nr", "string"),
        "partner_company_id": "string",
        "partner": 0,
        "agency": 0,
        "applied_at": email_data.get("date_sent", ""),
        "channel": "email",
        "notes": email_data.get("body", "string"),
        "attachments": [],
        "external_job_id": "string",
        "job": 0,
        "candidate": {
            "email": email_data.get("email", "user@example.com"),
            "first_name": email_data.get("name", "string"),
            "last_name": email_data.get("last_name", "string"),
            "full_name": email_data.get("full_name", "string"),
            "gender": "string",
            "phone": "string",
            "location": {"street": "string", "city": email_data.get("location", "string"), "country": "string"},
        },
    }

    # Добавление вложений, если они есть
    attachments = email_data.get("attachments", [])
    for attachment in attachments:
        attachment_type = None
        content_type = None
        if attachment.startswith("Cover_Letter"):
            attachment_type = "cover-letter"
            content_type = "image/jpeg"
        elif attachment.startswith("CV"):
            attachment_type = "cv"
            content_type = "application/pdf"

        if attachment_type and content_type:
            attachment_data = {
                "type": attachment_type,
                "name": attachment,
                "content_type": content_type,
                "data": "string"  # Данные вложения (не указаны в вашем примере)
            }
            payload["attachments"].append(attachment_data)


    headers = {
        "accept": "application/json",
        "Company-Id": email_data.get("id_value", "string"),
        "content-type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response)
    if response.status_code == 401:
        response = "Heeey where is token :("
    return response
