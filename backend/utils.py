import os
import logging
import json
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("detector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("detector")

def safe_print(message, *args):
    """Função para logging seguro com suporte a formatação."""
    try:
        if args:
            logger.info(message, *args)
        else:
            logger.info(message)
    except Exception as e:
        logger.error(f"Erro ao fazer log: {e}")

def save_analysis_result(result, directory="analysis_results"):
    """Salva o resultado da análise para referência futura."""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/{result['analysis_id']}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return filename
    except Exception as e:
        safe_print(f"Erro ao salvar resultado: {e}")
        return None

def normalize_url(url):
    """Normaliza URLs para comparação."""
    url = url.lower().strip()
    # Remove protocolos
    if url.startswith(('http://', 'https://')):
        url = url.split('://', 1)[1]
    # Remove www.
    if url.startswith('www.'):
        url = url[4:]
    # Remove path se for apenas /
    if url.endswith('/'):
        url = url[:-1]
    return url

def extract_domain(url):
    """Extrai o domínio de uma URL."""
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except:
        # Fallback simples se falhar
        url = url.replace('http://', '').replace('https://', '')
        return url.split('/')[0]