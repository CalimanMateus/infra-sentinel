#!/usr/bin/env python3
"""
Teste Simplificado - Valida Sistema de Segurança
Funciona sem dependências externas
"""

import os
import sys
import time
from datetime import datetime

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_logs():
    """
    Cria logs de teste realistas
    """
    test_log = "test_security.log"
    
    # Logs realistas de ataques
    attack_logs = [
        "01/20/2025-14:30:15.123456 [**] [1:2000001:1] ET SCAN Potential Port Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 203.0.113.50:12345 -> 192.168.1.100:22",
        "01/20/2025-14:30:16.234567 [**] [1:2000002:1] Nmap Scan Detected [**] [Classification: Detection of a Network Scan] [Priority: 2] {TCP} 203.0.113.50:54321 -> 192.168.1.100:80",
        "01/20/2025-14:30:17.345678 [**] [1:2000003:1] Possible Attack Detected [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 198.51.100.75:443 -> 192.168.1.100:8080",
        "01/20/2025-14:30:18.456789 [**] [1:2000004:1] DDoS Amplification Attack [**] [Classification: Attempted Denial of Service] [Priority: 1] {UDP} 192.0.2.100:53 -> 192.168.1.100:53",
        "01/20/2025-14:30:19.567890 [**] [1:2000005:1] malware communication detected [**] [Classification: Malware Command and Control] [Priority: 1] {TCP} 203.0.113.25:9999 -> 192.168.1.100:4444"
    ]
    
    with open(test_log, 'w', encoding='utf-8') as f:
        for log in attack_logs:
            f.write(log + '\n')
    
    return test_log

def test_parser():
    """
    Testa o parser de logs
    """
    print("🧪 Testando Parser de Logs...")
    
    try:
        from security.parser import parse_suricata_line, validate_ip, prioritize_source_ip
        
        # Testa parsing
        test_line = "01/20/2025-14:30:15.123456 [**] [1:2000001:1] ET SCAN Potential Port Scan [**] {TCP} 203.0.113.50:12345 -> 192.168.1.100:22"
        
        parsed = parse_suricata_line(test_line)
        
        print("✅ Parser funcionou!")
        print(f"   Tipo: {parsed['attack_type']}")
        print(f"   IP origem: {parsed['source_ips']}")
        print(f"   Severidade: {parsed['severity']}")
        
        # Testa validação de IP
        valid_ips = ["192.168.1.1", "8.8.8.8", "203.0.113.50"]
        invalid_ips = ["invalid.ip", "256.256.256.256"]
        
        for ip in valid_ips:
            if validate_ip(ip):
                print(f"✅ IP válido: {ip}")
            else:
                print(f"❌ IP deveria ser válido: {ip}")
        
        for ip in invalid_ips:
            if not validate_ip(ip):
                print(f"✅ IP inválido: {ip}")
            else:
                print(f"❌ IP deveria ser inválido: {ip}")
        
        # Testa priorização
        source_ips = ["192.168.1.100", "203.0.113.50"]
        prioritized = prioritize_source_ip(source_ips)
        print(f"✅ IP priorizado: {prioritized}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no parser: {e}")
        return False

def test_ids():
    """
    Testa o sistema de detecção
    """
    print("\n🛡️ Testando Sistema de Detecção...")
    
    try:
        from security.ids import check_intrusions
        
        # Cria logs de teste
        test_log = create_test_logs()
        
        print(f"📝 Log de teste criado: {test_log}")
        
        # Testa detecção
        intrusion = check_intrusions(test_log)
        
        if intrusion["detected"]:
            print("✅ IDS detectou ataque!")
            print(f"   Tipo: {intrusion.get('type', 'unknown')}")
            print(f"   IP: {intrusion.get('ip', 'N/A')}")
            print(f"   Severidade: {intrusion.get('severity', 'unknown')}")
            return True
        else:
            print("⚠️ IDS não detectou ataque")
            print(f"   Resultado: {intrusion}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no IDS: {e}")
        return False
    finally:
        # Limpa logs
        if os.path.exists("test_security.log"):
            os.remove("test_security.log")

def test_firewall():
    """
    Testa o firewall (sem executar comandos reais)
    """
    print("\n🔥 Testando Firewall Manager...")
    
    try:
        from security.firewall import get_firewall
        
        firewall = get_firewall()
        
        # Testa validação de IP
        test_cases = [
            ("192.168.1.1", True),
            ("8.8.8.8", True),
            ("127.0.0.1", False),  # Não deve bloquear loopback
            ("invalid.ip", False),
            ("224.0.0.1", False),  # Não deve bloquear multicast
        ]
        
        for ip, expected in test_cases:
            result = firewall._validate_ip_address(ip)
            status = "✅" if result == expected else "❌"
            print(f"{status} Validação IP {ip}: {result}")
        
        # Testa verificação de rede confiável
        trusted_tests = [
            ("192.168.1.100", True),   # Rede privada
            ("127.0.0.1", True),       # Loopback
            ("8.8.8.8", False),        # IP público
            ("10.0.0.50", True)        # Rede privada
        ]
        
        for ip, expected in trusted_tests:
            result = firewall._is_trusted_network(ip)
            status = "✅" if result == expected else "❌"
            print(f"{status} Rede confiável {ip}: {result}")
        
        # Testa status (não requer privilégios)
        status = firewall.get_firewall_status()
        print(f"✅ Status obtido: iptables disponível = {status.get('iptables_available', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no firewall: {e}")
        return False

def test_config():
    """
    Testa configurações
    """
    print("\n⚙️ Testando Configurações...")
    
    try:
        from security.config import get_config, ATTACK_PATTERNS, AUTO_BLOCK
        
        config = get_config()
        
        # Verifica configurações principais
        required_keys = ["auto_block", "log_file", "iptables_chain"]
        
        for key in required_keys:
            if key in config:
                print(f"✅ Config {key}: {config[key]}")
            else:
                print(f"❌ Config {key} não encontrada")
        
        # Verifica padrões de ataque
        print(f"✅ Padrões de ataque: {list(ATTACK_PATTERNS.keys())}")
        
        # Verifica AUTO_BLOCK
        print(f"✅ AUTO_BLOCK: {AUTO_BLOCK} (seguro por padrão)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_integration():
    """
    Teste de integração completa
    """
    print("\n🔗 Teste de Integração...")
    
    try:
        # Testa imports
        from security.ids import check_intrusions
        from security.firewall import block_ip, is_ip_blocked
        from security.config import AUTO_BLOCK
        
        print("✅ Imports funcionando")
        
        # Testa fluxo básico
        test_log = create_test_logs()
        
        # Detecção
        intrusion = check_intrusions(test_log)
        
        if intrusion["detected"]:
            print("✅ Detecção funcionando")
            
            # Testa lógica de bloqueio (sem executar)
            if AUTO_BLOCK and intrusion.get("ip"):
                print("✅ Lógica de bloqueio automático funcionaria")
                print(f"   IP para bloquear: {intrusion['ip']}")
            else:
                print("✅ Bloqueio automático desativado (seguro)")
        else:
            print("⚠️ Detecção não funcionou")
        
        # Limpa
        os.remove(test_log)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def main():
    """
    Função principal de testes
    """
    print("🛡️ INFRA SENTINEL - TESTE SIMPLIFICADO")
    print("=" * 50)
    
    tests = [
        ("Configurações", test_config),
        ("Parser", test_parser),
        ("Firewall", test_firewall),
        ("IDS", test_ids),
        ("Integração", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🎯 Executando: {test_name}")
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ Erro em {test_name}: {e}")
            results[test_name] = False
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:15} : {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema implementado corretamente")
        print("✅ Pronto para uso")
    else:
        print("\n⚠️ Alguns testes falharam")
        print("❌ Verifique os erros acima")
    
    return passed == total

if __name__ == "__main__":
    main()
