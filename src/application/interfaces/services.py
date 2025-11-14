"""
Interfaces de serviços da aplicação
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.entities.curriculum import CurriculumDocument, CurriculumAnalysis, AnalysisRequest, AnalysisResult
from ...domain.value_objects.curriculum_values import FileType, TechnicalSkillSet, ExperienceYears, ProfessionalLevel


class ITextExtractionService(ABC):
    """Interface para serviço de extração de texto"""
    
    @abstractmethod
    def extract_from_bytes(self, content: bytes, file_type: FileType) -> str:
        """Extrai texto de bytes de arquivo"""
        pass
    
    @abstractmethod
    def is_supported_type(self, file_type: FileType) -> bool:
        """Verifica se o tipo de arquivo é suportado"""
        pass


class IIntelligenceService(ABC):
    """Interface para serviço de inteligência (LLM)"""
    
    @abstractmethod
    def analyze_curriculum(self, document: CurriculumDocument) -> CurriculumAnalysis:
        """Analisa um currículo e gera insights"""
        pass
    
    @abstractmethod
    def extract_skills(self, text: str) -> TechnicalSkillSet:
        """Extrai habilidades do texto"""
        pass
    
    @abstractmethod
    def extract_experience(self, text: str) -> ExperienceYears:
        """Extrai anos de experiência"""
        pass
    
    @abstractmethod
    def determine_level(self, text: str, skills: TechnicalSkillSet, experience: ExperienceYears) -> ProfessionalLevel:
        """Determina o nível profissional"""
        pass
    
    @abstractmethod
    def generate_summary(self, text: str, file_name: str) -> str:
        """Gera resumo do currículo"""
        pass
    
    @abstractmethod
    def analyze_query_match(self, analyses: List[CurriculumAnalysis], query: str) -> dict:
        """Analisa match com query específica"""
        pass