// Script de inicialização do MongoDB
// Configura o banco de dados para o Curriculum Analyzer

// Selecionar/criar o banco de dados
db = db.getSiblingDB('curriculum_analyzer');

// Criar coleção de logs de uso com validação
db.createCollection('usage_logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['request_id', 'user_id', 'timestamp', 'files_count', 'processing_time_seconds', 'success'],
            properties: {
                request_id: {
                    bsonType: 'string',
                    description: 'ID único da requisição - obrigatório'
                },
                user_id: {
                    bsonType: 'string',
                    description: 'ID do usuário - obrigatório'
                },
                timestamp: {
                    bsonType: 'date',
                    description: 'Timestamp da requisição - obrigatório'
                },
                query: {
                    bsonType: 'string',
                    description: 'Query fornecida (opcional)'
                },
                files_count: {
                    bsonType: 'int',
                    minimum: 0,
                    description: 'Quantidade de arquivos processados - obrigatório'
                },
                processing_time_seconds: {
                    bsonType: 'double',
                    minimum: 0,
                    description: 'Tempo de processamento em segundos - obrigatório'
                },
                success: {
                    bsonType: 'bool',
                    description: 'Se a operação foi bem-sucedida - obrigatório'
                },
                error_message: {
                    bsonType: 'string',
                    description: 'Mensagem de erro (opcional)'
                }
            }
        }
    }
});

// Criar índices para otimização
db.usage_logs.createIndex({ 'request_id': 1 }, { unique: true });
db.usage_logs.createIndex({ 'user_id': 1, 'timestamp': -1 });
db.usage_logs.createIndex({ 'timestamp': -1 });
db.usage_logs.createIndex({ 'success': 1 });

// Inserir dados de exemplo para teste (opcional)
db.usage_logs.insertMany([
    {
        request_id: 'example-001',
        user_id: 'fabio.recruiter',
        timestamp: new Date(),
        query: 'Desenvolvedor Python sênior',
        files_count: 3,
        processing_time_seconds: 15.5,
        success: true
    },
    {
        request_id: 'example-002',
        user_id: 'fabio.recruiter',
        timestamp: new Date(Date.now() - 3600000), // 1 hora atrás
        files_count: 2,
        processing_time_seconds: 8.2,
        success: true
    }
]);

// Log de inicialização
print('✅ MongoDB inicializado para Curriculum Analyzer');
print('📊 Coleção usage_logs criada com validação');
print('🔍 Índices otimizados criados');
print('📝 Dados de exemplo inseridos');