"""
Modelos Pydantic para API
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response do upload de arquivo"""
    document_id: str
    file_name: str
    file_size: int
    message: str


class AnalysisResponse(BaseModel):
    """Response da análise individual"""
    document_id: str
    summary: str
    skills: List[str]
    experience_years: Optional[str] = None
    position_level: Optional[str] = None
    education: Optional[str] = None
    analysis_timestamp: datetime


class QueryAnalysisRequest(BaseModel):
    """Request para análise de query"""
    query: str = Field(..., description="Query para análise de matching")


class MatchResult(BaseModel):
    """Resultado de matching individual"""
    document_id: str
    score: float
    match_reasons: List[str]
    summary: str


class QueryAnalysisResponse(BaseModel):
    """Response da análise de query"""
    query: str
    best_matches: List[MatchResult]
    analysis_reasoning: str


class DocumentInfo(BaseModel):
    """Informações de documento"""
    document_id: str
    file_name: str
    file_type: str
    file_size: int
    processed: bool
    upload_timestamp: datetime
    processing_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Response da listagem de documentos"""
    documents: List[DocumentInfo]
    total: int
    offset: int
    limit: int


class ProcessingAuditInfo(BaseModel):
    """Informações de auditoria"""
    audit_id: str
    action: str
    document_id: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    processing_time_ms: int
    timestamp: datetime
    metadata: Optional[dict] = None


class AuditHistoryResponse(BaseModel):
    """Response do histórico de auditoria"""
    audits: List[ProcessingAuditInfo]
    total: int


class ErrorResponse(BaseModel):
    """Response de erro"""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Response do health check"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict