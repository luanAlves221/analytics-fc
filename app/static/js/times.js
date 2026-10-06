window.campeonatoSelecionado = "";

document.addEventListener("DOMContentLoaded", function() {
    const campeonatoSelect = document.getElementById("campeonato");
    const timeASelect = document.getElementById("time_a");
    const timeBSelect = document.getElementById("time_b");

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

        if (!window.campeonatoSelecionado) {
            timeASelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            timeBSelect.innerHTML = "<option value=''>Selecione um campeonato primeiro</option>";
            return;
        }

        timeASelect.innerHTML = "<option value=''>Carregando times...</option>";
        timeBSelect.innerHTML = "<option value=''>Carregando times...</option>";

        const timesCacheKey = `times_${window.campeonatoSelecionado}`;
        const timesCache = localStorage.getItem(timesCacheKey);

        if (timesCache) {
            try {
                const cacheData = JSON.parse(timesCache);
                const agora = new Date().getTime();

                if (cacheData.timestamp && (agora - cacheData.timestamp < 86400000)) {
                    preencherSelects(cacheData.times);
                    return;
                }
            } catch (e) {
                console.error("Erro ao ler cache de times:", e);
            }
        }

        fetch(`/times?campeonato=${window.campeonatoSelecionado}`)
            .then(function(response) {
                return response.json();
            })
            .then(function(times) {
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

    campeonatoSelect.addEventListener("change", carregarTimes);
    carregarTimes();
});