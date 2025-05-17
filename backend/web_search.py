import os
import json
import aiohttp
import asyncio
from utils import safe_print

class WebSearcher:
    def __init__(self):
        # API key para SerpAPI
        self.api_key = os.getenv("SERPAPI_API_KEY", "")
        # Cache de resultados para evitar duplicação de buscas
        self.search_cache = {}
        # Base URL para a SerpAPI
        self.base_url = "https://serpapi.com/search"
    
    async def search_async(self, query, num_results=5):
        """Realiza busca na web de forma assíncrona."""
        # Verificar cache
        cache_key = f"{query}_{num_results}"
        if cache_key in self.search_cache:
            safe_print(f"Usando resultados em cache para: {query}")
            return self.search_cache[cache_key]
        
        # Se não tiver API key, retorna erro
        if not self.api_key:
            safe_print("API key da SerpAPI não configurada. Usando modo fallback.")
            return self._fallback_search(query)
        
        try:
            params = {
                "api_key": self.api_key,
                "q": query,
                "num": num_results,
                "engine": "google"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extrair resultados relevantes
                        results = []
                        
                        if "organic_results" in data:
                            for result in data["organic_results"][:num_results]:
                                results.append({
                                    "title": result.get("title", ""),
                                    "link": result.get("link", ""),
                                    "snippet": result.get("snippet", "")
                                })
                        
                        # Armazenar no cache
                        self.search_cache[cache_key] = results
                        return results
                    else:
                        safe_print(f"Erro na busca: {response.status}")
                        return self._fallback_search(query)
        
        except Exception as e:
            safe_print(f"Erro ao buscar na web: {e}")
            return self._fallback_search(query)
    
    def _fallback_search(self, query):
        """Método de fallback para quando a API falha."""
        safe_print(f"Usando fallback para busca: {query}")
        
        # Resultados diferentes baseados no tipo de consulta
        if "motoboy" in query.lower():
            return [{
                "title": "Golpe do Motoboy: Fique alerta! - Febraban",
                "link": "https://portal.febraban.org.br/noticia/3412/pt-br/",
                "snippet": "No golpe do motoboy, criminosos ligam se passando pelo banco, dizem que o cartão foi clonado e enviam um portador para retirá-lo."
            },
            {
                "title": "Golpe do Motoboy: Como funciona e como se proteger - gov.br",
                "link": "https://www.gov.br/economia/pt-br/assuntos/noticias/2023/golpes-financeiros",
                "snippet": "Nunca entregue seu cartão bancário para nenhum portador ou motoboy. Bancos não recolhem cartões em domicílio."
            }]
        elif "familiar" in query.lower() or "filho" in query.lower() or "filha" in query.lower():
            return [{
                "title": "Golpe do Falso Familiar: Como identificar e evitar - Procon",
                "link": "https://www.procon.sp.gov.br/golpe-do-falso-familiar/",
                "snippet": "Criminosos se passam por familiares em mensagens alegando troca de número e pedindo dinheiro com urgência."
            },
            {
                "title": "Golpe do WhatsApp: O que fazer se alguém se passar por você - G1",
                "link": "https://g1.globo.com/economia/tecnologia/noticia/2023/08/golpe-do-whatsapp-o-que-fazer.ghtml",
                "snippet": "Sempre confirme por ligação telefônica a identidade de familiares pedindo dinheiro. O golpe do 'filho que trocou de número' é muito comum."
            }]
        else:
            return [{
                "title": "Informações sobre golpes financeiros - gov.br",
                "link": "https://www.gov.br/consumidor/pt-br/assuntos/saiba-como-se-proteger/golpes-financeiros",
                "snippet": "Aprenda a identificar golpes financeiros e como se proteger."
            },
            {
                "title": "Febraban - Cuidado com golpes",
                "link": "https://portal.febraban.org.br/pagina/3453/1285/pt-br/seguranca-cuidado-com-golpes",
                "snippet": "Bancos nunca pedem seus dados por email, SMS ou ligação telefônica."
            },
            {
                "title": "Golpes financeiros comuns: como se proteger - Banco Central",
                "link": "https://www.bcb.gov.br/estabilidadefinanceira/golpesefinanciamentos",
                "snippet": "Conheça os golpes mais comuns e saiba como se proteger de fraudes financeiras."
            },
            {
                "title": "Dicas para evitar cair em golpes online - CERT.br",
                "link": "https://cartilha.cert.br/golpes/",
                "snippet": "Informações sobre como identificar e evitar diversos tipos de golpes virtuais."
            },
            {
                "title": "Denuncie golpes financeiros - Polícia Civil",
                "link": "https://www.policiacivil.gov.br/denuncie",
                "snippet": "Denuncie tentativas de golpes financeiros às autoridades policiais."
            }]
    
    async def search_scam_reports(self, keyword, domain=None):
        """Busca por relatos de golpes relacionados à palavra-chave ou domínio."""
        query = f"golpe fraude {keyword}"
        if domain:
            query += f" site:{domain}"
        return await self.search_async(query, num_results=5)