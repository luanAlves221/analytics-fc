class PromptBuilder:
    """Responsável por montar os prompts de análise estatística e preditiva enviados à IA."""

    def _formatar_estatisticas_para_prompt(self, dados_time, nome_time):
        """Formata todas as estatísticas calculadas de um time para incluir no prompt da IA."""

        est = dados_time["estatisticas_gerais"]
        total_jogos = len(dados_time["ultimos_jogos"])
        pos = est.get("posicao_tabela")

        prompt = f"• {nome_time} (amostra: últimos {total_jogos} jogos finalizados):\n"
        if pos:
             prompt += (
                 f"  - Situação na Tabela ({pos['grupo']}): {pos['posicao']}º colocado com {pos['pontos']} pontos "
                 f"em {pos['jogos']} jogos ({pos['vitorias']}V, {pos['empates']}E, {pos['derrotas']}D, Saldo de Gols: {pos['saldo_gols']})\n"
             )
        prompt += f"  - Desempenho Recente (últimos {total_jogos} jogos): {est['vitorias']} vitórias, {est['empates']} empates, {est['derrotas']} derrotas (Aproveitamento: {est['aproveitamento']}%)\n"
        prompt += f"  - Desempenho por Mando: Casa ({est['vitorias_casa']} vitórias em {est['jogos_casa']} jogos) | Fora ({est['vitorias_fora']} vitórias em {est['jogos_fora']} jogos)\n"
        prompt += f"  - Gols: média de {est['media_gols_feitos']} marcados/jogo, {est['media_gols_sofridos']} sofridos/jogo (Média total das partidas: {est['media_gols_total']} gols/jogo)\n"
        prompt += f"  - Gols por Tempo: 1º Tempo = {est['gols_primeiro_tempo']} gols ({est['porcentagem_gols_1t']}% dos gols marcados) | 2º Tempo = {est['gols_segundo_tempo']} gols ({est['porcentagem_gols_2t']}% dos gols marcados)\n"
        prompt += f"  - Pênaltis Convertidos no Período: {est['total_penaltis']}\n"
        prompt += f"  - Partidas com Mais de 1.5 gols (Over 1.5): {est['porcentagem_over_1_5']}% ({est['jogos_over_1_5']}/{total_jogos} jogos)\n"
        prompt += f"  - Partidas com Mais de 2.5 gols (Over 2.5): {est['porcentagem_over_2_5']}% ({est['jogos_over_2_5']}/{total_jogos} jogos)\n"
        prompt += f"  - Partidas em que Ambas as Equipes Marcaram: {est['porcentagem_ambas_marcam']}% ({est['jogos_ambas_marcam']}/{total_jogos} jogos)\n"
        prompt += f"  - Finalizações: média de {est['media_chutes']} chutes/jogo ({est['media_chutes_alvo']} no alvo e {est['media_chutes_fora']} para fora)\n"
        prompt += f"  - Criação e Controle: Posse de bola média de {est['media_posse']}% | Média de {est['media_passes']} passes/jogo (Precisão: {est['precisao_passes']}%)\n"
        prompt += f"  - Bolas Paradas e Ataque: Média de {est['media_escanteios']} escanteios a favor/jogo | Média de {est['media_impedimentos']} impedimentos/jogo\n"
        prompt += f"  - Disciplina: Média de {est['media_faltas']} faltas cometidas/jogo | {est['media_cartoes_amarelos']} cartões amarelos/jogo | {est['media_cartoes_vermelhos']} cartões vermelhos/jogo\n"

        jogos_ordenados = sorted(dados_time["ultimos_jogos"], key=lambda j: j["data"], reverse=True)
        prompt += f"\n  - Histórico recente ({len(jogos_ordenados)} partidas, da mais recente para a mais antiga):\n"

        for jogo in jogos_ordenados:
            data = jogo["data"].split("T")[0] if "T" in jogo["data"] else jogo["data"]
            det = jogo.get("estatisticas_detalhadas") or {}
            prompt += (
                f"    * {data} - {jogo['local']} vs {jogo['adversario']}: "
                f"{jogo['gols_feitos']} x {jogo['gols_sofridos']} ({jogo['resultado']}) "
                f"[Posse: {det.get('posse_bola', 0)}%, Chutes: {det.get('chutes_total', 0)} ({det.get('chutes_no_alvo', 0)} no alvo), "
                f"Escanteios: {det.get('escanteios', 0)}, Cartões: {det.get('cartoes_amarelos', 0)}A/{det.get('cartoes_vermelhos', 0)}V]\n"
            )

        return prompt

    def criar_prompt_confronto(self, dados_time_a, nome_time_a, dados_time_b, nome_time_b):
        """Cria o prompt completo para projeção e análise preditiva de um confronto futuro entre dois times."""

        estatisticas_a = self._formatar_estatisticas_para_prompt(dados_time_a, nome_time_a)
        estatisticas_b = self._formatar_estatisticas_para_prompt(dados_time_b, nome_time_b)

        prompt = f"""
Você é um analista esportivo do sistema Analytics FC.
Sua missão é projetar e prever o comportamento estatístico de um **confronto futuro que ainda irá acontecer** entre **{nome_time_a}** e **{nome_time_b}**, baseando-se exclusivamente nos dados reais dos últimos jogos de cada equipe fornecidos abaixo.
Não invente dados externos, escalações ou fatos que não estejam nas estatísticas informadas, e não mencione casas de apostas ou recomendações financeiras.

Dados estatísticos das equipes para o confronto:

{estatisticas_a}

{estatisticas_b}

Com base nesses indicadores, elabore uma análise preditiva completa do confronto futuro contendo:

1. **Probabilidades de Resultado do Confronto**:
   - Estime a probabilidade percentual de vitória de {nome_time_a}, empate e vitória de {nome_time_b}, justificando com o aproveitamento recente, saldo de gols e desempenho em casa/fora.

2. **Expectativa de Gols na Partida**:
   - Projeção com porcentagens estimadas para:
     * Mais/Menos de 1.5 gols na partida
     * Mais/Menos de 2.5 gols na partida
     * Mais/Menos de 3.5 gols na partida
   - Probabilidade de **Ambas as Equipes Marcarem** (Sim/Não) e tendência de **qual tempo (1º ou 2º tempo)** concentra maior expectativa de gols neste duelo.

3. **Dinâmica Tática, Posse e Finalizações**:
   - Compare o volume ofensivo (chutes totais e no alvo), controle de posse de bola e precisão de passes das duas equipes: quem tende a propor o jogo e quem tende a ser mais eficiente nas finalizações.

4. **Projeção de Escanteios e Bolas Paradas**:
   - Expectativa combinada de escanteios para o confronto (faixas de 8.5, 9.5 e 10.5 escanteios) com base nas médias individuais.

5. **Disciplina, Faltas e Cartões**:
   - Expectativa de intensidade física, faltas e cartões na partida (faixas de 3.5, 4.5 e 5.5 cartões).

6. **Pontos Fortes e Vulnerabilidades de Cada Equipe**:
   - O que os números mostram como principal trunfo e principal ponto fraco de {nome_time_a} e de {nome_time_b} para este jogo.

Para cada projeção, indique o **Nível de Confiança Estatística (Alto, Médio ou Baixo)** de acordo com a regularidade dos dados.

Formate sua resposta em HTML simples usando apenas elementos `<h4>`, `<p>`, `<ul>`, `<li>` e `<strong>`. Não utilize cabeçalhos `<h1>`, `<h2>` ou `<h3>`.

Ao final da análise, inclua obrigatoriamente estas duas seções:

<h4>Resumo Executivo da Previsão</h4>
Liste de forma direta e objetiva os principais números projetados para o confronto:
- Cenário mais provável de resultado ({nome_time_a}, Empate ou {nome_time_b}) e placar tendencial aproximado
- Expectativa de gols no 1º e no 2º tempo
- Projeções individuais por equipe (finalizações no alvo, posse de bola esperada e escanteios)

<h4>Principais Tendências Estatísticas do Confronto</h4>
Destaque os 5 indicadores estatísticos mais consistentes identificados no cruzamento de dados entre {nome_time_a} e {nome_time_b} (ex.: tendência de gols, ambas marcam, volume de finalizações, escanteios e cartões), informando o Nível de Confiança (Alto, Médio ou Baixo) de cada tendência.
"""

        return prompt

    def criar_prompt_time_unico(self, dados_time, nome_time):
        """Cria o prompt para diagnóstico de desempenho e projeção do próximo jogo de um único time."""

        estatisticas = self._formatar_estatisticas_para_prompt(dados_time, nome_time)

        prompt = f"""
Você é um analista esportivo do sistema Analytics FC.
Baseando-se exclusivamente nos dados estatísticos fornecidos abaixo, elabore um diagnóstico de desempenho recente e uma projeção estatística para o próximo compromisso de **{nome_time}**.
Não invente dados externos que não estejam nas estatísticas informadas e não mencione casas de apostas ou recomendações financeiras.

Dados estatísticos da equipe:

{estatisticas}

Com base nesses indicadores, forneça:

1. **Diagnóstico de Desempenho e Momento Atual**:
   - Análise do aproveitamento recente, diferença de rendimento jogando em Casa vs. Fora, consistência defensiva e eficiência ofensiva.

2. **Padrão de Gols e Comportamento por Tempo (1ºT vs. 2ºT)**:
   - Projeção percentual para o total de gols nas partidas da equipe (Mais/Menos de 1.5, 2.5 e 3.5 gols).
   - Frequência em que ambas as equipes marcam nos jogos de {nome_time}.
   - Análise da distribuição de gols entre o 1º tempo e o 2º tempo (em qual etapa a equipe é mais letal).

3. **Volume Ofensivo, Posse de Bola e Qualidade de Passe**:
   - Avaliação da média de finalizações (totais e no alvo), taxa de conversão em gols, posse de bola média e precisão de passes.

4. **Padrão de Escanteios e Bolas Paradas**:
   - Média de escanteios gerados por partida e projeção para faixas de escanteios nos jogos da equipe.

5. **Disciplina Tática (Faltas e Cartões)**:
   - Avaliação do índice de faltas cometidas e média de cartões amarelos/vermelhos.

6. **Pontos Fortes e Pontos de Atenção**:
   - Síntese técnica das principais virtudes e fragilidades demonstradas nos últimos {len(dados_time['ultimos_jogos'])} jogos.

Para cada projeção, indique o **Nível de Confiança Estatística (Alto, Médio ou Baixo)** com base na consistência da amostra.

Formate sua resposta em HTML simples usando apenas elementos `<h4>`, `<p>`, `<ul>`, `<li>` e `<strong>`. Não utilize cabeçalhos `<h1>`, `<h2>` ou `<h3>`.

Ao final da análise, inclua obrigatoriamente estas duas seções:

<h4>Resumo Executivo da Equipe</h4>
Liste de forma direta e concisa:
- Classificação do momento da equipe (ex.: consistente, ofensivo, equilibrado, oscilante)
- Expectativa média de gols, finalizações no alvo, posse de bola e escanteios para o próximo jogo

<h4>Principais Tendências Estatísticas da Equipe</h4>
Destaque os 5 padrões estatísticos mais fortes identificados nos jogos recentes de {nome_time}, indicando o Nível de Confiança (Alto, Médio ou Baixo) de cada indicador.
"""

        return prompt
