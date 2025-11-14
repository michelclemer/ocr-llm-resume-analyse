import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.container.dependency_container import get_container, cleanup_container
from src.presentation.api.controllers import router as api_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando Curriculum Analyzer API...")
    try:
        container = await get_container()
        logger.info("✅ Container iniciado")
        repository = container.get_repository()
        await repository.list_documents(limit=1)
        logger.info("✅ Database OK")
        yield
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise
    finally:
        logger.info("🔄 Finalizando...")
        await cleanup_container()
        logger.info("✅ Finalizado")


app = FastAPI(
    title="Curriculum Analyzer API",
    description="API para análise de currículos com OCR e LLM usando Clean Architecture",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Curriculum Analyzer API", "version": "2.0.0", "docs": "/docs", "health": "/api/v1/health"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)