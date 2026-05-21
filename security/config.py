"""
Configurações do Módulo de Segurança
Define constantes e parâmetros de configuração para IDS e Firewall
"""

import os

# Configurações principais do sistema de segurança
AUTO_BLOCK = False  # Controle de bloqueio automático (default seguro por padrão)
LOG_FILE = "/var/log/suricata/fast.log"  # Caminho padrão do log do Suricata

# Configurações de detecção
SCAN_KEYWORDS = [
    "SCAN",
    "ET SCAN", 
    "Possible Attack",
    "Nmap",
    "port scan",
    "suspicious activity"
]

# Configurações de firewall
IPTABLES_CHAIN = "INPUT"  # Chain do iptables para bloqueio
BLOCK_TIMEOUT = 300  # Timeout em segundos para comandos do iptables

# Configurações de alerta
MAX_ALERTS_PER_HOUR = 10  # Rate limiting para evitar spam de alertas
ALERT_COOLDOWN = 360  # Cooldown entre alertas do mesmo IP (segundos)

# Configurações de log
SECURITY_LOG_FILE = "logs/security.log"  # Log específico de segurança
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB máximo para rotation

# Configurações de detecção por padrão
ATTACK_PATTERNS = {
    "port_scan": ["SCAN", "ET SCAN", "Nmap", "port scan"],
    "possible_attack": ["Possible Attack", "suspicious activity"],
    "ddos": ["DDoS", "flood", "amplification"],
    "malware": ["malware", "trojan", "backdoor", "exploit"]
}

# Lista de IPs confiáveis (whitelist)
TRUSTED_IPS = [
    "127.0.0.1",  # localhost
    "192.168.0.0/16",  # rede local privada
    "10.0.0.0/8",  # rede privada classe A
    "172.16.0.0/12"  # rede privada classe B
]

# Configurações de ambiente (permite override via variáveis de ambiente)
def get_config():
    """
    Retorna configurações com possíveis overrides de ambiente
    """
    config = {
        "auto_block": os.getenv("SECURITY_AUTO_BLOCK", str(AUTO_BLOCK)).lower() == "true",
        "log_file": os.getenv("SURICATA_LOG_FILE", LOG_FILE),
        "iptables_chain": os.getenv("IPTABLES_CHAIN", IPTABLES_CHAIN),
        "max_alerts_per_hour": int(os.getenv("MAX_ALERTS_PER_HOUR", MAX_ALERTS_PER_HOUR)),
        "alert_cooldown": int(os.getenv("ALERT_COOLDOWN", ALERT_COOLDOWN))
    }
    return config
