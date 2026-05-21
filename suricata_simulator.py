#!/usr/bin/env python3
"""
Simulador do Suricata para Testes do Infra Sentinel
Gera logs realistas de ataques para validar o sistema de segurança
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
from threading import Thread
import socket

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import log_info, log_success, log_error, log_warning
from security.ids import check_intrusions
from security.firewall import block_ip, is_ip_blocked
from security.config import get_config

class SuricataSimulator:
    """
    Simula logs do Suricata para testar o sistema de detecção
    """
    
    def __init__(self, log_file="/var/log/suricata/fast.log"):
        self.log_file = log_file
        self.running = False
        
        # Padrões de ataque realistas
        self.attack_patterns = [
            # Port Scan patterns
            "[**] [1:2000001:1] ET SCAN Potential Port Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.1.100:12345 -> 192.168.1.1:80",
            "[**] [1:2000002:1] ET SCAN Suspicious Port Scan Activity [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 10.0.0.50:54321 -> 192.168.1.1:443",
            
            # Nmap patterns  
            "[**] [1:2000003:1] Nmap NSE Script Detected [**] [Classification: Detection of a Network Scan] [Priority: 2] {TCP} 172.16.0.25:8080 -> 192.168.1.100:22",
            "[**] [1:2000004:1] Nmap Version Detection [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 203.0.113.50:123 -> 192.168.1.100:143",
            
            # DDoS patterns
            "[**] [1:2000005:1] DDoS Amplification Attack [**] [Classification: Attempted Denial of Service] [Priority: 1] {UDP} 198.51.100.75:53 -> 192.168.1.100:53",
            "[**] [1:2000006:1] Potential DNS Amplification [**] [Classification: Attempted Denial of Service] [Priority: 1] {UDP} 192.0.2.100:5353 -> 8.8.8.8:53",
            
            # Malware patterns
            "[**] [1:2000007:1] malware communication detected [**] [Classification: Malware Command and Control] [Priority: 1] {TCP} 203.0.113.25:443 -> 192.168.1.100:80",
            "[**] [1:2000008:1] trojan backdoor activity [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 192.0.2.150:9999 -> 192.168.1.100:4444",
            
            # Suspicious activity
            "[**] [1:2000009:1] suspicious activity from unknown source [**] [Classification: Potentially Bad Traffic] [Priority: 2] {ICMP} 198.18.0.1 -> 192.168.1.100",
            "[**] [1:2000010:1] Possible Attack Detected [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 203.0.113.200:80 -> 192.168.1.100:8080"
        ]
        
        # IPs de origem realistas para testes
        self.source_ips = [
            "192.168.1.100",  # Rede local
            "10.0.0.50",      # Rede privada
            "172.16.0.25",    # Rede privada
            "203.0.113.50",   # IP público (documentação)
            "198.51.100.75",  # IP público (documentação)
            "192.0.2.100",    # IP público (documentação)
            "198.18.0.1",     # IP de teste
            "203.0.113.25",   # IP público (documentação)
            "192.0.2.150",    # IP público (documentação)
            "203.0.113.200"   # IP público (documentação)
        ]
        
        # Portas de destino comuns
        self.destination_ports = [22, 80, 443, 53, 143, 8080, 4444, 9999, 5353, 12345]
        
        # IPs de destino (sua máquina)
        try:
            self.local_ip = socket.gethostbyname(socket.gethostname())
        except:
            self.local_ip = "192.168.1.100"  # Fallback
    
    def _create_log_directory(self):
        """
        Cria diretório de log se não existir
        """
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def _generate_timestamp(self):
        """
        Gera timestamp no formato do Suricata
        """
        now = datetime.now()
        return now.strftime("%m/%d/%Y-%H:%M:%S.%f")[:-3]
    
    def _generate_realistic_log(self):
        """
        Gera uma entrada de log realista
        """
        timestamp = self._generate_timestamp()
        
        # Escolhe padrão de ataque aleatório
        pattern = random.choice(self.attack_patterns)
        
        # Substitui IPs e portas por valores aleatórios
        source_ip = random.choice(self.source_ips)
        dest_port = random.choice(self.destination_ports)
        
        # Personaliza o padrão
        log_line = pattern.replace("192.168.1.100", source_ip)
        log_line = log_line.replace("192.168.1.1", self.local_ip)
        log_line = log_line.replace(":80", f":{dest_port}")
        
        # Adiciona timestamp
        full_log = f"{timestamp} {log_line}"
        
        return full_log
    
    def write_log(self, log_line):
        """
        Escreve linha no log do Suricata
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
            return True
        except Exception as e:
            log_error(f"Erro ao escrever log: {e}")
            return False
    
    def simulate_attack(self, attack_type="mixed", count=5):
        """
        Simula um ataque específico
        """
        log_info(f"🎭 Simulando ataque: {attack_type} ({count} entradas)")
        
        self._create_log_directory()
        
        if attack_type == "port_scan":
            patterns = [p for p in self.attack_patterns if "SCAN" in p]
        elif attack_type == "nmap":
            patterns = [p for p in self.attack_patterns if "Nmap" in p]
        elif attack_type == "ddos":
            patterns = [p for p in self.attack_patterns if "DDoS" in p]
        elif attack_type == "malware":
            patterns = [p for p in self.attack_patterns if "malware" in p or "trojan" in p]
        else:
            patterns = self.attack_patterns
        
        for i in range(count):
            timestamp = self._generate_timestamp()
            pattern = random.choice(patterns)
            
            source_ip = random.choice(self.source_ips)
            dest_port = random.choice(self.destination_ports)
            
            log_line = pattern.replace("192.168.1.100", source_ip)
            log_line = log_line.replace("192.168.1.1", self.local_ip)
            log_line = log_line.replace(":80", f":{dest_port}")
            
            full_log = f"{timestamp} {log_line}"
            
            if self.write_log(full_log):
                log_info(f"📝 Log gerado: {attack_type} -> {source_ip}")
            
            time.sleep(0.1)  # Pequeno delay entre entradas
        
        log_success(f"✅ Ataque {attack_type} simulado com {count} entradas")
    
    def start_continuous_simulation(self, interval=30):
        """
        Inicia simulação contínua de ataques
        """
        log_info(f"🔄 Iniciando simulação contínua (intervalo: {interval}s)")
        
        self.running = True
        self._create_log_directory()
        
        def simulation_loop():
            while self.running:
                # Gera ataque aleatório
                attack_types = ["port_scan", "nmap", "ddos", "malware", "mixed"]
                attack_type = random.choice(attack_types)
                count = random.randint(1, 5)
                
                self.simulate_attack(attack_type, count)
                
                # Espera próximo ciclo
                time.sleep(interval)
        
        thread = Thread(target=simulation_loop, daemon=True)
        thread.start()
        
        return thread
    
    def stop_simulation(self):
        """
        Para simulação contínua
        """
        self.running = False
        log_info("⏹️ Simulação contínua parada")
    
    def clear_logs(self):
        """
        Limpa arquivo de log
        """
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                log_info("🗑️ Log do Suricata limpo")
            return True
        except Exception as e:
            log_error(f"Erro ao limpar log: {e}")
            return False

def test_real_detection():
    """
    Teste completo: simular ataque → detectar → alertar → bloquear
    """
    log_info("🧪 INICIANDO TESTE REAL DE DETECÇÃO")
    log_info("=" * 50)
    
    # Configuração
    config = get_config()
    log_file = "test_suricata.log"  # Log temporário para teste
    
    # Sobrescreve configuração para teste
    config["log_file"] = log_file
    
    simulator = SuricataSimulator(log_file)
    
    try:
        # 1. Limpa logs anteriores
        simulator.clear_logs()
        
        # 2. Simula ataque real
        log_info("🎯 Etapa 1: Simulando ataque...")
        simulator.simulate_attack("port_scan", count=3)
        time.sleep(1)
        
        # 3. Verifica se log foi criado
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
            log_success(f"✅ Log criado com {len(lines)} entradas")
        else:
            log_error("❌ Log não foi criado")
            return False
        
        # 4. Testa detecção do IDS
        log_info("🔍 Etapa 2: Testando detecção do IDS...")
        intrusion = check_intrusions(log_file)
        
        if intrusion["detected"]:
            log_success("✅ IDS detectou ataque!")
            log_info(f"   Tipo: {intrusion.get('type', 'unknown')}")
            log_info(f"   IP: {intrusion.get('ip', 'N/A')}")
            log_info(f"   Severidade: {intrusion.get('severity', 'unknown')}")
            
            # 5. Testa bloqueio (se AUTO_BLOCK=True)
            if config.get("auto_block", False) and intrusion.get("ip"):
                log_info("🔥 Etapa 3: Testando bloqueio automático...")
                ip = intrusion["ip"]
                
                if block_ip(ip):
                    log_success(f"✅ IP {ip} bloqueado!")
                    
                    # Verifica se está bloqueado
                    if is_ip_blocked(ip):
                        log_success("✅ Verificação de bloqueio confirmada!")
                    else:
                        log_warning("⚠️ Bloqueio não confirmado")
                else:
                    log_error(f"❌ Falha ao bloquear IP {ip}")
            else:
                log_info("📝 Bloqueio automático desativado ou IP não identificado")
        else:
            log_warning("⚠️ IDS não detectou ataque")
        
        # 6. Testa rate limiting
        log_info("⏱️ Etapa 4: Testando rate limiting...")
        simulator.simulate_attack("mixed", count=20)  # Muitos alertas
        
        intrusion2 = check_intrusions(log_file)
        if intrusion2["detected"]:
            log_info("✅ Rate limiting funcionando (não spam)")
        else:
            log_warning("⚠️ Rate limiting pode estar bloqueando demais")
        
        log_info("=" * 50)
        log_success("🎉 TESTE REAL CONCLUÍDO!")
        
        return True
        
    except Exception as e:
        log_error(f"❌ Erro no teste real: {e}")
        return False
    
    finally:
        # Limpa logs de teste
        simulator.clear_logs()

def interactive_test():
    """
    Menu interativo para testes
    """
    simulator = SuricataSimulator()
    
    while True:
        print("\n" + "="*50)
        print("🛡️ INFRA SENTINEL - SIMULADOR SURICATA")
        print("="*50)
        print("1. Simular Port Scan")
        print("2. Simular Nmap")
        print("3. Simular DDoS")
        print("4. Simular Malware")
        print("5. Simular Ataque Misto")
        print("6. Teste Completo (Detecção + Bloqueio)")
        print("7. Iniciar Simulação Contínua")
        print("8. Parar Simulação")
        print("9. Limpar Logs")
        print("0. Sair")
        print("="*50)
        
        try:
            choice = input("Escolha: ").strip()
            
            if choice == "1":
                simulator.simulate_attack("port_scan", count=5)
            elif choice == "2":
                simulator.simulate_attack("nmap", count=5)
            elif choice == "3":
                simulator.simulate_attack("ddos", count=5)
            elif choice == "4":
                simulator.simulate_attack("malware", count=5)
            elif choice == "5":
                simulator.simulate_attack("mixed", count=10)
            elif choice == "6":
                test_real_detection()
            elif choice == "7":
                thread = simulator.start_continuous_simulation(interval=10)
                input("Pressione Enter para parar...")
                simulator.stop_simulation()
            elif choice == "8":
                simulator.stop_simulation()
            elif choice == "9":
                simulator.clear_logs()
            elif choice == "0":
                break
            else:
                print("Opção inválida!")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            log_error(f"Erro: {e}")
    
    log_info("👋 Simulador encerrado")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_real_detection()
    else:
        interactive_test()
