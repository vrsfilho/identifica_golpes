import re
import json
import asyncio
from google.generativeai import GenerativeModel
from utils import safe_print
from web_search import WebSearcher

class MessageAnalyzer:
    def __init__(self, model_name="gemini-2.0-flash"):  # Modelo atualizado
        self.model = GenerativeModel(model_name)
        self.web_searcher = WebSearcher()

    async def process(self, input_data):
        try:
            message = input_data.get("message", "")
            if not message:
                return {
                    "analysis": "Nenhuma mensagem fornecida para análise.",
                    "risk_score": 0,
                    "explanation": "Por favor, forneça uma mensagem para verificar.",
                    "recommendations": [],
                    "education_links": []
                }

            # Extrair palavras-chave para busca
            try:
                keywords = await self._extract_keywords(message)
                safe_print("Palavras-chave extraídas: %s", keywords)
            except Exception as e:
                safe_print("Erro ao extrair palavras-chave: %s", e)
                keywords = []
            
            # Iniciar busca na web se temos palavras-chave
            search_task = None
            if keywords:
                search_query = " ".join(keywords[:3]) + " golpe fraude"
                search_task = asyncio.create_task(
                    self.web_searcher.search_async(search_query)
                )
            
            # Analisar a mensagem com a IA
            prompt = f"""
            Você é um agente especializado em detectar golpes financeiros em mensagens de texto.
            Analise a seguinte mensagem e determine se ela apresenta características
            de golpes financeiros, focando em golpes comuns como coleta de cartões pelo banco,
            falsos prêmios, ou solicitações urgentes de dados.

            Mensagem a ser analisada:
            "{message}"

            Verifique os seguintes elementos e dê exemplos específicos da mensagem:
            1. **Urgência indevida ou pressão para ação imediata:** A mensagem exige uma resposta rápida ou ameaça consequências?
            2. **Solicitação de dados sensíveis:** Pede informações como número de cartão, senha, código de segurança (CVV), dados bancários, CPF, etc.? Bancos legítimos raramente pedem isso por mensagem.
            3. **Erros gramaticais ou ortográficos:** A mensagem contém erros que não seriam esperados de uma comunicação oficial?
            4. **Links suspeitos ou encurtados:** Contém links que parecem estranhos, não oficiais, ou usam encurtadores?
            5. **Remetente suspeito ou não verificável:** O número ou nome do remetente parece oficial? É possível verificar a identidade?
            6. **Ofertas irrealistas ou muito vantajosas:** Promete prêmios, descontos enormes, ou dinheiro fácil sem motivo claro?
            7. **Tom da mensagem:** É excessivamente informal, ameaçador, ou tenta criar pânico?

            Com base na sua análise, forneça:
            - Uma **análise detalhada** dos elementos suspeitos encontrados, citando trechos da mensagem se aplicável.
            - Uma **pontuação de risco** de 0 a 10 (0. Sem risco aparente, 10. Risco altíssimo de golpe). Inclua apenas o número.
            - Uma **explicação clara e simples** para um usuário leigo sobre por que a mensagem é ou não suspeita.
            - **Recomendações específicas** sobre o que o usuário deve fazer (ex: não clicar em links, não responder, não fornecer dados, entrar em contato direto com a instituição pelo canal oficial). 

            Formato da resposta:
            ANÁLISE DETALHADA: ...
            PONTUAÇÃO DE RISCO: [0-10]
            EXPLICAÇÃO PARA O USUÁRIO: ...
            RECOMENDAÇÕES:
            - Recomendação 1
            - Recomendação 2
            """

            try:
                response = await self.model.generate_content_async(prompt)
                response_text = response.text
            except Exception as e:
                safe_print(f"Erro na geração de conteúdo: {e}")
                # Fornecer análise padrão baseada em heurísticas simples
                risk_score = self._heuristic_analysis(message)
                return {
                    "analysis": f"Não foi possível analisar completamente a mensagem devido a um erro: {e}",
                    "risk_score": risk_score,
                    "explanation": "Esta mensagem contém elementos que podem indicar um golpe, como solicitação urgente ou menção a cartões/dados bancários.",
                    "recommendations": [
                        "Nunca forneça dados bancários por mensagem ou telefone",
                        "Contate diretamente sua instituição bancária pelos canais oficiais para verificar",
                        "Não clique em links recebidos por mensagem"
                    ],
                    "education_links": []
                }
            
            # Processar o texto de resposta
            analysis_detail = "Detalhes da análise não disponíveis."
            risk_score = 0
            explanation = ""
            recommendations = ["Recomendação não disponível."]
            
            # Esperar por resultados da busca na web
            search_results = []
            if search_task:
                try:
                    search_results = await search_task
                except Exception as e:
                    safe_print(f"Erro na busca web: {e}")
            
            # Extrair seções da resposta
            sections = re.split(r'(ANÁLISE DETALHADA:|PONTUAÇÃO DE RISCO:|EXPLICAÇÃO PARA O USUÁRIO:|RECOMENDAÇÕES:)', response_text)
            section_map = {}
            current_section = None
            for item in sections:
                if item.strip() in ['ANÁLISE DETALHADA:', 'PONTUAÇÃO DE RISCO:', 'EXPLICAÇÃO PARA O USUÁRIO:', 'RECOMENDAÇÕES:']:
                    current_section = item.strip()
                    section_map[current_section] = ""
                elif current_section is not None:
                    section_map[current_section] += item

            analysis_detail = section_map.get('ANÁLISE DETALHADA:', analysis_detail).strip()
            score_text = section_map.get('PONTUAÇÃO DE RISCO:', '0').strip()
            try:
                score_match = re.search(r'\d+', score_text)
                risk_score = int(score_match.group(0)) if score_match else 0
                risk_score = max(0, min(10, risk_score))
            except (ValueError, AttributeError):
                # Se não conseguir extrair a pontuação, usar análise heurística
                risk_score = self._heuristic_analysis(message)

            explanation = section_map.get('EXPLICAÇÃO PARA O USUÁRIO:', "").strip()
            if not explanation:
                # Gerar explicação baseada na pontuação
                if risk_score >= 7:
                    explanation = "Esta mensagem apresenta fortes indícios de ser um golpe. Tenha muito cuidado."
                elif risk_score >= 4:
                    explanation = "Esta mensagem contém elementos suspeitos que podem indicar uma tentativa de golpe."
                else:
                    explanation = "Esta mensagem não apresenta sinais claros de golpe, mas sempre mantenha atenção."
                
            rec_text = section_map.get('RECOMENDAÇÕES:', '').strip()
            recommendations = [item.strip('- ').strip() for item in rec_text.split('\n') if item.strip().startswith('- ')]
            if not recommendations and rec_text:
                recommendations = [rec_text]
            
            # Se ainda não tivermos recomendações, criar algumas genéricas
            if not recommendations or recommendations == ["Recomendação não disponível."]:
                if risk_score >= 7:
                    recommendations = [
                        "Não responda à mensagem",
                        "Não compartilhe dados pessoais ou bancários",
                        "Bloqueie o remetente",
                        "Reporte a tentativa de golpe às autoridades"
                    ]
                elif risk_score >= 4:
                    recommendations = [
                        "Verifique a autenticidade da solicitação por canais oficiais",
                        "Não compartilhe dados sensíveis",
                        "Entre em contato diretamente com a instituição mencionada"
                    ]
                else:
                    recommendations = [
                        "Mantenha-se vigilante com comunicações não solicitadas",
                        "Verifique sempre a identidade do remetente"
                    ]
            
            # Criar links educativos usando resultados da busca
            education_links = []
            for result in search_results[:3]:
                education_links.append({
                    "title": result.get("title", "Informação sobre golpes"),
                    "url": result.get("link", "https://www.gov.br/pt-br")
                })
            
            # Adicionar links padrão se não tiver resultados
            if not education_links:
                education_links = [
                    {
                        "title": "Febraban - Cartilha de Segurança",
                        "url": "https://portal.febraban.org.br/pagina/3055/33/pt-br/cartilha"
                    },
                    {
                        "title": "Banco Central - Golpes Financeiros",
                        "url": "https://www.bcb.gov.br/estabilidadefinanceira/golpesefinanciamentos"
                    }
                ]

            return {
                "analysis": analysis_detail,
                "risk_score": risk_score,
                "explanation": explanation,
                "recommendations": recommendations,
                "education_links": education_links,
                "web_search_results": search_results[:3] if search_results else []
            }

        except Exception as e:
            safe_print("Erro no MessageAnalyzer: %s", e)
            return {
                "analysis": f"Erro ao analisar a mensagem: {e}",
                "risk_score": 0,
                "explanation": "Houve um erro durante a análise.",
                "recommendations": [],
                "education_links": []
            }
    
    def _heuristic_analysis(self, message):
        """Análise heurística simples baseada em palavras-chave e padrões."""
        message_lower = message.lower()
        
        # Pontuação inicial
        score = 0
        
        # Sinais de urgência
        urgency_words = ["urgente", "imediato", "agora", "rápido", "emergência", "imediatamente"]
        for word in urgency_words:
            if word in message_lower:
                score += 2
                break
        
        # Menções a bancos/cartões
        bank_words = ["banco", "cartão", "senha", "pix", "transferência", "código", "atualização", "cadastro"]
        for word in bank_words:
            if word in message_lower:
                score += 1
        
        # Menções a dinheiro
        money_words = ["dinheiro", "reais", "r$", "pagamento", "transferir", "depósito"]
        for word in money_words:
            if word in message_lower:
                score += 1
        
        # Golpe do familiar
        family_words = ["filho", "filha", "mãe", "pai", "número novo", "mudei de número", "celular novo"]
        for word in family_words:
            if word in message_lower:
                score += 3
                break
        
        # Golpe do motoboy
        if "motoboy" in message_lower and ("cartão" in message_lower or "buscar" in message_lower):
            score += 4
        
        # Golpe de prêmios
        prize_words = ["prêmio", "sorteio", "ganhou", "contemplado", "promoção"]
        for word in prize_words:
            if word in message_lower:
                score += 3
                break
        
        return min(score, 10)  # Limitar a 10
    
    async def _extract_keywords(self, text):
        """Extrai palavras-chave relevantes para pesquisa."""
        try:
            # Usar o modelo para extrair palavras-chave
            prompt = f"""
            Extraia as 3-5 palavras-chave mais relevantes para identificar possíveis golpes no seguinte texto:
            
            "{text}"
            
            Formate sua resposta apenas como uma lista JSON de palavras-chave, sem comentários adicionais.
            Exemplo: ["banco", "atualização", "urgente"]
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Tentar extrair JSON da resposta
            json_pattern = re.search(r'$$.*$$', response_text)
            if json_pattern:
                try:
                    keywords = json.loads(json_pattern.group(0))
                    return keywords
                except json.JSONDecodeError:
                    pass
            
            # Fallback: extrair palavras mais comuns
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            # Filtrar palavras comuns que não são úteis
            stopwords = ["para", "como", "esse", "esta", "isso", "aqui", "voce", "você", "esta", "está", "muito"]
            filtered_words = [w for w in words if w not in stopwords]
            # Contar frequência
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Obter as 5 palavras mais frequentes
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, _ in sorted_words[:5]]
            
        except Exception as e:
            safe_print(f"Erro ao extrair palavras-chave: {e}")
            return []