document.addEventListener("DOMContentLoaded", function () {
    // Referenciar os elementos
    const btnEstatisticas = document.getElementById("btn-estatisticas");
    const selectTime = document.getElementById("time_a");
    const campeonatoSelect = document.getElementById("campeonato");
    const resultadoDiv = document.getElementById("resultado-estatisticas");

    btnEstatisticas.addEventListener("click", function () {
        // Obter os valores no momento do clique
        const timeId = selectTime.value;
        const campeonato = campeonatoSelect.value;

        // Imprimir informações de debug
        console.log("Botão Ver Estatísticas clicado");
        console.log("Time ID:", timeId);
        console.log("Campeonato:", campeonato);

        // Validações
        if (!campeonato) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione um campeonato.</p>";
            return;
        }

        if (!timeId) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione um time.</p>";
            return;
        }

        resultadoDiv.innerHTML = "<p>Carregando estatísticas...</p>";

        // Construir a URL completamente
        let url = `/estatisticas?time_id=${timeId}&campeonato=${campeonato}`;
        console.log("URL completa:", url);

        // Fazer a requisição
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

                const estat = data.estatisticas_gerais;
                const jogos = data.ultimos_jogos;

                let html = `
                    <h2 class="mt-5">Estatísticas</h2>
                    <h4 class="mt-3">Últimos ${jogos.length} jogos</h4>
                    <ul class="list-group mt-3">
                `;

                jogos.forEach(function(jogo) {
                    html += `
                        <li class="list-group-item">
                            ${new Date(jogo.data).toLocaleDateString()} - ${jogo.adversario} <br>
                            Placar: ${jogo.gols_feitos} x ${jogo.gols_sofridos} (${jogo.resultado})
                        </li>
                    `;
                });

                html += `</ul>
                    <div class="mt-4">
                        <h5>Resumo:</h5>
                        <p>Vitórias: ${estat.vitorias}</p>
                        <p>Empates: ${estat.empates}</p>
                        <p>Derrotas: ${estat.derrotas}</p>
                        <p>Média de Gols Feitos: ${estat.media_gols_feitos}</p>
                        <p>Média de Gols Sofridos: ${estat.media_gols_sofridos}</p>
                    </div>
                `;

                resultadoDiv.innerHTML = html;
            })
            .catch(function(erro) {
                console.error("Erro ao buscar estatísticas:", erro);
                resultadoDiv.innerHTML = "<p class='text-danger'>Erro ao buscar estatísticas. Verifique o console para mais detalhes.</p>";
            });
    });
});