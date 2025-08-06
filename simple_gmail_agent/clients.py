from openai import OpenAI
from composio import Composio
from composio_openai import OpenAIProvider


def create_openai_client(api_key: str | None = None):
    """
    Create and setup an OpenAI client.
    """
    return OpenAI(api_key=api_key)


def create_composio_client(api_key: str | None = None):
    """
    Create and setup a Composio client.
    """
    if api_key is None:
        return Composio(provider=OpenAIProvider())
    return Composio(provider=OpenAIProvider(), api_key=api_key)
