"""
Implementação do repositório usando MongoDB com Motor (async)
"""

import logging
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from ...domain.entities.curriculum import CurriculumDocument, CurriculumAnalysis, ProcessingAudit
from ...application.interfaces.repositories import ICurriculumRepository

logger = logging.getLogger(__name__)


class MongoDBCurriculumRepository(ICurriculumRepository):
    """
    Repositório de currículos usando MongoDB com Motor (async)
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Inicializa o repositório
        
        Args:
            database: Instância do banco de dados MongoDB
        """
        self.database = database
        self.documents_collection: AsyncIOMotorCollection = database.curriculum_documents
        self.analyses_collection: AsyncIOMotorCollection = database.curriculum_analyses
        self.audits_collection: AsyncIOMotorCollection = database.processing_audits
    
    async def save_document(self, document: CurriculumDocument) -> None:
        """
        Salva um documento de currículo
        
        Args:
            document: Documento a ser salvo
        """
        try:
            document_dict = {
                "id": document.id,
                "file_name": document.file_name,
                "file_type": document.file_type.value,
                "file_size": document.file_size,
                "extracted_text": document.extracted_text,
                "upload_timestamp": document.upload_timestamp.isoformat(),
                "processed": document.processed,
                "processing_timestamp": document.processing_timestamp.isoformat() if document.processing_timestamp else None,
                "error_message": document.error_message,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.documents_collection.insert_one(document_dict)
            logger.info(f"Documento salvo: {document.id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar documento {document.id}: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[CurriculumDocument]:
        """
        Recupera um documento por ID
        
        Args:
            document_id: ID do documento
            
        Returns:
            Documento encontrado ou None
        """
        try:
            doc_dict = await self.documents_collection.find_one({"id": document_id})
            
            if not doc_dict:
                return None
            
            return self._dict_to_document(doc_dict)
            
        except Exception as e:
            logger.error(f"Erro ao buscar documento {document_id}: {e}")
            raise
    
    async def list_documents(self, limit: int = 100, offset: int = 0) -> List[CurriculumDocument]:
        """
        Lista documentos com paginação
        
        Args:
            limit: Limite de documentos
            offset: Offset para paginação
            
        Returns:
            Lista de documentos
        """
        try:
            cursor = self.documents_collection.find().skip(offset).limit(limit).sort("upload_timestamp", -1)
            docs = await cursor.to_list(length=limit)
            
            return [self._dict_to_document(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Erro ao listar documentos: {e}")
            raise
    
    async def update_document(self, document: CurriculumDocument) -> None:
        """
        Atualiza um documento existente
        
        Args:
            document: Documento atualizado
        """
        try:
            update_dict = {
                "extracted_text": document.extracted_text,
                "processed": document.processed,
                "processing_timestamp": document.processing_timestamp.isoformat() if document.processing_timestamp else None,
                "error_message": document.error_message,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.documents_collection.update_one(
                {"id": document.id},
                {"$set": update_dict}
            )
            
            logger.info(f"Documento atualizado: {document.id}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar documento {document.id}: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Remove um documento
        
        Args:
            document_id: ID do documento a ser removido
            
        Returns:
            True se removido, False se não encontrado
        """
        try:
            result = await self.documents_collection.delete_one({"id": document_id})
            
            if result.deleted_count > 0:
                # Remover análises associadas também
                await self.analyses_collection.delete_many({"document_id": document_id})
                logger.info(f"Documento removido: {document_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover documento {document_id}: {e}")
            raise
    
    async def save_analysis(self, analysis: CurriculumAnalysis) -> None:
        """
        Salva uma análise de currículo
        
        Args:
            analysis: Análise a ser salva
        """
        try:
            analysis_dict = {
                "id": analysis.id,
                "document_id": analysis.document_id,
                "summary": analysis.summary,
                "skills": analysis.skills,
                "experience_years": analysis.experience_years,
                "position_level": analysis.position_level,
                "education": analysis.education,
                "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.analyses_collection.insert_one(analysis_dict)
            logger.info(f"Análise salva: {analysis.id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise {analysis.id}: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[CurriculumAnalysis]:
        """
        Recupera uma análise por ID
        
        Args:
            analysis_id: ID da análise
            
        Returns:
            Análise encontrada ou None
        """
        try:
            analysis_dict = await self.analyses_collection.find_one({"id": analysis_id})
            
            if not analysis_dict:
                return None
            
            return self._dict_to_analysis(analysis_dict)
            
        except Exception as e:
            logger.error(f"Erro ao buscar análise {analysis_id}: {e}")
            raise
    
    async def get_analysis_by_document(self, document_id: str) -> Optional[CurriculumAnalysis]:
        """
        Recupera análise por ID do documento
        
        Args:
            document_id: ID do documento
            
        Returns:
            Análise encontrada ou None
        """
        try:
            analysis_dict = await self.analyses_collection.find_one({"document_id": document_id})
            
            if not analysis_dict:
                return None
            
            return self._dict_to_analysis(analysis_dict)
            
        except Exception as e:
            logger.error(f"Erro ao buscar análise por documento {document_id}: {e}")
            raise
    
    async def list_analyses(self, limit: int = 100, offset: int = 0) -> List[CurriculumAnalysis]:
        """
        Lista análises com paginação
        
        Args:
            limit: Limite de análises
            offset: Offset para paginação
            
        Returns:
            Lista de análises
        """
        try:
            cursor = self.analyses_collection.find().skip(offset).limit(limit).sort("analysis_timestamp", -1)
            analyses = await cursor.to_list(length=limit)
            
            return [self._dict_to_analysis(analysis) for analysis in analyses]
            
        except Exception as e:
            logger.error(f"Erro ao listar análises: {e}")
            raise
    
    async def save_audit(self, audit: ProcessingAudit) -> None:
        """
        Salva um registro de auditoria
        
        Args:
            audit: Registro de auditoria
        """
        try:
            audit_dict = {
                "id": audit.id,
                "action": audit.action,
                "document_id": audit.document_id,
                "success": audit.success,
                "error_message": audit.error_message,
                "processing_time_ms": audit.processing_time_ms,
                "timestamp": audit.timestamp.isoformat(),
                "metadata": audit.metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.audits_collection.insert_one(audit_dict)
            logger.debug(f"Auditoria salva: {audit.id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar auditoria {audit.id}: {e}")
            raise
    
    async def get_audit_history(self, document_id: str = None, limit: int = 100) -> List[ProcessingAudit]:
        """
        Recupera histórico de auditoria
        
        Args:
            document_id: ID do documento (opcional, para filtrar)
            limit: Limite de registros
            
        Returns:
            Lista de registros de auditoria
        """
        try:
            query = {}
            if document_id:
                query["document_id"] = document_id
            
            cursor = self.audits_collection.find(query).limit(limit).sort("timestamp", -1)
            audits = await cursor.to_list(length=limit)
            
            return [self._dict_to_audit(audit) for audit in audits]
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico de auditoria: {e}")
            raise
    
    def _dict_to_document(self, doc_dict: dict) -> CurriculumDocument:
        """Converte dict do MongoDB para CurriculumDocument"""
        from ...domain.value_objects.curriculum_values import FileType
        
        return CurriculumDocument(
            id=doc_dict["id"],
            file_name=doc_dict["file_name"],
            file_type=FileType(doc_dict["file_type"]),
            file_size=doc_dict["file_size"],
            extracted_text=doc_dict["extracted_text"],
            upload_timestamp=datetime.fromisoformat(doc_dict["upload_timestamp"]),
            processed=doc_dict["processed"],
            processing_timestamp=datetime.fromisoformat(doc_dict["processing_timestamp"]) if doc_dict["processing_timestamp"] else None,
            error_message=doc_dict["error_message"]
        )
    
    def _dict_to_analysis(self, analysis_dict: dict) -> CurriculumAnalysis:
        """Converte dict do MongoDB para CurriculumAnalysis"""
        return CurriculumAnalysis(
            id=analysis_dict["id"],
            document_id=analysis_dict["document_id"],
            summary=analysis_dict["summary"],
            skills=analysis_dict["skills"],
            experience_years=analysis_dict["experience_years"],
            position_level=analysis_dict["position_level"],
            education=analysis_dict["education"],
            analysis_timestamp=datetime.fromisoformat(analysis_dict["analysis_timestamp"])
        )
    
    def _dict_to_audit(self, audit_dict: dict) -> ProcessingAudit:
        """Converte dict do MongoDB para ProcessingAudit"""
        return ProcessingAudit(
            id=audit_dict["id"],
            action=audit_dict["action"],
            document_id=audit_dict["document_id"],
            success=audit_dict["success"],
            error_message=audit_dict["error_message"],
            processing_time_ms=audit_dict["processing_time_ms"],
            timestamp=datetime.fromisoformat(audit_dict["timestamp"]),
            metadata=audit_dict.get("metadata", {})
        )


class DatabaseConnection:
    """
    Classe para gerenciar conexão com MongoDB
    """
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Inicializa conexão
        
        Args:
            connection_string: String de conexão MongoDB
            database_name: Nome do banco de dados
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """
        Conecta ao banco de dados
        
        Returns:
            Instância do banco de dados
        """
        if self.client is None:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.database = self.client[self.database_name]
            
            # Testar conexão
            try:
                await self.client.admin.command('ping')
                logger.info(f"Conectado ao MongoDB: {self.database_name}")
            except Exception as e:
                logger.error(f"Erro ao conectar MongoDB: {e}")
                raise
        
        return self.database
    
    async def disconnect(self) -> None:
        """Desconecta do banco de dados"""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("Desconectado do MongoDB")
    
    def get_repository(self) -> MongoDBCurriculumRepository:
        """
        Retorna instância do repositório
        
        Returns:
            Repositório configurado
        """
        if self.database is None:
            raise RuntimeError("Database não está conectado")
        
        return MongoDBCurriculumRepository(self.database)