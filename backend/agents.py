import os
import asyncio
import uuid
import re
import json
from datetime import date
from google.generativeai import configure, GenerativeModel, types

# --- Configuração da API Key ---
# É ALTAMENTE recomendado usar variáveis de ambiente para chaves sensíveis.
# Crie um arquivo .env na pasta backend com GOOGLE_API_KEY='sua_chave_aqui'
# e descomente as linhas abaixo:
# from dotenv import load_dotenv
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if not GOOGLE_API_KEY:
#     raise ValueError("Variável de ambiente GOOGLE_API_KEY não configurada.")
# configure(api_key=GOOGLE_API_KEY)

# Para este exemplo, vamos configurar diretamente (NÃO FAÇA ISSO EM PRODUÇÃO)
# Substitua 'YOUR_GOOGLE_API_KEY' pela sua chave real
configure(api_key="AIzaSyC4BQMgBMsXPaSt2PwDBQCqJFMfCtCzOok")

# Função segura para imprimir mensagens
def safe_print(message, *args):
    """
    Função segura para imprimir mensagens, evitando problemas com o operador % em strings.
    """
    try:
        if args:
            print(message % args)
        else:
            print(message)
    except Exception as e:
        print(f"Erro ao imprimir mensagem: {e}")
        print(f"Mensagem original: {message}")
        if args:
            print(f"Argumentos: {args}")

# --- Base para os Agentes ---
class BaseAgent:
    def __init__(self, name: str, description: str, model_name: str = "gemini-pro"):
        self.name = name
        self.description = description
        self.model = GenerativeModel(model_name)

    async def process(self, input_data: dict) -> dict:
        """
        Método assíncrono para processar a entrada e retornar um resultado.
        Deve ser implementado pelas classes filhas.
        """
        raise NotImplementedError("O método process deve ser implementado pela subclasse.")

# --- Agente de Análise de Mensagens ---
class MessageAnalyzer(BaseAgent):
    def __init__(self):
        super().__init__(
            "MessageAnalyzer",
            "Analisa mensagens para detectar padrões de golpes financeiros"
        )

    async def process(self, input_data: dict) -> dict:
        """
        Analisa a mensagem do usuário para identificar características de golpe.
        input_data deve conter 'message' (str).
        """
        message = input_data.get("message", "")
        if not message:
            return {
                "analysis": "Nenhuma mensagem fornecida para análise.",
                "risk_score": 0,
                "explanation": "Por favor, forneça uma mensagem para verificar.",
                "recommendations": [],
                "education_links": []
            }

        # Prompt detalhado para o modelo Gemini
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
        - **Recomendações específicas** sobre o que o usuário deve fazer (ex: não clicar em links, não responder, não fornecer dados, entrar em contato direto com a instituição pelo canal oficial). Liste cada recomendação em uma nova linha começando com '- '.
        - **education_links**: Uma lista vazia [] ou uma string JSON representando uma lista de objetos, onde cada objeto tem "title" (str) e "url" (str), para artigos confiáveis sobre como identificar golpes comuns. Ex: `[{"title": "Como identificar phishing", "url": "http://exemplo.com/phishing"}]`

        Formato da resposta (siga este formato para facilitar a extração):
        ANÁLISE DETALHADA: ...
        PONTUAÇÃO DE RISCO: [0-10]
        EXPLICAÇÃO PARA O USUÁRIO: ...
        RECOMENDAÇÕES:
        - Recomendação 1
        - Recomendação 2
        EDUCATION_LINKS: [...]
        """

        try:
            # Usar generate_content_async para chamadas assíncronas
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            safe_print("Resposta bruta do MessageAnalyzer:\n%s\n---", response_text) # Log para debug

            # --- Processar a resposta do modelo ---
            # Esta parte é crucial e pode precisar de refinamento.
            # O modelo retorna texto livre, você precisa extrair os dados estruturados.
            # Pode usar regex, parsing simples ou até outro modelo para extrair.
            # Exemplo simplificado de extração baseado nos cabeçalhos definidos no prompt:

            analysis_detail = "Não foi possível extrair a análise detalhada."
            risk_score = 0
            explanation = "Não foi possível extrair a explicação."
            recommendations = ["Não foi possível extrair recomendações."]
            education_links = []

            # Dividir a resposta em seções usando os cabeçalhos
            sections = re.split(r'(ANÁLISE DETALHADA:|PONTUAÇÃO DE RISCO:|EXPLICAÇÃO PARA O USUÁRIO:|RECOMENDAÇÕES:|EDUCATION_LINKS:)', response_text)

            # Mapear seções
            section_map = {}
            current_section = None
            for item in sections:
                if item.strip() in ['ANÁLISE DETALHADA:', 'PONTUAÇÃO DE RISCO:', 'EXPLICAÇÃO PARA O USUÁRIO:', 'RECOMENDAÇÕES:', 'EDUCATION_LINKS:']:
                    current_section = item.strip()
                    section_map[current_section] = ""
                elif current_section is not None:
                    section_map[current_section] += item

            # Extrair conteúdo de cada seção
            analysis_detail = section_map.get('ANÁLISE DETALHADA:', analysis_detail).strip()

            score_text = section_map.get('PONTUAÇÃO DE RISCO:', '0').strip()
            try:
                # Encontrar o primeiro número na string
                score_match = re.search(r'\d+', score_text)
                risk_score = int(score_match.group(0)) if score_match else 0
                risk_score = max(0, min(10, risk_score)) # Garantir que está entre 0 e 10
            except (ValueError, AttributeError):
                risk_score = 0 # Default em caso de erro na extração

            explanation = section_map.get('EXPLICAÇÃO PARA O USUÁRIO:', explanation).strip()

            rec_text = section_map.get('RECOMENDAÇÕES:', '').strip()
            # Extrair itens de lista que começam com '-'
            recommendations = [item.strip('- ').strip() for item in rec_text.split('\n') if item.strip().startswith('- ')]
            if not recommendations and rec_text: # Se não encontrou lista, mas tem texto, pega tudo como uma única recomendação
                 recommendations = [rec_text]
            if not recommendations: # Se ainda vazio, usa default
                 recommendations = ["Não foi possível extrair recomendações."]

            # Simplificar completamente o processamento de links educacionais
            education_links = [
                {
                    "title": "Como identificar golpes financeiros",
                    "url": "https://www.gov.br/mj/pt-br/assuntos/suas-protecoes/consumidor/saiba-como-se-proteger/golpes-financeiros"
                },
                {
                    "title": "Dicas de segurança digital",
                    "url": "https://www.gov.br/mj/pt-br/assuntos/suas-protecoes/consumidor/saiba-como-se-proteger/seguranca-digital"
                },
                {
                    "title": "Golpes comuns e como evitá-los",
                    "url": "https://www.bcb.gov.br/estabilidadefinanceira/golpesfinanceiros"
                }
            ]

            # Determinar se é fraude com base na pontuação (limiar ajustável)
            is_fraud = risk_score >= 5 # Limiar de risco

            return {
                "analysis": analysis_detail,
                "risk_score": risk_score,
                "is_fraud": is_fraud,
                "explanation": explanation,
                "recommendations": recommendations,
                "education_links": education_links
            }

        except Exception as e:
            safe_print("Erro no MessageAnalyzer: %s", e)
            return {
                "analysis": f"Erro ao analisar a mensagem: {e}",
                "risk_score": 0,
                "is_fraud": False, # Em caso de erro, assumir que não é fraude para segurança
                "explanation": "Não foi possível analisar a mensagem devido a um erro interno.",
                "recommendations": ["Tente novamente mais tarde."],
                "education_links": []
            }

# --- Agente de Validação de Links (Exemplo Simplificado) ---
class LinkValidator(BaseAgent):
    def __init__(self):
        super().__init__(
            "LinkValidator",
            "Verifica a segurança de URLs suspeitos"
        )

    async def process(self, input_data: dict) -> dict:
        """
        Valida um link. Implementação real precisaria de APIs de segurança web.
        input_data deve conter 'link' (str).
        """
        link = input_data.get("link", "")
        if not link:
             return {
                "analysis": "Nenhum link fornecido para análise.",
                "risk_score": 0,
                "explanation": "Por favor, forneça um link para verificar.",
                "recommendations": [],
                "education_links": []
            }

        # --- Lógica de validação de link (MUITO SIMPLIFICADA) ---
        # Uma implementação real usaria:
        # - Regex para padrões de phishing
        # - Consulta a bancos de dados de URLs maliciosas (ex: Google Safe Browsing API)
        # - Análise do domínio (idade, reputação)
        # - Verificação de HTTPS válido
        # - Simulação de acesso (com cuidado!)

        is_suspicious = False
        explanation = "Este link parece seguro."
        recommendations = ["Sempre verifique a URL completa.", "Confirme a fonte do link."]
        risk_score = 2 # Baixo risco por padrão
        education_links = [] # Links educativos específicos sobre links/phishing

        if "bit.ly" in link or "goo.gl" in link or "tinyurl" in link:
             is_suspicious = True
             explanation = "Este link usa um encurtador, o que pode esconder um destino malicioso."
             recommendations = ["Não clique no link encurtado.", "Tente encontrar a fonte original do link."]
             risk_score = 7
             education_links.append({"title": "Perigos dos Encurtadores de URL", "url": "http://exemplo.com/encurtadores"}) # Exemplo
        elif not link.startswith("https://"):
             is_suspicious = True
             explanation = "Este link não usa HTTPS, a conexão pode não ser segura."
             recommendations = ["Evite inserir dados pessoais ou financeiros em sites sem HTTPS.", "Verifique se o site tem um certificado de segurança válido."]
             risk_score = 6
             education_links.append({"title": "Por que HTTPS é Importante?", "url": "http://exemplo.com/https"}) # Exemplo
        # Adicionar mais verificações aqui (ex: imitação de domínio)
        elif re.search(r'banc[o0]do[b8]rasil\.com', link, re.IGNORECASE): # Exemplo de imitação
             is_suspicious = True
             explanation = "Este link imita o endereço de um banco conhecido. É provavelmente um site falso (phishing)."
             recommendations = ["Não clique neste link.", "Digite o endereço do banco diretamente no navegador.", "Reporte este link."]
             risk_score = 9
             education_links.append({"title": "Como Identificar Sites Falsos (Phishing)", "url": "http://exemplo.com/phishing"}) # Exemplo

        return {
            "analysis": f"Análise do link: {link}",
            "risk_score": risk_score,
            "is_fraud": is_suspicious, # Considerar link suspeito como indicativo de fraude
            "explanation": explanation,
            "recommendations": recommendations,
            "education_links": education_links
        }

# --- Agente Educacional ---
class EducationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "EducationAgent",
            "Fornece informações educativas sobre golpes"
        )

    async def process(self, input_data: dict) -> dict:
        """
        Gera conteúdo educativo com base no tipo de golpe detectado ou análise.
        input_data pode conter 'analysis_summary' (str) ou 'fraud_type' (str).
        """
        analysis_summary = input_data.get("analysis_summary", "golpes financeiros online")
        # fraud_type = input_data.get("fraud_type", "geral") # Poderia ser mais específico

        prompt = f"""
        Você é um agente educacional focado em segurança digital para usuários leigos.
        Crie um pequeno texto educativo e uma lista de dicas sobre como se proteger de {analysis_summary}.
        Use linguagem simples, evite jargões técnicos. O público é jovem (18-30 anos) e usa celular.

        Forneça:
        - Um parágrafo introdutório sobre o tema.
        - 3 a 5 dicas práticas de segurança, fáceis de aplicar no dia a dia.
        - Uma lista de education_links (URLs e títulos) para saber mais (pode ser uma lista fixa ou buscar). Formato JSON: `[{"title": "...", "url": "..."}, ...]`

        Formato:
        TEXTO EDUCATIVO: ...
        DICAS DE SEGURANÇA:
        - Dica 1
        - Dica 2
        EDUCATION_LINKS: [...]
        """

        try:
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            safe_print("Resposta bruta do EducationAgent:\n%s\n---", response_text) # Log para debug

            # --- Processar a resposta do modelo ---
            # Extrair texto educativo, dicas e links (exemplo simplificado)
            educational_text = "Conteúdo educativo não disponível."
            tips = []
            education_links = []

            # Dividir a resposta em seções usando os cabeçalhos
            sections = re.split(r'(TEXTO EDUCATIVO:|DICAS DE SEGURANÇA:|EDUCATION_LINKS:)', response_text)

            # Mapear seções
            section_map = {}
            current_section = None
            for item in sections:
                if item.strip() in ['TEXTO EDUCATIVO:', 'DICAS DE SEGURANÇA:', 'EDUCATION_LINKS:']:
                    current_section = item.strip()
                    section_map[current_section] = ""
                elif current_section is not None:
                    section_map[current_section] += item

            # Extrair conteúdo de cada seção
            educational_text = section_map.get('TEXTO EDUCATIVO:', educational_text).strip()

            tips_text = section_map.get('DICAS DE SEGURANÇA:', '').strip()
            # Extrair itens de lista que começam com '-'
            tips = [item.strip('- ').strip() for item in tips_text.split('\n') if item.strip().startswith('- ')]
            if not tips and tips_text: # Se não encontrou lista, mas tem texto, pega tudo como uma única dica
                 tips = [tips_text]
            if not tips: # Se ainda vazio, usa default
                 tips = ["Não foi possível extrair dicas de segurança."]

            # Simplificar completamente o processamento de links educacionais
            education_links = [
                {
                    "title": "Como identificar golpes financeiros",
                    "url": "https://www.gov.br/mj/pt-br/assuntos/suas-protecoes/consumidor/saiba-como-se-proteger/golpes-financeiros"
                },
                {
                    "title": "Dicas de segurança digital",
                    "url": "https://www.gov.br/mj/pt-br/assuntos/suas-protecoes/consumidor/saiba-como-se-proteger/seguranca-digital"
                },
                {
                    "title": "Golpes comuns e como evitá-los",
                    "url": "https://www.bcb.gov.br/estabilidadefinanceira/golpesfinanceiros"
                }
            ]

            return {
                "educational_text": educational_text,
                "tips": tips,
                "education_links": education_links
            }

        except Exception as e:
            safe_print("Erro no EducationAgent: %s", e)
            return {
                "educational_text": "Não foi possível gerar conteúdo educativo no momento.",
                "tips": [],
                "education_links": []
            }


# --- Gerenciador de Agentes ---
class AgentManager:
    def __init__(self):
        # Instanciar os agentes
        self.message_analyzer = MessageAnalyzer()
        self.link_validator = LinkValidator()
        self.education_agent = EducationAgent()
        # Adicionar outros agentes (Coleta, etc.) aqui

    async def process_user_query(self, query_data: dict) -> dict:
        """
        Orquestra a execução dos agentes para analisar a mensagem do usuário.
        query_data deve conter 'message' (str), 'user_id' (str), etc.
        """
        message = query_data.get("message", "")
        user_id = query_data.get("user_id", "anonymous")
        analysis_id = str(uuid.uuid4()) # Gerar um ID único para esta análise

        safe_print("[%s] Iniciando análise para o usuário %s...", analysis_id, user_id)

        # --- Fase 1: Coleta (Exemplo: extrair links da mensagem) ---
        # Uma implementação real de coleta envolveria:
        # - Agentes buscando informações externas (notícias de golpes, etc.)
        # - Extração mais robusta de elementos da mensagem (links, telefones, etc.)
        links_found = re.findall(r'(https?://[^\s]+)', message)
        safe_print("[%s] Links encontrados na mensagem: %s", analysis_id, links_found)

        # --- Fase 2: Análise ---
        # Rodar o analisador de mensagens
        message_analysis_result = await self.message_analyzer.process({"message": message})
        safe_print("[%s] Análise da mensagem concluída. Risco: %s", analysis_id, message_analysis_result.get('risk_score'))

        # Rodar o validador de links se links forem encontrados
        link_analysis_results = []
        if links_found:
            # Rodar validação para cada link em paralelo
            link_tasks = [self.link_validator.process({"link": link}) for link in links_found]
            link_analysis_results = await asyncio.gather(*link_tasks)
            safe_print("[%s] Análise de links concluída.", analysis_id)
            # Combinar resultados dos links na análise geral se necessário

        # Determinar o resultado final da análise
        # Lógica para combinar pontuações de risco da mensagem e dos links
        final_risk_score = message_analysis_result.get("risk_score", 0)
        if link_analysis_results:
             # Exemplo: usar a maior pontuação de risco entre mensagem e links
             max_link_risk = max([res.get("risk_score", 0) for res in link_analysis_results])
             final_risk_score = max(final_risk_score, max_link_risk)

        final_is_fraud = final_risk_score >= 5 # Usar o limiar combinado (ajustável)

        # Combinar explicações e recomendações
        final_explanation = message_analysis_result.get("explanation", "")
        final_recommendations = message_analysis_result.get("recommendations", [])

        if link_analysis_results:
             final_explanation += "\n\nAnálise de links:"
             for i, res in enumerate(link_analysis_results):
                 final_explanation += f"\nLink {i+1}: {res.get('explanation', 'Sem detalhes.')}"
                 final_recommendations.extend(res.get("recommendations", []))

        # Remover recomendações duplicadas mantendo a ordem
        final_recommendations = list(dict.fromkeys(final_recommendations))


        # --- Fase 3: Resposta e Educação ---
        # Gerar conteúdo educativo se for considerado fraude ou risco alto
        education_result = {}
        # Gerar educação para risco moderado/alto (score >= 3) ou se for fraude
        if final_is_fraud or final_risk_score >= 3:
             education_result = await self.education_agent.process({
                 "analysis_summary": f"golpes como o detectado (risco {final_risk_score}/10)"
                 })
             safe_print("[%s] Conteúdo educativo gerado.", analysis_id)


        # Combinar links educacionais
        final_education_links = message_analysis_result.get("education_links", [])
        if link_analysis_results:
             for res in link_analysis_results:
                 final_education_links.extend(res.get("education_links", []))
        if education_result:
             final_education_links.extend(education_result.get("education_links", []))

        # Remover links educacionais duplicados (baseado na URL)
        seen_urls = set()
        unique_education_links = []
        for link in final_education_links:
            # Apenas processa se for um dicionário e tiver 'url'
            if isinstance(link, dict) and link.get("url"):
                if link["url"] not in seen_urls:
                    unique_education_links.append(link)
                    seen_urls.add(link["url"])
            # Opcional: adicionar links que não são dicionários ou não têm URL (se o modelo gerar)
            # elif link not in unique_education_links:
            #      unique_education_links.append(link)


        # --- Montar a resposta final para o frontend ---
        response_data = {
            "analysis_id": analysis_id, # Incluir o ID da análise
            "is_fraud": final_is_fraud,
            "confidence": final_risk_score / 10.0, # Converter score 0-10 para confiança 0.0-1.0
            "explanation": final_explanation,
            "recommendations": final_recommendations,
            "education_links": unique_education_links,
            # Adicionar texto educativo e dicas separadamente para exibir na UI
            "educational_text": education_result.get("educational_text", ""),
            "education_tips": education_result.get("tips", [])
        }

        safe_print("[%s] Análise concluída. Resultado: %s", analysis_id, 'FRAUDE' if final_is_fraud else 'SEGURO')
        return response_data

# Exemplo de como rodar o AgentManager (apenas para teste local, não no FastAPI)
# async def test_agent_manager():
#     manager = AgentManager()
#     test_message = "Olá, seu cartão foi bloqueado. Clique aqui para desbloquear: http://bit.ly/linkfalso"
#     # test_message = "Olá, sua conta foi atualizada com sucesso. Att, Banco X"
#     result = await manager.process_user_query({"message": test_message, "user_id": "test_user"})
#     import json
#     print("\n--- Resultado Final ---")
#     print(json.dumps(result, indent=2, ensure_ascii=False))

# if __name__ == "__main__":
#     import asyncio
#     # Importar re e json aqui também se for rodar o teste diretamente
#     import re
#     import json
#     asyncio.run(test_agent_manager())