document.addEventListener("DOMContentLoaded", function () {
    const btnEstatisticas = document.getElementById("btn-estatisticas");
    const selectTime = document.getElementById("time_a");
    const resultadoDiv = document.getElementById("resultado-estatisticas");

    btnEstatisticas.addEventListener("click", async function () {
        const timeId = selectTime.value;

        if (!timeId) {
            resultadoDiv.innerHTML = "<p class='text-danger'>Selecione um time.</p>";
            return;
        }

        resultadoDiv.innerHTML = "<p>Carregando estatísticas...</p>";

        try {
            const response = await fetch(`/estatisticas?time_id=${timeId}`);
            const data = await response.json();

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

            jogos.forEach(jogo => {
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

        } catch (erro) {
            console.error("Erro ao buscar estatísticas:", erro);
            resultadoDiv.innerHTML = "<p class='text-danger'>Erro ao buscar estatísticas.</p>";
        }
    });
});
