# Analytics FC

Plataforma web de **Sports Analytics** que coleta estatísticas reais de equipes de futebol nas principais competições do mundo, calcula indicadores de desempenho dos últimos jogos e utiliza inteligência artificial (**Google Gemini**) para gerar análises táticas, probabilidades e projeções fundamentadas em dados.

O projeto integra três camadas:
- **API Pública de Futebol da ESPN**: fornece clubes, calendários de jogos, placares, eventos (gols por tempo e pênaltis) e estatísticas completas por partida na temporada atual — **sem necessidade de chave de API**;
- **Google Gemini (`gemini-3.8-flash`)**: transforma as métricas calculadas em análises preditivas detalhadas para confrontos ou desempenho individual;
- **SQLite**: banco local criado automaticamente na inicialização para gestão de usuários.

## Funcionalidades

- **10 competições suportadas na temporada atual**: Brasileirão Série A, Libertadores, Sul-Americana, Champions League, Premier League, La Liga, Serie A (Itália), Bundesliga, Ligue 1 e Liga Portugal
- **Tabela de classificação em tempo real**: consulta expansível da classificação atual de cada campeonato (pontos corridos ou fase de grupos), integrada também ao contexto da IA
- **Métricas calculadas sobre os últimos 10 jogos**: aproveitamento (geral, casa e fora), médias de gols marcados/sofridos, Over 1.5 / Over 2.5, Ambas Marcam (BTTS), escanteios, finalizações (totais, no alvo e para fora), posse de bola, precisão de passes, faltas, impedimentos, cartões (amarelos e vermelhos), pênaltis convertidos e distribuição de gols no 1º e 2º tempo
- **Dois modos de análise**: análise individual de uma equipe ou comparação lado a lado para confronto entre dois times
- **Análise preditiva com IA**: geração de relatório estruturado com probabilidades, pontos fortes/fracos e tendências estatísticas com nível de confiança
- **Alta performance**: requisições de estatísticas por partida executadas em paralelo (`ThreadPoolExecutor`) combinadas com cache em memória (`Flask-Caching`) e cache local no navegador (`localStorage`)
- **Autenticação segura**: cadastro e login com hash de senha (`Werkzeug`), proteção CSRF (`Flask-WTF`) e validação contra *open redirect*

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python, Flask |
| Banco de dados | SQLite (`Flask-SQLAlchemy`) |
| Autenticação | `Flask-Login`, `Flask-WTF`, `WTForms` |
| Cache | `Flask-Caching` (`SimpleCache`) |
| Frontend | HTML5, Jinja2, Bootstrap 5, JavaScript Vanilla |
| Dados Esportivos | ESPN Public Soccer API (`site.api.espn.com`) |
| Inteligência Artificial | Google Gemini (`google-genai` / `gemini-3.8-flash`) |

## Como rodar localmente

Requisitos: **Python 3.10** ou superior.

1. Clone o repositório e acesse a pasta do projeto:

   ```bash
   git clone https://github.com/luanAlves221/analytics-fc.git
   cd analytics-fc
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # Linux/macOS
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure o arquivo `.env` a partir do `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Preencha a variável `GEMINI_KEY` com sua chave gratuita obtida no [Google AI Studio](https://aistudio.google.com/apikey) (necessária apenas para o botão **Análise com IA**; a consulta de times, tabelas e estatísticas funciona sem nenhuma chave). O banco SQLite (`instance/analytics.db`) e a `SECRET_KEY` de sessão (`instance/secret_key`) são gerados automaticamente na primeira execução.

5. Inicie o servidor:

   ```bash
   python run.py
   ```

6. Acesse `http://localhost:5000`, crie uma conta e utilize o dashboard.

## Estrutura do projeto

```text
app/
├── __init__.py                        # Factory create_app, banco, cache, CSRF e blueprints
├── config.py                          # Configuração de ambiente e geração automática de SECRET_KEY
├── controllers/
│   ├── cliente_api.py                 # Integração HTTP com a API da ESPN (times, tabelas, partidas) e cache
│   ├── formatador_jogos.py            # Extração paralela de estatísticas e eventos por partida
│   ├── calculadora_estatisticas.py    # Cálculos puros e agregação de métricas dos jogos
│   ├── prompts_ia.py                  # Construção dos prompts estruturados (PromptBuilder)
│   └── servico_ia.py                  # Cliente Google Gemini e orquestração da análise (ServicoAnalise)
├── forms/
│   └── auth_forms.py                  # Formulários WTForms de login e cadastro
├── models/
│   ├── __init__.py                    # Exportação de db e Usuario
│   └── usuario.py                     # Modelo Usuario (SQLAlchemy)
├── routes/
│   ├── auth.py                        # Rotas de autenticação (/login, /register, /logout)
│   ├── main.py                        # Rotas principais (/ e /dashboard)
│   └── futebol.py                     # Endpoints JSON (/times, /tabela, /estatisticas, /campeonatos, /analise-ia)
├── static/js/
│   ├── times.js                       # Carregamento de equipes e tabela de classificação por competição
│   ├── estatisticas.js                # Renderização de estatísticas individuais e de confronto
│   └── analise_ia.js                  # Requisição e exibição do relatório preditivo da IA
└── templates/                         # Templates Jinja2 (layout, index, dashboard, login, register, 404, 500)
```

## Aviso

O **Analytics FC** é apenas um projeto de portfólio. As análises e projeções geradas têm caráter exclusivamente estatístico e informativo, sem qualquer vínculo com apostas ou recomendação financeira.