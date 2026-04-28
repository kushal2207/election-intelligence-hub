from pydantic import BaseModel, Field
from typing import Optional


class UserLocation(BaseModel):
    jurisdiction_id: str = Field(..., description="UUID of the user's jurisdiction")
    constituency_id: str = Field(..., description="UUID of the user's constituency")


class QueryRequest(BaseModel):
    query_text: str = Field(..., min_length=1, description="Natural language question from the user")
    user_location: UserLocation
    user_language: str = Field(default="en", description="BCP-47 language code, e.g. 'hi', 'ta', 'en'")
