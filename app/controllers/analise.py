from flask import current_app
from .IA import gerar_conteudo

def formatar_estatisticas_para_prompt(dados_time, nome_time):
    """Formata as estatísticas de um time para incluir no prompt da IA"""
    
    estatisticas = dados_time["estatisticas_gerais"]
    
    prompt = f"• {nome_time}:\n"
    prompt += f"  - Resultados: {estatisticas['vitorias']} vitórias, {estatisticas['empates']} empates, {estatisticas['derrotas']} derrotas\n"
    prompt += f"  - Aproveitamento: {estatisticas['aproveitamento']}%\n"
    prompt += f"  - Média de Gols Feitos: {estatisticas['media_gols_feitos']}\n"
    prompt += f"  - Média de Gols Sofridos: {estatisticas['media_gols_sofridos']}\n"
    prompt += f"  - Média Total de Gols: {estatisticas['media_gols_total']}\n"
    prompt += f"  - Over 1.5: {estatisticas['porcentagem_over_1_5']}% ({estatisticas['jogos_over_1_5']}/{len(dados_time['ultimos_jogos'])} jogos)\n"
    prompt += f"  - Over 2.5: {estatisticas['porcentagem_over_2_5']}% ({estatisticas['jogos_over_2_5']}/{len(dados_time['ultimos_jogos'])} jogos)\n"
    prompt += f"  - Ambas marcam: {estatisticas['porcentagem_ambas_marcam']}% ({estatisticas['jogos_ambas_marcam']}/{len(dados_time['ultimos_jogos'])} jogos)\n"
    prompt += f"  - Média de Escanteios: {estatisticas['media_escanteios']}\n"
    prompt += f"  - Média de Cartões Amarelos: {estatisticas['media_cartoes_amarelos']}\n"
    prompt += f"  - Média de Cartões Vermelhos: {estatisticas['media_cartoes_vermelhos']}\n"
    prompt += f"  - Média de Faltas: {estatisticas['media_faltas']}\n"
    prompt += f"  - Posse de Bola Média: {estatisticas['media_posse']}%\n"
    
    jogos_ordenados = sorted(dados_time['ultimos_jogos'], key=lambda j: j['data'], reverse=True)
    prompt += f"\n  - Últimos {len(jogos_ordenados)} jogos:\n"
    
    for jogo in jogos_ordenados:
        data = jogo['data'].split('T')[0] if 'T' in jogo['data'] else jogo['data']
        prompt += f"    * {data} - {jogo['local']} contra {jogo['adversario']}: {jogo['gols_feitos']} x {jogo['gols_sofridos']} ({jogo['resultado']})\n"
    
    return prompt

def criar_prompt_confronto(dados_time_a, nome_time_a, dados_time_b, nome_time_b):
    """Cria o prompt completo para análise de confronto"""
    
    estatisticas_a = formatar_estatisticas_para_prompt(dados_time_a, nome_time_a)
    estatisticas_b = formatar_estatisticas_para_prompt(dados_time_b, nome_time_b)
    
    prompt = f"""
Você é um analista esportivo especializado em futebol e estatísticas para apostas esportivas.
Baseando-se apenas nos dados estatísticos fornecidos, faça uma análise preditiva para um confronto direto entre {nome_time_a} e {nome_time_b}.
Não mencione dados que não foram fornecidos e não faça suposições além do que as estatísticas indicam.

Estatísticas dos times:

{estatisticas_a}

{estatisticas_b}

Considerando apenas estas estatísticas, forneça:

1. Análise de quem tem maior probabilidade de vitória ou empate com base nas estatísticas recentes. Seja específico com porcentagens (por exemplo: "{nome_time_a} tem probabilidade de vitória de X%, {nome_time_b} tem Y% e empate Z%").

2. Predição para total de gols com porcentagens:
   - Over/Under 1.5 gols
   - Over/Under 2.5 gols
   - Over/Under 3.5 gols

3. Probabilidade de ambas as equipes marcarem (Sim/Não)

4. Probabilidade de escanteios:
   - Over/Under 8.5 escanteios
   - Over/Under 9.5 escanteios
   - Over/Under 10.5 escanteios

5. Probabilidade de cartões:
   - Over/Under 3.5 cartões
   - Over/Under 4.5 cartões
   - Over/Under 5.5 cartões

6. Análise de estatísticas individuais para cada time:
   - Finalizações (total e no alvo)
   - Posse de bola
   - Faltas cometidas
   - Qualquer outra estatística relevante dos dados fornecidos

7. Análise dos pontos fortes e fracos de cada time com base nos dados

Para cada predição, forneça um nível de confiança (Alto, Médio, Baixo) baseado na consistência das estatísticas.

Formate sua resposta em HTML simples usando elementos <h4>, <p>, <ul>, <li>, <strong>. 
Não use cabeçalhos <h1>, <h2> ou <h3>.

Ao final da análise, inclua:

<h4>Resumo da Análise</h4>
Neste resumo, liste de forma concisa todas as previsões feitas anteriormente, sem explicações detalhadas. Inclua:
- Provável resultado da partida (vitória de {nome_time_a}, vitória de {nome_time_b} ou empate)
- Previsões específicas para cada time (ex: "{nome_time_a} deve marcar mais de 1.5 gols", "{nome_time_b} deve ter mais de 3.5 escanteios")
- Todas as estatísticas relevantes por time (gols, escanteios, cartões, finalizações, etc.)

<h4>Sugestões de Apostas</h4>
Liste suas recomendações de apostas para os seguintes mercados da Betano:
- Resultado da partida (1X2)
- Mais/Menos Gols (Over/Under)
- Ambas equipes marcam (Sim/Não)
- Escanteios (Over/Under)
- Cartões (Over/Under)
- Estatísticas (finalizações, chutes a gol, faltas, etc.)

Para cada sugestão, indique o nível de confiança (Alto, Médio, Baixo) com base na análise estatística.
"""
    
    return prompt

def analisar_confronto(dados_time_a, nome_time_a, dados_time_b, nome_time_b, campeonato_id):
    """Realiza a análise de confronto entre dois times"""
    
    try:
        # Verificar se os dados necessários estão presentes
        if not dados_time_a or not dados_time_b:
            return {
                "analise_formatada": "<p>Erro: Dados estatísticos insuficientes para análise.</p>",
                "success": False,
                "erro": "Dados estatísticos insuficientes"
            }
            
        # Criar o prompt para a IA
        prompt = criar_prompt_confronto(dados_time_a, nome_time_a, dados_time_b, nome_time_b)
        
        # Gerar a análise usando a IA
        resultado = gerar_conteudo(prompt)
        
        if not resultado["success"]:
            return {
                "analise_formatada": resultado["texto"],
                "success": False,
                "erro": resultado.get("erro", "Erro desconhecido na geração de conteúdo")
            }
        
        # Retornar o resultado formatado
        return {
            "analise_formatada": resultado["texto"],
            "success": True
        }
    
    except Exception as e:
        current_app.logger.error(f"Erro ao analisar confronto: {str(e)}")
        return {
            "analise_formatada": f"<p>Erro ao processar análise: {str(e)}</p>",
            "success": False,
            "erro": str(e)
        }