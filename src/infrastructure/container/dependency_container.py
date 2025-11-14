import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..ocr.tesseract_extractor import TesseractTextExtractor
from ..llm.transformers_service import TransformersIntelligenceService
from ..persistence.mongodb_repository import DatabaseConnection, MongoDBCurriculumRepository
from ...application.interfaces.repositories import ICurriculumRepository
from ...application.interfaces.services import ITextExtractionService, IIntelligenceService
from ...application.use_cases.analyze_curriculums import AnalyzeCurriculumsUseCase
from ...application.use_cases.audit_operations import CreateAuditUseCase, GetAuditHistoryUseCase

logger = logging.getLogger(__name__)


class DependencyContainer:
    def __init__(self):
        self._database_connection: Optional[DatabaseConnection] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._repository: Optional[ICurriculumRepository] = None
        self._text_extraction_service: Optional[ITextExtractionService] = None
        self._intelligence_service: Optional[IIntelligenceService] = None
        self._analyze_use_case: Optional[AnalyzeCurriculumsUseCase] = None
        self._audit_create_use_case: Optional[CreateAuditUseCase] = None
        self._audit_history_use_case: Optional[GetAuditHistoryUseCase] = None
    
    async def initialize(self) -> None:
        logger.info("Inicializando container...")
        await self._setup_database()
        self._setup_services()
        self._setup_use_cases()
        logger.info("Container inicializado")
    
    async def _setup_database(self) -> None:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "curriculum_analyzer")
        self._database_connection = DatabaseConnection(mongodb_url, database_name)
        self._database = await self._database_connection.connect()
        self._repository = self._database_connection.get_repository()
    
    def _setup_services(self) -> None:
        self._text_extraction_service = TesseractTextExtractor()
        model_name = os.getenv("LLM_MODEL_NAME")
        self._intelligence_service = TransformersIntelligenceService(model_name)
    
    def _setup_use_cases(self) -> None:
        """Configura use cases da aplicação"""
        if not self._repository:
            raise RuntimeError("Repository não foi inicializado")
        
        if not self._text_extraction_service:
            raise RuntimeError("Text extraction service não foi inicializado")
        
        if not self._intelligence_service:
            raise RuntimeError("Intelligence service não foi inicializado")
        
        # Use case principal
        self._analyze_use_case = AnalyzeCurriculumsUseCase(
            text_extraction_service=self._text_extraction_service,
            intelligence_service=self._intelligence_service,
            audit_repository=self._repository  # Temporariamente usando o mesmo repositório
        )
        
        # Use cases de auditoria
        self._audit_create_use_case = CreateAuditUseCase(self._repository)
        self._audit_history_use_case = GetAuditHistoryUseCase(self._repository)
    
    async def cleanup(self) -> None:
        """Limpa recursos"""
        if self._database_connection:
            await self._database_connection.disconnect()
        
        logger.info("Container limpo")
    
    # Getters para dependências
    
    def get_repository(self) -> ICurriculumRepository:
        """Retorna repositório"""
        if not self._repository:
            raise RuntimeError("Repository não foi inicializado")
        return self._repository
    
    def get_text_extraction_service(self) -> ITextExtractionService:
        """Retorna serviço de extração de texto"""
        if not self._text_extraction_service:
            raise RuntimeError("Text extraction service não foi inicializado")
        return self._text_extraction_service
    
    def get_intelligence_service(self) -> IIntelligenceService:
        """Retorna serviço de inteligência"""
        if not self._intelligence_service:
            raise RuntimeError("Intelligence service não foi inicializado")
        return self._intelligence_service
    
    def get_analyze_use_case(self) -> AnalyzeCurriculumsUseCase:
        """Retorna use case de análise"""
        if not self._analyze_use_case:
            raise RuntimeError("Analyze use case não foi inicializado")
        return self._analyze_use_case
    
    def get_audit_create_use_case(self) -> CreateAuditUseCase:
        """Retorna use case de criação de auditoria"""
        if not self._audit_create_use_case:
            raise RuntimeError("Audit create use case não foi inicializado")
        return self._audit_create_use_case
    
    def get_audit_history_use_case(self) -> GetAuditHistoryUseCase:
        """Retorna use case de histórico de auditoria"""
        if not self._audit_history_use_case:
            raise RuntimeError("Audit history use case não foi inicializado")
        return self._audit_history_use_case


# Instância global do container
_container: Optional[DependencyContainer] = None


async def get_container() -> DependencyContainer:
    """
    Retorna instância do container (singleton)
    
    Returns:
        Container inicializado
    """
    global _container
    
    if _container is None:
        _container = DependencyContainer()
        await _container.initialize()
    
    return _container


async def cleanup_container() -> None:
    """Limpa o container global"""
    global _container
    
    if _container:
        await _container.cleanup()
        _container = None