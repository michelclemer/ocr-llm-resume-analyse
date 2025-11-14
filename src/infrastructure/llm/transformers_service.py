"""
Implementação do serviço de inteligência usando Transformers
"""

import re
from typing import List, Dict, Any, Optional
import logging

from ...application.interfaces.services import IIntelligenceService
from ...domain.entities.curriculum import CurriculumDocument, CurriculumAnalysis
from ...domain.value_objects.curriculum_values import (
    TechnicalSkillSet, 
    ExperienceYears, 
    ProfessionalLevel, 
    MatchScore
)

logger = logging.getLogger(__name__)


class TransformersIntelligenceService(IIntelligenceService):
    """
    Serviço de inteligência usando regras e padrões + Transformers
    """
    
    def __init__(self, model_name: str = None):
        """
        Inicializa o serviço de inteligência
        
        Args:
            model_name: Nome do modelo (opcional, pode usar versão simplificada)
        """
        self.model_name = model_name
        
        # Lista de habilidades técnicas para detecção
        self.technical_skills_patterns = [
            # Linguagens de Programação
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
            
            # Frameworks Web
            "react", "angular", "vue", "django", "flask", "fastapi", "spring",
            "express", "nodejs", "laravel", "rails", "next.js", "nuxt",
            
            # Bancos de Dados
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch", 
            "sqlite", "oracle", "sql server", "cassandra", "dynamodb",
            
            # DevOps e Cloud
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
            "jenkins", "gitlab ci", "github actions", "ansible", "chef",
            
            # Outras tecnologias
            "git", "linux", "nginx", "apache", "microservices", "api rest",
            "graphql", "machine learning", "data science", "big data",
            "pandas", "numpy", "tensorflow", "pytorch"
        ]
    
    def analyze_curriculum(self, document: CurriculumDocument) -> CurriculumAnalysis:
        """
        Analisa um currículo completo
        
        Args:
            document: Documento do currículo
            
        Returns:
            Análise estruturada do currículo
        """
        text = document.extracted_text
        
        # Extrair informações
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        level = self.determine_level(text, skills, experience)
        summary = self.generate_summary(text, document.file_name)
        education = self._extract_education(text)
        
        # Criar análise
        analysis = CurriculumAnalysis(
            document_id=document.id,
            summary=summary,
            skills=skills.to_list(),
            experience_years=str(experience) if experience.years > 0 else None,
            position_level=level.value if level != ProfessionalLevel.UNKNOWN else None,
            education=education
        )
        
        return analysis
    
    def extract_skills(self, text: str) -> TechnicalSkillSet:
        """
        Extrai habilidades técnicas do texto
        
        Args:
            text: Texto do currículo
            
        Returns:
            Conjunto de habilidades identificadas
        """
        if not text:
            return TechnicalSkillSet([])
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.technical_skills_patterns:
            if skill in text_lower:
                # Verificar se não é parte de outra palavra
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill.title())
        
        return TechnicalSkillSet(found_skills)
    
    def extract_experience(self, text: str) -> ExperienceYears:
        """
        Extrai anos de experiência do texto
        
        Args:
            text: Texto do currículo
            
        Returns:
            Anos de experiência encontrados
        """
        return ExperienceYears.from_text(text)
    
    def determine_level(self, text: str, skills: TechnicalSkillSet, experience: ExperienceYears) -> ProfessionalLevel:
        """
        Determina o nível profissional
        
        Args:
            text: Texto do currículo
            skills: Habilidades identificadas
            experience: Anos de experiência
            
        Returns:
            Nível profissional determinado
        """
        # Primeiro, tentar identificar por palavras-chave no texto
        level_from_text = ProfessionalLevel.from_text(text)
        if level_from_text != ProfessionalLevel.UNKNOWN:
            return level_from_text
        
        # Se não encontrou no texto, usar experiência
        level_from_experience = experience.get_level_suggestion()
        if level_from_experience != ProfessionalLevel.UNKNOWN:
            return level_from_experience
        
        # Como último recurso, usar quantidade de habilidades
        skill_count = skills.count()
        if skill_count >= 10:
            return ProfessionalLevel.SENIOR
        elif skill_count >= 5:
            return ProfessionalLevel.PLENO
        elif skill_count > 0:
            return ProfessionalLevel.JUNIOR
        
        return ProfessionalLevel.UNKNOWN
    
    def generate_summary(self, text: str, file_name: str) -> str:
        """
        Gera resumo do currículo
        
        Args:
            text: Texto extraído
            file_name: Nome do arquivo
            
        Returns:
            Resumo estruturado
        """
        if not text.strip():
            return f"Não foi possível extrair texto significativo de {file_name}"
        
        # Extrair informações para o resumo
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        level = self.determine_level(text, skills, experience)
        education = self._extract_education(text)
        
        # Construir resumo
        summary_parts = []
        
        # Tentar extrair nome do candidato
        candidate_name = self._extract_candidate_name(text)
        if candidate_name:
            summary_parts.append(f"Perfil de {candidate_name}:")
        else:
            summary_parts.append("Perfil do candidato:")
        
        # Adicionar nível
        if level != ProfessionalLevel.UNKNOWN:
            summary_parts.append(f"Profissional de nível {level.value}")
        
        # Adicionar habilidades principais
        if skills.count() > 0:
            main_skills = skills.to_list()[:5]  # Top 5 habilidades
            skills_text = ", ".join(main_skills)
            summary_parts.append(f"com experiência em {skills_text}")
            
            if skills.count() > 5:
                summary_parts.append(f"e outras {skills.count() - 5} tecnologias")
        
        # Adicionar experiência
        if experience.years > 0:
            summary_parts.append(f"({experience} de experiência)")
        
        # Adicionar educação
        if education:
            summary_parts.append(f"Formação: {education}")
        
        # Identificar área de atuação
        area = self._identify_work_area(text)
        if area:
            summary_parts.append(f"Área: {area}")
        
        return ". ".join(summary_parts) + "."
    
    def analyze_query_match(self, analyses: List[CurriculumAnalysis], query: str) -> dict:
        """
        Analisa match com query específica
        
        Args:
            analyses: Lista de análises de currículos
            query: Query para matching
            
        Returns:
            Resultado da análise de matching
        """
        query_requirements = self._parse_query_requirements(query)
        
        matches = []
        for analysis in analyses:
            score = self._calculate_match_score(analysis, query_requirements)
            reasons = self._generate_match_reasons(analysis, query_requirements)
            
            matches.append({
                "document_id": analysis.document_id,
                "score": float(score),
                "match_reasons": reasons,
                "summary": analysis.summary
            })
        
        # Ordenar por score
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Gerar reasoning
        reasoning = self._generate_analysis_reasoning(matches, query)
        
        return {
            "query": query,
            "best_matches": matches,
            "analysis_reasoning": reasoning
        }
    
    def _extract_education(self, text: str) -> Optional[str]:
        """Extrai informações de educação"""
        education_keywords = [
            "bacharelado", "bacharel", "graduação", "graduado",
            "mestrado", "mestre", "doutorado", "doutor", "phd",
            "técnico", "tecnólogo", "superior", "universidade",
            "faculdade", "instituto", "engenharia", "ciência da computação",
            "sistemas de informação", "análise de sistemas"
        ]
        
        text_lower = text.lower()
        found_education = []
        
        for keyword in education_keywords:
            if keyword in text_lower:
                found_education.append(keyword.title())
        
        if found_education:
            return ", ".join(list(set(found_education))[:3])
        
        return None
    
    def _extract_candidate_name(self, text: str) -> Optional[str]:
        """Tenta extrair o nome do candidato das primeiras linhas"""
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip()
            # Nome provável: linha com 2-4 palavras, sem números, não muito longa
            if (2 <= len(line.split()) <= 4 and 
                len(line) < 50 and 
                not any(char.isdigit() for char in line) and
                not any(word in line.lower() for word in ['cv', 'curriculum', 'resumo', 'email', '@'])):
                return line
        
        return None
    
    def _identify_work_area(self, text: str) -> Optional[str]:
        """Identifica área de atuação principal"""
        text_lower = text.lower()
        
        areas = {
            "Desenvolvimento de Software": ["desenvolvedor", "programador", "software", "frontend", "backend"],
            "Ciência de Dados": ["dados", "data", "analytics", "scientist", "analyst"],
            "DevOps/Infraestrutura": ["devops", "infraestrutura", "cloud", "sysadmin", "sre"],
            "Mobile": ["mobile", "android", "ios", "app", "aplicativo"],
            "UI/UX": ["designer", "ui", "ux", "design", "interface"]
        }
        
        for area, keywords in areas.items():
            if any(keyword in text_lower for keyword in keywords):
                return area
        
        return None
    
    def _parse_query_requirements(self, query: str) -> dict:
        """Parse dos requisitos da query"""
        requirements = {
            "skills": [],
            "experience_years": 0,
            "level": ProfessionalLevel.UNKNOWN,
            "keywords": []
        }
        
        query_lower = query.lower()
        
        # Extrair habilidades mencionadas
        for skill in self.technical_skills_patterns:
            if skill in query_lower:
                requirements["skills"].append(skill)
        
        # Extrair anos de experiência
        exp_pattern = r'(\d+)\+?\s*anos?'
        exp_match = re.search(exp_pattern, query_lower)
        if exp_match:
            requirements["experience_years"] = int(exp_match.group(1))
        
        # Extrair nível
        if any(word in query_lower for word in ['senior', 'sênior']):
            requirements["level"] = ProfessionalLevel.SENIOR
        elif any(word in query_lower for word in ['junior', 'júnior']):
            requirements["level"] = ProfessionalLevel.JUNIOR
        elif 'pleno' in query_lower:
            requirements["level"] = ProfessionalLevel.PLENO
        
        # Palavras-chave gerais
        requirements["keywords"] = query.split()
        
        return requirements
    
    def _calculate_match_score(self, analysis: CurriculumAnalysis, requirements: dict) -> float:
        """Calcula score de match"""
        score = 0.0
        
        # Score por habilidades (40%)
        if requirements["skills"]:
            analysis_skills = [skill.lower() for skill in analysis.skills]
            matched_skills = sum(1 for skill in requirements["skills"] if skill in analysis_skills)
            skills_score = matched_skills / len(requirements["skills"])
            score += skills_score * 0.4
        
        # Score por experiência (30%)
        if requirements["experience_years"] > 0 and analysis.experience_years:
            try:
                analysis_years = int(re.search(r'(\d+)', analysis.experience_years).group(1))
                if analysis_years >= requirements["experience_years"]:
                    score += 0.3
                else:
                    ratio = analysis_years / requirements["experience_years"]
                    score += ratio * 0.3
            except:
                pass
        
        # Score por nível (20%)
        if (requirements["level"] != ProfessionalLevel.UNKNOWN and 
            analysis.position_level and
            ProfessionalLevel(analysis.position_level) == requirements["level"]):
            score += 0.2
        
        # Score por palavras-chave no resumo (10%)
        if requirements["keywords"] and analysis.summary:
            summary_lower = analysis.summary.lower()
            keyword_matches = sum(1 for kw in requirements["keywords"] if kw.lower() in summary_lower)
            if len(requirements["keywords"]) > 0:
                keyword_score = keyword_matches / len(requirements["keywords"])
                score += keyword_score * 0.1
        
        return min(score, 1.0)
    
    def _generate_match_reasons(self, analysis: CurriculumAnalysis, requirements: dict) -> List[str]:
        """Gera razões do match"""
        reasons = []
        
        # Razões por habilidades
        if requirements["skills"]:
            analysis_skills = [skill.lower() for skill in analysis.skills]
            matched_skills = [skill for skill in requirements["skills"] if skill in analysis_skills]
            if matched_skills:
                reasons.append(f"Domínio em: {', '.join(matched_skills)}")
        
        # Razões por experiência
        if analysis.experience_years:
            reasons.append(f"Experiência: {analysis.experience_years}")
        
        # Razões por nível
        if analysis.position_level:
            reasons.append(f"Nível: {analysis.position_level}")
        
        # Razões por formação
        if analysis.education:
            reasons.append(f"Formação: {analysis.education}")
        
        return reasons
    
    def _generate_analysis_reasoning(self, matches: List[dict], query: str) -> str:
        """Gera reasoning da análise"""
        if not matches:
            return "Nenhum currículo processado para análise."
        
        best_match = matches[0]
        
        reasoning = f"Baseado na análise da query '{query}', "
        reasoning += f"o candidato mais adequado apresenta score de {best_match['score']:.2f} "
        
        if best_match.get("match_reasons"):
            reasoning += f"devido a: {'; '.join(best_match['match_reasons'])}. "
        
        if len(matches) > 1:
            second_best = matches[1]
            reasoning += f"O segundo colocado tem score {second_best['score']:.2f}. "
        
        # Recomendação baseada no score
        score = best_match['score']
        if score >= 0.8:
            reasoning += "Recomendação: Excelente candidato para a posição."
        elif score >= 0.6:
            reasoning += "Recomendação: Bom candidato, recomendo entrevista."
        elif score >= 0.4:
            reasoning += "Recomendação: Candidato adequado, avaliar outros fatores."
        else:
            reasoning += "Recomendação: Match parcial, considerar requisitos alternativos."
        
        return reasoning