#!/usr/bin/env python3
"""
Script de Teste do Módulo de Segurança
Valida funcionalidades do IDS e Firewall
"""

import os
import sys
import tempfile
from datetime import datetime

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security.ids import check_intrusions, IntrusionDetector
from security.firewall import block_ip, is_ip_blocked, get_firewall
from security.parser import parse_suricata_line, validate_ip, prioritize_source_ip
from security.config import get_config, ATTACK_PATTERNS
from logger import log_info, log_success, log_error, log_warning

def create_test_log_file():
    """
    Cria arquivo de log temporário com exemplos de ataques para teste
    """
    test_logs = [
        "01/20/2025-14:30:15.123456 [**] [1:2000001:1] ET SCAN Potential Port Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.100:12345 -> 8.8.8.8:53",
        "01/20/2025-14:31:22.654321 [**] [1:2000002:1] Possible Attack Detected [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 10.0.0.50:443 -> 192.168.1.1:8080",
        "01/20/2025-14:32:10.987654 [**] [1:2000003:1] Nmap NSE Script Detected [**] [Classification: Detection of a Network Scan] [Priority: 2] {UDP} 172.16.0.25:5353 -> 192.168.1.100:161",
        "01/20/2025-14:33:05.111222 [**] [1:2000004:1] DDoS Amplification Attack [**] [Classification: Attempted Denial of Service] [Priority: 1] {UDP} 203.0.113.50:53 -> 192.168.1.100:53",
        "01/20/2025-14:34:12.333444 [**] [1:2000005:1] malware communication detected [**] [Classification: Malware Command and Control] [Priority: 1] {TCP} 198.51.100.75:443 -> 192.168.1.100:80",
        "01/20/2025-14:35:20.555666 [**] [1:2000006:1] suspicious activity from unknown source [**] [Classification: Potentially Bad Traffic] [Priority: 2] {ICMP} 192.0.2.100 -> 192.168.1.100"
    ]
    
    # Cria arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
    
    for log_entry in test_logs:
        temp_file.write(log_entry + '\n')
    
    temp_file.close()
    return temp_file.name

def test_parser():
    """
    Testa funcionalidades do parser de logs
    """
    log_info("🧪 Testando Parser de Logs...")
    
    test_lines = [
        "01/20/2025-14:30:15.123456 [**] [1:2000001:1] ET SCAN Potential Port Scan [**] {TCP} 192.168.1.100:12345 -> 8.8.8.8:53",
        "01/20/2025-14:31:22.654321 [**] [1:2000002:1] Possible Attack Detected [**] {TCP} 10.0.0.50:443 -> 192.168.1.1:8080"
    ]
    
    for i, line in enumerate(test_lines, 1):
        try:
            parsed = parse_suricata_line(line)
            log_success(f"✅ Teste {i}: Parser funcionou")
            log_info(f"   Tipo: {parsed['attack_type']}")
            log_info(f"   IPs origem: {parsed['source_ips']}")
            log_info(f"   Severidade: {parsed['severity']}")
        except Exception as e:
            log_error(f"❌ Teste {i} falhou: {e}")
    
    # Testa validação de IP
    test_ips = ["192.168.1.1", "8.8.8.8", "invalid.ip", "256.256.256.256"]
    for ip in test_ips:
        result = validate_ip(ip)
        status = "✅" if result == (ip in ["192.168.1.1", "8.8.8.8"]) else "❌"
        log_info(f"{status} Validação IP {ip}: {result}")
    
    # Testa priorização de IP
    test_source_ips = ["192.168.1.100", "8.8.8.8", "10.0.0.50"]
    prioritized = prioritize_source_ip(test_source_ips)
    expected = "8.8.8.8"  # Deve priorizar IP público
    status = "✅" if prioritized == expected else "❌"
    log_info(f"{status} Priorização IP: {prioritized} (esperado: {expected})")

def test_ids():
    """
    Testa funcionalidades do IDS
    """
    log_info("🛡️ Testando Sistema de Detecção de Intrusão...")
    
    # Cria arquivo de log temporário para teste
    test_log_file = create_test_log_file()
    
    try:
        # Testa detecção com arquivo de teste
        detector = IntrusionDetector()
        result = detector.check_intrusions(test_log_file)
        
        if result["detected"]:
            log_success("✅ IDS detectou atividade suspeita")
            log_info(f"   Tipo: {result['type']}")
            log_info(f"   IP: {result.get('ip', 'N/A')}")
            log_info(f"   Severidade: {result.get('severity', 'N/A')}")
        else:
            log_warning("⚠️ IDS não detectou atividade no arquivo de teste")
        
        # Testa função conveniência
        result2 = check_intrusions(test_log_file)
        log_info(f"✅ Função check_intrusions() funcionou: {result2['detected']}")
        
    except Exception as e:
        log_error(f"❌ Erro ao testar IDS: {e}")
    finally:
        # Remove arquivo temporário
        try:
            os.unlink(test_log_file)
        except:
            pass

def test_firewall():
    """
    Testa funcionalidades do firewall (modo seguro, sem executar comandos reais)
    """
    log_info("🔥 Testando Firewall Manager...")
    
    firewall = get_firewall()
    
    # Testa validação de IP
    test_ips = ["192.168.1.1", "8.8.8.8", "127.0.0.1", "invalid.ip", "224.0.0.1"]
    
    for ip in test_ips:
        is_valid = firewall._validate_ip_address(ip)
        expected_valid = ip in ["192.168.1.1", "8.8.8.8"]
        status = "✅" if is_valid == expected_valid else "❌"
        log_info(f"{status} Validação IP {ip}: {is_valid}")
    
    # Testa verificação de rede confiável
    trusted_tests = [
        ("192.168.1.100", True),   # Rede privada
        ("127.0.0.1", True),       # Loopback
        ("8.8.8.8", False),        # IP público
        ("10.0.0.50", True)        # Rede privada
    ]
    
    for ip, expected in trusted_tests:
        is_trusted = firewall._is_trusted_network(ip)
        status = "✅" if is_trusted == expected else "❌"
        log_info(f"{status} Rede confiável {ip}: {is_trusted}")
    
    # Testa status do firewall (não requer privilégios)
    try:
        status = firewall.get_firewall_status()
        log_info(f"✅ Status do firewall obtido")
        log_info(f"   iptables disponível: {status.get('iptables_available', False)}")
        log_info(f"   Chain: {status.get('chain', 'N/A')}")
    except Exception as e:
        log_error(f"❌ Erro ao obter status do firewall: {e}")

def test_config():
    """
    Testa configurações do módulo de segurança
    """
    log_info("⚙️ Testando Configurações...")
    
    config = get_config()
    
    # Verifica configurações esperadas
    expected_keys = ["auto_block", "log_file", "iptables_chain", "max_alerts_per_hour"]
    
    for key in expected_keys:
        if key in config:
            log_success(f"✅ Config {key}: {config[key]}")
        else:
            log_error(f"❌ Config {key} não encontrada")
    
    # Verifica padrões de ataque
    log_info(f"✅ Padrões de ataque configurados: {list(ATTACK_PATTERNS.keys())}")

def run_all_security_tests():
    """
    Executa todos os testes do módulo de segurança
    """
    log_info("🚀 Iniciando Testes do Módulo de Segurança")
    log_info("=" * 50)
    
    try:
        test_config()
        print()
        test_parser()
        print()
        test_ids()
        print()
        test_firewall()
        
        log_info("=" * 50)
        log_success("🎉 Testes de segurança concluídos!")
        
    except Exception as e:
        log_error(f"❌ Erro geral nos testes: {e}")

if __name__ == "__main__":
    run_all_security_tests()
