import pytest

from app.controllers.calculadora_estatisticas import CalculadoraEstatisticas
from app.controllers.formatador_jogos import FormatadorJogos


class TestExtrairEstatistica:

    def setup_method(self):
        self.calc = CalculadoraEstatisticas()

    def test_retorna_float_quando_valor_tem_porcentagem(self):
        stats = [{"type": "Ball Possession", "value": "62%"}]
        assert self.calc.extrair_estatistica(stats, "Ball Possession") == 62.0

    def test_retorna_valor_numerico_direto(self):
        stats = [{"type": "Total Shots", "value": 18}]
        assert self.calc.extrair_estatistica(stats, "Total Shots") == 18

    def test_converte_string_numerica_para_int(self):
        stats = [{"type": "Corner Kicks", "value": "7"}]
        assert self.calc.extrair_estatistica(stats, "Corner Kicks") == 7

    def test_retorna_zero_quando_tipo_nao_existe(self):
        assert self.calc.extrair_estatistica([], "Inexistente") == 0

    def test_retorna_valor_nao_numerico_quando_nao_parseavel(self):
        stats = [{"type": "Fouls", "value": "n/a"}]
        assert self.calc.extrair_estatistica(stats, "Fouls") == "n/a"


class TestCalcularEstatisticasGerais:

    def setup_method(self):
        self.calc = CalculadoraEstatisticas()

    def _jogo(self, feitos, sofridos, local="Casa", estatisticas=None):
        if estatisticas is None:
            estatisticas = {
                "escanteios": 0, "chutes_total": 0, "chutes_no_alvo": 0,
                "chutes_fora": 0, "posse_bola": 0, "cartoes_amarelos": 0,
                "cartoes_vermelhos": 0, "faltas": 0, "impedimentos": 0,
                "passes_total": 0, "passes_certos": 0
            }
        return {
            "gols_feitos": feitos,
            "gols_sofridos": sofridos,
            "local": local,
            "estatisticas_detalhadas": estatisticas
        }

    def test_conta_vitorias_empates_e_derrotas(self):
        jogos = [
            self._jogo(2, 1),
            self._jogo(0, 0),
            self._jogo(0, 3, local="Fora")
        ]
        result = self.calc.calcular_estatisticas_gerais(jogos)
        assert result["vitorias"] == 1
        assert result["empates"] == 1
        assert result["derrotas"] == 1

    def test_calcula_aproveitamento(self):
        jogos = [self._jogo(1, 0), self._jogo(1, 0), self._jogo(0, 1), self._jogo(0, 0)]
        result = self.calc.calcular_estatisticas_gerais(jogos)
        assert result["aproveitamento"] == 58.33

    def test_media_de_gols(self):
        jogos = [self._jogo(2, 1), self._jogo(0, 3)]
        result = self.calc.calcular_estatisticas_gerais(jogos)
        assert result["media_gols_feitos"] == 1.0
        assert result["media_gols_sofridos"] == 2.0
        assert result["media_gols_total"] == 3.0

    def test_over_e_ambas_marcam(self):
        jogos = [
            self._jogo(2, 1),
            self._jogo(1, 1),
            self._jogo(0, 0)
        ]
        result = self.calc.calcular_estatisticas_gerais(jogos)
        assert result["jogos_over_1_5"] == 2
        assert result["jogos_over_2_5"] == 1
        assert result["jogos_ambas_marcam"] == 2
        assert result["porcentagem_over_1_5"] == 66.67

    def test_acumula_penaltis_e_gols_por_tempo(self):
        extra = {
            "penaltis_marcados": 1,
            "gols_primeiro_tempo": 2,
            "gols_segundo_tempo": 1
        }
        estatisticas = {**self._jogo(3, 0)["estatisticas_detalhadas"], **extra}
        jogos = [self._jogo(3, 0, estatisticas=estatisticas)] * 2
        result = self.calc.calcular_estatisticas_gerais(jogos)
        assert result["total_penaltis"] == 2
        assert result["gols_primeiro_tempo"] == 4
        assert result["gols_segundo_tempo"] == 2

    def test_lista_vazia_nao_dividi_por_zero(self):
        result = self.calc.calcular_estatisticas_gerais([])
        assert result["aproveitamento"] == 0
        assert result["media_gols_total"] == 0

    def test_marca_resultado_em_cada_jogo(self):
        jogos = [self._jogo(2, 1, local="Casa"), self._jogo(0, 1, local="Fora")]
        self.calc.calcular_estatisticas_gerais(jogos)
        assert jogos[0]["resultado"] == "Vitória"
        assert jogos[1]["resultado"] == "Derrota"


class TestFormatadorEventos:

    def setup_method(self):
        self.formatador = FormatadorJogos()

    def test_buscar_eventos_conta_penaltis_e_gols_por_tempo(self, monkeypatch):
        eventos_brutos = {
            "response": [
                {"team": {"id": 1}, "type": "Goal", "detail": "Penalty", "time": {"elapsed": 30}},
                {"team": {"id": 1}, "type": "Goal", "detail": "Normal", "time": {"elapsed": 70}},
                {"team": {"id": 2}, "type": "Goal", "detail": "Normal", "time": {"elapsed": 80}}
            ]
        }

        class Resp:
            status_code = 200
            def json(self):
                return eventos_brutos

        monkeypatch.setattr("app.controllers.formatador_jogos.requests.get", lambda *a, **k: Resp())

        result = self.formatador.buscar_eventos_partida(99, "1", {})
        assert result["penaltis_marcados"] == 1
        assert result["gols_primeiro_tempo"] == 1
        assert result["gols_segundo_tempo"] == 1

    def test_buscar_eventos_erro_retorna_zeros(self, monkeypatch):
        class Resp:
            status_code = 429
            def json(self):
                return {"erro": "rate limit"}

        monkeypatch.setattr("app.controllers.formatador_jogos.requests.get", lambda *a, **k: Resp())

        result = self.formatador.buscar_eventos_partida(99, "1", {})
        assert result == {"penaltis_marcados": 0, "gols_primeiro_tempo": 0, "gols_segundo_tempo": 0}

    def test_buscar_estatisticas_partida_extrai_valores_do_time(self, monkeypatch):
        dados = {
            "response": [
                {
                    "team": {"id": 1},
                    "statistics": [
                        {"type": "Corner Kicks", "value": "6"},
                        {"type": "Ball Possession", "value": "55%"}
                    ]
                },
                {"team": {"id": 2}, "statistics": []}
            ]
        }

        class Resp:
            status_code = 200
            def json(self):
                return dados

        monkeypatch.setattr("app.controllers.formatador_jogos.requests.get", lambda *a, **k: Resp())

        result = self.formatador.buscar_estatisticas_partida(99, "1", {})
        assert result["escanteios"] == 6
        assert result["posse_bola"] == 55.0

    def test_buscar_estatisticas_partida_erro_retorna_vazio(self, monkeypatch):
        class Resp:
            status_code = 500
            def json(self):
                return {"erro": "boom"}

        monkeypatch.setattr("app.controllers.formatador_jogos.requests.get", lambda *a, **k: Resp())

        result = self.formatador.buscar_estatisticas_partida(99, "1", {})
        assert result == {}

    def test_formatar_jogos_preserva_ordem_e_paraleliza(self, monkeypatch):
        partidas = [
            {
                "fixture": {"id": i, "date": f"2026-01-{i:02d}T00:00:00"},
                "teams": {"home": {"id": 1, "name": "A"}, "away": {"id": i + 10, "name": f"Adv{i}"}},
                "goals": {"home": 1, "away": 0}
            }
            for i in range(1, 6)
        ]

        class Resp:
            status_code = 200
            def json(self):
                return {"response": []}

        monkeypatch.setattr("app.controllers.formatador_jogos.requests.get", lambda *a, **k: Resp())

        jogos = self.formatador.formatar_jogos(partidas, "1", {})
        adversarios = [j["adversario"] for j in jogos]
        assert adversarios == ["Adv1", "Adv2", "Adv3", "Adv4", "Adv5"]