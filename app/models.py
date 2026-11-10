from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SourceCitation(BaseModel):
    doc_id: str
    doc_title: str
    doc_number: str
    revision: str
    effective_date: Optional[str] = None
    page: int
    section: Optional[str] = None
    snippet: str
    score: float
    is_superseded: bool = False
    superseded_by: Optional[str] = None

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_title: str
    doc_number: str
    revision: str
    effective_date: Optional[str] = None
    page: int
    section: Optional[str] = None
    content: str
    tokens: List[str] = Field(default_factory=list)
    is_superseded: bool = False
    superseded_by: Optional[str] = None

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Question asked by the shop floor supervisor")
    top_k: Optional[int] = Field(4, ge=1, le=10)
    prefer_latest: Optional[bool] = Field(True, description="Prioritize active revisions over superseded ones")

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceCitation] = Field(default_factory=list)
    is_found: bool = True
    provider: str = "Local Engine"
    model: str = "extractive"
    processing_time_ms: float = 0.0
    superseded_warning: Optional[str] = None

class SystemInfoResponse(BaseModel):
    local_url: str
    network_url: str
    local_ip: str
    port: int
    total_docs: int
    total_chunks: int
    active_provider: str
    docs_summary: List[Dict[str, Any]]
