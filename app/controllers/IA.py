import os
from google import genai
from flask import current_app

MODELO = "gemini-2.5-flash"

def gerar_conteudo(prompt):
    """Função para gerar conteúdo usando o modelo Gemini"""
    try:
        api_key = os.getenv("GEMINI_KEY")
        if not api_key:
            raise ValueError("GEMINI_KEY não configurada no ambiente")

        client = genai.Client(api_key=api_key)
        resposta = client.models.generate_content(model=MODELO, contents=prompt)
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