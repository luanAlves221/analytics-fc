document.addEventListener("DOMContentLoaded", function() {
    const campeonatoSelect = document.getElementById("campeonato");
    const tipoAnaliseSelect = document.getElementById("tipo_analise");
    const timeASelect = document.getElementById("time_a");
    const timeBSelect = document.getElementById("time_b");
    const timeBContainer = document.getElementById("time_b_container");
    const btnEstatisticas = document.getElementById("btn-estatisticas");
    const resultadoDiv = document.getElementById("resultado-estatisticas");
    const formAnalise = document.getElementById("form-analise");
    
    let campeonatoSelecionado = "";
    
    function carregarTimes() {
        campeonatoSelecionado = campeonatoSelect.value;
        console.log("Campeonato selecionado:", campeonatoSelecionado);
    
        if (!campeonatoSelecionado) {
            timeASelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            timeBSelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            return;
        }
    
        timeASelect.innerHTML = "<option value=''>Carregando times...</option>";
        timeBSelect.innerHTML = "<option value=''>Carregando times...</option>";

        // Verificar se os dados dos times estão em cache e são válidos
        const timesCacheKey = `times_${campeonatoSelecionado}`;
        const timesCache = localStorage.getItem(timesCacheKey);
        
        if (timesCache) {
            try {
                const cacheData = JSON.parse(timesCache);
                const agora = new Date().getTime();
                
                // Verificar se o cache ainda é válido (24 horas = 86400000 ms)
                if (cacheData.timestamp && (agora - cacheData.timestamp < 86400000)) {
                    console.log("Usando times do cache local");
                    preencherSelects(cacheData.times);
                    return;
                } else {
                    console.log("Cache de times expirado");
                }
            } catch (e) {
                console.error("Erro ao ler cache de times:", e);
            }
        }

        // Se não tem cache válido, busca da API
        console.log("Buscando times da API");
        fetch(`/times?campeonato=${campeonatoSelecionado}`)
            .then(function(response) {
                return response.json();
            })
            .then(function(times) {
                // Salvar no cache
                const cacheData = {
                    times: times,
                    timestamp: new Date().getTime()
                };
                localStorage.setItem(timesCacheKey, JSON.stringify(cacheData));
                
                preencherSelects(times);
            })
            .catch(function(erro) {
                console.error("Erro ao carregar times:", erro);
                alert("Erro ao carregar os times.");
            });
    }
    
    function preencherSelects(times) {
        timeASelect.innerHTML = "<option value=''>Selecione o time A</option>";
        timeBSelect.innerHTML = "<option value=''>Selecione o time B</option>";
    
        times.forEach(function(time) {
            const optionA = document.createElement("option");
            optionA.value = time.id;
            optionA.textContent = time.name;
            timeASelect.appendChild(optionA);
    
            const optionB = document.createElement("option");
            optionB.value = time.id;
            optionB.textContent = time.name;
            timeBSelect.appendChild(optionB);
        });
    }
    
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
        
        console.log("Buscando estatísticas para:");
        console.log("- Tipo de análise:", tipoAnalise);
        console.log("- Time A ID:", timeIdA);
        console.log("- Time B ID:", timeIdB);
        console.log("- Campeonato:", campeonatoSelecionado);
        
        if (!campeonatoSelecionado) {
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
        
        resultadoDiv.innerHTML = "<p>Carregando estatísticas...</p>";
        
        if (tipoAnalise === "time_unico") {
            buscarEstatisticasTimeUnico(timeIdA);
        } else {
            buscarEstatisticasConfronto(timeIdA, timeIdB);
        }
    }
    
    function buscarEstatisticasTimeUnico(timeId) {
        const url = `/estatisticas?time_id=${timeId}&campeonato=${campeonatoSelecionado}`;
        console.log("URL completa:", url);
        
        fetch(url)
            .then(function(response) {
                console.log("Status da resposta:", response.status);
                if (!response.ok) {
                    throw new Error("Erro na resposta: " + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                console.log("Dados recebidos:", data);
                
                if (data.erro) {
                    resultadoDiv.innerHTML = `<p class="text-danger">${data.erro}</p>`;
                    return;
                }
                
                const timeNome = timeASelect.options[timeASelect.selectedIndex].text;
                exibirEstatisticasTime(data, timeNome);
            })
            .catch(function(erro) {
                console.error("Erro ao buscar estatísticas:", erro);
                resultadoDiv.innerHTML = "<p class='text-danger'>Erro ao buscar estatísticas. Verifique o console para mais detalhes.</p>";
            });
    }
    
    function buscarEstatisticasConfronto(timeIdA, timeIdB) {
        const urlA = `/estatisticas?time_id=${timeIdA}&campeonato=${campeonatoSelecionado}`;
        const urlB = `/estatisticas?time_id=${timeIdB}&campeonato=${campeonatoSelecionado}`;
        
        Promise.all([
            fetch(urlA).then(r => r.json()),
            fetch(urlB).then(r => r.json())
        ])
        .then(function([dataA, dataB]) {
            if (dataA.erro) {
                resultadoDiv.innerHTML = `<p class="text-danger">${dataA.erro}</p>`;
                return;
            }
            
            if (dataB.erro) {
                resultadoDiv.innerHTML = `<p class="text-danger">${dataB.erro}</p>`;
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
            <h2 class="mt-5">Estatísticas: ${timeNome}</h2>
            <h4 class="mt-3">Últimos ${jogosOrdenados.length} jogos</h4>
            <ul class="list-group mt-3">
        `;
        
        jogosOrdenados.forEach(function(jogo) {
            html += `
                <li class="list-group-item">
                    ${new Date(jogo.data).toLocaleDateString()} - ${jogo.local}: ${jogo.adversario} <br>
                    Placar: ${jogo.gols_feitos} x ${jogo.gols_sofridos} (${jogo.resultado})
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
    
    function solicitarAnaliseIA() {
        const tipoAnalise = tipoAnaliseSelect.value;
        const timeIdA = timeASelect.value;
        const timeIdB = timeBSelect.value;
        const timeANome = timeASelect.options[timeASelect.selectedIndex]?.text || "";
        const timeBNome = timeBSelect.options[timeBSelect.selectedIndex]?.text || "";
        
        if (!campeonatoSelecionado) {
            alert("Selecione um campeonato primeiro.");
            return false;
        }
        
        if (!timeIdA) {
            alert("Selecione o time A primeiro.");
            return false;
        }
        
        if (tipoAnalise === "confronto" && !timeIdB) {
            alert("Selecione o time B para análise de confronto.");
            return false;
        }

        resultadoDiv.innerHTML = "<div class='text-center'><p>Processando análise com IA, por favor aguarde...</p><div class='spinner-border' role='status'><span class='visually-hidden'>Carregando...</span></div></div>";
        
        // Obter o token CSRF do campo escondido no formulário
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        console.log("Token CSRF obtido:", csrfToken);
        
        const dados = {
            tipo_analise: tipoAnalise,
            campeonato: campeonatoSelecionado,
            time_a_id: timeIdA,
            time_a_nome: timeANome
        };
        
        if (tipoAnalise === "confronto") {
            dados.time_b_id = timeIdB;
            dados.time_b_nome = timeBNome;
        }
        
        console.log("Enviando dados para análise de IA:", dados);
        console.log("JSON a ser enviado:", JSON.stringify(dados));
        
        fetch('/analise-ia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Adicionar o token CSRF nos headers
            },
            body: JSON.stringify(dados)
        })
        .then(response => {
            console.log("Status da resposta da análise IA:", response.status);
            console.log("Headers da resposta:", [...response.headers.entries()]);
            
            if (!response.ok) {
                return response.text().then(text => {
                    console.error("Texto da resposta de erro:", text);
                    throw new Error('Erro na requisição: ' + response.status);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Resposta da análise de IA:", data);
            
            if (data.erro) {
                resultadoDiv.innerHTML = `<div class="alert alert-danger">${data.erro}</div>`;
                return;
            }
            
            exibirResultadoAnaliseIA(data);
        })
        .catch(erro => {
            console.error('Erro ao solicitar análise da IA:', erro);
            resultadoDiv.innerHTML = `<div class="alert alert-danger">Erro ao processar a análise com IA. Tente novamente mais tarde.</div>`;
        });
        
        return false;
    }
    
    function exibirResultadoAnaliseIA(data) {
        let html = `
            <div class="mt-4">
                <h3 class="text-center mb-4">Análise de IA</h3>
                <div class="card">
                    <div class="card-body">
                        ${data.analise_formatada}
                    </div>
                </div>
            </div>
        `;
        
        resultadoDiv.innerHTML = html;
    }
    
    // Event Listeners
    campeonatoSelect.addEventListener("change", carregarTimes);
    tipoAnaliseSelect.addEventListener("change", verificarTipoAnalise);
    btnEstatisticas.addEventListener("click", buscarEstatisticas);
    
    // Intercept form submission for IA analysis
    formAnalise.addEventListener("submit", function(event) {
        event.preventDefault();
        console.log("Formulário submetido. Submitter:", event.submitter?.value);
        
        if (event.submitter && event.submitter.value === "analise_ia") {
            console.log("Iniciando solicitação de análise IA");
            solicitarAnaliseIA();
        }
    });
    
    verificarTipoAnalise();
    carregarTimes();
});