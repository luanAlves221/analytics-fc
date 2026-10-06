from flask import jsonify
import requests
import os

TEMPORADAS_CAMPEONATOS = {
    "71": "2025",    # Brasileirão
    "13": "2025",    # Libertadores
    "11": "2025",    # Sul-Americana
    "2": "2024",     # Champions League
    "39": "2024",    # Premier League
    "140": "2024",   # La Liga
    "135": "2024",   # Serie A
    "78": "2024",    # Bundesliga
    "61": "2024",    # Ligue 1
    "94": "2024"     # Liga Portugal
}

def buscar_times(campeonato):
    """Busca os times de um determinado campeonato na API Football"""
    temporada = TEMPORADAS_CAMPEONATOS.get(campeonato, "2025")
    
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    params = {
        "league": campeonato,
        "season": temporada
    }
    headers = {
        "X-RapidAPI-Key": os.getenv("API_FOOTBALL_KEY"),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=params)
    
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
    return jsonify(times)

def extrair_estatistica(estatisticas, tipo):
    """Extrai uma estatística específica da lista de estatísticas"""
    for stat in estatisticas:
        if stat["type"] == tipo:
            valor = stat["value"]
            if isinstance(valor, str) and "%" in valor:
                return float(valor.replace("%", ""))
            elif isinstance(valor, (int, float)):
                return valor
            elif isinstance(valor, str) and valor.isdigit():
                return int(valor)
            return valor
    return 0

def buscar_estatisticas_time(time_id, campeonato_id):
    """Busca estatísticas detalhadas de um time em um campeonato"""
    temporada = TEMPORADAS_CAMPEONATOS.get(campeonato_id, "2025")
    
    headers = {
        "X-RapidAPI-Key": os.getenv("API_FOOTBALL_KEY"),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    fixtures_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {
        "team": time_id,
        "league": campeonato_id,
        "season": temporada,
        "status": "FT",
        "last": 10
    }

    resp = requests.get(fixtures_url, headers=headers, params=params)
    if resp.status_code != 200:
        return jsonify({"erro": "Erro ao buscar partidas"}), resp.status_code

    partidas = resp.json().get("response", [])
    if not partidas:
        return jsonify({"erro": "Nenhuma partida encontrada"}), 404

    jogos_formatados = formatar_jogos(partidas, time_id, headers)
    
    estatisticas_gerais = calcular_estatisticas_gerais(jogos_formatados)
    
    # Removido a inversão da lista - Ordenação será feita no frontend
    # jogos_formatados.reverse()
    
    return jsonify({
        "ultimos_jogos": jogos_formatados,
        "estatisticas_gerais": estatisticas_gerais
    })

def formatar_jogos(partidas, time_id, headers):
    """Formata os dados das partidas incluindo estatísticas detalhadas"""
    jogos_formatados = []
    
    for jogo in partidas:
        fixture_id = jogo["fixture"]["id"]
        data = jogo["fixture"]["date"]
        time_casa_id = str(jogo["teams"]["home"]["id"])
        time_fora_id = str(jogo["teams"]["away"]["id"])
        
        jogo_em_casa = (time_casa_id == time_id)
        
        adversario = jogo["teams"]["away"]["name"] if jogo_em_casa else jogo["teams"]["home"]["name"]
        gols_pro = jogo["goals"]["home"] if jogo_em_casa else jogo["goals"]["away"]
        gols_sofridos = jogo["goals"]["away"] if jogo_em_casa else jogo["goals"]["home"]
        
        local = "Casa" if jogo_em_casa else "Fora"

        estatisticas = buscar_estatisticas_partida(fixture_id, time_id, headers)
        
        eventos = buscar_eventos_partida(fixture_id, time_id, headers)
        
        jogo_formatado = {
            "data": data,
            "adversario": adversario,
            "local": local,
            "gols_feitos": gols_pro,
            "gols_sofridos": gols_sofridos,
            "estatisticas_detalhadas": estatisticas,
            "estatisticas": eventos["estatisticas"]
        }
        
        jogos_formatados.append(jogo_formatado)
    
    return jogos_formatados

def buscar_estatisticas_partida(fixture_id, time_id, headers):
    """Busca estatísticas detalhadas de uma partida específica"""
    stats_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
    stats_params = {"fixture": fixture_id}
    stats_resp = requests.get(stats_url, headers=headers, params=stats_params)
    stats_data = stats_resp.json().get("response", [])

    estatisticas_time = next(
        (item for item in stats_data if str(item["team"]["id"]) == time_id),
        {"statistics": []}
    )
    
    estatisticas = estatisticas_time.get("statistics", [])
    
    return {
        "escanteios": extrair_estatistica(estatisticas, "Corner Kicks"),
        "chutes_total": extrair_estatistica(estatisticas, "Total Shots"),
        "chutes_no_alvo": extrair_estatistica(estatisticas, "Shots on Goal"),
        "chutes_fora": extrair_estatistica(estatisticas, "Shots off Goal"),
        "posse_bola": extrair_estatistica(estatisticas, "Ball Possession"),
        "cartoes_amarelos": extrair_estatistica(estatisticas, "Yellow Cards"),
        "cartoes_vermelhos": extrair_estatistica(estatisticas, "Red Cards"),
        "faltas": extrair_estatistica(estatisticas, "Fouls"),
        "impedimentos": extrair_estatistica(estatisticas, "Offsides"),
        "passes_total": extrair_estatistica(estatisticas, "Total passes"),
        "passes_certos": extrair_estatistica(estatisticas, "Passes accurate")
    }

def buscar_eventos_partida(fixture_id, time_id, headers):
    """Busca eventos detalhados de uma partida (gols, cartões, etc.)"""
    events_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/events"
    events_params = {"fixture": fixture_id}
    events_resp = requests.get(events_url, headers=headers, params=events_params)
    events_data = events_resp.json().get("response", [])
    
    eventos_time = [evento for evento in events_data if str(evento.get("team", {}).get("id")) == time_id]
    
    penaltis_marcados = sum(1 for e in eventos_time if e.get("type") == "Goal" and e.get("detail") == "Penalty")
    gols_primeiro_tempo = sum(1 for e in eventos_time if e.get("type") == "Goal" and e.get("time", {}).get("elapsed", 0) <= 45)
    gols_segundo_tempo = sum(1 for e in eventos_time if e.get("type") == "Goal" and e.get("time", {}).get("elapsed", 0) > 45)
    
    resultado = {
        "penaltis_marcados": penaltis_marcados,
        "gols_primeiro_tempo": gols_primeiro_tempo,
        "gols_segundo_tempo": gols_segundo_tempo,
        "estatisticas": events_data
    }
    
    return resultado

def calcular_estatisticas_gerais(jogos_formatados):
    """Calcula estatísticas gerais com base nos jogos formatados"""
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
        
        est = jogo["estatisticas_detalhadas"]
        total_escanteios += est["escanteios"] or 0
        total_chutes += est["chutes_total"] or 0
        total_chutes_alvo += est["chutes_no_alvo"] or 0
        total_chutes_fora += est["chutes_fora"] or 0
        total_posse += est["posse_bola"] or 0
        total_cartoes_amarelos += est["cartoes_amarelos"] or 0
        total_cartoes_vermelhos += est["cartoes_vermelhos"] or 0
        total_faltas += est["faltas"] or 0
        total_impedimentos += est["impedimentos"] or 0
        total_passes += est["passes_total"] or 0
        total_passes_certos += est["passes_certos"] or 0
        
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

def buscar_campeonatos():
    """Busca todos os campeonatos disponíveis na API Football"""
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    headers = {
        "X-RapidAPI-Key": os.getenv("API_FOOTBALL_KEY"),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    params = {
        "current": "true"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return jsonify({"erro": "Erro ao buscar campeonatos"}), response.status_code
    
    dados = response.json()
    campeonatos = []
    
    for item in dados.get("response", []):
        league = item.get("league", {})
        country = item.get("country", {})
        
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
    
    campeonatos_ordenados = sorted(campeonatos, key=lambda x: (x["country"], x["name"]))
    
    return jsonify(campeonatos_ordenados)