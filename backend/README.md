# Detector de Golpes - Backend

API inteligente desenvolvida com FastAPI e Google Gemini para análise de mensagens e detecção de golpes financeiros.

## 📋 Visão Geral

O backend do Detector de Golpes é responsável pela análise de mensagens, verificação de links e geração de conteúdo educativo. Utiliza uma arquitetura de agentes especializados, onde cada componente é responsável por uma parte específica da análise.

## 🧠 Arquitetura de Agentes

O sistema é composto por vários agentes especializados:

* **AgentManager (manager.py):** Coordena todo o fluxo de análise e integra os resultados dos agentes especializados.
* **MessageAnalyzer (message\_analyzer.py):** Analisa o texto da mensagem usando IA para identificar padrões típicos de golpes.
* **LinkValidator (link\_validator.py):** Verifica URLs contidas na mensagem para identificar domínios suspeitos.
* **EducationAgent (education\_agent.py):** Gera conteúdo educativo personalizado sobre o tipo de golpe detectado.
* **WebSearcher (web\_search.py):** Realiza pesquisas na web para enriquecer a análise com informações atualizadas.

## 🚀 Instalação

### Pré-requisitos

* Python 3.9+
* Chaves de API:
    * Google Gemini API (obrigatória)
    * VirusTotal API (opcional)
    * SerpAPI (opcional)

### Passos para instalação

1.  Clone o repositório:

    ```bash
    git clone [https://github.com/seu-usuario/detector-golpes.git](https://github.com/seu-usuario/detector-golpes.git)
    cd detector-golpes/backend
    ```

2.  Crie e ative um ambiente virtual:

    ```bash
    python -m venv venv
    
    #   Windows
    venv\Scripts\activate
    
    #   Linux/Mac
    source venv/bin/activate
    ```

3.  Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4.  Configure as variáveis de ambiente criando um arquivo `.env` na raiz do projeto:

    ```
    GEMINI_API_KEY=sua_chave_api_gemini_aqui
    VIRUSTOTAL_API_KEY=sua_chave_api_virustotal_aqui
    SERPAPI_API_KEY=sua_chave_api_serpapi_aqui
    ```

5.  Crie os diretórios necessários:

    ```bash
    mkdir -p data analysis_results
    ```

6.  Inicie o servidor:

    ```bash
    uvicorn main:app --reload
    ```

    O servidor estará disponível em http://localhost:8000.

## 📡 API Endpoints

### Analisar Mensagem

`POST /analyze`

**Request Body:**

```json
{
  "message": "Olá, seu cartão foi bloqueado. Clique no link bit.ly/12345 para desbloquear.",
  "user_id": "user123",
  "device_info": {
    "platform": "android",
    "version": "13"
  }
}
```

**Response:**

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_fraud": true,
  "confidence": 0.8,
  "explanation": "Esta mensagem apresenta características típicas de golpe...",
  "recommendations": [
    "Não clique no link fornecido",
    "Entre em contato com seu banco pelos canais oficiais"
  ],
  "education_links": [
    {
      "title": "Como identificar golpes bancários",
      "url": "[https://www.banco.gov.br/seguranca](https://www.banco.gov.br/seguranca)"
    }
  ],
  "educational_text": "Os golpistas frequentemente se passam por bancos...",
  "education_tips": [
    "Nunca forneça senhas por telefone ou mensagens",
    "Verifique sempre a URL antes de inserir dados sensíveis"
  ]
}
```

### Enviar Feedback

`POST /feedback`

**Request Body:**

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "feedback_type": "correct",
  "comment": "A análise foi precisa e me ajudou a evitar um golpe."
}
```

## 🗂️ Estrutura de Arquivos

```
backend/
│
├── main.py              # Ponto de entrada e configuração da API FastAPI
├── manager.py           # Gerenciador de agentes
├── message_analyzer.py  # Analisador de mensagens com IA
├── link_validator.py    # Verificador de links suspeitos
├── education_agent.py   # Gerador de conteúdo educativo
├── web_search.py        # Serviço de pesquisa na web
├── utils.py             # Funções utilitárias
├── config.py            # Configurações e carregamento de API keys
│
├── requirements.txt     # Dependências do projeto
├── .env                 # Variáveis de ambiente (não versionado)
│
└── data/                # Diretório para dados de suporte
    └── blacklists.json  # Lista de domínios maliciosos conhecidos
```

## 🛠️ Solução de Problemas

### Erro de Modelo Gemini

**Problema:** Erro 404 com models/gemini-pro is not found

**Solução:**

* Verifique se está usando o modelo correto em `education_agent.py` e `message_analyzer.py`
* Altere de `gemini-pro` para `gemini-2.0-flash` ou outro modelo disponível
* Verifique se sua chave API tem acesso ao modelo

### Erro no AgentManager

**Problema:** `'str'` object has no attribute `'get'`

**Solução:**

* Verifique se o método `process()` nas classes de agentes retorna dicionários, não strings

## 📊 Monitoramento e Logs

O sistema mantém logs detalhados das análises:

* Logs em `detector.log`
* Resultados de análise em `analysis_results/`

Para visualizar logs em tempo real:

```bash
tail -f detector.log
```

## 🔄 Personalização

### Blacklists Personalizadas

Você pode adicionar domínios conhecidos por fraudes ao arquivo `data/blacklists.json`:

```json
{
  "phishing": [
    "banco-falso.com",
    "atualizar-cartao.net"
  ],
  "malware": [
    "download-virus.com"
  ],
  "scam": [
    "premio-falso.com.br"
  ]
}
```

## 📜 Licença

Este projeto está licenciado sob a Licença MIT.
