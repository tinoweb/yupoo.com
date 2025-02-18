# Plano de Desenvolvimento

## Funcionalidades Atuais

### Sistema de Autenticação
- Login com suporte a email e username
- Uso de JWT para autenticação
- Senhas seguras com bcrypt

### Extração de Dados
- Uso de Selenium para extração de dados do Yupoo
- Armazenamento de imagens e dados em estrutura organizada

### Interface Web
- Formulário para envio de URLs do Yupoo
- Exibição de status e resultados das extrações

## Próximas Implementações

### Painel de Administração
- **Status**: Planejado
- **Descrição**: Implementar um painel para gerenciar usuários e funcionalidades administrativas.
- **Tarefas**:
  - Adicionar campo `is_admin` ao modelo de usuário
  - Criar rotas e interface para administração
  - Implementar autenticação e autorização para administradores

### Fila de Mensagens
- **Status**: Planejado
- **Descrição**: Implementar RabbitMQ ou Celery para tarefas de extração.
- **Tarefas**:
  - Configurar workers para processamento assíncrono
  - Criar endpoints para consulta de status das extrações

### Escalabilidade e Resiliência
- **Status**: Planejado
- **Descrição**: Dockerizar componentes e considerar uso de Kubernetes.

### Melhorias na Interface
- **Status**: Planejado
- **Descrição**: Atualizar interface para suportar operações assíncronas e melhorar a experiência do usuário.

### Segurança e Logs
- **Status**: Planejado
- **Descrição**: Implementar rate limiting e melhorar logs para monitoramento.

---

Este documento será atualizado conforme o progresso do desenvolvimento. Mantenha-o como referência para o status das funcionalidades e próximas etapas.
