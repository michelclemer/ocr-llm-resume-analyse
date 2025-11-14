"""
Casos de uso para auditoria e estatísticas
"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.curriculum import UsageAudit
from ...domain.repositories.audit_repository import IUsageAuditRepository


class GetUserLogsUseCase:
    """
    Caso de uso para recuperar logs de um usuário
    """
    
    def __init__(self, audit_repository: IUsageAuditRepository):
        self.audit_repository = audit_repository
    
    async def execute(self, user_id: str, limit: int = 100, skip: int = 0) -> List[UsageAudit]:
        """
        Recupera logs de um usuário
        
        Args:
            user_id: ID do usuário
            limit: Limite de registros
            skip: Registros para pular
            
        Returns:
            Lista de logs do usuário
        """
        # Validações
        if not user_id or not user_id.strip():
            raise ValueError("User ID é obrigatório")
        
        if limit <= 0:
            limit = 100
        elif limit > 1000:  # Limite máximo
            limit = 1000
        
        if skip < 0:
            skip = 0
        
        # Buscar logs
        logs = await self.audit_repository.find_by_user(user_id, limit)
        
        # Aplicar skip se necessário
        if skip > 0:
            logs = logs[skip:]
        
        return logs


class GetUsageStatisticsUseCase:
    """
    Caso de uso para recuperar estatísticas de uso
    """
    
    def __init__(self, audit_repository: IUsageAuditRepository):
        self.audit_repository = audit_repository
    
    async def execute(
        self, 
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Recupera estatísticas de uso
        
        Args:
            user_id: ID do usuário (opcional)
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            
        Returns:
            Dicionário com estatísticas
        """
        # Validações de data
        if start_date and end_date and start_date > end_date:
            raise ValueError("Data inicial não pode ser maior que data final")
        
        # Buscar estatísticas
        stats = await self.audit_repository.get_statistics(user_id, start_date, end_date)
        
        # Enriquecer com metadados
        stats["query_params"] = {
            "user_id": user_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "generated_at": datetime.now().isoformat()
        }
        
        return stats


class GetRecentActivityUseCase:
    """
    Caso de uso para recuperar atividade recente
    """
    
    def __init__(self, audit_repository: IUsageAuditRepository):
        self.audit_repository = audit_repository
    
    async def execute(self, limit: int = 20) -> List[dict]:
        """
        Recupera atividade recente do sistema
        
        Args:
            limit: Número de atividades recentes
            
        Returns:
            Lista com atividades recentes
        """
        # Validações
        if limit <= 0:
            limit = 20
        elif limit > 100:  # Limite máximo
            limit = 100
        
        # Buscar atividade
        activities = await self.audit_repository.get_recent_activity(limit)
        
        return activities


class GetRequestDetailsUseCase:
    """
    Caso de uso para recuperar detalhes de uma requisição específica
    """
    
    def __init__(self, audit_repository: IUsageAuditRepository):
        self.audit_repository = audit_repository
    
    async def execute(self, request_id: str) -> Optional[UsageAudit]:
        """
        Recupera detalhes de uma requisição específica
        
        Args:
            request_id: ID da requisição
            
        Returns:
            Detalhes da requisição ou None se não encontrada
        """
        # Validação
        if not request_id or not request_id.strip():
            raise ValueError("Request ID é obrigatório")
        
        # Buscar requisição
        audit = await self.audit_repository.find_by_request_id(request_id)
        
        return audit


class CheckSystemHealthUseCase:
    """
    Caso de uso para verificar saúde do sistema
    """
    
    def __init__(self, audit_repository: IUsageAuditRepository):
        self.audit_repository = audit_repository
    
    async def execute(self) -> dict:
        """
        Verifica a saúde geral do sistema
        
        Returns:
            Status de saúde dos componentes
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Verificar database
        try:
            db_healthy = await self.audit_repository.health_check()
            health_status["services"]["database"] = "connected" if db_healthy else "disconnected"
        except Exception:
            health_status["services"]["database"] = "error"
        
        # Determinar status geral
        service_statuses = health_status["services"].values()
        if any(status == "error" for status in service_statuses):
            health_status["status"] = "error"
        elif any(status == "disconnected" for status in service_statuses):
            health_status["status"] = "degraded"
        
        return health_status