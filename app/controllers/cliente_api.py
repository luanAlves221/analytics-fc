import os
import requests
from datetime import datetime
from flask import jsonify
from app import cache
from .formatador_jogos import FormatadorJogos
from .calculadora_estatisticas import CalculadoraEstatisticas

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"


class ClienteApiFutebol:
    """Responsável pelas chamadas HTTP à API-Football (headners, rede e cache)."""

    temporadas_campeonatos = {}

    def __init__(self):
        self.formatador = FormatadorJogos()
        self.calculadora = CalculadoraEstatisticas()

    def _headers(self):
        return {
            "X-RapidAPI-Key": os.getenv("API_FOOTBALL_KEY"),
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

    def _obter_temporada(self, campeonato):
        """Retorna a temporada corrente de uma liga, com fallback para o ano atual."""
        return self.temporadas_campeonatos.get(campeonato) or str(datetime.now().year)

    @cache.memoize(timeout=1800)
    def buscar_times(self, campeonato):
        """Busca os times de um determinado campeonato na API Football"""
        temporada = self._obter_temporada(campeonato)

        url = f"{BASE_URL}/teams"
        params = {
            "league": campeonato,
            "season": temporada
        }

        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code != 200:
            return jsonify({"erro": "Erro ao buscar times"}), response.status_code

        dados = response.json()
        times = [
            {
                "id": item["team"]["id"],
                "name": item["team"]["name"]
            }
            for item in dados.get("response", [])
        ]
        return jsonify(times), 200

    @cache.memoize(timeout=600)
    def buscar_estatisticas_time(self, time_id, campeonato_id):
        """Busca estatísticas detalhadas de um time em um campeonato"""
        temporada = self._obter_temporada(campeonato_id)

        fixtures_url = f"{BASE_URL}/fixtures"
        params = {
            "team": time_id,
            "league": campeonato_id,
            "season": temporada,
            "status": "FT",
            "last": 10
        }

        resp = requests.get(fixtures_url, headers=self._headers(), params=params)
        if resp.status_code != 200:
            return jsonify({"erro": "Erro ao buscar partidas"}), resp.status_code

        partidas = resp.json().get("response", [])
        if not partidas:
            return jsonify({"erro": "Nenhuma partida encontrada"}), 404

        jogos_formatados = self.formatador.formatar_jogos(partidas, time_id, self._headers())

        estatisticas_gerais = self.calculadora.calcular_estatisticas_gerais(jogos_formatados)

        return jsonify({
            "ultimos_jogos": jogos_formatados,
            "estatisticas_gerais": estatisticas_gerais
        }), 200

    @cache.memoize(timeout=600)
    def buscar_campeonatos(self):
        """Busca todos os campeonatos disponíveis na API Football"""
        url = f"{BASE_URL}/leagues"
        params = {
            "current": "true"
        }

        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code != 200:
            return jsonify({"erro": "Erro ao buscar campeonatos"}), response.status_code

        dados = response.json()
        campeonatos = []

        for item in dados.get("response", []):
            league = item.get("league", {})
            country = item.get("country", {})

            seasons = league.get("seasons", [])
            temporada_atual = next(
                (s.get("year") for s in seasons if s.get("current")),
                None
            )
            if temporada_atual:
                self.temporadas_campeonatos[str(league.get("id"))] = str(temporada_atual)

            campeonato = {
                "id": league.get("id"),
                "name": league.get("name"),
                "type": league.get("type"),
                "logo": league.get("logo"),
                "country": country.get("name"),
                "country_code": country.get("code"),
                "flag": country.get("flag")
            }

            if campeonato["name"]:
                campeonatos.append(campeonato)

        campeonatos_ordenados = sorted(
            campeonatos,
            key=lambda x: (x["country"] or "", x["name"] or "")
        )

        return jsonify(campeonatos_ordenados), 200


cliente_api = ClienteApiFutebol()