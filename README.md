# 🧠 Projeto: FastAPI + Genius API + Redis + DynamoDB

## 📋 Descrição do Desafio

Este projeto implementa uma **API REST em Python (FastAPI)** que consome a **API do Genius** para listar as **10 músicas mais populares** de um artista informado.  
Os dados retornados são:
- Armazenados temporariamente no **Redis** (cache por 7 dias);
- Persistidos no **DynamoDB** (histórico de consultas);
- Retornados via endpoint REST documentado no **Swagger UI** (`/docs`).

O sistema também permite:
- Consultar dados do cache (quando disponíveis);
- Forçar a atualização (cache=False);
- Registrar transações com identificador único (UUID v4).

---

## ⚙️ Arquitetura Geral

```
Usuário → FastAPI → Genius API → Redis (cache) → DynamoDB (persistência)
```

---

## 🧰 Tecnologias Utilizadas

- **Python 3.12**
- **FastAPI** — Framework principal da API
- **Uvicorn** — Servidor ASGI
- **Redis** — Armazenamento em cache
- **AWS DynamoDB** — Persistência de histórico
- **Boto3** — SDK AWS
- **Requests** — Consumo da API Genius
- **UUID** — Geração de IDs únicos
- **Docker + Docker Compose** — Ambiente local para Redis e LocalStack

---

## 📁 Estrutura do Projeto

```
fastapi-genius-redis-dynamodb/
│
├── app/
│   ├── main.py                # API principal
│   ├── genius_client.py       # Cliente para API Genius
│   ├── redis_client.py        # Controle de cache
│   └── dynamodb_client.py     # Integração com DynamoDB
│
├── .env                       # Configurações locais (tokens, URLs, etc.)
├── docker-compose.yml         # Containers: Redis e LocalStack
├── requirements.txt           # Dependências do projeto
└── README.md                  # Este arquivo
```

---

## 🚀 Passo a Passo para Execução

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/lucasabrantes1/fastapi-genius-redis-dynamodb
cd fastapi-genius-redis-dynamodb
```

---

### 2️⃣ Criar o ambiente virtual
```bash
python -m venv .venv
source .venv/Scripts/activate     # Windows
# ou
source .venv/bin/activate         # Linux/Mac
```

---

### 3️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configurar variáveis de ambiente
Crie o arquivo **.env** na raiz do projeto:

```bash
GENIUS_API_TOKEN=seu_access_token_aqui
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=seu_access_key_id
AWS_SECRET_ACCESS_KEY=seu_secret_access_key
DYNAMODB_TABLE=artist_transactions
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL_DAYS=7
```

> 🔹 O token Genius é obtido em: [https://genius.com/api-clients](https://genius.com/api-clients)  
> 🔹 As credenciais AWS podem ser criadas no IAM → *Users → Create access key*

---

### 5️⃣ Subir os serviços de apoio com Docker
```bash
docker compose up -d
```
Isso iniciará:
- **Redis** (porta 6379)
- **LocalStack** (porta 4566) — emulador da AWS para testes locais

---

### 6️⃣ Criar a tabela DynamoDB (apenas na primeira execução)
#### Local (via LocalStack):
```bash
aws --endpoint-url=http://localhost:4566 dynamodb create-table   --table-name artist_transactions   --attribute-definitions AttributeName=transaction_id,AttributeType=S   --key-schema AttributeName=transaction_id,KeyType=HASH   --billing-mode PAY_PER_REQUEST   --region us-east-1
```

#### Na AWS real:
Crie manualmente em **DynamoDB → Create Table**:
- Table name: `artist_transactions`
- Partition key: `transaction_id (String)`
- Capacity mode: `On-demand`

---

### 7️⃣ Executar a aplicação
```bash
uvicorn app.main:app --reload
```

Acesse em:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧩 Endpoints Disponíveis

### 🔹 `GET /v1/artists/top-tracks`
Lista as 10 músicas mais populares do artista.

#### Parâmetros:
| Nome | Tipo | Obrigatório | Descrição |
|------|------|--------------|------------|
| `name` | string | ✅ | Nome do artista |
| `cache` | bool | ❌ | `true` (default) usa cache; `false` força atualização |

#### Exemplo:
```bash
# Usando cache
GET /v1/artists/top-tracks?name=Taylor%20Swift

# Forçando atualização
GET /v1/artists/top-tracks?name=Taylor%20Swift&cache=false
```

---

## 💾 Estrutura de dados armazenada

### DynamoDB
```json
{
  "transaction_id": "16cce046-1918-4701-9ab1-559585af65e0",
  "artist_name": "taylor swift",
  "tracks_count": 10,
  "cache_enabled": true,
  "source": "genius",
  "created_at": "2025-10-06T23:48:33.645548+00:00",
  "ttl": 1760485713
}
```

### Redis
```json
{
  "artist": "taylor swift",
  "tracks": [
    {"title": "Love Story", "url": "..."},
    {"title": "Blank Space", "url": "..."}
  ]
}
```

---

## 🧠 Lógica de funcionamento

1. O usuário requisita `/v1/artists/top-tracks?name=<artista>`.
2. A API gera um `transaction_id` (UUID v4).
3. Verifica no Redis se o artista está em cache:
   - ✅ **Se sim:** retorna os dados do cache.
   - ❌ **Se não:** consulta o Genius, salva no Redis (por 7 dias) e registra no DynamoDB.
4. Se `cache=False`, o Redis é limpo e uma nova transação é salva no DynamoDB.

---

## 🧪 Testando manualmente

### Via cURL:
```bash
curl "http://localhost:8000/v1/artists/top-tracks?name=Taylor%20Swift"
```

### Via Swagger:
Acesse [http://localhost:8000/docs](http://localhost:8000/docs) e execute direto pela interface interativa.

---

## ☁️ Visualização do DynamoDB (AWS)

A tabela pode ser visualizada diretamente na **AWS Console**, em:
👉 [https://console.aws.amazon.com/dynamodb/home](https://console.aws.amazon.com/dynamodb/home)

**Passos:**
1. Faça login com seu usuário AWS.
2. Acesse o serviço **DynamoDB**.
3. Vá em **Tables → artist_transactions → Explore items**.
4. Você verá todas as transações registradas.

---

## 🧹 Limpeza do ambiente

Para encerrar containers e liberar recursos:
```bash
docker compose down
```

---

## 👨‍💻 Autor
**Lucas Silva Dantas Abrantes**  
Desenvolvedor Python / Data Engineer  
📧 lucasabrantes002@gmail.com
💼 [LinkedIn](https://www.linkedin.com/in/lucassilvadantasabrantes/)
