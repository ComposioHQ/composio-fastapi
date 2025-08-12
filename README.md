# Building an AI Agent with Composio and FastAPI

In this guide you will learn how to build a **Gmail Agent** powered by **Composio**. The agent will be able to use various Gmail tools, listed [here](https://docs.composio.dev/toolkits/gmail#tool-list).

## Features

* Composio comes with built in support for gmail authentication and actions (and [300+ more apps](https://docs.composio.dev/toolkits/introduction))
* You can easily use any providers like **OpenAI**, **Anthropic**, **LangChain**, **Vercel AI SDK**, and [more](https://docs.composio.dev/providers/openai).

## Prerequisites

* Python3.x
* [UV](https://docs.astral.sh/uv/getting-started/installation/)
* [Composio](https://platform.composio.dev/auth) API key - Sign up here and navigate to **Settings** in your project dashboard.
* [OpenAI API key](https://platform.openai.com/api-keys)

## Setup

**1. Clone the Repository**

```bash
git clone git@github.com:composiohq/composio-fastapi
cd composio-fastapi/
```

**2. Setup Environment Variables**

Copy the example .env file to create your own:

```bash
cp .env.example .env
```

**3. Fill in the necessary API keys:**

```dotenv
COMPOSIO_API_KEY=your-composio-api-key
OPENAI_API_KEY=your-openai-api-key
```

**4. Create the virtual environment and activate it:**

```bash
make env
source .venv/bin/activate
```

## Building an AI agent to interact with gmail

Let's build a simple AI agent that has access to the **gmail** toolkit. 

```python
from openai import OpenAI
from composio import Composio
from composio_openai import OpenAIProvider


def run_gmail_agent(
    composio_client: Composio[OpenAIProvider],
    openai_client: OpenAI,
    user_id: str,  # Composio uses User ID to store and access user level authentication tokens
    prompt: str,
):
    """
    Run the Gmail agent using composio and openai clients.
    """
    # Step 1: Fetch the list of necessary Gmail tools using Composio
    tools = composio_client.tools.get(
        user_id=user_id,
        tools=[
            "GMAIL_FETCH_EMAILS",
            "GMAIL_SEND_EMAIL",
            "GMAIL_CREATE_EMAIL_DRAFT"
        ]
    )

    # Step 2: Use OpenAI to generate a response based on the prompt and available tools
    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        tools=tools,
        messages=[{"role": "user", "content": prompt}],
    )

    # Step 3: Handle tool calls with Composio and return the result
    result = composio_client.provider.handle_tool_calls(response=response, user_id=user_id)
    return result
```

> **NOTE**: This is a very simple agent without any state management and agentic loop implementation, so the agent won't be able to perform very complicated tasks. If you want to understand how composio can be used with agentic loops, check other cookbooks with more agentic frameworks.

To **invoke** this agent you need to authenticate your users with Composio's managed authentication service.

## Creating Auth Config

<!-- TODO: redirect them to dashboard and remove complexity -->

To authenticate your users with Composio you need an authentication config for the given toolkit(gmail). To create an authentication config for `gmail` you need `client_id` and `client_secret` from your [Google OAuth Console](https://developers.google.com/identity/protocols/oauth2). Once you have the required credentials you can use the following piece of code to set up authentication for `gmail`.

```python
from composio import Composio
from composio_openai import OpenAIProvider

def create_auth_config(composio_client: Composio[OpenAIProvider]):
    """
    Create a auth config for the gmail toolkit.
    """
    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set")

    return composio_client.auth_configs.create(
        toolkit="GMAIL,
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
```


> **NOTE**: 
1. "One Authentication Config Per Project": Ideally, you only need to create one authentication config per project. Before creating a new one, check for an existing auth config in your project.
2. "Composio's Managed Authentication": Composio platform provides native managed authentication to help you fast-track your development. You can use these default auth configs for development. For production, always use your own OAuth app configuration to ensure secure and scalable authentication.

## Authenticating users

### Fetch the Auth Config

The following function fetches the auth config for the Gmail toolkit:

```python
def fetch_auth_config(composio_client: Composio[OpenAIProvider]):
    """
    Fetch the auth config for a given user id.
    """
    auth_configs = composio_client.auth_configs.list() # Fetch all auth configs
    for auth_config in auth_configs.items:
        if auth_config.toolkit == "GMAIL": # Check for Gmail-specific auth config
            return auth_config # Return None if no Gmail auth config is found
        else:
            raise ValueError("No Gmail auth config found. Please create one before proceeding.")

    return None
```

### Creating a connected account for the Auth Config

To authenticate users, you need to initiate a connection for them using the auth config you just fetched. This is done through the Composio connected accounts API. 

```python
from fastapi import FastAPI

# Function to initiate a connected account
def create_connection(composio_client: Composio[OpenAIProvider], user_id: str):
    """
    Create a connection for a given user id and auth config id.
    """
    # Fetch or create the auth config for the gmail toolkit
    auth_config = fetch_auth_config(composio_client=composio_client)

    # Create a connection for the user
    return composio_client.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=auth_config.id,
    )

# Setup FastAPI
app = FastAPI()

# Endpoint for initiating a connection
@app.post("/connection/create")
def _create_connection(
    request: CreateConnectionRequest,
    composio_client: ComposioClient,
) -> dict:
    """
    Create a connection for a given user id.
    """
    # For demonstration, using a default user_id. Replace with real user logic in production.
    user_id = "default"

    # Create a new connection for the user
    connection_request = create_connection(composio_client=composio_client, user_id=user_id)
    return {
        "connection_id": connection_request.id,
        "redirect_url": connection_request.redirect_url,
    }
```


** From your client app, call this endpoint to obtain the **redirect URL** for user authentication. **


## Setup Composio SDK client

We recommend you to use the composio SDK client as a singleton. FastAPI allows [dependency injection](https://fastapi.tiangolo.com/reference/dependencies/) to simplify the usage of SDK clients which are required to be singletons. 

```python
import os
import typing_extensions as te

from composio import Composio
from composio_openai import OpenAIProvider

from fastapi import Depends

_composio_client: Composio[OpenAIProvider] | None = None

def provide_composio_client():
    """
    Provide a Composio client.
    """
    global _composio_client
    if _composio_client is None:
        _composio_client = Composio(provider=OpenAIProvider())
    return _composio_client


ComposioClient = te.Annotated[Composio, Depends(provide_composio_client)]
"""
A Composio client dependency.
"""
```

> Check [dependencies](./simple_gmail_agent/server/dependencies.py) module for more details.


## Invoke the agent via FastAPI

When invoking the agent, make sure to validate the `user_id` to ensure that the request is tied to an authenticated user.

```python
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

        # Warning for inactive accounts, ideally delete them if found
        print(f"[warning] inactive account {account.id} found for user id: {user_id}")
    return False

def validate_user_id(user_id: str, composio_client: ComposioClient):
    """
    Validate the user id, if no connected account is found, create a new connection.

    Raises an HTTPException if no connected account exists for the user.
    """
    if check_connected_account_exists(composio_client=composio_client, user_id=user_id):
        return user_id

    raise HTTPException(
        status_code=404, detail={"error": "No connected account found for the user id"}
    )

# Endpoint: Run the Gmail agent for a given user ID and prompt
@app.post("/agent")
def _run_gmail_agent(
    request: RunGmailAgentRequest,
    composio_client: ComposioClient, # Injected Composio client
    openai_client: OpenAIClient,  # Injected OpenAI client for generating responses
) -> List[ToolExecutionResponse]:
    """
    Run the Gmail agent for a given user id and prompt.
    """
    # For demonstration, we are using a default user_id. Replace this with actual user ID value in production
    user_id = "default"

    # Validate the user ID before invoking the agent
    user_id = validate_user_id(user_id=user_id, composio_client=composio_client)

    # Run the Gmail agent using Composio and OpenAI
    result = run_gmail_agent(
        composio_client=composio_client,
        openai_client=openai_client,
        user_id=user_id,
        prompt=request.prompt,
    )
    return result
```

> **NOTE**: Check [server](./simple_gmail_agent/server/) module for service implementation

## Running the service

We've built an agent that interacts with Gmail using the Composio toolkit, handles connected user accounts. Now, let's run the service.

> For additional utility endpoints, check the code.

Run the HTTP server
   ```bash
   uvicorn simple_gmail_agent.server.api:create_app --factory
   ```


## Best practices

**🎯 Effective Prompts**:
- Be specific: "Send email to john@company.com about tomorrow's 2pm meeting" is clearer than "send email"
- Provide useful context: "Reply to Sarah's email about the budget with our approval"

**🔒 User Management**:
- Use unique, consistent `user_id` for each person.
- Ensure each user has their own Gmail connected account.
- Keep user_id consistent across requests.

## Troubleshooting

**Connection Issues**:
- Verify your `.env` file has valid `COMPOSIO_API_KEY` and `OPENAI_API_KEY`
- Verify that the user has completed Gmail authorization
- Verify that the user_id matches between requests

**API Errors**:
- Check server logs for detailed error messages
- Ensure request payloads follow the expected format.
- Visit `/docs` endpoint for API schema validation

**Gmail API Limits**:
- Gmail has rate limits; the agent will handle these gracefully
- For high-volume usage, consider implementing request queuing
