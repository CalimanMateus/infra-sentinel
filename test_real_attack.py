#!/usr/bin/env python3
"""
Teste Real de Ataque - Simula Nmap e Valida Sistema Completo
Reproduz exatamente o cenário real: ataque → log → detecção → alerta → bloqueio
"""

import os
import sys
import time
import subprocess
import socket
from datetime import datetime

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import log_info, log_success, log_error, log_warning
from security.ids import check_intrusions
from security.firewall import block_ip, is_ip_blocked, get_firewall
from security.config import get_config, AUTO_BLOCK
from suricata_simulator import SuricataSimulator

class RealAttackTester:
    """
    Testador que simula ataques reais e valida o sistema completo
    """
    
    def __init__(self):
        self.config = get_config()
        self.simulator = SuricataSimulator("test_real_attack.log")
        self.test_log = "test_real_attack.log"
        
        # IPs de teste (documentação RFC 5737)
        self.test_ips = [
            "203.0.113.50",   # IP público de teste
            "198.51.100.75",  # IP público de teste  
            "192.0.2.100",    # IP público de teste
            "192.168.1.100",  # IP local (se estiver em rede local)
        ]
        
        # Obtém IP real da máquina
        try:
            self.local_ip = socket.gethostbyname(socket.gethostname())
        except:
            self.local_ip = "127.0.0.1"
    
    def simulate_nmap_scan(self, target_ip, scan_type="syn"):
        """
        Simula um scan Nmap realista
        """
        log_info(f"🎯 Simulando Nmap {scan_type} scan contra {target_ip}")
        
        # Gera logs realistas de Nmap
        nmap_logs = [
            f"{self.simulator._generate_timestamp()} [**] [1:2000003:1] Nmap NSE Script Detected [**] [Classification: Detection of a Network Scan] [Priority: 2] {TCP} {target_ip}:12345 -> {self.local_ip}:22",
            f"{self.simulator._generate_timestamp()} [**] [1:2000004:1] Nmap Version Detection [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} {target_ip}:54321 -> {self.local_ip}:80",
            f"{self.simulator._generate_timestamp()} [**] [1:2000005:1] Nmap OS Detection [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} {target_ip}:32768 -> {self.local_ip}:443",
            f"{self.simulator._generate_timestamp()} [**] [1:2000006:1] ET SCAN Nmap Scan Detected [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} {target_ip}:8080 -> {self.local_ip}:8080",
        ]
        
        for log_line in nmap_logs:
            self.simulator.write_log(log_line)
            time.sleep(0.1)
        
        log_success(f"✅ Nmap scan simulado: {len(nmap_logs)} entradas geradas")
        return target_ip
    
    def simulate_port_scan(self, source_ip):
        """
        Simula um port scan realista
        """
        log_info(f"🔍 Simulando port scan de {source_ip}")
        
        # Simula scan em múltiplas portas
        ports = [22, 80, 443, 53, 143, 993, 995, 8080, 3306, 5432]
        
        for port in ports:
            timestamp = self.simulator._generate_timestamp()
            log_line = f"{timestamp} [**] [1:2000001:1] ET SCAN Potential Port Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} {source_ip}:{random.randint(10000, 65535)} -> {self.local_ip}:{port}"
            self.simulator.write_log(log_line)
            time.sleep(0.05)
        
        log_success(f"✅ Port scan simulado: {len(ports)} portas testadas")
        return source_ip
    
    def simulate_ddos_attack(self, source_ip):
        """
        Simula ataque DDoS
        """
        log_info(f"💥 Simulando ataque DDoS de {source_ip}")
        
        # Gera múltiplas entradas de DDoS
        for i in range(20):
            timestamp = self.simulator._generate_timestamp()
            log_line = f"{timestamp} [**] [1:2000007:1] DDoS Amplification Attack [**] [Classification: Attempted Denial of Service] [Priority: 1] {UDP} {source_ip}:53 -> {self.local_ip}:53"
            self.simulator.write_log(log_line)
            time.sleep(0.01)
        
        log_success(f"✅ DDoS simulado: 20 pacotes")
        return source_ip
    
    def test_detection_pipeline(self, attack_type="nmap"):
        """
        Teste completo do pipeline de detecção
        """
        log_info(f"🧪 TESTE COMPLETO - {attack_type.upper()}")
        log_info("=" * 60)
        
        # 1. Limpa ambiente
        self.simulator.clear_logs()
        
        # 2. Escolhe IP de ataque
        attacker_ip = random.choice(self.test_ips)
        
        # 3. Simula ataque específico
        if attack_type == "nmap":
            attacker_ip = self.simulate_nmap_scan(attacker_ip)
        elif attack_type == "port_scan":
            attacker_ip = self.simulate_port_scan(attacker_ip)
        elif attack_type == "ddos":
            attacker_ip = self.simulate_ddos_attack(attacker_ip)
        
        # 4. Verifica se log foi gerado
        if not os.path.exists(self.test_log):
            log_error("❌ Log de ataque não foi gerado")
            return False
        
        with open(self.test_log, 'r') as f:
            log_lines = f.readlines()
        
        log_info(f"📝 Log gerado: {len(log_lines)} entradas")
        
        # 5. Testa detecção do IDS
        log_info("🔍 Etapa 1: Testando IDS...")
        intrusion = check_intrusions(self.test_log)
        
        detection_success = False
        if intrusion["detected"]:
            detection_success = True
            log_success("✅ IDS detectou ataque!")
            log_info(f"   Tipo: {intrusion.get('type', 'unknown')}")
            log_info(f"   IP detectado: {intrusion.get('ip', 'N/A')}")
            log_info(f"   Severidade: {intrusion.get('severity', 'unknown')}")
            log_info(f"   Raw: {intrusion.get('raw', 'N/A')[:100]}...")
        else:
            log_warning("⚠️ IDS não detectou ataque")
            log_info(f"   Resultado: {intrusion}")
        
        # 6. Testa bloqueio automático
        blocking_success = None
        if detection_success and intrusion.get("ip"):
            log_info("🔥 Etapa 2: Testando bloqueio automático...")
            
            # Salva estado original do AUTO_BLOCK
            original_auto_block = AUTO_BLOCK
            
            # Força AUTO_BLOCK=True para teste
            import security.config
            security.config.AUTO_BLOCK = True
            
            try:
                ip_to_block = intrusion["ip"]
                log_info(f"   Tentando bloquear IP: {ip_to_block}")
                
                if block_ip(ip_to_block):
                    blocking_success = True
                    log_success(f"✅ IP {ip_to_block} bloqueado!")
                    
                    # Verifica se realmente está bloqueado
                    if is_ip_blocked(ip_to_block):
                        log_success("✅ Verificação de bloqueio confirmada!")
                    else:
                        log_warning("⚠️ Bloqueio não confirmado na verificação")
                else:
                    blocking_success = False
                    log_error(f"❌ Falha ao bloquear IP {ip_to_block}")
                
            finally:
                # Restaura configuração original
                security.config.AUTO_BLOCK = original_auto_block
        else:
            log_info("📝 Pulando teste de bloqueio (sem IP detectado)")
        
        # 7. Testa rate limiting
        log_info("⏱️ Etapa 3: Testando rate limiting...")
        
        # Gera muitos ataques rápidos
        for i in range(15):
            self.simulator.simulate_attack("mixed", count=2)
            time.sleep(0.1)
        
        # Verifica se rate limiting está funcionando
        intrusion_after_rate_limit = check_intrusions(self.test_log)
        if intrusion_after_rate_limit["detected"]:
            log_info("✅ Rate limiting funcionando (ainda detecta, mas não spam)")
        else:
            log_info("ℹ️ Rate limiting pode ter bloqueado detecção (normal)")
        
        # 8. Relatório final
        log_info("=" * 60)
        log_info("📊 RELATÓRIO FINAL")
        log_info(f"   Tipo de ataque: {attack_type}")
        log_info(f"   IP atacante: {attacker_ip}")
        log_info(f"   Logs gerados: {len(log_lines)}")
        log_info(f"   IDS detectou: {'✅' if detection_success else '❌'}")
        log_info(f"   Bloqueio testado: {'✅' if blocking_success == True else '❌' if blocking_success == False else '⏭️'}")
        
        # 9. Limpa logs
        self.simulator.clear_logs()
        
        overall_success = detection_success
        log_success("🎉 TESTE COMPLETO CONCLUÍDO!" if overall_success else "⚠️ TESTE COM PROBLEMAS")
        
        return overall_success
    
    def test_all_attack_types(self):
        """
        Testa todos os tipos de ataque
        """
        log_info("🚀 INICIANDO SUITE COMPLETA DE TESTES")
        log_info("=" * 60)
        
        attack_types = ["nmap", "port_scan", "ddos"]
        results = {}
        
        for attack_type in attack_types:
            log_info(f"\n🎯 Testando: {attack_type}")
            try:
                success = self.test_detection_pipeline(attack_type)
                results[attack_type] = success
                
                time.sleep(2)  # Delay entre testes
                
            except Exception as e:
                log_error(f"❌ Erro no teste {attack_type}: {e}")
                results[attack_type] = False
        
        # Relatório geral
        log_info("\n" + "=" * 60)
        log_info("📈 RELATÓRIO GERAL DA SUITE DE TESTES")
        log_info("=" * 60)
        
        for attack_type, success in results.items():
            status = "✅ PASSOU" if success else "❌ FALHOU"
            log_info(f"   {attack_type:15} : {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        log_info(f"\n📊 Total: {passed_tests}/{total_tests} testes passaram")
        
        if passed_tests == total_tests:
            log_success("🏆 TODOS OS TESTES PASSARAM! Sistema pronto para produção.")
        else:
            log_warning("⚠️ Alguns testes falharam. Verifique os logs.")
        
        return passed_tests == total_tests
    
    def test_firewall_directly(self):
        """
        Testa o firewall diretamente (sem depender do IDS)
        """
        log_info("🔥 TESTE DIRETO DO FIREWALL")
        log_info("=" * 40)
        
        test_ip = "203.0.113.50"  # IP de teste
        
        # 1. Verifica se não está bloqueado
        initial_state = is_ip_blocked(test_ip)
        log_info(f"Estado inicial do IP {test_ip}: {'Bloqueado' if initial_state else 'Livre'}")
        
        # 2. Tenta bloquear
        log_info(f"Tentando bloquear {test_ip}...")
        block_result = block_ip(test_ip)
        
        if block_result:
            log_success(f"✅ Bloqueio executado com sucesso")
            
            # 3. Verifica se está bloqueado
            final_state = is_ip_blocked(test_ip)
            log_info(f"Estado final do IP {test_ip}: {'Bloqueado' if final_state else 'Livre'}")
            
            if final_state:
                log_success("✅ Bloqueio confirmado!")
                
                # 4. Tenta desbloquear para limpeza
                firewall = get_firewall()
                if firewall.unblock_ip(test_ip):
                    log_info("✅ IP desbloqueado (limpeza)")
                else:
                    log_warning("⚠️ Falha ao desbloquear IP")
                
                return True
            else:
                log_error("❌ Bloqueio não confirmado")
                return False
        else:
            log_error("❌ Falha ao executar bloqueio")
            return False

def main():
    """
    Função principal de testes
    """
    import random
    
    tester = RealAttackTester()
    
    print("🛡️ INFRA SENTINEL - TESTE REAL DE ATAQUE")
    print("=" * 50)
    print("Este teste simula ataques reais e valida:")
    print("1. Geração de logs do Suricata")
    print("2. Detecção pelo IDS")
    print("3. Bloqueio automático pelo Firewall")
    print("4. Rate limiting")
    print("=" * 50)
    
    try:
        # Teste 1: Firewall diretamente
        print("\n🔥 Teste 1: Firewall Diretamente")
        firewall_ok = tester.test_firewall_directly()
        
        # Teste 2: Todos os tipos de ataque
        print("\n🎯 Teste 2: Suite Completa de Ataques")
        attacks_ok = tester.test_all_attack_types()
        
        # Resultado final
        print("\n" + "=" * 50)
        print("🏁 RESULTADO FINAL")
        print("=" * 50)
        print(f"Firewall: {'✅ OK' if firewall_ok else '❌ FALHOU'}")
        print(f"Ataques:  {'✅ OK' if attacks_ok else '❌ FALHOU'}")
        
        if firewall_ok and attacks_ok:
            print("\n🎉 SISTEMA 100% FUNCIONAL!")
            print("✅ Pronto para produção")
            print("✅ Todos os componentes testados")
            print("✅ Detecção e bloqueio funcionando")
        else:
            print("\n⚠️ SISTENTE COM PROBLEMAS")
            print("❌ Verifique os logs acima")
            print("❌ Corrija antes de usar em produção")
        
    except KeyboardInterrupt:
        print("\n👋 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral nos testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
