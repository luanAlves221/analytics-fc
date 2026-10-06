document.addEventListener("DOMContentLoaded", function() {
    const tipoAnaliseSelect = document.getElementById("tipo_analise");
    const timeASelect = document.getElementById("time_a");
    const timeBSelect = document.getElementById("time_b");
    const timeBContainer = document.getElementById("time_b_container");
    const btnEstatisticas = document.getElementById("btn-estatisticas");
    const resultadoDiv = document.getElementById("resultado-estatisticas");

    function verificarTipoAnalise() {
        const tipoAnalise = tipoAnaliseSelect.value;
        if (tipoAnalise === "confronto") {
            timeBContainer.style.display = "block";
        } else {
            timeBContainer.style.display = "none";
        }
    }

    function buscarEstatisticas() {
        const tipoAnalise = tipoAnaliseSelect.value;
        const timeIdA = timeASelect.value;
        const timeIdB = timeBSelect.value;

        if (!window.campeonatoSelecionado) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione um campeonato.</p>";
            return;
        }

        if (!timeIdA) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione o time A.</p>";
            return;
        }

        if (tipoAnalise === "confronto" && !timeIdB) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione o time B para análise de confronto.</p>";
            return;
        }

        if (tipoAnalise === "confronto" && timeIdA === timeIdB) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione dois times diferentes para a análise de confronto.</p>";
            return;
        }

        btnEstatisticas.disabled = true;
        btnEstatisticas.textContent = "Carregando...";
        resultadoDiv.innerHTML = "<p class='text-center'>Carregando estatísticas...</p>";

        if (tipoAnalise === "time_unico") {
            buscarEstatisticasTimeUnico(timeIdA);
        } else {
            buscarEstatisticasConfronto(timeIdA, timeIdB);
        }
    }

    function buscarEstatisticasTimeUnico(timeId) {
        const url = `/estatisticas?time_id=${timeId}&campeonato=${window.campeonatoSelecionado}`;

        fetch(url)
            .then(function(response) {
                if (!response.ok) {
                    throw new Error("Erro na resposta: " + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                if (data.erro) {
                    resultadoDiv.innerHTML = `<p class="text-danger">${escapeHtml(data.erro)}</p>`;
                    return;
                }

                const timeNome = timeASelect.options[timeASelect.selectedIndex].text;
                exibirEstatisticasTime(data, timeNome);
            })
            .catch(function(erro) {
                console.error("Erro ao buscar estatísticas:", erro);
                resultadoDiv.innerHTML = "<p class='text-danger'>Erro ao buscar estatísticas. Verifique o console para mais detalhes.</p>";
            })
            .finally(function() {
                btnEstatisticas.disabled = false;
                btnEstatisticas.textContent = "Ver Estatísticas";
            });
    }

    function buscarEstatisticasConfronto(timeIdA, timeIdB) {
        const urlA = `/estatisticas?time_id=${timeIdA}&campeonato=${window.campeonatoSelecionado}`;
        const urlB = `/estatisticas?time_id=${timeIdB}&campeonato=${window.campeonatoSelecionado}`;

        Promise.all([
            fetch(urlA).then(r => r.json()),
            fetch(urlB).then(r => r.json())
        ])
        .then(function([dataA, dataB]) {
            if (dataA.erro) {
                resultadoDiv.innerHTML = `<p class="text-danger">${escapeHtml(dataA.erro)}</p>`;
                return;
            }

            if (dataB.erro) {
                resultadoDiv.innerHTML = `<p class="text-danger">${escapeHtml(dataB.erro)}</p>`;
                return;
            }

            const timeANome = timeASelect.options[timeASelect.selectedIndex].text;
            const timeBNome = timeBSelect.options[timeBSelect.selectedIndex].text;

            let html = "";
            html += criarHtmlEstatisticasTime(dataA, timeANome);
            html += criarHtmlEstatisticasTime(dataB, timeBNome);
            resultadoDiv.innerHTML = html;
        })
        .catch(function(erro) {
            console.error("Erro ao buscar estatísticas de confronto:", erro);
            resultadoDiv.innerHTML = "<p class='text-danger'>Erro ao buscar estatísticas de confronto. Verifique o console para mais detalhes.</p>";
        })
        .finally(function() {
            btnEstatisticas.disabled = false;
            btnEstatisticas.textContent = "Ver Estatísticas";
        });
    }

    function exibirEstatisticasTime(data, timeNome) {
        const html = criarHtmlEstatisticasTime(data, timeNome);
        resultadoDiv.innerHTML = html;
    }

    function criarHtmlEstatisticasTime(data, timeNome) {
        const estat = data.estatisticas_gerais;
        const jogosOrdenados = [...data.ultimos_jogos].sort((a, b) => {
            return new Date(b.data) - new Date(a.data);
        });

        let html = `
            <h2 class="mt-5">Estatísticas: ${escapeHtml(timeNome)}</h2>
            <h4 class="mt-3">Últimos ${jogosOrdenados.length} jogos</h4>
            <ul class="list-group mt-3">
        `;

        jogosOrdenados.forEach(function(jogo) {
            html += `
                <li class="list-group-item">
                    ${new Date(jogo.data).toLocaleDateString()} - ${escapeHtml(jogo.local)}: ${escapeHtml(jogo.adversario)} <br>
                    Placar: ${jogo.gols_feitos} x ${jogo.gols_sofridos} (${escapeHtml(jogo.resultado)})
                    <div class="mt-2">
                        <strong>Estatísticas da partida:</strong>
                        <div class="row small">
                            <div class="col-md-4">
                                <p>Escanteios: ${jogo.estatisticas_detalhadas.escanteios || 0}</p>
                                <p>Chutes: ${jogo.estatisticas_detalhadas.chutes_total || 0} (${jogo.estatisticas_detalhadas.chutes_no_alvo || 0} no alvo)</p>
                            </div>
                            <div class="col-md-4">
                                <p>Cartões amarelos: ${jogo.estatisticas_detalhadas.cartoes_amarelos || 0}</p>
                                <p>Cartões vermelhos: ${jogo.estatisticas_detalhadas.cartoes_vermelhos || 0}</p>
                                <p>Posse de bola: ${jogo.estatisticas_detalhadas.posse_bola || 0}%</p>
                            </div>
                            <div class="col-md-4">
                                <p>Faltas: ${jogo.estatisticas_detalhadas.faltas || 0}</p>
                                <p>Impedimentos: ${jogo.estatisticas_detalhadas.impedimentos || 0}</p>
                            </div>
                        </div>
                    </div>
                </li>
            `;
        });

        html += `</ul>
            <div class="mt-4">
                <h5>Resumo:</h5>
                <div class="row">
                    <div class="col-md-4">
                        <h6>Resultados:</h6>
                        <p>Vitórias: ${estat.vitorias} (Casa: ${estat.vitorias_casa}, Fora: ${estat.vitorias_fora})</p>
                        <p>Empates: ${estat.empates}</p>
                        <p>Derrotas: ${estat.derrotas}</p>
                        <p>Aproveitamento: ${estat.aproveitamento}%</p>
                    </div>

                    <div class="col-md-4">
                        <h6>Gols:</h6>
                        <p>Média de Gols Feitos: ${estat.media_gols_feitos}</p>
                        <p>Média de Gols Sofridos: ${estat.media_gols_sofridos}</p>
                        <p>Média Total de Gols: ${estat.media_gols_total}</p>
                        <p>Gols por Tempo: 1ºT: ${estat.gols_primeiro_tempo} (${estat.porcentagem_gols_1t}%) | 2ºT: ${estat.gols_segundo_tempo} (${estat.porcentagem_gols_2t}%)</p>
                        <p>Pênaltis Convertidos: ${estat.total_penaltis}</p>
                        <p>Over 1.5: ${estat.porcentagem_over_1_5}% (${estat.jogos_over_1_5}/${jogosOrdenados.length})</p>
                        <p>Over 2.5: ${estat.porcentagem_over_2_5}% (${estat.jogos_over_2_5}/${jogosOrdenados.length})</p>
                        <p>Ambas marcam: ${estat.porcentagem_ambas_marcam}% (${estat.jogos_ambas_marcam}/${jogosOrdenados.length})</p>
                    </div>

                    <div class="col-md-4">
                        <h6>Estatísticas:</h6>
                        <p>Média de Escanteios: ${estat.media_escanteios}</p>
                        <p>Média de Chutes: ${estat.media_chutes} (${estat.media_chutes_alvo} no alvo)</p>
                        <p>Média de Cartões Amarelos: ${estat.media_cartoes_amarelos}</p>
                        <p>Média de Cartões Vermelhos: ${estat.media_cartoes_vermelhos}</p>
                        <p>Média de Faltas: ${estat.media_faltas}</p>
                        <p>Posse de Bola Média: ${estat.media_posse}%</p>
                        <p>Precisão nos Passes: ${estat.precisao_passes}%</p>
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    tipoAnaliseSelect.addEventListener("change", verificarTipoAnalise);
    btnEstatisticas.addEventListener("click", buscarEstatisticas);
    verificarTipoAnalise();
});