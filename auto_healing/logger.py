#!/usr/bin/env python3
"""
Sistema de Logs Profissional para Auto-Healing
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Configurar logs
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "healing.log"

# Garantir que diretório de logs existe
LOG_DIR.mkdir(exist_ok=True)

def setup_logger():
    """Configura o logger profissional"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

def log(message, level="INFO"):
    """
    Função central de log
    Args:
        message (str): Mensagem para logar
        level (str): Nível do log (INFO, SUCCESS, ERROR, WARNING)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_message = f"[{timestamp}] [{level}] {message}"
    
    # Escrever no arquivo
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(formatted_message + '\n')
    
    # Exibir no console
    print(formatted_message)
    
    # Log no sistema de logging
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "SUCCESS":
        logger.info(f"✅ {message}")
    else:
        logger.info(message)
