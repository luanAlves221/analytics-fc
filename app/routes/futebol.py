from flask import Blueprint, request, jsonify, current_app
from ..controllers.cliente_api import cliente_api
from ..controllers.analise import servico_analise

futebol_bp = Blueprint("futebol", __name__)

@futebol_bp.route("/times")
def get_times():
    campeonato = request.args.get("campeonato")

    if not campeonato:
        return jsonify({"erro": "Campeonato não informado"}), 400

    return cliente_api.buscar_times(campeonato)

@futebol_bp.route("/estatisticas", methods=["GET"])
def estatisticas_time():
    time_id = request.args.get("time_id")
    campeonato_id = request.args.get("campeonato")

    if not time_id or not campeonato_id:
        return jsonify({"erro": "Parâmetros inválidos"}), 400

    return cliente_api.buscar_estatisticas_time(time_id, campeonato_id)

@futebol_bp.route("/campeonatos")
def get_campeonatos():
    return cliente_api.buscar_campeonatos()

@futebol_bp.route('/analise-ia', methods=['POST'])
def analise_ia():
    """Endpoint para análise com IA de confrontos entre times"""

    try:
        dados = request.get_json()
        current_app.logger.info(f"Dados recebidos na requisição: {dados}")

        if not dados:
            current_app.logger.error("Nenhum dado JSON recebido no corpo da requisição")
            return jsonify({"erro": "Dados não fornecidos"}), 400

        campeonato_id = dados.get('campeonato')
        time_a_id = dados.get('time_a_id')
        time_a_nome = dados.get('time_a_nome', 'Time A')
        time_b_id = dados.get('time_b_id')
        time_b_nome = dados.get('time_b_nome', 'Time B')
        tipo_analise = dados.get('tipo_analise', 'confronto')

        current_app.logger.info(f"Parâmetros extraídos: campeonato={campeonato_id}, time_a={time_a_id}, time_b={time_b_id}, tipo_analise={tipo_analise}")

        if not campeonato_id or not time_a_id:
            missing = []
            if not campeonato_id: missing.append("campeonato")
            if not time_a_id: missing.append("time_a_id")

            error_msg = f"Parâmetros obrigatórios ausentes: {', '.join(missing)}"
            current_app.logger.error(error_msg)
            return jsonify({"erro": error_msg}), 400

        try:
            dados_time_a_response, status_a = cliente_api.buscar_estatisticas_time(time_a_id, campeonato_id)

            if status_a != 200:
                current_app.logger.error(f"Erro ao buscar dados do time A: {status_a}")
                return dados_time_a_response, status_a

            dados_time_a = dados_time_a_response.get_json()
            current_app.logger.info(f"Dados do time A obtidos com sucesso. Chaves disponíveis: {dados_time_a.keys()}")

            if tipo_analise == "time_unico":
                current_app.logger.info("Iniciando análise de time único")
                resultado_analise = servico_analise.analisar_time_unico(dados_time_a, time_a_nome)
            else:
                if not time_b_id:
                    current_app.logger.error("Parâmetro obrigatório ausente: time_b_id")
                    return jsonify({"erro": "Parâmetros obrigatórios ausentes: time_b_id"}), 400

                dados_time_b_response, status_b = cliente_api.buscar_estatisticas_time(time_b_id, campeonato_id)

                if status_b != 200:
                    current_app.logger.error(f"Erro ao buscar dados do time B: {status_b}")
                    return dados_time_b_response, status_b

                dados_time_b = dados_time_b_response.get_json()
                current_app.logger.info(f"Dados do time B obtidos com sucesso. Chaves disponíveis: {dados_time_b.keys()}")

                current_app.logger.info(f"Analisando confronto: {time_a_nome} vs {time_b_nome}")
                resultado_analise = servico_analise.analisar_confronto(
                    dados_time_a, time_a_nome,
                    dados_time_b, time_b_nome
                )

            current_app.logger.info(f"Análise concluída. Success: {resultado_analise.get('success', False)}")
            return jsonify(resultado_analise)

        except Exception as e:
            current_app.logger.exception(f"Erro ao processar estatísticas ou análise: {str(e)}")
            return jsonify({"erro": f"Erro ao processar estatísticas: {str(e)}"}), 500

    except Exception as e:
        current_app.logger.exception(f"Erro geral na rota de análise: {str(e)}")
        return jsonify({"erro": f"Erro ao processar a análise: {str(e)}"}), 500