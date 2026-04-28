from pydantic import BaseModel
from typing import List, Literal


class SourceCitation(BaseModel):
    authority_name: str
    source_detail: str


class QueryResponse(BaseModel):
    status: Literal["success", "partial", "error"]
    execution_trace: List[str]
    final_answer: str
    confidence: Literal["high", "medium", "low"]
    conflict_detected: bool
    source_citations: List[SourceCitation]
