from flask import Blueprint, request, jsonify, current_app
from ..controllers.api_futebol import (
    buscar_times, 
    buscar_estatisticas_time,
    buscar_campeonatos
)
from ..controllers.analise import analisar_confronto

futebol_bp = Blueprint("futebol", __name__)

@futebol_bp.route("/times")
def get_times():
    campeonato = request.args.get("campeonato")

    if not campeonato:
        return jsonify({"erro": "Campeonato não informado"}), 400
    
    return buscar_times(campeonato)

@futebol_bp.route("/estatisticas", methods=["GET"])
def estatisticas_time():
    time_id = request.args.get("time_id")
    campeonato_id = request.args.get("campeonato")
    
    if not time_id or not campeonato_id:
        return jsonify({"erro": "Parâmetros inválidos"}), 400
    
    return buscar_estatisticas_time(time_id, campeonato_id)

@futebol_bp.route("/campeonatos")
def get_campeonatos():
    return buscar_campeonatos()

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
        
        current_app.logger.info(f"Parâmetros extraídos: campeonato={campeonato_id}, time_a={time_a_id}, time_b={time_b_id}")
        
        if not campeonato_id or not time_a_id or not time_b_id:
            missing = []
            if not campeonato_id: missing.append("campeonato")
            if not time_a_id: missing.append("time_a_id")
            if not time_b_id: missing.append("time_b_id")
            
            error_msg = f"Parâmetros obrigatórios ausentes: {', '.join(missing)}"
            current_app.logger.error(error_msg)
            return jsonify({"erro": error_msg}), 400
        
        current_app.logger.info(f"Analisando confronto: {time_a_nome} vs {time_b_nome}")
        
        try:
            dados_time_a_response = buscar_estatisticas_time(time_a_id, campeonato_id)
            current_app.logger.info(f"Tipo de retorno de buscar_estatisticas_time para time A: {type(dados_time_a_response)}")
            
            if isinstance(dados_time_a_response, tuple):
                current_app.logger.error(f"Erro ao buscar dados do time A: {dados_time_a_response}")
                return dados_time_a_response
            
            if not isinstance(dados_time_a_response, dict):
                dados_time_a = dados_time_a_response.get_json()
                current_app.logger.info("Convertendo resposta do time A de objeto Response para dict")
            else:
                dados_time_a = dados_time_a_response
                
            current_app.logger.info(f"Dados do time A obtidos com sucesso. Chaves disponíveis: {dados_time_a.keys()}")
        
            dados_time_b_response = buscar_estatisticas_time(time_b_id, campeonato_id)
            current_app.logger.info(f"Tipo de retorno de buscar_estatisticas_time para time B: {type(dados_time_b_response)}")
            
            if isinstance(dados_time_b_response, tuple):
                current_app.logger.error(f"Erro ao buscar dados do time B: {dados_time_b_response}")
                return dados_time_b_response
            
            if not isinstance(dados_time_b_response, dict):
                dados_time_b = dados_time_b_response.get_json()
                current_app.logger.info("Convertendo resposta do time B de objeto Response para dict")
            else:
                dados_time_b = dados_time_b_response
                
            current_app.logger.info(f"Dados do time B obtidos com sucesso. Chaves disponíveis: {dados_time_b.keys()}")
            
            current_app.logger.info("Iniciando análise de confronto")
            resultado_analise = analisar_confronto(
                dados_time_a, time_a_nome, 
                dados_time_b, time_b_nome, 
                campeonato_id
            )
            
            current_app.logger.info(f"Análise concluída. Success: {resultado_analise.get('success', False)}")
            return jsonify(resultado_analise)
            
        except Exception as e:
            current_app.logger.exception(f"Erro ao processar estatísticas ou análise: {str(e)}")
            return jsonify({"erro": f"Erro ao processar estatísticas: {str(e)}"}), 500
    
    except Exception as e:
        current_app.logger.exception(f"Erro geral na rota de análise: {str(e)}")
        return jsonify({"erro": f"Erro ao processar a análise: {str(e)}"}), 500