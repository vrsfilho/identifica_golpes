import os
import json
from google.generativeai import configure
from dotenv import load_dotenv

def setup_api():
    """Configura as credenciais de API necessárias."""
    load_dotenv()  # Carrega variáveis de ambiente de um arquivo .env
    
    # Configuração do Google Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        configure(api_key=gemini_api_key)
    else:
        print("Aviso: API key do Google Gemini não encontrada. Algumas funcionalidades podem não funcionar corretamente.")
        # Não levanta exceção para permitir inicialização mesmo sem API key
    
    # Configuração da API de segurança (VirusTotal)
    vt_api_key = os.getenv("VIRUSTOTAL_API_KEY", "")
    if not vt_api_key:
        print("Aviso: API key do VirusTotal não encontrada. A validação de links será limitada.")
    
    # Configuração da API de busca (SerpAPI)
    serpapi_api_key = os.getenv("SERPAPI_API_KEY", "")
    if not serpapi_api_key:
        print("Aviso: API key da SerpAPI não encontrada. A pesquisa na web será limitada.")

def get_api_key(service):
    """Retorna a chave de API para o serviço especificado."""
    keys = {
        "virustotal": os.getenv("VIRUSTOTAL_API_KEY", ""),
        "serpapi": os.getenv("SERPAPI_API_KEY", ""),
        "gemini": os.getenv("GEMINI_API_KEY", ""),
    }
    return keys.get(service, "")

def get_blacklists():
    """Carrega listas de sites maliciosos conhecidos."""
    try:
        with open("data/blacklists.json", "r") as f:
            return json.load(f)
    except:
        # Criar arquivo de exemplo se não existir
        os.makedirs("data", exist_ok=True)
        example_blacklists = {
            "phishing": ["phishing-example.com"],
            "malware": ["malware-example.com"],
            "scam": ["scam-example.com"]
        }
        with open("data/blacklists.json", "w") as f:
            json.dump(example_blacklists, f, indent=2)
        return example_blacklists