# 🎯 Curriculum Analyzer API

> **Sistema Inteligente de Análise de Currículos para TechMatch**  
> Desenvolvido especialmente para **Fabio** - Automatize a análise de currículos com OCR + LLM!

## 🌟 Visão Geral

O **Curriculum Analyzer** é uma solução completa que combina OCR (Reconhecimento Óptico de Caracteres) com LLM (Large Language Model) para automatizar a análise de currículos, proporcionando:

- 📄 **Extração automática** de texto de PDFs e imagens
- 🤖 **Análise inteligente** com resumos estruturados  
- 🎯 **Matching inteligente** baseado em queries específicas
- 📊 **Auditoria completa** com logs detalhados
- 🐳 **Deploy simplificado** com Docker

---

## 🚀 Principais Funcionalidades

### 1. 📋 Análise Automática de Currículos
- Suporte a **PDFs** e **imagens** (PNG, JPG, JPEG)
- Extração de texto via **OCR (Tesseract)**
- Geração de **resumos estruturados**
- Identificação automática de:
  - 💼 Habilidades técnicas
  - ⏱️ Anos de experiência  
  - 📊 Nível profissional (Júnior/Pleno/Sênior)
  - 🎓 Formação acadêmica

### 2. 🔍 Query Inteligente
```
"Qual desses currículos se enquadra melhor para a vaga de 
Engenheiro de Software com Python, FastAPI e 3+ anos de experiência?"
```
- **Análise semântica** da query
- **Ranking automático** dos candidatos
- **Justificativas detalhadas** para cada match
- **Score de compatibilidade** por candidato

### 3. 📊 Auditoria e Rastreamento
- **Logs completos** de todas as análises
- **Rastreamento por usuário** e request
- **Estatísticas de uso** e performance
- **Atividade recente** para monitoramento
- ⚠️ **Sem armazenamento** do conteúdo dos arquivos

---

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Uso |
|-----------|------------|-----|
| **Backend** | FastAPI | API REST com Swagger automático |
| **OCR** | Tesseract | Extração de texto de imagens |
| **PDF** | PyPDF2 | Extração de texto de PDFs |
| **LLM** | Transformers (Hugging Face) | Análise inteligente de texto |
| **Database** | MongoDB | Armazenamento de logs |
| **Containerização** | Docker + Docker Compose | Deploy e orquestração |
| **Validação** | Pydantic | Validação e serialização |

---

## 📦 Instalação e Configuração

### Opção 1: Docker (Recomendado) 🐳

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd ocr-fastapi

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env conforme necessário

# 3. Iniciar com Docker Compose
docker-compose up -d

# 4. Verificar se tudo está funcionando
curl http://localhost:8000/health
```

### Opção 2: Instalação Local 💻

#### Pré-requisitos
- Python 3.11+
- MongoDB
- Tesseract OCR

#### Windows
```powershell
# Instalar Tesseract
# Baixar de: https://github.com/UB-Mannheim/tesseract/wiki
# Instalar em: C:\Program Files\tesseract.exe

# Instalar MongoDB
# Baixar de: https://www.mongodb.com/try/download/community

# Configurar projeto
uv sync
cp .env.example .env
# Editar TESSERACT_PATH no .env

# Iniciar aplicação
python main.py
```

#### Linux
```bash
# Instalar dependências do sistema
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por

# Instalar MongoDB
sudo apt-get install mongodb

# Configurar projeto
uv sync
cp .env.example .env

# Iniciar aplicação
python main.py
```

---

## 🎮 Como Usar

### 1. 🌐 Interface Swagger

Acesse: **http://localhost:8000/docs**

### 2. 📤 Análise Básica (Resumos Automáticos)

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "user_id=fabio.recruiter" \
  -F "files=@curriculo1.pdf" \
  -F "files=@curriculo2.png"
```

**Resposta:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true,
  "processed_files": 2,
  "summaries": [
    {
      "file_name": "curriculo1.pdf",
      "file_type": "application/pdf",
      "extracted_text_length": 1250,
      "summary": "Desenvolvedor Python com 4 anos de experiência...",
      "key_skills": ["Python", "FastAPI", "Docker"],
      "experience_years": "4 anos",
      "position_level": "Pleno",
      "education": "Bacharelado em Ciência da Computação"
    }
  ],
  "processing_time_seconds": 12.5
}
```

### 3. 🔍 Query Inteligente

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "user_id=fabio.recruiter" \
  -F "query=Desenvolvedor Python sênior com Docker e FastAPI" \
  -F "files=@curriculo1.pdf" \
  -F "files=@curriculo2.pdf"
```

**Resposta:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "success": true,
  "processed_files": 2,
  "summaries": [...],
  "query_analysis": {
    "query": "Desenvolvedor Python sênior com Docker e FastAPI",
    "best_matches": [
      {
        "file_name": "curriculo1.pdf",
        "score": 0.95,
        "match_reasons": [
          "Domínio em: python, docker, fastapi",
          "Experiência: 6 anos",
          "Nível: Sênior"
        ]
      }
    ],
    "analysis_reasoning": "João Silva é o candidato mais adequado pois possui exatamente as tecnologias solicitadas..."
  }
}
```

### 4. 📊 Auditoria

```bash
# Ver logs de um usuário
curl "http://localhost:8000/logs/fabio.recruiter?limit=10"

# Ver estatísticas gerais
curl "http://localhost:8000/stats"

# Ver atividade recente
curl "http://localhost:8000/activity/recent"
```

---

## 🎯 Exemplos Práticos para Fabio

### Caso 1: Triagem Rápida
```bash
# Fabio recebe 5 currículos e quer resumos rápidos
curl -X POST "http://localhost:8000/analyze" \
  -F "user_id=fabio.recruiter" \
  -F "files=@candidato1.pdf" \
  -F "files=@candidato2.png" \
  -F "files=@candidato3.pdf"
```

### Caso 2: Vaga Específica
```bash
# Vaga: Engenheiro de Software Python Sênior
curl -X POST "http://localhost:8000/analyze" \
  -F "user_id=fabio.recruiter" \
  -F "query=Engenheiro de Software Python sênior com 5+ anos, conhecimento em FastAPI, Docker, PostgreSQL" \
  -F "files=@stack_curriculos/*"
```

### Caso 3: Análise por Área
```bash
# Separar candidatos por área
curl -X POST "http://localhost:8000/analyze" \
  -F "user_id=fabio.recruiter" \
  -F "query=Desenvolvedor Full-Stack com React e Node.js" \
  -F "files=@frontend_candidatos/*"
```

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   OCR Service   │    │   LLM Service   │
│   (Endpoints)   │───▶│   (Tesseract)   │───▶│  (Transformers) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pydantic      │    │  Text Extractor │    │   Intelligence  │
│   (Validation)  │    │    Service      │    │    Analysis     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│     MongoDB     │
│   (Audit Logs)  │
└─────────────────┘
```

### Fluxo de Processamento

1. **📤 Upload**: Fabio envia arquivos via API
2. **🔍 OCR**: Sistema extrai texto (PDF/Imagem)
3. **🤖 LLM**: Análise inteligente e estruturação
4. **🎯 Query**: Matching com requisitos (se fornecido)
5. **📊 Response**: Resumos + Rankings + Justificativas
6. **📝 Log**: Auditoria salva no MongoDB

---

## 📊 API Documentation

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/analyze` | Análise principal de currículos |
| `GET` | `/health` | Status dos serviços |
| `GET` | `/logs/{user_id}` | Histórico de análises |
| `GET` | `/stats` | Estatísticas de uso |
| `GET` | `/activity/recent` | Atividade recente |

### Modelos de Dados

#### AnalyzeRequest
```json
{
  "request_id": "string (UUID)",
  "user_id": "string (required)",
  "query": "string (optional)"
}
```

#### CurriculumSummary
```json
{
  "file_name": "string",
  "file_type": "string",
  "extracted_text_length": "integer",
  "summary": "string",
  "key_skills": ["string"],
  "experience_years": "string",
  "position_level": "string",
  "education": "string"
}
```

---

## 🐳 Deploy com Docker

### Desenvolvimento
```bash
# Iniciar apenas a aplicação
docker-compose up curriculum-analyzer

# Iniciar com MongoDB Express (interface web)
docker-compose --profile dev up
# Acesse: http://localhost:8081
```

### Produção
```bash
# Deploy completo
docker-compose up -d

# Ver logs
docker-compose logs -f curriculum-analyzer

# Backup do banco
docker exec curriculum-analyzer-mongodb mongodump --out /backup
```

### Configurações Docker

#### Volumes
- `mongodb_data`: Dados persistentes do MongoDB
- `./logs`: Logs da aplicação
- `/tmp/uploads`: Arquivos temporários

#### Portas
- `8000`: API principal
- `27017`: MongoDB
- `8081`: MongoDB Express (dev)

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# .env file
HOST=0.0.0.0
PORT=8000
TESSERACT_PATH=/usr/bin/tesseract
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=curriculum_analyzer
MAX_FILES_PER_REQUEST=20
PROCESSING_TIMEOUT=300
```

### Customização do LLM

```python
# Para usar um modelo diferente
llm_service = LLMService(model_name="microsoft/DialoGPT-medium")
```

### OCR em Múltiplos Idiomas

```python
# Configurar idiomas do Tesseract
extractor.extract_text_from_image("curriculo.png", lang="por+eng")
```

---

## 📈 Monitoramento e Performance

### Health Checks

```bash
# Verificar status geral
curl http://localhost:8000/health

# Resposta esperada
{
  "status": "healthy",
  "timestamp": "2025-11-14T15:30:00.000Z",
  "services": {
    "ocr": "available",
    "llm": "available",
    "database": "connected"
  }
}
```

### Métricas de Performance

```bash
# Estatísticas de uso
curl http://localhost:8000/stats

{
  "stats": {
    "total_requests": 150,
    "successful_requests": 145,
    "success_rate": 96.67,
    "total_files_processed": 350,
    "average_processing_time": 15.2,
    "unique_users_count": 5
  }
}
```

### Logs e Debugging

```bash
# Ver logs em tempo real
docker-compose logs -f curriculum-analyzer

# Logs específicos de erro
docker-compose logs curriculum-analyzer | grep ERROR
```

---

## 🛡️ Segurança e Boas Práticas

### Dados Sensíveis
- ✅ **Não armazenamos** conteúdo completo dos currículos
- ✅ **Apenas metadados** são salvos para auditoria
- ✅ **Logs estruturados** para rastreamento
- ✅ **Limpeza automática** de arquivos temporários

### Validações
- 📋 **Tipos de arquivo** suportados verificados
- 📏 **Limite de arquivos** por requisição (20)
- ⏱️ **Timeout** de processamento (300s)
- 🔍 **Validação de dados** com Pydantic

---

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Tesseract não encontrado
```bash
# Erro: tesseract is not installed
# Solução: Instalar Tesseract e configurar PATH
apt-get install tesseract-ocr  # Linux
# ou baixar installer para Windows
```

#### 2. MongoDB não conecta
```bash
# Erro: MongoDB connection failed
# Verificar se está rodando
docker-compose logs mongodb

# Reiniciar se necessário
docker-compose restart mongodb
```

#### 3. Modelo LLM não carrega
```bash
# Erro: Model loading failed
# Verificar memória disponível
free -h

# Usar modelo menor se necessário
export LLM_MODEL_NAME=distilgpt2
```

#### 4. Performance lenta
```bash
# Otimizações:
# - Usar GPU se disponível
# - Reduzir qualidade de imagens grandes
# - Processar em batches menores
# - Aumentar recursos do container
```

---

## 📝 Changelog

### v1.0.0 - Release Inicial
- ✅ OCR completo (PDF + Imagens)
- ✅ LLM para análise inteligente  
- ✅ API FastAPI com Swagger
- ✅ MongoDB para auditoria
- ✅ Docker + Docker Compose
- ✅ Documentação completa

### Próximas Versões
- 🔄 Cache de resultados
- 🔐 Autenticação JWT
- 📊 Dashboard web
- 🚀 Processamento assíncrono
- 📈 Métricas avançadas

---

## 👨‍💻 Para Desenvolvedores

### Estrutura do Projeto
```
ocr-fastapi/
├── main.py                 # API FastAPI principal
├── models.py               # Modelos Pydantic
├── text_extractor_service.py  # Serviço OCR
├── llm_service.py          # Serviço LLM
├── database_repository.py  # Repositório MongoDB
├── Dockerfile              # Container da aplicação
├── docker-compose.yml      # Orquestração
├── pyproject.toml          # Dependências
├── scripts/
│   └── init-mongo.js       # Inicialização MongoDB
└── data/                   # Dados de exemplo
```

### Executar Testes
```bash
# Instalar dependências de teste
uv add pytest pytest-asyncio httpx

# Executar testes
pytest tests/ -v

# Cobertura
pytest --cov=. tests/
```

### Desenvolvimento Local
```bash
# Modo desenvolvimento com reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Debug com logs detalhados
export LOG_LEVEL=DEBUG
python main.py
```

---

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🙋‍♂️ Suporte

Para dúvidas ou problemas:

1. 📖 Consulte esta documentação
2. 🐛 Abra uma issue no GitHub
3. 💬 Entre em contato com a equipe

---

## 🎉 Conclusão

O **Curriculum Analyzer** foi desenvolvido especialmente para resolver os problemas de **Fabio da TechMatch**:

- ✅ **Automatiza** a análise manual de currículos
- ✅ **Economiza horas** de trabalho repetitivo  
- ✅ **Fornece insights** inteligentes sobre candidatos
- ✅ **Mantém auditoria** completa das análises
- ✅ **Deploy simples** com Docker

**Agora Fabio pode focar no que realmente importa: entrevistas e estratégia!** 🚀

---

*Desenvolvido com ❤️ para facilitar a vida do Fabio e da equipe TechMatch*
