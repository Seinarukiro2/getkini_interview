import unittest
from unittest.mock import patch, Mock
from functions.new_application_request import send_application


class TestSendApplication(unittest.TestCase):

    def mock_post_401(*args, **kwargs):
        mock_response = Mock()
        mock_response.status_code = 401
        return mock_response

    @patch("send_application.requests.post")
    def test_send_application_token_required(self, mock_post):
        mock_post.side_effect = self.mock_post_401

        email_data = {
            "company": 1,
            "subject": "Test Application",
            "ref_nr": "12345",
            "date_sent": "2024-04-01T12:00:00Z",
            "body": "Test application body",
            "attachments": ["resume.pdf"],
            "to": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
        }

        response = send_application(email_data)

        self.assertIsNone(response)


if __name__ == "__main__":
    unittest.main()
