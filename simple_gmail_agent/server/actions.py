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

