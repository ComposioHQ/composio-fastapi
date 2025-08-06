from pydantic import BaseModel, Field

class RunGmailAgentRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="The user id of the user to run the Gmail agent for.",
    )
    prompt: str = Field(
        ...,
        description="The prompt to run the Gmail agent for.",
    )

class CreateConnectionRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="The user id of the user to create a connection for.",
    )
    auth_config_id: str = Field(
        ...,
        description="The auth config id of the user to create a connection for.",
    )

class WaitForConnectionRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="The user id of the user to wait for a connection for.",
    )
    connection_id: str = Field(
        ...,
        description="The connection id of the user to wait for a connection for.",
    )

class FetchEmailsRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="The user id of the user to fetch emails for.",
    )
    limit: int = Field(
        5,
        description="The limit of emails to fetch.",
    )

class SendEmailRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="The user id of the user to send an email for.",
    )
    email_recipient: str = Field(
        ...,
        description="The recipient of the email.",
    )
    email_subject: str = Field(
        ...,
        description="The subject of the email.",
    )
    email_body: str = Field(
        ...,
        description="The body of the email.",
    )

class CreateEmailDraftRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="The user id of the user to create an email draft for.",
    )
    email_recipient: str = Field(
        ...,
        description="The recipient of the email.",
    )
    email_subject: str = Field(
        ...,
        description="The subject of the email.",
    )
    email_body: str = Field(
        ...,
        description="The body of the email.",
    )
