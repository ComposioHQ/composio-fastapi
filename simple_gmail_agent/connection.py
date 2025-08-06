"""
Utilities for managing composio user connections.
"""

from composio import Composio
from composio_openai import OpenAIProvider


def fetch_auth_config_id(composio_client: Composio[OpenAIProvider], user_id: str):
    """
    Fetch the auth config id for a given user id.
    """
    auth_config_id = composio_client.auth_configs.get(user_id)
    return auth_config_id


def check_connected_account_exists(
    composio_client: Composio[OpenAIProvider],
    user_id: str,
):
    """
    Check if a connected account exists for a given user id.
    """
    connected_accounts = composio_client.connected_accounts.list(user_ids=[user_id])
    for account in connected_accounts.items:
        if account.status == "ACTIVE":
            return True
        print(f"[warning] inactive account {account.id} found for user id: {user_id}")
    return False


def create_connection(
    composio_client: Composio[OpenAIProvider],
    user_id: str,
):
    """
    Create a connection for a given user id and auth config id.
    """
    return composio_client.toolkits.authorize(user_id=user_id, toolkit="GMAIL")


def get_connection_status(
    composio_client: Composio[OpenAIProvider],
    connection_id: str,
) -> str:
    """
    Check the status of a connection for a given connection id.
    """
    connection_object = composio_client.connected_accounts.get(connection_id)
    return connection_object.status
