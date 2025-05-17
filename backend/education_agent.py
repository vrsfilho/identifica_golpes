import re
import asyncio
from google.generativeai import GenerativeModel
from utils import safe_print
from web_search import WebSearcher

class EducationAgent:
    def __init__(self, model_name="gemini-2.0-flash"):  # Modelo atualizado
        self.model = GenerativeModel(model_name)
        self.web_searcher = WebSearcher()
        self.content_cache = {}  # Cache para conteúdo educativo
    
    async def process(self, input_data):
        try:
            analysis_summary = input_data.get("analysis_summary", "golpes financeiros online")
            
            # Verificar cache
            if analysis_summary in self.content_cache:
                safe_print(f"Usando conteúdo educativo em cache para: {analysis_summary}")
                return self.content_cache[analysis_summary]
            
            # Buscar informações atualizadas na web
            search_task = asyncio.create_task(
                self.web_searcher.search_async(f"como se proteger de {analysis_summary} dicas")
            )
            
            # Enquanto a busca ocorre, começar a gerar o conteúdo base
            base_prompt = f"""
            Você é um agente educacional focado em segurança digital para usuários leigos. 
            Crie um texto educativo sobre {analysis_summary}.
            
            O texto deve:
            1. Ser claro e acessível para o público geral
            2. Explicar de forma simples como funciona este tipo de golpe
            3. Destacar os sinais de alerta mais comuns
            4. Ser conciso, com no máximo 250 palavras
            
            Também liste 5 dicas práticas para se proteger deste tipo de golpe.
            
            Formato da resposta:
            TEXTO EDUCATIVO: [seu texto aqui]
            
            DICAS DE SEGURANÇA:
            - Dica 1
            - Dica 2
            - Dica 3
            - Dica 4
            - Dica 5
            """
            
            base_response_task = asyncio.create_task(self.model.generate_content_async(base_prompt))
            
            # Esperar pelos resultados das buscas
            search_results = []
            try:
                search_results = await asyncio.wait_for(search_task, timeout=5.0)
                safe_print(f"Obtidos {len(search_results)} resultados de busca para conteúdo educativo")
            except asyncio.TimeoutError:
                safe_print("Timeout na busca de informações educativas")
            except Exception as e:
                safe_print(f"Erro na busca de informações: {e}")
            
            # Preparar contexto de busca para enriquecer o conteúdo
            search_context = ""
            if search_results:
                search_context = "Informações atualizadas encontradas:\n\n"
                for idx, result in enumerate(search_results[:3], 1):
                    search_context += f"{idx}. {result.get('title', '')}\n"
                    search_context += f"   {result.get('snippet', '')}\n\n"
            
            # Esperar pela resposta base
            base_text = ""
            try:
                base_response = await asyncio.wait_for(base_response_task, timeout=10.0)
                base_text = base_response.text
            except asyncio.TimeoutError:
                safe_print("Timeout na geração de conteúdo educativo base")
            except Exception as e:
                safe_print(f"Erro na geração de conteúdo base: {e}")
                # Em caso de erro, fornecer texto padrão
                base_text = f"""
                TEXTO EDUCATIVO: Cuidado com {analysis_summary}! Este tipo de golpe é comum e pode causar prejuízos financeiros. Os golpistas usam técnicas de engenharia social para enganar as vítimas.
                
                DICAS DE SEGURANÇA:
                - Sempre verifique a identidade de quem entra em contato
                - Nunca compartilhe senhas ou dados bancários
                - Desconfie de ofertas muito vantajosas
                - Em caso de dúvida, entre em contato pelo telefone oficial
                - Mantenha-se informado sobre golpes recentes
                """
            
            # Se temos resultados de busca e base_text, enriquecer o conteúdo
            final_text = base_text
            if search_results and base_text:
                try:
                    enrichment_prompt = f"""
                    Analise o seguinte texto educativo sobre {analysis_summary}:
                    
                    {base_text}
                    
                    Agora, melhore e atualize este conteúdo com base nestas informações recentes:
                    
                    {search_context}
                    
                    Mantenha o formato original, mas adicione informações relevantes e atualizadas.
                    O texto final não deve ultrapassar 300 palavras.
                    
                    Formato da resposta:
                    TEXTO EDUCATIVO: [seu texto melhorado aqui]
                    
                    DICAS DE SEGURANÇA:
                    - Dica 1 (atualizada se necessário)
                    - Dica 2
                    - Dica 3
                    - Dica 4
                    - Dica 5
                    """
                    
                    enriched_response = await self.model.generate_content_async(enrichment_prompt)
                    if enriched_response.text and len(enriched_response.text) > 50:
                        final_text = enriched_response.text
                except Exception as e:
                    safe_print(f"Erro ao enriquecer conteúdo: {e}")
                    # Continuar com o texto base em caso de erro
            
            # Processamento do texto
            educational_text = "Conteúdo educativo não disponível."
            tips = []

            sections = re.split(r'(TEXTO EDUCATIVO:|DICAS DE SEGURANÇA:)', final_text)
            section_map = {}
            current_section = None
            for item in sections:
                if item.strip() in ['TEXTO EDUCATIVO:', 'DICAS DE SEGURANÇA:']:
                    current_section = item.strip()
                    section_map[current_section] = ""
                elif current_section is not None:
                    section_map[current_section] += item

            educational_text = section_map.get('TEXTO EDUCATIVO:', educational_text).strip()
            tips_text = section_map.get('DICAS DE SEGURANÇA:', '').strip()
            tips = [item.strip('- ').strip() for item in tips_text.split('\n') if item.strip().startswith('- ')]
            if not tips and tips_text:
                tips = [tips_text]
            
            # Se ainda não tivermos dicas, criar algumas genéricas
            if not tips:
                tips = [
                    "Sempre verifique a identidade de quem entra em contato",
                    "Nunca compartilhe senhas, códigos ou dados bancários",
                    "Desconfie de pedidos urgentes de dinheiro ou informações",
                    "Em caso de dúvida, entre em contato diretamente com a instituição pelos canais oficiais",
                    "Mantenha-se informado sobre golpes recentes"
                ]
            
            # Garantir que não temos uma string vazia como texto educativo
            if not educational_text or educational_text == "Conteúdo educativo não disponível.":
                educational_text = f"Tenha cuidado com {analysis_summary}. Estes golpes são comuns e podem causar prejuízos. Sempre verifique a identidade de quem solicita informações ou dinheiro."
            
            # Armazenar no cache
            result = {
                "educational_text": educational_text,
                "tips": tips,
            }
            self.content_cache[analysis_summary] = result
            
            return result

        except Exception as e:
            safe_print("Erro no EducationAgent: %s", e)
            # Garantir que sempre retornamos um dicionário, mesmo em caso de erro
            return {
                "educational_text": f"Cuidado com {input_data.get('analysis_summary', 'golpes')}! Sempre verifique a identidade de quem solicita informações ou dinheiro.",
                "tips": [
                    "Mantenha-se informado sobre golpes atuais", 
                    "Desconfie de ofertas muito vantajosas", 
                    "Nunca forneça dados sensíveis em links recebidos por mensagem",
                    "Verifique a identidade do remetente por outros meios",
                    "Reporte tentativas de golpe às autoridades"
                ],
            }