import re
import asyncio
import uuid
import json
from message_analyzer import MessageAnalyzer
from link_validator import LinkValidator
from education_agent import EducationAgent
from web_search import WebSearcher
from utils import safe_print, save_analysis_result

class AgentManager:
    def __init__(self):
        self.message_analyzer = MessageAnalyzer()
        self.link_validator = LinkValidator()
        self.education_agent = EducationAgent()
        self.web_searcher = WebSearcher()
        self.analysis_history = {}  # Armazena histórico de análises
    
    async def process_user_query(self, query_data):
        try:
            message = query_data.get("message", "")
            user_id = query_data.get("user_id", "anonymous")
            device_info = query_data.get("device_info", {})
            
            analysis_id = str(uuid.uuid4())
            safe_print(f"[{analysis_id}] Iniciando análise para usuário {user_id}")

            # 1. Buscar informações gerais sobre golpes recentes
            safe_print(f"[{analysis_id}] Buscando informações sobre golpes recentes")
            recent_scams_search = asyncio.create_task(
                self.web_searcher.search_async("golpes financeiros recentes Brasil")
            )
            
            # 2. Analisar a mensagem
            safe_print(f"[{analysis_id}] Analisando mensagem")
            message_analysis_result = await self.message_analyzer.process({"message": message})
            safe_print(f"[{analysis_id}] Análise de mensagem concluída")

            # 3. Extrair e validar links
            links_found = re.findall(r'(https?://[^\s]+)', message)
            safe_print(f"[{analysis_id}] Encontrados {len(links_found)} links para validação")
            
            link_analysis_results = []
            if links_found:
                link_analysis_results = await asyncio.gather(
                    *(self.link_validator.process({"link": link}) for link in links_found)
                )
                safe_print(f"[{analysis_id}] Validação de links concluída")
            
            # 4. Esperar resultado da busca de golpes recentes
            recent_scams_info = await recent_scams_search
            safe_print(f"[{analysis_id}] Busca de golpes recentes concluída")
            
            # 5. Calcular pontuação de risco final
            # Pontuação da mensagem
            message_risk = message_analysis_result.get("risk_score", 0)
            
            # Pontuação máxima dos links
            link_risk = max((res.get("risk_score", 0) for res in link_analysis_results), default=0)
            
            # Combinar pontuações (priorizar a maior, mas considerar ambas)
            final_risk_score = max(message_risk, link_risk)
            if message_risk >= 3 and link_risk >= 3:
                # Adicionar bônus se ambos tiverem algum risco
                final_risk_score = min(final_risk_score + 1, 10)
            
            final_is_fraud = final_risk_score >= 5
            safe_print(f"[{analysis_id}] Pontuação final: {final_risk_score}/10 (Fraude: {final_is_fraud})")
            
            # 6. Obter conteúdo educativo se for fraude ou risco médio
            education_result = {
                "educational_text": "",
                "tips": []
            }
            
            if final_risk_score >= 3:  # Gerar conteúdo educativo para risco médio ou alto
                scam_type = "golpes financeiros"
                
                # Determinar tipo de golpe com base na análise
                if "pix" in message.lower():
                    scam_type += " com pix"
                elif "banco" in message.lower() or "cartão" in message.lower() or "motoboy" in message.lower():
                    scam_type += " bancários"
                elif "prêmio" in message.lower() or "sorteio" in message.lower():
                    scam_type += " de falsos prêmios"
                elif "familiar" in message.lower() or "filho" in message.lower() or "filha" in message.lower() or "urgente" in message.lower() or "dinheiro" in message.lower():
                    scam_type += " do falso familiar"
                
                try:
                    edu_result = await self.education_agent.process({"analysis_summary": scam_type})
                    
                    # Garantir que education_result seja um dicionário
                    if isinstance(edu_result, dict):
                        education_result = edu_result
                    elif isinstance(edu_result, str):
                        # Se por algum motivo retornou string, converter para dicionário
                        education_result = {
                            "educational_text": edu_result,
                            "tips": [
                                "Verifique a identidade do remetente por outros meios",
                                "Nunca compartilhe dados sensíveis",
                                "Em caso de dúvida, contate a instituição pelos canais oficiais"
                            ]
                        }
                    
                    safe_print(f"[{analysis_id}] Conteúdo educativo gerado")
                except Exception as e:
                    safe_print(f"Erro ao gerar conteúdo educativo: {e}")
                    # Fornecer conteúdo padrão em caso de erro
                    education_result = {
                        "educational_text": f"Tenha cuidado com {scam_type}. Sempre verifique a identidade de quem entra em contato com você.",
                        "tips": [
                            "Nunca compartilhe senhas ou códigos",
                            "Desconfie de solicitações urgentes",
                            "Entre em contato com a instituição pelos canais oficiais para confirmar"
                        ]
                    }
            
            # 7. Combinar links educativos de todas as fontes
            # Do analisador de mensagens
            education_links = message_analysis_result.get("education_links", [])
            
            # Da busca web recente
            for result in recent_scams_info[:2]:
                education_links.append({
                    "title": result.get("title", "Informação sobre golpes"),
                    "url": result.get("link", "https://www.gov.br/pt-br")
                })
            
            # Remover duplicatas
            unique_education_links = []
            seen_urls = set()
            for link in education_links:
                url = link.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_education_links.append(link)
            
            # Limitar a 5 links
            unique_education_links = unique_education_links[:5]
            
            # 8. Criar resposta final
            response = {
                "analysis_id": analysis_id,
                "is_fraud": final_is_fraud,
                "confidence": final_risk_score / 10.0,
                "explanation": message_analysis_result.get("explanation", ""),
                "recommendations": message_analysis_result.get("recommendations", []),
                "education_links": unique_education_links,
                "educational_text": education_result.get("educational_text", ""),
                "education_tips": education_result.get("tips", [])
            }
            
            # 9. Salvar resultado para referência futura
            self.analysis_history[analysis_id] = {
                "query": query_data,
                "result": response,
                "message_analysis": message_analysis_result,
                "link_analyses": link_analysis_results
            }
            
            save_analysis_result(response)
            safe_print(f"[{analysis_id}] Análise concluída e salva")
            
            return response

        except Exception as e:
            safe_print(f"Erro no AgentManager: {e}")
            return {
                "analysis_id": "erro",
                "is_fraud": False,
                "confidence": 0.0,
                "explanation": f"Erro ao processar a consulta: {e}",
                "recommendations": ["Tente novamente mais tarde."],
                "education_links": [],
                "educational_text": "Erro ao gerar conteúdo educativo.",
                "education_tips": []
            }