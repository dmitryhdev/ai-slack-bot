from pydantic import BaseModel


class SlackMessage(BaseModel):
    text: str