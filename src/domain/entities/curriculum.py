from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
import uuid

from ..value_objects.curriculum_values import FileType

@dataclass
class CurriculumDocument:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str = ""
    file_type: FileType = FileType.UNKNOWN
    file_size: int = 0
    extracted_text: str = ""
    upload_timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    processing_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def is_valid(self) -> bool:
        return bool(self.file_name and self.file_size > 0 and self.file_type != FileType.UNKNOWN)
    
    def get_file_extension(self) -> str:
        return self.file_name.split('.')[-1].lower() if '.' in self.file_name else ""
    
    def mark_as_processed(self, extracted_text: str) -> None:
        self.extracted_text = extracted_text
        self.processed = True
        self.processing_timestamp = datetime.now()
        self.error_message = None
    
    def mark_as_failed(self, error_message: str) -> None:
        self.processed = False
        self.processing_timestamp = datetime.now()
        self.error_message = error_message
    
    @classmethod
    def create(cls, file_name: str, file_type: FileType, file_size: int, file_content: bytes = b"") -> 'CurriculumDocument':
        return cls(file_name=file_name, file_type=file_type, file_size=file_size)


@dataclass
class CurriculumAnalysis:
    """
    Entidade que representa a análise de um currículo
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    experience_years: Optional[str] = None
    position_level: Optional[str] = None
    education: Optional[str] = None
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def add_skill(self, skill: str) -> None:
        """Adiciona uma habilidade se não existir"""
        if skill and skill not in self.skills:
            self.skills.append(skill)
    
    def has_skill(self, skill: str) -> bool:
        """Verifica se possui uma habilidade"""
        return skill.lower() in [s.lower() for s in self.skills]


@dataclass
class AnalysisRequest:
    """
    Entidade que representa uma requisição de análise
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    query: Optional[str] = None
    documents: List[CurriculumDocument] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_document(self, document: CurriculumDocument) -> None:
        """Adiciona um documento à requisição"""
        if document.is_valid():
            self.documents.append(document)
    
    def get_document_count(self) -> int:
        """Retorna o número de documentos"""
        return len(self.documents)
    
    def has_query(self) -> bool:
        """Verifica se tem query específica"""
        return bool(self.query and self.query.strip())


@dataclass
class QueryMatch:
    """
    Entidade que representa um match entre currículo e query
    """
    document_id: str
    score: float
    reasons: List[str] = field(default_factory=list)
    
    def add_reason(self, reason: str) -> None:
        """Adiciona uma razão do match"""
        if reason and reason not in self.reasons:
            self.reasons.append(reason)


@dataclass
class AnalysisResult:
    """
    Entidade que representa o resultado completo de uma análise
    """
    request_id: str
    analyses: List[CurriculumAnalysis] = field(default_factory=list)
    query_matches: List[QueryMatch] = field(default_factory=list)
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)
    
    def add_analysis(self, analysis: CurriculumAnalysis) -> None:
        """Adiciona uma análise ao resultado"""
        self.analyses.append(analysis)
    
    def add_query_match(self, match: QueryMatch) -> None:
        """Adiciona um match de query ao resultado"""
        self.query_matches.append(match)
    
    def get_best_match(self) -> Optional[QueryMatch]:
        """Retorna o melhor match (maior score)"""
        if not self.query_matches:
            return None
        return max(self.query_matches, key=lambda m: m.score)
    
    def mark_as_failed(self, error: str) -> None:
        """Marca o resultado como falhado"""
        self.success = False
        self.error_message = error


@dataclass
class UsageAudit:
    """
    Entidade para auditoria de uso do sistema
    """
    request_id: str
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    query: Optional[str] = None
    files_count: int = 0
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    @classmethod
    def from_request_and_result(
        cls, 
        request: AnalysisRequest, 
        result: AnalysisResult
    ) -> 'UsageAudit':
        """Cria auditoria a partir de request e result"""
        return cls(
            request_id=request.id,
            user_id=request.user_id,
            query=request.query,
            files_count=request.get_document_count(),
            processing_time=result.processing_time,
            success=result.success,
            error_message=result.error_message
        )


@dataclass
class ProcessingAudit:
    """
    Entidade para auditoria de operações de processamento
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: str = ""
    document_id: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None
    processing_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[dict] = field(default_factory=dict)
    
    @classmethod
    def create_success(
        cls,
        action: str,
        document_id: Optional[str] = None,
        processing_time_ms: int = 0,
        metadata: Optional[dict] = None
    ) -> 'ProcessingAudit':
        """Cria auditoria de sucesso"""
        return cls(
            action=action,
            document_id=document_id,
            success=True,
            processing_time_ms=processing_time_ms,
            metadata=metadata or {}
        )
    
    @classmethod
    def create_error(
        cls,
        action: str,
        error_message: str,
        document_id: Optional[str] = None,
        processing_time_ms: int = 0,
        metadata: Optional[dict] = None
    ) -> 'ProcessingAudit':
        """Cria auditoria de erro"""
        return cls(
            action=action,
            document_id=document_id,
            success=False,
            error_message=error_message,
            processing_time_ms=processing_time_ms,
            metadata=metadata or {}
        )