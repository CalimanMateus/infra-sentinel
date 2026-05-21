"""
Parser de Logs do Suricata
Responsável por extrair informações estruturadas de linhas de log do IDS
"""

import re
import ipaddress
from typing import Dict, Optional, List
from datetime import datetime

# Padrões regex para extração de informações de logs do Suricata
IPV4_PATTERN = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
TIMESTAMP_PATTERN = r'^(\d{2}/\d{2}/\d{4}-\d{2}:\d{2}:\d{2}\.\d+)'

# Padrões de ataque específicos
ATTACK_PATTERNS = {
    "port_scan": [
        r'SCAN',
        r'ET\s+SCAN',
        r'Nmap',
        r'port\s+scan',
        r'Port\s+Scan'
    ],
    "possible_attack": [
        r'Possible\s+Attack',
        r'suspicious\s+activity',
        r'Potential\s+Attack'
    ],
    "ddos": [
        r'DDoS',
        r'flood',
        r'amplification'
    ],
    "malware": [
        r'malware',
        r'trojan',
        r'backdoor',
        r'exploit'
    ]
}

def validate_ip(ip_str: str) -> bool:
    """
    Valida se uma string é um endereço IP válido
    """
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def extract_ips_from_line(line: str) -> List[str]:
    """
    Extrai todos os IPs válidos de uma linha de log
    Retorna lista vazia se nenhum IP for encontrado
    """
    ips = re.findall(IPV4_PATTERN, line)
    # Filtra apenas IPs válidos e remove duplicatas
    valid_ips = []
    seen_ips = set()
    
    for ip in ips:
        if validate_ip(ip) and ip not in seen_ips:
            valid_ips.append(ip)
            seen_ips.add(ip)
    
    return valid_ips

def extract_timestamp(line: str) -> Optional[datetime]:
    """
    Extrai timestamp da linha de log do Suricata
    Retorna None se não conseguir extrair
    """
    timestamp_match = re.search(TIMESTAMP_PATTERN, line)
    if timestamp_match:
        try:
            # Formato do Suricata: MM/DD/YYYY-HH:MM:SS.microseconds
            timestamp_str = timestamp_match.group(1)
            return datetime.strptime(timestamp_str, "%m/%d/%Y-%H:%M:%S.%f")
        except ValueError:
            return None
    return None

def detect_attack_type(line: str) -> str:
    """
    Detecta o tipo de ataque com base em padrões na linha
    Retorna "unknown" se nenhum padrão for reconhecido
    """
    line_lower = line.lower()
    
    for attack_type, patterns in ATTACK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return attack_type
    
    return "unknown"

def extract_port_info(line: str) -> Optional[int]:
    """
    Extrai informação de porta da linha de log (se disponível)
    """
    # Procura por padrões como :80, :443, port 80, etc.
    port_patterns = [
        r':(\d{1,5})\b',  # :80, :443
        r'port\s+(\d{1,5})\b',  # port 80
        r'destination\s+port\s+(\d{1,5})\b'  # destination port 80
    ]
    
    for pattern in port_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            try:
                port = int(match.group(1))
                if 1 <= port <= 65535:  # Porta válida
                    return port
            except ValueError:
                continue
    
    return None

def parse_suricata_line(line: str) -> Dict:
    """
    Função principal de parsing - extrai informações estruturadas de uma linha do Suricata
    
    Args:
        line: Linha do log do Suricata
        
    Returns:
        Dict com informações estruturadas:
        {
            "timestamp": datetime ou None,
            "attack_type": str,
            "source_ips": List[str],
            "destination_ips": List[str],
            "ports": List[int],
            "raw_message": str,
            "severity": str,
            "classification": str
        }
    """
    # Remove espaços em branco extras
    line = line.strip()
    
    # Extrai timestamp
    timestamp = extract_timestamp(line)
    
    # Detecta tipo de ataque
    attack_type = detect_attack_type(line)
    
    # Extrai IPs
    all_ips = extract_ips_from_line(line)
    
    # Separa IPs de origem e destino (heurística simples)
    source_ips = []
    destination_ips = []
    
    if len(all_ips) >= 2:
        # Assume que o primeiro IP é origem, segundo é destino
        source_ips = [all_ips[0]]
        destination_ips = [all_ips[1]]
    elif len(all_ips) == 1:
        # Se só tem um IP, assume que é origem
        source_ips = [all_ips[0]]
    
    # Extrai portas
    port = extract_port_info(line)
    ports = [port] if port else []
    
    # Determina severidade baseada no tipo de ataque
    severity_map = {
        "port_scan": "medium",
        "possible_attack": "high", 
        "ddos": "critical",
        "malware": "critical",
        "unknown": "low"
    }
    severity = severity_map.get(attack_type, "low")
    
    # Classificação adicional baseada em conteúdo
    classification = "network_intrusion"
    if "ET" in line:
        classification = "emerging_threats"
    elif "GPL" in line:
        classification = "general_public_license"
    
    return {
        "timestamp": timestamp,
        "attack_type": attack_type,
        "source_ips": source_ips,
        "destination_ips": destination_ips,
        "ports": ports,
        "raw_message": line,
        "severity": severity,
        "classification": classification
    }

def is_private_ip(ip: str) -> bool:
    """
    Verifica se um IP é de rede privada
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False

def prioritize_source_ip(source_ips: List[str]) -> Optional[str]:
    """
    Seleciona o IP de origem mais relevante para bloqueio
    Prioriza IPs públicos sobre privados
    """
    if not source_ips:
        return None
    
    # Prioriza IPs públicos (mais prováveis de serem atacantes)
    public_ips = [ip for ip in source_ips if not is_private_ip(ip)]
    
    if public_ips:
        return public_ips[0]  # Retorna primeiro IP público
    
    return source_ips[0]  # Se não houver IPs públicos, retorna o primeiro
