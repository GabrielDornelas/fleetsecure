# FleetSecure - Sistema de Gerenciamento de Frota

FleetSecure é uma aplicação completa para gerenciamento de motoristas e caminhões de frotas, desenvolvida com Django REST Framework no backend e Next.js no frontend.

## Recursos

- **Autenticação de Usuários**: Sistema JWT com refresh tokens e blacklisting
- **Gerenciamento de Usuários/Motoristas**: Cadastro, atualização e remoção
- **Gerenciamento de Caminhões**: Atribuição a motoristas, tracking de informações
- **API RESTful**: Endpoints bem documentados para integração
- **Testes Automatizados**: Testes de unidade, integração e end-to-end

## Stack Tecnológica

### Backend

- **Framework**: Django + Django REST Framework
- **Banco de Dados**: PostgreSQL (Neon)
- **Cache**: Redis (Upstash)
- **Armazenamento**: AWS S3
- **Autenticação**: JWT
- **Contêineres**: Docker

### Frontend

- **Framework**: Next.js (React)
- **Estilização**: Tailwind CSS
- **Gerenciamento de Estado**: React Query
- **Formulários**: React Hook Form
- **Testes E2E**: Playwright

### DevOps

- **CI/CD**: GitHub Actions
- **Hospedagem**: Vercel (frontend + backend)
- **Monitoramento**: Sentry

## Como Executar o Projeto

### Requisitos

- Docker e Docker Compose
- Node.js 16+
- Python 3.9+

### Backend (com Docker)

```bash
# Executar o backend com Docker Compose
docker-compose up
```

### Frontend

```bash
# Instalar dependências
cd frontend
npm install

# Executar em modo de desenvolvimento
npm run dev
```

### Testes

```bash
# Testes de Backend
docker-compose run backend-test

# Testes de Frontend
cd frontend
npm test

# Testes E2E
cd frontend
npm run test:e2e
```

## Estrutura do Projeto

```
fleetsecure/
├── backend/             # API Django
│   ├── fleetsecure/     # Configurações do projeto
│   ├── trucks/          # App de caminhões
│   ├── users/           # App de usuários
│   ├── tests/           # Testes de integração
│   └── utils/           # Utilitários
├── frontend/            # Aplicação Next.js
│   ├── src/
│   │   ├── pages/       # Páginas do Next.js
│   │   ├── components/  # Componentes React
│   │   └── styles/      # Estilos CSS
│   ├── e2e/             # Testes E2E com Playwright
│   └── public/          # Arquivos estáticos
└── .github/             # Workflows do GitHub Actions
```

## API Endpoints

### Autenticação

- `POST /api/v1/auth/login/`: Login com usuário/senha
- `POST /api/v1/auth/refresh/`: Atualizar token JWT
- `POST /api/v1/auth/logout/`: Invalidar token JWT
- `POST /api/v1/auth/verify/`: Verificar token JWT

### Usuários

- `GET /api/v1/users/`: Listar todos usuários (admin)
- `POST /api/v1/users/`: Criar novo usuário
- `GET /api/v1/users/{id}/`: Obter detalhes do usuário
- `PATCH /api/v1/users/{id}/`: Atualizar usuário
- `DELETE /api/v1/users/{id}/`: Excluir usuário
- `GET /api/v1/users/me/`: Obter perfil do usuário atual

### Caminhões

- `GET /api/v1/trucks/`: Listar todos caminhões
- `POST /api/v1/trucks/`: Criar novo caminhão
- `GET /api/v1/trucks/{id}/`: Obter detalhes do caminhão
- `PATCH /api/v1/trucks/{id}/`: Atualizar caminhão
- `DELETE /api/v1/trucks/{id}/`: Excluir caminhão
- `GET /api/v1/trucks/by_user/?user_id=X`: Filtrar caminhões por usuário

## Deploy

O projeto está configurado para deploy automático na Vercel através do GitHub Actions.

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (veja `.env.example` para referência).

## Licença

MIT
