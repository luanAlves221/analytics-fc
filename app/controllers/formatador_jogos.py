import requests
from concurrent.futures import ThreadPoolExecutor
from .calculadora_estatisticas import CalculadoraEstatisticas

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"


class FormatadorJogos:
    """Responsável por formatar partidas com estatísticas e eventos detalhados via ESPN API."""

    def __init__(self):
        """Inicializa o formatador com uma instância da calculadora de estatísticas."""
        self.calculadora = CalculadoraEstatisticas()

    def formatar_jogos(self, partidas, time_id, campeonato_slug="all"):
        """Formata os dados das partidas incluindo estatísticas e eventos em paralelo."""
        time_id_str = str(time_id)
        with ThreadPoolExecutor(max_workers=5) as executor:
            jogos_formatados = list(
                executor.map(
                    lambda jogo: self._formatar_jogo(jogo, time_id_str, campeonato_slug),
                    partidas,
                )
            )
        return jogos_formatados

    def _extrair_placar(self, competidor):
        """Extrai o placar numérico de um competidor no formato da ESPN."""
        score = competidor.get("score")
        if isinstance(score, dict):
            valor = score.get("value") if score.get("value") is not None else score.get("displayValue", 0)
        else:
            valor = score
        try:
            return int(float(valor))
        except (TypeError, ValueError):
            return 0

    def _formatar_jogo(self, jogo, time_id, campeonato_slug):
        """Formata um único jogo com estatísticas e eventos detalhados."""
        fixture_id = str(jogo.get("id", ""))
        data = jogo.get("date", "")
        competicao = (jogo.get("competitions") or [{}])[0]
        competidores = competicao.get("competitors") or []

        comp_time = next(
            (c for c in competidores if str(c.get("id") or c.get("team", {}).get("id")) == time_id),
            None,
        )
        comp_adv = next(
            (c for c in competidores if str(c.get("id") or c.get("team", {}).get("id")) != time_id),
            None,
        )

        if not comp_time or not comp_adv:
            return {
                "data": data,
                "adversario": "Desconhecido",
                "local": "Casa",
                "gols_feitos": 0,
                "gols_sofridos": 0,
                "estatisticas_detalhadas": self._estatisticas_vazias(),
            }

        jogo_em_casa = comp_time.get("homeAway") == "home"
        adversario = comp_adv.get("team", {}).get("displayName") or comp_adv.get("team", {}).get("name", "Adversário")
        gols_pro = self._extrair_placar(comp_time)
        gols_sofridos = self._extrair_placar(comp_adv)
        local = "Casa" if jogo_em_casa else "Fora"

        estatisticas = self.buscar_resumo_partida(fixture_id, time_id, campeonato_slug)

        return {
            "data": data,
            "adversario": adversario,
            "local": local,
            "gols_feitos": gols_pro,
            "gols_sofridos": gols_sofridos,
            "estatisticas_detalhadas": estatisticas,
        }

    def _estatisticas_vazias(self):
        """Retorna um dicionário com todas as estatísticas da partida zeradas."""
        return {
            "escanteios": 0,
            "chutes_total": 0,
            "chutes_no_alvo": 0,
            "chutes_fora": 0,
            "posse_bola": 0,
            "cartoes_amarelos": 0,
            "cartoes_vermelhos": 0,
            "faltas": 0,
            "impedimentos": 0,
            "passes_total": 0,
            "passes_certos": 0,
            "penaltis_marcados": 0,
            "gols_primeiro_tempo": 0,
            "gols_segundo_tempo": 0,
        }

    def buscar_resumo_partida(self, fixture_id, time_id, campeonato_slug="all"):
        """Busca estatísticas e eventos de uma partida em uma única chamada ao endpoint /summary."""
        summary_url = f"{BASE_URL}/{campeonato_slug}/summary"
        try:
            resp = requests.get(summary_url, params={"event": fixture_id}, timeout=10)
            if resp.status_code != 200:
                return self._estatisticas_vazias()
            dados = resp.json()
        except Exception:
            return self._estatisticas_vazias()

        box_teams = dados.get("boxscore", {}).get("teams", [])
        estatisticas_time = next(
            (item for item in box_teams if str(item.get("team", {}).get("id")) == time_id),
            {"statistics": []},
        )
        estatisticas = estatisticas_time.get("statistics", [])

        chutes_total = int(self.calculadora.extrair_estatistica(estatisticas, "totalShots") or 0)
        chutes_no_alvo = int(self.calculadora.extrair_estatistica(estatisticas, "shotsOnTarget") or 0)
        chutes_fora = max(0, chutes_total - chutes_no_alvo)
        penaltis_box = int(self.calculadora.extrair_estatistica(estatisticas, "penaltyKickGoals") or 0)

        key_events = dados.get("keyEvents", [])
        eventos_gol_time = [
            ev for ev in key_events
            if ev.get("scoringPlay") and str(ev.get("team", {}).get("id")) == time_id
        ]

        gols_1t = sum(1 for ev in eventos_gol_time if (ev.get("period", {}).get("number") or 1) == 1)
        gols_2t = sum(1 for ev in eventos_gol_time if (ev.get("period", {}).get("number") or 1) >= 2)
        penaltis_eventos = sum(
            1 for ev in eventos_gol_time
            if "penalty" in (ev.get("type", {}).get("type") or "").lower()
            or "penalty" in (ev.get("type", {}).get("text") or "").lower()
        )

        return {
            "escanteios": int(self.calculadora.extrair_estatistica(estatisticas, "wonCorners") or 0),
            "chutes_total": chutes_total,
            "chutes_no_alvo": chutes_no_alvo,
            "chutes_fora": chutes_fora,
            "posse_bola": float(self.calculadora.extrair_estatistica(estatisticas, "possessionPct") or 0),
            "cartoes_amarelos": int(self.calculadora.extrair_estatistica(estatisticas, "yellowCards") or 0),
            "cartoes_vermelhos": int(self.calculadora.extrair_estatistica(estatisticas, "redCards") or 0),
            "faltas": int(self.calculadora.extrair_estatistica(estatisticas, "foulsCommitted") or 0),
            "impedimentos": int(self.calculadora.extrair_estatistica(estatisticas, "offsides") or 0),
            "passes_total": int(self.calculadora.extrair_estatistica(estatisticas, "totalPasses") or 0),
            "passes_certos": int(self.calculadora.extrair_estatistica(estatisticas, "accuratePasses") or 0),
            "penaltis_marcados": max(penaltis_box, penaltis_eventos),
            "gols_primeiro_tempo": gols_1t,
            "gols_segundo_tempo": gols_2t,
        }