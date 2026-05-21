"""
Firewall Manager
Responsável por gerenciar regras de firewall e bloqueio de IPs
"""

import os
import subprocess
import re
import ipaddress
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta

from .config import get_config, TRUSTED_IPS
from .parser import validate_ip, is_private_ip
from ..logger import log_info, log_error, log_warning, log_success

class FirewallManager:
    """
    Classe para gerenciamento de regras de firewall via iptables
    Implementa validação, cache e prevenção de duplicação
    """
    
    def __init__(self):
        self.config = get_config()
        self._blocked_ips_cache: Set[str] = set()  # Cache de IPs bloqueados
        self._last_cache_update = datetime.now()
        self._cache_ttl = 300  # Cache por 5 minutos
    
    def _validate_ip_address(self, ip: str) -> bool:
        """
        Valida endereço IP com verificação adicional
        """
        if not ip or not isinstance(ip, str):
            return False
        
        # Validação básica de formato
        if not validate_ip(ip):
            return False
        
        # Converte para objeto IP para validações adicionais
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Não bloqueia IPs reservados especiais
            if ip_obj.is_loopback:
                log_warning(f"Tentativa de bloquear IP loopback: {ip}")
                return False
            
            if ip_obj.is_multicast:
                log_warning(f"Tentativa de bloquear IP multicast: {ip}")
                return False
            
            if ip_obj.is_link_local:
                log_warning(f"Tentativa de bloquear IP link-local: {ip}")
                return False
            
            return True
            
        except ValueError:
            return False
    
    def _is_trusted_network(self, ip: str) -> bool:
        """
        Verifica se o IP pertence a uma rede confiável
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Verifica redes confiáveis configuradas
            for trusted_network in TRUSTED_IPS:
                try:
                    # Suporta tanto IPs individuais quanto redes CIDR
                    if '/' in trusted_network:
                        network = ipaddress.ip_network(trusted_network, strict=False)
                        if ip_obj in network:
                            log_warning(f"IP {ip} pertence à rede confiável {trusted_network}")
                            return True
                    else:
                        trusted_ip = ipaddress.ip_address(trusted_network)
                        if ip_obj == trusted_ip:
                            log_warning(f"IP {ip} está na whitelist")
                            return True
                except ValueError:
                    continue
            
            return False
            
        except ValueError:
            return False
    
    def _run_iptables_command(self, command: List[str], timeout: int = 10) -> Dict:
        """
        Executa comando iptables de forma segura com timeout
        """
        try:
            # Adiciona sudo se necessário (verifica se não é root)
            full_command = ["sudo"] + command if os.geteuid() != 0 else command
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Não levanta exceção em códigos de erro
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            log_error(f"Timeout ao executar comando iptables: {' '.join(command)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timeout",
                "returncode": -1
            }
        except FileNotFoundError:
            log_error("Comando iptables não encontrado")
            return {
                "success": False,
                "stdout": "",
                "stderr": "iptables command not found",
                "returncode": -1
            }
        except Exception as e:
            log_error(f"Erro inesperado ao executar iptables: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def _update_blocked_ips_cache(self):
        """
        Atualiza cache de IPs bloqueados consultando o iptables
        """
        try:
            # Lista regras atuais na chain INPUT
            result = self._run_iptables_command([
                "iptables", "-L", self.config["iptables_chain"], "--numeric", "--verbose"
            ])
            
            if result["success"]:
                self._blocked_ips_cache.clear()
                
                # Extrai IPs das regras DROP
                for line in result["stdout"].split('\n'):
                    if 'DROP' in line:
                        # Procura por padrões de IP na linha
                        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            if validate_ip(ip):
                                self._blocked_ips_cache.add(ip)
                
                self._last_cache_update = datetime.now()
                log_info(f"Cache atualizado: {len(self._blocked_ips_cache)} IPs bloqueados")
            
        except Exception as e:
            log_error(f"Erro ao atualizar cache de IPs bloqueados: {e}")
    
    def _is_ip_blocked_cached(self, ip: str) -> bool:
        """
        Verifica se IP está bloqueado usando cache (performance)
        """
        # Atualiza cache se necessário
        now = datetime.now()
        if now - self._last_cache_update > timedelta(seconds=self._cache_ttl):
            self._update_blocked_ips_cache()
        
        return ip in self._blocked_ips_cache
    
    def block_ip(self, ip: str) -> bool:
        """
        Bloqueia um IP específico usando iptables
        
        Args:
            ip: Endereço IP a ser bloqueado
            
        Returns:
            bool: True se bloqueio foi bem-sucedido, False caso contrário
        """
        log_info(f"🔥 Tentando bloquear IP: {ip}")
        
        # Validação do IP
        if not self._validate_ip_address(ip):
            log_error(f"IP inválido para bloqueio: {ip}")
            return False
        
        # Verifica se é rede confiável
        if self._is_trusted_network(ip):
            log_error(f"Recusado bloqueio de IP em rede confiável: {ip}")
            return False
        
        # Verifica se já está bloqueado
        if self._is_ip_blocked_cached(ip):
            log_info(f"IP {ip} já está bloqueado")
            return True
        
        # Monta comando iptables
        chain = self.config["iptables_chain"]
        command = [
            "iptables",
            "-A", chain,
            "-s", ip,
            "-j", "DROP"
        ]
        
        # Executa comando
        result = self._run_iptables_command(command, self.config.get("block_timeout", 10))
        
        if result["success"]:
            log_success(f"✅ IP {ip} bloqueado com sucesso")
            # Atualiza cache imediatamente
            self._blocked_ips_cache.add(ip)
            return True
        else:
            log_error(f"❌ Falha ao bloquear IP {ip}: {result['stderr']}")
            return False
    
    def is_ip_blocked(self, ip: str) -> bool:
        """
        Verifica se um IP está bloqueado no firewall
        
        Args:
            ip: Endereço IP a verificar
            
        Returns:
            bool: True se IP está bloqueado, False caso contrário
        """
        # Validação básica
        if not validate_ip(ip):
            return False
        
        return self._is_ip_blocked_cached(ip)
    
    def unblock_ip(self, ip: str) -> bool:
        """
        Desbloqueia um IP específico
        
        Args:
            ip: Endereço IP a ser desbloqueado
            
        Returns:
            bool: True se desbloqueio foi bem-sucedido, False caso contrário
        """
        log_info(f"🔓 Tentando desbloquear IP: {ip}")
        
        # Validação do IP
        if not validate_ip(ip):
            log_error(f"IP inválido para desbloqueio: {ip}")
            return False
        
        # Verifica se está bloqueado
        if not self._is_ip_blocked_cached(ip):
            log_info(f"IP {ip} não está bloqueado")
            return True
        
        # Monta comando iptables para remover regra
        chain = self.config["iptables_chain"]
        command = [
            "iptables",
            "-D", chain,
            "-s", ip,
            "-j", "DROP"
        ]
        
        # Executa comando
        result = self._run_iptables_command(command, 10)
        
        if result["success"]:
            log_success(f"✅ IP {ip} desbloqueado com sucesso")
            # Remove do cache
            self._blocked_ips_cache.discard(ip)
            return True
        else:
            log_error(f"❌ Falha ao desbloquear IP {ip}: {result['stderr']}")
            return False
    
    def get_blocked_ips(self) -> List[str]:
        """
        Retorna lista de todos os IPs bloqueados
        
        Returns:
            List[str]: Lista de IPs bloqueados
        """
        # Garante que cache esteja atualizado
        self._update_blocked_ips_cache()
        return sorted(list(self._blocked_ips_cache))
    
    def get_firewall_status(self) -> Dict:
        """
        Retorna status completo do firewall
        
        Returns:
            Dict com informações do status do firewall
        """
        try:
            # Verifica se iptables está disponível
            iptables_result = self._run_iptables_command(["iptables", "--version"])
            
            # Lista regras da chain
            rules_result = self._run_iptables_command([
                "iptables", "-L", self.config["iptables_chain"], "--numeric"
            ])
            
            return {
                "iptables_available": iptables_result["success"],
                "iptables_version": iptables_result["stdout"].strip() if iptables_result["success"] else "N/A",
                "chain": self.config["iptables_chain"],
                "blocked_ips_count": len(self._blocked_ips_cache),
                "blocked_ips": self.get_blocked_ips(),
                "rules_output": rules_result["stdout"] if rules_result["success"] else "N/A",
                "last_cache_update": self._last_cache_update.isoformat()
            }
            
        except Exception as e:
            log_error(f"Erro ao obter status do firewall: {e}")
            return {
                "iptables_available": False,
                "error": str(e)
            }

# Instância global do firewall
_firewall = None

def get_firewall() -> FirewallManager:
    """
    Retorna instância singleton do firewall manager
    """
    global _firewall
    if _firewall is None:
        _firewall = FirewallManager()
    return _firewall

def block_ip(ip: str) -> bool:
    """
    Função conveniência para bloquear IP
    Mantém compatibilidade com a interface original
    
    Args:
        ip: Endereço IP a bloquear
        
    Returns:
        bool: True se sucesso, False caso contrário
    """
    firewall = get_firewall()
    return firewall.block_ip(ip)

def is_ip_blocked(ip: str) -> bool:
    """
    Função conveniência para verificar se IP está bloqueado
    Mantém compatibilidade com a interface original
    
    Args:
        ip: Endereço IP a verificar
        
    Returns:
        bool: True se bloqueado, False caso contrário
    """
    firewall = get_firewall()
    return firewall.is_ip_blocked(ip)
