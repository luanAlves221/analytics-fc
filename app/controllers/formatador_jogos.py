import requests
from concurrent.futures import ThreadPoolExecutor
from .calculadora_estatisticas import CalculadoraEstatisticas

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"


class FormatadorJogos:
    """Responsável por formatar partidas com estatísticas e eventos detalhados."""

    def __init__(self):
        self.calculadora = CalculadoraEstatisticas()

    def formatar_jogos(self, partidas, time_id, headers):
        """Formata os dados das partidas incluindo estatísticas detalhadas"""
        with ThreadPoolExecutor(max_workers=5) as executor:
            jogos_formatados = list(executor.map(
                lambda jogo: self._formatar_jogo(jogo, time_id, headers),
                partidas
            ))
        return jogos_formatados

    def _formatar_jogo(self, jogo, time_id, headers):
        """Formata um único jogo com estatísticas e eventos detalhados"""
        fixture_id = jogo["fixture"]["id"]
        data = jogo["fixture"]["date"]
        time_casa_id = str(jogo["teams"]["home"]["id"])
        time_fora_id = str(jogo["teams"]["away"]["id"])

        jogo_em_casa = (time_casa_id == time_id)

        adversario = jogo["teams"]["away"]["name"] if jogo_em_casa else jogo["teams"]["home"]["name"]
        gols_pro = jogo["goals"]["home"] if jogo_em_casa else jogo["goals"]["away"]
        gols_sofridos = jogo["goals"]["away"] if jogo_em_casa else jogo["goals"]["home"]

        local = "Casa" if jogo_em_casa else "Fora"

        estatisticas = self.buscar_estatisticas_partida(fixture_id, time_id, headers)

        eventos = self.buscar_eventos_partida(fixture_id, time_id, headers)

        estatisticas.update({
            "penaltis_marcados": eventos["penaltis_marcados"],
            "gols_primeiro_tempo": eventos["gols_primeiro_tempo"],
            "gols_segundo_tempo": eventos["gols_segundo_tempo"]
        })

        return {
            "data": data,
            "adversario": adversario,
            "local": local,
            "gols_feitos": gols_pro,
            "gols_sofridos": gols_sofridos,
            "estatisticas_detalhadas": estatisticas
        }

    def buscar_estatisticas_partida(self, fixture_id, time_id, headers):
        """Busca estatísticas detalhadas de uma partida específica"""
        stats_url = f"{BASE_URL}/fixtures/statistics"
        stats_params = {"fixture": fixture_id}
        stats_resp = requests.get(stats_url, headers=headers, params=stats_params)

        if stats_resp.status_code != 200:
            return {}

        stats_data = stats_resp.json().get("response", [])

        estatisticas_time = next(
            (item for item in stats_data if str(item["team"]["id"]) == time_id),
            {"statistics": []}
        )

        estatisticas = estatisticas_time.get("statistics", [])

        return {
            "escanteios": self.calculadora.extrair_estatistica(estatisticas, "Corner Kicks"),
            "chutes_total": self.calculadora.extrair_estatistica(estatisticas, "Total Shots"),
            "chutes_no_alvo": self.calculadora.extrair_estatistica(estatisticas, "Shots on Goal"),
            "chutes_fora": self.calculadora.extrair_estatistica(estatisticas, "Shots off Goal"),
            "posse_bola": self.calculadora.extrair_estatistica(estatisticas, "Ball Possession"),
            "cartoes_amarelos": self.calculadora.extrair_estatistica(estatisticas, "Yellow Cards"),
            "cartoes_vermelhos": self.calculadora.extrair_estatistica(estatisticas, "Red Cards"),
            "faltas": self.calculadora.extrair_estatistica(estatisticas, "Fouls"),
            "impedimentos": self.calculadora.extrair_estatistica(estatisticas, "Offsides"),
            "passes_total": self.calculadora.extrair_estatistica(estatisticas, "Total passes"),
            "passes_certos": self.calculadora.extrair_estatistica(estatisticas, "Passes accurate")
        }

    def buscar_eventos_partida(self, fixture_id, time_id, headers):
        """Busca eventos detalhados de uma partida (gols, cartões, etc.)"""
        events_url = f"{BASE_URL}/fixtures/events"
        events_params = {"fixture": fixture_id}
        events_resp = requests.get(events_url, headers=headers, params=events_params)

        if events_resp.status_code != 200:
            return {
                "penaltis_marcados": 0,
                "gols_primeiro_tempo": 0,
                "gols_segundo_tempo": 0
            }

        events_data = events_resp.json().get("response", [])

        eventos_time = [evento for evento in events_data if str(evento.get("team", {}).get("id")) == time_id]

        return {
            "penaltis_marcados": sum(1 for e in eventos_time if e.get("type") == "Goal" and e.get("detail") == "Penalty"),
            "gols_primeiro_tempo": sum(1 for e in eventos_time if e.get("type") == "Goal" and e.get("time", {}).get("elapsed", 0) <= 45),
            "gols_segundo_tempo": sum(1 for e in eventos_time if e.get("type") == "Goal" and e.get("time", {}).get("elapsed", 0) > 45)
        }