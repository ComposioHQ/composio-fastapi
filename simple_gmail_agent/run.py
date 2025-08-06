import os
import argparse
import dotenv

from composio import Composio
from composio_openai import OpenAIProvider

from simple_gmail_agent.agent import run_gmail_agent
from simple_gmail_agent.clients import create_openai_client, create_composio_client
from simple_gmail_agent.connection import (
    check_connected_account_exists,
    create_connection,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user_id", type=str, required=True, help="The user id to run the agent for."
    )
    parser.add_argument(
        "--prompt", type=str, required=True, help="The prompt to run the agent for."
    )
    return parser.parse_args()


def validate_user_id(user_id: str, composio_client: Composio[OpenAIProvider]):
    """
    Validate the user id, if no connected account is found, create a new connection.
    """
    if check_connected_account_exists(composio_client=composio_client, user_id=user_id):
        return user_id

    # Prompt the user to connect their account if not already connected
    connection_request = create_connection(
        composio_client=composio_client,
        user_id=user_id,
    )
    print(
        "\n\n==== Please visit the following URL to connect your account: ====\n"
        + str(connection_request.redirect_url)
        + "\n"
        + "=" * 65,
    )
    connection_request.wait_for_connection()
    return user_id


def main():
    # Initialize args and load environment variables
    args = parse_args()
    dotenv.load_dotenv()

    # Initialize clients
    openai_client = create_openai_client(os.getenv("OPENAI_API_KEY"))
    composio_client = create_composio_client(os.getenv("COMPOSIO_API_KEY"))

    # Validate user id
    user_id = validate_user_id(args.user_id, composio_client)

    # Run the agent
    result = run_gmail_agent(
        composio_client=composio_client,
        openai_client=openai_client,
        user_id=user_id,
        prompt=args.prompt,
    )
    print(result)


if __name__ == "__main__":
    main()
