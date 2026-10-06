class CalculadoraEstatisticas:
    """Responsável por extrair e acumular estatísticas de partidas."""

    def extrair_estatistica(self, estatisticas, tipo):
        """Extrai uma estatística específica da lista de estatísticas da partida."""
        for stat in estatisticas:
            chave = stat.get("name") or stat.get("type")
            if chave == tipo:
                valor = stat.get("displayValue") if "displayValue" in stat else stat.get("value")
                if valor is None:
                    return 0
                if isinstance(valor, (int, float)):
                    return valor
                if isinstance(valor, str):
                    texto = valor.replace("%", "").strip()
                    try:
                        return int(texto) if texto.isdigit() or (texto.startswith("-") and texto[1:].isdigit()) else float(texto)
                    except ValueError:
                        return 0
        return 0

    def calcular_estatisticas_gerais(self, jogos_formatados):
        """Calcula as médias, totais e percentuais gerais a partir dos jogos formatados."""
        vitorias = 0
        empates = 0
        derrotas = 0
        total_gols_feitos = 0
        total_gols_sofridos = 0
        vitorias_casa = 0
        vitorias_fora = 0
        jogos_casa = 0
        jogos_fora = 0

        total_escanteios = 0
        total_chutes = 0
        total_chutes_alvo = 0
        total_chutes_fora = 0
        total_posse = 0
        total_cartoes_amarelos = 0
        total_cartoes_vermelhos = 0
        total_faltas = 0
        total_impedimentos = 0
        total_passes = 0
        total_passes_certos = 0
        total_penaltis = 0
        total_gols_1t = 0
        total_gols_2t = 0

        for jogo in jogos_formatados:
            if jogo["gols_feitos"] > jogo["gols_sofridos"]:
                vitorias += 1
                jogo["resultado"] = "Vitória"
                if jogo["local"] == "Casa":
                    vitorias_casa += 1
                else:
                    vitorias_fora += 1
            elif jogo["gols_feitos"] < jogo["gols_sofridos"]:
                derrotas += 1
                jogo["resultado"] = "Derrota"
            else:
                empates += 1
                jogo["resultado"] = "Empate"

            total_gols_feitos += jogo["gols_feitos"] or 0
            total_gols_sofridos += jogo["gols_sofridos"] or 0

            if jogo["local"] == "Casa":
                jogos_casa += 1
            else:
                jogos_fora += 1

            est = jogo.get("estatisticas_detalhadas") or {}
            total_escanteios += est.get("escanteios", 0) or 0
            total_chutes += est.get("chutes_total", 0) or 0
            total_chutes_alvo += est.get("chutes_no_alvo", 0) or 0
            total_chutes_fora += est.get("chutes_fora", 0) or 0
            total_posse += est.get("posse_bola", 0) or 0
            total_cartoes_amarelos += est.get("cartoes_amarelos", 0) or 0
            total_cartoes_vermelhos += est.get("cartoes_vermelhos", 0) or 0
            total_faltas += est.get("faltas", 0) or 0
            total_impedimentos += est.get("impedimentos", 0) or 0
            total_passes += est.get("passes_total", 0) or 0
            total_passes_certos += est.get("passes_certos", 0) or 0

            total_penaltis += est.get("penaltis_marcados", 0) or 0
            total_gols_1t += est.get("gols_primeiro_tempo", 0) or 0
            total_gols_2t += est.get("gols_segundo_tempo", 0) or 0

        total_jogos = len(jogos_formatados)

        jogos_over_15 = sum(1 for j in jogos_formatados if (j["gols_feitos"] or 0) + (j["gols_sofridos"] or 0) > 1.5)
        jogos_over_25 = sum(1 for j in jogos_formatados if (j["gols_feitos"] or 0) + (j["gols_sofridos"] or 0) > 2.5)
        jogos_ambas_marcam = sum(1 for j in jogos_formatados if (j["gols_feitos"] or 0) > 0 and (j["gols_sofridos"] or 0) > 0)

        estatisticas_gerais = {
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "vitorias_casa": vitorias_casa,
            "vitorias_fora": vitorias_fora,
            "jogos_casa": jogos_casa,
            "jogos_fora": jogos_fora,
            "aproveitamento": round((vitorias * 3 + empates) / (total_jogos * 3) * 100, 2) if total_jogos > 0 else 0,
            "media_gols_feitos": round(total_gols_feitos / total_jogos, 2) if total_jogos > 0 else 0,
            "media_gols_sofridos": round(total_gols_sofridos / total_jogos, 2) if total_jogos > 0 else 0,
            "media_gols_total": round((total_gols_feitos + total_gols_sofridos) / total_jogos, 2) if total_jogos > 0 else 0,
            "jogos_over_1_5": jogos_over_15,
            "jogos_over_2_5": jogos_over_25,
            "jogos_ambas_marcam": jogos_ambas_marcam,
            "porcentagem_over_1_5": round(jogos_over_15 / total_jogos * 100, 2) if total_jogos > 0 else 0,
            "porcentagem_over_2_5": round(jogos_over_25 / total_jogos * 100, 2) if total_jogos > 0 else 0,
            "porcentagem_ambas_marcam": round(jogos_ambas_marcam / total_jogos * 100, 2) if total_jogos > 0 else 0,
            "media_escanteios": round(total_escanteios / total_jogos, 2) if total_jogos > 0 else 0,
            "media_chutes": round(total_chutes / total_jogos, 2) if total_jogos > 0 else 0,
            "media_chutes_alvo": round(total_chutes_alvo / total_jogos, 2) if total_jogos > 0 else 0,
            "media_chutes_fora": round(total_chutes_fora / total_jogos, 2) if total_jogos > 0 else 0,
            "media_posse": round(total_posse / total_jogos, 2) if total_jogos > 0 else 0,
            "media_cartoes_amarelos": round(total_cartoes_amarelos / total_jogos, 2) if total_jogos > 0 else 0,
            "media_cartoes_vermelhos": round(total_cartoes_vermelhos / total_jogos, 2) if total_jogos > 0 else 0,
            "media_faltas": round(total_faltas / total_jogos, 2) if total_jogos > 0 else 0,
            "media_impedimentos": round(total_impedimentos / total_jogos, 2) if total_jogos > 0 else 0,
            "precisao_passes": round(total_passes_certos / total_passes * 100, 2) if total_passes > 0 else 0,
            "media_passes": round(total_passes / total_jogos, 2) if total_jogos > 0 else 0,
            "total_penaltis": total_penaltis,
            "gols_primeiro_tempo": total_gols_1t,
            "gols_segundo_tempo": total_gols_2t,
            "porcentagem_gols_1t": round(total_gols_1t / total_gols_feitos * 100, 2) if total_gols_feitos > 0 else 0,
            "porcentagem_gols_2t": round(total_gols_2t / total_gols_feitos * 100, 2) if total_gols_feitos > 0 else 0
        }

        return estatisticas_gerais