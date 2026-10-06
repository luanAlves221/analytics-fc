import os
import google.generativeai as genai
from flask import current_app

def configurar_gemini():
    """Configura e retorna o modelo Gemini"""
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        raise ValueError("GEMINI_KEY não configurada no ambiente")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

def gerar_conteudo(prompt):
    """Função para gerar conteúdo usando o modelo Gemini"""
    try:
        modelo = configurar_gemini()
        resposta = modelo.generate_content(prompt)
        return {
            "texto": resposta.text,
            "success": True
        }
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar conteúdo com Gemini: {str(e)}")
        return {
            "texto": "<p>Erro ao gerar análise. Por favor, tente novamente mais tarde.</p>",
            "success": False,
            "erro": str(e)
        }