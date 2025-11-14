import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ...infrastructure.container.dependency_container import get_container, DependencyContainer
from ...domain.entities.curriculum import CurriculumDocument
from ...domain.value_objects.curriculum_values import FileType
from .models import *

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_dependency_container() -> DependencyContainer:
    return await get_container()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...), container: DependencyContainer = Depends(get_dependency_container)):
    try:
        # Validar tipo de arquivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
        
        file_extension = file.filename.split('.')[-1].lower()
        try:
            file_type = FileType.from_extension(file_extension)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não suportado: {file_extension}"
            )
        
        # Ler conteúdo do arquivo
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validar tamanho
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="Arquivo muito grande (máximo 10MB)")
        
        # Criar documento
        document = CurriculumDocument.create(
            file_name=file.filename,
            file_type=file_type,
            file_size=file_size,
            file_content=file_content
        )
        
        # Salvar no repositório
        repository = container.get_repository()
        await repository.save_document(document)
        
        return FileUploadResponse(
            document_id=document.id,
            file_name=document.file_name,
            file_size=document.file_size,
            message="Arquivo enviado com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/analyze/{document_id}", response_model=AnalysisResponse)
async def analyze_document(
    document_id: str,
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Analisa um documento específico
    """
    try:
        use_case = container.get_analyze_use_case()
        
        # Executar análise
        result = await use_case.execute([document_id])
        
        if not result.analyses:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        analysis = result.analyses[0]
        
        return AnalysisResponse(
            document_id=analysis.document_id,
            summary=analysis.summary,
            skills=analysis.skills,
            experience_years=analysis.experience_years,
            position_level=analysis.position_level,
            education=analysis.education,
            analysis_timestamp=analysis.analysis_timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise do documento {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/analyze/query", response_model=QueryAnalysisResponse)
async def analyze_query(
    request: QueryAnalysisRequest,
    document_ids: Optional[List[str]] = Query(None, description="IDs dos documentos (opcional)"),
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Analisa query contra currículos
    """
    try:
        use_case = container.get_analyze_use_case()
        
        # Se não especificou documentos, usar todos
        if not document_ids:
            repository = container.get_repository()
            documents = await repository.list_documents(limit=100)
            document_ids = [doc.id for doc in documents]
        
        # Executar análise
        result = await use_case.execute(document_ids, query=request.query)
        
        return QueryAnalysisResponse(
            query=request.query,
            best_matches=result.matching_results.get("best_matches", []),
            analysis_reasoning=result.matching_results.get("analysis_reasoning", "")
        )
        
    except Exception as e:
        logger.error(f"Erro na análise de query: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(50, ge=1, le=100, description="Limite de documentos"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Lista documentos enviados
    """
    try:
        repository = container.get_repository()
        documents = await repository.list_documents(limit=limit, offset=offset)
        
        document_infos = [
            DocumentInfo(
                document_id=doc.id,
                file_name=doc.file_name,
                file_type=doc.file_type.value,
                file_size=doc.file_size,
                processed=doc.processed,
                upload_timestamp=doc.upload_timestamp,
                processing_timestamp=doc.processing_timestamp,
                error_message=doc.error_message
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=document_infos,
            total=len(document_infos),
            offset=offset,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Obtém informações de um documento específico
    """
    try:
        repository = container.get_repository()
        document = await repository.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Buscar análise associada
        analysis = await repository.get_analysis_by_document(document_id)
        
        response = {
            "document": DocumentInfo(
                document_id=document.id,
                file_name=document.file_name,
                file_type=document.file_type.value,
                file_size=document.file_size,
                processed=document.processed,
                upload_timestamp=document.upload_timestamp,
                processing_timestamp=document.processing_timestamp,
                error_message=document.error_message
            )
        }
        
        if analysis:
            response["analysis"] = AnalysisResponse(
                document_id=analysis.document_id,
                summary=analysis.summary,
                skills=analysis.skills,
                experience_years=analysis.experience_years,
                position_level=analysis.position_level,
                education=analysis.education,
                analysis_timestamp=analysis.analysis_timestamp
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar documento {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Remove um documento
    """
    try:
        repository = container.get_repository()
        success = await repository.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        return {"message": "Documento removido com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover documento {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/audit", response_model=AuditHistoryResponse)
async def get_audit_history(
    document_id: Optional[str] = Query(None, description="ID do documento (opcional)"),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Obtém histórico de auditoria
    """
    try:
        use_case = container.get_audit_history_use_case()
        audits = await use_case.execute(document_id=document_id, limit=limit)
        
        audit_infos = [
            ProcessingAuditInfo(
                audit_id=audit.id,
                action=audit.action,
                document_id=audit.document_id,
                success=audit.success,
                error_message=audit.error_message,
                processing_time_ms=audit.processing_time_ms,
                timestamp=audit.timestamp,
                metadata=audit.metadata
            )
            for audit in audits
        ]
        
        return AuditHistoryResponse(
            audits=audit_infos,
            total=len(audit_infos)
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de auditoria: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    container: DependencyContainer = Depends(get_dependency_container)
):
    """
    Health check da aplicação
    """
    try:
        # Testar serviços
        services = {}
        
        # Testar repositório
        try:
            repository = container.get_repository()
            # Teste simples - listar documentos
            await repository.list_documents(limit=1)
            services["database"] = "healthy"
        except Exception as e:
            services["database"] = f"unhealthy: {str(e)}"
        
        # Testar serviço de OCR
        try:
            ocr_service = container.get_text_extraction_service()
            services["ocr"] = "healthy"
        except Exception as e:
            services["ocr"] = f"unhealthy: {str(e)}"
        
        # Testar serviço de LLM
        try:
            llm_service = container.get_intelligence_service()
            services["llm"] = "healthy"
        except Exception as e:
            services["llm"] = f"unhealthy: {str(e)}"
        
        # Determinar status geral
        status = "healthy" if all("healthy" in s for s in services.values()) else "degraded"
        
        return HealthCheckResponse(
            status=status,
            services=services
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            services={"error": str(e)}
        )


# Note: Exception handlers devem ser registrados na app principal, não no router