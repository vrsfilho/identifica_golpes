import os
import re
import aiohttp
import asyncio
from utils import safe_print, normalize_url, extract_domain
from web_search import WebSearcher
from config import get_api_key, get_blacklists

class LinkValidator:
    def __init__(self):
        self.api_key = get_api_key("virustotal")
        self.blacklists = get_blacklists()
        self.web_searcher = WebSearcher()
        self.check_cache = {}  # Cache para evitar verificações duplicadas
    
    async def process(self, input_data):
        try:
            link = input_data.get("link", "")
            if not link:
                return {
                    "analysis": "Nenhum link fornecido para análise.",
                    "risk_score": 0,
                    "recommendations": [],
                }
            
            # Normaliza o link
            domain = extract_domain(link)
            if not domain:
                return {
                    "analysis": "Não foi possível extrair o domínio do link.",
                    "risk_score": 3,
                    "is_fraud": False,
                    "recommendations": ["Verifique se o formato do link está correto."]
                }
            
            # Verificar se é um link encurtado
            shortened_domains = ["bit.ly", "goo.gl", "tinyurl.com", "t.co", "is.gd", "buff.ly", 
                               "ow.ly", "rebrand.ly", "cutt.ly", "shorturl.at", "tiny.one"]
            is_shortened = any(sd in domain for sd in shortened_domains)
            
            # Análise inicial
            explanations = []
            recommendations = []
            risk_score = 0
            
            # Verifica encurtadores
            if is_shortened:
                explanations.append("Este link usa um encurtador, o que pode esconder um destino malicioso.")
                recommendations.append("Evite clicar em links encurtados recebidos de fontes desconhecidas.")
                recommendations.append("Use um serviço para expandir links encurtados antes de clicar.")
                risk_score += 4
            
            # Verificar na blacklist
            in_blacklist = False
            blacklist_type = ""
            
            for bl_type, domains in self.blacklists.items():
                if domain in domains:
                    in_blacklist = True
                    blacklist_type = bl_type
                    break
            
            if in_blacklist:
                explanations.append(f"Este site está em nossa lista de {blacklist_type}.")
                recommendations.append("Não acesse este site sob nenhuma circunstância.")
                risk_score += 6
            
            # Verificação no VirusTotal, se disponível API
            vt_result = {}
            if self.api_key and not in_blacklist:
                vt_result = await self._check_virustotal(link)
                if vt_result.get("malicious", 0) > 0:
                    explanations.append(f"Este link foi marcado como malicioso por {vt_result.get('malicious')} serviços de segurança.")
                    risk_score += min(vt_result.get("malicious", 0), 5)  # Máximo de 5 pontos
            
            # Pesquisa web para verificar se há relatos sobre este domínio
            if not in_blacklist and risk_score < 7:
                scam_reports = await self.web_searcher.search_scam_reports(domain)
                if len(scam_reports) > 2:  # Se encontrar mais de 2 relatórios
                    explanations.append("Encontramos relatórios online que podem indicar que este site está envolvido em golpes.")
                    risk_score += 2
            
            # Análise de características da URL
            url_analysis = self._analyze_url_characteristics(link)
            if url_analysis["suspicious"]:
                explanations.append(url_analysis["explanation"])
                risk_score += url_analysis["score"]
                recommendations.extend(url_analysis["recommendations"])
            
            # Finaliza a análise
            if not explanations:
                explanations.append("Não foram encontrados sinais claros de que este link seja malicioso.")
                
            if not recommendations:
                recommendations = [
                    "Sempre verifique a URL completa antes de clicar.",
                    "Tenha certeza da fonte do link antes de fornecer informações pessoais.",
                    "Use um antivírus atualizado que inclua proteção de navegação."
                ]
            
            # Limita o score a 10
            risk_score = min(risk_score, 10)
            
            # Classificação final
            is_fraud = risk_score >= 5
            
            return {
                "analysis": " ".join(explanations),
                "risk_score": risk_score,
                "is_fraud": is_fraud,
                "recommendations": recommendations,
                "technical_details": vt_result
            }

        except Exception as e:
            safe_print("Erro no LinkValidator: %s", e)
            return {
                "analysis": f"Erro ao analisar o link: {e}",
                "risk_score": 0,
                "recommendations": ["Erro durante a análise de link."]
            }
    
    async def _check_virustotal(self, url):
        """Verifica o URL no VirusTotal."""
        try:
            # Verificar cache
            cache_key = normalize_url(url)
            if cache_key in self.check_cache:
                return self.check_cache[cache_key]
            
            # API do VirusTotal
            vt_api_url = "https://www.virustotal.com/api/v3/urls"
            
            # Primeiro, enviar URL para análise
            headers = {
                "x-apikey": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with aiohttp.ClientSession() as session:
                # Submeter URL para análise
                async with session.post(vt_api_url, headers=headers, data={"url": url}) as response:
                    if response.status != 200:
                        return {"error": "Erro ao enviar URL para análise"}
                    
                    data = await response.json()
                    analysis_id = data.get("data", {}).get("id", "")
                    
                    if not analysis_id:
                        return {"error": "ID de análise não encontrado"}
                    
                    # Esperar alguns segundos para a análise ser concluída
                    await asyncio.sleep(2)
                    
                    # Obter resultados
                    result_url = f"{vt_api_url}/{analysis_id}"
                    async with session.get(result_url, headers=headers) as result_response:
                        if result_response.status != 200:
                            return {"error": "Erro ao obter resultados da análise"}
                        
                        result_data = await result_response.json()
                        
                        # Processar resultados
                        attributes = result_data.get("data", {}).get("attributes", {})
                        stats = attributes.get("stats", {})
                        
                        result = {
                            "malicious": stats.get("malicious", 0),
                            "suspicious": stats.get("suspicious", 0),
                            "harmless": stats.get("harmless", 0),
                            "undetected": stats.get("undetected", 0)
                        }
                        
                        # Armazenar no cache
                        self.check_cache[cache_key] = result
                        return result
        
        except Exception as e:
            safe_print(f"Erro ao verificar URL no VirusTotal: {e}")
            return {"error": str(e)}
    
    def _analyze_url_characteristics(self, url):
        """Analisa características da URL que podem indicar phishing."""
        result = {
            "suspicious": False,
            "explanation": "",
            "score": 0,
            "recommendations": []
        }
        
        # Verifica se a URL contém números em excesso ou caracteres estranhos
        num_count = len(re.findall(r'\d', url))
        if num_count > 10:
            result["suspicious"] = True
            result["explanation"] += "A URL contém muitos números, o que é incomum para sites legítimos. "
            result["score"] += 2
        
        # Verifica presença de palavras de instituições financeiras combinadas com domínios suspeitos
        financial_terms = ["banco", "bank", "caixa", "santander", "bradesco", "itau", "nubank", "inter"]
        domain = extract_domain(url).lower()
        
        for term in financial_terms:
            if term in url.lower() and term not in domain:
                result["suspicious"] = True
                result["explanation"] += f"A URL contém a palavra '{term}', mas não está no domínio oficial. Pode ser uma tentativa de phishing. "
                result["score"] += 4
                result["recommendations"].append("Bancos legítimos usam apenas seus domínios oficiais. Acesse o site digitando o endereço diretamente no navegador.")
                break
        
        # Verifica se o domínio parece uma imitação de domínio legítimo
        common_domains = {
            "google": "google.com",
            "facebook": "facebook.com",
            "whatsapp": "whatsapp.com",
            "instagram": "instagram.com",
            "microsoft": "microsoft.com",
            "apple": "apple.com"
        }
        
        for brand, official_domain in common_domains.items():
            if brand in domain and official_domain not in domain:
                result["suspicious"] = True
                result["explanation"] += f"Esta URL parece imitar o site da {brand}, mas não é o domínio oficial ({official_domain}). "
                result["score"] += 3
                result["recommendations"].append(f"O site oficial da {brand} é {official_domain}. Acesse apenas este domínio.")
        
        # Verifica se a URL tem muitos subdomínios (possível técnica de confusão)
        subdomain_count = domain.count(".")
        if subdomain_count > 2:
            result["suspicious"] = True
            result["explanation"] += "Esta URL tem uma estrutura de subdomínios complexa, o que pode ser uma tentativa de confundir o usuário. "
            result["score"] += 2
        
        return result