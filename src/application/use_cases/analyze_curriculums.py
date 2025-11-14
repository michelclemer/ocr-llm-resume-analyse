import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ...domain.entities.curriculum import CurriculumDocument, CurriculumAnalysis, ProcessingAudit
from ..interfaces.services import ITextExtractionService, IIntelligenceService
from ..interfaces.repositories import ICurriculumRepository

@dataclass
class AnalysisExecutionResult:
    analyses: List[CurriculumAnalysis]
    matching_results: Optional[Dict[str, Any]] = None
    processing_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None


class AnalyzeCurriculumsUseCase:
    def __init__(self, text_extraction_service: ITextExtractionService, intelligence_service: IIntelligenceService, audit_repository: ICurriculumRepository):
        self.text_extraction_service = text_extraction_service
        self.intelligence_service = intelligence_service
        self.repository = audit_repository
    
    async def execute(
        self, 
        document_ids: List[str], 
        query: Optional[str] = None
    ) -> AnalysisExecutionResult:
        """
        Executa a análise de currículos
        
        Args:
            document_ids: Lista de IDs dos documentos para analisar
            query: Query opcional para matching
            
        Returns:
            Resultado da análise
        """
        start_time = time.time()
        analyses = []
        matching_results = None
        
        try:
            # Processar cada documento
            for doc_id in document_ids:
                try:
                    # Buscar documento
                    document = await self.repository.get_document(doc_id)
                    if not document:
                        continue
                    
                    # Verificar se já foi processado
                    existing_analysis = await self.repository.get_analysis_by_document(doc_id)
                    if existing_analysis:
                        analyses.append(existing_analysis)
                        continue
                    
                    # Extrair texto se necessário
                    if not document.processed:
                        # Simular conteúdo do arquivo para extração
                        text = await self.text_extraction_service.extract_from_bytes(
                            b"",  # Placeholder - em produção seria o conteúdo real
                            document.file_type
                        )
                        document.mark_as_processed(text)
                        await self.repository.update_document(document)
                    
                    # Analisar com inteligência
                    analysis = self.intelligence_service.analyze_curriculum(document)
                    
                    # Salvar análise
                    await self.repository.save_analysis(analysis)
                    analyses.append(analysis)
                    
                    # Criar auditoria de sucesso
                    audit = ProcessingAudit.create_success(
                        action="document_analysis",
                        document_id=doc_id,
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )
                    await self.repository.save_audit(audit)
                    
                except Exception as e:
                    # Criar auditoria de erro
                    audit = ProcessingAudit.create_error(
                        action="document_analysis",
                        error_message=str(e),
                        document_id=doc_id,
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )
                    await self.repository.save_audit(audit)
                    continue
            
            # Análise de matching se query fornecida
            if query and analyses:
                matching_results = self.intelligence_service.analyze_query_match(analyses, query)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return AnalysisExecutionResult(
                analyses=analyses,
                matching_results=matching_results,
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            
            # Auditoria de erro geral
            audit = ProcessingAudit.create_error(
                action="batch_analysis",
                error_message=str(e),
                processing_time_ms=processing_time
            )
            await self.repository.save_audit(audit)
            
            return AnalysisExecutionResult(
                analyses=[],
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )