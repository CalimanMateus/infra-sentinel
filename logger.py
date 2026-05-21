import logging
from datetime import datetime

def setup_logger():
    """Configura sistema de logs profissional"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('infra-sentinel.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

def log_info(message):
    """Registra mensagem informativa"""
    logger.info(message)

def log_error(message):
    """Registra mensagem de erro"""
    logger.error(message)

def log_warning(message):
    """Registra mensagem de aviso"""
    logger.warning(message)

def log_success(message):
    """Registra mensagem de sucesso"""
    logger.info(f"✅ {message}")
