"""
Value Objects - Objetos de valor imutáveis
"""

from dataclasses import dataclass
from typing import Set, List
from enum import Enum


class FileType(Enum):
    """Tipos de arquivo suportados"""
    PDF = "application/pdf"
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    GIF = "image/gif"
    WEBP = "image/webp"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_filename(cls, filename: str) -> 'FileType':
        """Determina o tipo de arquivo pela extensão"""
        if not filename or '.' not in filename:
            return cls.UNKNOWN
        
        extension = filename.split('.')[-1].lower()
        
        extension_map = {
            'pdf': cls.PDF,
            'jpg': cls.JPG,
            'jpeg': cls.JPEG,
            'png': cls.PNG,
            'bmp': cls.BMP,
            'tiff': cls.TIFF,
            'gif': cls.GIF,
            'webp': cls.WEBP,
        }
        
        return extension_map.get(extension, cls.UNKNOWN)
    
    def is_image(self) -> bool:
        """Verifica se é um tipo de imagem"""
        image_types = {
            self.JPEG, self.JPG, self.PNG, self.BMP, 
            self.TIFF, self.GIF, self.WEBP
        }
        return self in image_types
    
    def is_pdf(self) -> bool:
        """Verifica se é PDF"""
        return self == self.PDF
    
    def is_supported(self) -> bool:
        """Verifica se o tipo é suportado"""
        return self != self.UNKNOWN


class ProfessionalLevel(Enum):
    """Níveis profissionais"""
    JUNIOR = "Júnior"
    PLENO = "Pleno"
    SENIOR = "Sênior"
    ESPECIALISTA = "Especialista"
    UNKNOWN = "Desconhecido"
    
    @classmethod
    def from_text(cls, text: str) -> 'ProfessionalLevel':
        """Determina o nível a partir de texto"""
        if not text:
            return cls.UNKNOWN
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['senior', 'sênior', 'lead', 'líder', 'arquiteto']):
            return cls.SENIOR
        elif any(word in text_lower for word in ['junior', 'júnior', 'trainee', 'estagiário']):
            return cls.JUNIOR
        elif 'pleno' in text_lower:
            return cls.PLENO
        elif 'especialista' in text_lower:
            return cls.ESPECIALISTA
        
        return cls.UNKNOWN


@dataclass(frozen=True)
class TechnicalSkill:
    """Habilidade técnica"""
    name: str
    category: str = "Geral"
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Nome da habilidade não pode ser vazio")
    
    def matches(self, other_skill: str) -> bool:
        """Verifica se corresponde a outra habilidade"""
        return self.name.lower() == other_skill.lower()


@dataclass(frozen=True)
class TechnicalSkillSet:
    """Conjunto de habilidades técnicas"""
    skills: Set[TechnicalSkill]
    
    def __init__(self, skills: List[str]):
        # Converter strings em TechnicalSkill
        skill_objects = set()
        for skill in skills:
            if skill and skill.strip():
                category = self._categorize_skill(skill)
                skill_objects.add(TechnicalSkill(skill.strip(), category))
        
        object.__setattr__(self, 'skills', frozenset(skill_objects))
    
    def _categorize_skill(self, skill: str) -> str:
        """Categoriza uma habilidade"""
        skill_lower = skill.lower()
        
        languages = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby']
        frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express']
        databases = ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sqlite']
        devops = ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'jenkins']
        
        if any(lang in skill_lower for lang in languages):
            return "Linguagem de Programação"
        elif any(fw in skill_lower for fw in frameworks):
            return "Framework"
        elif any(db in skill_lower for db in databases):
            return "Banco de Dados"
        elif any(devops_tool in skill_lower for devops_tool in devops):
            return "DevOps"
        else:
            return "Geral"
    
    def has_skill(self, skill_name: str) -> bool:
        """Verifica se possui uma habilidade"""
        return any(skill.matches(skill_name) for skill in self.skills)
    
    def get_skills_by_category(self, category: str) -> List[TechnicalSkill]:
        """Retorna habilidades de uma categoria"""
        return [skill for skill in self.skills if skill.category == category]
    
    def count(self) -> int:
        """Retorna o número de habilidades"""
        return len(self.skills)
    
    def to_list(self) -> List[str]:
        """Converte para lista de strings"""
        return [skill.name for skill in self.skills]


@dataclass(frozen=True)
class ExperienceYears:
    """Anos de experiência"""
    years: int
    
    def __post_init__(self):
        if self.years < 0:
            raise ValueError("Anos de experiência não pode ser negativo")
    
    @classmethod
    def from_text(cls, text: str) -> 'ExperienceYears':
        """Extrai anos de experiência de texto"""
        import re
        
        if not text:
            return cls(0)
        
        # Padrões para encontrar anos
        patterns = [
            r'(\d+)\s*anos?\s*de\s*experiência',
            r'experiência\s*de\s*(\d+)\s*anos?',
            r'(\d+)\s*years?\s*of\s*experience',
            r'(\d+)\+\s*anos?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return cls(int(match.group(1)))
        
        return cls(0)
    
    def get_level_suggestion(self) -> ProfessionalLevel:
        """Sugere nível baseado nos anos"""
        if self.years >= 5:
            return ProfessionalLevel.SENIOR
        elif self.years >= 2:
            return ProfessionalLevel.PLENO
        elif self.years > 0:
            return ProfessionalLevel.JUNIOR
        else:
            return ProfessionalLevel.UNKNOWN
    
    def __str__(self) -> str:
        return f"{self.years} anos"


@dataclass(frozen=True)
class MatchScore:
    """Score de match entre currículo e requisitos"""
    value: float
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Score deve estar entre 0.0 e 1.0")
    
    @classmethod
    def calculate(
        cls,
        required_skills: List[str],
        candidate_skills: TechnicalSkillSet,
        required_experience: int,
        candidate_experience: ExperienceYears,
        required_level: ProfessionalLevel,
        candidate_level: ProfessionalLevel
    ) -> 'MatchScore':
        """Calcula score de match"""
        score = 0.0
        
        # Score por habilidades (50%)
        if required_skills:
            matched_skills = sum(1 for skill in required_skills if candidate_skills.has_skill(skill))
            skills_score = matched_skills / len(required_skills)
            score += skills_score * 0.5
        
        # Score por experiência (30%)
        if required_experience > 0:
            if candidate_experience.years >= required_experience:
                score += 0.3
            else:
                ratio = candidate_experience.years / required_experience
                score += ratio * 0.3
        
        # Score por nível (20%)
        if required_level != ProfessionalLevel.UNKNOWN:
            level_scores = {
                ProfessionalLevel.JUNIOR: 1,
                ProfessionalLevel.PLENO: 2,
                ProfessionalLevel.SENIOR: 3,
                ProfessionalLevel.ESPECIALISTA: 4
            }
            
            req_score = level_scores.get(required_level, 0)
            cand_score = level_scores.get(candidate_level, 0)
            
            if cand_score >= req_score:
                score += 0.2
            elif abs(cand_score - req_score) <= 1:
                score += 0.1
        
        return cls(min(score, 1.0))
    
    def is_excellent(self) -> bool:
        """Verifica se é um match excelente"""
        return self.value >= 0.8
    
    def is_good(self) -> bool:
        """Verifica se é um bom match"""
        return self.value >= 0.6
    
    def is_poor(self) -> bool:
        """Verifica se é um match pobre"""
        return self.value < 0.4
    
    def __str__(self) -> str:
        return f"{self.value:.2f}"