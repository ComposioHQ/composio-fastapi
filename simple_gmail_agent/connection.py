"""
Utilities for managing composio user connections.
"""

import os

from composio import Composio
from composio_openai import OpenAIProvider

from .constants import GMAIL_TOOLKIT, ENVIRONMENT


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
    # Fetch all connected accounts for the user
    connected_accounts = composio_client.connected_accounts.list(user_ids=[user_id])

    # Check if there's an active connected account
    for account in connected_accounts.items:
        if account.status == "ACTIVE":
            return True

        # Ideally you should not have inactive accounts, but if you do, you should delete them
        print(f"[warning] inactive account {account.id} found for user id: {user_id}")
    return False


def fetch_auth_config(composio_client: Composio[OpenAIProvider]):
    """
    Fetch the auth config for a given user id.
    """
    # Fetch all auth configs for the project
    auth_configs = composio_client.auth_configs.list()

    # Filter out composio managed auth configs
    for auth_config in auth_configs.items:
        if auth_config.is_composio_managed and ENVIRONMENT != "development":
            continue

        # Check if the auth config is for the gmail toolkit
        if auth_config.toolkit == GMAIL_TOOLKIT:
            return auth_config

    return None


def create_auth_config(composio_client: Composio[OpenAIProvider]):
    """
    Create a auth config for the gmail toolkit.
    """
    # In development, we use the composio managed auth config for rapid prototyping
    if ENVIRONMENT == "development":
        return composio_client.auth_configs.create(
            toolkit=GMAIL_TOOLKIT,
            options={
                "type": "use_composio_managed_auth",
            },
        )

    # In production, use your own auth config
    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set")

    return composio_client.auth_configs.create(
        toolkit=GMAIL_TOOLKIT,
        options={
            "name": "default_gmail_auth_config",
            "type": "use_custom_auth",
            "auth_scheme": "OAUTH2",
            "credentials": {
                "client_id": client_id,
                "client_secret": client_secret,
            },
        },
    )


def create_connection(composio_client: Composio[OpenAIProvider], user_id: str):
    """
    Create a connection for a given user id and auth config id.
    """
    # Fetch or create the auth config for the gmail toolkit
    auth_config = fetch_auth_config(composio_client=composio_client)
    if not auth_config:
        auth_config = create_auth_config(composio_client=composio_client)

    # Create a connection for the user
    return composio_client.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=auth_config.id,
    )


def get_connection_status(
    composio_client: Composio[OpenAIProvider],
    connection_id: str,
) -> str:
    """
    Check the status of a connection for a given connection id.
    """
    return composio_client.connected_accounts.get(connection_id).status
