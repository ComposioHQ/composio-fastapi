"""
API for the gmail server.
"""

import dotenv
from fastapi import FastAPI, HTTPException
from typing import List

from .models import (
    RunGmailAgentRequest,
    CreateConnectionRequest,
    WaitForConnectionRequest,
    FetchEmailsRequest,
)
from ..agent import run_gmail_agent
from .actions import composio_fetch_emails
from ..connection import (
    create_connection,
    get_connection_status,
    check_connected_account_exists,
)
from .dependencies import ComposioClient, OpenAIClient
from composio.types import ToolExecutionResponse


def validate_user_id(user_id: str, composio_client: ComposioClient):
    """
    Validate the user id, if no connected account is found, create a new connection.
    """
    if check_connected_account_exists(composio_client=composio_client, user_id=user_id):
        return user_id

    raise HTTPException(
        status_code=404, detail={"error": "No connected account found for the user id"}
    )


def create_app():
    """
    Create a FastAPI app
    """
    # Load the environment variables
    dotenv.load_dotenv()

    # Create the FastAPI app
    app = FastAPI()

    # Endpoint: Create a new connection for a user
    @app.post("/connection/exists")
    def _get_connection(composio_client: ComposioClient) -> dict:
        """
        Check if a connection exists for a given user id.
        """
        # For demonstration, using a default user_id. Replace with real user logic in production.
        user_id = "default"

        # Check if a connection exists for the user
        return {
            "exists": check_connected_account_exists(
                composio_client=composio_client, user_id=user_id
            )
        }

    # Endpoint: Create a new connection for a user
    @app.post("/connection/create")
    def _create_connection(
        request: CreateConnectionRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Create a connection for a given user id and auth config id.
        """
        # For demonstration, using a default user_id. Replace with real user logic in production.
        user_id = "default"

        # Create a new connection for the user
        connection_request = create_connection(
            composio_client=composio_client, user_id=user_id
        )
        return {
            "connection_id": connection_request.id,
            "redirect_url": connection_request.redirect_url,
        }

    # Endpoint: Check the status of a connection
    @app.post("/connection/status")
    def _check_connection_status(
        request: WaitForConnectionRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Wait for a connection to be established for a given connection id.
        """
        # Query the connection status using the provided connection_id
        status = get_connection_status(
            composio_client=composio_client,
            connection_id=request.connection_id,
        )
        return {"status": status}

    # Endpoint: Run the Gmail agent for a given user id and prompt
    @app.post("/agent")
    def _run_gmail_agent(
        request: RunGmailAgentRequest,
        composio_client: ComposioClient,
        openai_client: OpenAIClient,
    ) -> List[ToolExecutionResponse]:
        """
        Run the Gmail agent for a given user id and prompt.
        """
        # For demonstration, using a default user_id. Replace with real user logic in production.
        user_id = "default"

        # Validate the user id before proceeding
        user_id = validate_user_id(user_id=user_id, composio_client=composio_client)

        # Run the Gmail agent using Composio and OpenAI
        result = run_gmail_agent(
            composio_client=composio_client,
            openai_client=openai_client,
            user_id=user_id,
            prompt=request.prompt,
        )
        return result

    # Endpoint: Fetch emails for a user
    @app.post("/actions/fetch_emails")
    def _composio_fetch_emails(
        request: FetchEmailsRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Fetch emails for a given user id and limit.
        """
        # Use the Composio action to fetch emails
        result = composio_fetch_emails(
            composio_client=composio_client,
            user_id=request.user_id,
            limit=request.limit,
        )
        if result["error"] is not None:
            raise HTTPException(status_code=500, detail=result["error"])
        return {"emails": result["data"]}

    return app
