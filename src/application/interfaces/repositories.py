"""
Interfaces de Repositórios
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.entities.curriculum import CurriculumDocument, CurriculumAnalysis, ProcessingAudit


class ICurriculumRepository(ABC):
    """
    Interface para repositório de currículos
    """
    
    @abstractmethod
    async def save_document(self, document: CurriculumDocument) -> None:
        """Salva um documento de currículo"""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[CurriculumDocument]:
        """Recupera um documento por ID"""
        pass
    
    @abstractmethod
    async def list_documents(self, limit: int = 100, offset: int = 0) -> List[CurriculumDocument]:
        """Lista documentos com paginação"""
        pass
    
    @abstractmethod
    async def update_document(self, document: CurriculumDocument) -> None:
        """Atualiza um documento existente"""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Remove um documento"""
        pass
    
    @abstractmethod
    async def save_analysis(self, analysis: CurriculumAnalysis) -> None:
        """Salva uma análise de currículo"""
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[CurriculumAnalysis]:
        """Recupera uma análise por ID"""
        pass
    
    @abstractmethod
    async def get_analysis_by_document(self, document_id: str) -> Optional[CurriculumAnalysis]:
        """Recupera análise por ID do documento"""
        pass
    
    @abstractmethod
    async def list_analyses(self, limit: int = 100, offset: int = 0) -> List[CurriculumAnalysis]:
        """Lista análises com paginação"""
        pass
    
    @abstractmethod
    async def save_audit(self, audit: ProcessingAudit) -> None:
        """Salva um registro de auditoria"""
        pass
    
    @abstractmethod
    async def get_audit_history(self, document_id: str = None, limit: int = 100) -> List[ProcessingAudit]:
        """Recupera histórico de auditoria"""
        pass