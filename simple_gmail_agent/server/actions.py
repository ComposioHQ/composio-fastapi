"""
Composio actions for the gmail server.
"""

from composio import Composio
from composio_openai import OpenAIProvider


def composio_fetch_emails(
    composio_client: Composio[OpenAIProvider],
    user_id: str,
    limit: int = 5,
):
    """
    Fetch emails for a given user id and limit.
    """
    # Fetches emails from the user's inbox.
    result = composio_client.tools.execute(
        user_id=user_id, slug="GMAIL_FETCH_EMAILS", arguments={"max_results": limit}
    )
    return result


def composio_send_email(
    composio_client: Composio[OpenAIProvider],
    user_id: str,
    email_recipient: str,
    email_subject: str,
    email_body: str,
):
    """
    Send an email for a given user id, recipient, subject, and body.
    """
    # Sends an email to the user's recipient.
    result = composio_client.tools.execute(
        user_id=user_id,
        slug="GMAIL_SEND_EMAIL",
        arguments={
            "recipient_email": email_recipient,
            "subject": email_subject,
            "body": email_body,
        },
    )
    return result


def composio_create_email_draft(
    composio_client: Composio[OpenAIProvider],
    user_id: str,
    email_recipient: str,
    email_subject: str,
    email_body: str,
):
    """
    Create an email draft for a given user id, recipient, subject, and body.
    """
    # Creates an email draft for the user's recipient.
    result = composio_client.tools.execute(
        user_id=user_id,
        slug="GMAIL_CREATE_EMAIL_DRAFT",
        arguments={
            "recipient_email": email_recipient,
            "subject": email_subject,
            "body": email_body,
        },
    )
    return result
