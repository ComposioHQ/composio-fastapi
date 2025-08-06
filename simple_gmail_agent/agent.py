from openai import OpenAI
from composio import Composio
from composio_openai import OpenAIProvider


def run_gmail_agent(
    composio_client: Composio[OpenAIProvider],
    openai_client: OpenAI,
    user_id: str,
    prompt: str,
):
    """
    Run the Gmail agent using composio and openai clients.
    """
    # Step 1: Fetch the list of necessary Gmail tools with Composio
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
