document.addEventListener("DOMContentLoaded", function() {
    const tipoAnaliseSelect = document.getElementById("tipo_analise");
    const timeASelect = document.getElementById("time_a");
    const timeBSelect = document.getElementById("time_b");
    const formAnalise = document.getElementById("form-analise");
    const btnAnaliseIA = document.getElementById("btn-analise-ia");
    const resultadoDiv = document.getElementById("resultado-ia") || document.getElementById("resultado-estatisticas");

    function solicitarAnaliseIA() {
        const tipoAnalise = tipoAnaliseSelect.value;
        const timeIdA = timeASelect.value;
        const timeIdB = timeBSelect.value;
        const timeANome = timeASelect.options[timeASelect.selectedIndex]?.text || "";
        const timeBNome = timeBSelect.options[timeBSelect.selectedIndex]?.text || "";

        if (!window.campeonatoSelecionado) {
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

        if (tipoAnalise === "confronto" && timeIdA === timeIdB) {
            alert("Selecione dois times diferentes para a análise de confronto.");
            return false;
        }

        if (btnAnaliseIA) {
            btnAnaliseIA.disabled = true;
            btnAnaliseIA.textContent = "Analisando...";
        }

        resultadoDiv.innerHTML = "<div class='text-center'><p>Processando análise com IA, por favor aguarde...</p><div class='spinner-border' role='status'><span class='visually-hidden'>Carregando...</span></div></div>";

        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        const dados = {
            tipo_analise: tipoAnalise,
            campeonato: window.campeonatoSelecionado,
            time_a_id: timeIdA,
            time_a_nome: timeANome
        };

        if (tipoAnalise === "confronto") {
            dados.time_b_id = timeIdB;
            dados.time_b_nome = timeBNome;
        }

        fetch('/analise-ia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dados)
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    console.error("Texto da resposta de erro:", text);
                    throw new Error('Erro na requisição: ' + response.status);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.erro) {
                resultadoDiv.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.erro)}</div>`;
                return;
            }
            exibirResultadoAnaliseIA(data);
        })
        .catch(erro => {
            console.error('Erro ao solicitar análise da IA:', erro);
            resultadoDiv.innerHTML = `<div class="alert alert-danger">Erro ao processar a análise com IA. Tente novamente mais tarde.</div>`;
        })
        .finally(() => {
            if (btnAnaliseIA) {
                btnAnaliseIA.disabled = false;
                btnAnaliseIA.textContent = "Análise com IA";
            }
        });

        return false;
    }

    function exibirResultadoAnaliseIA(data) {
        let html = `
            <div class="mt-4">
                <h3 class="text-center mb-4">Análise de IA</h3>
                <div class="card shadow-sm">
                    <div class="card-body p-4">
                        ${data.analise_formatada}
                    </div>
                </div>
            </div>
        `;

        resultadoDiv.innerHTML = html;
    }

    formAnalise.addEventListener("submit", function(event) {
        event.preventDefault();
        if (event.submitter && event.submitter.value === "analise_ia") {
            solicitarAnaliseIA();
        }
    });
});