# Aposta Inteligente

Sistema web que analisa o desempenho recente de equipes de futebol em
competições reais e usa inteligência artificial para gerar previsões e
sugestões de aposta fundamentadas em estatísticas.

O projeto integra três fontes de dados: a **API-Football** (RapidAPI)
fornece fixtures, jogos e estatísticas por partida; o **Google Gemini**
transforma as métricas calculadas em análises preditivas em linguagem
natural; e o **SQLite** armazena os usuários da aplicação.

## Funcionalidades

- Seleção de campeonato, time e modo de análise (confronto entre dois
  times ou análise de um único time)
- Cálculo de métricas recentes: aproveitamento, médias de gols, over/under,
  ambas marcam, escanteios, cartões, posse de bola e mais
- Análise preditiva gerada por IA com probabilidades, pontos fortes e
  fracos e sugestões de aposta por mercado
- Cache em memória para reduzir chamadas à API externa e chamadas por
  partida executadas em paralelo
- Cadastro e login de usuários com proteção CSRF e correção de open redirect

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python, Flask |
| Banco de dados | SQLite (via Flask-SQLAlchemy) |
| Autenticação | Flask-Login, Flask-WTF |
| Cache | Flask-Caching |
| Frontend | Jinja2, Bootstrap 5, JavaScript vanilla |
| APIs externas | API-Football (RapidAPI), Google Gemini |

## Como rodar localmente

Requisitos: Python 3.10 ou superior.

1. Clone o repositório e entre na pasta do projeto.

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure o ambiente. Copie o `.env.example` para `.env` e preencha:

   ```bash
   cp .env.example .env
   ```

   - `API_FOOTBALL_KEY`: chave da API-Football na RapidAPI
   - `GEMINI_KEY`: chave da API do Google Gemini
   - `SECRET_KEY`: opcional. Se vazio, o app gera e persiste uma chave
     localmente na primeira execução (mantida entre reinícios)
   - `DATABASE_URL`: opcional; por padrão usa `sqlite:///analytics.db`

5. Rode o servidor:

   ```bash
   python run.py
   ```

   As tabelas do banco são criadas automaticamente no primeiro boot (o
   arquivo `analytics.db` é gerado em `instance/`).

6. Acesse `http://localhost:5000`, crie uma conta e use o dashboard.

## Estrutura do projeto

```
app/
├── __init__.py                    # create_app, banco, cache, blueprints
├── config.py                      # configuração e validação de ambiente
├── controllers/
│   ├── cliente_api.py             # chamadas à API-Football (rede + cache)
│   ├── calculadora_estatisticas.py # cálculos puros de métricas
│   ├── formatador_jogos.py        # transformação de fixtures/estatísticas
│   ├── analise.py                 # PromptBuilder + ServicoAnalise
│   └── IA.py                      # integração com o Google Gemini
├── models/models.py               # modelo Usuario (SQLAlchemy)
├── routes/                        # auth, main e futebol (blueprints)
├── static/js/                     # times.js, estatisticas.js, analise_ia.js
└── templates/                     # Jinja2 (layout, dashboard, auth, 404/500)
```

## Limitações

- O plano gratuito da API-Football impõe limite de requisições; o cache em
  memória e o paralelismo reduzem, mas não eliminam, esse efeito.
- As previsões geradas pela IA são baseadas exclusivamente nas estatísticas
  fornecidas e não são garantia de resultado.
- O projeto é de demonstração/educação: não incentive, nem seja usado como,
  recomendação financeira de apostas.