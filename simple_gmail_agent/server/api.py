"""
API for the gmail server.
"""

from fastapi import FastAPI, HTTPException
from typing import List

from .models import (
    RunGmailAgentRequest,
    CreateConnectionRequest,
    WaitForConnectionRequest,
    FetchEmailsRequest,
    SendEmailRequest,
    CreateEmailDraftRequest,
)
from ..agent import run_gmail_agent
from .actions import (
    composio_fetch_emails,
    composio_send_email,
    composio_create_email_draft,
)
from ..connection import create_connection, get_connection_status, check_connected_account_exists
from .dependencies import ComposioClient, OpenAIClient
from composio.types import ToolExecutionResponse

def validate_user_id(user_id: str, composio_client: ComposioClient):
    """
    Validate the user id, if no connected account is found, create a new connection.
    """
    if check_connected_account_exists(composio_client=composio_client, user_id=user_id):
        return user_id
    raise HTTPException(status_code=404, detail={"error": "No connected account found for the user id"})


def create_app():
    """
    Create a FastAPI app
    """

    app = FastAPI()

    # Endpoint: Run the Gmail agent for a given user id and prompt
    @app.post("/run_gmail_agent")
    async def run_gmail_agent_endpoint(
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

    # Endpoint: Create a new connection for a user
    @app.post("/connection/create")
    async def create_connection_endpoint(
        request: CreateConnectionRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Create a connection for a given user id and auth config id.
        """
        # For demonstration, using a default user_id. Replace with real user logic in production.
        user_id = "default" 

        # Create a new connection for the user
        result = create_connection(composio_client=composio_client, user_id=user_id)
        return {
            "connection_id": result.id,
            "redirect_url": result.redirect_url,
        }

    # Endpoint: Check the status of a connection
    @app.post("/connection/status")
    async def wait_for_connection_endpoint(
        request: WaitForConnectionRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Wait for a connection to be established for a given connection id.
        """
        # Query the connection status using the provided connection_id
        result = get_connection_status(
            composio_client=composio_client,
            connection_id=request.connection_id,
        )
        return {"status": result}

    # Endpoint: Fetch emails for a user
    @app.post("/actions/fetch_emails")
    async def composio_fetch_emails_endpoint(
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
        return {"emails": result['data']}

    # Endpoint: Send an email for a user
    @app.post("/actions/send_email")
    async def composio_send_email_endpoint(
        request: SendEmailRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Send an email for a given user id, recipient, subject, and body.
        """
        # Use the Composio action to send an email
        result = composio_send_email(
            composio_client=composio_client,
            user_id=request.user_id,
            email_recipient=request.email_recipient,
            email_subject=request.email_subject,
            email_body=request.email_body,
        )
        if result["error"] is not None:
            raise HTTPException(status_code=500, detail=result["error"])
        return {"message": result['data']}

    # Endpoint: Create an email draft for a user
    @app.post("/actions/create_email_draft")
    async def composio_create_email_draft_endpoint(
        request: CreateEmailDraftRequest,
        composio_client: ComposioClient,
    ) -> dict:
        """
        Create an email draft for a given user id, recipient, subject, and body.
        """
        # Use the Composio action to create an email draft
        result = composio_create_email_draft(
            composio_client=composio_client,
            user_id=request.user_id,
            email_recipient=request.email_recipient,
            email_subject=request.email_subject,
            email_body=request.email_body,
        )
        if result["error"] is not None:
            raise HTTPException(status_code=500, detail=result["error"])
        return {"message": result['data']}

    return app

