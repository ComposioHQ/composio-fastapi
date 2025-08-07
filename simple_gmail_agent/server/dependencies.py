import os
import typing_extensions as te

from composio import Composio
from composio_openai import OpenAIProvider

from openai import OpenAI
from fastapi import Depends


_openai_client: OpenAI | None = None
_composio_client: Composio[OpenAIProvider] | None = None


def provide_openai_client():
    """
    Provide an OpenAI client.
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def provide_composio_client():
    """
    Provide a Composio client.
    """
    global _composio_client
    if _composio_client is None:
        _composio_client = Composio(provider=OpenAIProvider())
    return _composio_client


OpenAIClient = te.Annotated[OpenAI, Depends(provide_openai_client)]
"""
An OpenAI client dependency.
"""

ComposioClient = te.Annotated[Composio, Depends(provide_composio_client)]
"""
A Composio client dependency.
"""
