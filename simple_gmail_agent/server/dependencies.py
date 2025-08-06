import os
import typing_extensions as te

from composio import Composio
from composio_openai import OpenAIProvider

from openai import OpenAI
from fastapi import Depends, HTTPException, status

def provide_openai_client():
    """
    Provide an OpenAI client.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def provide_composio_client():
    """
    Provide a Composio client.
    """
    api_key = os.getenv("COMPOSIO_API_KEY")
    return Composio(provider=OpenAIProvider())


OpenAIClient = te.Annotated[OpenAI, Depends(provide_openai_client)]
"""
An OpenAI client dependency.
"""

ComposioClient = te.Annotated[Composio, Depends(provide_composio_client)]
"""
A Composio client dependency.
"""
