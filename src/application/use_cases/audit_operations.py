"""
Use Cases para operações de auditoria
"""

from typing import List, Optional

from ..interfaces.repositories import ICurriculumRepository
from ...domain.entities.curriculum import ProcessingAudit


class CreateAuditUseCase:
    """
    Use Case para criar registros de auditoria
    """
    
    def __init__(self, repository: ICurriculumRepository):
        self.repository = repository
    
    async def execute(self, audit: ProcessingAudit) -> None:
        """
        Executa criação de auditoria
        
        Args:
            audit: Registro de auditoria
        """
        await self.repository.save_audit(audit)


class GetAuditHistoryUseCase:
    """
    Use Case para recuperar histórico de auditoria
    """
    
    def __init__(self, repository: ICurriculumRepository):
        self.repository = repository
    
    async def execute(
        self,
        document_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ProcessingAudit]:
        """
        Executa recuperação de histórico
        
        Args:
            document_id: ID do documento (opcional)
            limit: Limite de registros
            
        Returns:
            Lista de registros de auditoria
        """
        return await self.repository.get_audit_history(
            document_id=document_id,
            limit=limit
        )