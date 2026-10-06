import os
from flask import current_app
from google import genai
from .prompts_ia import PromptBuilder

MODELO = "gemini-3.8-flash"


def _limpar_html(texto):
    """Remove cercas de código markdown (```html ... ```) caso o modelo as inclua."""
    if not texto:
        return ""
    limpo = texto.strip()
    if limpo.startswith("```"):
        linhas = limpo.splitlines()
        if linhas and linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        limpo = "\n".join(linhas).strip()
    return limpo


def gerar_conteudo(prompt):
    """Gera conteúdo preditivo usando o modelo Gemini."""
    try:
        api_key = os.getenv("GEMINI_KEY")
        if not api_key:
            raise ValueError("GEMINI_KEY não configurada no ambiente")

        client = genai.Client(api_key=api_key)
        if hasattr(client, "interactions"):
            interaction = client.interactions.create(model=MODELO, input=prompt)
            texto = getattr(interaction, "output_text", None) or interaction.outputs[-1].text
        else:
            resposta = client.models.generate_content(model=MODELO, contents=prompt)
            texto = resposta.text

        return {
            "texto": _limpar_html(texto),
            "success": True,
        }
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar conteúdo com Gemini: {str(e)}")
        return {
            "texto": "<p>Erro ao gerar análise. Por favor, tente novamente mais tarde.</p>",
            "success": False,
            "erro": str(e),
        }


class ServicoAnalise:
    """Responsável por orquestrar a análise: monta o prompt e chama a IA."""

    def __init__(self):
        """Inicializa o serviço de análise com o construtor de prompts."""
        self.prompt_builder = PromptBuilder()

    def analisar_confronto(self, dados_time_a, nome_time_a, dados_time_b, nome_time_b):
        """Realiza a análise de confronto entre dois times."""
        try:
            if not dados_time_a or not dados_time_b:
                return {
                    "analise_formatada": "<p>Erro: Dados estatísticos insuficientes para análise.</p>",
                    "success": False,
                    "erro": "Dados estatísticos insuficientes",
                }

            prompt = self.prompt_builder.criar_prompt_confronto(
                dados_time_a, nome_time_a,
                dados_time_b, nome_time_b,
            )

            resultado = gerar_conteudo(prompt)

            if not resultado["success"]:
                return {
                    "analise_formatada": resultado["texto"],
                    "success": False,
                    "erro": resultado.get("erro", "Erro desconhecido na geração de conteúdo"),
                }

            return {
                "analise_formatada": resultado["texto"],
                "success": True,
            }

        except Exception as e:
            current_app.logger.error(f"Erro ao analisar confronto: {str(e)}")
            return {
                "analise_formatada": f"<p>Erro ao processar análise: {str(e)}</p>",
                "success": False,
                "erro": str(e),
            }

    def analisar_time_unico(self, dados_time, nome_time):
        """Realiza a análise individual de um único time."""
        try:
            if not dados_time:
                return {
                    "analise_formatada": "<p>Erro: Dados estatísticos insuficientes para análise.</p>",
                    "success": False,
                    "erro": "Dados estatísticos insuficientes",
                }

            prompt = self.prompt_builder.criar_prompt_time_unico(dados_time, nome_time)

            resultado = gerar_conteudo(prompt)

            if not resultado["success"]:
                return {
                    "analise_formatada": resultado["texto"],
                    "success": False,
                    "erro": resultado.get("erro", "Erro desconhecido na geração de conteúdo"),
                }

            return {
                "analise_formatada": resultado["texto"],
                "success": True,
            }

        except Exception as e:
            current_app.logger.error(f"Erro ao analisar time único: {str(e)}")
            return {
                "analise_formatada": f"<p>Erro ao processar análise: {str(e)}</p>",
                "success": False,
                "erro": str(e),
            }


servico_analise = ServicoAnalise()
