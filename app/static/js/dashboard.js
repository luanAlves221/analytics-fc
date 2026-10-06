document.addEventListener("DOMContentLoaded", () => {
    const campeonatoSelect = document.getElementById("campeonato");
    const timeASelect = document.getElementById("time_a");

    campeonatoSelect.addEventListener("change", () => {
        const campeonato = campeonatoSelect.value;
        console.log("Campeonato selecionado (change event):", campeonato);

        // Limpar o dropdown de times se "Nenhum" for selecionado
        if (!campeonato) {
            timeASelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            return;
        }

        // Caso contrário, carregar times do campeonato selecionado
        fetch(`/times?campeonato=${campeonato}`)
            .then(response => response.json())
            .then(times => {
                timeASelect.innerHTML = "";
                times.forEach(time => {
                    const option = document.createElement("option");
                    option.value = time.id;
                    option.textContent = time.name;
                    timeASelect.appendChild(option);
                });
            })
            .catch(() => {
                alert("Erro ao carregar os times.");
            });
    });

    // Disparar o evento de change para configurar inicialmente
    campeonatoSelect.dispatchEvent(new Event("change"));
});