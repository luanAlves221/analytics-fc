window.campeonatoSelecionado = "";

function escapeHtml(texto) {
    const div = document.createElement("div");
    div.textContent = texto == null ? "" : String(texto);
    return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", function() {
    const campeonatoSelect = document.getElementById("campeonato");
    const timeASelect = document.getElementById("time_a");
    const timeBSelect = document.getElementById("time_b");

    const tabelaContainer = document.getElementById("tabela-container");
    const btnTabela = document.getElementById("btn-tabela");
    const resultadoTabela = document.getElementById("resultado-tabela");
    let tabelaCarregadaParaLiga = "";

    function obterNomeCampeonato() {
        const optionSelecionada = campeonatoSelect.options[campeonatoSelect.selectedIndex];
        return optionSelecionada && campeonatoSelect.value ? optionSelecionada.textContent.trim() : "";
    }

    function atualizarEstadoBotaoTabela() {
        const nomeLiga = obterNomeCampeonato();
        if (!nomeLiga) {
            tabelaContainer.style.display = "none";
            resultadoTabela.style.display = "none";
            resultadoTabela.innerHTML = "";
            tabelaCarregadaParaLiga = "";
            return;
        }

        tabelaContainer.style.display = "block";
        resultadoTabela.style.display = "none";
        resultadoTabela.innerHTML = "";
        tabelaCarregadaParaLiga = "";
        btnTabela.disabled = false;
        btnTabela.textContent = `Ver Tabela ${nomeLiga}`;
    }

    function renderizarTabela(dados) {
        if (!dados.grupos || dados.grupos.length === 0) {
            resultadoTabela.innerHTML = "<p class='text-muted'>Tabela de classificação indisponível no momento.</p>";
            return;
        }

        let html = "";
        dados.grupos.forEach(function(grupo) {
            html += `<div class="card shadow-sm mb-3">`;
            html += `<div class="card-header bg-dark text-white fw-bold">${escapeHtml(grupo.nome)}</div>`;
            html += `<div class="table-responsive">`;
            html += `<table class="table table-sm table-striped table-hover mb-0 align-middle">`;
            html += `<thead class="table-light">
                        <tr>
                            <th class="text-center">#</th>
                            <th>Time</th>
                            <th class="text-center" title="Pontos">P</th>
                            <th class="text-center" title="Jogos">J</th>
                            <th class="text-center" title="Vitórias">V</th>
                            <th class="text-center" title="Empates">E</th>
                            <th class="text-center" title="Derrotas">D</th>
                            <th class="text-center" title="Gols Pró">GP</th>
                            <th class="text-center" title="Gols Contra">GC</th>
                            <th class="text-center" title="Saldo de Gols">SG</th>
                        </tr>
                     </thead><tbody>`;

            (grupo.classificacao || []).forEach(function(item) {
                html += `<tr>
                            <td class="text-center fw-bold">${escapeHtml(item.posicao)}</td>
                            <td>${escapeHtml(item.time)}</td>
                            <td class="text-center fw-bold">${escapeHtml(item.pontos)}</td>
                            <td class="text-center">${escapeHtml(item.jogos)}</td>
                            <td class="text-center">${escapeHtml(item.vitorias)}</td>
                            <td class="text-center">${escapeHtml(item.empates)}</td>
                            <td class="text-center">${escapeHtml(item.derrotas)}</td>
                            <td class="text-center">${escapeHtml(item.gols_pro)}</td>
                            <td class="text-center">${escapeHtml(item.gols_contra)}</td>
                            <td class="text-center">${escapeHtml(item.saldo_gols)}</td>
                         </tr>`;
            });

            html += `</tbody></table></div></div>`;
        });

        resultadoTabela.innerHTML = html;
    }

    if (btnTabela) {
        btnTabela.addEventListener("click", function() {
            const nomeLiga = obterNomeCampeonato();
            if (!window.campeonatoSelecionado || !nomeLiga) {
                return;
            }

            if (resultadoTabela.style.display === "block") {
                resultadoTabela.style.display = "none";
                btnTabela.textContent = `Ver Tabela ${nomeLiga}`;
                return;
            }

            if (tabelaCarregadaParaLiga === window.campeonatoSelecionado && resultadoTabela.innerHTML !== "") {
                resultadoTabela.style.display = "block";
                btnTabela.textContent = `Ocultar Tabela ${nomeLiga}`;
                return;
            }

            btnTabela.disabled = true;
            btnTabela.textContent = `Carregando Tabela ${nomeLiga}...`;

            fetch(`/tabela?campeonato=${encodeURIComponent(window.campeonatoSelecionado)}`)
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error("Erro ao carregar tabela: " + response.status);
                    }
                    return response.json();
                })
                .then(function(dados) {
                    if (dados.erro) {
                        throw new Error(dados.erro);
                    }
                    renderizarTabela(dados);
                    tabelaCarregadaParaLiga = window.campeonatoSelecionado;
                    resultadoTabela.style.display = "block";
                    btnTabela.textContent = `Ocultar Tabela ${nomeLiga}`;
                })
                .catch(function(erro) {
                    console.error("Erro ao buscar tabela:", erro);
                    resultadoTabela.innerHTML = "<p class='text-danger'>Erro ao carregar a tabela do campeonato.</p>";
                    resultadoTabela.style.display = "block";
                    btnTabela.textContent = `Ver Tabela ${nomeLiga}`;
                })
                .finally(function() {
                    btnTabela.disabled = false;
                });
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

    function carregarTimes() {
        window.campeonatoSelecionado = campeonatoSelect.value;
        atualizarEstadoBotaoTabela();

        if (!window.campeonatoSelecionado) {
            timeASelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            timeBSelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            return;
        }

        timeASelect.innerHTML = "<option value=''>Carregando times...</option>";
        timeBSelect.innerHTML = "<option value=''>Carregando times...</option>";

        const timesCacheKey = `espn_times_${window.campeonatoSelecionado}`;
        const timesCache = localStorage.getItem(timesCacheKey);

        if (timesCache) {
            try {
                const cacheData = JSON.parse(timesCache);
                const agora = new Date().getTime();

                if (cacheData.timestamp && Array.isArray(cacheData.times) && (agora - cacheData.timestamp < 86400000)) {
                    preencherSelects(cacheData.times);
                    return;
                }
            } catch (e) {
                console.error("Erro ao ler cache de times:", e);
            }
        }

        fetch(`/times?campeonato=${encodeURIComponent(window.campeonatoSelecionado)}`)
            .then(function(response) {
                if (!response.ok) {
                    throw new Error("Erro ao buscar times: " + response.status);
                }
                return response.json();
            })
            .then(function(times) {
                if (!Array.isArray(times)) {
                    throw new Error(times.erro || "Formato inválido de resposta");
                }
                const cacheData = {
                    times: times,
                    timestamp: new Date().getTime()
                };
                localStorage.setItem(timesCacheKey, JSON.stringify(cacheData));
                preencherSelects(times);
            })
            .catch(function(erro) {
                console.error("Erro ao carregar times:", erro);
                timeASelect.innerHTML = "<option value=''>Erro ao carregar times</option>";
                timeBSelect.innerHTML = "<option value=''>Erro ao carregar times</option>";
            });
    }

    campeonatoSelect.addEventListener("change", carregarTimes);
    carregarTimes();
});