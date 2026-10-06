import requests
from app import cache
from .formatador_jogos import FormatadorJogos
from .calculadora_estatisticas import CalculadoraEstatisticas

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"
STANDINGS_BASE_URL = "https://site.api.espn.com/apis/v2/sports/soccer"

CAMPEONATOS_SUPORTADOS = [
    {"id": "bra.1", "name": "Brasileirão Série A", "country": "Brazil"},
    {"id": "conmebol.libertadores", "name": "CONMEBOL Libertadores", "country": "South America"},
    {"id": "conmebol.sudamericana", "name": "CONMEBOL Sul-Americana", "country": "South America"},
    {"id": "uefa.champions", "name": "UEFA Champions League", "country": "Europe"},
    {"id": "eng.1", "name": "Premier League", "country": "England"},
    {"id": "esp.1", "name": "La Liga", "country": "Spain"},
    {"id": "ita.1", "name": "Serie A", "country": "Italy"},
    {"id": "ger.1", "name": "Bundesliga", "country": "Germany"},
    {"id": "fra.1", "name": "Ligue 1", "country": "France"},
    {"id": "por.1", "name": "Liga Portugal", "country": "Portugal"},
]

MAPA_LIGAS_LEGADO = {
    "71": "bra.1",
    "13": "conmebol.libertadores",
    "11": "conmebol.sudamericana",
    "2": "uefa.champions",
    "39": "eng.1",
    "140": "esp.1",
    "135": "ita.1",
    "78": "ger.1",
    "61": "fra.1",
    "94": "por.1",
}


class ClienteApiFutebol:
    """Responsável pelas chamadas HTTP à API pública de futebol da ESPN e cache."""

    def __init__(self):
        """Inicializa o cliente com as instâncias do formatador e da calculadora."""
        self.formatador = FormatadorJogos()
        self.calculadora = CalculadoraEstatisticas()

    def _normalizar_campeonato(self, campeonato):
        """Converte códigos legados ou retorna o slug do campeonato usado pela ESPN."""
        codigo = str(campeonato or "").strip()
        return MAPA_LIGAS_LEGADO.get(codigo, codigo)

    @cache.memoize(timeout=1800)
    def buscar_times(self, campeonato):
        """Busca os times de um determinado campeonato na API da ESPN."""
        liga = self._normalizar_campeonato(campeonato)
        url = f"{BASE_URL}/{liga}/teams"

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException:
            return {"erro": "Erro de conexão ao buscar times"}, 502

        if response.status_code != 200:
            return {"erro": "Erro ao buscar times"}, response.status_code

        dados = response.json()
        equipes_brutas = (
            dados.get("sports", [{}])[0]
            .get("leagues", [{}])[0]
            .get("teams", [])
        )

        times = [
            {
                "id": str(item["team"]["id"]),
                "name": item["team"].get("displayName") or item["team"].get("name"),
            }
            for item in equipes_brutas
            if item.get("team", {}).get("id")
        ]
        times.sort(key=lambda t: t["name"] or "")
        return times, 200

    @cache.memoize(timeout=600)
    def buscar_tabela(self, campeonato):
        """Busca a tabela de classificação atual de um campeonato na API da ESPN."""
        liga = self._normalizar_campeonato(campeonato)
        url = f"{STANDINGS_BASE_URL}/{liga}/standings"

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException:
            return {"erro": "Erro de conexão ao buscar tabela"}, 502

        if response.status_code != 200:
            return {"erro": "Erro ao buscar tabela do campeonato"}, response.status_code

        dados = response.json()
        children = dados.get("children", [])
        if not children and dados.get("standings"):
            children = [dados]

        grupos = []
        for child in children:
            nome_grupo = child.get("name") or dados.get("name") or "Classificação"
            entries = child.get("standings", {}).get("entries", [])
            classificacao = []

            for entry in entries:
                team = entry.get("team", {})
                stats_map = {}
                for s in entry.get("stats", []):
                    nome_stat = s.get("name")
                    if nome_stat:
                        stats_map[nome_stat] = s.get("displayValue") if s.get("displayValue") is not None else s.get("value")

                try:
                    posicao = int(float(stats_map.get("rank", 0) or 0))
                except (TypeError, ValueError):
                    posicao = 0

                classificacao.append({
                    "posicao": posicao,
                    "time_id": str(team.get("id", "")),
                    "time": team.get("displayName") or team.get("name", ""),
                    "pontos": int(float(stats_map.get("points", 0) or 0)),
                    "jogos": int(float(stats_map.get("gamesPlayed", 0) or 0)),
                    "vitorias": int(float(stats_map.get("wins", 0) or 0)),
                    "empates": int(float(stats_map.get("ties", 0) or 0)),
                    "derrotas": int(float(stats_map.get("losses", 0) or 0)),
                    "gols_pro": int(float(stats_map.get("pointsFor", 0) or 0)),
                    "gols_contra": int(float(stats_map.get("pointsAgainst", 0) or 0)),
                    "saldo_gols": str(stats_map.get("pointDifferential", "0")),
                })

            classificacao.sort(key=lambda item: item["posicao"] if item["posicao"] > 0 else 999)
            if classificacao:
                grupos.append({
                    "nome": nome_grupo,
                    "classificacao": classificacao,
                })

        if not grupos:
            return {"erro": "Tabela de classificação indisponível para este campeonato"}, 404

        return {"grupos": grupos}, 200

    def _obter_posicao_time_na_tabela(self, time_id, campeonato_id):
        """Retorna os dados de classificação do time na tabela atual, se disponíveis."""
        dados_tabela, status = self.buscar_tabela(campeonato_id)
        if status != 200 or not isinstance(dados_tabela, dict):
            return None

        time_id_str = str(time_id)
        for grupo in dados_tabela.get("grupos", []):
            for item in grupo.get("classificacao", []):
                if item.get("time_id") == time_id_str:
                    return {
                        "grupo": grupo.get("nome"),
                        "posicao": item.get("posicao"),
                        "pontos": item.get("pontos"),
                        "jogos": item.get("jogos"),
                        "vitorias": item.get("vitorias"),
                        "empates": item.get("empates"),
                        "derrotas": item.get("derrotas"),
                        "saldo_gols": item.get("saldo_gols"),
                    }
        return None

    @cache.memoize(timeout=600)
    def buscar_estatisticas_time(self, time_id, campeonato_id):
        """Busca os últimos 10 jogos finalizados e calcula as estatísticas de um time."""
        liga = self._normalizar_campeonato(campeonato_id)
        schedule_url = f"{BASE_URL}/{liga}/teams/{time_id}/schedule"

        try:
            resp = requests.get(schedule_url, timeout=10)
        except requests.RequestException:
            return {"erro": "Erro de conexão ao buscar partidas"}, 502

        if resp.status_code != 200:
            return {"erro": "Erro ao buscar partidas"}, resp.status_code

        eventos = resp.json().get("events", [])
        partidas_finalizadas = [
            ev for ev in eventos
            if (ev.get("competitions") or [{}])[0].get("status", {}).get("type", {}).get("completed")
        ]

        if not partidas_finalizadas:
            try:
                resp_all = requests.get(f"{BASE_URL}/all/teams/{time_id}/schedule", timeout=10)
                if resp_all.status_code == 200:
                    eventos_all = resp_all.json().get("events", [])
                    partidas_finalizadas = [
                        ev for ev in eventos_all
                        if (ev.get("competitions") or [{}])[0].get("status", {}).get("type", {}).get("completed")
                    ]
            except requests.RequestException:
                pass

        if not partidas_finalizadas:
            return {"erro": "Nenhuma partida finalizada encontrada para este time na temporada"}, 404

        partidas_ordenadas = sorted(
            partidas_finalizadas,
            key=lambda ev: ev.get("date", ""),
            reverse=True,
        )[:10]

        jogos_formatados = self.formatador.formatar_jogos(partidas_ordenadas, str(time_id), liga)
        estatisticas_gerais = self.calculadora.calcular_estatisticas_gerais(jogos_formatados)
        estatisticas_gerais["posicao_tabela"] = self._obter_posicao_time_na_tabela(time_id, liga)

        return {
            "ultimos_jogos": jogos_formatados,
            "estatisticas_gerais": estatisticas_gerais,
        }, 200

    @cache.memoize(timeout=3600)
    def buscar_campeonatos(self):
        """Retorna a lista de campeonatos suportados pelo sistema."""
        return CAMPEONATOS_SUPORTADOS, 200


cliente_api = ClienteApiFutebol()